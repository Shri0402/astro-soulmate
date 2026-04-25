"""Email provider abstraction. Currently uses Resend (https://resend.com).
Swap-out for SendGrid is straightforward — implement send_email() with provider's SDK.
"""
import os
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import resend
except ImportError:
    resend = None


def _provider() -> str:
    return os.environ.get("EMAIL_PROVIDER", "resend").lower()


async def send_email(to: str, subject: str, html: str, text: Optional[str] = None) -> dict:
    """Send a transactional email. Returns {ok, id?, message?}."""
    api_key = os.environ.get("RESEND_API_KEY", "").strip()
    sender = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev").strip()
    sender_name = os.environ.get("SENDER_NAME", "Stars Connection").strip()
    from_field = f"{sender_name} <{sender}>" if sender_name else sender

    if not api_key or _provider() != "resend" or resend is None:
        # Provider not configured — log and no-op (UI still works, link is shareable manually)
        logger.warning(f"[email-stub] would send to={to} subject={subject!r} (RESEND_API_KEY missing)")
        return {"ok": False, "stub": True, "message": "Email provider not configured."}

    resend.api_key = api_key
    params = {"from": from_field, "to": [to], "subject": subject, "html": html}
    if text:
        params["text"] = text
    try:
        result = await asyncio.to_thread(resend.Emails.send, params)
        return {"ok": True, "id": (result or {}).get("id")}
    except Exception as e:
        logger.error(f"Resend send failed: {e}")
        return {"ok": False, "message": str(e)}


def invite_email_html(invitee_name: str, referrer_name: str, link: str, code: str, note: str = "") -> str:
    """Branded maroon/gold invite email."""
    note_html = f'<p style="color:#8A6B72;font-style:italic;margin:0 0 16px 0">{note}</p>' if note else ""
    return f"""
<!doctype html>
<html><body style="margin:0;background:#0A0305;font-family:'Cormorant Garamond',Georgia,serif;color:#F3E6C6;">
<table width="100%" cellspacing="0" cellpadding="0" border="0" style="background:#0A0305;padding:40px 0;">
<tr><td align="center">
  <table width="560" cellspacing="0" cellpadding="0" border="0" style="background:#1A0810;border:1px solid rgba(212,175,55,0.25);">
    <tr><td style="padding:48px 48px 24px;">
      <p style="color:#D4AF37;letter-spacing:0.3em;font-size:11px;font-family:Helvetica,Arial,sans-serif;text-transform:uppercase;margin:0 0 12px 0;">⋆ Stars Connection ⋆</p>
      <h1 style="font-family:Georgia,serif;font-size:36px;line-height:1.1;color:#F3E6C6;margin:0 0 24px 0;font-weight:400;">You have been chosen.</h1>
      <p style="color:#C2A3A8;font-family:Helvetica,Arial,sans-serif;font-size:15px;line-height:1.7;margin:0 0 20px 0;">
        {referrer_name} has personally invited you to join <strong>Stars Connection</strong> — an ultra-private Vedic matchmaking circle where every connection is woven from your janam kundali.
      </p>
      {note_html}
      <p style="color:#C2A3A8;font-family:Helvetica,Arial,sans-serif;font-size:15px;line-height:1.7;margin:0 0 32px 0;">
        Use the invitation code below to claim your seat. This invite is single-use and tied to your name.
      </p>
      <table cellspacing="0" cellpadding="0" border="0" style="margin:0 auto;">
        <tr><td align="center" style="background:#D4AF37;padding:16px 40px;">
          <a href="{link}" style="color:#0A0305;font-family:Helvetica,Arial,sans-serif;font-size:13px;letter-spacing:0.2em;text-transform:uppercase;text-decoration:none;font-weight:600;">Accept Invitation</a>
        </td></tr>
      </table>
      <p style="text-align:center;color:#8A6B72;font-family:'Courier New',monospace;font-size:18px;letter-spacing:0.3em;margin:24px 0 8px 0;">{code}</p>
      <p style="text-align:center;color:#8A6B72;font-family:Helvetica,Arial,sans-serif;font-size:12px;margin:0 0 32px 0;">Or open {link}</p>
    </td></tr>
    <tr><td style="padding:24px 48px;border-top:1px solid rgba(212,175,55,0.1);">
      <p style="color:#8A6B72;font-family:Helvetica,Arial,sans-serif;font-size:11px;line-height:1.6;margin:0;">
        Stars Connection is invite-only. If this email reached you in error, simply ignore it — the invite will expire when the referrer revokes it.
      </p>
    </td></tr>
  </table>
</td></tr></table>
</body></html>"""


def phone_request_email_html(receiver_name: str, requester_name: str, dashboard_url: str) -> str:
    return f"""
<!doctype html>
<html><body style="margin:0;background:#0A0305;font-family:Helvetica,Arial,sans-serif;color:#F3E6C6;">
<table width="100%" style="background:#0A0305;padding:40px 0;"><tr><td align="center">
<table width="540" cellpadding="0" cellspacing="0" style="background:#1A0810;border:1px solid rgba(212,175,55,0.25);">
<tr><td style="padding:40px;">
  <p style="color:#D4AF37;letter-spacing:0.3em;font-size:11px;text-transform:uppercase;margin:0 0 12px 0;">New Request</p>
  <h2 style="font-family:Georgia,serif;font-size:26px;color:#F3E6C6;margin:0 0 16px 0;font-weight:400;">{requester_name} wants access to your phone number.</h2>
  <p style="color:#C2A3A8;font-size:14px;line-height:1.7;margin:0 0 24px 0;">Sharing your phone number is completely your personal choice and happens only with your consent. Review the request in your inbox.</p>
  <a href="{dashboard_url}" style="display:inline-block;background:#D4AF37;color:#0A0305;padding:12px 32px;text-decoration:none;letter-spacing:0.2em;font-size:12px;text-transform:uppercase;font-weight:600;">Open inbox</a>
</td></tr></table></td></tr></table></body></html>"""
