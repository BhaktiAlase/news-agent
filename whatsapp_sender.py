"""
Sends messages via WhatsApp using Twilio API.
Handles message splitting for long content (WhatsApp 1600-char limit).
"""

from typing import List
from twilio.rest import Client
from config import TWILIO_SID, TWILIO_AUTH, TWILIO_FROM, MY_NUMBER

client = Client(TWILIO_SID, TWILIO_AUTH)

WHATSAPP_CHAR_LIMIT = 1600


def _split_message(text: str, limit: int = WHATSAPP_CHAR_LIMIT) -> List[str]:
    """
    Split a long message into chunks that fit WhatsApp's character limit.
    Splits on newlines to avoid breaking mid-sentence.
    """
    if len(text) <= limit:
        return [text]

    chunks = []
    current_chunk = ""

    for line in text.split("\n"):
        # If adding this line would exceed the limit, save current chunk
        if len(current_chunk) + len(line) + 1 > limit:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def send_whatsapp(
    message_body: str,
    to_number: str = MY_NUMBER,
    from_number: str = TWILIO_FROM,
) -> List[str]:
    """
    Send a WhatsApp message. Automatically splits long messages.

    Args:
        message_body: The text to send.
        to_number:    Recipient in format 'whatsapp:+1234567890'.
        from_number:  Sender (Twilio number) in same format.

    Returns:
        List of Twilio message SIDs.
    """
    chunks = _split_message(message_body)
    sids = []

    for i, chunk in enumerate(chunks, 1):
        if len(chunks) > 1:
            chunk = f"({i}/{len(chunks)})\n\n{chunk}"

        message = client.messages.create(
            from_=from_number,
            to=to_number,
            body=chunk,
        )
        sids.append(message.sid)
        print(f"[✓] WhatsApp message {i}/{len(chunks)} sent. SID: {message.sid}")

    return sids


def send_whatsapp_to_multiple(
    message_body: str,
    numbers: List[str],
) -> dict:
    """
    Send the same message to multiple WhatsApp numbers.

    Args:
        message_body: The text to send.
        numbers:      List of numbers in 'whatsapp:+...' format.

    Returns:
        Dict mapping number → list of SIDs.
    """
    results = {}
    for number in numbers:
        try:
            sids = send_whatsapp(message_body, to_number=number)
            results[number] = {"status": "sent", "sids": sids}
        except Exception as e:
            print(f"[✗] Failed to send to {number}: {e}")
            results[number] = {"status": "failed", "error": str(e)}
    return results


# ─── Quick test ──────────────────────────────────────────────
if __name__ == "__main__":
    send_whatsapp("🧪 Test message from AI News Agent!")