import random
import time

from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

from db import update_job

app = FastAPI()


class ProcessRequest(BaseModel):
    job_id: str
    video_key: str
    weight_kg: float


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/process")
def process(req: ProcessRequest, background_tasks: BackgroundTasks):
    # Return immediately so QStash doesn't time out waiting for the (slow) pipeline.
    update_job(req.job_id, status="processing")
    background_tasks.add_task(run_pipeline_stub, req.job_id, req.weight_kg)
    return {"accepted": True}


def run_pipeline_stub(job_id: str, weight_kg: float) -> None:
    """
    Phase 0 stub: no real video processing yet. Just proves the
    upload -> job row -> queue -> worker -> status update -> polling
    pipeline actually works end to end. Replaced in Phase 2/3 with
    real pose estimation + calorie estimation.
    """
    time.sleep(5)
    low = round(weight_kg * 4.5)
    high = round(weight_kg * 6.5)
    update_job(
        job_id,
        status="done",
        result_json={
            "calories_low": low,
            "calories_high": high,
            "confidence": random.choice(["low", "medium", "high"]),
            "note": "stub result — real pose/calorie pipeline not implemented yet",
        },
    )
