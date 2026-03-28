import logging

logger = logging.getLogger(__name__)


async def persist(call_sid: str | None, profile: dict, conversation: dict) -> None:
    logger.info("Persisting session", extra={"call_sid": call_sid, "profile": profile, "conversation": conversation})
