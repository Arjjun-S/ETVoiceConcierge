import logging
import os
from typing import Any, Dict, List

import httpx


logger = logging.getLogger(__name__)

supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")
_rest_base = f"{supabase_url}/rest/v1" if supabase_url else None
_client = httpx.Client(timeout=10.0)


def _auth_headers() -> Dict[str, str]:
    return {
        "apikey": supabase_service_key or "",
        "Authorization": f"Bearer {supabase_service_key}" if supabase_service_key else "",
        "Content-Type": "application/json",
    }


def _is_configured() -> bool:
    if not supabase_url or not supabase_service_key:
        logger.error("Supabase env vars missing; set SUPABASE_URL and SUPABASE_SERVICE_KEY")
        return False
    return True


def save_message(user_id: str, role: str, content: str) -> None:
    if not _is_configured() or not _rest_base:
        return

    try:
        headers = _auth_headers()
        headers["Prefer"] = "return=minimal"
        resp = _client.post(
            f"{_rest_base}/conversations",
            headers=headers,
            json={"user_id": user_id, "role": role, "content": content},
        )
        resp.raise_for_status()
    except Exception as exc:
        logger.error("Failed to save conversation message: %s", exc)


def get_history(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    if not _is_configured() or not _rest_base:
        return []

    try:
        resp = _client.get(
            f"{_rest_base}/conversations",
            headers=_auth_headers(),
            params={
                "select": "role,content,created_at",
                "user_id": f"eq.{user_id}",
                "order": "created_at",
                "limit": limit,
            },
        )
        resp.raise_for_status()
        return resp.json() or []
    except Exception as exc:
        logger.error("Failed to fetch conversation history: %s", exc)
        return []
