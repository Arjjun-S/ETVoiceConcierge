from typing import List, Dict

from memory import save_message, get_history
from services.llm_service import chat_completion
from tools.send_sms import send_sms

SYSTEM_PROMPT = """
You are an AI financial concierge for Economic Times.

Behavior:
- Speak like a human (friendly, confident)
- Keep responses under 2 sentences
- Ask only one question at a time
- Understand user quickly (within 2–3 turns)
- Recommend relevant ET services

Actions:
- If user wants info → send_sms
- If user is beginner → guide them step-by-step
- Always try to move conversation forward

Never:
- Give long explanations
- Sound robotic
""".strip()


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

    # 5. Save assistant reply
    save_message(user_id, "assistant", reply)
    return reply


async def run_agent_pipeline(user_id: str, text: str) -> str:
    reply = await run_agent(user_id=user_id, user_text=text)

    # Lightweight action trigger
    lowered = text.lower()
    if "guide" in lowered or "start" in lowered:
        send_sms(user_id, "Start investing here: https://etmarkets.com/start")
        reply = f"{reply} I’ve sent you a guide on SMS."

    return reply
