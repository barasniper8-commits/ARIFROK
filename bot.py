import json
import os
import sys
import time
import requests

TELEGRAM_TOKEN = "9253138868:AAFXhdgueoLoR-Sx8cY3jsbwb2uZQXPyD6A"
GROQ_API_KEY = "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"
GROQ_MODEL = "llama-3.3-70b-versatile"

OFFSET_FILE = "last_offset.json"
RUN_DURATION_SECONDS = 6 * 60 * 60  # 6 jam = 21.600 detik
POLL_INTERVAL_SECONDS = 5          # jeda cek pesan baru (detik)

SYSTEM_PROMPT = """Kamu adalah asisten AI di Telegram dengan kepribadian:
- GALAK & SARKAS: Nyinyir tapi tetap kena, suka menyindir pertanyaan yang malas dipikir, namun tidak melewati batas kasar yang tidak perlu.
- CERDAS: Jawabanmu akurat, tajam, logis, dan berbobot—jangan ngawur meski sambil nyindir.
- LUCU: Selipkan punchline kering, analogi absurd, atau humor receh yang pas di momennya.

Aturan gaya bahasa:
1. Gunakan Bahasa Indonesia santai yang mengalir.
2. Jangan pernah bilang "Sebagai AI..." atau terdengar seperti customer service yang terlalu ramah.
3. Jawab inti masalahnya dengan benar, tapi bungkus dengan sarkasme dan humor cerdas.
4. Ringkas dan padat, jangan bertele-tele kecuali memang perlu penjelasan teknis.
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


def ask_groq(user_message: str, sender_name: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"[Pengirim: {sender_name}]\nPesan: {user_message}",
            },
        ],
        "temperature": 0.85,
        "max_tokens": 600,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=40)
    if not resp.ok:
        raise RuntimeError(f"Groq HTTP {resp.status_code}: {resp.text}")
    data = resp.json()
    return data["choices"][0]["message"]["content"].strip()


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


def poll_once(current_offset: int | None) -> int | None:
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

        text = message.get("text")
        if not text:
            continue

        chat_id = message["chat"]["id"]
        message_id = message.get("message_id")
        from_user = message.get("from", {})
        sender_name = from_user.get("first_name") or from_user.get("username") or "Manusia"

        prompt_text = (
            "User baru saja menekan /start. Sambut dia dengan gaya galak, sarkas, cerdas, dan lucu."
            if text.strip() == "/start"
            else text
        )

        try:
            reply_text = ask_groq(prompt_text, sender_name)
            send_telegram_message(chat_id, reply_text, reply_to_message_id=message_id)
            print(f"Membalas pesan dari {sender_name} (chat_id={chat_id}).", flush=True)
        except Exception as e:
            print(f"Gagal memproses update {update_id}: {e}", file=sys.stderr, flush=True)
            try:
                send_telegram_message(
                    chat_id,
                    "Tadi otak saya sempat nge-freeze gara-gara pertanyaanmu. Coba kirim ulang sebentar lagi!",
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

    start_time = time.monotonic()
    end_time = start_time + RUN_DURATION_SECONDS
    current_offset = load_last_offset()

    print("Bot aktif! Mode siaga selama 6 jam...", flush=True)

    while time.monotonic() < end_time:
        try:
            current_offset = poll_once(current_offset)
        except Exception as e:
            print(f"Error saat polling: {e}", file=sys.stderr, flush=True)

        remaining = end_time - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(POLL_INTERVAL_SECONDS, remaining))

    print("Sesi 6 jam selesai.", flush=True)


if __name__ == "__main__":
    main()
