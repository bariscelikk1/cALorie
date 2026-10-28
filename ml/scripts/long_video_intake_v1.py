#!/usr/bin/env python3
"""Long-video test v1 intake: download, normalize, extract pose and stills, delete raw video.

Per video (PLAN.md sections 1 and 3):
- yt-dlp fetches a <=360p video-only stream; its SHA-256, size, and format are recorded.
- ffmpeg normalizes it to H.264, 15 FPS, 360p, no audio (one sequential decode path).
- One sequential pass extracts MediaPipe pose for every frame (15 FPS) plus stills:
  overview frames every 2 s (320 px wide) and dense frames every 0.5 s (192 px wide).
- Raw and normalized video files are deleted before the per-video ZIP is written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import time
import urllib.request
import zipfile
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd

TARGET_FPS = 15
OVERVIEW_EVERY, DENSE_EVERY = 30, 7.5  # frames at 15 FPS: every 2 s, every 0.5 s
OVERVIEW_W, DENSE_W = 320, 192
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"
KEEP_17 = [0, 2, 5, 7, 8, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_HIP, RIGHT_HIP = 5, 6, 11, 12


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_pose(frame: np.ndarray) -> np.ndarray:
    xyz = frame[:, :3].copy()
    hip = (xyz[LEFT_HIP] + xyz[RIGHT_HIP]) / 2
    shoulder = (xyz[LEFT_SHOULDER] + xyz[RIGHT_SHOULDER]) / 2
    scale = max(float(np.linalg.norm(xyz[LEFT_SHOULDER] - xyz[RIGHT_SHOULDER])), float(np.linalg.norm(shoulder - hip)), 1e-6)
    return np.concatenate([(xyz - hip) / scale, frame[:, 3:4]], axis=1)


def fill_missing(sequence: np.ndarray) -> np.ndarray:
    flat = sequence.reshape(len(sequence), -1)
    return pd.DataFrame(flat).interpolate(limit_direction="both").fillna(0).to_numpy().reshape(sequence.shape).astype(np.float32)


def resize_width(frame: np.ndarray, width: int) -> np.ndarray:
    return cv2.resize(frame, (width, max(1, round(frame.shape[0] * width / frame.shape[1]))), interpolation=cv2.INTER_AREA)


def process(video_id: str, work: Path, out_dir: Path, ytdlp: str, model: Path, prefix: str = "long_video_test_v1") -> dict:
    vdir = work / video_id
    if vdir.exists():
        shutil.rmtree(vdir)
    (vdir / "overview").mkdir(parents=True)
    (vdir / "dense").mkdir()
    record = {"video_id": video_id, "status": "ok", "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    raw = normalized = None
    try:
        subprocess.run([ytdlp, "--no-warnings", "--no-playlist", "-f", "bv*[height<=360][ext=mp4]/bv*[height<=360]/b[height<=360]",
                        "-o", str(vdir / "raw.%(ext)s"), "--print-to-file", "%(format_id)s|%(ext)s|%(height)s|%(fps)s|%(duration)s",
                        str(vdir / "format.txt"), f"https://www.youtube.com/watch?v={video_id}"], check=True, capture_output=True, text=True)
        raw = next(p for p in vdir.iterdir() if p.name.startswith("raw."))
        fmt = (vdir / "format.txt").read_text().strip().split("|")
        record.update({"raw_sha256": sha256(raw), "raw_bytes": raw.stat().st_size, "format_id": fmt[0], "ext": fmt[1],
                       "height": fmt[2], "source_fps": fmt[3], "duration_s": float(fmt[4])})
        normalized = vdir / "normalized.mp4"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw), "-an", "-vf",
                        f"fps={TARGET_FPS},scale=-2:360", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                        "-pix_fmt", "yuv420p", str(normalized)], check=True)
        cap = cv2.VideoCapture(str(normalized))
        assert cap.isOpened(), "normalized video does not open"
        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(model)),
            running_mode=mp.tasks.vision.RunningMode.VIDEO, num_poses=1,
            min_pose_detection_confidence=0.5, min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5, output_segmentation_masks=False)
        poses, raw_poses, detected = [], [], []
        next_dense, index = 0.0, 0
        with mp.tasks.vision.PoseLandmarker.create_from_options(options) as landmarker:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                t_ms = int(round(index * 1000 / TARGET_FPS))
                result = landmarker.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)), t_ms)
                if result.pose_landmarks:
                    pts = result.pose_landmarks[0]
                    pose = np.asarray([[pts[i].x, pts[i].y, pts[i].z, float(pts[i].visibility or 0)] for i in KEEP_17], dtype=np.float32)
                    poses.append(normalize_pose(pose)); raw_poses.append(pose); detected.append(True)
                else:
                    poses.append(np.full((17, 4), np.nan, np.float32)); raw_poses.append(np.full((17, 4), np.nan, np.float32)); detected.append(False)
                if index % OVERVIEW_EVERY == 0:
                    cv2.imwrite(str(vdir / "overview" / f"{index // OVERVIEW_EVERY:05d}_{index / TARGET_FPS:08.1f}s.jpg"),
                                resize_width(frame, OVERVIEW_W), [cv2.IMWRITE_JPEG_QUALITY, 80])
                if index >= next_dense:
                    cv2.imwrite(str(vdir / "dense" / f"{index / TARGET_FPS:08.2f}s.jpg"), resize_width(frame, DENSE_W), [cv2.IMWRITE_JPEG_QUALITY, 75])
                    next_dense += DENSE_EVERY
                index += 1
        cap.release()
        assert poses, "no frames decoded"
        detected = np.asarray(detected, bool)
        np.savez_compressed(vdir / "pose.npz", landmarks=fill_missing(np.stack(poses)), image_landmarks=fill_missing(np.stack(raw_poses)),
                            detected=detected, timestamps_s=(np.arange(len(poses)) / TARGET_FPS).astype(np.float32),
                            target_fps=np.float32(TARGET_FPS), video_id=video_id)
        record.update({"frames": len(poses), "decoded_duration_s": len(poses) / TARGET_FPS, "pose_detection_rate": float(detected.mean())})
    except Exception as error:  # record and continue with the next video
        record.update({"status": "error", "error": f"{type(error).__name__}: {str(error)[:300]}"})
    finally:
        for path in (raw, normalized):
            if path is not None:
                path.unlink(missing_ok=True)  # raw media never persists
    assert not list(vdir.glob("*.mp4")) and not list(vdir.glob("raw.*")), "raw video left on disk"
    record["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    (vdir / "record.json").write_text(json.dumps(record, indent=2) + "\n")
    if record["status"] == "ok":
        files = sorted(p for p in vdir.rglob("*") if p.is_file() and p.name != "format.txt")
        (vdir / "SHA256SUMS.txt").write_text("".join(f"{sha256(p)}  {p.relative_to(vdir)}\n" for p in files))
        zip_path = out_dir / f"{prefix}_{video_id}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as archive:  # JPEG and npz are already compressed
            for p in sorted(q for q in vdir.rglob("*") if q.is_file() and q.name != "format.txt"):
                archive.write(p, Path(video_id) / p.relative_to(vdir))
        record["zip_sha256"] = sha256(zip_path)
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work", type=Path)
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("video_ids", nargs="+")
    parser.add_argument("--yt-dlp", default="yt-dlp")
    parser.add_argument("--prefix", default="long_video_test_v1", help="ZIP name prefix")
    args = parser.parse_args()
    args.work.mkdir(parents=True, exist_ok=True)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    model = args.work / "pose_landmarker_full.task"
    if not model.exists():
        urllib.request.urlretrieve(MODEL_URL, model)
    for video_id in args.video_ids:
        record = process(video_id, args.work, args.out_dir, args.yt_dlp, model, args.prefix)
        record["pose_model_sha256"] = sha256(model)
        with (args.out_dir / "intake_log.jsonl").open("a") as log:
            log.write(json.dumps(record) + "\n")
        print(json.dumps({k: record.get(k) for k in ("video_id", "status", "duration_s", "frames", "pose_detection_rate", "error")}), flush=True)


if __name__ == "__main__":
    main()
