"""Seed 11 private invite-only users. Password = DDMMYYYY from DOB."""
from datetime import datetime, timezone
from auth import hash_password
from astrology import compute_moon_position, resolve_location, CITY_DB

# Make sure obscure cities are resolvable
CITY_DB.setdefault("ft walton beach", (30.4058, -86.6187))
CITY_DB.setdefault("paducah", (37.0834, -88.6000))
CITY_DB.setdefault("los angeles", (34.0522, -118.2437))
CITY_DB.setdefault("jalandhar", (31.3260, 75.5762))
CITY_DB.setdefault("nanded", (19.1383, 77.3210))
CITY_DB.setdefault("houston", (29.7604, -95.3698))
CITY_DB.setdefault("new delhi", (28.6139, 77.2090))

# DOB stored as YYYY-MM-DD; password is DDMMYYYY
PRIVATE_USERS = [
    {"full_name": "Shakuntala Thatti", "email": "123@gmail.com", "dob": "1998-08-02", "birth_time": "23:45", "gender": "female", "city": "Mumbai", "state": "Maharashtra", "looking_for": "male"},
    {"full_name": "Michael Anthony", "email": "michaelanthonyssj5@gmail.com", "dob": "2000-01-07", "birth_time": "07:00", "gender": "male", "city": "Houston", "state": "Texas", "looking_for": "female"},
    {"full_name": "Garvit", "email": "garvit.gandhi.05@gmail.com", "dob": "2005-06-25", "birth_time": "12:00", "gender": "male", "city": "New Delhi", "state": "Delhi", "looking_for": "female"},
    {"full_name": "Shubham", "email": "shubhamneema011@gmail.com", "dob": "2005-11-11", "birth_time": "06:00", "gender": "male", "city": "Mumbai", "state": "Maharashtra", "looking_for": "male"},
    {"full_name": "Jeremiah W", "email": "Jbw2443@gmail.com", "dob": "1983-12-03", "birth_time": "05:50", "gender": "male", "city": "Ft Walton Beach", "state": "Florida", "looking_for": "female"},
    {"full_name": "AJ", "email": "spammywammy200@gmail.com", "dob": "1997-02-06", "birth_time": "08:19", "gender": "male", "city": "Paducah", "state": "Kentucky", "looking_for": "female"},
    {"full_name": "Rachel", "email": "Garlicbutterfriedchicken@gmail.com", "dob": "2004-09-10", "birth_time": "02:30", "gender": "female", "city": "Los Angeles", "state": "California", "looking_for": "male"},
    {"full_name": "Minal", "email": "Minalshah013@gmail.com", "dob": "1996-07-20", "birth_time": "02:10", "gender": "female", "city": "Mumbai", "state": "Maharashtra", "looking_for": "male"},
    {"full_name": "Anuketan", "email": "anutkhi@gmail.com", "dob": "1997-04-06", "birth_time": "12:25", "gender": "male", "city": "Jalandhar", "state": "Punjab", "looking_for": "female"},
    {"full_name": "Shrilatha Shripathi", "email": "shrilatha0402@gmail.com", "dob": "2000-02-04", "birth_time": "23:44", "gender": "female", "city": "Mumbai", "state": "Maharashtra", "looking_for": "male"},
    # No-email user: synthesize internal email; cannot login by email but profile exists for matching
    {"full_name": "Venkatesh Amrutwar", "email": "venkatesh.amrutwar@noemail.local", "dob": "1994-12-06", "birth_time": "03:40", "gender": "male", "city": "Nanded", "state": "Maharashtra", "looking_for": "female"},
]


def dob_password(dob_iso: str) -> str:
    """YYYY-MM-DD -> DDMMYYYY"""
    d = datetime.strptime(dob_iso, "%Y-%m-%d")
    return d.strftime("%d%m%Y")


async def seed_demo_profiles(db) -> None:
    for p in PRIVATE_USERS:
        existing = await db.users.find_one({"email": p["email"].lower()})
        if existing:
            continue
        astro = compute_moon_position(p["dob"], p["birth_time"], p["city"])
        pwd = dob_password(p["dob"])
        doc = {
            "email": p["email"].lower(),
            "password_hash": hash_password(pwd),
            "name": p["full_name"],
            "full_name": p["full_name"],
            "gender": p["gender"],
            "looking_for": p["looking_for"],
            "dob": p["dob"],
            "birth_time": p["birth_time"],
            "birth_city": p["city"],
            "city": p["city"],
            "state": p["state"],
            "bio": "",
            "phone": "",  # populate later
            "role": "user",
            "is_premium": True,         # paywall removed - all approved users have full visibility
            "unlocked_premium": 999,
            "is_private_member": True,
            "profile_complete": True,
            "referral_source": "founding_member",
            "referred_by_user_id": None,
            "referred_by_name": "Founding Cohort",
            "astro": astro,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.users.insert_one(doc)
