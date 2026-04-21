"""Stars Connection - Astrology Matchmaking SaaS backend."""
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / ".env")

import os
import logging
from datetime import datetime, timezone
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
import io

from auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    set_auth_cookies, clear_auth_cookies, get_current_user
)
from astrology import compute_moon_position
from matching import generate_matches_for_user, regenerate_all_matches
from pdf_gen import generate_kundali_pdf
from seed_data import seed_demo_profiles

from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

PREMIUM_PRICE_INR = 1000.0   # ₹1000 unlocks 5 premium matches
UNLOCKS_PER_PURCHASE = 5


async def seed_admin():
    admin_email = os.environ["ADMIN_EMAIL"]
    admin_pwd = os.environ["ADMIN_PASSWORD"]
    existing = await db.users.find_one({"email": admin_email})
    if existing is None:
        await db.users.insert_one({
            "email": admin_email,
            "password_hash": hash_password(admin_pwd),
            "name": "Admin",
            "role": "admin",
            "is_premium": True,
            "unlocked_premium": 999,
            "profile_complete": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
    elif not verify_password(admin_pwd, existing["password_hash"]):
        await db.users.update_one(
            {"email": admin_email},
            {"$set": {"password_hash": hash_password(admin_pwd)}}
        )


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await db.users.create_index("email", unique=True)
    await db.matches.create_index([("user_id", 1), ("score", -1)])
    await db.payment_transactions.create_index("session_id", unique=True)
    await seed_admin()
    await seed_demo_profiles(db)
    await regenerate_all_matches(db)
    logger.info("Startup complete: admin + demo seeded, matches generated.")
    yield
    client.close()


app = FastAPI(lifespan=lifespan)
api = APIRouter(prefix="/api")

# ---------- Models ----------
class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ProfileIn(BaseModel):
    name: str
    gender: str  # "male" | "female"
    looking_for: str  # "male" | "female"
    dob: str  # YYYY-MM-DD
    birth_time: str  # HH:MM
    birth_city: str
    bio: Optional[str] = ""


class CheckoutIn(BaseModel):
    origin_url: str


# ---------- Helpers ----------
async def _current(request: Request) -> dict:
    return await get_current_user(request, db)


def _public_user(u: dict) -> dict:
    """Strip sensitive data."""
    return {
        "id": u["id"] if "id" in u else str(u.get("_id", "")),
        "email": u.get("email"),
        "name": u.get("name"),
        "gender": u.get("gender"),
        "looking_for": u.get("looking_for"),
        "dob": u.get("dob"),
        "birth_time": u.get("birth_time"),
        "birth_city": u.get("birth_city"),
        "bio": u.get("bio", ""),
        "role": u.get("role", "user"),
        "is_premium": u.get("is_premium", False),
        "unlocked_premium": u.get("unlocked_premium", 0),
        "profile_complete": u.get("profile_complete", False),
        "astro": u.get("astro"),
    }


# ---------- Auth ----------
@api.post("/auth/register")
async def register(body: RegisterIn, response: Response):
    email = body.email.lower()
    if await db.users.find_one({"email": email}):
        raise HTTPException(400, "Email already registered")
    doc = {
        "email": email,
        "password_hash": hash_password(body.password),
        "name": body.name,
        "role": "user",
        "is_premium": False,
        "unlocked_premium": 0,
        "profile_complete": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    result = await db.users.insert_one(doc)
    uid = str(result.inserted_id)
    set_auth_cookies(response, create_access_token(uid, email), create_refresh_token(uid))
    return _public_user({**doc, "id": uid})


@api.post("/auth/login")
async def login(body: LoginIn, response: Response):
    email = body.email.lower()
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    uid = str(user["_id"])
    set_auth_cookies(response, create_access_token(uid, email), create_refresh_token(uid))
    user["id"] = uid
    return _public_user(user)


@api.post("/auth/logout")
async def logout(response: Response):
    clear_auth_cookies(response)
    return {"ok": True}


@api.get("/auth/me")
async def me(request: Request):
    u = await _current(request)
    return _public_user(u)


# ---------- Profile ----------
@api.post("/profile")
async def save_profile(body: ProfileIn, request: Request):
    user = await _current(request)
    # Compute astrology server-side
    try:
        astro = compute_moon_position(body.dob, body.birth_time, body.birth_city)
    except Exception as e:
        raise HTTPException(400, f"Invalid birth data: {e}")

    update = {
        "name": body.name,
        "gender": body.gender,
        "looking_for": body.looking_for,
        "dob": body.dob,
        "birth_time": body.birth_time,
        "birth_city": body.birth_city,
        "bio": body.bio or "",
        "astro": astro,
        "profile_complete": True,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.users.update_one({"_id": ObjectId(user["id"])}, {"$set": update})
    # Generate matches for this user
    count = await generate_matches_for_user(db, user["id"])
    # Also refresh matches for any demo user who lists this user's gender
    # so the new user appears in their match pool (for future use)
    refreshed = await db.users.find_one({"_id": ObjectId(user["id"])})
    refreshed["id"] = user["id"]
    return {"user": _public_user(refreshed), "matches_generated": count}


# ---------- Matches & Dashboard ----------
@api.get("/matches")
async def get_matches(request: Request):
    """Return dashboard: low-score visible, high-score locked/unlocked with blur."""
    user = await _current(request)
    if not user.get("profile_complete"):
        return {"status": "needs_profile", "low": [], "high": [], "unlocked_ids": []}

    all_matches = await db.matches.find(
        {"user_id": user["id"]}, {"_id": 0}
    ).sort("score", -1).to_list(500)

    if not all_matches:
        return {"status": "waiting", "low": [], "high": [], "unlocked_ids": [],
                "unlocked_count": user.get("unlocked_premium", 0)}

    low = [m for m in all_matches if m["score"] < 18]
    high = [m for m in all_matches if m["score"] >= 18]

    # Determine which high matches are unlocked: top N by score where N = unlocked_premium
    unlocked_count = int(user.get("unlocked_premium", 0))
    unlocked_ids = [m["match_user_id"] for m in high[:unlocked_count]]

    # Strip sensitive info from locked cards
    sanitized_high = []
    for idx, m in enumerate(high):
        is_unlocked = idx < unlocked_count
        if is_unlocked:
            sanitized_high.append({**m, "locked": False})
        else:
            sanitized_high.append({
                "match_user_id": m["match_user_id"],
                "score": m["score"],
                "max_score": m["max_score"],
                "locked": True,
                "match_name": "⋆ Hidden ⋆",
                "match_city": "•••",
                "match_bio": "Unlock to reveal this highly compatible soul.",
                "match_avatar": "",
            })

    return {
        "status": "ready",
        "low": low,
        "high": sanitized_high,
        "unlocked_ids": unlocked_ids,
        "unlocked_count": unlocked_count,
        "total_high": len(high),
        "remaining_locked": max(0, len(high) - unlocked_count),
    }


@api.get("/kundali/{match_id}")
async def get_kundali(match_id: str, request: Request):
    user = await _current(request)
    match = await db.matches.find_one(
        {"user_id": user["id"], "match_user_id": match_id}, {"_id": 0}
    )
    if not match:
        raise HTTPException(404, "Match not found")

    # Access control: if premium match, must be within user's unlocked count
    if match["score"] >= 18:
        unlocked_count = int(user.get("unlocked_premium", 0))
        # Check rank among premium matches
        all_high = await db.matches.find(
            {"user_id": user["id"], "score": {"$gte": 18}}, {"_id": 0}
        ).sort("score", -1).to_list(500)
        rank = next((i for i, m in enumerate(all_high) if m["match_user_id"] == match_id), -1)
        if rank >= unlocked_count:
            raise HTTPException(402, "This kundali is locked. Unlock premium matches to view.")

    # Add self astro for UI
    me_user = await db.users.find_one({"_id": ObjectId(user["id"])})
    return {
        "match": match,
        "self": {
            "name": me_user.get("name"),
            "gender": me_user.get("gender"),
            "dob": me_user.get("dob"),
            "birth_city": me_user.get("birth_city"),
            "astro": me_user.get("astro"),
        }
    }


@api.get("/kundali/{match_id}/pdf")
async def get_kundali_pdf(match_id: str, request: Request):
    user = await _current(request)
    match = await db.matches.find_one(
        {"user_id": user["id"], "match_user_id": match_id}, {"_id": 0}
    )
    if not match:
        raise HTTPException(404, "Match not found")

    if match["score"] >= 18:
        unlocked_count = int(user.get("unlocked_premium", 0))
        all_high = await db.matches.find(
            {"user_id": user["id"], "score": {"$gte": 18}}, {"_id": 0}
        ).sort("score", -1).to_list(500)
        rank = next((i for i, m in enumerate(all_high) if m["match_user_id"] == match_id), -1)
        if rank >= unlocked_count:
            raise HTTPException(402, "PDF locked - unlock premium first.")

    me_user = await db.users.find_one({"_id": ObjectId(user["id"])})
    me_user["id"] = str(me_user["_id"])
    pdf_bytes = generate_kundali_pdf(_public_user(me_user), match)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="kundali_{match["match_name"].replace(" ", "_")}.pdf"'}
    )


# ---------- Payments (Stripe) ----------
def _get_stripe(request: Request) -> StripeCheckout:
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    return StripeCheckout(api_key=os.environ["STRIPE_API_KEY"], webhook_url=webhook_url)


@api.post("/payments/checkout")
async def create_checkout(body: CheckoutIn, request: Request):
    user = await _current(request)
    if not user.get("profile_complete"):
        raise HTTPException(400, "Complete your profile before purchasing")

    origin = body.origin_url.rstrip("/")
    stripe = _get_stripe(request)
    success_url = f"{origin}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin}/payment/cancel"

    req = CheckoutSessionRequest(
        amount=PREMIUM_PRICE_INR,  # ₹1000 as float
        currency="inr",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_id": user["id"],
            "email": user["email"],
            "package": "premium_unlock_5",
            "unlocks": str(UNLOCKS_PER_PURCHASE),
        },
    )
    session = await stripe.create_checkout_session(req)

    await db.payment_transactions.insert_one({
        "session_id": session.session_id,
        "user_id": user["id"],
        "email": user["email"],
        "amount": PREMIUM_PRICE_INR,
        "currency": "inr",
        "unlocks": UNLOCKS_PER_PURCHASE,
        "payment_status": "initiated",
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "processed": False,
    })
    return {"url": session.url, "session_id": session.session_id}


@api.get("/payments/status/{session_id}")
async def payment_status(session_id: str, request: Request):
    user = await _current(request)
    txn = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if not txn:
        raise HTTPException(404, "Transaction not found")
    if txn["user_id"] != user["id"]:
        raise HTTPException(403, "Not your transaction")

    stripe = _get_stripe(request)
    status = await stripe.get_checkout_status(session_id)

    # Update txn
    await db.payment_transactions.update_one(
        {"session_id": session_id},
        {"$set": {
            "status": status.status,
            "payment_status": status.payment_status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }}
    )

    # Idempotent unlock
    if status.payment_status == "paid" and not txn.get("processed"):
        result = await db.payment_transactions.update_one(
            {"session_id": session_id, "processed": {"$ne": True}},
            {"$set": {"processed": True, "processed_at": datetime.now(timezone.utc).isoformat()}}
        )
        if result.modified_count == 1:
            await db.users.update_one(
                {"_id": ObjectId(user["id"])},
                {"$inc": {"unlocked_premium": UNLOCKS_PER_PURCHASE},
                 "$set": {"is_premium": True}}
            )

    # Return fresh user state
    fresh = await db.users.find_one({"_id": ObjectId(user["id"])})
    fresh["id"] = user["id"]
    return {
        "status": status.status,
        "payment_status": status.payment_status,
        "amount_total": status.amount_total,
        "currency": status.currency,
        "unlocked_premium": fresh.get("unlocked_premium", 0),
    }


@api.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    body = await request.body()
    sig = request.headers.get("Stripe-Signature", "")
    stripe = _get_stripe(request)
    try:
        event = await stripe.handle_webhook(body, sig)
    except Exception as e:
        raise HTTPException(400, f"Webhook error: {e}")

    if event.payment_status == "paid" and event.session_id:
        txn = await db.payment_transactions.find_one({"session_id": event.session_id})
        if txn and not txn.get("processed"):
            result = await db.payment_transactions.update_one(
                {"session_id": event.session_id, "processed": {"$ne": True}},
                {"$set": {"processed": True, "status": "complete",
                          "payment_status": "paid",
                          "processed_at": datetime.now(timezone.utc).isoformat()}}
            )
            if result.modified_count == 1:
                await db.users.update_one(
                    {"_id": ObjectId(txn["user_id"])},
                    {"$inc": {"unlocked_premium": UNLOCKS_PER_PURCHASE},
                     "$set": {"is_premium": True}}
                )
    return {"received": True}


# ---------- Analytics ----------
@api.get("/analytics/me")
async def my_analytics(request: Request):
    user = await _current(request)
    total_matches = await db.matches.count_documents({"user_id": user["id"]})
    high_count = await db.matches.count_documents({"user_id": user["id"], "score": {"$gte": 18}})
    low_count = total_matches - high_count
    conversions = await db.payment_transactions.count_documents(
        {"user_id": user["id"], "processed": True}
    )
    return {
        "total_matches": total_matches,
        "high_matches": high_count,
        "low_matches": low_count,
        "unlocked_premium": user.get("unlocked_premium", 0),
        "purchases": conversions,
    }


# ---------- Root ----------
@api.get("/")
async def root():
    return {"service": "Stars Connection", "version": "1.0"}


app.include_router(api)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_URL", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
