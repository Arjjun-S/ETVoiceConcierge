import os
from supabase import create_client
from typing import List, Dict, Any

# Supabase client for conversation memory
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(supabase_url, supabase_service_key)  # type: ignore[arg-type]


def save_message(user_id: str, role: str, content: str) -> None:
    supabase.table("conversations").insert(
        {
            "user_id": user_id,
            "role": role,
            "content": content,
        }
    ).execute()


def get_history(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    res = (
        supabase.table("conversations")
        .select("role,content,created_at")
        .eq("user_id", user_id)
        .order("created_at")
        .limit(limit)
        .execute()
    )
    return res.data or []
