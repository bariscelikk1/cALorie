#!/usr/bin/env python3
"""cALorie pipeline: video in, exercise timeline out.

Steps: ffmpeg normalizes to 15 FPS / 360p -> MediaPipe pose (17 keypoints, same
normalization as the training data) -> final model (Notebook 46, three seeds
averaged) -> dense windows every 8 frames -> gate threshold 0.65 -> smoothed
decoder -> segments. Nothing is uploaded anywhere; the video stays local.

Usage: python calorie_pipeline.py VIDEO [--out timeline.csv] [--device cpu|mps]
"""

from __future__ import annotations

import argparse
import io
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml/scripts"))
from score_long_video_test_v1 import (SUPPORTED, STREAMS, STEP, THRESHOLD, WINDOW, SmallTCN, features, load,  # noqa: E402
                                      run_bounds, smooth, stream)

FPS = 15
KEEP_17 = [0, 2, 5, 7, 8, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_HIP, RIGHT_HIP = 5, 6, 11, 12
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"
MODEL_DIR = ROOT / "ml/artifacts/final_model_v1/models"
SEEDS = (42, 137, 2026)


def pose_model_path() -> Path:
    path = ROOT / "ml/app/pose_landmarker_full.task"
    if not path.exists():
        urllib.request.urlretrieve(MODEL_URL, path)
    return path


def normalize_pose(frame: np.ndarray) -> np.ndarray:
    xyz = frame[:, :3].copy()
    hip = (xyz[LEFT_HIP] + xyz[RIGHT_HIP]) / 2
    shoulder = (xyz[LEFT_SHOULDER] + xyz[RIGHT_SHOULDER]) / 2
    scale = max(float(np.linalg.norm(xyz[LEFT_SHOULDER] - xyz[RIGHT_SHOULDER])), float(np.linalg.norm(shoulder - hip)), 1e-6)
    return np.concatenate([(xyz - hip) / scale, frame[:, 3:4]], axis=1)


def extract_pose(video: Path, progress=None) -> tuple[np.ndarray, float]:
    """Return (normalized landmarks [frames, 17, 4], pose detection rate)."""
    with tempfile.TemporaryDirectory() as tmp:
        normalized = Path(tmp) / "normalized.mp4"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video), "-an", "-vf",
                        f"fps={FPS},scale=-2:360", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                        "-pix_fmt", "yuv420p", str(normalized)], check=True)
        cap = cv2.VideoCapture(str(normalized))
        total = max(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 1)
        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(pose_model_path())),
            running_mode=mp.tasks.vision.RunningMode.VIDEO, num_poses=1,
            min_pose_detection_confidence=0.5, min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5, output_segmentation_masks=False)
        poses, detected = [], []
        with mp.tasks.vision.PoseLandmarker.create_from_options(options) as landmarker:
            index = 0
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                result = landmarker.detect_for_video(
                    mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)),
                    int(round(index * 1000 / FPS)))
                if result.pose_landmarks:
                    pts = result.pose_landmarks[0]
                    pose = np.asarray([[pts[i].x, pts[i].y, pts[i].z, float(pts[i].visibility or 0)] for i in KEEP_17], dtype=np.float32)
                    poses.append(normalize_pose(pose)); detected.append(True)
                else:
                    poses.append(np.full((17, 4), np.nan, np.float32)); detected.append(False)
                index += 1
                if progress and index % 150 == 0:
                    progress(min(index / total, 1.0))
        cap.release()
    if not poses:
        raise ValueError("No frames could be decoded from this video.")
    flat = np.stack(poses).reshape(len(poses), -1)
    filled = pd.DataFrame(flat).interpolate(limit_direction="both").fillna(0).to_numpy().reshape(len(poses), 17, 4)
    return filled.astype(np.float32), float(np.mean(detected))


def load_final_model(device):
    seeds = []
    for seed in SEEDS:
        ck = load(str(MODEL_DIR / f"seed_{seed}_classifier_from_nb45.pt"), device)
        assert list(ck["supported_classes"]) == SUPPORTED
        cls = SmallTCN(100, 14).to(device); cls.load_state_dict(ck["exercise_state_dict"]); cls.eval()
        gates = {}
        for name, dim in STREAMS.items():
            g = SmallTCN(dim, 2).to(device)
            g.load_state_dict(load(str(MODEL_DIR / f"seed_{seed}_{name}_gate.pt"), device)["state_dict"]); gates[name] = g.eval()
        seeds.append((cls, gates))
    return seeds


def predict_windows(pose: np.ndarray, models, device, batch: int = 256):
    """Per-window label and gate score; the three seeds' probabilities are averaged."""
    centers = np.arange(0, len(pose), STEP)
    labels, scores = [], []
    with torch.no_grad():
        for i in range(0, len(centers), batch):
            idx = [np.clip(np.arange(c - WINDOW // 2, c + WINDOW // 2), 0, len(pose) - 1) for c in centers[i:i + batch]]
            wins = [pose[j] for j in idx]
            x = torch.from_numpy(np.stack([features(w) for w in wins]).transpose(0, 2, 1).astype(np.float32)).to(device)
            streams = {s: torch.from_numpy(np.stack([stream(w, s) for w in wins]).transpose(0, 2, 1).astype(np.float32)).to(device) for s in STREAMS}
            cls_p = np.mean([cls(x).softmax(1).cpu().numpy() for cls, _ in models], axis=0)
            gate_p = np.mean([np.mean([g[s](streams[s]).softmax(1)[:, 1].cpu().numpy() for s in STREAMS], axis=0) for _, g in models], axis=0)
            labels += [SUPPORTED[c] if gs >= THRESHOLD else "unknown" for c, gs in zip(cls_p.argmax(1), gate_p)]
            scores += list(gate_p)
    return centers / FPS, np.array(labels, dtype=object), np.array(scores)


def timeline(pose: np.ndarray, device="cpu", models=None) -> pd.DataFrame:
    models = models or load_final_model(torch.device(device))
    times, raw, _ = predict_windows(pose, models, torch.device(device))
    smoothed = smooth(raw.copy())
    duration = len(pose) / FPS
    rows = []
    for s, e in run_bounds(smoothed):
        start = 0.0 if s == 0 else float(times[s] - STEP / FPS / 2)
        end = duration if e == len(smoothed) else float(times[e] - STEP / FPS / 2)
        rows.append({"start_s": round(start, 1), "end_s": round(end, 1), "label": smoothed[s]})
    return pd.DataFrame(rows)


def fmt(seconds: float) -> str:
    return f"{int(seconds // 60):02d}:{seconds % 60:04.1f}"


def run(video: Path, device="cpu", progress=None) -> tuple[pd.DataFrame, float]:
    pose, rate = extract_pose(video, progress)
    return timeline(pose, device), rate


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("video", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()
    table, rate = run(args.video, args.device, lambda p: print(f"pose {p:.0%}", flush=True))
    print(f"pose detected in {rate:.0%} of frames")
    for r in table.itertuples():
        print(f"{fmt(r.start_s)} - {fmt(r.end_s)}  {r.label}")
    if args.out:
        table.to_csv(args.out, index=False)


if __name__ == "__main__":
    main()
