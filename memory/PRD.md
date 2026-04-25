# Stars Connection — Product Requirements Document

## 1. Original Problem Statement (v1)
SaaS platform for astrology-based matchmaking with monetization. Users input DOB / birth time / location → system computes Moon sign, Nakshatra, Rashi, Ashtakoota score (0–36), full kundali compatibility. Matches split: low (<18, free) and high (≥18, paywalled — ₹1000 unlocks 5).

## 2. Phase-2 Requirement (current — Feb 2026)
Pivot to **ULTRA-PRIVATE invite-only network**. Wipe all user data, import 11 named members with DOB-based passwords, REMOVE paywall (full visibility for approved members), add **strict gender filtering**, add **consent-based phone-number request flow**, add **referral / invitation gate**, restructure matchmaking report to AstroSage canonical layout.

## 3. Architecture
- Backend: FastAPI + Motor (async MongoDB) + pyswisseph (Lahiri sidereal) + reportlab + emergentintegrations Stripe (test mode, kept but UI hidden)
- Frontend: React 19 + react-router-dom 7 + Tailwind + shadcn/ui + @phosphor-icons/react + sonner (toasts) + Cormorant Garamond + Outfit
- Auth: JWT in httpOnly cookies (samesite=none; secure), bcrypt password hashing
- Theme: deep maroon (#0A0305 / #1A0810 / #2A0E18) + gold (#D4AF37) + cream (#F3E6C6), Cormorant Garamond serif

## 4. Personas
- **Member** — invited Vedic matchmaking seeker, sees gender-filtered matches, requests phone access, generates invites
- **Admin** — bootstraps invites, manages members; cannot self-match

## 5. What's been implemented

### v1 (Apr 21 2026)
- Vedic astrology engine (Swiss Ephemeris, Lahiri ayanamsa) — Moon sign, Nakshatra, Rashi, 8-guna Ashtakoota, Mangal Dosha
- JWT auth (register/login/me/logout) with bcrypt + httpOnly cookies
- Stripe test-mode payment (₹1000 unlocks 5 high-compat matches; webhook + status polling)
- Reportlab maroon/gold PDF report
- Frontend: Landing, Login, Register, 3-step Onboarding, Waiting room, Dashboard (paywall blur), Kundali, Payment success/cancel
- 20 demo profiles seeded

### v2 — Private Network (Apr 25 2026)
- **Wiped** all v1 user/match/payment data
- **Seeded 11 named private members** (`is_private_member=true`, password = DDMMYYYY of DOB):
  Shakuntala Thatti, Michael Anthony, Garvit, Shubham, Jeremiah W, AJ, Rachel, Minal, Anuketan, Shrilatha Shripathi, Venkatesh Amrutwar (synthetic email, can_login=false)
- **Strict gender filter** in `matching.py` — `looking_for=Male` returns only Male profiles, no reciprocity
- **Removed paywall** — `/api/matches` returns all matches fully visible (no locked/blurred fields); `/api/kundali/:id` no longer 402s for high scores; PDF endpoint has no gating
- **Phone request consent flow**:
  - new collection `phone_number_requests` with unique (requester, receiver) compound index
  - `POST /api/phone-requests`, `GET /api/phone-requests/inbox|sent`, `POST /:id/accept|reject`
  - phone only revealed in `/api/kundali/:id` after accept
  - frontend: in-app `/inbox` page + nav badge + Phone Request CTA on Kundali page with consent disclaimer
- **Invite-only registration**:
  - `POST /api/auth/register` requires valid `invite_code`; `invites` collection (unique `code`) marked used after redemption
  - public `GET /api/auth/invite/:code` validates invites
  - `POST /api/invites` lets members generate invites; `/invitations` page UI
  - `/invite/:code` route prefills register form with referral display
- **AstroSage report layout** (`report_interpretations.py` + Kundali.jsx + pdf_gen.py):
  - Birth Details Table (8 rows incl. Rashi, Rashi Lord, Nakshatra-Pada)
  - Ashtakoota Points Table (Boy/Girl/Max/Obtained/Area Of Life columns + total)
  - Mangal Dosha statement (`Mr. X has '...' and Ms. Y has '...'`)
  - Conclusion line (preferable / NOT preferable)
  - 8 Interpretation paragraphs (canonical AstroSage texts for shown combos + score-tier fallbacks)
  - Disclaimer footer

### v3 — Phase 3 Follow-ups (Apr 25 2026 evening)
- **Expanded interpretation library** (~50 new (boy, girl) combos across all 8 gunas) — Brahmin/Kshatriya, Manav/Chatushpada, Horse/Buffalo, Sun/Moon Graha-Maitri, Aadi/Madhya pairs, etc.
- **Lagna, Tithi, Karan, Yoga, Paksha, Nakshatra Lord, Lagna Lord, weekday** computed via pyswisseph and surfaced in birth_details (15-row table)
- **Profile editing** with field-level policy:
  - **Free edit** (`PATCH /api/profile`): bio, phone, birth_city, state, name
  - **Admin approval required** (`POST /api/profile/change-request`): looking_for, dob, birth_time, gender — DOB & birth_time treated as immutable kundali identity
  - Frontend `/profile` shows free-edit form + Lock icons + change-request form + history list
- **Admin approval queue** (`/admin/change-requests` GET/approve/reject) + **Members directory** (`/admin/members`):
  - Frontend `/admin` page for admin only (Crown icon in nav)
  - Approving DOB/birth_time recomputes astro & regenerates matches
  - Approving looking_for / gender regenerates matches
- **Resend email integration** (`emailservice.py` + `POST /api/invites/send-email`):
  - Provider abstraction (Resend default, SendGrid swap-friendly)
  - Branded maroon/gold HTML invite email
  - **Soft-fail** when `RESEND_API_KEY` empty → returns `{ok:false, stub:true, share_link}` so UX still works
  - Frontend Invitations page now has "Email it" inline form (invitee_name + email + note)
- Bug fix: admin user now seeded with `profile_complete=True` so Admin/Invitations routes are reachable

### Test pass rate (iteration_4.json): Backend **39/39 (100%)**, Frontend **100%**

## 6. Backlog (next phases)

### P1
- Expand interpretation library with more (boy, girl) combinations per guna for richer copy
- Profile editing / view-own-chart page
- Birth chart SVG visualization (Lagna / Navamsa / Chandra)
- Computed Lagna, Tithi, Karan, Yoga (currently birth-details table shows them as "—")
- Email-based invite delivery (currently link must be shared manually)

### P2
- Admin moderation dashboard (approve invites, deactivate members)
- Block / report flow
- Push notifications for phone requests
- Re-enable Stripe paywall behind a feature flag for non-private public tier

## 7. Test credentials & endpoints
See `/app/memory/test_credentials.md`.

## 8. Notes / Design system
- `/app/design_guidelines.json` — Jewel & Luxury archetype (maroon + gold), Cormorant Garamond + Outfit
- Brand: dark mode, no purple AI-slop gradients, sidereal celestial motifs
