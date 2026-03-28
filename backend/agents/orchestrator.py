from agents import conversation_agent, profiling_agent, recommendation_agent, action_agent, memory_agent


async def run_agent_pipeline(user_text: str, call_sid: str | None = None) -> str:
    conversation = await conversation_agent.converse(user_text)
    profile = await profiling_agent.extract_profile(conversation)
    recommendations = await recommendation_agent.recommend(profile)
    action_result = await action_agent.execute(recommendations, profile)
    await memory_agent.persist(call_sid=call_sid, profile=profile, conversation=conversation)
    return action_result
