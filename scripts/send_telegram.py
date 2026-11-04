
#!/usr/bin/env python3

import json
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from html import escape
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

# Jenkins environment variables
token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
status = os.environ.get("NOTIFY_STATUS", "UNKNOWN")
job = os.environ.get("JOB_NAME", "unknown-job")
build = os.environ.get("BUILD_NUMBER", "?")
build_url = os.environ.get("BUILD_URL", "")

if not token or not chat_id:
    print("Telegram credentials missing", file=sys.stderr)
    sys.exit(2)

# Status icons
icons = {
    "SUCCESS": "✅",
    "FAILURE": "❌",
    "UNSTABLE": "⚠️",
    "ABORTED": "⏹️"
}

icon = icons.get(status, "ℹ️")

# Cambodia timezone
now = datetime.now(ZoneInfo("Asia/Phnom_Penh"))
build_time = now.strftime("%d %b %Y, %H:%M")

# Escape dynamic text for Telegram HTML
safe_status = escape(status)
safe_job = escape(job)
safe_build = escape(build)
safe_url = escape(build_url, quote=True)

message = (
    f"{icon} <b>Jenkins Pipeline {safe_status}</b>\n\n"
    f"📦 <b>Project:</b> Fullstack Application\n"
    f"🔧 <b>Job:</b> {safe_job}\n"
    f"🔢 <b>Build:</b> #{safe_build}\n"
    f"📊 <b>Status:</b> {safe_status}\n"
    f"🕒 <b>Time:</b> {build_time} (Cambodia)\n\n"
)

if build_url:
    message += (
        f'🔗 <a href="{safe_url}">View Build Details</a>'
    )

# Telegram API
endpoint = f"https://api.telegram.org/bot{token}/sendMessage"

payload = urlencode({
    "chat_id": chat_id,
    "text": message,
    "parse_mode": "HTML",
    "disable_web_page_preview": "true"
}).encode("utf-8")

try:
    request = Request(
        endpoint,
        data=payload,
        method="POST"
    )

    with urlopen(request, timeout=15) as response:
        result = json.load(response)

    if result.get("ok") is not True:
        print("Telegram API rejected request", file=sys.stderr)
        sys.exit(1)

    print("Telegram notification accepted by API")

except HTTPError as error:
    print(
        f"Telegram HTTP error: {error.code}",
        file=sys.stderr
    )
    sys.exit(1)

except (URLError, TimeoutError, ValueError) as error:
    print(
        f"Telegram request failed: {type(error).__name__}",
        file=sys.stderr
    )
    sys.exit(1)
