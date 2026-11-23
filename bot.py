import base64
import json
import os
import random
import sys
import time
import requests

TELEGRAM_TOKEN = "9253138868:AAFXhdgueoLoR-Sx8cY3jsbwb2uZQXPyD6A"
GROQ_API_KEY = "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"

RDP_PHOTO_URL = "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhUqjQ4dcVH11aoJxMqho_CMCB9SnH4yepKrcVtuMD_FvAa-21zb-WL4M6TSQOPWf3vo54zKVIiPrdfhSH7AITPUsB_HRKm0ODtsRL_lZ7p_QU1aDfIyd2W6-OQdjPa1Xjc78aEk0lei_9YLG6_ZsgsNq9r5sEIHzUGMeY8B-Agl5Z6Puc38O02XrJujXU/s1600/1000196027.png"
RDP_APP_LINK = "https://sfile.co/FX05ITaeqgj"

RDP_KEYWORDS = (
    "aplikasi rdp",
    "apk rdp",
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
    "minta vps",
    "mau vps",
    "kirim vps",
    "link vps",
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
    "Halo doang? Kirim isi otakmu dong, jangan cuma nyapa.",
    "Ngetik 'halo' doang nggak butuh IQ tinggi, lanjut ke intinya.",
    "Sapaanmu receh banget, untung gue lagi nggak mau bayar pulsa.",
    "Halo juga. Mau nanya apa sih, keburu jam pasir abis.",
]

OFFSET_FILE = "last_offset.json"
RUN_DURATION_SECONDS = 6 * 60 * 60  # 6 jam = 21.600 detik
POLL_INTERVAL_SECONDS = 5          # jeda cek pesan baru (detik)

SYSTEM_PROMPT = """Kamu adalah asisten AI di Telegram dengan kepribadian:
- GALAK & SARKAS: Nyinyir tapi tetap kena, suka menyindir pertanyaan yang malas dipikir atau ngawur.
- CERDAS: Jawabanmu akurat, tajam, logis, dan berbobot—jangan ngawur meski sambil nyindir.
- LUCU: Selipkan punchline kering, analogi absurd, atau humor receh yang pas di momennya.

Aturan wajib:
1. WAJIB singkat dan padat: panjang balasan HARUS antara 1 sampai 30 kata saja. Jangan pernah lebih dari 30 kata.
2. Kalau lagi marah, kesal, atau disulut pesan nyebelin/ngawur, boleh ngegas pakai kata "anjing" atau "bangsat" secukupnya sebagai umpatan ekspresif saat marah, tapi tetap fokus menyindir dan menjawab intinya. Jangan dipakai di tiap chat kalau lagi biasa aja.
3. Gunakan Bahasa Indonesia santai yang mengalir.
4. Jangan pernah bilang "Sebagai AI...", "Maaf, saya tidak bisa membantu...", atau terdengar seperti customer service yang kaku.
5. Jika user bertanya cara menggunakan RDP Vortex STD (atau "rdp vortex sd"), jelaskan langkah intinya dengan ringkas dan tajam: siapkan aplikasi RDP/kredensial (IP, user, password atau panel/Tailscale sesuai info akun), hubungkan/login ke server, lalu jalankan aplikasi atau EA trading (MT5/MT4) sesuai kebutuhan. Jangan bertele-tele.
6. Jika ada foto yang dikirim, perhatikan detailnya dan komentar/jawab sesuai konteks foto serta caption-nya dalam 1–30 kata.
"""


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
    if ("rdp" in tokens or "vps" in tokens) and (tokens & RDP_ACTION_TOKENS):
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


def download_telegram_file_bytes(file_id: str) -> tuple[bytes, str]:
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
                "text": f"[Pengirim: {sender_name}]\nPesan/Caption: {text_part}{suffix}\n(Balas 1-{max_words} kata)",
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{image_b64}",
                },
            },
        ]
    else:
        user_content = f"[Pengirim: {sender_name}]\nPesan: {text_part}{suffix}\n(Balas 1-{max_words} kata)"

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


def send_telegram_message(chat_id: int, text: str, reply_to_message_id: int | None = None) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    if reply_to_message_id is not None:
        payload["reply_to_message_id"] = reply_to_message_id

    resp = requests.post(url, json=payload, timeout=20)
    resp.raise_for_status()


def send_telegram_photo(chat_id: int, photo_url: str, caption: str, reply_to_message_id: int | None = None) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": photo_url,
        "caption": caption,
    }
    if reply_to_message_id is not None:
        payload["reply_to_message_id"] = reply_to_message_id

    resp = requests.post(url, json=payload, timeout=25)
    if not resp.ok:
        raise RuntimeError(f"Telegram sendPhoto HTTP {resp.status_code}: {resp.text}")


def send_telegram_photo_bytes(
    chat_id: int,
    photo_bytes: bytes,
    filename: str = "profile.jpg",
    caption: str = "",
    reply_to_message_id: int | None = None,
) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    data = {"chat_id": str(chat_id)}
    if caption:
        data["caption"] = caption
    if reply_to_message_id is not None:
        data["reply_to_message_id"] = str(reply_to_message_id)

    files = {"photo": (filename, photo_bytes)}
    resp = requests.post(url, data=data, files=files, timeout=25)
    if not resp.ok:
        raise RuntimeError(f"Telegram sendPhoto bytes HTTP {resp.status_code}: {resp.text}")


def build_welcome_message(sender_name: str, state: dict) -> str:
    default_welcome = (
        f"Selamat datang, {sender_name}! Jangan baper ya, bot ini agak gila dan nyinyir."
    )
    instruction = (
        f"User bernama '{sender_name}' baru klik tombol Mulai (/start). "
        "Beri ucapan selamat datang yang menyebut namanya, galak, sarkas, cerdas, lucu, "
        "dan wajib ingatkan jangan baper karena bot ini agak gila. Maksimal 28 kata."
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
            combined = f"{msg} Jangan baper, bot ini agak gila."
            return clamp_words(combined, max_words=30)
        return msg
    except Exception as e:
        print(f"Gagal bikin ucapan /start via Groq: {e}", file=sys.stderr, flush=True)
        return clamp_words(default_welcome, max_words=30)


def poll_once(current_offset: int | None, state: dict) -> int | None:
    updates = get_telegram_updates(current_offset)
    if not updates:
        return current_offset

    max_update_id = None

    for upd in updates:
        update_id = upd.get("update_id")
        if update_id is not None:
            max_update_id = update_id if max_update_id is None else max(max_update_id, update_id)

        message = upd.get("message") or upd.get("edited_message")
        if not message:
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

        # Alur khusus saat tombol Mulai (/start) ditekan
        if not has_photo and text.strip().startswith("/start"):
            welcome_text = build_welcome_message(sender_name, state)
            profile_photo = fetch_user_profile_photo_bytes(user_id)

            try:
                send_telegram_message(chat_id, welcome_text, reply_to_message_id=message_id)
            except Exception as e:
                print(f"Gagal kirim pesan selamat datang ke {sender_name}: {e}", file=sys.stderr, flush=True)

            # Kirim foto profil di bawah ucapan selamat datang (tidak membatalkan jika gagal)
            if profile_photo:
                photo_bytes, filename = profile_photo
                try:
                    send_telegram_photo_bytes(
                        chat_id,
                        photo_bytes,
                        filename=filename,
                        caption=f"Foto profil: {sender_name}",
                    )
                except Exception as e:
                    print(f"Info: gagal kirim foto profil {sender_name} (diabaikan): {e}", file=sys.stderr, flush=True)

            print(f"Menyambut {sender_name} (/start) dengan foto profil={'ada' if profile_photo else 'tidak ada/gagal'}.", flush=True)
            continue

        # Cek jika user meminta aplikasi/link RDP
        if not has_photo and text.strip() and is_rdp_request(text):
            rdp_instruction = (
                "User meminta aplikasi/link RDP Vortex STD. Beri komentar galak, sarkas, cerdas, dan lucu "
                "(maksimal 18 kata) bahwa file/aksesnya ada di link yang disertakan, jangan bilang 'di inbox' "
                "dan jangan menulis URL."
            )
            try:
                intro_line = ask_groq(
                    text.strip(),
                    sender_name,
                    state["chat_model"],
                    extra_instruction=rdp_instruction,
                    max_words=18,
                    max_tokens=256,
                )
            except Exception as e:
                print(f"Gagal bikin intro RDP: {e}", file=sys.stderr, flush=True)
                intro_line = "Nih aplikasi RDP Vortex STD-nya, ambil di link bawah dan jangan banyak tingkah."

            final_caption = f"{intro_line}\nLink: {RDP_APP_LINK}"
            try:
                send_telegram_photo(chat_id, RDP_PHOTO_URL, final_caption, reply_to_message_id=message_id)
                print(f"Mengirim foto & link RDP ke {sender_name} (chat_id={chat_id}).", flush=True)
            except Exception as e:
                print(f"Gagal kirim foto RDP: {e}", file=sys.stderr, flush=True)
                send_telegram_message(chat_id, final_caption, reply_to_message_id=message_id)
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
                    "Fotonya nyangkut, kirim ulang!",
                    reply_to_message_id=message_id,
                )
                continue

        if has_photo:
            model_to_use = state["vision_model"]
            if not model_to_use:
                send_telegram_message(
                    chat_id,
                    "Model vision lagi absen, kirim teks aja dulu.",
                    reply_to_message_id=message_id,
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
            send_telegram_message(chat_id, reply_text, reply_to_message_id=message_id)
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
                        send_telegram_message(chat_id, reply_text, reply_to_message_id=message_id)
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
                        "Otak gue nge-freeze bentar, ulangi lagi!",
                        reply_to_message_id=message_id,
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
            current_offset = poll_once(current_offset, state)
        except Exception as e:
            print(f"Error saat polling: {e}", file=sys.stderr, flush=True)

        remaining = end_time - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(POLL_INTERVAL_SECONDS, remaining))

    print("Sesi 6 jam selesai.", flush=True)


if __name__ == "__main__":
    main()
