"""Minimal ActiveCampaign helpers (API v3 only): create a draft email campaign and send a test.

Config comes from environment variables (never commit keys):
  AC_API_URL  e.g. https://youraccount.api-us1.com
  AC_API_KEY  your API key
A local .env file (KEY=value lines) is loaded if present.

Draft flow (the campaign stays a draft until it is scheduled/enabled, which this repo never does):
  1. POST /api/3/campaign          create the campaign
  2. POST /api/3/messages          create the message (subject, sender, html, text)
  3. POST /api/3/campaignMessages  attach the message to the campaign
  4. PUT  /api/3/campaigns/{id}/edit  set the list(s)
Test send: POST /api/3/campaigns/test-send
"""
import json
import os
import urllib.error
import urllib.request


def _load_env(path=".env"):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env()


def _cfg():
    url = os.environ.get("AC_API_URL", "").rstrip("/")
    key = os.environ.get("AC_API_KEY", "")
    if not url or not key:
        raise SystemExit("Set AC_API_URL and AC_API_KEY (env vars or .env file).")
    return url, key


def _v3(method, path, body):
    """Call a v3 endpoint with a JSON body. Returns (status, response text)."""
    url, key = _cfg()
    req = urllib.request.Request(
        f"{url}/api/3/{path}",
        data=json.dumps(body).encode(),
        method=method,
        headers={"Api-Token": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def _json_ok(step, status, text):
    if status not in (200, 201):
        raise SystemExit(f"{step} failed (HTTP {status}): {text[:500]}")
    return json.loads(text)


def create_draft(name, subject, html, text, from_email, from_name, list_id,
                 reply_to=None, preheader=None):
    """Create a draft campaign with one message. Returns (campaign_id, message_id)."""
    camp = _json_ok("create campaign", *_v3("POST", "campaign", {"name": name, "type": "single"}))
    campaign_id = int(camp["id"])

    message = {
        "fromname": from_name,
        "fromemail": from_email,
        "reply2": reply_to or from_email,
        "subject": subject,
        "html": html,
        "text": text,
        "format": "mime",
    }
    if preheader:
        message["preheader_text"] = preheader
    msg = _json_ok("create message", *_v3("POST", "messages", {"message": message}))
    message_id = int(msg["message"]["id"])

    _json_ok("attach message", *_v3("POST", "campaignMessages", {
        "campaignMessage": {"campaignid": campaign_id, "messageid": message_id},
    }))
    _json_ok("set list", *_v3("PUT", f"campaigns/{campaign_id}/edit", {"listIds": [int(list_id)]}))
    return campaign_id, message_id


def send_test(campaign_id, message_id, subject, to_email):
    """Send a test of a campaign. Prefix to_email with '+' to use the regular mail server."""
    status, text = _v3("POST", "campaigns/test-send", {
        "campaignId": int(campaign_id),
        "messageId": int(message_id),
        "subject": subject,
        "toEmail": to_email,
    })
    if status != 200:
        raise SystemExit(f"test-send failed (HTTP {status}): {text}")
    return text
