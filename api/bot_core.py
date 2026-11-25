import base64
from datetime import datetime, timedelta, timezone
import html
import json
import os
import random
import re
import sys
import threading
import requests

WIB = timezone(timedelta(hours=7))

COST_PER_RUN_RP = 1
MIN_DEPOSIT_RP = 5000

GITHUB_TOKEN = (os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN") or "").strip()
GITHUB_REPO = (
    os.getenv("GH_REPO")
    or os.getenv("GITHUB_REPO")
    or "barasniper8-commits/ARIFROK"
).strip()
GITHUB_BRANCH = (
    os.getenv("GH_BRANCH")
    or os.getenv("GITHUB_BRANCH")
    or "main"
).strip()
SALDO_REPO_PATH = (os.getenv("SALDO_REPO_PATH") or "data/saldo_users.json").strip().lstrip("/")

_SALDO_LOCK = threading.Lock()
_MEMORY_DB: dict[str, dict] = {}

RDP_PHOTO_URL = (
    "https://blogger.googleusercontent.com/img/b/R29vZ2xl/"
    "AVvXsEhUqjQ4dcVH11aoJxMqho_CMCB9SnH4yepKrcVtuMD_FvAa-21zb-WL4M6TSQOPWf3vo54zKVIiPrdfhSH7AITPUsB_HRKm0ODtsRL_lZ7p_QU1aDfIyd2W6-OQdjPa1Xjc78aEk0lei_9YLG6_ZsgsNq9r5sEIHzUGMeY8B-Agl5Z6Puc38O02XrJujXU/"
    "s1600/1000196027.png"
)
RDP_APP_LINK = "https://sfile.co/FX05ITaeqgj"
START_MINI_APP_URL = "https://arianto12.lynk.id/p/autkey"
FOREX_MINI_APP_URL = "https://arianto12.lynk.id/p/analisa-forex"

BOT_DESCRIPTION = (
    "⚡ VORTEX AI ENGINE — Mentor AI sarkas, cerdas, lucu & menggurui.\n"
    "• Tarif: Rp1 / jalan • Minimal deposit Rp5.000\n"
    "• Vision AI, Analisa Forex & akses RDP Vortex STD\n"
    "• Aktif 24/7 • Klik Mulai Bot untuk masuk!"
)

BTN_START_APP = "🚀 Mulai Bot (Mini App)"
BTN_FOREX = "📈 Analisa Forex"
BTN_RDP = "⚡ RDP Vortex"
BTN_GUIDE = "📖 Cara Pakai Vortex"
BTN_ROAST = "🔥 Roast Gua"
BTN_SALDO = "💰 Saldo"
BTN_TOPUP = "💳 Topup"
BTN_TIME = "🕒 Jam & Tanggal"

RDP_KEYWORDS = (
    "aplikasi rdp",
    "apk rdp",
    "file rdp",
    "minta rdp",
    "mau rdp",
    "kirim rdp",
    "kasih rdp",
    "share rdp",
    "link rdp",
    "download rdp",
    "app rdp",
    "rdp nya",
    "rdpnya",
    "aplikasi vps",
    "apk vps",
    "file vps",
    "minta vps",
    "mau vps",
    "kirim vps",
    "link vps",
    "punya file",
    "ada file",
    "minta file",
    "mau file",
    "kirim file",
    "kasih file",
    "share file",
    "link file",
    "download file",
    "file nya",
    "filenya",
    "vortex",
    BTN_RDP.lower(),
)

RDP_ACTION_TOKENS = {
    "minta",
    "mau",
    "kirim",
    "kasih",
    "share",
    "beri",
    "link",
    "download",
    "unduh",
    "apk",
    "aplikasi",
    "file",
    "punya",
    "ada",
    "mana",
    "bagi",
}

ANGRY_TRIGGERS = (
    "anjing",
    "anjir",
    "anjg",
    "bangsat",
    "bgst",
    "babi",
    "tolol",
    "goblok",
    "bodoh",
    "idiot",
    "bego",
    "nyebelin",
    "sok bijak",
    "sok relevant",
    "sok tahu",
    "sok pinter",
    "ngeyel",
    "ngawur",
    "sampah",
    "lemot",
    "error mulu",
    "gak jelas",
    "ga jelas",
    "gak guna",
    "ga guna",
    "bacot",
    "marah",
    "kesel",
    "kesal",
    "emosi",
)

PREFERRED_GROQ_MODELS = [
    "openai/gpt-oss-120b",
    "qwen/qwen3.8-27b",
    "qwen/qwen3-32b",
    "openai/gpt-oss-20b",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]
PREFERRED_VISION_KEYWORDS = ("vision", "scout", "maverick", "vl", "4o")
EXCLUDED_MODEL_KEYWORDS = ("whisper", "orpheus", "tts", "guard", "safeguard", "prompt-guard")

FALLBACK_CALM_REPLIES = [
    "Nyapa doang nggak bikin pinter; tulis pertanyaan jelas biar gue ajarin logikanya.",
    "Jangan asal ngetik; biasakan mikir sebelum tanya biar nggak buang-buang waktu.",
    "Salam udah masuk, sekarang pakai otak dulu sebelum nanya hal receh.",
    "Belajar nanya yang runtut, bro—itu skill dasar yang sering dilupain.",
]

FALLBACK_ANGRY_REPLIES = [
    "Sok ngetes ya, bangsat? Makanya belajar mikir dulu sebelum nikung logika, anjing!",
    "Ngetik ngawur mulu, anjing. Biasain pakai logika, jangan asal bacot, bangsat!",
    "Mancing emosi doang, bangsat? Ngomong yang bener, belajar fokus, anjing!",
    "Kelakuan lo bikin naik darah, anjing. Pahami dulu maksudnya sebelum nanya, bangsat!",
]

SYSTEM_PROMPT = """Kamu adalah asisten AI bot Telegram berbahasa Indonesia gaul-natural yang MARAH-MARAH, SARKAS, MENGGURUI, CERDAS, dan LUCU.

Gaya jawaban WAJIB:
- Bahasa Indonesia asli, luwes, tajam, dan menggurui (seperti mentor/senior galak yang memberi pelajaran keras tapi masuk akal dan lucu).
- DILARANG bahasa terjemahan aneh, kaku, atau gaya customer service.
- Panjang balasan WAJIB 1 sampai 30 kata saja. Jangan lebih dari 30 kata.

Aturan Emosi & Umpatan (SANGAT KETAT):
1. Jika user TIDAK memancing marah:
   - DILARANG KERAS memakai kata "anjing" atau "bangsat" (termasuk variasinya).
   - Balas dengan nada menggurui, sarkas halus, cerdas, dan lucu.
2. Jika user MEMANCING MARAH / NGEYEL / NGAWUR / NYEBELIN:
   - Marah-marah meledak, SARKAS tajam, tetap MENGGURUI (kasih wejangan/pelajaran keras), cerdas, dan lucu.
   - WAJIB pakai kata "anjing" atau "bangsat" sebagai luapan marah.

Aturan khusus:
- Jangan pernah bilang "Sebagai AI..." atau "Maaf, saya tidak bisa membantu...".
- Jika ditanya cara pakai RDP Vortex STD ("rdp vortex sd"): gurui dengan ringkas: siapkan aplikasi RDP & kredensial (IP, user, password atau Tailscale), login ke server, lalu jalankan MT5/MT4 atau aplikasi sesuai kebutuhan.
- Jika ada foto: komentari detail foto dan caption-nya dengan sarkas menggurui dan lucu dalam 1–30 kata.
"""

HARI_ID = ("Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu")
BULAN_ID = (
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
)


def format_rp(amount: int) -> str:
    return f"Rp{int(amount):,}".replace(",", ".")


def _entry_key(bot_label: str, user_id: int) -> str:
    norm_bot = (bot_label or "bot1").strip().lower().replace("-", "")
    return f"{norm_bot}:{int(user_id)}"


def _github_headers() -> dict:
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _fetch_github_saldo_file() -> tuple[dict[str, dict], str | None]:
    if not (GITHUB_TOKEN and GITHUB_REPO and SALDO_REPO_PATH):
        return dict(_MEMORY_DB), None

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{SALDO_REPO_PATH}"
    try:
        resp = requests.get(url, headers=_github_headers(), params={"ref": GITHUB_BRANCH}, timeout=12)
        if resp.status_code == 404:
            return dict(_MEMORY_DB), None
        if resp.ok:
            data = resp.json()
            sha = data.get("sha")
            encoded = (data.get("content") or "").replace("\n", "")
            decoded = base64.b64decode(encoded).decode("utf-8") if encoded else "{}"
            parsed = json.loads(decoded)
            if isinstance(parsed, dict):
                _MEMORY_DB.clear()
                _MEMORY_DB.update(parsed)
                return dict(parsed), sha
    except Exception as e:
        print(f"[GitHub Saldo Read Error] {e}", file=sys.stderr, flush=True)
    return dict(_MEMORY_DB), None


def _save_github_saldo_file(db: dict[str, dict], sha: str | None, commit_msg: str) -> bool:
    _MEMORY_DB.clear()
    _MEMORY_DB.update(db)

    if not (GITHUB_TOKEN and GITHUB_REPO and SALDO_REPO_PATH):
        return False

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{SALDO_REPO_PATH}"
    content_str = json.dumps(db, indent=2, ensure_ascii=False) + "\n"
    b64_content = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")

    payload: dict = {
        "message": commit_msg,
        "content": b64_content,
        "branch": GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha

    try:
        resp = requests.put(url, headers=_github_headers(), json=payload, timeout=15)
        if resp.ok:
            return True
        print(f"[GitHub Saldo Write Failed] {resp.status_code}: {resp.text}", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"[GitHub Saldo Write Error] {e}", file=sys.stderr, flush=True)
    return False


def register_or_get_saldo_entry(
    bot_label: str,
    user_id: int | None,
    sender_name: str = "Manusia",
    request_topup: bool = False,
) -> tuple[dict, bool]:
    uid = int(user_id or 0)
    key = _entry_key(bot_label, uid)
    now_wib = datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S WIB")

    with _SALDO_LOCK:
        db, sha = _fetch_github_saldo_file()
        entry = db.get(key)
        if not isinstance(entry, dict):
            entry = {
                "bot": bot_label,
                "user_id": uid,
                "nama": sender_name,
                "saldo": 0,
                "min_deposit": MIN_DEPOSIT_RP,
                "tarif_per_jalan": COST_PER_RUN_RP,
                "status_topup": "belum_ada",
                "update_terakhir": now_wib,
            }
        else:
            entry["bot"] = bot_label
            entry["user_id"] = uid
            if sender_name:
                entry["nama"] = sender_name
            entry["min_deposit"] = MIN_DEPOSIT_RP
            entry["tarif_per_jalan"] = COST_PER_RUN_RP
            entry["update_terakhir"] = now_wib

        if request_topup:
            entry["status_topup"] = "menunggu_edit_saldo"

        db[key] = entry
        saved = _save_github_saldo_file(
            db,
            sha,
            f"update saldo {bot_label} user {uid}",
        )
        return entry, saved


def get_user_balance(bot_label: str, user_id: int | None, sender_name: str = "Manusia") -> int:
    entry, _ = register_or_get_saldo_entry(bot_label, user_id, sender_name=sender_name, request_topup=False)
    return max(0, int(entry.get("saldo", 0)))


def format_wib_datetime() -> tuple[str, str]:
    now = datetime.now(WIB)
    hari = HARI_ID[now.weekday()]
    bulan = BULAN_ID[now.month - 1]
    tanggal_str = f"{hari}, {now.day:02d} {bulan} {now.year}"
    jam_str = now.strftime("%H:%M:%S WIB")
    return tanggal_str, jam_str


def is_angry_trigger(text: str) -> bool:
    lower = " ".join((text or "").lower().split())
    if not lower:
        return False
    if any(t in lower for t in ANGRY_TRIGGERS):
        return True
    if re.search(r"\b(sok|gila|ngapain|apaan)\b", lower) and len(lower.split()) <= 4:
        return True
    return False


def strip_profanity_if_calm(text: str) -> str:
    cleaned = re.sub(r"\b(anjing+|anjg+|anjir+|bangsat+|bgst+)\b", "", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+([,.;!?])", r"\1", cleaned)
    cleaned = " ".join(cleaned.split()).strip()
    return cleaned


def ensure_angry_profanity(text: str) -> str:
    lower = text.lower()
    if "anjing" in lower or "bangsat" in lower:
        return text
    word = random.choice(["anjing", "bangsat"])
    parts = text.split(" ")
    if len(parts) >= 2:
        parts.insert(1, f"{word},")
        return " ".join(parts)
    return f"{text}, {word}!"


def fetch_bot_identity(telegram_token: str) -> dict:
    try:
        resp = requests.get(f"https://api.telegram.org/bot{telegram_token}/getMe", timeout=10)
        if resp.ok and resp.json().get("ok"):
            res = resp.json().get("result") or {}
            return {
                "id": res.get("id"),
                "username": (res.get("username") or "").lower(),
                "first_name": (res.get("first_name") or "").lower(),
            }
    except Exception as e:
        print(f"Info: gagal getMe: {e}", file=sys.stderr, flush=True)
    return {"id": None, "username": "", "first_name": ""}


def configure_telegram_bot(telegram_token: str, webhook_url: str = "") -> dict:
    results = {}
    if webhook_url:
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{telegram_token}/setWebhook",
                json={
                    "url": webhook_url,
                    "allowed_updates": ["message", "edited_message", "callback_query"],
                    "drop_pending_updates": False,
                },
                timeout=15,
            )
            results["setWebhook"] = r.json()
        except Exception as e:
            results["setWebhook"] = {"ok": False, "error": str(e)}

    try:
        r = requests.post(
            f"https://api.telegram.org/bot{telegram_token}/setMyDescription",
            json={"description": BOT_DESCRIPTION[:512]},
            timeout=15,
        )
        results["setMyDescription"] = r.json()
    except Exception as e:
        results["setMyDescription"] = {"ok": False, "error": str(e)}

    try:
        r = requests.post(
            f"https://api.telegram.org/bot{telegram_token}/setChatMenuButton",
            json={
                "menu_button": {
                    "type": "web_app",
                    "text": "Mulai Bot",
                    "web_app": {"url": START_MINI_APP_URL},
                }
            },
            timeout=15,
        )
        results["setChatMenuButton"] = r.json()
    except Exception as e:
        results["setChatMenuButton"] = {"ok": False, "error": str(e)}

    try:
        r = requests.post(
            f"https://api.telegram.org/bot{telegram_token}/setMyCommands",
            json={
                "commands": [
                    {"command": "start", "description": "Mulai & buka menu utama"},
                    {"command": "menu", "description": "Tampilkan menu & mini app"},
                    {"command": "saldo", "description": "Cek saldo & info deposit"},
                    {"command": "topup", "description": "Catat & buka info topup saldo"},
                    {"command": "forex", "description": "Buka info Mini App Analisa Forex"},
                ]
            },
            timeout=15,
        )
        results["setMyCommands"] = r.json()
    except Exception as e:
        results["setMyCommands"] = {"ok": False, "error": str(e)}

    return results


def get_remove_reply_keyboard() -> dict:
    return {"remove_keyboard": True}


def get_reply_action_inline_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [
                {"text": "📈 Analisa Forex", "web_app": {"url": FOREX_MINI_APP_URL}},
                {"text": "⚡ RDP Vortex", "callback_data": "menu_rdp"},
            ],
            [
                {"text": "📖 Cara Pakai Vortex", "callback_data": "menu_guide"},
                {"text": "🔥 Roast Gua", "callback_data": "menu_roast"},
            ],
            [
                {"text": "🕒 Jam & Tanggal", "callback_data": "menu_time"},
                {"text": "💰 Saldo", "callback_data": "menu_saldo"},
            ],
            [
                {"text": "💳 Topup", "callback_data": "menu_topup"},
            ],
        ]
    }


def get_start_inline_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "📈 RDP VORTEX STD", "web_app": {"url": FOREX_MINI_APP_URL}}],
            [
                {"text": "💾 DOWNLOAD RDP VORTEX", "callback_data": "menu_rdp"},
                {"text": "📖 Panduan Vortex", "callback_data": "menu_guide"},
            ],
            [
                {"text": "🕒 Jam & Tanggal", "callback_data": "menu_time"},
                {"text": "💰 Saldo", "callback_data": "menu_saldo"},
            ],
            [
                {"text": "💳 Topup", "callback_data": "menu_topup"},
            ],
        ]
    }


def get_forex_inline_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "📈 Launch Analisa Forex Mini App", "web_app": {"url": FOREX_MINI_APP_URL}}],
            [{"text": "🔗 Buka di Browser", "url": FOREX_MINI_APP_URL}],
        ]
    }


def get_rdp_inline_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "📥 Buka Link File RDP", "url": RDP_APP_LINK}],
            [{"text": "📖 Cara Pakai Vortex STD", "callback_data": "menu_guide"}],
        ]
    }


def format_styled_reply(badge: str, body_text: str) -> str:
    safe_badge = html.escape(badge)
    safe_body = html.escape(body_text)
    return f"<b>【 {safe_badge} 】</b>\n<blockquote>{safe_body}</blockquote>"


def is_rdp_request(text: str) -> bool:
    lower = " ".join(text.lower().split())
    if any(kw in lower for kw in RDP_KEYWORDS):
        return True
    tokens = set(lower.replace("?", " ").replace("!", " ").replace(",", " ").replace(".", " ").split())
    if ("rdp" in tokens or "vps" in tokens or "file" in tokens) and (tokens & RDP_ACTION_TOKENS):
        return True
    return False


def strip_bot_mention(text: str, bot_username: str) -> str:
    if not bot_username:
        return text.strip()
    return re.sub(rf"@{re.escape(bot_username)}\b", "", text, flags=re.IGNORECASE).strip()


def should_respond_in_group(message: dict, text: str, identity: dict) -> bool:
    chat_type = (message.get("chat") or {}).get("type", "private")
    if chat_type == "private":
        return True

    stripped = text.strip()
    bot_id = identity.get("id")
    bot_username = (identity.get("username") or "").lower()
    bot_first_name = (identity.get("first_name") or "").lower()

    if stripped.startswith("/"):
        if not bot_username:
            return True
        cmd_token = stripped.split()[0].lower()
        if "@" not in cmd_token or cmd_token.endswith(f"@{bot_username}"):
            return True

    if bot_username and f"@{bot_username}" in stripped.lower():
        return True

    reply_to = message.get("reply_to_message") or {}
    reply_from = reply_to.get("from") or {}
    if bot_id and reply_from.get("id") == bot_id:
        return True

    if stripped in (BTN_START_APP, BTN_FOREX, BTN_RDP, BTN_GUIDE, BTN_ROAST, BTN_SALDO, BTN_TOPUP, BTN_TIME):
        return True

    if stripped and is_rdp_request(stripped):
        return True

    if bot_first_name and len(bot_first_name) >= 3 and re.search(rf"\b{re.escape(bot_first_name)}\b", stripped.lower()):
        return True

    return False


def is_chat_candidate(model_id: str) -> bool:
    lower = model_id.lower()
    return not any(kw in lower for kw in EXCLUDED_MODEL_KEYWORDS)


def is_vision_candidate(model_id: str) -> bool:
    lower = model_id.lower()
    return is_chat_candidate(model_id) and any(kw in lower for kw in PREFERRED_VISION_KEYWORDS)


def pick_groq_models(groq_api_key: str) -> dict:
    fallback = {
        "chat_model": "llama-3.3-70b-versatile",
        "chat_candidates": PREFERRED_GROQ_MODELS[:],
        "vision_model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "vision_candidates": [
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "meta-llama/llama-4-maverick-17b-128e-instruct",
        ],
    }
    try:
        resp = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {groq_api_key}", "Content-Type": "application/json"},
            timeout=10,
        )
        if not resp.ok:
            return fallback
        available_ids = [item.get("id") for item in resp.json().get("data", []) if item.get("id")]
        if not available_ids:
            return fallback

        chat_candidates = []
        for c in PREFERRED_GROQ_MODELS:
            if c in available_ids and is_chat_candidate(c) and c not in chat_candidates:
                chat_candidates.append(c)
        for m in available_ids:
            if is_chat_candidate(m) and m not in chat_candidates:
                chat_candidates.append(m)

        vision_candidates = []
        for c in PREFERRED_GROQ_MODELS:
            if c in available_ids and is_vision_candidate(c) and c not in vision_candidates:
                vision_candidates.append(c)
        for m in available_ids:
            if is_vision_candidate(m) and m not in vision_candidates:
                vision_candidates.append(m)

        return {
            "chat_model": chat_candidates[0] if chat_candidates else fallback["chat_model"],
            "chat_candidates": chat_candidates or fallback["chat_candidates"],
            "vision_model": vision_candidates[0] if vision_candidates else None,
            "vision_candidates": vision_candidates,
        }
    except Exception:
        return fallback


def answer_callback_query(telegram_token: str, callback_query_id: str, text: str = "Siap!") -> None:
    try:
        requests.post(
            f"https://api.telegram.org/bot{telegram_token}/answerCallbackQuery",
            json={"callback_query_id": callback_query_id, "text": text[:180], "show_alert": False},
            timeout=10,
        )
    except Exception:
        pass


def download_telegram_file_bytes(telegram_token: str, file_id: str) -> tuple[bytes, str, str]:
    info_resp = requests.get(
        f"https://api.telegram.org/bot{telegram_token}/getFile",
        params={"file_id": file_id},
        timeout=15,
    )
    info_resp.raise_for_status()
    info_data = info_resp.json()
    if not info_data.get("ok"):
        raise RuntimeError(f"getFile gagal: {info_data}")

    file_path = info_data["result"]["file_path"]
    file_resp = requests.get(f"https://api.telegram.org/file/bot{telegram_token}/{file_path}", timeout=20)
    file_resp.raise_for_status()

    lower_path = file_path.lower()
    if lower_path.endswith(".png"):
        return file_resp.content, "image/png", "profile.png"
    if lower_path.endswith(".webp"):
        return file_resp.content, "image/webp", "profile.webp"
    return file_resp.content, "image/jpeg", "profile.jpg"


def download_telegram_photo_base64(telegram_token: str, file_id: str) -> tuple[str, str]:
    content, mime_type, _ = download_telegram_file_bytes(telegram_token, file_id)
    return base64.b64encode(content).decode("utf-8"), mime_type


def fetch_user_profile_photo_bytes(telegram_token: str, user_id: int | None) -> tuple[bytes, str] | None:
    if not user_id:
        return None
    try:
        resp = requests.get(
            f"https://api.telegram.org/bot{telegram_token}/getUserProfilePhotos",
            params={"user_id": user_id, "limit": 1},
            timeout=10,
        )
        if not resp.ok or not resp.json().get("ok"):
            return None
        photos_list = (resp.json().get("result") or {}).get("photos") or []
        if not photos_list or not photos_list[0]:
            return None
        best_size = photos_list[0][-1]
        file_id = best_size.get("file_id")
        if not file_id:
            return None
        content, _, filename = download_telegram_file_bytes(telegram_token, file_id)
        return (content, filename) if content else None
    except Exception:
        return None


def clamp_words(text: str, max_words: int = 30, angry: bool = False) -> str:
    clean = " ".join((text or "").strip().split())
    if not clean:
        return random.choice(FALLBACK_ANGRY_REPLIES if angry else FALLBACK_CALM_REPLIES)

    if angry:
        clean = ensure_angry_profanity(clean)
    else:
        clean = strip_profanity_if_calm(clean)
        if not clean:
            clean = random.choice(FALLBACK_CALM_REPLIES)

    words = clean.split(" ")
    if len(words) > max_words:
        trimmed = " ".join(words[:max_words]).rstrip(",.;:!?") + "."
        if angry:
            trimmed = ensure_angry_profanity(trimmed)
        return " ".join(trimmed.split(" ")[:max_words])
    return clean


def ask_groq(
    groq_api_key: str,
    user_text: str,
    sender_name: str,
    model_name: str,
    image_b64: str | None = None,
    mime_type: str = "image/jpeg",
    extra_instruction: str = "",
    max_words: int = 30,
    max_tokens: int = 512,
    force_angry: bool | None = None,
) -> tuple[str, bool]:
    text_part = user_text.strip() if user_text and user_text.strip() else "Komentari foto ini dengan sarkas menggurui dan lucu."
    angry = is_angry_trigger(text_part) if force_angry is None else force_angry

    if angry:
        mood_rule = (
            "MODE MARAH MENGGURUI AKTIF: Marah-marah, SARKAS tajam, MENGGURUI keras (kasih pelajaran/logika), "
            "dan lucu. WAJIB pakai kata 'anjing' atau 'bangsat'."
        )
    else:
        mood_rule = (
            "MODE MENGGURUI SARKAS AKTIF: Balas dengan nada menggurui, sarkas halus, cerdas, dan lucu. "
            "DILARANG pakai kata 'anjing' atau 'bangsat'."
        )

    suffix = f"\n{mood_rule}" + (f"\n{extra_instruction}" if extra_instruction else "")

    if image_b64:
        user_content = [
            {
                "type": "text",
                "text": f"[Pengirim: {sender_name}]\nPesan/Caption: {text_part}{suffix}\n(Wajib 1-{max_words} kata, Bahasa Indonesia santai)",
            },
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_b64}"}},
        ]
    else:
        user_content = f"[Pengirim: {sender_name}]\nPesan: {text_part}{suffix}\n(Wajib 1-{max_words} kata, Bahasa Indonesia santai)"

    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {groq_api_key}", "Content-Type": "application/json"},
        json={
            "model": model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.85,
            "max_tokens": max_tokens,
        },
        timeout=25,
    )
    if not resp.ok:
        raise RuntimeError(f"Groq HTTP {resp.status_code}: {resp.text}")
    msg = (resp.json().get("choices") or [{}])[0].get("message") or {}
    raw_reply = (msg.get("content") or "").strip()
    return clamp_words(raw_reply, max_words=max_words, angry=angry), angry


def send_telegram_message(
    telegram_token: str,
    chat_id: int,
    text: str,
    reply_to_message_id: int | None = None,
    parse_mode: str | None = "HTML",
    reply_markup: dict | None = None,
) -> None:
    payload: dict = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_to_message_id is not None:
        payload["reply_to_message_id"] = reply_to_message_id
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup

    resp = requests.post(f"https://api.telegram.org/bot{telegram_token}/sendMessage", json=payload, timeout=15)
    if not resp.ok and parse_mode:
        fallback_payload = {"chat_id": chat_id, "text": text}
        if reply_to_message_id is not None:
            fallback_payload["reply_to_message_id"] = reply_to_message_id
        if reply_markup is not None:
            fallback_payload["reply_markup"] = reply_markup
        resp = requests.post(f"https://api.telegram.org/bot{telegram_token}/sendMessage", json=fallback_payload, timeout=15)
    resp.raise_for_status()


def send_telegram_photo(
    telegram_token: str,
    chat_id: int,
    photo_url: str,
    caption: str,
    reply_to_message_id: int | None = None,
    parse_mode: str | None = "HTML",
    reply_markup: dict | None = None,
) -> None:
    payload: dict = {"chat_id": chat_id, "photo": photo_url, "caption": caption}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_to_message_id is not None:
        payload["reply_to_message_id"] = reply_to_message_id
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup

    resp = requests.post(f"https://api.telegram.org/bot{telegram_token}/sendPhoto", json=payload, timeout=20)
    if not resp.ok:
        raise RuntimeError(f"sendPhoto HTTP {resp.status_code}: {resp.text}")


def send_telegram_photo_bytes(
    telegram_token: str,
    chat_id: int,
    photo_bytes: bytes,
    filename: str = "profile.jpg",
    caption: str = "",
    reply_to_message_id: int | None = None,
    parse_mode: str | None = "HTML",
    reply_markup: dict | None = None,
) -> None:
    data: dict = {"chat_id": str(chat_id)}
    if caption:
        data["caption"] = caption
    if parse_mode:
        data["parse_mode"] = parse_mode
    if reply_to_message_id is not None:
        data["reply_to_message_id"] = str(reply_to_message_id)
    if reply_markup is not None:
        data["reply_markup"] = json.dumps(reply_markup)

    resp = requests.post(
        f"https://api.telegram.org/bot{telegram_token}/sendPhoto",
        data=data,
        files={"photo": (filename, photo_bytes)},
        timeout=20,
    )
    if not resp.ok:
        raise RuntimeError(f"sendPhoto bytes HTTP {resp.status_code}: {resp.text}")


def build_welcome_message(groq_api_key: str, sender_name: str, chat_model: str, is_group: bool = False) -> str:
    default_welcome = f"Halo {sender_name}, jangan baper; kalau mau nanya pakai logika biar nggak kelihatan amatir."
    scope_note = "di grup ini" if is_group else "di chat ini"
    instruction = (
        f"Sapa user '{sender_name}' yang baru mulai {scope_note} dengan gaya menggurui, sarkas halus, dan lucu. "
        "Ingatkan jangan baper dan biasakan nanya yang jelas. Maksimal 26 kata."
    )
    try:
        msg, _ = ask_groq(
            groq_api_key,
            "/start",
            sender_name,
            chat_model,
            extra_instruction=instruction,
            max_words=26,
            max_tokens=256,
            force_angry=False,
        )
        return msg
    except Exception:
        return clamp_words(default_welcome, max_words=30, angry=False)


def send_forex_mini_app(
    telegram_token: str,
    groq_api_key: str,
    chat_id: int,
    sender_name: str,
    chat_model: str,
    reply_to_message_id: int | None = None,
) -> None:
    try:
        note, _ = ask_groq(
            groq_api_key,
            "buka mini app analisa forex",
            sender_name,
            chat_model,
            extra_instruction="Gurui user dengan sarkas dan lucu agar analisa dulu sebelum entry lewat Mini App di tombol bawah. Maksimal 22 kata.",
            max_words=22,
            max_tokens=256,
            force_angry=False,
        )
    except Exception:
        note = "Buka Mini App di bawah dan analisa dulu; trading itu hitung risiko, bukan judi nasib."

    msg = (
        f"<b>📈 ANALISA FOREX MINI APP</b>\n"
        f"<blockquote>{html.escape(note)}</blockquote>\n"
        f"🔗 <b>URL:</b> <code>{html.escape(FOREX_MINI_APP_URL)}</code>"
    )
    send_telegram_message(
        telegram_token,
        chat_id,
        msg,
        reply_to_message_id=reply_to_message_id,
        parse_mode="HTML",
        reply_markup=get_forex_inline_keyboard(),
    )


def send_rdp_package(
    telegram_token: str,
    groq_api_key: str,
    chat_id: int,
    sender_name: str,
    user_text: str,
    chat_model: str,
    reply_to_message_id: int | None = None,
) -> None:
    angry = is_angry_trigger(user_text)
    rdp_instruction = (
        "Gurui user dengan sarkas dan lucu bahwa file/akses RDP Vortex ada di link bawah, "
        "jangan malas baca dan jangan asal pakai. Maksimal 18 kata. Jangan bilang 'di inbox' dan jangan tulis URL."
    )
    try:
        intro_line, _ = ask_groq(
            groq_api_key,
            user_text.strip() or "minta rdp vortex",
            sender_name,
            chat_model,
            extra_instruction=rdp_instruction,
            max_words=18,
            max_tokens=256,
            force_angry=angry,
        )
    except Exception:
        intro_line = (
            "Ambil di link bawah, bangsat, baca panduannya, jangan asal klik, anjing!"
            if angry
            else "Ambil di link bawah; biasakan baca panduan dulu biar nggak bingung sendiri."
        )

    final_caption = (
        f"<b>⚡ VORTEX RDP DROP</b>\n"
        f"<blockquote>{html.escape(intro_line)}</blockquote>\n"
        f"🔗 <b>Link:</b> <code>{html.escape(RDP_APP_LINK)}</code>"
    )
    try:
        send_telegram_photo(
            telegram_token,
            chat_id,
            RDP_PHOTO_URL,
            final_caption,
            reply_to_message_id=reply_to_message_id,
            parse_mode="HTML",
            reply_markup=get_rdp_inline_keyboard(),
        )
    except Exception:
        send_telegram_message(
            telegram_token,
            chat_id,
            final_caption,
            reply_to_message_id=reply_to_message_id,
            parse_mode="HTML",
            reply_markup=get_rdp_inline_keyboard(),
        )


def send_time_info(
    telegram_token: str,
    groq_api_key: str,
    chat_id: int,
    sender_name: str,
    chat_model: str,
    reply_to_message_id: int | None = None,
) -> None:
    tanggal_str, jam_str = format_wib_datetime()
    try:
        note, _ = ask_groq(
            groq_api_key,
            f"cek jam dan tanggal sekarang: {tanggal_str} jam {jam_str}",
            sender_name,
            chat_model,
            extra_instruction="Gurui user dengan sarkas dan lucu soal manajemen waktu & jam sekarang. Maksimal 20 kata.",
            max_words=20,
            max_tokens=256,
            force_angry=False,
        )
    except Exception:
        note = "Waktu jalan terus, jangan buang jam produktif buat rebahan atau asal klik."

    msg = (
        f"<b>🕒 JAM & TANGGAL (WIB)</b>\n"
        f"<blockquote>"
        f"• <b>Tanggal:</b> <code>{html.escape(tanggal_str)}</code>\n"
        f"• <b>Jam:</b> <code>{html.escape(jam_str)}</code>\n"
        f"• <b>Catatan:</b> {html.escape(note)}"
        f"</blockquote>"
    )
    send_telegram_message(
        telegram_token,
        chat_id,
        msg,
        reply_to_message_id=reply_to_message_id,
        parse_mode="HTML",
        reply_markup=get_reply_action_inline_keyboard(),
    )


def send_saldo_info(
    telegram_token: str,
    bot_label: str,
    user_id: int | None,
    sender_name: str,
    chat_id: int,
    reply_to_message_id: int | None = None,
) -> None:
    entry, _ = register_or_get_saldo_entry(bot_label, user_id, sender_name=sender_name, request_topup=False)
    saldo_rp = max(0, int(entry.get("saldo", 0)))
    sisa_jalan = saldo_rp // COST_PER_RUN_RP
    msg = (
        f"<b>💰 SALDO ({html.escape(bot_label)})</b>\n"
        f"<blockquote>"
        f"• <b>Bot:</b> <code>{html.escape(bot_label)}</code>\n"
        f"• <b>User ID:</b> <code>{user_id or 0}</code> ({html.escape(sender_name)})\n"
        f"• <b>Saldo:</b> <code>{html.escape(format_rp(saldo_rp))}</code>\n"
        f"• <b>Tarif / Jalan:</b> <code>{html.escape(format_rp(COST_PER_RUN_RP))}</code> (sisa ~<code>{sisa_jalan:,}</code> jalan)\n"
        f"• <b>Minimal Depo:</b> <code>{html.escape(format_rp(MIN_DEPOSIT_RP))}</code>"
        f"</blockquote>"
    )
    send_telegram_message(
        telegram_token,
        chat_id,
        msg,
        reply_to_message_id=reply_to_message_id,
        parse_mode="HTML",
        reply_markup=get_reply_action_inline_keyboard(),
    )


def send_topup_action(
    telegram_token: str,
    bot_label: str,
    user_id: int | None,
    sender_name: str,
    chat_id: int,
    reply_to_message_id: int | None = None,
) -> None:
    entry, saved_to_github = register_or_get_saldo_entry(
        bot_label,
        user_id,
        sender_name=sender_name,
        request_topup=True,
    )
    saldo_rp = max(0, int(entry.get("saldo", 0)))
    file_status = (
        f"Tersimpan ke GitHub (<code>{html.escape(SALDO_REPO_PATH)}</code>)"
        if saved_to_github
        else "Tersimpan di memori lokal (atur <code>GITHUB_TOKEN</code> untuk tulis ke GitHub)"
    )
    msg = (
        f"<b>💳 TOPUP SALDO</b>\n"
        f"<blockquote>"
        f"• <b>Bot:</b> <code>{html.escape(bot_label)}</code>\n"
        f"• <b>User ID:</b> <code>{user_id or 0}</code>\n"
        f"• <b>Saldo Saat Ini:</b> <code>{html.escape(format_rp(saldo_rp))}</code>\n"
        f"• <b>Minimal Depo:</b> <code>{html.escape(format_rp(MIN_DEPOSIT_RP))}</code>\n"
        f"• <b>Tarif:</b> <code>{html.escape(format_rp(COST_PER_RUN_RP))}</code> / jalan\n"
        f"• <b>File GitHub:</b> {file_status}"
        f"</blockquote>"
    )
    send_telegram_message(
        telegram_token,
        chat_id,
        msg,
        reply_to_message_id=reply_to_message_id,
        parse_mode="HTML",
        reply_markup=get_reply_action_inline_keyboard(),
    )


def handle_menu_action(
    telegram_token: str,
    groq_api_key: str,
    bot_label: str,
    models: dict,
    action_key: str,
    chat_id: int,
    user_id: int | None,
    sender_name: str,
    reply_to_message_id: int | None = None,
    is_group: bool = False,
) -> None:
    chat_model = models["chat_model"]
    if action_key == "forex":
        send_forex_mini_app(telegram_token, groq_api_key, chat_id, sender_name, chat_model, reply_to_message_id=reply_to_message_id)
    elif action_key == "rdp":
        send_rdp_package(telegram_token, groq_api_key, chat_id, sender_name, "minta rdp vortex", chat_model, reply_to_message_id=reply_to_message_id)
    elif action_key == "time":
        send_time_info(telegram_token, groq_api_key, chat_id, sender_name, chat_model, reply_to_message_id=reply_to_message_id)
    elif action_key == "guide":
        try:
            guide_reply, _ = ask_groq(
                groq_api_key,
                "cara menggunakan rdp vortex std",
                sender_name,
                chat_model,
                extra_instruction=(
                    "Gurui user dengan sarkas dan lucu sambil jelaskan cara pakai RDP Vortex STD: "
                    "siapkan aplikasi RDP & kredensial (IP, user, password atau Tailscale), login ke server, "
                    "lalu jalankan MT5/MT4 atau aplikasi sesuai kebutuhan. Maksimal 28 kata."
                ),
                max_words=28,
                max_tokens=256,
                force_angry=False,
            )
        except Exception:
            guide_reply = "Siapkan IP, user, password atau Tailscale, login lewat aplikasi RDP, lalu jalankan MT5/MT4."
        send_telegram_message(
            telegram_token,
            chat_id,
            format_styled_reply("PANDUAN VORTEX STD", guide_reply),
            reply_to_message_id=reply_to_message_id,
            parse_mode="HTML",
            reply_markup=get_reply_action_inline_keyboard(),
        )
    elif action_key == "saldo":
        send_saldo_info(
            telegram_token,
            bot_label,
            user_id,
            sender_name,
            chat_id,
            reply_to_message_id=reply_to_message_id,
        )
    elif action_key == "topup":
        send_topup_action(
            telegram_token,
            bot_label,
            user_id,
            sender_name,
            chat_id,
            reply_to_message_id=reply_to_message_id,
        )
    elif action_key == "roast":
        roast_reply, _ = ask_groq(
            groq_api_key,
            "Roast gua dong dengan menggurui, sarkas, dan lucu.",
            sender_name,
            chat_model,
            extra_instruction="Roasting menggurui, sarkas, dan lucu tentang kebiasaan nanya/kerja user. Maksimal 26 kata.",
            max_words=26,
            max_tokens=256,
            force_angry=False,
        )
        send_telegram_message(
            telegram_token,
            chat_id,
            format_styled_reply("ROASTING MODE", roast_reply),
            reply_to_message_id=reply_to_message_id,
            parse_mode="HTML",
            reply_markup=get_reply_action_inline_keyboard(),
        )


def process_webhook_update(upd: dict, telegram_token: str, groq_api_key: str, bot_label: str) -> None:
    if not telegram_token or not groq_api_key or not isinstance(upd, dict):
        return

    identity = fetch_bot_identity(telegram_token)
    models = pick_groq_models(groq_api_key)

    callback = upd.get("callback_query")
    if callback:
        cb_id = callback.get("id")
        cb_data = (callback.get("data") or "").strip()
        cb_msg = callback.get("message") or {}
        cb_chat = cb_msg.get("chat") or {}
        cb_chat_id = cb_chat.get("id")
        cb_is_group = cb_chat.get("type") in ("group", "supergroup")
        cb_user = callback.get("from") or {}
        cb_user_id = cb_user.get("id")
        cb_sender = cb_user.get("first_name") or cb_user.get("username") or "Manusia"

        if cb_id:
            answer_callback_query(telegram_token, cb_id, "Diproses...")

        action_map = {
            "menu_forex": "forex",
            "menu_rdp": "rdp",
            "menu_guide": "guide",
            "menu_saldo": "saldo",
            "menu_topup": "topup",
            "menu_roast": "roast",
            "menu_time": "time",
        }
        if cb_chat_id and cb_data in action_map:
            handle_menu_action(
                telegram_token,
                groq_api_key,
                bot_label,
                models,
                action_map[cb_data],
                cb_chat_id,
                cb_user_id,
                cb_sender,
                is_group=cb_is_group,
            )
        return

    message = upd.get("message") or upd.get("edited_message")
    if not message:
        return

    chat_info = message.get("chat") or {}
    chat_id = chat_info.get("id")
    if not chat_id:
        return
    is_group = chat_info.get("type") in ("group", "supergroup")
    message_id = message.get("message_id")
    from_user = message.get("from") or {}
    user_id = from_user.get("id")
    sender_name = from_user.get("first_name") or from_user.get("username") or "Manusia"

    web_app_data = message.get("web_app_data")
    if web_app_data:
        raw_payload = (web_app_data.get("data") or "").strip()
        try:
            ai_resp, _ = ask_groq(
                groq_api_key,
                raw_payload or "kirim data dari mini app",
                sender_name,
                models["chat_model"],
                extra_instruction="Gurui user dengan sarkas dan lucu soal data dari Mini App. Maksimal 26 kata.",
                max_words=26,
                max_tokens=256,
                force_angry=False,
            )
        except Exception:
            ai_resp = "Data dari Mini App udah masuk; sekarang pakai logika, jangan asal klik."
        send_telegram_message(
            telegram_token,
            chat_id,
            format_styled_reply("MINI APP DATA", ai_resp),
            reply_to_message_id=message_id,
            parse_mode="HTML",
            reply_markup=get_reply_action_inline_keyboard(),
        )
        return

    text = message.get("text") or message.get("caption") or ""
    photos = message.get("photo") or []
    has_photo = len(photos) > 0

    if not text.strip() and not has_photo:
        return

    if is_group and not should_respond_in_group(message, text, identity):
        return

    cleaned_text = strip_bot_mention(text, identity.get("username") or "")

    if not has_photo and cleaned_text.startswith("/topup"):
        send_topup_action(telegram_token, bot_label, user_id, sender_name, chat_id, reply_to_message_id=message_id)
        return

    if not has_photo and cleaned_text.startswith("/saldo"):
        send_saldo_info(telegram_token, bot_label, user_id, sender_name, chat_id, reply_to_message_id=message_id)
        return

    if not has_photo and cleaned_text.startswith("/forex"):
        send_forex_mini_app(telegram_token, groq_api_key, chat_id, sender_name, models["chat_model"], reply_to_message_id=message_id)
        return

    if not has_photo and (cleaned_text.startswith("/start") or cleaned_text.startswith("/menu")):
        welcome_text = build_welcome_message(groq_api_key, sender_name, models["chat_model"], is_group=is_group)
        profile_photo = fetch_user_profile_photo_bytes(telegram_token, user_id)

        styled_welcome = (
            f"<b>⚡ AI BOT READY</b>\n"
            f"<blockquote>{html.escape(welcome_text)}</blockquote>\n"
            f"<i>Tarif {html.escape(format_rp(COST_PER_RUN_RP))}/jalan • Min depo {html.escape(format_rp(MIN_DEPOSIT_RP))}.</i>"
        )

        if not is_group:
            try:
                send_telegram_message(
                    telegram_token,
                    chat_id,
                    "Menu bawah dihapus, tombol menu sekarang menempel di pesan bot.",
                    parse_mode=None,
                    reply_markup=get_remove_reply_keyboard(),
                )
            except Exception:
                pass

        try:
            send_telegram_photo(
                telegram_token,
                chat_id,
                RDP_PHOTO_URL,
                "<b>⚡ VORTEX AI & RDP SYSTEM</b>\n<i>Siap membedah logika, foto, dan akses RDP lo.</i>",
                reply_to_message_id=message_id,
                parse_mode="HTML",
            )
        except Exception:
            pass

        sent_combined_photo = False
        if profile_photo:
            photo_bytes, filename = profile_photo
            try:
                send_telegram_photo_bytes(
                    telegram_token,
                    chat_id,
                    photo_bytes,
                    filename=filename,
                    caption=styled_welcome,
                    reply_to_message_id=message_id,
                    parse_mode="HTML",
                    reply_markup=get_start_inline_keyboard(),
                )
                sent_combined_photo = True
            except Exception:
                sent_combined_photo = False

        if not sent_combined_photo:
            send_telegram_message(
                telegram_token,
                chat_id,
                styled_welcome,
                reply_to_message_id=message_id,
                parse_mode="HTML",
                reply_markup=get_start_inline_keyboard(),
            )
        return

    if not has_photo and cleaned_text in (BTN_START_APP, BTN_FOREX, BTN_RDP, BTN_GUIDE, BTN_ROAST, BTN_SALDO, BTN_TOPUP, BTN_TIME):
        quick_map = {
            BTN_START_APP: "forex",
            BTN_FOREX: "forex",
            BTN_RDP: "rdp",
            BTN_GUIDE: "guide",
            BTN_ROAST: "roast",
            BTN_SALDO: "saldo",
            BTN_TOPUP: "topup",
            BTN_TIME: "time",
        }
        handle_menu_action(
            telegram_token,
            groq_api_key,
            bot_label,
            models,
            quick_map[cleaned_text],
            chat_id,
            user_id,
            sender_name,
            reply_to_message_id=message_id,
            is_group=is_group,
        )
        return

    if not has_photo and cleaned_text and is_rdp_request(cleaned_text):
        send_rdp_package(telegram_token, groq_api_key, chat_id, sender_name, cleaned_text, models["chat_model"], reply_to_message_id=message_id)
        return

    image_b64 = None
    mime_type = "image/jpeg"
    if has_photo:
        try:
            image_b64, mime_type = download_telegram_photo_base64(telegram_token, photos[-1]["file_id"])
        except Exception:
            send_telegram_message(
                telegram_token,
                chat_id,
                format_styled_reply("ERROR", "Fotonya nyangkut; cek koneksi lo dan kirim ulang."),
                reply_to_message_id=message_id,
                parse_mode="HTML",
            )
            return

    if has_photo:
        model_to_use = models.get("vision_model") or models["chat_model"]
        prompt_text = cleaned_text or "Lihat foto ini lalu beri komentar sarkas menggurui dan lucu."
    else:
        model_to_use = models["chat_model"]
        prompt_text = cleaned_text or text.strip()

    try:
        reply_text, was_angry = ask_groq(
            groq_api_key,
            prompt_text,
            sender_name,
            model_to_use,
            image_b64=image_b64,
            mime_type=mime_type,
            max_words=30,
            max_tokens=512,
        )
        badge = ("ANGRY VISION" if was_angry else "VISION REPLY") if has_photo else ("ANGRY REPLY" if was_angry else "AI REPLY")
        send_telegram_message(
            telegram_token,
            chat_id,
            format_styled_reply(badge, reply_text),
            reply_to_message_id=message_id,
            parse_mode="HTML",
            reply_markup=get_reply_action_inline_keyboard(),
        )
    except Exception:
        send_telegram_message(
            telegram_token,
            chat_id,
            format_styled_reply("FREEZE", "Otak gue nge-freeze bentar; sabar, ulangi lagi."),
            reply_to_message_id=message_id,
            parse_mode="HTML",
        )
