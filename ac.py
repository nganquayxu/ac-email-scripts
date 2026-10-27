"""Minimal ActiveCampaign helpers: create a draft email campaign and send a test.

Config comes from environment variables (never commit keys):
  AC_API_URL  e.g. https://youraccount.api-us1.com
  AC_API_KEY  your API key
A local .env file (KEY=value lines) is loaded if present.

Create uses the v1 API (form-encoded): message_add + campaign_create (status=0 = draft).
Test send uses the v3 endpoint POST /api/3/campaigns/test-send.
"""
import json
import os
import urllib.error
import urllib.parse
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


def _request(req):
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def _v1(action, fields):
    url, key = _cfg()
    endpoint = f"{url}/admin/api.php?api_action={action}&api_output=json"
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(
        endpoint, data=data, method="POST", headers={"API-TOKEN": key}
    )
    status, body = _request(req)
    try:
        out = json.loads(body)
    except ValueError:
        raise SystemExit(f"{action} failed (HTTP {status}): {body[:500]}")
    if out.get("result_code") != 1:
        raise SystemExit(f"{action} failed: {out.get('result_message')}")
    return out


def create_draft(name, subject, html, text, from_email, from_name, list_id, reply_to=None):
    """Create a message and a draft campaign for it. Returns (campaign_id, message_id)."""
    msg = _v1("message_add", {
        "format": "mime",
        "subject": subject,
        "fromemail": from_email,
        "fromname": from_name,
        "reply2": reply_to or from_email,
        "priority": "3",
        "charset": "utf-8",
        "encoding": "quoted-printable",
        "htmlconstructor": "editor",
        "html": html,
        "textconstructor": "editor",
        "text": text,
        f"p[{list_id}]": list_id,
    })
    message_id = int(msg["id"])
    camp = _v1("campaign_create", {
        "type": "single",
        "name": name,
        "sdate": "2099-01-01 09:00:00",  # placeholder; status=0 keeps it a draft
        "status": "0",
        "public": "0",
        "tracklinks": "all",
        "trackreads": "1",
        f"p[{list_id}]": list_id,
        f"m[{message_id}]": "100",
    })
    return int(camp["id"]), message_id


def send_test(campaign_id, message_id, subject, to_email):
    """Send a test of a campaign. Prefix to_email with '+' to use the regular mail server."""
    url, key = _cfg()
    body = json.dumps({
        "campaignId": int(campaign_id),
        "messageId": int(message_id),
        "subject": subject,
        "toEmail": to_email,
    }).encode()
    req = urllib.request.Request(
        f"{url}/api/3/campaigns/test-send",
        data=body,
        method="POST",
        headers={"Api-Token": key, "Content-Type": "application/json"},
    )
    status, text = _request(req)
    if status != 200:
        raise SystemExit(f"test-send failed (HTTP {status}): {text}")
    return text
