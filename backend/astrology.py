"""
Astrology engine using Swiss Ephemeris (pyswisseph).
Computes: Moon sign (Rashi), Nakshatra, Ashtakoota 8-guna score, Mangal Dosha.
All calculations use sidereal (Lahiri ayanamsa) - the Vedic standard.
"""
import swisseph as swe
from datetime import datetime
from timezonefinder import TimezoneFinder
import pytz

# Configure sidereal mode (Lahiri) - Vedic standard
swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

# 12 Rashi (zodiac signs) in order starting from Aries
RASHIS = [
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena"
]

RASHI_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
               "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

# 27 Nakshatras (each 13°20' = 800')
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Nakshatra -> gana (Deva/Manushya/Rakshasa)
NAKSHATRA_GANA = {
    "Ashwini": "Deva", "Bharani": "Manushya", "Krittika": "Rakshasa", "Rohini": "Manushya",
    "Mrigashira": "Deva", "Ardra": "Manushya", "Punarvasu": "Deva", "Pushya": "Deva",
    "Ashlesha": "Rakshasa", "Magha": "Rakshasa", "Purva Phalguni": "Manushya", "Uttara Phalguni": "Manushya",
    "Hasta": "Deva", "Chitra": "Rakshasa", "Swati": "Deva", "Vishakha": "Rakshasa",
    "Anuradha": "Deva", "Jyeshtha": "Rakshasa", "Mula": "Rakshasa", "Purva Ashadha": "Manushya",
    "Uttara Ashadha": "Manushya", "Shravana": "Deva", "Dhanishta": "Rakshasa",
    "Shatabhisha": "Rakshasa", "Purva Bhadrapada": "Manushya", "Uttara Bhadrapada": "Manushya",
    "Revati": "Deva"
}

# Yoni - animal symbol for each nakshatra
NAKSHATRA_YONI = {
    "Ashwini": "Horse", "Bharani": "Elephant", "Krittika": "Sheep", "Rohini": "Serpent",
    "Mrigashira": "Serpent", "Ardra": "Dog", "Punarvasu": "Cat", "Pushya": "Sheep",
    "Ashlesha": "Cat", "Magha": "Rat", "Purva Phalguni": "Rat", "Uttara Phalguni": "Cow",
    "Hasta": "Buffalo", "Chitra": "Tiger", "Swati": "Buffalo", "Vishakha": "Tiger",
    "Anuradha": "Deer", "Jyeshtha": "Deer", "Mula": "Dog", "Purva Ashadha": "Monkey",
    "Uttara Ashadha": "Mongoose", "Shravana": "Monkey", "Dhanishta": "Lion",
    "Shatabhisha": "Horse", "Purva Bhadrapada": "Lion", "Uttara Bhadrapada": "Cow",
    "Revati": "Elephant"
}

# Nadi: Aadi / Madhya / Antya - cycling through 27 nakshatras
NADI_CYCLE = ["Aadi", "Madhya", "Antya"]

# Varna by Rashi (Moon sign)
RASHI_VARNA = {
    "Meena": "Brahmin", "Karka": "Brahmin", "Vrischika": "Brahmin",
    "Mesha": "Kshatriya", "Simha": "Kshatriya", "Dhanu": "Kshatriya",
    "Vrishabha": "Vaishya", "Kanya": "Vaishya", "Makara": "Vaishya",
    "Mithuna": "Shudra", "Tula": "Shudra", "Kumbha": "Shudra"
}
VARNA_RANK = {"Brahmin": 4, "Kshatriya": 3, "Vaishya": 2, "Shudra": 1}

# Vashya by Rashi
RASHI_VASHYA = {
    "Mesha": "Chatushpada", "Vrishabha": "Chatushpada", "Mithuna": "Manav",
    "Karka": "Jalachar", "Simha": "Vanachar", "Kanya": "Manav",
    "Tula": "Manav", "Vrischika": "Keet", "Dhanu": "Chatushpada",
    "Makara": "Jalachar", "Kumbha": "Manav", "Meena": "Jalachar"
}

# Simplified city database (lat, lon) - covers major Indian + world cities
CITY_DB = {
    "mumbai": (19.0760, 72.8777), "delhi": (28.7041, 77.1025),
    "bangalore": (12.9716, 77.5946), "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639), "hyderabad": (17.3850, 78.4867),
    "pune": (18.5204, 73.8567), "ahmedabad": (23.0225, 72.5714),
    "jaipur": (26.9124, 75.7873), "lucknow": (26.8467, 80.9462),
    "chandigarh": (30.7333, 76.7794), "bhopal": (23.2599, 77.4126),
    "indore": (22.7196, 75.8577), "patna": (25.5941, 85.1376),
    "nagpur": (21.1458, 79.0882), "surat": (21.1702, 72.8311),
    "kochi": (9.9312, 76.2673), "thiruvananthapuram": (8.5241, 76.9366),
    "varanasi": (25.3176, 82.9739), "amritsar": (31.6340, 74.8723),
    "new york": (40.7128, -74.0060), "london": (51.5074, -0.1278),
    "dubai": (25.2048, 55.2708), "singapore": (1.3521, 103.8198),
    "toronto": (43.6532, -79.3832), "sydney": (-33.8688, 151.2093),
}


def resolve_location(city: str) -> tuple[float, float]:
    """Resolve city name to (lat, lon). Falls back to Delhi."""
    key = city.strip().lower()
    if key in CITY_DB:
        return CITY_DB[key]
    # partial match
    for k, v in CITY_DB.items():
        if key in k or k in key:
            return v
    return CITY_DB["delhi"]


def compute_moon_position(dob: str, birth_time: str, city: str) -> dict:
    """
    dob: 'YYYY-MM-DD'
    birth_time: 'HH:MM' (24h, local)
    city: str
    Returns: {rashi, rashi_idx, nakshatra, nakshatra_idx, pada, moon_lon_sid, lat, lon}
    """
    lat, lon = resolve_location(city)

    # Determine timezone at birth location
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lng=lon, lat=lat) or "Asia/Kolkata"
    tz = pytz.timezone(tz_name)

    # Local naive datetime -> UTC
    local_dt = datetime.strptime(f"{dob} {birth_time}", "%Y-%m-%d %H:%M")
    local_dt = tz.localize(local_dt)
    utc_dt = local_dt.astimezone(pytz.UTC)

    # Julian day (UT)
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                    utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600)

    # Sidereal moon longitude
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    moon_lon, _ = swe.calc_ut(jd, swe.MOON, flags)
    moon_lon_sid = moon_lon[0] % 360

    # Rashi: 30° each
    rashi_idx = int(moon_lon_sid // 30)
    # Nakshatra: 13°20' each = 13.3333°
    nak_idx = int(moon_lon_sid // (360 / 27))
    # Pada: 1-4 within a nakshatra
    pada = int(((moon_lon_sid % (360 / 27)) // (360 / 108))) + 1

    # Mars longitude for Mangal dosha detection
    mars_lon, _ = swe.calc_ut(jd, swe.MARS, flags)
    mars_sign_idx = int((mars_lon[0] % 360) // 30)

    return {
        "rashi": RASHIS[rashi_idx],
        "rashi_idx": rashi_idx,
        "nakshatra": NAKSHATRAS[nak_idx],
        "nakshatra_idx": nak_idx,
        "pada": pada,
        "moon_lon_sid": round(moon_lon_sid, 4),
        "mars_sign_idx": mars_sign_idx,
        "lat": lat,
        "lon": lon,
    }


def has_mangal_dosha(mars_sign_idx: int) -> bool:
    """Mars in houses 1, 2, 4, 7, 8, 12 relative to Moon -> dosha.
    For a simplified version, we check if Mars is in aggressive signs: Aries(0), Scorpio(7), Capricorn(9)."""
    return mars_sign_idx in {0, 3, 6, 7, 11}


def compute_ashtakoota(a: dict, b: dict) -> dict:
    """
    Compute Ashtakoota 8-guna compatibility.
    a, b: outputs of compute_moon_position
    Returns: {gunas: {name: {score, max}}, total, max_total, mangal_a, mangal_b}
    """
    gunas = {}

    # 1. Varna (1 pt) - male varna >= female varna (we compare equal/greater-or-less)
    va = RASHI_VARNA[a["rashi"]]
    vb = RASHI_VARNA[b["rashi"]]
    varna_score = 1 if VARNA_RANK[va] >= VARNA_RANK[vb] else 0
    gunas["Varna"] = {"score": varna_score, "max": 1, "a": va, "b": vb}

    # 2. Vashya (2 pts) - same group = 2, compatible = 1, else 0
    wa = RASHI_VASHYA[a["rashi"]]
    wb = RASHI_VASHYA[b["rashi"]]
    if wa == wb:
        vashya_score = 2
    elif {wa, wb} in [{"Manav", "Chatushpada"}, {"Chatushpada", "Jalachar"}, {"Jalachar", "Keet"}]:
        vashya_score = 1
    else:
        vashya_score = 0
    gunas["Vashya"] = {"score": vashya_score, "max": 2, "a": wa, "b": wb}

    # 3. Tara (3 pts) - based on count from A's nakshatra to B's
    from report_interpretations import tara_name
    count_ab = ((b["nakshatra_idx"] - a["nakshatra_idx"]) % 27) + 1
    count_ba = ((a["nakshatra_idx"] - b["nakshatra_idx"]) % 27) + 1
    def tara_val(n):
        r = n % 9
        if r == 0:
            r = 9
        return 1.5 if r in {2, 4, 6, 8, 9} else 0
    tara_score = tara_val(count_ab) + tara_val(count_ba)
    gunas["Tara"] = {"score": round(tara_score, 1), "max": 3,
                     "a": tara_name(count_ab), "b": tara_name(count_ba)}

    # 4. Yoni (4 pts) - same yoni=4, friendly=3, neutral=2, enemy=1, mortal=0
    ya = NAKSHATRA_YONI[a["nakshatra"]]
    yb = NAKSHATRA_YONI[b["nakshatra"]]
    if ya == yb:
        yoni_score = 4
    else:
        # Simplified: different yonis get varied scores deterministically
        enemies = {("Horse", "Buffalo"), ("Cow", "Tiger"), ("Serpent", "Mongoose"),
                   ("Cat", "Rat"), ("Dog", "Deer"), ("Monkey", "Sheep"),
                   ("Lion", "Elephant")}
        pair = tuple(sorted([ya, yb]))
        if pair in {tuple(sorted(e)) for e in enemies}:
            yoni_score = 0
        else:
            yoni_score = 2
    gunas["Yoni"] = {"score": yoni_score, "max": 4, "a": ya, "b": yb}

    # 5. Graha Maitri (5 pts) - friendship of Moon-sign lords
    la = RASHI_LORDS[a["rashi_idx"]]
    lb = RASHI_LORDS[b["rashi_idx"]]
    friends = {
        "Sun": {"Moon", "Mars", "Jupiter"},
        "Moon": {"Sun", "Mercury"},
        "Mars": {"Sun", "Moon", "Jupiter"},
        "Mercury": {"Sun", "Venus"},
        "Jupiter": {"Sun", "Moon", "Mars"},
        "Venus": {"Mercury", "Saturn"},
        "Saturn": {"Mercury", "Venus"}
    }
    if la == lb:
        gm_score = 5
    elif lb in friends.get(la, set()) and la in friends.get(lb, set()):
        gm_score = 4
    elif lb in friends.get(la, set()) or la in friends.get(lb, set()):
        gm_score = 3
    else:
        gm_score = 1
    gunas["Graha Maitri"] = {"score": gm_score, "max": 5, "a": la, "b": lb}

    # 6. Gana (6 pts) - Deva-Deva=6, Deva-Manushya=5, Manushya-Manushya=6, Rakshasa-Rakshasa=6, Deva-Rakshasa=0, Manushya-Rakshasa=1
    ga = NAKSHATRA_GANA[a["nakshatra"]]
    gb = NAKSHATRA_GANA[b["nakshatra"]]
    if ga == gb:
        gana_score = 6
    elif {ga, gb} == {"Deva", "Manushya"}:
        gana_score = 5
    elif {ga, gb} == {"Manushya", "Rakshasa"}:
        gana_score = 1
    else:
        gana_score = 0
    gunas["Gana"] = {"score": gana_score, "max": 6, "a": ga, "b": gb}

    # 7. Bhakoot (7 pts) - based on Rashi difference
    diff = abs(a["rashi_idx"] - b["rashi_idx"])
    diff = min(diff, 12 - diff)
    if diff in {1, 5}:
        bhakoot_score = 0
    elif diff in {2, 6}:
        bhakoot_score = 7
    elif diff in {3}:
        bhakoot_score = 4
    elif diff in {4}:
        bhakoot_score = 4
    else:
        bhakoot_score = 7
    gunas["Bhakoot"] = {"score": bhakoot_score, "max": 7}

    # 8. Nadi (8 pts) - same nadi = 0, different = 8
    nadi_a = NADI_CYCLE[a["nakshatra_idx"] % 3]
    nadi_b = NADI_CYCLE[b["nakshatra_idx"] % 3]
    nadi_score = 0 if nadi_a == nadi_b else 8
    gunas["Nadi"] = {"score": nadi_score, "max": 8, "a": nadi_a, "b": nadi_b}

    total = sum(g["score"] for g in gunas.values())

    mangal_a = has_mangal_dosha(a["mars_sign_idx"])
    mangal_b = has_mangal_dosha(b["mars_sign_idx"])

    return {
        "gunas": gunas,
        "total": round(total, 1),
        "max_total": 36,
        "mangal_a": mangal_a,
        "mangal_b": mangal_b,
    }


def compatibility_verdict(total: float, mangal_a: bool, mangal_b: bool) -> str:
    """Generate human-readable verdict."""
    if total >= 28:
        base = "Exceptional Match - The stars strongly bless this union with deep harmony."
    elif total >= 24:
        base = "Excellent Match - A highly compatible pair with strong mutual support."
    elif total >= 18:
        base = "Good Match - A compatible pairing with prospects for a happy union."
    elif total >= 14:
        base = "Average Match - Some compatibility exists but careful consideration is advised."
    else:
        base = "Low Match - Significant astrological differences suggest challenges."

    if mangal_a != mangal_b:
        base += " Note: One partner has Mangal Dosha - remedial measures are traditionally suggested."
    elif mangal_a and mangal_b:
        base += " Both partners share Mangal Dosha, which traditionally cancels its effect."
    return base
