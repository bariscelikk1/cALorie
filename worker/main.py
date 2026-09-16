import json
import logging
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

from analysis.errors import AnalysisError
from analysis.models import Exercise
from analysis.pipeline import analyze_video
from db import get_job, mark_processing, update_job
from security import SignatureError, verify_qstash
from storage import download_video, validate_storage_key

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("calorie-worker")
app = FastAPI(title="cALorie worker", docs_url=None, redoc_url=None)


class ProcessRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    job_id: UUID
    video_key: str = Field(min_length=45, max_length=80)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/process", status_code=202)
async def process(
    request: Request,
    background_tasks: BackgroundTasks,
    upstash_signature: str | None = Header(default=None),
):
    raw_body = await request.body()
    try:
        verify_qstash(upstash_signature, raw_body)
        req = ProcessRequest.model_validate(json.loads(raw_body))
        validate_storage_key(req.video_key)
    except (SignatureError, ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=401, detail="Request verification failed") from exc

    job = get_job(str(req.job_id))
    if not job or job["video_key"] != req.video_key:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] == "done":
        return {"accepted": False, "reason": "already completed"}
    if not mark_processing(str(req.job_id)):
        return {"accepted": False, "reason": "already processing"}

    background_tasks.add_task(run_pipeline, str(req.job_id), req.video_key)
    return {"accepted": True}


def run_pipeline(job_id: str, video_key: str) -> None:
    try:
        job = get_job(job_id)
        exercise = Exercise(job["exercise"])
        with tempfile.TemporaryDirectory(prefix="calorie-") as directory:
            path = Path(directory) / f"input{Path(video_key).suffix}"
            download_video(video_key, path)
            result = analyze_video(path, exercise, float(job["weight_kg"]))
        update_job(
            job_id,
            status="done",
            result_json=result.to_dict(),
            error_message=None,
            completed_at=datetime.now(UTC).isoformat(),
        )
    except AnalysisError as exc:
        update_job(
            job_id,
            status="error",
            error_message=str(exc),
            completed_at=datetime.now(UTC).isoformat(),
        )
    except Exception:
        logger.exception("Unexpected pipeline failure for job %s", job_id)
        update_job(
            job_id,
            status="error",
            error_message="The video could not be analyzed. Please try another video.",
            completed_at=datetime.now(UTC).isoformat(),
        )
