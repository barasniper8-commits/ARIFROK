import base64
import html
import json
import os
import random
import re
import shutil
import sys
import time
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "9253138868:AAFXhdgueoLoR-Sx8cY3jsbwb2uZQXPyD6A")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")

RDP_PHOTO_URL = (
    "https://blogger.googleusercontent.com/img/b/R29vZ2xl/"
    "AVvXsEhUqjQ4dcVH11aoJxMqho_CMCB9SnH4yepKrcVtuMD_FvAa-21zb-WL4M6TSQOPWf3vo54zKVIiPrdfhSH7AITPUsB_HRKm0ODtsRL_lZ7p_QU1aDfIyd2W6-OQdjPa1Xjc78aEk0lei_9YLG6_ZsgsNq9r5sEIHzUGMeY8B-Agl5Z6Puc38O02XrJujXU/"
    "s1600/1000196027.png"
)
RDP_APP_LINK = "https://sfile.co/FX05ITaeqgj"
START_MINI_APP_URL = "https://arianto12.lynk.id/p/ganjeng"
FOREX_MINI_APP_URL = "https://arianto12.lynk.id/p/analisa-forex"

BOT_DESCRIPTION = (
    "Asisten AI bot Telegram sarkas, cerdas, lucu, dan menggurui. "
    "Akses RDP Vortex STD, panduan penggunaan, dan Mini App."
)

BTN_START_APP = "🚀 Mulai Bot (Mini App)"
BTN_FOREX = "📈 Analisa Forex"
BTN_RDP = "⚡ RDP Vortex"
BTN_GUIDE = "📖 Cara Pakai Vortex"
BTN_ROAST = "🔥 Roast Gua"
BTN_STATUS = "📊 Status Bot"

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

OFFSET_FILE = "last_offset.json"
RUN_DURATION_SECONDS = 6 * 60 * 60  # 6 jam (sesuai kode awal)
POLL_INTERVAL_SECONDS = 5          # jeda cek pesan baru (detik)

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


def get_battery_status() -> str:
    """Membaca status baterai jika tersedia di OS/sysfs, atau mengembalikan info host/server."""
    # Coba modul psutil jika terpasang
    try:
        import psutil  # type: ignore

        batt = psutil.sensors_battery()
        if batt is not None:
            pct = round(batt.percent)
            plug = "Mengisi daya" if batt.power_plugged else "Baterai"
            return f"{pct}% ({plug})"
    except Exception:
        pass

    # Coba Linux /sys/class/power_supply
    power_root = "/sys/class/power_supply"
    if os.path.isdir(power_root):
        try:
            for entry in sorted(os.listdir(power_root)):
                cap_path = os.path.join(power_root, entry, "capacity")
                status_path = os.path.join(power_root, entry, "status")
                if os.path.isfile(cap_path):
                    with open(cap_path, "r", encoding="utf-8") as f:
                        pct = f.read().strip()
                    status = ""
                    if os.path.isfile(status_path):
                        with open(status_path, "r", encoding="utf-8") as f:
                            status = f.read().strip()
                    return f"{pct}% ({status})" if status else f"{pct}%"
        except Exception:
            pass

    # Fallback jika berjalan di server / container tanpa sensor baterai
    env_batt = os.getenv("BATTERY_STATUS")
    if env_batt:
        return env_batt
    return "AC / Cloud Host"


def _format_bytes(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    val = float(max(0, num_bytes))
    idx = 0
    while val >= 1024 and idx < len(units) - 1:
        val /= 1024.0
        idx += 1
    return f"{val:.1f} {units[idx]}"


def get_ram_status() -> str:
    """Membaca penggunaan RAM sistem secara dinamis."""
    try:
        import psutil  # type: ignore

        vm = psutil.virtual_memory()
        return f"{_format_bytes(vm.used)} / {_format_bytes(vm.total)} ({vm.percent:.0f}%)"
    except Exception:
        pass

    meminfo_path = "/proc/meminfo"
    if os.path.isfile(meminfo_path):
        try:
            info: dict[str, int] = {}
            with open(meminfo_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.split(":")
                    if len(parts) == 2:
                        key = parts[0].strip()
                        val_kb = int(parts[1].strip().split()[0])
                        info[key] = val_kb * 1024
            total = info.get("MemTotal", 0)
            avail = info.get("MemAvailable", info.get("MemFree", 0))
            if total > 0:
                used = max(0, total - avail)
                pct = (used / total) * 100.0
                return f"{_format_bytes(used)} / {_format_bytes(total)} ({pct:.0f}%)"
        except Exception:
            pass

    return "Tidak terdeteksi"


def get_internal_storage_status() -> str:
    """Membaca kapasitas penyimpanan internal (disk utama)."""
    try:
        usage = shutil.disk_usage("/")
        used = usage.used
        total = usage.total
        pct = (used / total * 100.0) if total > 0 else 0.0
        return f"{_format_bytes(used)} / {_format_bytes(total)} ({pct:.0f}%)"
    except Exception:
        return "Tidak terdeteksi"


def format_remaining_time(remaining_sec: int) -> str:
    """
    Memformat sisa waktu. Jika <= 3660 detik (60 menit 60 detik), tampilkan dalam format
    '60 menit 60 detik' (menit bisa 0..60 dan detik 0..60 saat tepat di batas, atau standar mm:ss).
    Jika lebih dari itu, tampilkan jam, menit, detik.
    """
    sec = max(0, int(remaining_sec))
    if sec == 3660:
        return "60 menit 60 detik"
    if sec <= 3600:
        mins, rem = divmod(sec, 60)
        return f"{mins} menit {rem} detik"
    hours, rem = divmod(sec, 3600)
    mins, secs = divmod(rem, 60)
    return f"{hours} jam {mins} menit {secs} detik"


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


def register_bot_description() -> None:
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setMyDescription"
        resp = requests.post(url, json={"description": BOT_DESCRIPTION}, timeout=15)
        if resp.ok:
            print("Deskripsi bot (setMyDescription) berhasil diperbarui.", flush=True)
        else:
            print(f"Info: gagal setMyDescription ({resp.status_code}): {resp.text}", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"Info: gagal setMyDescription (diabaikan): {e}", file=sys.stderr, flush=True)


def register_chat_menu_button() -> None:
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setChatMenuButton"
        payload = {
            "menu_button": {
                "type": "web_app",
                "text": "Mulai Bot",
                "web_app": {"url": START_MINI_APP_URL},
            }
        }
        resp = requests.post(url, json=payload, timeout=15)
        if resp.ok:
            print(f"Menu button web_app berhasil diatur ke {START_MINI_APP_URL}.", flush=True)
        else:
            print(f"Info: gagal setChatMenuButton ({resp.status_code}): {resp.text}", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"Info: gagal setChatMenuButton (diabaikan): {e}", file=sys.stderr, flush=True)


def register_bot_commands() -> None:
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setMyCommands"
        commands = [
            {"command": "start", "description": "Mulai & buka menu utama"},
            {"command": "menu", "description": "Tampilkan menu & mini app"},
            {"command": "forex", "description": "Buka info Mini App Analisa Forex"},
            {"command": "rdp", "description": "Ambil link & info RDP Vortex"},
            {"command": "status", "description": "Cek status bot & perangkat"},
        ]
        requests.post(url, json={"commands": commands}, timeout=15)
    except Exception as e:
        print(f"Info: gagal setMyCommands (diabaikan): {e}", file=sys.stderr, flush=True)


def get_main_reply_keyboard() -> dict:
    return {
        "keyboard": [
            [{"text": BTN_START_APP, "web_app": {"url": START_MINI_APP_URL}}],
            [{"text": BTN_FOREX, "web_app": {"url": FOREX_MINI_APP_URL}}, {"text": BTN_RDP}],
            [{"text": BTN_GUIDE}, {"text": BTN_ROAST}, {"text": BTN_STATUS}],
        ],
        "resize_keyboard": True,
        "is_persistent": True,
        "input_field_placeholder": "Ketik pesan atau klik Mulai Bot...",
    }


def get_start_inline_keyboard() -> dict:
    return {
        "inline_keyboard": [
            [{"text": "🚀 Mulai Bot (Mini App)", "web_app": {"url": START_MINI_APP_URL}}],
            [{"text": "📈 Buka Mini App Analisa Forex", "web_app": {"url": FOREX_MINI_APP_URL}}],
            [
                {"text": "⚡ Ambil RDP Vortex", "callback_data": "menu_rdp"},
                {"text": "📖 Panduan Vortex", "callback_data": "menu_guide"},
            ],
            [
                {"text": "📊 Status Bot", "callback_data": "menu_status"},
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


def load_last_offset() -> int | None:
    if os.path.exists(OFFSET_FILE):
        try:
            with open(OFFSET_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("offset")
        except Exception:
            return None
    return None


def save_last_offset(offset: int) -> None:
    with open(OFFSET_FILE, "w", encoding="utf-8") as f:
        json.dump({"offset": offset}, f)


def is_rdp_request(text: str) -> bool:
    lower = " ".join(text.lower().split())
    if any(kw in lower for kw in RDP_KEYWORDS):
        return True
    tokens = set(lower.replace("?", " ").replace("!", " ").replace(",", " ").replace(".", " ").split())
    if ("rdp" in tokens or "vps" in tokens or "file" in tokens) and (tokens & RDP_ACTION_TOKENS):
        return True
    return False


def is_chat_candidate(model_id: str) -> bool:
    lower = model_id.lower()
    return not any(kw in lower for kw in EXCLUDED_MODEL_KEYWORDS)


def is_vision_candidate(model_id: str) -> bool:
    lower = model_id.lower()
    return is_chat_candidate(model_id) and any(kw in lower for kw in PREFERRED_VISION_KEYWORDS)


def test_groq_chat_model(model_name: str) -> bool:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "balas ok"}],
        "max_tokens": 16,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=25)
    return resp.ok


def resolve_groq_models() -> dict:
    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    resp = requests.get(url, headers=headers, timeout=20)
    if not resp.ok:
        raise RuntimeError(f"Gagal mengambil daftar model Groq ({resp.status_code}): {resp.text}")

    data = resp.json()
    available_ids = [item.get("id") for item in data.get("data", []) if item.get("id")]
    if not available_ids:
        raise RuntimeError("Daftar model Groq kosong untuk API key ini.")

    chat_candidates: list[str] = []
    for candidate in PREFERRED_GROQ_MODELS:
        if candidate in available_ids and is_chat_candidate(candidate) and candidate not in chat_candidates:
            chat_candidates.append(candidate)
    for model_id in available_ids:
        if is_chat_candidate(model_id) and model_id not in chat_candidates:
            chat_candidates.append(model_id)

    active_chat_model = None
    for model_id in chat_candidates:
        try:
            if test_groq_chat_model(model_id):
                active_chat_model = model_id
                break
        except Exception:
            continue

    if not active_chat_model:
        raise RuntimeError(f"Tidak ada model chat Groq yang lolos uji coba. Kandidat: {chat_candidates}")

    vision_candidates: list[str] = []
    for candidate in PREFERRED_GROQ_MODELS:
        if candidate in available_ids and is_vision_candidate(candidate) and candidate not in vision_candidates:
            vision_candidates.append(candidate)
    for model_id in available_ids:
        if is_vision_candidate(model_id) and model_id not in vision_candidates:
            vision_candidates.append(model_id)

    active_vision_model = None
    for model_id in vision_candidates:
        try:
            if test_groq_chat_model(model_id):
                active_vision_model = model_id
                break
        except Exception:
            continue

    return {
        "chat_model": active_chat_model,
        "chat_candidates": chat_candidates,
        "vision_model": active_vision_model,
        "vision_candidates": vision_candidates,
    }


def get_telegram_updates(offset: int | None) -> list:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"timeout": 10}
    if offset is not None:
        params["offset"] = offset

    resp = requests.get(url, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data}")
    return data.get("result", [])


def answer_callback_query(callback_query_id: str, text: str = "Siap!") -> None:
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery"
        requests.post(
            url,
            json={"callback_query_id": callback_query_id, "text": text[:180], "show_alert": False},
            timeout=15,
        )
    except Exception:
        pass


def download_telegram_file_bytes(file_id: str) -> tuple[bytes, str, str]:
    info_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile"
    info_resp = requests.get(info_url, params={"file_id": file_id}, timeout=20)
    info_resp.raise_for_status()
    info_data = info_resp.json()
    if not info_data.get("ok"):
        raise RuntimeError(f"Gagal ambil getFile Telegram: {info_data}")

    file_path = info_data["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
    file_resp = requests.get(file_url, timeout=30)
    file_resp.raise_for_status()

    lower_path = file_path.lower()
    if lower_path.endswith(".png"):
        mime_type = "image/png"
        filename = "profile.png"
    elif lower_path.endswith(".webp"):
        mime_type = "image/webp"
        filename = "profile.webp"
    else:
        mime_type = "image/jpeg"
        filename = "profile.jpg"

    return file_resp.content, mime_type, filename


def download_telegram_photo_base64(file_id: str) -> tuple[str, str]:
    content, mime_type, _ = download_telegram_file_bytes(file_id)
    b64_data = base64.b64encode(content).decode("utf-8")
    return b64_data, mime_type


def fetch_user_profile_photo_bytes(user_id: int | None) -> tuple[bytes, str] | None:
    """Mengambil foto profil terbaru user secara aman; mengembalikan None jika tidak ada atau gagal."""
    if not user_id:
        return None
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUserProfilePhotos"
        resp = requests.get(url, params={"user_id": user_id, "limit": 1}, timeout=15)
        if not resp.ok:
            return None
        data = resp.json()
        if not data.get("ok"):
            return None

        photos_list = (data.get("result") or {}).get("photos") or []
        if not photos_list or not photos_list[0]:
            return None

        best_size = photos_list[0][-1]
        file_id = best_size.get("file_id")
        if not file_id:
            return None

        content, _, filename = download_telegram_file_bytes(file_id)
        if not content:
            return None
        return content, filename
    except Exception as e:
        print(f"Info: gagal ambil foto profil user {user_id} (diabaikan): {e}", file=sys.stderr, flush=True)
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
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

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
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{image_b64}",
                },
            },
        ]
    else:
        user_content = f"[Pengirim: {sender_name}]\nPesan: {text_part}{suffix}\n(Wajib 1-{max_words} kata, Bahasa Indonesia santai)"

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.85,
        "max_tokens": max_tokens,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=45)
    if not resp.ok:
        raise RuntimeError(f"Groq HTTP {resp.status_code}: {resp.text}")
    data = resp.json()
    msg = (data.get("choices") or [{}])[0].get("message") or {}
    raw_reply = (msg.get("content") or "").strip()
    if not raw_reply:
        print(f"Peringatan: respon kosong dari {model_name}: {data}", file=sys.stderr, flush=True)
    return clamp_words(raw_reply, max_words=max_words, angry=angry), angry


def send_telegram_message(
    chat_id: int,
    text: str,
    reply_to_message_id: int | None = None,
    parse_mode: str | None = "HTML",
    reply_markup: dict | None = None,
) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload: dict = {
        "chat_id": chat_id,
        "text": text,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_to_message_id is not None:
        payload["reply_to_message_id"] = reply_to_message_id
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup

    resp = requests.post(url, json=payload, timeout=20)
    if not resp.ok and parse_mode:
        fallback_payload = {"chat_id": chat_id, "text": text}
        if reply_to_message_id is not None:
            fallback_payload["reply_to_message_id"] = reply_to_message_id
        if reply_markup is not None:
            fallback_payload["reply_markup"] = reply_markup
        resp = requests.post(url, json=fallback_payload, timeout=20)
    resp.raise_for_status()


def send_telegram_photo(
    chat_id: int,
    photo_url: str,
    caption: str,
    reply_to_message_id: int | None = None,
    parse_mode: str | None = "HTML",
    reply_markup: dict | None = None,
) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    payload: dict = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_to_message_id is not None:
        payload["reply_to_message_id"] = reply_to_message_id
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup

    resp = requests.post(url, json=payload, timeout=25)
    if not resp.ok:
        raise RuntimeError(f"Telegram sendPhoto HTTP {resp.status_code}: {resp.text}")


def send_telegram_photo_bytes(
    chat_id: int,
    photo_bytes: bytes,
    filename: str = "profile.jpg",
    caption: str = "",
    reply_to_message_id: int | None = None,
    parse_mode: str | None = "HTML",
    reply_markup: dict | None = None,
) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    data: dict = {"chat_id": str(chat_id)}
    if caption:
        data["caption"] = caption
    if parse_mode:
        data["parse_mode"] = parse_mode
    if reply_to_message_id is not None:
        data["reply_to_message_id"] = str(reply_to_message_id)
    if reply_markup is not None:
        data["reply_markup"] = json.dumps(reply_markup)

    files = {"photo": (filename, photo_bytes)}
    resp = requests.post(url, data=data, files=files, timeout=25)
    if not resp.ok:
        raise RuntimeError(f"Telegram sendPhoto bytes HTTP {resp.status_code}: {resp.text}")


def build_welcome_message(sender_name: str, state: dict) -> str:
    default_welcome = (
        f"Halo {sender_name}, jangan baper; kalau mau nanya pakai logika biar nggak kelihatan amatir."
    )
    instruction = (
        f"Sapa user '{sender_name}' yang baru klik /start dengan gaya menggurui, sarkas halus, dan lucu. "
        "Ingatkan jangan baper dan biasakan nanya yang jelas. Maksimal 26 kata."
    )
    try:
        msg, _ = ask_groq(
            "/start",
            sender_name,
            state["chat_model"],
            extra_instruction=instruction,
            max_words=26,
            max_tokens=256,
            force_angry=False,
        )
        return msg
    except Exception as e:
        print(f"Gagal bikin ucapan /start via Groq: {e}", file=sys.stderr, flush=True)
        return clamp_words(default_welcome, max_words=30, angry=False)


def send_forex_mini_app(chat_id: int, sender_name: str, state: dict, reply_to_message_id: int | None = None) -> None:
    try:
        note, _ = ask_groq(
            "buka mini app analisa forex",
            sender_name,
            state["chat_model"],
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
        chat_id,
        msg,
        reply_to_message_id=reply_to_message_id,
        parse_mode="HTML",
        reply_markup=get_forex_inline_keyboard(),
    )


def send_rdp_package(chat_id: int, sender_name: str, user_text: str, state: dict, reply_to_message_id: int | None = None) -> None:
    angry = is_angry_trigger(user_text)
    rdp_instruction = (
        "Gurui user dengan sarkas dan lucu bahwa file/akses RDP Vortex ada di link bawah, "
        "jangan malas baca dan jangan asal pakai. Maksimal 18 kata. Jangan bilang 'di inbox' dan jangan tulis URL."
    )
    try:
        intro_line, _ = ask_groq(
            user_text.strip() or "minta rdp vortex",
            sender_name,
            state["chat_model"],
            extra_instruction=rdp_instruction,
            max_words=18,
            max_tokens=256,
            force_angry=angry,
        )
    except Exception as e:
        print(f"Gagal bikin intro RDP: {e}", file=sys.stderr, flush=True)
        intro_line = (
            "Ambil di link bawah, bangsat, baca panduannya, jangan asal klik, anjing!"
            if angry
            else "Ambil di link bawah; biasakan baca panduan dulu biar nggak bingung sendiri."
        )

    safe_intro = html.escape(intro_line)
    safe_link = html.escape(RDP_APP_LINK)
    final_caption = (
        f"<b>⚡ VORTEX RDP DROP</b>\n"
        f"<blockquote>{safe_intro}</blockquote>\n"
        f"🔗 <b>Link:</b> <code>{safe_link}</code>"
    )
    try:
        send_telegram_photo(
            chat_id,
            RDP_PHOTO_URL,
            final_caption,
            reply_to_message_id=reply_to_message_id,
            parse_mode="HTML",
            reply_markup=get_rdp_inline_keyboard(),
        )
        print(f"Mengirim foto & link RDP Vortex ke {sender_name} (chat_id={chat_id}).", flush=True)
    except Exception as e:
        print(f"Gagal kirim foto RDP: {e}", file=sys.stderr, flush=True)
        send_telegram_message(
            chat_id,
            final_caption,
            reply_to_message_id=reply_to_message_id,
            parse_mode="HTML",
            reply_markup=get_rdp_inline_keyboard(),
        )


def send_vortex_guide(chat_id: int, sender_name: str, state: dict, reply_to_message_id: int | None = None) -> None:
    guide_instruction = (
        "Gurui user dengan sarkas dan lucu sambil jelaskan cara pakai RDP Vortex STD: "
        "siapkan aplikasi RDP & kredensial (IP, user, password atau Tailscale), login ke server, "
        "lalu jalankan MT5/MT4 atau aplikasi sesuai kebutuhan. Maksimal 28 kata."
    )
    try:
        guide_reply, _ = ask_groq(
            "cara menggunakan rdp vortex std",
            sender_name,
            state["chat_model"],
            extra_instruction=guide_instruction,
            max_words=28,
            max_tokens=256,
            force_angry=False,
        )
    except Exception:
        guide_reply = (
            "Siapkan IP, user, password atau Tailscale, login lewat aplikasi RDP, "
            "lalu jalankan MT5/MT4. Ikuti alurnya, jangan loncat-loncat."
        )

    formatted = format_styled_reply("PANDUAN VORTEX STD", guide_reply)
    send_telegram_message(
        chat_id,
        formatted,
        reply_to_message_id=reply_to_message_id,
        parse_mode="HTML",
        reply_markup=get_main_reply_keyboard(),
    )


def send_bot_status(
    chat_id: int,
    sender_name: str,
    end_time: float,
    reply_to_message_id: int | None = None,
) -> None:
    remaining_sec = max(0, int(end_time - time.monotonic()))
    sisa_waktu_str = format_remaining_time(remaining_sec)

    user_label = html.escape(sender_name or "Manusia")
    sisa_label = html.escape(sisa_waktu_str)
    battery_label = html.escape(get_battery_status())
    ram_label = html.escape(get_ram_status())
    internal_label = html.escape(get_internal_storage_status())

    status_msg = (
        f"<b>📊 BOT STATUS</b>\n"
        f"<blockquote>"
        f"• <b>Pengguna:</b> <code>{user_label}</code>\n"
        f"• <b>Sisa Waktu:</b> <code>{sisa_label}</code>\n"
        f"• <b>Baterai Daya:</b> <code>{battery_label}</code>\n"
        f"• <b>RAM:</b> <code>{ram_label}</code>\n"
        f"• <b>Internal:</b> <code>{internal_label}</code>"
        f"</blockquote>"
    )
    send_telegram_message(
        chat_id,
        status_msg,
        reply_to_message_id=reply_to_message_id,
        parse_mode="HTML",
        reply_markup=get_main_reply_keyboard(),
    )


def handle_menu_action(
    action_key: str,
    chat_id: int,
    sender_name: str,
    state: dict,
    end_time: float,
    reply_to_message_id: int | None = None,
) -> None:
    if action_key == "forex":
        send_forex_mini_app(chat_id, sender_name, state, reply_to_message_id=reply_to_message_id)
    elif action_key == "rdp":
        send_rdp_package(chat_id, sender_name, "minta rdp vortex", state, reply_to_message_id=reply_to_message_id)
    elif action_key == "guide":
        send_vortex_guide(chat_id, sender_name, state, reply_to_message_id=reply_to_message_id)
    elif action_key == "status":
        send_bot_status(chat_id, sender_name, end_time, reply_to_message_id=reply_to_message_id)
    elif action_key == "roast":
        roast_reply, _ = ask_groq(
            "Roast gua dong dengan menggurui, sarkas, dan lucu.",
            sender_name,
            state["chat_model"],
            extra_instruction="Roasting menggurui, sarkas, dan lucu tentang kebiasaan nanya/kerja user. Maksimal 26 kata.",
            max_words=26,
            max_tokens=256,
            force_angry=False,
        )
        send_telegram_message(
            chat_id,
            format_styled_reply("ROASTING MODE", roast_reply),
            reply_to_message_id=reply_to_message_id,
            parse_mode="HTML",
            reply_markup=get_main_reply_keyboard(),
        )


def poll_once(current_offset: int | None, state: dict, end_time: float) -> int | None:
    updates = get_telegram_updates(current_offset)
    if not updates:
        return current_offset

    max_update_id = None

    for upd in updates:
        update_id = upd.get("update_id")
        if update_id is not None:
            max_update_id = update_id if max_update_id is None else max(max_update_id, update_id)

        callback = upd.get("callback_query")
        if callback:
            cb_id = callback.get("id")
            cb_data = (callback.get("data") or "").strip()
            cb_msg = callback.get("message") or {}
            cb_chat_id = (cb_msg.get("chat") or {}).get("id")
            cb_user = callback.get("from") or {}
            cb_sender = cb_user.get("first_name") or cb_user.get("username") or "Manusia"

            if cb_id:
                answer_callback_query(cb_id, "Diproses...")

            if cb_chat_id:
                action_map = {
                    "menu_forex": "forex",
                    "menu_rdp": "rdp",
                    "menu_guide": "guide",
                    "menu_status": "status",
                    "menu_roast": "roast",
                }
                if cb_data in action_map:
                    try:
                        handle_menu_action(action_map[cb_data], cb_chat_id, cb_sender, state, end_time)
                    except Exception as e:
                        print(f"Gagal proses callback {cb_data}: {e}", file=sys.stderr, flush=True)
            continue

        message = upd.get("message") or upd.get("edited_message")
        if not message:
            continue

        web_app_data = message.get("web_app_data")
        if web_app_data:
            chat_id = message["chat"]["id"]
            message_id = message.get("message_id")
            from_user = message.get("from", {})
            sender_name = from_user.get("first_name") or from_user.get("username") or "Manusia"
            raw_payload = (web_app_data.get("data") or "").strip()
            try:
                ai_resp, _ = ask_groq(
                    raw_payload or "kirim data dari mini app",
                    sender_name,
                    state["chat_model"],
                    extra_instruction="Gurui user dengan sarkas dan lucu soal data dari Mini App. Maksimal 26 kata.",
                    max_words=26,
                    max_tokens=256,
                    force_angry=False,
                )
            except Exception:
                ai_resp = "Data dari Mini App udah masuk; sekarang pakai logika, jangan asal klik."
            send_telegram_message(
                chat_id,
                format_styled_reply("MINI APP DATA", ai_resp),
                reply_to_message_id=message_id,
                parse_mode="HTML",
                reply_markup=get_main_reply_keyboard(),
            )
            continue

        text = message.get("text") or message.get("caption") or ""
        photos = message.get("photo") or []
        has_photo = len(photos) > 0

        if not text.strip() and not has_photo:
            continue

        chat_id = message["chat"]["id"]
        message_id = message.get("message_id")
        from_user = message.get("from", {})
        user_id = from_user.get("id")
        sender_name = from_user.get("first_name") or from_user.get("username") or "Manusia"

        if not has_photo and text.strip().startswith("/forex"):
            send_forex_mini_app(chat_id, sender_name, state, reply_to_message_id=message_id)
            continue

        if not has_photo and text.strip().startswith("/status"):
            send_bot_status(chat_id, sender_name, end_time, reply_to_message_id=message_id)
            continue

        if not has_photo and (text.strip().startswith("/start") or text.strip().startswith("/menu")):
            welcome_text = build_welcome_message(sender_name, state)
            profile_photo = fetch_user_profile_photo_bytes(user_id)

            styled_welcome = (
                f"<b>⚡ AI BOT READY</b>\n"
                f"<blockquote>{html.escape(welcome_text)}</blockquote>\n"
                f"<i>Klik Mulai Bot atau pilih menu di bawah.</i>"
            )

            sent_combined_photo = False
            if profile_photo:
                photo_bytes, filename = profile_photo
                try:
                    send_telegram_photo_bytes(
                        chat_id,
                        photo_bytes,
                        filename=filename,
                        caption=styled_welcome,
                        reply_to_message_id=message_id,
                        parse_mode="HTML",
                        reply_markup=get_start_inline_keyboard(),
                    )
                    sent_combined_photo = True
                except Exception as e:
                    print(f"Info: gagal kirim foto profil menyatu dengan AI BOT READY (fallback teks): {e}", file=sys.stderr, flush=True)

            if not sent_combined_photo:
                try:
                    send_telegram_message(
                        chat_id,
                        styled_welcome,
                        reply_to_message_id=message_id,
                        parse_mode="HTML",
                        reply_markup=get_start_inline_keyboard(),
                    )
                except Exception as e:
                    print(f"Gagal kirim pesan selamat datang ke {sender_name}: {e}", file=sys.stderr, flush=True)

            print(f"Menyambut {sender_name} (/start) menyatu={'ya' if sent_combined_photo else 'tidak'}.", flush=True)
            continue

        if not has_photo and text.strip() in (BTN_START_APP, BTN_FOREX, BTN_RDP, BTN_GUIDE, BTN_ROAST, BTN_STATUS):
            try:
                quick_map = {
                    BTN_START_APP: "forex",
                    BTN_FOREX: "forex",
                    BTN_RDP: "rdp",
                    BTN_GUIDE: "guide",
                    BTN_ROAST: "roast",
                    BTN_STATUS: "status",
                }
                handle_menu_action(quick_map[text.strip()], chat_id, sender_name, state, end_time, reply_to_message_id=message_id)
            except Exception as e:
                print(f"Gagal proses tombol menu {text.strip()}: {e}", file=sys.stderr, flush=True)
            continue

        if not has_photo and text.strip() and is_rdp_request(text):
            send_rdp_package(chat_id, sender_name, text, state, reply_to_message_id=message_id)
            continue

        image_b64 = None
        mime_type = "image/jpeg"
        if has_photo:
            best_photo = photos[-1]
            try:
                image_b64, mime_type = download_telegram_photo_base64(best_photo["file_id"])
            except Exception as e:
                print(f"Gagal mengunduh foto update {update_id}: {e}", file=sys.stderr, flush=True)
                send_telegram_message(
                    chat_id,
                    format_styled_reply("ERROR", "Fotonya nyangkut; cek koneksi lo dan kirim ulang."),
                    reply_to_message_id=message_id,
                    parse_mode="HTML",
                )
                continue

        if has_photo:
            model_to_use = state["vision_model"]
            if not model_to_use:
                send_telegram_message(
                    chat_id,
                    format_styled_reply("INFO", "Model vision lagi absen; kirim teks dulu, jangan maksa."),
                    reply_to_message_id=message_id,
                    parse_mode="HTML",
                )
                continue
            prompt_text = text.strip() or "Lihat foto ini lalu beri komentar sarkas menggurui dan lucu."
        else:
            model_to_use = state["chat_model"]
            prompt_text = text.strip()

        try:
            reply_text, was_angry = ask_groq(
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
                chat_id,
                format_styled_reply(badge, reply_text),
                reply_to_message_id=message_id,
                parse_mode="HTML",
                reply_markup=get_main_reply_keyboard(),
            )
            print(f"Membalas pesan dari {sender_name} (chat_id={chat_id}) pakai {model_to_use} [angry={was_angry}].", flush=True)
        except Exception as e:
            err_str = str(e)
            switched = False
            candidate_pool = state["vision_candidates"] if has_photo else state["chat_candidates"]

            if "model_terms_required" in err_str or "model_not_found" in err_str or "400" in err_str:
                for alt_model in candidate_pool:
                    if alt_model == model_to_use:
                        continue
                    try:
                        reply_text, was_angry = ask_groq(
                            prompt_text,
                            sender_name,
                            alt_model,
                            image_b64=image_b64,
                            mime_type=mime_type,
                            max_words=30,
                            max_tokens=512,
                        )
                        if has_photo:
                            state["vision_model"] = alt_model
                        else:
                            state["chat_model"] = alt_model
                        badge = ("ANGRY VISION" if was_angry else "VISION REPLY") if has_photo else ("ANGRY REPLY" if was_angry else "AI REPLY")
                        send_telegram_message(
                            chat_id,
                            format_styled_reply(badge, reply_text),
                            reply_to_message_id=message_id,
                            parse_mode="HTML",
                            reply_markup=get_main_reply_keyboard(),
                        )
                        print(f"Beralih ke model {alt_model} dan membalas {sender_name}.", flush=True)
                        switched = True
                        break
                    except Exception:
                        continue

            if not switched:
                print(f"Gagal memproses update {update_id}: {e}", file=sys.stderr, flush=True)
                try:
                    send_telegram_message(
                        chat_id,
                        format_styled_reply("FREEZE", "Otak gue nge-freeze bentar; sabar, ulangi lagi."),
                        reply_to_message_id=message_id,
                        parse_mode="HTML",
                    )
                except Exception:
                    pass

    if max_update_id is not None:
        new_offset = max_update_id + 1
        save_last_offset(new_offset)
        return new_offset

    return current_offset


def main() -> None:
    if not TELEGRAM_TOKEN or not GROQ_API_KEY:
        print("Error: TELEGRAM_TOKEN atau GROQ_API_KEY kosong.", file=sys.stderr)
        sys.exit(1)

    register_bot_description()
    register_chat_menu_button()
    register_bot_commands()

    models_info = resolve_groq_models()
    state = {
        "chat_model": models_info["chat_model"],
        "chat_candidates": models_info["chat_candidates"],
        "vision_model": models_info["vision_model"],
        "vision_candidates": models_info["vision_candidates"],
    }
    print(
        f"Model chat aktif: {state['chat_model']} | Model vision aktif: {state['vision_model'] or 'Tidak tersedia'}",
        flush=True,
    )

    start_time = time.monotonic()
    end_time = start_time + RUN_DURATION_SECONDS
    current_offset = load_last_offset()

    print("Bot aktif! Mode siaga berjalan...", flush=True)

    while time.monotonic() < end_time:
        try:
            current_offset = poll_once(current_offset, state, end_time)
        except Exception as e:
            print(f"Error saat polling: {e}", file=sys.stderr, flush=True)

        remaining = end_time - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(POLL_INTERVAL_SECONDS, remaining))

    print("Sesi selesai.", flush=True)


if __name__ == "__main__":
    main()
