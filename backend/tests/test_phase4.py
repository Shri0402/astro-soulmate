"""Phase-4: Astrology engine fixes + Password reset flow."""
import os
import sys
import pytest
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from astrology import (
    nadi_for, NADI_PATTERN, yoni_score, YONI_MORTAL_ENEMIES, YONI_FRIENDS,
    VASHYA_TABLE, maitri_score, mangal_dosha_full, compute_ashtakoota,
    compute_moon_position,
)

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    # fall back to frontend env
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL="):
                BASE_URL = line.split("=", 1)[1].strip().rstrip("/")


# ------------------ Astrology engine unit tests ------------------
class TestNadiPattern:
    def test_pattern_length(self):
        assert len(NADI_PATTERN) == 9

    def test_canonical_positions(self):
        # nadi_for(0) == 'Aadi'
        assert nadi_for(0) == "Aadi"
        # nadi_for(2) == 'Antya'
        assert nadi_for(2) == "Antya"
        # nadi_for(8) == 'Antya'
        assert nadi_for(8) == "Antya"
        # nadi_for(16) → 16 % 9 = 7 → 'Madhya'
        assert nadi_for(16) == "Madhya"

    def test_anuradha_madhya(self):
        # Anuradha is nakshatra index 16 → Madhya
        from astrology import NAKSHATRAS
        idx = NAKSHATRAS.index("Anuradha")
        assert idx == 16
        assert nadi_for(idx) == "Madhya"


class TestYoniScore:
    def test_same_yoni(self):
        assert yoni_score("Horse", "Horse") == 4

    def test_mortal_enemies(self):
        for pair in YONI_MORTAL_ENEMIES:
            a, b = list(pair)
            assert yoni_score(a, b) == 0
            assert yoni_score(b, a) == 0

    def test_friends(self):
        for pair in YONI_FRIENDS:
            a, b = list(pair)
            if a != b:
                assert yoni_score(a, b) == 3

    def test_neutral(self):
        # Horse vs Cat — not in mortal enemies, not in friends
        assert yoni_score("Horse", "Cat") == 2


class TestVashya:
    def test_table_values(self):
        assert VASHYA_TABLE[("Manav", "Manav")] == 2.0
        assert VASHYA_TABLE[("Manav", "Vanachar")] == 0.0
        assert VASHYA_TABLE[("Jalachar", "Jalachar")] == 2.0


class TestMaitri:
    def test_same_lord(self):
        assert maitri_score("Sun", "Sun") == 5

    def test_mutual_friends(self):
        # Sun & Moon mutually friend
        assert maitri_score("Sun", "Moon") == 5

    def test_mutual_enemies(self):
        # Sun & Saturn: Sun has Saturn as enemy; Saturn has Sun as enemy
        assert maitri_score("Sun", "Saturn") == 0

    def test_one_friend_one_neutral(self):
        # Moon's friends: Sun, Mercury. Mercury's friends: Sun, Venus.
        # Moon→Mercury: friend; Mercury→Moon: enemy → mixed (1)
        assert maitri_score("Moon", "Mercury") == 1


class TestBhakoot:
    def test_diff_table(self):
        # construct minimal astro dicts
        def mk(rashi_idx, nak_idx=0):
            from astrology import RASHIS, RASHI_LORDS, NAKSHATRAS
            return {
                "rashi": RASHIS[rashi_idx], "rashi_idx": rashi_idx,
                "rashi_lord": RASHI_LORDS[rashi_idx],
                "nakshatra": NAKSHATRAS[nak_idx], "nakshatra_idx": nak_idx,
                "mars_sign_idx": 0, "lagna_idx": 0, "venus_sign_idx": 0,
            }

        # diff 0 → 7
        assert compute_ashtakoota(mk(0), mk(0))["gunas"]["Bhakoot"]["score"] == 7
        # diff 1 → 0
        assert compute_ashtakoota(mk(0), mk(1))["gunas"]["Bhakoot"]["score"] == 0
        # diff 2 → 7
        assert compute_ashtakoota(mk(0), mk(2))["gunas"]["Bhakoot"]["score"] == 7
        # diff 3 → 7
        assert compute_ashtakoota(mk(0), mk(3))["gunas"]["Bhakoot"]["score"] == 7
        # diff 4 → 0
        assert compute_ashtakoota(mk(0), mk(4))["gunas"]["Bhakoot"]["score"] == 0
        # diff 5 → 0
        assert compute_ashtakoota(mk(0), mk(5))["gunas"]["Bhakoot"]["score"] == 0
        # diff 6 → 7
        assert compute_ashtakoota(mk(0), mk(6))["gunas"]["Bhakoot"]["score"] == 7
        # diff 11 → folds to 1 → 0
        assert compute_ashtakoota(mk(0), mk(11))["gunas"]["Bhakoot"]["score"] == 0


class TestMangalDosha:
    def test_mars_in_dosha_house_from_lagna(self):
        # mars_sign_idx=0 lagna=0 → house 1 → dosha
        astro = {"mars_sign_idx": 0, "lagna_idx": 0, "rashi_idx": 5, "venus_sign_idx": 5}
        assert mangal_dosha_full(astro) is True

    def test_no_dosha(self):
        # Mars house from all refs in safe houses
        # mars=2 lagna=0 → house 3 (safe); mars=2 moon(rashi)=0 → house 3 (safe);
        # mars=2 venus=0 → house 3 (safe)
        astro = {"mars_sign_idx": 2, "lagna_idx": 0, "rashi_idx": 0, "venus_sign_idx": 0}
        assert mangal_dosha_full(astro) is False

    def test_dosha_from_venus(self):
        # mars in 7th from venus only
        astro = {"mars_sign_idx": 6, "lagna_idx": 2, "rashi_idx": 2, "venus_sign_idx": 0}
        assert mangal_dosha_full(astro) is True


class TestComputeMoonPosition:
    def test_includes_lagna_and_venus(self):
        out = compute_moon_position("1998-08-02", "10:30", "Mumbai")
        assert "lagna_idx" in out
        assert "venus_sign_idx" in out
        assert "mars_sign_idx" in out
        assert isinstance(out["venus_sign_idx"], int)
        assert 0 <= out["venus_sign_idx"] < 12


class TestNadiInAshtakoota:
    def test_same_nadi_zero(self):
        # Two members in same nadi (and not same rashi/nakshatra) → 0
        from astrology import NAKSHATRAS, RASHIS, RASHI_LORDS
        # Find two indices with same nadi (mod 9) but different rashi
        # idx 0 (Aadi) and idx 5 (Aadi) — different rashis
        a = {"rashi": RASHIS[0], "rashi_idx": 0, "rashi_lord": RASHI_LORDS[0],
             "nakshatra": NAKSHATRAS[0], "nakshatra_idx": 0,
             "mars_sign_idx": 0, "lagna_idx": 0, "venus_sign_idx": 0}
        b = {"rashi": RASHIS[3], "rashi_idx": 3, "rashi_lord": RASHI_LORDS[3],
             "nakshatra": NAKSHATRAS[5], "nakshatra_idx": 5,
             "mars_sign_idx": 0, "lagna_idx": 0, "venus_sign_idx": 0}
        # both in Aadi
        assert nadi_for(0) == "Aadi"
        assert nadi_for(5) == "Aadi"
        result = compute_ashtakoota(a, b)
        assert result["gunas"]["Nadi"]["score"] == 0

    def test_different_nadi_eight(self):
        from astrology import NAKSHATRAS, RASHIS, RASHI_LORDS
        a = {"rashi": RASHIS[0], "rashi_idx": 0, "rashi_lord": RASHI_LORDS[0],
             "nakshatra": NAKSHATRAS[0], "nakshatra_idx": 0,
             "mars_sign_idx": 0, "lagna_idx": 0, "venus_sign_idx": 0}
        b = {"rashi": RASHIS[3], "rashi_idx": 3, "rashi_lord": RASHI_LORDS[3],
             "nakshatra": NAKSHATRAS[1], "nakshatra_idx": 1,
             "mars_sign_idx": 0, "lagna_idx": 0, "venus_sign_idx": 0}
        # Aadi vs Madhya
        assert nadi_for(0) == "Aadi"
        assert nadi_for(1) == "Madhya"
        result = compute_ashtakoota(a, b)
        assert result["gunas"]["Nadi"]["score"] == 8

    def test_same_rashi_cancellation(self):
        from astrology import NAKSHATRAS, RASHIS, RASHI_LORDS
        # Same rashi, same nadi — should cancel to 8
        a = {"rashi": RASHIS[0], "rashi_idx": 0, "rashi_lord": RASHI_LORDS[0],
             "nakshatra": NAKSHATRAS[0], "nakshatra_idx": 0,
             "mars_sign_idx": 0, "lagna_idx": 0, "venus_sign_idx": 0}
        b = {"rashi": RASHIS[0], "rashi_idx": 0, "rashi_lord": RASHI_LORDS[0],
             "nakshatra": NAKSHATRAS[5], "nakshatra_idx": 5,
             "mars_sign_idx": 0, "lagna_idx": 0, "venus_sign_idx": 0}
        result = compute_ashtakoota(a, b)
        # both Aadi (same nadi) BUT same rashi → cancellation → 8
        assert result["gunas"]["Nadi"]["score"] == 8


# ------------------ Backend integration: matches sanity ------------------
@pytest.fixture(scope="module")
def member_session():
    """Try login Shakuntala — could be 02081998 or 03081998 (mutated by prior agent)."""
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    for pwd in ["02081998", "03081998"]:
        r = s.post(f"{BASE_URL}/api/auth/login", json={"email": "123@gmail.com", "password": pwd})
        if r.status_code == 200:
            return s
    pytest.skip("Cannot login as Shakuntala")


class TestMatchesSanity:
    def test_matches_within_bounds(self, member_session):
        r = member_session.get(f"{BASE_URL}/api/matches")
        assert r.status_code == 200
        data = r.json()
        if data.get("status") != "ready":
            pytest.skip(f"Matches status: {data.get('status')}")
        max_per_guna = {"Varna": 1, "Vashya": 2, "Tara": 3, "Yoni": 4,
                        "Graha Maitri": 5, "Gana": 6, "Bhakoot": 7, "Nadi": 8}
        for m in data["matches"]:
            assert m["score"] <= 36, f"score {m['score']} > 36 for {m.get('match_name')}"
            assert m["score"] >= 0
            for gname, g in m["breakdown"].items():
                assert g["score"] <= max_per_guna[gname], f"{gname}={g['score']} > {max_per_guna[gname]}"
                assert g["score"] >= 0


# ------------------ Password reset flow ------------------
class TestPasswordReset:
    def test_unknown_email_no_leak(self):
        r = requests.post(f"{BASE_URL}/api/auth/forgot-password",
                          json={"email": "unknown_xyz@nowhere.com"})
        assert r.status_code == 200
        data = r.json()
        assert "message" in data
        assert "dev_link" not in data, "Should NOT leak dev_link for unknown email"

    def test_known_email_dev_link(self):
        r = requests.post(f"{BASE_URL}/api/auth/forgot-password",
                          json={"email": "michaelanthonyssj5@gmail.com"})
        assert r.status_code == 200
        data = r.json()
        assert "dev_link" in data, "RESEND_API_KEY empty → expect dev_link in response"
        assert "/reset-password/" in data["dev_link"]

    def test_short_password_422(self):
        r = requests.post(f"{BASE_URL}/api/auth/reset-password",
                          json={"token": "fake", "new_password": "abc"})
        assert r.status_code == 422

    def test_invalid_token_400(self):
        r = requests.post(f"{BASE_URL}/api/auth/reset-password",
                          json={"token": "definitely-not-real", "new_password": "abcdef"})
        assert r.status_code == 400

    def test_full_reset_flow_michael(self):
        """Use Michael (won't disrupt Shakuntala). Reset → login new → restore old."""
        EMAIL = "michaelanthonyssj5@gmail.com"
        OLD_PWD = "07012000"
        NEW_PWD = "TestNew@2026"

        # 1. forgot
        r = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={"email": EMAIL})
        assert r.status_code == 200
        link = r.json().get("dev_link")
        assert link
        token = link.rsplit("/", 1)[-1]

        # 2. reset with valid token
        s = requests.Session()
        r = s.post(f"{BASE_URL}/api/auth/reset-password",
                   json={"token": token, "new_password": NEW_PWD})
        assert r.status_code == 200
        data = r.json()
        assert data.get("email") == EMAIL
        # Auth cookies set on session
        assert any(c.name in ("access_token", "refresh_token") for c in s.cookies)

        # 3. token reuse → 400
        r2 = requests.post(f"{BASE_URL}/api/auth/reset-password",
                           json={"token": token, "new_password": NEW_PWD})
        assert r2.status_code == 400

        # 4. old password no longer works
        r3 = requests.post(f"{BASE_URL}/api/auth/login",
                           json={"email": EMAIL, "password": OLD_PWD})
        assert r3.status_code == 401, "Old password should NOT work after reset"

        # 5. new password works
        r4 = requests.post(f"{BASE_URL}/api/auth/login",
                           json={"email": EMAIL, "password": NEW_PWD})
        assert r4.status_code == 200

        # 6. restore old password via another reset (cleanup)
        r5 = requests.post(f"{BASE_URL}/api/auth/forgot-password", json={"email": EMAIL})
        token2 = r5.json()["dev_link"].rsplit("/", 1)[-1]
        r6 = requests.post(f"{BASE_URL}/api/auth/reset-password",
                           json={"token": token2, "new_password": OLD_PWD})
        assert r6.status_code == 200
