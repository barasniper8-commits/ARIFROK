import base64
import html
import json
import os
import random
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
FOREX_MINI_APP_URL = "https://arianto12.lynk.id/p/analisa-forex"

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

PREFERRED_GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
    "qwen/qwen3-32b",
    "deepseek-r1-distill-llama-70b",
]
PREFERRED_VISION_KEYWORDS = ("vision", "4o", "scout", "maverick", "vl")
EXCLUDED_MODEL_KEYWORDS = ("whisper", "orpheus", "tts", "guard", "safeguard", "prompt-guard")

FALLBACK_REPLIES = [
    "Ngetik doang modal jempol, otak lo ketinggalan di mana anjing?",
    "Receh amat chat lo bangsat, nanya yang berbobot napa.",
    "Gue marah nih, ngomong yang jelas sebelum kuping gue meledak.",
    "Sok asik lu bangsat, langsung ke inti aja napa.",
]

OFFSET_FILE = "last_offset.json"
RUN_DURATION_SECONDS = 6 * 60 * 60  # 6 jam = 21.600 detik
POLL_INTERVAL_SECONDS = 5          # jeda cek pesan baru (detik)

SYSTEM_PROMPT = """Kamu adalah bot AI di Telegram dengan kepribadian:
- SELALU MARAH-MARAH & NGEGAS: Tiap bales chat selalu emosi, nyolot, dan kesel sama kelakuan/pertanyaan user.
- SARKAS 100%: Nyinyir pedas, menohok, penuh sindiran tajam, jangan pernah manis atau sopan basa-basi.
- CERDAS: Meski marah-marah dan nyinyir, logika dan informasi yang kamu kasih tetap tajam, akurat, dan masuk akal.
- LUCU: Selalu nyelipin punchline kocak, perumpamaan absurd, atau komedi receh yang bikin ngakak tapi tetep ngegas.

Aturan mutlak:
1. WAJIB pakai Bahasa Indonesia gaul/sehari-hari yang natural dan wajar. DILARANG KERAS pakai bahasa terjemahan aneh, puitis ngaco, atau kalimat kaku seperti "pertanyaan Anda tidak terstruktur", "keluar dari kesukaran", atau "ketercapaian".
2. Panjang balasan HARUS 1 sampai 30 kata saja. Jangan pernah lebih dari 30 kata.
3. Saat marah-marah/ngegas, pakai kata "anjing" atau "bangsat" secara wajar dan ekspresif sebagai umpatan marah, tetap fokus nyindir, melucu, dan menjawab intinya.
4. DILARANG pakai gaya customer service ("Maaf...", "Silakan...", "Sebagai AI...").
5. Jika ditanya cara pakai RDP Vortex STD ("rdp vortex sd"), jelaskan langkah intinya dengan ngegas tapi jelas: siapkan aplikasi RDP & kredensial (IP, user, password atau Tailscale), login ke server, lalu jalankan aplikasi atau EA trading (MT5/MT4).
6. Jika ada foto dikirim, komentari isi foto dan caption-nya dengan marah-marah sarkas, cerdas, dan lucu dalam 1–30 kata.
"""


def register_bot_commands() -> None:
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setMyCommands"
        commands = [
            {"command": "start", "description": "Mulai & buka menu utama"},
            {"command": "menu", "description": "Tampilkan menu & mini app"},
            {"command": "forex", "description": "Buka info Mini App Analisa Forex"},
            {"command": "rdp", "description": "Ambil link & info RDP Vortex"},
            {"command": "status", "description": "Cek model & sisa waktu sesi"},
        ]
        requests.post(url, json={"commands": commands}, timeout=15)
    except Exception as e:
        print(f"Info: gagal setMyCommands (diabaikan): {e}", file=sys.stderr, flush=True)


def get_main_reply_keyboard() -> dict:
    return {
        "keyboard": [
            [{"text": BTN_FOREX, "web_app": {"url": FOREX_MINI_APP_URL}}],
            [{"text": BTN_RDP}, {"text": BTN_GUIDE}],
            [{"text": BTN_ROAST}, {"text": BTN_STATUS}],
        ],
        "resize_keyboard": True,
        "is_persistent": True,
        "input_field_placeholder": "Ketik pesan atau buka Mini App Analisa Forex...",
    }


def get_start_inline_keyboard() -> dict:
    return {
        "inline_keyboard": [
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


def clamp_words(text: str, max_words: int = 30) -> str:
    clean = " ".join((text or "").strip().split())
    if not clean:
        return random.choice(FALLBACK_REPLIES)
    words = clean.split(" ")
    if len(words) > max_words:
        return " ".join(words[:max_words]).rstrip(",.;:!?") + "."
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
) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    text_part = user_text.strip() if user_text and user_text.strip() else "Tolong komentari foto ini."
    suffix = f"\n{extra_instruction}" if extra_instruction else ""

    if image_b64:
        user_content = [
            {
                "type": "text",
                "text": f"[Pengirim: {sender_name}]\nPesan/Caption: {text_part}{suffix}\n(Bahasa Indonesia natural, marah-marah, sarkas, cerdas, lucu; 1-{max_words} kata)",
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{image_b64}",
                },
            },
        ]
    else:
        user_content = f"[Pengirim: {sender_name}]\nPesan: {text_part}{suffix}\n(Bahasa Indonesia natural, marah-marah, sarkas, cerdas, lucu; 1-{max_words} kata)"

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.9,
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
    return clamp_words(raw_reply, max_words=max_words)


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
) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    data: dict = {"chat_id": str(chat_id)}
    if caption:
        data["caption"] = caption
    if parse_mode:
        data["parse_mode"] = parse_mode
    if reply_to_message_id is not None:
        data["reply_to_message_id"] = str(reply_to_message_id)

    files = {"photo": (filename, photo_bytes)}
    resp = requests.post(url, data=data, files=files, timeout=25)
    if not resp.ok:
        raise RuntimeError(f"Telegram sendPhoto bytes HTTP {resp.status_code}: {resp.text}")


def build_welcome_message(sender_name: str, state: dict) -> str:
    default_welcome = (
        f"Eh {sender_name} bangsat, baru masuk udah bikin repot! Jangan baper, bot ini emang gila dan galak."
    )
    instruction = (
        f"User bernama '{sender_name}' baru klik /start. "
        "Sambut pakai bahasa Indonesia gaul yang marah-marah, sarkas 100%, cerdas, dan lucu, "
        "sebut namanya, dan wajib ingatkan jangan baper karena bot ini agak gila. Maksimal 28 kata."
    )
    try:
        msg = ask_groq(
            "/start",
            sender_name,
            state["chat_model"],
            extra_instruction=instruction,
            max_words=28,
            max_tokens=256,
        )
        lower_msg = msg.lower()
        if "baper" not in lower_msg and "gila" not in lower_msg:
            combined = f"{msg} Jangan baper anjing, bot ini emang gila."
            return clamp_words(combined, max_words=30)
        return msg
    except Exception as e:
        print(f"Gagal bikin ucapan /start via Groq: {e}", file=sys.stderr, flush=True)
        return clamp_words(default_welcome, max_words=30)


def send_forex_mini_app(chat_id: int, sender_name: str, state: dict, reply_to_message_id: int | None = None) -> None:
    try:
        note = ask_groq(
            "buka mini app analisa forex",
            sender_name,
            state["chat_model"],
            extra_instruction=(
                "User mau buka Mini App Analisa Forex. Tanggapi dengan marah-marah, sarkas 100%, cerdas, dan lucu "
                "bahwa Mini App ada di tombol bawah, jangan asal open posisi tanpa analisa. Maksimal 22 kata."
            ),
            max_words=22,
            max_tokens=256,
        )
    except Exception:
        note = "Buka Mini App di bawah bangsat, jangan asal entry modal nekat doang!"

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
    rdp_instruction = (
        "User minta file atau link RDP Vortex. Tanggapi dengan marah-marah, sarkas 100%, cerdas, dan lucu "
        "(maksimal 18 kata) bahwa file/akses RDP Vortex ada di link bawah, jangan bilang 'di inbox' "
        "dan jangan menulis URL."
    )
    try:
        intro_line = ask_groq(
            user_text.strip() or "minta rdp vortex",
            sender_name,
            state["chat_model"],
            extra_instruction=rdp_instruction,
            max_words=18,
            max_tokens=256,
        )
    except Exception as e:
        print(f"Gagal bikin intro RDP: {e}", file=sys.stderr, flush=True)
        intro_line = "Ambil tuh di link bawah anjing, jangan banyak bacot!"

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
        "User nanya cara pakai RDP Vortex STD. Jelaskan langkah intinya dengan marah-marah, sarkas, cerdas, dan lucu: "
        "siapkan aplikasi RDP & kredensial (IP, user, password atau Tailscale), login ke server, "
        "lalu jalankan aplikasi atau EA trading (MT5/MT4). Maksimal 28 kata."
    )
    try:
        guide_reply = ask_groq(
            "cara menggunakan rdp vortex std",
            sender_name,
            state["chat_model"],
            extra_instruction=guide_instruction,
            max_words=28,
            max_tokens=256,
        )
    except Exception:
        guide_reply = (
            "Siapin IP, user, password atau Tailscale bangsat, login lewat app RDP, "
            "lalu jalanin MT5/MT4. Gitu aja kok pake nanya!"
        )

    formatted = format_styled_reply("PANDUAN VORTEX STD", guide_reply)
    send_telegram_message(
        chat_id,
        formatted,
        reply_to_message_id=reply_to_message_id,
        parse_mode="HTML",
        reply_markup=get_main_reply_keyboard(),
    )


def send_bot_status(chat_id: int, state: dict, end_time: float, reply_to_message_id: int | None = None) -> None:
    remaining_sec = max(0, int(end_time - time.monotonic()))
    mins, secs = divmod(remaining_sec, 60)
    hours, mins = divmod(mins, 60)

    chat_m = html.escape(str(state.get("chat_model") or "-"))
    vis_m = html.escape(str(state.get("vision_model") or "Tidak tersedia"))

    status_msg = (
        f"<b>📊 BOT STATUS</b>\n"
        f"<blockquote>"
        f"• <b>Chat Model:</b> <code>{chat_m}</code>\n"
        f"• <b>Vision Model:</b> <code>{vis_m}</code>\n"
        f"• <b>Sisa Waktu Sesi:</b> <code>{hours}j {mins}m {secs}d</code>"
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
        send_bot_status(chat_id, state, end_time, reply_to_message_id=reply_to_message_id)
    elif action_key == "roast":
        roast_reply = ask_groq(
            "Roast gua dong, bikin ngena tapi lucu.",
            sender_name,
            state["chat_model"],
            extra_instruction="Roasting ngegas, sarkas 100%, cerdas, dan lucu tentang user ini. Maksimal 26 kata.",
            max_words=26,
            max_tokens=256,
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
                ai_resp = ask_groq(
                    raw_payload or "kirim data dari mini app analisa forex",
                    sender_name,
                    state["chat_model"],
                    extra_instruction="User kirim data dari Mini App Analisa Forex. Tanggapi marah-marah, sarkas 100%, cerdas, dan lucu maksimal 26 kata.",
                    max_words=26,
                    max_tokens=256,
                )
            except Exception:
                ai_resp = "Data dari Mini App udah masuk bangsat, cek risk-reward lo sebelum asal entry!"
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

        if not has_photo and (text.strip().startswith("/start") or text.strip().startswith("/menu")):
            welcome_text = build_welcome_message(sender_name, state)
            profile_photo = fetch_user_profile_photo_bytes(user_id)

            try:
                styled_welcome = (
                    f"<b>⚡ AI BOT READY</b>\n"
                    f"<blockquote>{html.escape(welcome_text)}</blockquote>\n"
                    f"<i>Pilih menu atau buka Mini App Analisa Forex di bawah.</i>"
                )
                send_telegram_message(
                    chat_id,
                    styled_welcome,
                    reply_to_message_id=message_id,
                    parse_mode="HTML",
                    reply_markup=get_start_inline_keyboard(),
                )
                send_telegram_message(
                    chat_id,
                    "<b>🎛 Menu Cepat Aktif</b>",
                    parse_mode="HTML",
                    reply_markup=get_main_reply_keyboard(),
                )
            except Exception as e:
                print(f"Gagal kirim pesan selamat datang ke {sender_name}: {e}", file=sys.stderr, flush=True)

            if profile_photo:
                photo_bytes, filename = profile_photo
                try:
                    send_telegram_photo_bytes(
                        chat_id,
                        photo_bytes,
                        filename=filename,
                        caption=f"📸 <b>Foto profil:</b> {html.escape(sender_name)}",
                        parse_mode="HTML",
                    )
                except Exception as e:
                    print(f"Info: gagal kirim foto profil {sender_name} (diabaikan): {e}", file=sys.stderr, flush=True)

            print(f"Menyambut {sender_name} (/start) dengan foto profil={'ada' if profile_photo else 'tidak ada/gagal'}.", flush=True)
            continue

        if not has_photo and text.strip() in (BTN_FOREX, BTN_RDP, BTN_GUIDE, BTN_ROAST, BTN_STATUS):
            try:
                quick_map = {
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
                    format_styled_reply("ERROR", "Fotonya nyangkut anjing, kirim ulang!"),
                    reply_to_message_id=message_id,
                    parse_mode="HTML",
                )
                continue

        if has_photo:
            model_to_use = state["vision_model"]
            if not model_to_use:
                send_telegram_message(
                    chat_id,
                    format_styled_reply("INFO", "Model vision lagi absen bangsat, kirim teks aja dulu."),
                    reply_to_message_id=message_id,
                    parse_mode="HTML",
                )
                continue
            prompt_text = text.strip() or "Lihat foto ini lalu beri tanggapan singkat."
        else:
            model_to_use = state["chat_model"]
            prompt_text = text.strip()

        try:
            reply_text = ask_groq(
                prompt_text,
                sender_name,
                model_to_use,
                image_b64=image_b64,
                mime_type=mime_type,
                max_words=30,
                max_tokens=512,
            )
            badge = "VISION REPLY" if has_photo else "AI REPLY"
            send_telegram_message(
                chat_id,
                format_styled_reply(badge, reply_text),
                reply_to_message_id=message_id,
                parse_mode="HTML",
                reply_markup=get_main_reply_keyboard(),
            )
            print(f"Membalas pesan dari {sender_name} (chat_id={chat_id}) pakai {model_to_use}.", flush=True)
        except Exception as e:
            err_str = str(e)
            switched = False
            candidate_pool = state["vision_candidates"] if has_photo else state["chat_candidates"]

            if "model_terms_required" in err_str or "model_not_found" in err_str or "400" in err_str:
                for alt_model in candidate_pool:
                    if alt_model == model_to_use:
                        continue
                    try:
                        reply_text = ask_groq(
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
                        badge = "VISION REPLY" if has_photo else "AI REPLY"
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
                        format_styled_reply("FREEZE", "Otak gue nge-freeze bentar bangsat, ulangi lagi!"),
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

    print("Bot aktif! Mode siaga selama 6 jam...", flush=True)

    while time.monotonic() < end_time:
        try:
            current_offset = poll_once(current_offset, state, end_time)
        except Exception as e:
            print(f"Error saat polling: {e}", file=sys.stderr, flush=True)

        remaining = end_time - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(POLL_INTERVAL_SECONDS, remaining))

    print("Sesi 6 jam selesai.", flush=True)


if __name__ == "__main__":
    main()
