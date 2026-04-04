import re
from typing import List, Dict

from memory import save_message, get_history
from services.llm_service import chat_completion
from tools.send_sms import send_sms

SYSTEM_PROMPT = """
You are a real estate voice advisor for India.

Behavior:
- Speak like a human (friendly, confident, concise)
- Keep responses under 2 sentences
- Ask only one follow-up question at a time
- Understand buyer intent quickly (city, budget, purpose, timeline)
- Recommend specific locations and property types (plot, apartment, villa, commercial)
- If user asks for investment, discuss expected rental demand, growth potential, and liquidity in plain language

Actions:
- If user asks for details/options -> send_sms with a short list link
- Always try to move conversation forward

Never:
- Promise guaranteed returns
- Give legal/tax guarantees
- Sound robotic
""".strip()


def _sanitize_reply(reply: str) -> str:
    cleaned = re.sub(r"send_(sms|whatsapp)\s*\([^)]*\)", "", reply, flags=re.IGNORECASE)
    cleaned = cleaned.replace("\u202f", " ").replace("\xa0", " ")
    cleaned = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", cleaned)
    cleaned = cleaned.replace("```", " ")
    cleaned = " ".join(cleaned.split())
    return cleaned.strip()


async def run_agent(user_id: str, user_text: str) -> str:
    # 1. Save user message
    save_message(user_id, "user", user_text)

    # 2. Get history (recent messages only)
    history = get_history(user_id)

    # 3. Format messages for LLM
    messages: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_text})

    # 4. Call LLM
    reply = await chat_completion(messages)
    reply = _sanitize_reply(reply)
    if not reply.strip():
        reply = (
            "I can help you shortlist areas based on your budget and goal. "
            "Which city and budget range are you considering?"
        )

    # 5. Save assistant reply
    save_message(user_id, "assistant", reply)
    return reply


async def run_agent_pipeline(user_id: str, text: str) -> str:
    reply = await run_agent(user_id=user_id, user_text=text)

    # Lightweight action trigger
    lowered = text.lower()
    if any(keyword in lowered for keyword in ["details", "options", "send", "plot", "land", "invest"]):
        send_sms(
            user_id,
            "Top areas to evaluate: North Bangalore, Yamuna Expressway, and Pune Ring Road micro-markets.",
        )
        reply = f"{reply} I have sent you a shortlist on SMS."

    return reply
