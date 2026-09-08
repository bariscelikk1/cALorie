import os

import httpx

BUCKET = "workout-videos"


def download_video(key: str, dest_path: str) -> None:
    url = f"{os.environ['SUPABASE_URL']}/storage/v1/object/{BUCKET}/{key}"
    headers = {"apikey": os.environ["SUPABASE_SERVICE_ROLE_KEY"]}
    with httpx.stream("GET", url, headers=headers, timeout=60) as res:
        res.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in res.iter_bytes():
                f.write(chunk)


def delete_video(key: str) -> None:
    url = f"{os.environ['SUPABASE_URL']}/storage/v1/object/{BUCKET}/{key}"
    headers = {"apikey": os.environ["SUPABASE_SERVICE_ROLE_KEY"]}
    httpx.delete(url, headers=headers, timeout=30)
