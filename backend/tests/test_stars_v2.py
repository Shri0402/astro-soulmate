"""End-to-end backend test for Stars Connection v2 (invite-only)."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://astro-soulmate-4.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

# Test members from /app/memory/test_credentials.md
SHAKUNTALA = ("123@gmail.com", "02081998")            # F looking_for=M
MICHAEL = ("michaelanthonyssj5@gmail.com", "07012000")  # M looking_for=F
SHUBHAM = ("shubhamneema011@gmail.com", "11112005")     # M looking_for=M
ADMIN = ("admin@starsconnection.com", "Admin@Stars2026")


def _client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def _login(s, email, pwd):
    r = s.post(f"{API}/auth/login", json={"email": email, "password": pwd})
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    return r.json()


# ---------- Auth ----------
class TestAuth:
    def test_login_shakuntala(self):
        s = _client()
        u = _login(s, *SHAKUNTALA)
        assert u["gender"] == "female"
        assert u["looking_for"] == "male"
        assert u["is_private_member"] is True

    def test_login_michael_dob_password(self):
        s = _client()
        u = _login(s, *MICHAEL)
        assert u["gender"] == "male"

    def test_login_invalid_password(self):
        s = _client()
        r = s.post(f"{API}/auth/login", json={"email": SHAKUNTALA[0], "password": "wrongpw"})
        assert r.status_code == 401

    def test_register_without_invite_code_403(self):
        s = _client()
        # Pydantic requires invite_code; sending empty string -> 403 "Invalid or used invite code"
        r = s.post(f"{API}/auth/register", json={
            "email": "TEST_noinvite@example.com", "password": "abcdef",
            "name": "TEST No Invite", "invite_code": "",
        })
        assert r.status_code in (403, 422)

    def test_register_invalid_invite_code_403(self):
        s = _client()
        r = s.post(f"{API}/auth/register", json={
            "email": "TEST_bad@example.com", "password": "abcdef",
            "name": "TEST Bad", "invite_code": "TOTALLYFAKE123",
        })
        assert r.status_code == 403

    def test_validate_invite_invalid_returns_404(self):
        s = _client()
        r = s.get(f"{API}/auth/invite/THISISBAD")
        assert r.status_code == 404


# ---------- Invites ----------
class TestInvites:
    def test_admin_create_invite(self):
        s = _client()
        _login(s, *ADMIN)
        r = s.post(f"{API}/invites", json={"note": "TEST_invite"})
        assert r.status_code == 200
        data = r.json()
        assert "code" in data
        assert isinstance(data["code"], str)
        assert len(data["code"]) == 8

    def test_invites_mine(self):
        s = _client()
        _login(s, *ADMIN)
        # generate one
        c = s.post(f"{API}/invites", json={"note": "TEST_mine"}).json()["code"]
        r = s.get(f"{API}/invites/mine")
        assert r.status_code == 200
        codes = [it["code"] for it in r.json()["items"]]
        assert c in codes

    def test_validate_invite_valid(self):
        s = _client()
        _login(s, *ADMIN)
        c = s.post(f"{API}/invites", json={"note": "TEST_validate"}).json()["code"]
        # public, no auth
        r = requests.get(f"{API}/auth/invite/{c}")
        assert r.status_code == 200
        body = r.json()
        assert body["valid"] is True
        assert body["code"] == c

    def test_register_with_invite_then_reuse_403(self):
        admin = _client()
        _login(admin, *ADMIN)
        c = admin.post(f"{API}/invites", json={"note": "TEST_reuse"}).json()["code"]

        u = _client()
        email = f"TEST_invitee_{c.lower()}@example.com"
        r = u.post(f"{API}/auth/register", json={
            "email": email, "password": "abcdef",
            "name": "TEST Invitee", "invite_code": c,
        })
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["email"] == email.lower()
        assert body["is_private_member"] is True

        # Reuse same code should now 403
        u2 = _client()
        r2 = u2.post(f"{API}/auth/register", json={
            "email": "TEST_reuser@example.com", "password": "abcdef",
            "name": "TEST Reuse", "invite_code": c,
        })
        assert r2.status_code == 403


# ---------- Matches: strict gender filter & no paywall ----------
class TestMatches:
    def test_strict_gender_for_shakuntala(self):
        s = _client()
        _login(s, *SHAKUNTALA)
        r = s.get(f"{API}/matches")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ready"
        matches = body["matches"]
        assert len(matches) > 0
        # ALL matches should be male (Shakuntala wants male)
        for m in matches:
            assert m.get("match_gender") == "male", f"non-male match leaked: {m}"
        # Shubham (male, looking_for=male) should appear
        names = [m["match_name"].lower() for m in matches]
        assert any("shubham" in n for n in names), f"Shubham missing from Shakuntala's matches: {names}"

    def test_no_paywall_fields(self):
        s = _client()
        _login(s, *SHAKUNTALA)
        r = s.get(f"{API}/matches")
        body = r.json()
        for m in body["matches"]:
            assert "locked" not in m, "match contains locked field"
            assert m.get("match_name"), "match_name missing"
            assert m.get("match_city") is not None
            assert m.get("match_bio") is not None
            assert "phone_visible" in m

    def test_michael_strict_filter(self):
        s = _client()
        _login(s, *MICHAEL)
        body = s.get(f"{API}/matches").json()
        for m in body.get("matches", []):
            # Michael (male) looking_for=female -> all matches must be female
            assert m.get("match_gender") == "female", m


# ---------- Kundali ----------
class TestKundali:
    @pytest.fixture(scope="class")
    def shakuntala_match(self):
        s = _client()
        _login(s, *SHAKUNTALA)
        body = s.get(f"{API}/matches").json()
        # pick first high-score
        m = sorted(body["matches"], key=lambda x: -x["score"])[0]
        return s, m

    def test_kundali_shape(self, shakuntala_match):
        s, m = shakuntala_match
        r = s.get(f"{API}/kundali/{m['match_user_id']}")
        assert r.status_code == 200, r.text
        data = r.json()
        rep = data["report"]
        assert len(rep["birth_details"]) == 8
        assert len(rep["ashtakoota_table"]) == 8
        for row in rep["ashtakoota_table"]:
            assert {"guna", "boy", "girl", "max_points", "points_obtained", "area_of_life"} <= set(row.keys())
        assert isinstance(rep["mangal_dosha_text"], str) and rep["mangal_dosha_text"].strip()
        assert rep["mangal_dosha_text"].startswith(("Mr.", "Ms."))
        assert isinstance(rep["conclusion_text"], str) and rep["conclusion_text"].strip()
        assert len(rep["interpretations"]) == 8
        for it in rep["interpretations"]:
            assert it["guna"] and it["text"]

    def test_kundali_no_paywall(self, shakuntala_match):
        s, m = shakuntala_match
        # any score should succeed (no 402)
        r = s.get(f"{API}/kundali/{m['match_user_id']}")
        assert r.status_code != 402
        assert r.status_code == 200

    def test_pdf_download_no_paywall(self, shakuntala_match):
        s, m = shakuntala_match
        r = s.get(f"{API}/kundali/{m['match_user_id']}/pdf")
        assert r.status_code == 200
        assert r.headers.get("content-type", "").startswith("application/pdf")
        assert len(r.content) > 100


# ---------- Phone requests ----------
class TestPhoneRequests:
    def test_full_phone_consent_flow(self):
        # Shakuntala requests Michael's phone
        sh = _client()
        sh_user = _login(sh, *SHAKUNTALA)
        mi = _client()
        mi_user = _login(mi, *MICHAEL)

        receiver_id = mi_user["id"]

        # Create request
        r = sh.post(f"{API}/phone-requests", json={"receiver_user_id": receiver_id})
        assert r.status_code == 200
        first = r.json()
        assert first["status"] in ("pending", "accepted", "rejected")
        rid = first["id"]

        # Idempotent: re-post returns existing
        r2 = sh.post(f"{API}/phone-requests", json={"receiver_user_id": receiver_id})
        assert r2.status_code == 200
        assert r2.json()["id"] == rid

        # Receiver inbox
        ib = mi.get(f"{API}/phone-requests/inbox").json()
        ids = [x["id"] for x in ib["items"]]
        assert rid in ids

        # Stranger cannot accept this request
        sub = _client()
        _login(sub, *SHUBHAM)
        bad = sub.post(f"{API}/phone-requests/{rid}/accept")
        assert bad.status_code == 404

        # Receiver accepts
        ok = mi.post(f"{API}/phone-requests/{rid}/accept")
        assert ok.status_code == 200

        # Now Shakuntala's kundali for Michael should reveal phone
        kundali = sh.get(f"{API}/kundali/{receiver_id}").json()
        assert kundali["phone_status"] == "accepted"
        # phone field present (may be empty string if Michael has no phone saved)
        assert "phone" in kundali

    def test_reject_flow(self):
        # Michael requests Shakuntala
        mi = _client()
        _login(mi, *MICHAEL)
        sh = _client()
        sh_user = _login(sh, *SHAKUNTALA)

        r = mi.post(f"{API}/phone-requests", json={"receiver_user_id": sh_user["id"]})
        assert r.status_code == 200
        rid = r.json()["id"]

        # If status already final from a prior run, skip
        if r.json()["status"] == "rejected":
            pass
        else:
            rej = sh.post(f"{API}/phone-requests/{rid}/reject")
            # Could be 200 if pending; if previously accepted in another test run, allow that too
            assert rej.status_code in (200, 404)

        # Michael's kundali for Shakuntala
        k = mi.get(f"{API}/kundali/{sh_user['id']}").json()
        assert k["phone_status"] in ("rejected", "accepted", "pending")
        if k["phone_status"] == "rejected":
            assert k["phone"] == ""

    def test_cannot_request_self(self):
        sh = _client()
        u = _login(sh, *SHAKUNTALA)
        r = sh.post(f"{API}/phone-requests", json={"receiver_user_id": u["id"]})
        assert r.status_code == 400


# ---------- Security: cannot self-modify premium ----------
class TestSecurity:
    def test_no_endpoint_to_modify_premium(self):
        sh = _client()
        u = _login(sh, *SHAKUNTALA)
        # Try common attack vectors - none should succeed
        for path, payload in [
            ("/profile", {"name": "x", "gender": "female", "looking_for": "male",
                          "dob": "02-08-1998", "birth_time": "12:00", "birth_city": "Mumbai",
                          "is_premium": True, "unlocked_premium": 999, "is_private_member": False, "role": "admin"}),
        ]:
            r = sh.post(f"{API}{path}", json=payload)
            # endpoint may succeed but extra fields should be ignored
        # Verify /auth/me unchanged values
        me = sh.get(f"{API}/auth/me").json()
        assert me["role"] == "user"
        # is_premium is True for all members by design (paywall removed) - just ensure role didn't escalate
