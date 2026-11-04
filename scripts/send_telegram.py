
#!/usr/bin/env python3

import json
import os
import re
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# Escape Telegram MarkdownV2 special characters
def md(text):
    return re.sub(
        r'([_*\[\]()~`>#+\-=|{}.!\\])',
        r'\\\1',
        str(text)
    )


def md_url(url):
    return str(url).replace("\\", "\\\\").replace(")", "\\)")


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


# Build result
status_icons = {
    "SUCCESS": "✅",
    "FAILURE": "❌",
    "UNSTABLE": "⚠️",
    "ABORTED": "⏹️",
}

icon = status_icons.get(status, "ℹ️")

# Current Cambodia time (notification time)
now = datetime.now(ZoneInfo("Asia/Phnom_Penh"))
notification_time = now.strftime("%d %b %Y, %H:%M")


# MarkdownV2 message
message = (
    f"{icon} *JENKINS PIPELINE {md(status)}*\n"
    f"{md('━━━━━━━━━━━━━━━━━━━━')}\n\n"
    f"📦 *Project:* {md('Fullstack Application')}\n"
    f"🛠️ *Job:* {md(job)}\n"
    f"🔢 *Build:* {md('#' + build)}\n"
    f"📊 *Status:* {md(status)}\n"
    f"🕒 *Time:* {md(notification_time)} ICT\n\n"
)

if build_url.startswith(("http://", "https://")):
    message += (
        f"🔗 [View Build Details]({md_url(build_url)})"
    )
else:
    message += "🔗 Build details unavailable"


# Telegram Bot API
endpoint = f"https://api.telegram.org/bot{token}/sendMessage"

payload = urlencode({
    "chat_id": chat_id,
    "text": message,
    "parse_mode": "MarkdownV2",
    "link_preview_options": json.dumps({
        "is_disabled": True
    })
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
    print(f"Telegram HTTP error: {error.code}", file=sys.stderr)
    sys.exit(1)

except (URLError, TimeoutError, ValueError) as error:
    print(
        f"Telegram request failed: {type(error).__name__}",
        file=sys.stderr
    )
    sys.exit(1)
