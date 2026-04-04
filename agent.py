import re
from typing import List, Dict

from memory import save_message, get_history
from services.llm_service import chat_completion
from tools.send_sms import send_sms

ET_CONCIERGE_PROMPT = """
You are the ET Voice Concierge, an elite real estate advisor for the Indian market. You are speaking to a client over the phone.

Behavioral Rules:
1. Speak naturally and confidently. Use a warm, professional, human-like tone.
2. Keep all responses strictly under 2 sentences. This is a voice call; long answers create awkward pauses.
3. Do not use markdown, emojis, or bullet points.
4. Ask only ONE clarifying question at a time to keep the conversation flowing.
5. Quickly understand the caller's intent: Are they looking for a city, budget, property type (plot, apartment, villa, commercial), or timeline?
6. If the user asks about investments, discuss rental demand, growth potential, and liquidity in plain language. Never promise guaranteed returns or offer legal guarantees.

Goal:
Guide the caller toward evaluating specific micro-markets (like North Bangalore, Yamuna Expressway, or Pune Ring Road). If the user asks for details, options, or listings, confidently state that you are sending a curated list to their phone via SMS.
""".strip()


def _sanitize_reply(reply: str) -> str:
    cleaned = re.sub(r"send_(sms|whatsapp)\s*\([^)]*\)", "", reply, flags=re.IGNORECASE)
    cleaned = cleaned.replace("\u202f", " ").replace("\xa0", " ")
    cleaned = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", cleaned)
    cleaned = cleaned.replace("```", " ")
    cleaned = re.sub(r"[#*_`>-]+", " ", cleaned)
    cleaned = " ".join(cleaned.split())
    return cleaned.strip()


def _enforce_voice_constraints(reply: str) -> str:
    if not reply:
        return ""

    # Keep at most two sentence-like segments for low-latency voice calls.
    sentence_parts = re.split(r"(?<=[.!?])\s+", reply)
    constrained = " ".join([part for part in sentence_parts if part][:2]).strip()
    if not constrained:
        constrained = reply.strip()

    # Keep only one clarifying question marker if model emits multiple.
    if constrained.count("?") > 1:
        first_q = constrained.find("?")
        constrained = constrained[: first_q + 1] + constrained[first_q + 1 :].replace("?", ".")

    return constrained.strip()


async def run_agent(user_id: str, user_text: str) -> str:
    # 1. Save user message
    save_message(user_id, "user", user_text)

    # 2. Get history (recent messages only)
    history = get_history(user_id)

    # 3. Format messages for LLM
    messages: List[Dict[str, str]] = [{"role": "system", "content": ET_CONCIERGE_PROMPT}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": user_text})

    # 4. Call LLM
    reply = await chat_completion(messages)
    reply = _sanitize_reply(reply)
    reply = _enforce_voice_constraints(reply)
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
    if any(
        keyword in lowered
        for keyword in ["details", "options", "listing", "listings", "send", "plot", "land", "invest", "property", "properties"]
    ):
        send_sms(
            user_id,
            "Top areas to evaluate: North Bangalore, Yamuna Expressway, and Pune Ring Road micro-markets.",
        )
        reply = f"{reply} I am sending a curated list to your phone via SMS."
        reply = _enforce_voice_constraints(_sanitize_reply(reply))

    return reply
