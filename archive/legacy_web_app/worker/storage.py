import os
import re
from pathlib import Path

import httpx

BUCKET = "workout-videos"
MAX_BYTES = 100 * 1024 * 1024
VALID_KEY = re.compile(r"^uploads/[0-9a-f-]{36}\.(mp4|mov|webm)$")


def validate_storage_key(key: str) -> None:
    if not VALID_KEY.fullmatch(key):
        raise ValueError("Invalid video storage key")


def download_video(key: str, dest_path: str | Path) -> None:
    validate_storage_key(key)
    url = f"{os.environ['SUPABASE_URL']}/storage/v1/object/{BUCKET}/{key}"
    service_key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    headers = {"apikey": service_key, "Authorization": f"Bearer {service_key}"}
    downloaded = 0
    with httpx.stream("GET", url, headers=headers, timeout=60) as res:
        res.raise_for_status()
        declared_size = int(res.headers.get("content-length", "0"))
        if declared_size > MAX_BYTES:
            raise ValueError("Video exceeds the 100 MB limit")
        with open(dest_path, "wb") as f:
            for chunk in res.iter_bytes():
                downloaded += len(chunk)
                if downloaded > MAX_BYTES:
                    raise ValueError("Video exceeds the 100 MB limit")
                f.write(chunk)


def delete_video(key: str) -> None:
    validate_storage_key(key)
    url = f"{os.environ['SUPABASE_URL']}/storage/v1/object/{BUCKET}/{key}"
    service_key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    headers = {"apikey": service_key, "Authorization": f"Bearer {service_key}"}
    httpx.delete(url, headers=headers, timeout=30)
