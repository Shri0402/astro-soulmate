"""Match generation: compute Ashtakoota score between a user and opposite-gender candidates."""
from bson import ObjectId
from datetime import datetime, timezone
from astrology import compute_ashtakoota, compatibility_verdict


async def generate_matches_for_user(db, user_id: str) -> int:
    """Compute matches for a user against all opposite-gender profiles in DB.
    Stores in matches collection. Returns count."""
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user or not user.get("astro"):
        return 0

    looking_for = user.get("looking_for")
    if not looking_for:
        return 0

    # Remove prior matches
    await db.matches.delete_many({"user_id": user_id})

    # Strict filter: candidates whose gender matches the user's "looking_for".
    # No reciprocity required (per ultra-private platform rules).
    candidates = await db.users.find({
        "_id": {"$ne": ObjectId(user_id)},
        "gender": looking_for,
        "astro": {"$exists": True},
        "role": {"$ne": "admin"},
    }).to_list(500)

    created = 0
    for c in candidates:
        a = user["astro"]
        b = c["astro"]
        score_data = compute_ashtakoota(a, b)
        verdict = compatibility_verdict(score_data["total"], score_data["mangal_a"], score_data["mangal_b"])

        match_doc = {
            "user_id": user_id,
            "match_user_id": str(c["_id"]),
            "match_name": c.get("name", "Unknown"),
            "match_gender": c.get("gender"),
            "match_dob": c.get("dob"),
            "match_city": c.get("birth_city"),
            "match_bio": c.get("bio", ""),
            "match_avatar": c.get("avatar_url", ""),
            "score": score_data["total"],
            "max_score": 36,
            "breakdown": score_data["gunas"],
            "mangal_a": score_data["mangal_a"],
            "mangal_b": score_data["mangal_b"],
            "verdict": verdict,
            "is_premium": score_data["total"] >= 18,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.matches.insert_one(match_doc)
        created += 1

    return created


async def regenerate_all_matches(db) -> None:
    """Rebuild matches for every user with a completed profile."""
    users = await db.users.find({"astro": {"$exists": True}}).to_list(1000)
    for u in users:
        await generate_matches_for_user(db, str(u["_id"]))
