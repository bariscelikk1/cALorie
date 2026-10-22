#!/usr/bin/env python3
"""Build Notebook 37: pinned RepCount external-development intake."""

import json
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "ml/notebooks/37_colab_repcount_external_development_intake.ipynb"


def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": dedent(source).lstrip().splitlines(True)}


def code(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": dedent(source).lstrip().splitlines(True),
    }


cells = [
    md(
        """
        # cALorie Notebook 37 — RepCount external development intake

        **Purpose:** automatically fetch a pinned, 30-video RepCount-A development pack,
        extract visible-motion evidence and MediaPipe pose, then run the already-frozen V6-F
        model. This is a source-shift diagnostic, **not** a new benchmark and not training.

        - No YouTube downloader and no manual upload.
        - The locked six-creator benchmark is never read or changed.
        - Published RepCount action/cycle metadata is a provisional locator, not a human label.
        - `stu1`–`stu7` are review-only train-pool candidates; training remains forbidden.
        - `stu8`–`stu10` are person-disjoint development validation and remain evaluation-only.
        - V6-F threshold stays frozen at `0.65`; this notebook must not tune it.

        Use **Runtime → Run all**. CPU is sufficient; a T4 does not materially accelerate
        MediaPipe extraction. Raw videos are deleted before the report ZIP is built.
        """
    ),
    code(
        """
        %pip install -q "pylance>=0.37,<0.40" mediapipe==0.10.35 opencv-python-headless==4.11.0.86 pandas==2.2.3
        """
    ),
    code(
        """
        import hashlib, json, math, os, re, shutil, urllib.request, zipfile
        from pathlib import Path

        import cv2
        import lance
        import mediapipe as mp
        import numpy as np
        import pandas as pd
        import torch
        import torch.nn as nn
        from google.colab import files
        from IPython.display import display
        from PIL import Image, ImageDraw, ImageFont
        from tqdm.auto import tqdm

        SEED = 20261022
        np.random.seed(SEED); torch.manual_seed(SEED)
        DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        SOURCE_COMMIT = "aa3279b6714e0ffa2f0bb6b245da335284b1c25f"
        RAW_ROOT = f"https://raw.githubusercontent.com/bariscelikk1/cALorie/{SOURCE_COMMIT}"
        LANCE_REVISION = "ae2e0b0496124d900d4e54a8e92f7ec15a292afd"
        METADATA_REVISION = "d4c2ad3df38dfef3d1fca6f7b3fdfad6a38128e5"
        TARGET_FPS, WINDOW, STRIDE = 15.0, 64, 32
        V6F_THRESHOLD = 0.65
        SUPPORTED_CLASSES = [
            "bench_press", "bicep_curl", "deadlift", "dumbbell_row",
            "jumping_jack", "lat_pulldown", "lateral_raise", "lunge",
            "pull_up", "push_up", "shoulder_press", "sit_up", "squat",
            "tricep_extension",
        ]

        WORK = Path("/content/calorie_repcount_external_development_v1_work")
        INPUTS, VIDEOS, POSE, EVIDENCE, REPORT = [WORK / x for x in ("inputs", "videos", "pose", "evidence", "report")]
        for path in (INPUTS, VIDEOS, POSE, EVIDENCE, REPORT): path.mkdir(parents=True, exist_ok=True)

        print("Device:", DEVICE)
        print("Pinned project commit:", SOURCE_COMMIT)
        print("Pinned RepCount-A Lance revision:", LANCE_REVISION)
        """
    ),
    code(
        """
        def sha256(path):
            digest = hashlib.sha256()
            with open(path, "rb") as handle:
                for chunk in iter(lambda: handle.read(1 << 20), b""): digest.update(chunk)
            return digest.hexdigest()

        FILES = {
            "candidates.csv": ("ml/data/repcount_development_v1/candidates.csv", "266726ce170a992cd33aae8de3fd6cb9dfba6d2128908f93bf4edb4859234dad"),
            "contract_audit.json": ("ml/data/repcount_development_v1/audit.json", "14d128b823937f7000c47f28e022e10ade2be02f4bafffedde4b7339b312980c"),
            "v6f_classifier.pt": ("ml/artifacts/v6f_multistream_gate/model/frozen_temporal_classifier_checkpoint.pt", "c30ecd625d77f31380a503f881eff5c540b8a7cdbbb71a39276c33b908947b92"),
            "joint_gate.pt": ("ml/artifacts/v6f_multistream_gate/model/joint_gate.pt", "a01b0f9c00bcd69150fbd10db385fddb5e3c8b35497acae620dc1fa35f8f6cfb"),
            "bone_gate.pt": ("ml/artifacts/v6f_multistream_gate/model/bone_gate.pt", "ef7d3e19a7c237e99c7cad956b6f39e13f5aa8a36ff965c167ee690f4d400707"),
            "velocity_gate.pt": ("ml/artifacts/v6f_multistream_gate/model/velocity_gate.pt", "3af308a69145981ca0a5ea79b243b3d0b04d18f7c75ff49c59a088e9ce50788c"),
        }

        downloaded = {}
        for name, (relative, expected) in FILES.items():
            target = INPUTS / name
            urllib.request.urlretrieve(f"{RAW_ROOT}/{relative}", target)
            observed = sha256(target)
            assert observed == expected, (name, observed, expected)
            downloaded[name] = target
            print(name, observed[:12])
        """
    ),
    code(
        """
        candidates = pd.read_csv(downloaded["candidates.csv"])
        contract = json.loads(downloaded["contract_audit.json"].read_text())
        candidates["training_allowed"] = candidates.training_allowed.astype(str).str.lower().eq("true")

        assert contract["audit_pass"] and not contract["errors"]
        assert len(candidates) == 30 and candidates.person_id.nunique() == 10
        assert candidates.video_id.is_unique and candidates.source_name.is_unique
        assert set(candidates.source_action) == {"squat", "situp", "front_raise"}
        assert dict(candidates.groupby("source_action").size()) == {"front_raise": 10, "situp": 10, "squat": 10}
        assert set(candidates[candidates.development_role == "train_pool"].person_id) == {f"stu{i}" for i in range(1, 8)}
        assert set(candidates[candidates.development_role == "dev_validation"].person_id) == {"stu8", "stu9", "stu10"}
        assert not candidates.training_allowed.any()
        assert candidates.review_status.eq("metadata_only").all()
        assert candidates.loc[candidates.source_action == "front_raise", "target_label"].eq("unknown").all()
        print("Contract locked: 30 clips / 10 people / zero training-approved rows")
        display(candidates.groupby(["development_role", "source_action"]).size().unstack(fill_value=0))
        """
    ),
    md(
        """
        ## Fetch only the selected embedded video blobs

        The public mirror is revision-pinned. Scalar metadata is matched first; only the 30
        selected row blobs are read. Raw videos remain ephemeral and are not put in the ZIP.
        """
    ),
    code(
        """
        scalar_columns = ["video_id", "source_name", "split", "action_type", "count", "cycle_bounds_json", "video_ext", "video_size_bytes"]
        datasets, metadata_parts = {}, []
        for split in ("train", "validation", "test"):
            uri = f"hf://datasets/lmms-lab-eval/repcounta-lance/data/{split}.lance"
            ds = lance.dataset(uri, storage_options={"hf_revision": LANCE_REVISION, "hf_enable_resolve_cache": "true"})
            frame = ds.to_table(columns=scalar_columns, with_row_id=True).to_pandas()
            frame["lance_split"] = split
            datasets[split] = ds
            metadata_parts.append(frame)
            print(split, len(frame), "rows")

        mirror = pd.concat(metadata_parts, ignore_index=True).rename(columns={"_rowid": "lance_row_id"})
        selected = candidates.merge(mirror, on="video_id", how="left", validate="one_to_one", suffixes=("_contract", "_mirror"))
        assert selected.lance_row_id.notna().all()
        assert selected.source_name_contract.eq(selected.source_name_mirror).all()
        assert selected.metadata_split.eq(selected.lance_split).all()
        assert selected.source_action.eq(selected.action_type).all()
        assert selected.repetition_count.astype(int).eq(selected["count"].astype(int)).all()
        selected.to_csv(REPORT / "selected_source_metadata.csv", index=False)
        display(selected[["video_id", "person_id", "source_action", "target_label", "development_role", "count"]])
        """
    ),
    code(
        """
        def parse_bounds(value):
            try: value = json.loads(value) if isinstance(value, str) else value
            except json.JSONDecodeError: return []
            numbers = []
            def walk(item):
                if isinstance(item, dict):
                    for child in item.values(): walk(child)
                elif isinstance(item, (list, tuple, np.ndarray)):
                    for child in item: walk(child)
                elif isinstance(item, (int, float)) and np.isfinite(item): numbers.append(float(item))
            walk(value)
            return sorted(x for x in numbers if x >= 0)

        def probe(path):
            cap = cv2.VideoCapture(str(path)); assert cap.isOpened(), path
            fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
            frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
            cap.release()
            assert fps > 0 and frames > 0 and width > 0 and height > 0, (path, fps, frames, width, height)
            return {"source_fps": fps, "source_frames": frames, "duration_s": frames / fps, "width": width, "height": height}

        source_rows = []
        for row in tqdm(selected.itertuples(index=False), total=len(selected), desc="Reading pinned blobs"):
            extension = str(row.video_ext or ".mp4")
            if not extension.startswith("."): extension = "." + extension
            target = VIDEOS / f"{row.video_id}{extension}"
            blob = datasets[row.lance_split].take_blobs("video_blob", ids=[int(row.lance_row_id)])[0]
            payload = blob.read()
            if hasattr(payload, "to_pybytes"): payload = payload.to_pybytes()
            target.write_bytes(payload)
            assert target.stat().st_size == int(row.video_size_bytes)
            info = probe(target)
            bounds = parse_bounds(row.cycle_bounds_json)
            start_frame = max(0, int(math.floor(min(bounds)))) if bounds else 0
            end_frame = min(info["source_frames"] - 1, int(math.ceil(max(bounds)))) if bounds else info["source_frames"] - 1
            assert end_frame > start_frame, (row.video_id, bounds)
            source_rows.append({
                "video_id": row.video_id, "video_path": str(target), "video_sha256": sha256(target),
                "annotated_start_frame": start_frame, "annotated_end_frame": end_frame,
                "annotated_start_s": start_frame / info["source_fps"], "annotated_end_s": end_frame / info["source_fps"],
                "cycle_boundary_count": len(bounds), **info,
            })

        source_audit = selected.merge(pd.DataFrame(source_rows), on="video_id", validate="one_to_one")
        source_audit.to_csv(REPORT / "source_download_audit.csv", index=False)
        print("Downloaded selected GB:", round(sum(Path(x).stat().st_size for x in source_audit.video_path) / 1e9, 3))
        """
    ),
    code(
        """
        def contact_sheet(row, columns=4, rows=3):
            count = columns * rows
            times = np.linspace(row.annotated_start_s, row.annotated_end_s, count)
            cap = cv2.VideoCapture(row.video_path)
            tiles = []
            for time_s in times:
                cap.set(cv2.CAP_PROP_POS_MSEC, float(time_s) * 1000)
                ok, frame = cap.read(); assert ok, (row.video_id, time_s)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame); image.thumbnail((320, 200))
                canvas = Image.new("RGB", (320, 225), "black")
                canvas.paste(image, ((320 - image.width) // 2, 25))
                ImageDraw.Draw(canvas).text((8, 5), f"{row.video_id} | {time_s:.2f}s", fill="yellow")
                tiles.append(canvas)
            cap.release()
            sheet = Image.new("RGB", (columns * 320, rows * 225), "black")
            for index, tile in enumerate(tiles): sheet.paste(tile, ((index % columns) * 320, (index // columns) * 225))
            output = EVIDENCE / f"{row.video_id}.jpg"; sheet.save(output, quality=88)
            return str(output.relative_to(WORK))

        source_audit["contact_sheet"] = [contact_sheet(row) for row in tqdm(source_audit.itertuples(index=False), total=len(source_audit), desc="Contact sheets")]
        source_audit.to_csv(REPORT / "source_download_audit.csv", index=False)
        display(Image.open(WORK / source_audit.iloc[0].contact_sheet))
        """
    ),
    md(
        """
        ## Continuous pose extraction inside published cycle bounds

        The crop uses published repetition-cycle boundaries, while class acceptance remains
        provisional. Pose is normalized using hip center and shoulder/torso scale, matching the
        existing cALorie pipeline.
        """
    ),
    code(
        """
        MODEL_PATH = WORK / "pose_landmarker_full.task"
        MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"
        if not MODEL_PATH.exists(): urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        KEEP_17 = [0, 2, 5, 7, 8, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
        LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_HIP, RIGHT_HIP = 5, 6, 11, 12

        def normalize_pose(frame):
            xyz = frame[:, :3].copy()
            hip = (xyz[LEFT_HIP] + xyz[RIGHT_HIP]) / 2
            shoulder = (xyz[LEFT_SHOULDER] + xyz[RIGHT_SHOULDER]) / 2
            scale = max(float(np.linalg.norm(xyz[LEFT_SHOULDER] - xyz[RIGHT_SHOULDER])), float(np.linalg.norm(shoulder - hip)), 1e-6)
            return np.concatenate([(xyz - hip) / scale, frame[:, 3:4]], axis=1)

        def fill_missing(sequence):
            flat = sequence.reshape(len(sequence), -1)
            return pd.DataFrame(flat).interpolate(limit_direction="both").fillna(0).to_numpy().reshape(sequence.shape).astype(np.float32)

        def extract_pose(row):
            cap = cv2.VideoCapture(row.video_path); assert cap.isOpened()
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(row.annotated_start_frame))
            next_sample = float(row.annotated_start_s)
            frame_index = int(row.annotated_start_frame)
            poses, timestamps, detected = [], [], []
            options = mp.tasks.vision.PoseLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(MODEL_PATH)),
                running_mode=mp.tasks.vision.RunningMode.VIDEO, num_poses=1,
                min_pose_detection_confidence=0.5, min_pose_presence_confidence=0.5,
                min_tracking_confidence=0.5, output_segmentation_masks=False,
            )
            with mp.tasks.vision.PoseLandmarker.create_from_options(options) as landmarker:
                while frame_index <= int(row.annotated_end_frame):
                    ok, frame = cap.read()
                    if not ok: break
                    time_s = frame_index / float(row.source_fps); frame_index += 1
                    if time_s + 1e-9 < next_sample: continue
                    next_sample += 1 / TARGET_FPS
                    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    result = landmarker.detect_for_video(image, int(round(time_s * 1000)))
                    if result.pose_landmarks:
                        points = result.pose_landmarks[0]
                        pose = np.asarray([[points[i].x, points[i].y, points[i].z, float(points[i].visibility or 0)] for i in KEEP_17], dtype=np.float32)
                        poses.append(normalize_pose(pose)); detected.append(True)
                    else:
                        poses.append(np.full((17, 4), np.nan, dtype=np.float32)); detected.append(False)
                    timestamps.append(time_s)
            cap.release()
            assert poses, row.video_id
            return fill_missing(np.stack(poses)), np.asarray(timestamps, np.float32), np.asarray(detected, bool)

        pose_rows = []
        for row in tqdm(source_audit.itertuples(index=False), total=len(source_audit), desc="MediaPipe pose"):
            landmarks, timestamps, detected = extract_pose(row)
            output = POSE / f"{row.video_id}.npz"
            np.savez_compressed(output, landmarks=landmarks, timestamps_s=timestamps, detected=detected,
                                target_fps=np.float32(TARGET_FPS), source_fps=np.float32(row.source_fps), video_id=row.video_id)
            pose_rows.append({"video_id": row.video_id, "pose_path": str(output.relative_to(WORK)), "sampled_frames": len(landmarks),
                              "pose_detection_rate": float(detected.mean()), "pose_status": "ok" if detected.mean() >= 0.8 else "needs_pose_review"})
        pose_audit = source_audit.merge(pd.DataFrame(pose_rows), on="video_id", validate="one_to_one")
        pose_audit.to_csv(REPORT / "pose_audit.csv", index=False)
        display(pose_audit.groupby(["development_role", "source_action"])["pose_detection_rate"].agg(["count", "mean", "min"]))
        """
    ),
    code(
        """
        def resample_window(pose):
            old = np.arange(len(pose), dtype=np.float32); new = np.linspace(0, len(pose) - 1, WINDOW, dtype=np.float32)
            flat = pose.reshape(len(pose), -1)
            return np.stack([np.interp(new, old, flat[:, j]) for j in range(flat.shape[1])], 1).reshape(WINDOW, 17, 4).astype(np.float32)

        arrays, window_rows = [], []
        for row in pose_audit.itertuples(index=False):
            with np.load(WORK / row.pose_path, allow_pickle=False) as data:
                pose, timestamps = data["landmarks"], data["timestamps_s"]
            if len(pose) < WINDOW:
                starts, windows = [0], [resample_window(pose)]
            else:
                starts = list(range(0, len(pose) - WINDOW + 1, STRIDE)); final = len(pose) - WINDOW
                if starts[-1] != final: starts.append(final)
                windows = [pose[start:start + WINDOW].astype(np.float32) for start in starts]
            for local_index, (start, window) in enumerate(zip(starts, windows)):
                assert window.shape == (WINDOW, 17, 4) and np.isfinite(window).all()
                arrays.append(window)
                window_rows.append({"video_id": row.video_id, "person_id": row.person_id, "source_action": row.source_action,
                                    "target_label": row.target_label, "development_role": row.development_role,
                                    "window_index": local_index, "window_start_s": float(timestamps[min(start, len(timestamps)-1)])})
        X = np.stack(arrays).astype(np.float32); window_meta = pd.DataFrame(window_rows)
        print("Diagnostic windows:", X.shape)
        """
    ),
    code(
        """
        BONE_EDGES = [(5,6),(5,7),(7,9),(6,8),(8,10),(5,11),(6,12),(11,12),(11,13),(13,15),(12,14),(14,16)]
        ANGLE_TRIPLETS = [(5,7,9),(6,8,10),(7,5,11),(8,6,12),(5,11,13),(6,12,14),(11,13,15),(12,14,16)]

        def pose_to_features(sample):
            xy = sample[:, :, :2].astype(np.float32)
            velocity = np.zeros_like(xy); velocity[1:] = xy[1:] - xy[:-1]
            bones = np.stack([xy[:, child] - xy[:, parent] for parent, child in BONE_EDGES], 1)
            angles = []
            for first, center, last in ANGLE_TRIPLETS:
                a, b = xy[:, first] - xy[:, center], xy[:, last] - xy[:, center]
                cosine = np.sum(a*b, 1) / np.maximum(np.linalg.norm(a, axis=1)*np.linalg.norm(b, axis=1), 1e-6)
                angles.append(np.arccos(np.clip(cosine, -1, 1)) / np.pi)
            return np.concatenate([xy.reshape(WINDOW,-1), velocity.reshape(WINDOW,-1), bones.reshape(WINDOW,-1), np.stack(angles,1)], 1).astype(np.float32)

        def pose_to_stream(sample, stream):
            xy = sample[:, :, :2].astype(np.float32)
            if stream == "joint": return xy.reshape(WINDOW, -1)
            if stream == "velocity":
                velocity = np.zeros_like(xy); velocity[1:] = xy[1:] - xy[:-1]
                return velocity.reshape(WINDOW, -1)
            if stream == "bone": return np.stack([xy[:, child] - xy[:, parent] for parent, child in BONE_EDGES], 1).reshape(WINDOW, -1)
            raise ValueError(stream)

        class TemporalBlock(nn.Module):
            def __init__(self, input_channels, output_channels, dilation, dropout=0.2):
                super().__init__()
                self.net = nn.Sequential(nn.Conv1d(input_channels, output_channels, 3, padding=dilation, dilation=dilation), nn.BatchNorm1d(output_channels), nn.ReLU(), nn.Dropout(dropout),
                                         nn.Conv1d(output_channels, output_channels, 3, padding=dilation, dilation=dilation), nn.BatchNorm1d(output_channels), nn.ReLU(), nn.Dropout(dropout))
                self.residual = nn.Conv1d(input_channels, output_channels, 1) if input_channels != output_channels else nn.Identity()
            def forward(self, x): return torch.relu(self.net(x) + self.residual(x))

        class SmallTCN(nn.Module):
            def __init__(self, input_features, classes):
                super().__init__(); blocks, current = [], input_features
                for level, output in enumerate([64, 96, 128, 128]):
                    blocks.append(TemporalBlock(current, output, 2**level)); current = output
                self.features, self.classifier = nn.Sequential(*blocks), nn.Linear(current, classes)
            def forward(self, x): return self.classifier(self.features(x).mean(-1))

        classifier_checkpoint = torch.load(downloaded["v6f_classifier.pt"], map_location=DEVICE, weights_only=False)
        assert list(classifier_checkpoint["supported_classes"]) == SUPPORTED_CLASSES
        exercise_model = SmallTCN(100, len(SUPPORTED_CLASSES)).to(DEVICE)
        exercise_model.load_state_dict(classifier_checkpoint["exercise_state_dict"])
        gates = {}
        for stream, dimension in {"joint":34, "bone":24, "velocity":34}.items():
            checkpoint = torch.load(downloaded[f"{stream}_gate.pt"], map_location=DEVICE, weights_only=False)
            assert checkpoint["stream"] == stream and int(checkpoint["input_features"]) == dimension
            model = SmallTCN(dimension, 2).to(DEVICE); model.load_state_dict(checkpoint["state_dict"]); gates[stream] = model
        for model in [exercise_model, *gates.values()]: model.eval()

        def probabilities(model, transform, batch_size=256):
            output = []
            with torch.no_grad():
                for start in range(0, len(X), batch_size):
                    batch = np.stack([transform(x) for x in X[start:start+batch_size]]).transpose(0,2,1)
                    output.append(model(torch.from_numpy(batch).to(DEVICE)).softmax(1).cpu().numpy())
            return np.concatenate(output)

        exercise_probability = probabilities(exercise_model, pose_to_features)
        stream_probability = {name: probabilities(model, lambda x, n=name: pose_to_stream(x,n))[:,1] for name, model in gates.items()}
        gate_probability = np.stack([stream_probability[x] for x in ("joint","bone","velocity")], 1).mean(1)
        exercise_index = exercise_probability.argmax(1)
        window_meta["gate_supported_probability"] = gate_probability
        for stream in ("joint","bone","velocity"): window_meta[f"{stream}_gate_supported_probability"] = stream_probability[stream]
        window_meta["exercise_prediction"] = [SUPPORTED_CLASSES[i] for i in exercise_index]
        window_meta["prediction"] = np.where(gate_probability >= V6F_THRESHOLD, window_meta.exercise_prediction, "unknown")
        for index, name in enumerate(SUPPORTED_CLASSES): window_meta[f"exercise_probability__{name}"] = exercise_probability[:,index]
        window_meta.to_csv(REPORT / "window_predictions.csv", index=False)
        """
    ),
    code(
        """
        video_rows = []
        for video_id, group in window_meta.groupby("video_id", sort=False):
            base = group.iloc[0]
            mean_class = np.asarray([group[f"exercise_probability__{name}"].mean() for name in SUPPORTED_CLASSES])
            predicted_exercise = SUPPORTED_CLASSES[int(mean_class.argmax())]
            gate = float(group.gate_supported_probability.mean())
            video_rows.append({"video_id": video_id, "person_id": base.person_id, "source_action": base.source_action,
                               "provisional_target": base.target_label, "development_role": base.development_role,
                               "window_count": len(group), "gate_supported_probability": gate,
                               "predicted_exercise": predicted_exercise,
                               "frozen_v6f_prediction": predicted_exercise if gate >= V6F_THRESHOLD else "unknown",
                               "provisional_match": (predicted_exercise if gate >= V6F_THRESHOLD else "unknown") == base.target_label,
                               **{f"{s}_gate_supported_probability": float(group[f"{s}_gate_supported_probability"].mean()) for s in ("joint","bone","velocity")}})
        diagnostics = pd.DataFrame(video_rows)
        diagnostics.to_csv(REPORT / "video_diagnostics.csv", index=False)

        summary = diagnostics.groupby(["development_role", "source_action", "provisional_target"]).agg(
            clips=("video_id","size"), provisional_alignment=("provisional_match","mean"),
            mean_gate_probability=("gate_supported_probability","mean")
        ).reset_index()
        summary.to_csv(REPORT / "provisional_summary.csv", index=False)
        display(summary)
        display(diagnostics[["video_id","person_id","source_action","provisional_target","frozen_v6f_prediction","gate_supported_probability","provisional_match"]])
        print("Reminder: provisional alignment is a development diagnostic, NOT locked-benchmark accuracy.")
        """
    ),
    code(
        """
        run_metadata = {
            "notebook": "37_colab_repcount_external_development_intake.ipynb",
            "experiment": "repcount_external_development_intake_v1",
            "source_commit": SOURCE_COMMIT,
            "repcount_lance_revision": LANCE_REVISION,
            "repcount_metadata_revision": METADATA_REVISION,
            "seed": SEED, "target_fps": TARGET_FPS, "window_frames": WINDOW, "stride_frames": STRIDE,
            "model": "frozen_v6f", "gate_threshold": V6F_THRESHOLD, "threshold_changed": False,
            "rows": int(len(diagnostics)), "people": int(diagnostics.person_id.nunique()),
            "roles": diagnostics.development_role.value_counts().to_dict(),
            "raw_video_packaged": False, "training_performed": False, "training_allowed_rows": 0,
            "locked_benchmark_read": False, "eligible_as_locked_benchmark": False,
            "eligible_for_threshold_selection": False,
            "interpretation": "Source-shift screening using published action/cycle metadata. Visible-motion review is required before train-pool promotion. Dev-validation people remain evaluation-only.",
        }
        (REPORT / "run_metadata.json").write_text(json.dumps(run_metadata, indent=2) + "\\n")
        (REPORT / "README.md").write_text(
            "# cALorie RepCount external development intake v1\\n\\n"
            "Thirty pinned RepCount-A clips from ten people were fetched without YouTube or manual uploads. "
            "The frozen V6-F model was scored inside published repetition-cycle bounds. Results are provisional "
            "source-shift diagnostics, not locked-benchmark accuracy. No training, calibration, threshold tuning, "
            "or locked benchmark access occurred. Raw videos are intentionally excluded.\\n"
        )

        # Copy compact derived evidence, never raw source video.
        shutil.copytree(POSE, REPORT / "pose", dirs_exist_ok=True)
        shutil.copytree(EVIDENCE, REPORT / "evidence", dirs_exist_ok=True)
        for name in ("candidates.csv", "contract_audit.json"): shutil.copy2(downloaded[name], REPORT / name)
        checksum_rows = []
        for path in sorted(p for p in REPORT.rglob("*") if p.is_file()):
            checksum_rows.append(f"{sha256(path)}  {path.relative_to(REPORT)}")
        (REPORT / "SHA256SUMS.txt").write_text("\\n".join(checksum_rows) + "\\n")

        shutil.rmtree(VIDEOS)  # Explicitly remove licensed raw media before packaging.
        zip_path = Path("/content/calorie_repcount_external_development_v1_report.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(p for p in REPORT.rglob("*") if p.is_file()): archive.write(path, path.relative_to(REPORT.parent))
        print("Report:", zip_path, round(zip_path.stat().st_size / 1e6, 2), "MB")
        files.download(str(zip_path))
        """
    ),
]

notebook = {
    "cells": cells,
    "metadata": {
        "accelerator": "CPU",
        "colab": {"name": OUTPUT.name, "provenance": []},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")
print(OUTPUT)
