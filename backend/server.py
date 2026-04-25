"""Stars Connection - Astrology Matchmaking SaaS backend (private invite-only)."""
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / ".env")

import os
import io
import logging
import secrets
from datetime import datetime, timezone
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId

from auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    set_auth_cookies, clear_auth_cookies, get_current_user
)
from astrology import compute_moon_position
from matching import generate_matches_for_user, regenerate_all_matches
from pdf_gen import generate_kundali_pdf
from seed_data import seed_demo_profiles
from report_interpretations import interpret, GUNA_AREA, conclusion, mangal_statement

from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

PREMIUM_PRICE_INR = 1000.0
UNLOCKS_PER_PURCHASE = 5


async def seed_admin():
    admin_email = os.environ["ADMIN_EMAIL"]
    admin_pwd = os.environ["ADMIN_PASSWORD"]
    existing = await db.users.find_one({"email": admin_email})
    if existing is None:
        await db.users.insert_one({
            "email": admin_email,
            "password_hash": hash_password(admin_pwd),
            "name": "Admin", "full_name": "Admin",
            "role": "admin", "is_premium": True, "unlocked_premium": 999,
            "is_private_member": True, "profile_complete": False,
            "can_login": True, "email_verified": True,
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
    await db.invites.create_index("code", unique=True)
    await db.phone_number_requests.create_index(
        [("requester_user_id", 1), ("receiver_user_id", 1)], unique=True
    )
    await seed_admin()
    await seed_demo_profiles(db)
    await regenerate_all_matches(db)
    logger.info("Startup complete: admin + private members seeded, matches generated.")
    yield
    client.close()


app = FastAPI(lifespan=lifespan)
api = APIRouter(prefix="/api")


# ---------- Models ----------
class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str
    invite_code: str  # required - invite-only platform


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class ProfileIn(BaseModel):
    name: str
    gender: str
    looking_for: str
    dob: str
    birth_time: str
    birth_city: str
    state: Optional[str] = ""
    bio: Optional[str] = ""
    phone: Optional[str] = ""


class CheckoutIn(BaseModel):
    origin_url: str


class PhoneRequestIn(BaseModel):
    receiver_user_id: str


class InviteCreateIn(BaseModel):
    note: Optional[str] = ""


# ---------- Helpers ----------
async def _current(request: Request) -> dict:
    return await get_current_user(request, db)


def _public_user(u: dict) -> dict:
    return {
        "id": u["id"] if "id" in u else str(u.get("_id", "")),
        "email": u.get("email"),
        "name": u.get("name") or u.get("full_name"),
        "full_name": u.get("full_name") or u.get("name"),
        "gender": u.get("gender"),
        "looking_for": u.get("looking_for"),
        "dob": u.get("dob"),
        "birth_time": u.get("birth_time"),
        "birth_city": u.get("birth_city") or u.get("city"),
        "city": u.get("city") or u.get("birth_city"),
        "state": u.get("state", ""),
        "bio": u.get("bio", ""),
        "phone": u.get("phone", ""),
        "role": u.get("role", "user"),
        "is_private_member": u.get("is_private_member", False),
        "is_premium": u.get("is_premium", False),
        "unlocked_premium": u.get("unlocked_premium", 0),
        "profile_complete": u.get("profile_complete", False),
        "referral_source": u.get("referral_source"),
        "referred_by_name": u.get("referred_by_name"),
        "astro": u.get("astro"),
    }


# ---------- Auth (invite-only) ----------
@api.post("/auth/register")
async def register(body: RegisterIn, response: Response):
    email = body.email.lower()
    code = body.invite_code.strip().upper()

    invite = await db.invites.find_one({"code": code, "used": False})
    if not invite:
        raise HTTPException(403, "Invalid or used invite code. This is a private referral-only network.")

    if await db.users.find_one({"email": email}):
        raise HTTPException(400, "Email already registered")

    referred_by = None
    referred_by_name = "Founding Cohort"
    if invite.get("created_by"):
        referrer = await db.users.find_one({"_id": ObjectId(invite["created_by"])})
        if referrer:
            referred_by = str(referrer["_id"])
            referred_by_name = referrer.get("name") or referrer.get("full_name") or "Member"

    doc = {
        "email": email,
        "password_hash": hash_password(body.password),
        "name": body.name, "full_name": body.name,
        "role": "user",
        "is_premium": True, "unlocked_premium": 999,  # paywall removed for approved members
        "is_private_member": True,
        "can_login": True, "email_verified": False,
        "profile_complete": False,
        "referral_source": "referral",
        "referred_by_user_id": referred_by,
        "referred_by_name": referred_by_name,
        "invite_code_used": code,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    result = await db.users.insert_one(doc)
    uid = str(result.inserted_id)

    await db.invites.update_one(
        {"_id": invite["_id"]},
        {"$set": {"used": True, "used_by": uid, "used_at": datetime.now(timezone.utc).isoformat()}}
    )

    set_auth_cookies(response, create_access_token(uid, email), create_refresh_token(uid))
    return _public_user({**doc, "id": uid})


@api.get("/auth/invite/{code}")
async def validate_invite(code: str):
    """Public: check if an invite code is valid (used to gate the registration UI)."""
    code = code.strip().upper()
    invite = await db.invites.find_one({"code": code, "used": False}, {"_id": 0, "code": 1, "created_by": 1, "note": 1})
    if not invite:
        raise HTTPException(404, "Invalid or already-used invite code.")
    referrer_name = "Founding Cohort"
    if invite.get("created_by"):
        u = await db.users.find_one({"_id": ObjectId(invite["created_by"])}, {"name": 1, "full_name": 1})
        if u:
            referrer_name = u.get("name") or u.get("full_name") or referrer_name
    return {"valid": True, "code": code, "referrer_name": referrer_name}


@api.post("/auth/login")
async def login(body: LoginIn, response: Response):
    email = body.email.lower()
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    if user.get("can_login") is False:
        raise HTTPException(403, "This account cannot login.")
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
    try:
        astro = compute_moon_position(body.dob, body.birth_time, body.birth_city)
    except Exception as e:
        raise HTTPException(400, f"Invalid birth data: {e}")

    update = {
        "name": body.name, "full_name": body.name,
        "gender": body.gender,
        "looking_for": body.looking_for,
        "dob": body.dob, "birth_time": body.birth_time,
        "birth_city": body.birth_city, "city": body.birth_city,
        "state": body.state or "",
        "bio": body.bio or "",
        "phone": body.phone or "",
        "astro": astro,
        "profile_complete": True,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.users.update_one({"_id": ObjectId(user["id"])}, {"$set": update})
    count = await generate_matches_for_user(db, user["id"])
    refreshed = await db.users.find_one({"_id": ObjectId(user["id"])})
    refreshed["id"] = user["id"]
    return {"user": _public_user(refreshed), "matches_generated": count}


# ---------- Matches & Dashboard (no paywall) ----------
@api.get("/matches")
async def get_matches(request: Request):
    user = await _current(request)
    if not user.get("profile_complete"):
        return {"status": "needs_profile", "matches": []}

    all_matches = await db.matches.find(
        {"user_id": user["id"]}, {"_id": 0}
    ).sort("score", -1).to_list(500)

    if not all_matches:
        return {"status": "waiting", "matches": []}

    # All matches fully visible. Annotate with phone_visible flag.
    out = []
    for m in all_matches:
        # Has the requester (current user) been granted phone access by this match?
        granted = await db.phone_number_requests.find_one({
            "requester_user_id": user["id"],
            "receiver_user_id": m["match_user_id"],
            "status": "accepted",
        })
        phone = ""
        if granted:
            other = await db.users.find_one(
                {"_id": ObjectId(m["match_user_id"])}, {"phone": 1}
            )
            phone = (other or {}).get("phone", "")
        out.append({**m, "phone": phone, "phone_visible": bool(granted)})

    return {"status": "ready", "matches": out, "count": len(out)}


@api.get("/kundali/{match_id}")
async def get_kundali(match_id: str, request: Request):
    user = await _current(request)
    match = await db.matches.find_one(
        {"user_id": user["id"], "match_user_id": match_id}, {"_id": 0}
    )
    if not match:
        raise HTTPException(404, "Match not found")

    me_user = await db.users.find_one({"_id": ObjectId(user["id"])})
    other = await db.users.find_one({"_id": ObjectId(match_id)}) or {}

    # Phone access state
    granted = await db.phone_number_requests.find_one({
        "requester_user_id": user["id"],
        "receiver_user_id": match_id,
        "status": "accepted",
    })
    pending = await db.phone_number_requests.find_one({
        "requester_user_id": user["id"],
        "receiver_user_id": match_id,
    })
    phone_status = "none"
    if pending:
        phone_status = pending.get("status", "pending")

    # Build report sections
    name_a = me_user.get("name") or me_user.get("full_name") or "You"
    name_b = match["match_name"]

    report = {
        "title": f"Matching between {name_a} and {name_b}",
        "birth_details": [
            {"label": "Sex",            "a": me_user.get("gender", "—").capitalize(), "b": (match.get("match_gender") or "—").capitalize()},
            {"label": "Date of Birth",  "a": me_user.get("dob", "—"),              "b": match.get("match_dob", "—")},
            {"label": "Time of Birth",  "a": me_user.get("birth_time", "—"),       "b": other.get("birth_time", "—")},
            {"label": "Place of Birth", "a": me_user.get("birth_city", "—"),       "b": match.get("match_city", "—")},
            {"label": "State",          "a": me_user.get("state", "—"),            "b": other.get("state", "—")},
            {"label": "Rashi",          "a": me_user.get("astro", {}).get("rashi", "—"),     "b": other.get("astro", {}).get("rashi", "—")},
            {"label": "Rashi Lord",     "a": _rashi_lord(me_user.get("astro", {}).get("rashi_idx")),
                                         "b": _rashi_lord(other.get("astro", {}).get("rashi_idx"))},
            {"label": "Nakshatra-Pada", "a": f"{me_user.get('astro', {}).get('nakshatra', '—')} - {me_user.get('astro', {}).get('pada', '—')}",
                                         "b": f"{other.get('astro', {}).get('nakshatra', '—')} - {other.get('astro', {}).get('pada', '—')}"},
        ],
        "ashtakoota_table": [],
        "interpretations": [],
    }

    for guna_name, g in match["breakdown"].items():
        a_val = g.get("a", "—") if isinstance(g, dict) else "—"
        b_val = g.get("b", "—") if isinstance(g, dict) else "—"
        report["ashtakoota_table"].append({
            "guna": guna_name,
            "boy": a_val if me_user.get("gender") == "male" else b_val,
            "girl": b_val if me_user.get("gender") == "male" else a_val,
            "max_points": g["max"],
            "points_obtained": g["score"],
            "area_of_life": GUNA_AREA.get(guna_name, "—"),
        })
        # interpret expects boy first
        boy_val = a_val if me_user.get("gender") == "male" else b_val
        girl_val = b_val if me_user.get("gender") == "male" else a_val
        report["interpretations"].append({
            "guna": guna_name,
            "text": interpret(guna_name, boy_val, girl_val, g["score"], g["max"]),
        })

    # Mangal & Conclusion
    if me_user.get("gender") == "male":
        mb_a, mb_b = match["mangal_a"], match["mangal_b"]
        m_name_a, m_name_b = name_a, name_b
    else:
        mb_a, mb_b = match["mangal_b"], match["mangal_a"]
        m_name_a, m_name_b = name_b, name_a

    report["mangal_dosha_text"] = mangal_statement(m_name_a, m_name_b, mb_a, mb_b)
    report["conclusion_text"] = conclusion(match["score"], 36, match["mangal_a"], match["mangal_b"])
    report["total_points"] = match["score"]
    report["max_total"] = 36

    return {
        "match": match,
        "self": {
            "id": user["id"],
            "name": name_a,
            "gender": me_user.get("gender"),
            "dob": me_user.get("dob"),
            "birth_city": me_user.get("birth_city"),
            "astro": me_user.get("astro"),
        },
        "report": report,
        "phone_status": phone_status,
        "phone": (other.get("phone", "") if granted else ""),
    }


def _rashi_lord(idx):
    if idx is None: return "—"
    lords = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
            "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
    try:
        return lords[idx]
    except Exception:
        return "—"


@api.get("/kundali/{match_id}/pdf")
async def get_kundali_pdf(match_id: str, request: Request):
    user = await _current(request)
    match = await db.matches.find_one(
        {"user_id": user["id"], "match_user_id": match_id}, {"_id": 0}
    )
    if not match:
        raise HTTPException(404, "Match not found")
    me_user = await db.users.find_one({"_id": ObjectId(user["id"])})
    me_user["id"] = str(me_user["_id"])
    pdf_bytes = generate_kundali_pdf(_public_user(me_user), match)
    safe_name = (match.get('match_name') or 'partner').replace(' ', '_')
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="kundali_{safe_name}.pdf"'}
    )


# ---------- Phone number request ----------
@api.post("/phone-requests")
async def create_phone_request(body: PhoneRequestIn, request: Request):
    user = await _current(request)
    if user["id"] == body.receiver_user_id:
        raise HTTPException(400, "Cannot request own phone")
    receiver = await db.users.find_one({"_id": ObjectId(body.receiver_user_id)})
    if not receiver:
        raise HTTPException(404, "Member not found")

    existing = await db.phone_number_requests.find_one({
        "requester_user_id": user["id"],
        "receiver_user_id": body.receiver_user_id,
    })
    if existing:
        return {"status": existing["status"], "id": str(existing["_id"])}
    doc = {
        "requester_user_id": user["id"],
        "requester_name": user.get("name") or user.get("full_name"),
        "receiver_user_id": body.receiver_user_id,
        "receiver_name": receiver.get("name") or receiver.get("full_name"),
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    res = await db.phone_number_requests.insert_one(doc)
    return {"status": "pending", "id": str(res.inserted_id)}


@api.get("/phone-requests/inbox")
async def phone_inbox(request: Request):
    user = await _current(request)
    items = await db.phone_number_requests.find(
        {"receiver_user_id": user["id"]}
    ).sort("created_at", -1).to_list(200)
    out = []
    for it in items:
        out.append({
            "id": str(it["_id"]),
            "requester_user_id": it["requester_user_id"],
            "requester_name": it.get("requester_name"),
            "status": it["status"],
            "created_at": it.get("created_at"),
        })
    return {"items": out, "pending_count": sum(1 for x in out if x["status"] == "pending")}


@api.get("/phone-requests/sent")
async def phone_sent(request: Request):
    user = await _current(request)
    items = await db.phone_number_requests.find(
        {"requester_user_id": user["id"]}
    ).sort("created_at", -1).to_list(200)
    return {"items": [
        {"id": str(i["_id"]), "receiver_user_id": i["receiver_user_id"],
         "receiver_name": i.get("receiver_name"), "status": i["status"],
         "created_at": i.get("created_at")}
        for i in items
    ]}


@api.post("/phone-requests/{req_id}/accept")
async def accept_phone(req_id: str, request: Request):
    user = await _current(request)
    req = await db.phone_number_requests.find_one({"_id": ObjectId(req_id)})
    if not req or req["receiver_user_id"] != user["id"]:
        raise HTTPException(404, "Request not found")
    await db.phone_number_requests.update_one(
        {"_id": ObjectId(req_id)},
        {"$set": {"status": "accepted", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"ok": True}


@api.post("/phone-requests/{req_id}/reject")
async def reject_phone(req_id: str, request: Request):
    user = await _current(request)
    req = await db.phone_number_requests.find_one({"_id": ObjectId(req_id)})
    if not req or req["receiver_user_id"] != user["id"]:
        raise HTTPException(404, "Request not found")
    await db.phone_number_requests.update_one(
        {"_id": ObjectId(req_id)},
        {"$set": {"status": "rejected", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return {"ok": True}


# ---------- Invites ----------
def _gen_code() -> str:
    return secrets.token_urlsafe(6).replace("_", "X").replace("-", "X").upper()[:8]


@api.post("/invites")
async def create_invite(body: InviteCreateIn, request: Request):
    user = await _current(request)
    code = _gen_code()
    while await db.invites.find_one({"code": code}):
        code = _gen_code()
    doc = {
        "code": code,
        "created_by": user["id"],
        "created_by_name": user.get("name") or user.get("full_name"),
        "note": body.note or "",
        "used": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.invites.insert_one(doc)
    return {"code": code}


@api.get("/invites/mine")
async def my_invites(request: Request):
    user = await _current(request)
    items = await db.invites.find({"created_by": user["id"]}).sort("created_at", -1).to_list(200)
    out = []
    for i in items:
        out.append({
            "code": i["code"], "used": i.get("used", False),
            "used_by": i.get("used_by"), "note": i.get("note", ""),
            "created_at": i.get("created_at"),
        })
    return {"items": out}


# ---------- Payments (kept available, UI hidden) ----------
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
        amount=PREMIUM_PRICE_INR, currency="inr",
        success_url=success_url, cancel_url=cancel_url,
        metadata={"user_id": user["id"], "email": user["email"], "package": "premium_unlock_5", "unlocks": str(UNLOCKS_PER_PURCHASE)},
    )
    session = await stripe.create_checkout_session(req)
    await db.payment_transactions.insert_one({
        "session_id": session.session_id, "user_id": user["id"], "email": user["email"],
        "amount": PREMIUM_PRICE_INR, "currency": "inr", "unlocks": UNLOCKS_PER_PURCHASE,
        "payment_status": "initiated", "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(), "processed": False,
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
    await db.payment_transactions.update_one(
        {"session_id": session_id},
        {"$set": {"status": status.status, "payment_status": status.payment_status,
                  "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if status.payment_status == "paid" and not txn.get("processed"):
        result = await db.payment_transactions.update_one(
            {"session_id": session_id, "processed": {"$ne": True}},
            {"$set": {"processed": True, "processed_at": datetime.now(timezone.utc).isoformat()}}
        )
        if result.modified_count == 1:
            await db.users.update_one(
                {"_id": ObjectId(user["id"])},
                {"$inc": {"unlocked_premium": UNLOCKS_PER_PURCHASE}, "$set": {"is_premium": True}}
            )
    fresh = await db.users.find_one({"_id": ObjectId(user["id"])})
    fresh["id"] = user["id"]
    return {"status": status.status, "payment_status": status.payment_status,
            "amount_total": status.amount_total, "currency": status.currency,
            "unlocked_premium": fresh.get("unlocked_premium", 0)}


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
                {"$set": {"processed": True, "status": "complete", "payment_status": "paid",
                          "processed_at": datetime.now(timezone.utc).isoformat()}}
            )
            if result.modified_count == 1:
                await db.users.update_one(
                    {"_id": ObjectId(txn["user_id"])},
                    {"$inc": {"unlocked_premium": UNLOCKS_PER_PURCHASE}, "$set": {"is_premium": True}}
                )
    return {"received": True}


# ---------- Analytics ----------
@api.get("/analytics/me")
async def my_analytics(request: Request):
    user = await _current(request)
    total_matches = await db.matches.count_documents({"user_id": user["id"]})
    high_count = await db.matches.count_documents({"user_id": user["id"], "score": {"$gte": 18}})
    return {"total_matches": total_matches, "high_matches": high_count,
            "low_matches": total_matches - high_count}


@api.get("/")
async def root():
    return {"service": "Stars Connection", "version": "2.0", "private": True}


app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("FRONTEND_URL", "*")],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)
