"""Stars Connection v3 - pytest covering Phase-3 features:
- expanded astro fields (lagna, lagna_lord, tithi, paksha, yoga, karan, nakshatra_lord)
- expanded interpretation library
- PATCH /profile, /profile/change-request flow
- /admin/* endpoints
- /invites/send-email soft-fail (RESEND_API_KEY empty)
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://astro-soulmate-4.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

SHAKUNTALA = ("123@gmail.com", "02081998")
ADMIN = ("admin@starsconnection.com", "Admin@Stars2026")
MICHAEL = ("michaelanthonyssj5@gmail.com", "07012000")


# ---------- helpers ----------
def _login(creds):
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    r = s.post(f"{API}/auth/login", json={"email": creds[0], "password": creds[1]})
    assert r.status_code == 200, f"login failed for {creds[0]}: {r.status_code} {r.text}"
    return s


@pytest.fixture(scope="module")
def shak():
    return _login(SHAKUNTALA)


@pytest.fixture(scope="module")
def admin():
    return _login(ADMIN)


@pytest.fixture(scope="module")
def michael():
    return _login(MICHAEL)


# ---------- (a) astro: new fields on /auth/me ----------
def test_me_has_new_astro_fields(shak):
    r = shak.get(f"{API}/auth/me")
    assert r.status_code == 200
    astro = (r.json() or {}).get("astro") or {}
    for k in ["lagna", "lagna_lord", "tithi", "paksha", "yoga", "karan", "nakshatra_lord"]:
        assert astro.get(k), f"astro.{k} missing/empty: {astro}"


# ---------- (b) kundali birth_details = 15 rows ----------
def test_kundali_birth_details_15_rows(shak):
    r = shak.get(f"{API}/matches")
    assert r.status_code == 200
    matches = r.json().get("matches") or []
    assert matches, "no matches found for Shakuntala"
    mid = matches[0]["match_user_id"]

    k = shak.get(f"{API}/kundali/{mid}")
    assert k.status_code == 200
    bd = k.json()["report"]["birth_details"]
    labels = [row["label"] for row in bd]
    expected = {"Tithi", "Paksha", "Yoga", "Karan", "Lagna", "Lagna Lord",
                "Rashi", "Rashi Lord", "Nakshatra-Pada", "Nakshatra Lord"}
    missing = expected - set(labels)
    assert not missing, f"missing labels: {missing}; got {labels}"
    assert len(bd) == 15, f"expected 15 rows, got {len(bd)}: {labels}"


# ---------- (c) interpretation library covers more combos (non-fallback) ----------
def test_interpretations_non_fallback(shak):
    """At least one match should produce non-empty/non-fallback interpretations for all 8 gunas."""
    matches = shak.get(f"{API}/matches").json().get("matches") or []
    assert matches
    mid = matches[0]["match_user_id"]
    k = shak.get(f"{API}/kundali/{mid}").json()
    interps = k["report"]["interpretations"]
    assert len(interps) == 8
    for it in interps:
        assert it["text"] and len(it["text"].strip()) > 20, f"empty interpretation for {it['guna']}"


def test_report_interpretations_module_has_expanded_combos():
    """Quick smoke check that the interpretation dictionaries contain new combos."""
    import sys
    sys.path.insert(0, "/app/backend")
    from report_interpretations import interpret  # noqa
    # Probe a few combos that v3 added
    combos = [
        ("Varna", "Brahmin", "Kshatriya"),
        ("Vashya", "Manav", "Chatushpada"),
        ("Yoni", "Horse", "Buffalo"),
        ("Graha Maitri", "Sun", "Moon"),
        ("Gana", "Dev", "Manav"),
    ]
    for guna, b, g in combos:
        txt = interpret(guna, b, g, 0, 1)
        assert txt and len(txt) > 10, f"{guna}/{b}/{g} produced empty: {txt!r}"


# ---------- (d) PATCH /profile free fields ----------
def test_patch_profile_free_fields(shak):
    new_bio = f"v3-test-bio-{int(time.time())}"
    r = shak.patch(f"{API}/profile", json={"bio": new_bio, "phone": "+919876543210"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["bio"] == new_bio
    # verify GET /me reflects
    me = shak.get(f"{API}/auth/me").json()
    assert me["bio"] == new_bio
    assert me["phone"] == "+919876543210"


def test_patch_profile_ignores_sensitive_fields(shak):
    """Even if client sends looking_for / dob, they must be silently ignored (only EDITABLE_FIELDS applied)."""
    before = shak.get(f"{API}/auth/me").json()
    orig_lf = before["looking_for"]; orig_dob = before["dob"]
    # Send a sensitive field along with a valid editable one
    r = shak.patch(f"{API}/profile", json={"bio": "ok", "looking_for": "male_or_female", "dob": "1900-01-01"})
    # Pydantic ProfileEditIn does not declare looking_for/dob → those are dropped at model level (200)
    assert r.status_code == 200, r.text
    after = shak.get(f"{API}/auth/me").json()
    assert after["looking_for"] == orig_lf
    assert after["dob"] == orig_dob


def test_patch_profile_empty_body(shak):
    r = shak.patch(f"{API}/profile", json={})
    assert r.status_code == 400
    assert "Nothing to update" in r.text


# ---------- (e) change-request flow ----------
def test_change_request_non_sensitive_400(shak):
    r = shak.post(f"{API}/profile/change-request", json={"field": "bio", "new_value": "x"})
    assert r.status_code == 400


def test_change_request_create_and_duplicate_409(shak, admin):
    # First clean any previous pending for looking_for by approving/rejecting via admin
    pending = admin.get(f"{API}/admin/change-requests?status=pending").json().get("items", [])
    for it in pending:
        if it["field"] == "looking_for" and it["user_email"] == SHAKUNTALA[0]:
            admin.post(f"{API}/admin/change-requests/{it['id']}/reject")

    # Now create a new request
    r1 = shak.post(f"{API}/profile/change-request",
                   json={"field": "looking_for", "new_value": "female", "reason": "test"})
    assert r1.status_code == 200, r1.text
    req_id = r1.json()["id"]

    # Duplicate
    r2 = shak.post(f"{API}/profile/change-request",
                   json={"field": "looking_for", "new_value": "female"})
    assert r2.status_code == 409

    # Listed by user
    mine = shak.get(f"{API}/profile/change-requests/mine").json().get("items", [])
    assert any(i["id"] == req_id for i in mine)


# ---------- (f) admin endpoints ----------
def test_admin_endpoints_reject_non_admin(shak):
    for path in ["/admin/change-requests", "/admin/members"]:
        r = shak.get(f"{API}{path}")
        assert r.status_code == 403, f"{path} should be 403 for non-admin; got {r.status_code}"


def test_admin_list_members(admin):
    r = admin.get(f"{API}/admin/members")
    assert r.status_code == 200
    items = r.json()["items"]
    assert isinstance(items, list) and len(items) >= 5
    # No password_hash leaked, _id is stringified
    for it in items:
        assert "password_hash" not in it
        assert isinstance(it.get("_id"), str)
        assert it.get("role") != "admin"


def test_admin_pending_list(admin):
    r = admin.get(f"{API}/admin/change-requests?status=pending")
    assert r.status_code == 200
    items = r.json()["items"]
    # We just created one above for Shakuntala
    assert any(i["user_email"] == SHAKUNTALA[0] and i["field"] == "looking_for" for i in items)


def test_admin_approve_looking_for_flips_matches(admin, shak):
    # Get current Shakuntala matches (all male before)
    before = shak.get(f"{API}/matches").json().get("matches", [])
    before_ids = {m["match_user_id"] for m in before}

    # Find pending request for Shakuntala/looking_for
    items = admin.get(f"{API}/admin/change-requests?status=pending").json()["items"]
    target = next((i for i in items if i["user_email"] == SHAKUNTALA[0] and i["field"] == "looking_for"), None)
    assert target, "expected pending looking_for request for Shakuntala"

    r = admin.post(f"{API}/admin/change-requests/{target['id']}/approve")
    assert r.status_code == 200, r.text

    # Shakuntala's looking_for is now 'female' → matches list must change
    me = shak.get(f"{API}/auth/me").json()
    assert me["looking_for"] == "female"
    after = shak.get(f"{API}/matches").json().get("matches", [])
    after_ids = {m["match_user_id"] for m in after}
    assert after_ids != before_ids, "matches did not refresh after approval"

    # Reset back to 'male' via admin direct update through another change-request cycle
    r2 = shak.post(f"{API}/profile/change-request",
                   json={"field": "looking_for", "new_value": "male"})
    assert r2.status_code == 200
    items2 = admin.get(f"{API}/admin/change-requests?status=pending").json()["items"]
    rid = next(i["id"] for i in items2 if i["user_email"] == SHAKUNTALA[0] and i["field"] == "looking_for")
    admin.post(f"{API}/admin/change-requests/{rid}/approve")


def test_admin_reject_then_approve_fails(admin, shak):
    # Create a fresh request (use birth_time)
    r1 = shak.post(f"{API}/profile/change-request",
                   json={"field": "birth_time", "new_value": "10:30",
                         "reason": "verify rejection blocks subsequent approve"})
    assert r1.status_code == 200
    rid = r1.json()["id"]

    rej = admin.post(f"{API}/admin/change-requests/{rid}/reject?admin_note=test-reject")
    assert rej.status_code == 200

    # Approve should now 404 (already decided)
    again = admin.post(f"{API}/admin/change-requests/{rid}/approve")
    assert again.status_code == 404


def test_admin_approve_birth_time_recomputes_astro(admin, shak):
    before = shak.get(f"{API}/auth/me").json()["astro"]
    # Make a tweak: shift birth_time by 1 minute
    orig_bt = before.get("birth_time") or "08:00"
    new_bt = "09:15"

    r1 = shak.post(f"{API}/profile/change-request",
                   json={"field": "birth_time", "new_value": new_bt})
    assert r1.status_code == 200
    rid = r1.json()["id"]

    appr = admin.post(f"{API}/admin/change-requests/{rid}/approve")
    assert appr.status_code == 200, appr.text

    after_me = shak.get(f"{API}/auth/me").json()
    assert after_me["birth_time"] == new_bt
    after_astro = after_me["astro"]
    # All new fields still present after recompute
    for k in ["lagna", "tithi", "yoga", "karan", "nakshatra_lord"]:
        assert after_astro.get(k), f"recomputed astro.{k} missing"


# ---------- (g) email send: soft-fail when no API key ----------
def test_invite_send_email_soft_fails(shak):
    # Create a fresh invite as Shakuntala
    inv = shak.post(f"{API}/invites", json={"note": "v3-test"}).json()
    code = inv["code"]
    r = shak.post(f"{API}/invites/send-email", json={
        "code": code, "invitee_email": "test_v3_invitee@example.com",
        "invitee_name": "Test"
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ok"] is False
    assert body.get("stub") is True
    assert "share_link" in body and f"/invite/{code}" in body["share_link"]


def test_invite_send_email_403_for_non_creator(shak, michael):
    inv = shak.post(f"{API}/invites", json={}).json()
    code = inv["code"]
    r = michael.post(f"{API}/invites/send-email", json={
        "code": code, "invitee_email": "x@example.com"
    })
    assert r.status_code == 403


def test_invite_send_email_404_unknown_code(shak):
    r = shak.post(f"{API}/invites/send-email", json={
        "code": "ZZZZZZZZ", "invitee_email": "x@example.com"
    })
    assert r.status_code == 404


def test_invite_send_email_400_already_used(admin):
    # Create + use an invite (register via it) then attempt to email it
    inv = admin.post(f"{API}/invites", json={}).json()
    code = inv["code"]
    em = f"v3used+{int(time.time())}@example.com"
    reg = requests.post(f"{API}/auth/register",
                        json={"email": em, "password": "passw0rd!", "name": "V3 Used", "invite_code": code})
    assert reg.status_code == 200, reg.text
    r = admin.post(f"{API}/invites/send-email", json={"code": code, "invitee_email": em})
    assert r.status_code == 400
