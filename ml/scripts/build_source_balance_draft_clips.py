#!/usr/bin/env python3
"""Slice the 29F pose archive into quarantined, first-pass candidate clips."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "ml/artifacts/source_balance_v1/calorie_source_balance_v1_pose_audit.zip"
LABELS = ROOT / "ml/data/source_balance_v1/annotations/first_pass"
OUTPUT = ROOT / "ml/artifacts/source_balance_v1/calorie_source_balance_v1_draft_clips.zip"
EXPECTED_SOURCE_SHA256 = "f8393f2b8c0de03a01121e544d502245cfa0729bd75e56eeac66a936bc013bf0"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(data: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--labels", type=Path, default=LABELS)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    assert sha256(args.source.read_bytes()) == EXPECTED_SOURCE_SHA256, "29F source archive changed"
    files: dict[str, bytes] = {}
    with zipfile.ZipFile(args.source) as source:
        assert source.testzip() is None, "Corrupt 29F source archive"
        checksums = source.read("SHA256SUMS.txt").decode().splitlines()
        for entry in checksums:
            expected, name = entry.split("  ", 1)
            assert sha256(source.read(name)) == expected, f"29F internal hash mismatch: {name}"
        quality = {row["window_id"]: row for row in read_csv(source.read("pose_quality.csv"))}
        assert len(quality) == 17 and all(row["status"] == "pose_ready" for row in quality.values())

        manifest: list[dict[str, object]] = []
        label_paths = sorted(args.labels.glob("*.labels.csv"))
        assert len(label_paths) == 3, "Expected exactly three first-pass window timelines"
        for label_path in label_paths:
            window_id = label_path.name.removesuffix(".labels.csv")
            assert window_id in quality, window_id
            rows = read_csv(label_path.read_bytes())
            assert rows and len([row for row in rows if row["segment_type"] == "exercise"]) == 1
            assert all(
                row["review_status"] == "draft"
                and row["needs_second_review"].lower() == "true"
                and row["use_for_training"].lower() == "false"
                for row in rows
            ), f"This builder only handles unapproved first-pass labels: {window_id}"
            exercise = next(row for row in rows if row["segment_type"] == "exercise")
            assert exercise["current_tcn_label"] in {"dumbbell_row", "sit_up"}
            assert exercise["video_id"] == quality[window_id]["video_id"]
            start_s, end_s = float(exercise["start_s"]), float(exercise["end_s"])
            assert start_s < end_s

            with np.load(io.BytesIO(source.read(quality[window_id]["landmark_path"])), allow_pickle=False) as pose:
                times = pose["timestamps_s"]
                selected = (times >= start_s) & (times < end_s)
                landmarks = pose["landmarks"][selected].astype(np.float32)
                detected = pose["detected"][selected]
                assert str(pose["video_id"].item()) == exercise["video_id"]
                group_id = str(pose["group_id"].item())
                assert group_id == f"youtube:{exercise['video_id']}"
                assert landmarks.shape[1:] == (17, 4) and len(landmarks) >= 64
                detection_rate = float(detected.mean())
                assert detection_rate >= 0.95, (window_id, detection_rate)
                target_fps = float(pose["target_fps"].item())
                assert abs(target_fps - 15) < 0.01

            output_path = f"clips/{exercise['current_tcn_label']}/{window_id}.npz"
            buffer = io.BytesIO()
            np.savez_compressed(
                buffer,
                landmarks=landmarks,
                timestamps_s=(times[selected] - start_s).astype(np.float32),
                detected=detected,
                source_fps=np.float32(target_fps),
            )
            files[output_path] = buffer.getvalue()
            manifest.append({
                "clip_id": window_id,
                "source_dataset": "source_balance_v1_first_pass",
                "source_class": exercise["fine_label"],
                "canonical_class": exercise["current_tcn_label"],
                "original_path": f"youtube:{exercise['video_id']}#{start_s:.2f}-{end_s:.2f}",
                "output_path": output_path,
                "fingerprint": exercise["video_id"],
                "status": "quarantined",
                "source_fps": target_fps,
                "sampled_frames": len(landmarks),
                "detection_rate": round(detection_rate, 6),
                "duration_s": round(end_s - start_s, 2),
                "group_id": group_id,
                "review_status": "draft",
                "needs_second_review": True,
                "training_allowed": False,
            })

    assert len(manifest) == 3
    assert len({row["group_id"] for row in manifest}) == 2
    output_csv = io.StringIO()
    writer = csv.DictWriter(output_csv, fieldnames=list(manifest[0]))
    writer.writeheader()
    writer.writerows(manifest)
    files["manifest.csv"] = output_csv.getvalue().replace("\r\n", "\n").encode()
    files["run_metadata.json"] = (json.dumps({
        "source_report_sha256": EXPECTED_SOURCE_SHA256,
        "source_notebook": "29f_colab_audit_source_balance_pose_candidates.ipynb",
        "annotation_stage": "first_pass_only",
        "independent_second_review_complete": False,
        "training_allowed": False,
        "clip_count": len(manifest),
        "group_count": 2,
        "purpose": "preserve sliced candidate landmarks; block training until review",
    }, indent=2) + "\n").encode()
    files["SHA256SUMS.txt"] = ("\n".join(
        f"{sha256(data)}  {name}" for name, data in sorted(files.items())
    ) + "\n").encode()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED) as output:
        for name, data in sorted(files.items()):
            output.writestr(name, data)
    print(args.output)
    for row in manifest:
        print(row["clip_id"], row["canonical_class"], row["sampled_frames"], row["group_id"])
    print("SHA-256:", sha256(args.output.read_bytes()))


if __name__ == "__main__":
    main()
