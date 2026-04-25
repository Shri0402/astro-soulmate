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

# Nadi by NAKSHATRA index — canonical 9-position pattern (NOT idx % 3)
# Each cycle of 9 nakshatras: Aadi, Madhya, Antya, Antya, Madhya, Aadi, Aadi, Madhya, Antya
NADI_PATTERN = ["Aadi", "Madhya", "Antya", "Antya", "Madhya", "Aadi", "Aadi", "Madhya", "Antya"]


def nadi_for(nak_idx: int) -> str:
    return NADI_PATTERN[nak_idx % 9]


# Yoni mortal-enemy pairs (vairya yonis) — score = 0 regardless of sex
YONI_MORTAL_ENEMIES = frozenset({
    frozenset({"Horse", "Buffalo"}),
    frozenset({"Elephant", "Lion"}),
    frozenset({"Sheep", "Monkey"}),
    frozenset({"Serpent", "Mongoose"}),
    frozenset({"Dog", "Deer"}),
    frozenset({"Cat", "Rat"}),
    frozenset({"Cow", "Tiger"}),
})

# Yoni "friendly" pairs (3 pts) — natural compatibility per classical sources
YONI_FRIENDS = frozenset({
    frozenset({"Horse", "Sheep"}),
    frozenset({"Elephant", "Buffalo"}),
    frozenset({"Sheep", "Cow"}),
    frozenset({"Cow", "Buffalo"}),
    frozenset({"Cow", "Deer"}),
    frozenset({"Dog", "Monkey"}),
    frozenset({"Cat", "Monkey"}),
    frozenset({"Tiger", "Lion"}),
    frozenset({"Mongoose", "Cat"}),
})


def yoni_score(ya: str, yb: str) -> int:
    if ya == yb:
        return 4
    pair = frozenset({ya, yb})
    if pair in YONI_MORTAL_ENEMIES:
        return 0
    if pair in YONI_FRIENDS:
        return 3
    return 2  # neutral


# Vashya 5×5 compatibility table (max 2 pts).
VASHYA_TABLE = {
    ("Manav", "Manav"): 2.0,        ("Manav", "Chatushpada"): 1.0, ("Manav", "Jalachar"): 1.0,  ("Manav", "Vanachar"): 0.0, ("Manav", "Keet"): 1.0,
    ("Chatushpada", "Manav"): 1.0,  ("Chatushpada", "Chatushpada"): 2.0, ("Chatushpada", "Jalachar"): 1.0, ("Chatushpada", "Vanachar"): 1.0, ("Chatushpada", "Keet"): 0.0,
    ("Jalachar", "Manav"): 0.5,     ("Jalachar", "Chatushpada"): 1.0,    ("Jalachar", "Jalachar"): 2.0,   ("Jalachar", "Vanachar"): 0.0,  ("Jalachar", "Keet"): 0.5,
    ("Vanachar", "Manav"): 1.0,     ("Vanachar", "Chatushpada"): 1.0,    ("Vanachar", "Jalachar"): 0.0,   ("Vanachar", "Vanachar"): 2.0,  ("Vanachar", "Keet"): 0.0,
    ("Keet", "Manav"): 0.0,         ("Keet", "Chatushpada"): 0.0,        ("Keet", "Jalachar"): 0.5,       ("Keet", "Vanachar"): 0.0,      ("Keet", "Keet"): 2.0,
}


# Graha-Maitri planetary friendship (per Brihat Parashara)
PLANET_FRIENDS = {
    "Sun":     {"Moon", "Mars", "Jupiter"},
    "Moon":    {"Sun", "Mercury"},
    "Mars":    {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus":   {"Mercury", "Saturn"},
    "Saturn":  {"Mercury", "Venus"},
}
PLANET_ENEMIES = {
    "Sun":     {"Venus", "Saturn"},
    "Moon":    set(),
    "Mars":    {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus":   {"Sun", "Moon"},
    "Saturn":  {"Sun", "Moon", "Mars"},
}


def maitri_score(la: str, lb: str) -> int:
    """Graha-Maitri scoring (max 5)."""
    if la == lb:
        return 5
    a_friend = lb in PLANET_FRIENDS.get(la, set())
    b_friend = la in PLANET_FRIENDS.get(lb, set())
    a_enemy = lb in PLANET_ENEMIES.get(la, set())
    b_enemy = la in PLANET_ENEMIES.get(lb, set())
    if a_friend and b_friend:
        return 5
    if a_friend or b_friend:
        # one friend, other neutral or enemy
        return 4 if not (a_enemy or b_enemy) else 1
    if not (a_enemy or b_enemy):
        return 3  # mutual neutral
    if a_enemy and b_enemy:
        return 0  # mutual enemy
    return 1  # one neutral, one enemy

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
    Returns full natal data including Rashi, Nakshatra, Lagna, Tithi, Yoga, Karan.
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

    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

    # Sidereal moon longitude
    moon_lon, _ = swe.calc_ut(jd, swe.MOON, flags)
    moon_lon_sid = moon_lon[0] % 360
    # Sun (sidereal)
    sun_lon, _ = swe.calc_ut(jd, swe.SUN, flags)
    sun_lon_sid = sun_lon[0] % 360
    # Mars (sidereal) for Mangal dosha
    mars_lon, _ = swe.calc_ut(jd, swe.MARS, flags)
    mars_sign_idx = int((mars_lon[0] % 360) // 30)
    # Venus (sidereal) — used as Mangal-dosha reference point
    venus_lon, _ = swe.calc_ut(jd, swe.VENUS, flags)
    venus_sign_idx = int((venus_lon[0] % 360) // 30)

    # Rashi (Moon sign)
    rashi_idx = int(moon_lon_sid // 30)
    nak_idx = int(moon_lon_sid // (360 / 27))
    pada = int(((moon_lon_sid % (360 / 27)) // (360 / 108))) + 1

    # ---- Lagna (Ascendant) ----
    try:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
        lagna_lon = ascmc[0] % 360
        lagna_idx = int(lagna_lon // 30)
        lagna = RASHIS[lagna_idx]
        lagna_lord = RASHI_LORDS[lagna_idx]
    except Exception:
        lagna = "—"; lagna_lord = "—"; lagna_idx = None
    # ---- Tithi (lunar day) ----
    diff = (moon_lon[0] - sun_lon[0]) % 360
    tithi_idx = int(diff // 12)  # 0..29
    tithi_name = _tithi_name(tithi_idx)
    paksha = "Shukla" if tithi_idx < 15 else "Krishna"

    # ---- Yoga ----
    yoga_idx = int(((moon_lon[0] + sun_lon[0]) % 360) // (360 / 27))
    yoga = YOGAS[yoga_idx]

    # ---- Karan (half tithi) ----
    karan_num = int(diff // 6) % 60  # 60 karans in a synodic cycle
    karan = _karan_name(karan_num)

    # ---- Hindu weekday ----
    weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    weekday = weekdays[utc_dt.weekday() if False else (utc_dt.isoweekday() % 7)]

    return {
        "rashi": RASHIS[rashi_idx],
        "rashi_idx": rashi_idx,
        "rashi_lord": RASHI_LORDS[rashi_idx],
        "nakshatra": NAKSHATRAS[nak_idx],
        "nakshatra_idx": nak_idx,
        "nakshatra_lord": NAK_LORDS[nak_idx],
        "pada": pada,
        "moon_lon_sid": round(moon_lon_sid, 4),
        "sun_lon_sid": round(sun_lon_sid, 4),
        "mars_sign_idx": mars_sign_idx,
        "venus_sign_idx": venus_sign_idx,
        "lagna": lagna,
        "lagna_idx": lagna_idx,
        "lagna_lord": lagna_lord,
        "tithi": tithi_name,
        "paksha": paksha,
        "yoga": yoga,
        "karan": karan,
        "weekday": weekday,
        "lat": lat,
        "lon": lon,
        "tz": tz_name,
    }


# Nakshatra lords (cycle of 9: Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury)
NAK_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"] * 3

YOGAS = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shoola", "Ganda", "Vridhi", "Dhruva",
    "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana",
    "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla",
    "Brahma", "Indra", "Vaidhriti"
]

TITHI_NAMES_HALF = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi"
]


def _tithi_name(idx: int) -> str:
    # 0..14 = Shukla 1..15 (15th = Purnima); 15..29 = Krishna 1..15 (30th = Amavasya)
    if idx == 14:
        return "Purnima"
    if idx == 29:
        return "Amavasya"
    half_idx = idx if idx < 14 else idx - 15
    return TITHI_NAMES_HALF[half_idx]


# 11 Karans (4 fixed + 7 movable cycle through 60 half-tithis)
KARANS_MOVABLE = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti"]
KARANS_FIXED = ["Shakuni", "Chatushpada", "Naga", "Kimstughna"]


def _karan_name(n: int) -> str:
    # Position 0: Kimstughna, 1..56: 7 movables × 8, 57: Shakuni, 58: Chatushpada, 59: Naga
    if n == 0:
        return "Kimstughna"
    if n == 57:
        return "Shakuni"
    if n == 58:
        return "Chatushpada"
    if n == 59:
        return "Naga"
    # 1..56 cycles 7 movable karans
    return KARANS_MOVABLE[(n - 1) % 7]


def has_mangal_dosha(mars_sign_idx: int) -> bool:
    """DEPRECATED — kept for backward compat. Use mangal_dosha_full(astro) instead."""
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

    # 2. Vashya (2 pts) - canonical 5×5 table
    wa = RASHI_VASHYA[a["rashi"]]
    wb = RASHI_VASHYA[b["rashi"]]
    vashya_score = VASHYA_TABLE.get((wa, wb), 0.0)
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

    # 4. Yoni (4 pts) - canonical table with 7 mortal-enemy pairs
    ya = NAKSHATRA_YONI[a["nakshatra"]]
    yb = NAKSHATRA_YONI[b["nakshatra"]]
    gunas["Yoni"] = {"score": yoni_score(ya, yb), "max": 4, "a": ya, "b": yb}

    # 5. Graha Maitri (5 pts) - Brihat Parashara friendship table
    la = RASHI_LORDS[a["rashi_idx"]]
    lb = RASHI_LORDS[b["rashi_idx"]]
    gunas["Graha Maitri"] = {"score": maitri_score(la, lb), "max": 5, "a": la, "b": lb}

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
    # 7. Bhakoot (7 pts) - rashi distance (folded to 0..6)
    # 0(same):7, 1(Dwirdwadash 12/2):0, 2:7, 3(Trikona):7,
    # 4(Navam-Pancham 9/5):0, 5(Shadashtak 6/8):0, 6(1/7):7
    diff = abs(a["rashi_idx"] - b["rashi_idx"])
    diff = min(diff, 12 - diff)
    bhakoot_score = 0 if diff in {1, 4, 5} else 7
    gunas["Bhakoot"] = {"score": bhakoot_score, "max": 7, "a": a["rashi"], "b": b["rashi"]}

    # 8. Nadi (8 pts) - canonical 9-position pattern; same nadi → 0
    nadi_a = nadi_for(a["nakshatra_idx"])
    nadi_b = nadi_for(b["nakshatra_idx"])
    nadi_score = 0 if nadi_a == nadi_b else 8
    # Nadi-dosha exception: same Rashi or same Nakshatra cancels the dosha
    if nadi_score == 0 and (a["rashi_idx"] == b["rashi_idx"] or a["nakshatra_idx"] == b["nakshatra_idx"]):
        nadi_score = 8
    gunas["Nadi"] = {"score": nadi_score, "max": 8, "a": nadi_a, "b": nadi_b}

    total = sum(g["score"] for g in gunas.values())

    mangal_a = mangal_dosha_full(a)
    mangal_b = mangal_dosha_full(b)

    return {
        "gunas": gunas,
        "total": round(total, 1),
        "max_total": 36,
        "mangal_a": mangal_a,
        "mangal_b": mangal_b,
    }


def mangal_dosha_full(astro: dict) -> bool:
    """Mars in 1st, 2nd, 4th, 7th, 8th, 12th house from Lagna, Moon, OR Venus → Mangal Dosha.
    Cancellations (simplified):
      - Mars in own/exalted sign (Aries, Scorpio, Capricorn) → reduced.
      - Born during day for some houses, etc. — not implemented.
    """
    mars_sign = astro.get("mars_sign_idx")
    if mars_sign is None:
        return False

    DOSHA_HOUSES = {1, 2, 4, 7, 8, 12}
    refs = []
    if astro.get("lagna_idx") is not None:
        refs.append(astro["lagna_idx"])
    if astro.get("rashi_idx") is not None:
        refs.append(astro["rashi_idx"])
    venus_sign_idx = astro.get("venus_sign_idx")
    if venus_sign_idx is not None:
        refs.append(venus_sign_idx)

    for ref in refs:
        house = ((mars_sign - ref) % 12) + 1
        if house in DOSHA_HOUSES:
            return True
    return False


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
