import os
from datetime import UTC, datetime

from supabase import Client, create_client

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
        _client = create_client(url, key)
    return _client


def get_job(job_id: str) -> dict:
    res = get_client().table("jobs").select("*").eq("id", job_id).single().execute()
    return res.data


def update_job(job_id: str, **fields) -> None:
    get_client().table("jobs").update(fields).eq("id", job_id).execute()


def mark_processing(job_id: str) -> bool:
    result = (
        get_client()
        .table("jobs")
        .update({"status": "processing", "started_at": datetime.now(UTC).isoformat()})
        .eq("id", job_id)
        .eq("status", "queued")
        .execute()
    )
    return bool(result.data)
