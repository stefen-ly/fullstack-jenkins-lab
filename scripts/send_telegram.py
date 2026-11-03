#!/usr/bin/env python3
"""Send Jenkins status via Telegram without putting tokens in CLI arguments.

The Jenkins withCredentials() block provides TOKEN and CHAT_ID as temporary
environment variables. Do not log the API URL or secrets.
"""
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
status = os.environ.get('NOTIFY_STATUS', 'UNKNOWN')
job = os.environ.get('JOB_NAME', 'unknown-job')
build = os.environ.get('BUILD_NUMBER', '?')
url = os.environ.get('BUILD_URL', '(check Jenkins)')

if not token or not chat_id:
    print('Telegram credentials missing', file=sys.stderr)
    sys.exit(2)

text = f'Jenkins {status}\nJob: {job}\nBuild: #{build}\n{url}'
data = urlencode({'chat_id': chat_id, 'text': text}).encode('utf-8')
endpoint = f'https://api.telegram.org/bot{token}/sendMessage'

try:
    request = Request(endpoint, data=data, method='POST')
    with urlopen(request, timeout=15) as response:
        result = json.load(response)
    if result.get('ok') is not True:
        print('Telegram API returned unsuccessful response', file=sys.stderr)
        sys.exit(1)
    print('Telegram notification delivered to API')
except HTTPError as error:
    print(f'Telegram HTTP error: {error.code}', file=sys.stderr)
    sys.exit(1)
except (URLError, TimeoutError, ValueError) as error:
    print(f'Telegram request failed ({type(error).__name__})', file=sys.stderr)
    sys.exit(1)
