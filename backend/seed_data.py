"""Seed 20 demo user profiles on startup (only if they don't already exist)."""
from datetime import datetime, timezone
from auth import hash_password
from astrology import compute_moon_position

DEMO_PROFILES = [
    {"name": "Ananya Sharma", "gender": "female", "looking_for": "male", "dob": "1997-03-12", "birth_time": "07:45", "birth_city": "Mumbai", "bio": "Classical dancer, love vedic philosophy.", "email": "ananya@demo.stars"},
    {"name": "Rohan Patel", "gender": "male", "looking_for": "female", "dob": "1994-11-22", "birth_time": "14:30", "birth_city": "Ahmedabad", "bio": "Engineer turned entrepreneur.", "email": "rohan@demo.stars"},
    {"name": "Priya Nair", "gender": "female", "looking_for": "male", "dob": "1996-06-08", "birth_time": "04:15", "birth_city": "Kochi", "bio": "Doctor, reader of ancient texts.", "email": "priya@demo.stars"},
    {"name": "Aditya Verma", "gender": "male", "looking_for": "female", "dob": "1993-01-18", "birth_time": "22:10", "birth_city": "Delhi", "bio": "Architect with love for music.", "email": "aditya@demo.stars"},
    {"name": "Ishita Reddy", "gender": "female", "looking_for": "male", "dob": "1998-09-27", "birth_time": "11:00", "birth_city": "Hyderabad", "bio": "UX designer, yoga teacher.", "email": "ishita@demo.stars"},
    {"name": "Arjun Singh", "gender": "male", "looking_for": "female", "dob": "1995-05-14", "birth_time": "18:45", "birth_city": "Jaipur", "bio": "Photographer, travels for a living.", "email": "arjun@demo.stars"},
    {"name": "Meera Iyer", "gender": "female", "looking_for": "male", "dob": "1999-02-03", "birth_time": "08:30", "birth_city": "Chennai", "bio": "AI researcher and karnatic singer.", "email": "meera@demo.stars"},
    {"name": "Vikram Joshi", "gender": "male", "looking_for": "female", "dob": "1992-07-19", "birth_time": "16:20", "birth_city": "Pune", "bio": "Finance, amateur astronomer.", "email": "vikram@demo.stars"},
    {"name": "Nandini Kapoor", "gender": "female", "looking_for": "male", "dob": "1996-12-05", "birth_time": "03:40", "birth_city": "Chandigarh", "bio": "Lawyer with a poetic side.", "email": "nandini@demo.stars"},
    {"name": "Karan Mehta", "gender": "male", "looking_for": "female", "dob": "1994-04-25", "birth_time": "12:15", "birth_city": "Surat", "bio": "Startup founder in fintech.", "email": "karan@demo.stars"},
    {"name": "Shreya Desai", "gender": "female", "looking_for": "male", "dob": "1997-08-17", "birth_time": "21:00", "birth_city": "Bangalore", "bio": "Product manager, salsa dancer.", "email": "shreya@demo.stars"},
    {"name": "Dev Malhotra", "gender": "male", "looking_for": "female", "dob": "1993-10-02", "birth_time": "06:50", "birth_city": "Lucknow", "bio": "Professor of history.", "email": "dev@demo.stars"},
    {"name": "Tanvi Bhatt", "gender": "female", "looking_for": "male", "dob": "1998-01-29", "birth_time": "13:25", "birth_city": "Indore", "bio": "Dentist, foodie.", "email": "tanvi@demo.stars"},
    {"name": "Siddharth Rao", "gender": "male", "looking_for": "female", "dob": "1995-03-30", "birth_time": "09:55", "birth_city": "Bhopal", "bio": "Data scientist, trekker.", "email": "sid@demo.stars"},
    {"name": "Riya Chopra", "gender": "female", "looking_for": "male", "dob": "1996-11-11", "birth_time": "17:30", "birth_city": "Amritsar", "bio": "Chartered accountant and traveller.", "email": "riya@demo.stars"},
    {"name": "Harsh Khanna", "gender": "male", "looking_for": "female", "dob": "1994-06-21", "birth_time": "02:20", "birth_city": "Varanasi", "bio": "Filmmaker and storyteller.", "email": "harsh@demo.stars"},
    {"name": "Diya Ghosh", "gender": "female", "looking_for": "male", "dob": "1999-04-08", "birth_time": "19:45", "birth_city": "Kolkata", "bio": "Literature enthusiast and painter.", "email": "diya@demo.stars"},
    {"name": "Ayaan Qureshi", "gender": "male", "looking_for": "female", "dob": "1992-09-14", "birth_time": "05:10", "birth_city": "Patna", "bio": "Civil servant, cricket fan.", "email": "ayaan@demo.stars"},
    {"name": "Kavya Menon", "gender": "female", "looking_for": "male", "dob": "1997-07-02", "birth_time": "23:15", "birth_city": "Thiruvananthapuram", "bio": "Marine biologist.", "email": "kavya@demo.stars"},
    {"name": "Rahul Gupta", "gender": "male", "looking_for": "female", "dob": "1993-12-26", "birth_time": "10:40", "birth_city": "Nagpur", "bio": "Musician and marketer.", "email": "rahul@demo.stars"},
]


async def seed_demo_profiles(db) -> None:
    for p in DEMO_PROFILES:
        existing = await db.users.find_one({"email": p["email"]})
        if existing:
            continue
        astro = compute_moon_position(p["dob"], p["birth_time"], p["birth_city"])
        doc = {
            "email": p["email"],
            "password_hash": hash_password("DemoPass123!"),
            "name": p["name"],
            "gender": p["gender"],
            "looking_for": p["looking_for"],
            "dob": p["dob"],
            "birth_time": p["birth_time"],
            "birth_city": p["birth_city"],
            "bio": p["bio"],
            "role": "demo",
            "is_premium": False,
            "unlocked_premium": 0,
            "profile_complete": True,
            "astro": astro,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.users.insert_one(doc)
