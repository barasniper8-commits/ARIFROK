import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.append(os.path.dirname(__file__))
from bot_core import process_webhook_update

BOT1_TOKEN = os.getenv("TELEGRAM_TOKEN_1", os.getenv("TELEGRAM_TOKEN", "9042103827:AAHRljMm11tXucZUgkks4RiuHcJj99VZkss"))
GROQ_KEY_1 = os.getenv("GROQ_API_KEY_1", os.getenv("GROQ_API_KEY", "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"))


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True, "bot": "Bot-1", "mode": "vercel-webhook"}).encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            update = json.loads(raw_body.decode("utf-8"))
            process_webhook_update(update, BOT1_TOKEN, GROQ_KEY_1, "Bot-1")
        except Exception as e:
            print(f"[Bot-1 Webhook Error] {e}", file=sys.stderr, flush=True)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')
