from typing import Any


async def extract_profile(conversation: dict[str, Any]) -> dict[str, str]:
    user_text = conversation.get("user_text", "").lower()
    experience = "advanced" if "already" in user_text or "experience" in user_text else "beginner"
    goal = "investing" if "invest" in user_text else "general"
    risk = "low" if "safe" in user_text or "low" in user_text else "medium"

    return {
        "experience": experience,
        "goal": goal,
        "risk": risk,
    }
