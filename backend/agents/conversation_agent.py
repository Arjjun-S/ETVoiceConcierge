DEFAULT_TONE = "short, friendly, human concierge"


async def converse(user_text: str) -> dict:
    return {
        "user_text": user_text,
        "tone": DEFAULT_TONE,
        "follow_up": "What brings you to ET today?",
    }
