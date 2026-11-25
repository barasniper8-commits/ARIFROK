import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

sys.path.append(os.path.dirname(__file__))
from bot_core import MIN_DEPOSIT_RP, add_user_balance

ADMIN_SECRET = os.getenv("TOPUP_SECRET", os.getenv("ADMIN_KEY", "")).strip()
BOT1_TOKEN = os.getenv(
    "TELEGRAM_TOKEN_1_",
    os.getenv("TELEGRAM_TOKEN_1", os.getenv("TELEGRAM_TOKEN", "")),
).strip()
BOT2_TOKEN = os.getenv(
    "TELEGRAM_TOKEN_2_",
    os.getenv("TELEGRAM_TOKEN_2", ""),
).strip()


def _resolve_token(bot_key: str) -> str:
    b = (bot_key or "bot1").strip().lower()
    if b in ("bot2", "2", "bot-2"):
        return BOT2_TOKEN
    return BOT1_TOKEN


class handler(BaseHTTPRequestHandler):
    def _send_json(self, code: int, payload: dict):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload, indent=2).encode("utf-8"))

    def _authorized(self, query_params: dict, body_data: dict) -> bool:
        if not ADMIN_SECRET:
            return True
        header_key = (self.headers.get("X-Admin-Key") or "").strip()
        q_key = (query_params.get("key", [""])[0] or "").strip()
        b_key = str(body_data.get("key") or "").strip()
        return ADMIN_SECRET in (header_key, q_key, b_key)

    def do_GET(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        if not self._authorized(qs, {}):
            self._send_json(401, {"ok": False, "error": "Unauthorized"})
            return

        bot_key = (qs.get("bot", ["bot1"])[0] or "bot1").strip().lower()
        user_id_raw = (qs.get("user_id", [""])[0] or "").strip()
        amount_raw = (qs.get("amount", [""])[0] or "").strip()

        if not user_id_raw or not amount_raw:
            self._send_json(
                400,
                {
                    "ok": False,
                    "usage": "/topup?bot=bot1|bot2&user_id=123456&amount=5000",
                    "min_deposit": MIN_DEPOSIT_RP,
                },
            )
            return

        try:
            user_id = int(user_id_raw)
            amount = int(amount_raw)
        except ValueError:
            self._send_json(400, {"ok": False, "error": "user_id dan amount harus angka bulat"})
            return

        if amount < MIN_DEPOSIT_RP:
            self._send_json(
                400,
                {
                    "ok": False,
                    "error": f"Minimal deposit Rp{MIN_DEPOSIT_RP:,}".replace(",", "."),
                },
            )
            return

        token = _resolve_token(bot_key)
        if not token:
            self._send_json(400, {"ok": False, "error": f"Token untuk {bot_key} belum diatur"})
            return

        new_balance = add_user_balance(bot_key, user_id, amount)
        self._send_json(
            200,
            {
                "ok": True,
                "bot": bot_key,
                "user_id": user_id,
                "added_rp": amount,
                "saldo_rp": new_balance,
            },
        )

    def do_POST(self):
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except Exception:
            body = {}

        if not self._authorized(qs, body):
            self._send_json(401, {"ok": False, "error": "Unauthorized"})
            return

        bot_key = str(body.get("bot") or qs.get("bot", ["bot1"])[0] or "bot1").strip().lower()
        try:
            user_id = int(body.get("user_id"))
            amount = int(body.get("amount"))
        except (TypeError, ValueError):
            self._send_json(400, {"ok": False, "error": "user_id dan amount wajib diisi angka"})
            return

        if amount < MIN_DEPOSIT_RP:
            self._send_json(
                400,
                {
                    "ok": False,
                    "error": f"Minimal deposit Rp{MIN_DEPOSIT_RP:,}".replace(",", "."),
                },
            )
            return

        token = _resolve_token(bot_key)
        if not token:
            self._send_json(400, {"ok": False, "error": f"Token untuk {bot_key} belum diatur"})
            return

        new_balance = add_user_balance(bot_key, user_id, amount)
        self._send_json(
            200,
            {
                "ok": True,
                "bot": bot_key,
                "user_id": user_id,
                "added_rp": amount,
                "saldo_rp": new_balance,
            },
        )
