
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.append(os.path.dirname(__file__))
from bot_core import configure_telegram_bot

BOT1_TOKEN = os.getenv(
    "TELEGRAM_TOKEN_1_",
    os.getenv("TELEGRAM_TOKEN_1", os.getenv("TELEGRAM_TOKEN", "")),
).strip()
BOT2_TOKEN = os.getenv("TELEGRAM_TOKEN_2_", os.getenv("TELEGRAM_TOKEN_2", "")).strip()


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        host = self.headers.get("Host", "")
        scheme = "http" if host.startswith("localhost") or host.startswith("127.0.0.1") else "https"
        base_url = f"{scheme}://{host}" if host else ""

        output = {}
        if base_url and BOT1_TOKEN:
            output["bot1"] = configure_telegram_bot(BOT1_TOKEN, f"{base_url}/webhook/bot1")
        if base_url and BOT2_TOKEN:
            output["bot2"] = configure_telegram_bot(BOT2_TOKEN, f"{base_url}/webhook/bot2")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True, "configured": output}, indent=2).encode("utf-8"))
