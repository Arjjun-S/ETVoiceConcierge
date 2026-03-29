from agent import run_agent_pipeline as run_concierge_pipeline


async def run_agent_pipeline(user_text: str, call_sid: str | None = None) -> str:
    user_id = call_sid or "test_user"
    return await run_concierge_pipeline(user_id=user_id, text=user_text)
