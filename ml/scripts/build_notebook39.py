#!/usr/bin/env python3
"""Build Notebook 39: RepCount gate rotation v1 (predeclared, non-promotable)."""

import json
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "ml/notebooks/39_colab_repcount_gate_rotation.ipynb"


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
        # cALorie Notebook 39 — RepCount gate rotation v1

        **Runtime: T4 GPU. Run all.** Output: `calorie_repcount_gate_rotation_v1_report.zip`.

        This runs the predeclared design in
        `ml/data/repcount_development_v1/gate_rotation_v1/DESIGN.md` exactly once.

        - Only the joint, bone, and velocity gate TCNs are retrained, with Notebook 31's recipe.
        - The V6-E exercise classifier, mean-probability fusion, and threshold `0.65` are frozen.
        - The 30 adjudicated RepCount clips are split into 3 source-group folds. Each fold is scored
          only by gates that never trained on it. RepCount is never used for early stopping.
        - Control arm: Notebook 31's archived three-seed gates (same recipe, no RepCount data).
        - The locked creator benchmark is never downloaded or read.
        - The result is **non-promotable** whatever it shows. Do not rerun because of a result.

        Every input is downloaded from a pinned GitHub commit and checked against its SHA-256.
        """
    ),
    code(
        """
        %pip install -q scikit-learn pandas==2.2.3
        """
    ),
    code(
        r'''
        from pathlib import Path
        import hashlib
        import json
        import os
        import random
        import shutil
        import urllib.request
        import zipfile

        import numpy as np
        import pandas as pd
        import torch
        from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report, f1_score
        from torch import nn
        from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler

        try:
            from IPython.display import display
        except ImportError:  # local dry run outside IPython
            display = print

        # Local dry-run switches. Colab leaves all of these unset.
        DRY_RUN = os.environ.get("CALORIE_DRY_RUN") == "1"
        LOCAL_REPO = os.environ.get("CALORIE_LOCAL_REPO")
        WORK = Path(os.environ.get("CALORIE_WORK", "/content"))
        WORK.mkdir(parents=True, exist_ok=True)

        RUN_SEEDS = [42] if DRY_RUN else [42, 137, 2026]
        CONTROL_SEEDS = [42, 137, 2026]
        N_FOLDS = 3
        FIXED_FUSION = "mean_probability"
        FIXED_THRESHOLD = 0.65
        WINDOW = 64
        STRIDE = 32
        BATCH_SIZE = 64
        MAX_EPOCHS = 1 if DRY_RUN else 40
        PATIENCE = 8
        GROUP_TEMPERATURE = 0.5  # frozen from V6-A.1
        DRY_RUN_TRAIN_WINDOWS = 1500
        DRY_RUN_VALIDATION_WINDOWS = 400
        AUGMENTATION_CONFIG = {
            "horizontal_flip_probability": 0.5,
            "rotation_probability": 0.7,
            "max_rotation_degrees": 7.0,
            "speed_probability": 0.5,
            "speed_range": [0.85, 1.15],
            "frame_drop_probability": 0.35,
            "frame_drop_fraction_range": [0.05, 0.12],
            "coordinate_noise_probability": 0.8,
            "coordinate_noise_std": 0.008,
        }
        RETIRED_CLASSES = {"plank"}
        NEW_TRAIN_GROUPS = {"youtube:Fk1wnNX4wQ8", "youtube:zxqCV_eQHZY"}
        UNREVIEWED_GROUPS = {"youtube:oLsonHQJOUc", "youtube:c4TomZjzobY", "youtube:W2Bm9dfQjbk"}
        STREAMS = {"joint": 34, "bone": 24, "velocity": 34}
        SHARED_SOURCE_GROUPS = {
            "outdoor_crunch_shared_01": {"stu8_49", "stu9_56"},
            "orange_rig_squat_shared_01": {"stu1_69", "stu6_59"},
        }


        def seed_everything(seed):
            random.seed(seed)
            np.random.seed(seed)
            torch.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)


        seed_everything(RUN_SEEDS[0])
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("Device:", DEVICE, "| dry run:", DRY_RUN)
        if not DRY_RUN:
            assert DEVICE.type == "cuda", "Select a T4 runtime before training."
        '''
    ),
    md(
        """
        ## Download pinned inputs

        Training evidence is pinned to Notebook 31's commit. RepCount pose, folds, frozen V6-F gates,
        and the Notebook 31 control gates are pinned to the commit that predeclared this design.
        """
    ),
    code(
        r'''
        TRAINING_COMMIT = "9874773e4681464bb00f5f0fb4dc3459caf75d6c"
        DESIGN_COMMIT = "9544dfb4436148bed3328a2854b055f52b82893d"
        INPUTS = {
            # name: (commit, repository path, sha256)
            "calorie_workoutfitness_landmarks_v1.zip": (TRAINING_COMMIT, "ml/artifacts/v1/landmarks/calorie_workoutfitness_landmarks_v1.zip", "6dd4828e73f1ac1cd83a175de5bc1caf8465cbf61b72777467fba540af339aa9"),
            "calorie_mmfit_landmarks_v1.zip": (TRAINING_COMMIT, "ml/artifacts/v1/landmarks/calorie_mmfit_landmarks_v1.zip", "2d3bff2c52842b276562e749fd7eaefe4925385efa7ff8c242c82ba1803413f1"),
            "calorie_mmfit_unknown_v1.zip": (TRAINING_COMMIT, "ml/artifacts/v1/landmarks/calorie_mmfit_unknown_v1.zip", "b0b113b3c5c7fc501b6b3ac4a7d2dade5fb4bccf3416d2eb85fa8b9197ae5596"),
            "calorie_youtube_mixed_landmarks_v3.zip": (TRAINING_COMMIT, "ml/artifacts/v2/landmarks/calorie_youtube_mixed_landmarks_v3.zip", "bd0426eda35654a95a8bac70b0357ba484e82bd29e6b3f71760fcc743f432cf4"),
            "calorie_youtube_additional_landmarks_v1.zip": (TRAINING_COMMIT, "ml/artifacts/v3/landmarks/calorie_youtube_additional_landmarks_v1.zip", "0c60478086400fdfa6974afc6b091023b46e10783a71e40929aaa2b646d02743"),
            "calorie_youtube_training_landmarks_v4.zip": (TRAINING_COMMIT, "ml/artifacts/v3/landmarks/calorie_youtube_training_landmarks_v4.zip", "e0588c9a4a7d0257f710fec74b657e863cda5e0bc3285a640443863c9ede2b19"),
            "calorie_workoutfitness_gate_hardneg_v1.zip": (TRAINING_COMMIT, "ml/artifacts/v5/landmarks/calorie_workoutfitness_gate_hardneg_v1.zip", "b3aab2dbcefd709f1977c4d8d3f7d0326b50444ab44db4ba6b0cf64bbae0f4f6"),
            "calorie_youtube_long_workouts_v2_reviewed_clips.zip": (TRAINING_COMMIT, "ml/artifacts/youtube_long_v2/reviewed_clips/calorie_youtube_long_workouts_v2_reviewed_clips.zip", "84fb55b981820af702a94f0c0070960b24fdd1acb617097f1838c782cd942284"),
            "hard_positive_windows.csv": (TRAINING_COMMIT, "ml/artifacts/v5/hard_positive_mining/hard_positive_windows.csv", "5a4b73c04ee85659570e7931ea0e84b35c0abeb16fd3f08238e629f6eca091c5"),
            "split_assignments.csv": (TRAINING_COMMIT, "ml/artifacts/v6a1/model/split_assignments.csv", "8c013695fe095ceccc4ff65722d2a26e5a309674f5b877b840b71ba73dc085d6"),
            "baseline_test_predictions.csv": (TRAINING_COMMIT, "ml/artifacts/v6c/model/test_window_predictions.csv", "b34b6cada90355682ef7aa225e3d18dad0960dd79ce32856ebb524356734326c"),
            "temporal_checkpoint.pt": (TRAINING_COMMIT, "ml/artifacts/v6e_complete_action_temporal/model/two_stage_tcn_v6e_temporal.pt", "c30ecd625d77f31380a503f881eff5c540b8a7cdbbb71a39276c33b908947b92"),
            "repcount_report.zip": (DESIGN_COMMIT, "ml/artifacts/repcount_external_development_v1/calorie_repcount_external_development_v1_report.zip", "fddd4e63f1162c1b48d1d81165c6e204127226824e5af500f452161f8a7219ef"),
            "folds.csv": (DESIGN_COMMIT, "ml/data/repcount_development_v1/gate_rotation_v1/folds.csv", "37cb91d473d7a940673f0cfe09a59db9a21fe7a2c60577091c619dc11478751c"),
            "v6f_joint_gate.pt": (DESIGN_COMMIT, "ml/artifacts/v6f_multistream_gate/model/joint_gate.pt", "a01b0f9c00bcd69150fbd10db385fddb5e3c8b35497acae620dc1fa35f8f6cfb"),
            "v6f_bone_gate.pt": (DESIGN_COMMIT, "ml/artifacts/v6f_multistream_gate/model/bone_gate.pt", "ef7d3e19a7c237e99c7cad956b6f39e13f5aa8a36ff965c167ee690f4d400707"),
            "v6f_velocity_gate.pt": (DESIGN_COMMIT, "ml/artifacts/v6f_multistream_gate/model/velocity_gate.pt", "3af308a69145981ca0a5ea79b243b3d0b04d18f7c75ff49c59a088e9ce50788c"),
            "nb31_seed_metrics.csv": (DESIGN_COMMIT, "ml/artifacts/v6f_seed_stability/seed_metrics.csv", "a2fec12319d63ce6b65615acabb3a456b26dab46d88b9cc76644ee115c29d76e"),
            "control_seed_42_joint_gate.pt": (DESIGN_COMMIT, "ml/artifacts/v6f_seed_stability/seed_42_joint_gate.pt", "06953c97bf51b659be35d362637701bd5c17c78b5fd67bb8adf2c80ae22de210"),
            "control_seed_42_bone_gate.pt": (DESIGN_COMMIT, "ml/artifacts/v6f_seed_stability/seed_42_bone_gate.pt", "2d0f06da85f968dc024322db1ed006f2404545dbaf45aadc1cf629ebf55a2161"),
            "control_seed_42_velocity_gate.pt": (DESIGN_COMMIT, "ml/artifacts/v6f_seed_stability/seed_42_velocity_gate.pt", "bf0f5f1b6532e191003a1efdcad2b1303f3d9e41b57df7075c193ef0515069d6"),
            "control_seed_137_joint_gate.pt": (DESIGN_COMMIT, "ml/artifacts/v6f_seed_stability/seed_137_joint_gate.pt", "a7c8aed60f96476ee743868c1518628a7d7bb38afb141731476b4fd28a5e507c"),
            "control_seed_137_bone_gate.pt": (DESIGN_COMMIT, "ml/artifacts/v6f_seed_stability/seed_137_bone_gate.pt", "8bf896c9bf17a46f508f7cf4b079b6729e3b0fe387f3bc231fc39331e1e7069a"),
            "control_seed_137_velocity_gate.pt": (DESIGN_COMMIT, "ml/artifacts/v6f_seed_stability/seed_137_velocity_gate.pt", "7135cebc01c1d7c791f0b7288ff293274a5ded620dbaaab1ddd7bfe9b1c5c943"),
            "control_seed_2026_joint_gate.pt": (DESIGN_COMMIT, "ml/artifacts/v6f_seed_stability/seed_2026_joint_gate.pt", "32d3d29d62be3ceaf3412f6b163665d84e2edb4879b84b3c9e198f0a8f2f0aaa"),
            "control_seed_2026_bone_gate.pt": (DESIGN_COMMIT, "ml/artifacts/v6f_seed_stability/seed_2026_bone_gate.pt", "50b7b1ed5e347ad7021faa23fea38e09a7fb618587f53528e181f2ea7cff2948"),
            "control_seed_2026_velocity_gate.pt": (DESIGN_COMMIT, "ml/artifacts/v6f_seed_stability/seed_2026_velocity_gate.pt", "404b5ef7df394f6a99806021227ad4d85957b7809a33876e057063b0787de69a"),
        }
        assert not any("youtube_creator_benchmark" in path for _, path, _ in INPUTS.values()), "Locked benchmark must not be an input."
        LANDMARK_ARCHIVES = [name for name in INPUTS if name.startswith("calorie_") and name.endswith(".zip")]
        INPUT_ROOT = WORK / "inputs"
        INPUT_ROOT.mkdir(exist_ok=True)


        def sha256(path):
            digest = hashlib.sha256()
            with Path(path).open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
            return digest.hexdigest()


        def fetch(name):
            commit, relative, expected = INPUTS[name]
            destination = INPUT_ROOT / name
            if destination.exists() and sha256(destination) == expected:
                print("Cached:", name)
                return destination
            temporary = destination.with_suffix(destination.suffix + ".part")
            temporary.unlink(missing_ok=True)
            if LOCAL_REPO:
                shutil.copy2(Path(LOCAL_REPO) / relative, temporary)
            else:
                url = f"https://raw.githubusercontent.com/bariscelikk1/cALorie/{commit}/{relative}"
                request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(request, timeout=300) as response, temporary.open("wb") as output:
                    shutil.copyfileobj(response, output)
            actual = sha256(temporary)
            assert actual == expected, f"SHA-256 mismatch for {name}: {actual} (expected {expected}). Re-run the cell; if it repeats, the pinned file changed."
            temporary.replace(destination)
            print(f"{name}: {destination.stat().st_size / 1e6:.1f} MB")
            return destination


        PATHS = {name: fetch(name) for name in INPUTS}
        for name in LANDMARK_ARCHIVES:
            with zipfile.ZipFile(PATHS[name]) as archive:
                assert archive.testzip() is None, f"Corrupt ZIP: {name}"
        hard_positive_frame = pd.read_csv(PATHS["hard_positive_windows.csv"])
        assert hard_positive_frame.window_key.is_unique
        baseline_predictions = pd.read_csv(PATHS["baseline_test_predictions.csv"])
        nb31_seed_metrics = pd.read_csv(PATHS["nb31_seed_metrics.csv"])

        SOURCE_ROOT = WORK / "training_sources"
        if SOURCE_ROOT.exists():
            shutil.rmtree(SOURCE_ROOT)
        SOURCE_ROOT.mkdir()
        for index, name in enumerate(LANDMARK_ARCHIVES):
            destination = SOURCE_ROOT / f"source_{index}"
            destination.mkdir()
            with zipfile.ZipFile(PATHS[name]) as archive:
                archive.extractall(destination)

        frames = []
        for manifest_path in SOURCE_ROOT.rglob("manifest.csv"):
            frame = pd.read_csv(manifest_path).fillna("")
            frame["npz_path"] = frame["output_path"].map(lambda value: str(manifest_path.parent / value))
            frames.append(frame)
        assert frames, "No manifest.csv was found."
        manifest = pd.concat(frames, ignore_index=True)
        manifest = manifest[(manifest.status == "ok") & manifest.npz_path.map(lambda value: Path(value).exists())].copy()
        if "group_id" not in manifest or manifest.group_id.eq("").any():
            manifest["group_id"] = manifest.apply(lambda row: f"{row['source_dataset']}:{row['clip_id']}", axis=1)
        assert NEW_TRAIN_GROUPS <= set(manifest.group_id)
        print("Valid clips:", len(manifest), "Groups:", manifest.group_id.nunique())
        '''
    ),
    md(
        """
        ## Rebuild Notebook 31's exact training pool

        Same windows, frozen V6-A.1 split, and train-only phase-resampled cycles as Notebook 31.
        The internal test must still be the same 1,971 windows.
        """
    ),
    code(
        r'''
        def resample_sequence(sequence, source_fps, target_fps=15):
            if not source_fps or abs(float(source_fps) - target_fps) < 0.1:
                return sequence
            duration = (len(sequence) - 1) / float(source_fps)
            target_length = max(2, int(round(duration * target_fps)) + 1)
            old_x = np.linspace(0, duration, len(sequence))
            new_x = np.linspace(0, duration, target_length)
            flat = sequence.reshape(len(sequence), -1)
            sampled = np.stack([np.interp(new_x, old_x, flat[:, index]) for index in range(flat.shape[1])], axis=1)
            return sampled.reshape(target_length, 17, 4).astype(np.float32)


        windows, original_labels, groups = [], [], []
        clip_ids, sources, starts = [], [], []
        for row in manifest.itertuples(index=False):
            with np.load(row.npz_path, allow_pickle=False) as item:
                sequence = item["landmarks"].astype(np.float32)
            if sequence.ndim != 3 or sequence.shape[1:] != (17, 4):
                print("Skipping unexpected shape:", row.npz_path, sequence.shape)
                continue
            sequence = resample_sequence(sequence, getattr(row, "source_fps", 15) or 15)
            clip_starts = list(range(0, max(1, len(sequence) - WINDOW + 1), STRIDE))
            if len(sequence) > WINDOW and clip_starts[-1] != len(sequence) - WINDOW:
                clip_starts.append(len(sequence) - WINDOW)
            for start in clip_starts:
                window = sequence[start:start + WINDOW]
                if len(window) < WINDOW:
                    window = np.concatenate([window, np.repeat(window[-1:], WINDOW - len(window), axis=0)])
                windows.append(window)
                original_labels.append(row.canonical_class)
                groups.append(row.group_id)
                clip_ids.append(row.clip_id)
                sources.append(row.source_dataset)
                starts.append(start)

        X = np.asarray(windows, dtype=np.float32)
        original_labels = np.asarray(original_labels, dtype=object)
        groups = np.asarray(groups, dtype=object)
        clip_ids = np.asarray(clip_ids, dtype=object)
        sources = np.asarray(sources, dtype=object)
        starts = np.asarray(starts, dtype=np.int64)
        window_keys = np.asarray([f"{s}|{g}|{c}|{t}" for s, g, c, t in zip(sources, groups, clip_ids, starts)], dtype=object)

        frozen_split = pd.read_csv(PATHS["split_assignments.csv"])
        assert frozen_split.groupby("group_id")["split"].nunique().max() == 1
        group_to_split = frozen_split[["group_id", "split"]].drop_duplicates("group_id").set_index("group_id")["split"].to_dict()
        old_evidence_mask = np.asarray([group in group_to_split for group in groups])
        assigned_split = np.asarray([group_to_split.get(group, "") for group in groups], dtype=object)
        new_train_mask = np.isin(groups, list(NEW_TRAIN_GROUPS))
        assigned_split[new_train_mask] = "train"
        missing_groups = set(groups[assigned_split == ""])
        assert missing_groups <= UNREVIEWED_GROUPS, "Unexpected unresolved groups: " + str(sorted(missing_groups))
        labels = np.where(np.isin(original_labels, list(RETIRED_CLASSES)), "unknown", original_labels).astype(object)
        ALL_CLASSES = sorted(np.unique(labels).tolist())
        SUPPORTED_CLASSES = [name for name in ALL_CLASSES if name != "unknown"]
        assert len(SUPPORTED_CLASSES) == 14, SUPPORTED_CLASSES
        supported_to_id = {name: index for index, name in enumerate(SUPPORTED_CLASSES)}
        assert set(window_keys[old_evidence_mask]) == set(frozen_split.window_key), "Reviewed window evidence changed since V6-A.1."


        def estimate_period(sequence, minimum=12, maximum=90):
            xy = sequence[:, :, :2]
            energy = np.r_[0.0, np.linalg.norm(np.diff(xy, axis=0), axis=2).mean(axis=1)]
            energy = np.convolve(energy, np.ones(5) / 5.0, mode="same")
            centered = energy - energy.mean()
            upper = min(maximum, len(sequence) // 2)
            if upper <= minimum:
                return max(minimum, len(sequence))
            scores = []
            for lag in range(minimum, upper + 1):
                left, right = centered[:-lag], centered[lag:]
                denom = np.linalg.norm(left) * np.linalg.norm(right)
                scores.append(float(np.dot(left, right) / max(denom, 1e-8)))
            return minimum + int(np.argmax(scores))


        def phase_resample(segment, target_length=WINDOW):
            xy = segment[:, :, :2]
            step_motion = np.r_[0.0, np.linalg.norm(np.diff(xy, axis=0), axis=2).mean(axis=1)]
            progress = np.cumsum(step_motion + 1e-5)
            progress = (progress - progress[0]) / max(progress[-1] - progress[0], 1e-8)
            targets = np.linspace(0.0, 1.0, target_length)
            flat = segment.reshape(len(segment), -1)
            sampled = np.stack([np.interp(targets, progress, flat[:, column]) for column in range(flat.shape[1])], axis=1)
            return sampled.reshape(target_length, 17, 4).astype(np.float32)


        temporal_windows, temporal_labels, temporal_groups = [], [], []
        temporal_clip_ids, temporal_sources, temporal_starts, temporal_keys = [], [], [], []
        for row in manifest.itertuples(index=False):
            canonical = "unknown" if row.canonical_class in RETIRED_CLASSES else row.canonical_class
            if (group_to_split.get(row.group_id) != "train" and row.group_id not in NEW_TRAIN_GROUPS) or canonical == "unknown":
                continue
            with np.load(row.npz_path, allow_pickle=False) as item:
                sequence = item["landmarks"].astype(np.float32)
            sequence = resample_sequence(sequence, getattr(row, "source_fps", 15) or 15)
            if len(sequence) < 24:
                continue
            period = estimate_period(sequence)
            candidate_starts = list(range(0, max(1, len(sequence) - period + 1), period))
            if len(candidate_starts) > 6:
                candidate_starts = [candidate_starts[i] for i in np.linspace(0, len(candidate_starts) - 1, 6, dtype=int)]
            for cycle_index, start in enumerate(candidate_starts):
                end = min(len(sequence), start + period)
                if end - start < 12:
                    continue
                temporal_windows.append(phase_resample(sequence[start:end]))
                temporal_labels.append(canonical)
                temporal_groups.append(row.group_id)
                temporal_clip_ids.append(row.clip_id)
                temporal_sources.append(row.source_dataset)
                temporal_starts.append(start)
                temporal_keys.append(f"phase64|{row.source_dataset}|{row.group_id}|{row.clip_id}|{cycle_index}")

        assert temporal_windows, "No complete-action candidates were built."
        X = np.concatenate([X, np.asarray(temporal_windows, dtype=np.float32)])
        original_labels = np.concatenate([original_labels, np.asarray(temporal_labels, dtype=object)])
        labels = np.concatenate([labels, np.asarray(temporal_labels, dtype=object)])
        groups = np.concatenate([groups, np.asarray(temporal_groups, dtype=object)])
        clip_ids = np.concatenate([clip_ids, np.asarray(temporal_clip_ids, dtype=object)])
        sources = np.concatenate([sources, np.asarray(temporal_sources, dtype=object)])
        starts = np.concatenate([starts, np.asarray(temporal_starts, dtype=np.int64)])
        window_keys = np.concatenate([window_keys, np.asarray(temporal_keys, dtype=object)])
        assigned_split = np.concatenate([assigned_split, np.repeat("train", len(temporal_windows)).astype(object)])

        train_idx = np.flatnonzero(assigned_split == "train")
        val_idx = np.flatnonzero(assigned_split == "validation")
        test_idx = np.flatnonzero(assigned_split == "test")
        assert not (set(groups[train_idx]) & set(groups[val_idx]))
        assert not (set(groups[train_idx]) & set(groups[test_idx]))
        assert not (set(groups[val_idx]) & set(groups[test_idx]))
        assert not (set(groups[train_idx]) & UNREVIEWED_GROUPS)
        assert len(test_idx) == 1971, len(test_idx)
        assert set(window_keys[test_idx]) == set(baseline_predictions.window_key)
        baseline_truth_by_key = dict(zip(baseline_predictions.window_key, baseline_predictions.true_class))
        assert all(baseline_truth_by_key[key] == truth for key, truth in zip(window_keys[test_idx], labels[test_idx])), "Frozen test labels changed."
        print("Base windows:", X.shape, "| train", len(train_idx), "| validation", len(val_idx), "| test", len(test_idx))
        '''
    ),
    md(
        """
        ## Add the 30 RepCount clips with their predeclared folds

        Pose comes from the archived Notebook 37 report (every file is checked against that report's own
        checksums). Windows use Notebook 37's exact rule, so frozen V6-F can be reproduced below.
        """
    ),
    code(
        r'''
        REPCOUNT_ROOT = WORK / "repcount_report"
        if REPCOUNT_ROOT.exists():
            shutil.rmtree(REPCOUNT_ROOT)
        with zipfile.ZipFile(PATHS["repcount_report.zip"]) as archive:
            archive.extractall(REPCOUNT_ROOT)
        REPCOUNT_REPORT = REPCOUNT_ROOT / "report"
        listed = {}
        for line in (REPCOUNT_REPORT / "SHA256SUMS.txt").read_text().splitlines():
            digest, relative = line.split("  ", 1)
            listed[relative] = digest
        for relative, digest in listed.items():
            assert sha256(REPCOUNT_REPORT / relative) == digest, f"Notebook 37 report file changed: {relative}"
        assert not list(REPCOUNT_REPORT.rglob("*.mp4")), "Raw video must not be present."

        folds = pd.read_csv(PATHS["folds.csv"])
        assert len(folds) == 30 and folds.video_id.is_unique
        assert folds.groupby("source_group_id").eval_fold.nunique().max() == 1, "A source group spans folds."
        assert set(folds.eval_fold) == set(range(N_FOLDS))
        for group, members in SHARED_SOURCE_GROUPS.items():
            assert set(folds.loc[folds.source_group_id == group, "video_id"]) == members, group
        assert set(folds.visible_target) <= set(ALL_CLASSES)
        assert (folds.visible_target != "unknown").sum() == 18 and (folds.visible_target == "unknown").sum() == 12


        def resample_window(pose):
            old = np.arange(len(pose), dtype=np.float32)
            new = np.linspace(0, len(pose) - 1, WINDOW, dtype=np.float32)
            flat = pose.reshape(len(pose), -1)
            return np.stack([np.interp(new, old, flat[:, j]) for j in range(flat.shape[1])], 1).reshape(WINDOW, 17, 4).astype(np.float32)


        rep_windows, rep_rows = [], []
        for row in folds.itertuples(index=False):
            relative = f"pose/{row.video_id}.npz"
            assert relative in listed, relative
            with np.load(REPCOUNT_REPORT / relative, allow_pickle=False) as item:
                pose = item["landmarks"].astype(np.float32)
                assert abs(float(item["target_fps"]) - 15.0) < 1e-3
            assert pose.ndim == 3 and pose.shape[1:] == (17, 4) and len(pose) > 0
            if len(pose) < WINDOW:
                clip_starts, clip_windows = [0], [resample_window(pose)]
            else:
                clip_starts = list(range(0, len(pose) - WINDOW + 1, STRIDE))
                if clip_starts[-1] != len(pose) - WINDOW:
                    clip_starts.append(len(pose) - WINDOW)
                clip_windows = [pose[start:start + WINDOW] for start in clip_starts]
            for window_index, (start, window) in enumerate(zip(clip_starts, clip_windows)):
                assert window.shape == (WINDOW, 17, 4) and np.isfinite(window).all()
                rep_windows.append(window)
                rep_rows.append({
                    "video_id": row.video_id, "source_group_id": row.source_group_id,
                    "visible_target": row.visible_target, "eval_fold": int(row.eval_fold),
                    "window_index": window_index, "start_frame": int(start),
                    "window_key": f"repcount|{row.source_group_id}|{row.video_id}|{start}",
                })
        rep_meta = pd.DataFrame(rep_rows)
        rep_start = len(X)
        X = np.concatenate([X, np.asarray(rep_windows, dtype=np.float32)])
        original_labels = np.concatenate([original_labels, rep_meta.visible_target.to_numpy(dtype=object)])
        labels = np.concatenate([labels, rep_meta.visible_target.to_numpy(dtype=object)])
        groups = np.concatenate([groups, ("repcount:" + rep_meta.source_group_id).to_numpy(dtype=object)])
        clip_ids = np.concatenate([clip_ids, rep_meta.video_id.to_numpy(dtype=object)])
        sources = np.concatenate([sources, np.repeat("repcount", len(rep_meta)).astype(object)])
        starts = np.concatenate([starts, rep_meta.start_frame.to_numpy(dtype=np.int64)])
        window_keys = np.concatenate([window_keys, rep_meta.window_key.to_numpy(dtype=object)])
        assigned_split = np.concatenate([assigned_split, np.repeat("repcount", len(rep_meta)).astype(object)])
        repcount_fold = np.full(len(X), -1, dtype=np.int64)
        repcount_fold[rep_start:] = rep_meta.eval_fold.to_numpy()
        rep_idx = np.arange(rep_start, len(X))
        rep_position = {int(index): position for position, index in enumerate(rep_idx)}

        y_gate = (labels != "unknown").astype(np.int64)
        y_exercise = np.asarray([supported_to_id.get(name, -1) for name in labels], dtype=np.int64)
        assert window_keys.size == len(set(window_keys)), "Window keys must be unique."
        assert np.array_equal(train_idx, np.flatnonzero(assigned_split == "train"))
        assert np.array_equal(test_idx, np.flatnonzero(assigned_split == "test"))
        assert not set(groups[rep_idx]) & set(groups[np.r_[train_idx, val_idx, test_idx]])
        print("RepCount windows:", len(rep_idx))
        display(rep_meta.groupby(["eval_fold", "visible_target"]).agg(clips=("video_id", "nunique"), windows=("window_key", "count")))
        '''
    ),
    md(
        """
        ## Sampler, augmentation, and streams (unchanged from Notebook 31)

        Each RepCount source group enters the tempered sampler as its own group, with no extra weight.
        """
    ),
    code(
        r'''
        hard_weight_by_key = dict(zip(hard_positive_frame.window_key, hard_positive_frame.recommended_sample_weight))
        hard_positive_weights = np.asarray([float(hard_weight_by_key.get(key, 1.0)) for key in window_keys], dtype=np.float64)
        hard_positive_weights[labels == "unknown"] = 1.0
        assert not (set(window_keys[val_idx]) & set(hard_weight_by_key))
        assert not (set(window_keys[test_idx]) & set(hard_weight_by_key))
        assert not (set(window_keys[rep_idx]) & set(hard_weight_by_key))
        gate_hierarchy = np.where(y_gate == 1, "supported", "unknown")


        def hierarchical_window_weights(indices, hierarchy_labels, extra_weights=None):
            table = pd.DataFrame({"index": indices, "hierarchy_label": hierarchy_labels[indices], "group": groups[indices]})
            class_count = table["hierarchy_label"].nunique()
            group_sizes = table.groupby(["hierarchy_label", "group"])["index"].transform("count").astype(float)
            table["group_mass"] = group_sizes.pow(GROUP_TEMPERATURE)
            class_group_mass = table.drop_duplicates(["hierarchy_label", "group"]).groupby("hierarchy_label")["group_mass"].sum()
            table["extra_weight"] = 1.0 if extra_weights is None else extra_weights[table["index"].to_numpy()]
            table["pair_extra_total"] = table.groupby(["hierarchy_label", "group"])["extra_weight"].transform("sum")
            weights = (
                1.0 / class_count
                * table["group_mass"].to_numpy() / class_group_mass.loc[table["hierarchy_label"]].to_numpy()
                * table["extra_weight"].to_numpy() / table["pair_extra_total"].to_numpy()
            )
            return weights / weights.mean()


        def dry_run_subset(indices, size, seed):
            if not DRY_RUN or len(indices) <= size:
                return indices
            return np.sort(np.random.default_rng(seed).choice(indices, size, replace=False))


        LEFT_RIGHT_PAIRS = [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10), (11, 12), (13, 14), (15, 16)]


        def augment_pose_window(sample):
            sample = sample.copy()
            config = AUGMENTATION_CONFIG
            if np.random.random() < config["horizontal_flip_probability"]:
                sample[:, :, 0] *= -1.0
                for left, right in LEFT_RIGHT_PAIRS:
                    sample[:, [left, right], :] = sample[:, [right, left], :]
            if np.random.random() < config["rotation_probability"]:
                radians = np.deg2rad(np.random.uniform(-config["max_rotation_degrees"], config["max_rotation_degrees"]))
                cosine, sine = np.cos(radians), np.sin(radians)
                x = sample[:, :, 0].copy()
                y = sample[:, :, 1].copy()
                sample[:, :, 0] = cosine * x - sine * y
                sample[:, :, 1] = sine * x + cosine * y
            if np.random.random() < config["speed_probability"]:
                speed = np.random.uniform(*config["speed_range"])
                center = (WINDOW - 1) / 2.0
                positions = (np.arange(WINDOW) - center) * speed + center
                flat = sample.reshape(WINDOW, -1)
                flat = np.stack([np.interp(positions, np.arange(WINDOW), flat[:, column]) for column in range(flat.shape[1])], axis=1)
                sample = flat.reshape(WINDOW, 17, 4).astype(np.float32)
            if np.random.random() < config["frame_drop_probability"]:
                fraction = np.random.uniform(*config["frame_drop_fraction_range"])
                count = max(1, int(round(WINDOW * fraction)))
                dropped = np.random.choice(np.arange(1, WINDOW), size=count, replace=False)
                sample[dropped] = sample[dropped - 1]
            if np.random.random() < config["coordinate_noise_probability"]:
                sample[:, :, :2] += np.random.normal(0, config["coordinate_noise_std"], sample[:, :, :2].shape).astype(np.float32)
            return sample.astype(np.float32)


        BONE_EDGES = [(5, 6), (5, 7), (7, 9), (6, 8), (8, 10), (5, 11), (6, 12), (11, 12), (11, 13), (13, 15), (12, 14), (14, 16)]
        ANGLE_TRIPLETS = [(5, 7, 9), (6, 8, 10), (7, 5, 11), (8, 6, 12), (5, 11, 13), (6, 12, 14), (11, 13, 15), (12, 14, 16)]
        FEATURE_DIM = 100


        def pose_to_features(sample):
            xy = sample[:, :, :2].astype(np.float32)
            velocity = np.zeros_like(xy)
            velocity[1:] = xy[1:] - xy[:-1]
            bones = np.stack([xy[:, child] - xy[:, parent] for parent, child in BONE_EDGES], axis=1)
            angles = []
            for first, center, last in ANGLE_TRIPLETS:
                first_vector = xy[:, first] - xy[:, center]
                last_vector = xy[:, last] - xy[:, center]
                denominator = np.linalg.norm(first_vector, axis=1) * np.linalg.norm(last_vector, axis=1)
                cosine = np.sum(first_vector * last_vector, axis=1) / np.maximum(denominator, 1e-6)
                angles.append(np.arccos(np.clip(cosine, -1.0, 1.0)) / np.pi)
            features = np.concatenate([xy.reshape(WINDOW, -1), velocity.reshape(WINDOW, -1), bones.reshape(WINDOW, -1), np.stack(angles, axis=1)], axis=1).astype(np.float32)
            assert features.shape == (WINDOW, FEATURE_DIM) and np.isfinite(features).all()
            return features


        def pose_to_stream(sample, stream):
            xy = sample[:, :, :2].astype(np.float32)
            if stream == "joint":
                return xy.reshape(WINDOW, -1)
            if stream == "velocity":
                velocity = np.zeros_like(xy)
                velocity[1:] = xy[1:] - xy[:-1]
                return velocity.reshape(WINDOW, -1)
            if stream == "bone":
                return np.stack([xy[:, child] - xy[:, parent] for parent, child in BONE_EDGES], axis=1).reshape(WINDOW, -1)
            raise ValueError(stream)


        class StreamDataset(Dataset):
            def __init__(self, indices, training, stream):
                self.indices, self.training, self.stream = np.asarray(indices), training, stream

            def __len__(self):
                return len(self.indices)

            def __getitem__(self, item):
                actual = self.indices[item]
                sample = X[actual].copy()
                if self.training:
                    sample = augment_pose_window(sample)
                return torch.from_numpy(pose_to_stream(sample, self.stream).T), torch.tensor(y_gate[actual], dtype=torch.long)


        def make_stream_loaders(stream, seed, train_indices, train_weights, validation_indices):
            generator = torch.Generator().manual_seed(seed)
            sampler = WeightedRandomSampler(torch.as_tensor(train_weights, dtype=torch.double), len(train_weights), replacement=True, generator=generator)
            return (
                DataLoader(StreamDataset(train_indices, True, stream), batch_size=BATCH_SIZE, sampler=sampler),
                DataLoader(StreamDataset(validation_indices, False, stream), batch_size=BATCH_SIZE, shuffle=False),
            )


        fold_train_indices, fold_train_weights, sampler_rows = {}, {}, []
        for fold in range(N_FOLDS):
            indices = np.concatenate([dry_run_subset(train_idx, DRY_RUN_TRAIN_WINDOWS, fold), rep_idx[repcount_fold[rep_idx] != fold]])
            weights = hierarchical_window_weights(indices, gate_hierarchy, hard_positive_weights)
            assert not set(groups[indices]) & set(groups[rep_idx[repcount_fold[rep_idx] == fold]]), "Scored fold leaked into training."
            assert not set(groups[indices]) & set(groups[val_idx]) and not set(groups[indices]) & set(groups[test_idx])
            fold_train_indices[fold], fold_train_weights[fold] = indices, weights
            is_rep = sources[indices] == "repcount"
            for target in ("supported", "unknown"):
                mask = gate_hierarchy[indices] == target
                sampler_rows.append({
                    "eval_fold": fold, "gate_target": target,
                    "windows": int(mask.sum()), "repcount_windows": int((mask & is_rep).sum()),
                    "repcount_groups": int(len(set(groups[indices][mask & is_rep]))),
                    "sampler_mass": float(weights[mask].sum() / weights.sum()),
                    "repcount_sampler_mass": float(weights[mask & is_rep].sum() / weights.sum()),
                })
        sampler_audit = pd.DataFrame(sampler_rows)
        display(sampler_audit)
        validation_indices = dry_run_subset(val_idx, DRY_RUN_VALIDATION_WINDOWS, 99)
        '''
    ),
    md(
        """
        ## Frozen classifier and Notebook 31's gate trainer
        """
    ),
    code(
        r'''
        class TemporalBlock(nn.Module):
            def __init__(self, in_channels, out_channels, dilation, dropout=0.2):
                super().__init__()
                padding = dilation
                self.net = nn.Sequential(
                    nn.Conv1d(in_channels, out_channels, 3, padding=padding, dilation=dilation),
                    nn.BatchNorm1d(out_channels), nn.ReLU(), nn.Dropout(dropout),
                    nn.Conv1d(out_channels, out_channels, 3, padding=padding, dilation=dilation),
                    nn.BatchNorm1d(out_channels), nn.ReLU(), nn.Dropout(dropout),
                )
                self.residual = nn.Conv1d(in_channels, out_channels, 1) if in_channels != out_channels else nn.Identity()

            def forward(self, x):
                return torch.relu(self.net(x) + self.residual(x))


        class SmallTCN(nn.Module):
            def __init__(self, input_features, num_classes):
                super().__init__()
                blocks, current = [], input_features
                for level, output in enumerate([64, 96, 128, 128]):
                    blocks.append(TemporalBlock(current, output, dilation=2 ** level))
                    current = output
                self.features = nn.Sequential(*blocks)
                self.classifier = nn.Linear(current, num_classes)

            def forward(self, x):
                return self.classifier(self.features(x).mean(dim=-1))


        checkpoint = torch.load(PATHS["temporal_checkpoint.pt"], map_location=DEVICE, weights_only=False)
        frozen_exercise_model = SmallTCN(FEATURE_DIM, len(SUPPORTED_CLASSES)).to(DEVICE)
        frozen_exercise_model.load_state_dict(checkpoint["exercise_state_dict"])
        frozen_exercise_model.eval()
        for parameter in frozen_exercise_model.parameters():
            parameter.requires_grad = False


        def load_gate(path, stream):
            gate_checkpoint = torch.load(path, map_location=DEVICE, weights_only=False)
            assert gate_checkpoint["stream"] == stream and int(gate_checkpoint["input_features"]) == STREAMS[stream]
            model = SmallTCN(STREAMS[stream], 2).to(DEVICE)
            model.load_state_dict(gate_checkpoint["state_dict"])
            return model.eval()


        def train_gate(stream, loaders, seed, tag):
            seed_everything(seed)
            model = SmallTCN(STREAMS[stream], 2).to(DEVICE)
            criterion = nn.CrossEntropyLoss()
            optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", patience=3, factor=0.5)
            best_path = WORK / f"best_{tag}_{seed}_{stream}.pt"
            best_f1, stale, history = -1.0, 0, []

            def epoch(loader, training):
                model.train(training)
                losses, truth, prediction = [], [], []
                with (torch.enable_grad() if training else torch.no_grad()):
                    for features, targets in loader:
                        features, targets = features.to(DEVICE), targets.to(DEVICE)
                        if training:
                            optimizer.zero_grad(set_to_none=True)
                        logits = model(features)
                        loss = criterion(logits, targets)
                        if training:
                            loss.backward()
                            optimizer.step()
                        losses.append(loss.item() * len(targets))
                        truth.extend(targets.cpu().numpy())
                        prediction.extend(logits.argmax(1).cpu().numpy())
                return sum(losses) / len(truth), f1_score(truth, prediction, average="macro", zero_division=0)

            for epoch_number in range(1, MAX_EPOCHS + 1):
                train_loss, train_f1 = epoch(loaders[0], True)
                val_loss, val_f1 = epoch(loaders[1], False)
                scheduler.step(val_f1)
                history.append({"tag": tag, "seed": seed, "stream": stream, "epoch": epoch_number, "train_loss": train_loss,
                                "train_macro_f1": train_f1, "val_loss": val_loss, "val_macro_f1": val_f1})
                print(tag, seed, stream, epoch_number, round(train_f1, 3), round(val_f1, 3))
                if val_f1 > best_f1 + 1e-4:
                    best_f1, stale = val_f1, 0
                    torch.save(model.state_dict(), best_path)
                else:
                    stale += 1
                    if stale >= PATIENCE:
                        break
            model.load_state_dict(torch.load(best_path, map_location=DEVICE))
            return model.eval(), history, best_f1
        '''
    ),
    md(
        """
        ## Fixed scoring

        Window gate score = mean of the three stream probabilities. A clip uses the Notebook 37 rule:
        mean window gate score against `0.65`, and mean window class probabilities for the exercise.
        """
    ),
    code(
        r'''
        def infer_stream(model, indices, stream, batch_size=256):
            probabilities = []
            with torch.no_grad():
                for start in range(0, len(indices), batch_size):
                    batch = np.stack([pose_to_stream(X[index], stream) for index in indices[start:start + batch_size]]).transpose(0, 2, 1)
                    probabilities.append(model(torch.from_numpy(batch).to(DEVICE)).softmax(1).cpu().numpy())
            return np.concatenate(probabilities)[:, 1]


        def fused_score(gates, indices):
            return np.stack([infer_stream(gates[stream], indices, stream) for stream in STREAMS], axis=1).mean(axis=1)


        def exercise_probabilities(indices, batch_size=256):
            probabilities = []
            with torch.no_grad():
                for start in range(0, len(indices), batch_size):
                    batch = np.stack([pose_to_features(X[index]) for index in indices[start:start + batch_size]]).transpose(0, 2, 1)
                    probabilities.append(frozen_exercise_model(torch.from_numpy(batch).to(DEVICE)).softmax(1).cpu().numpy())
            return np.concatenate(probabilities)


        test_exercise_prediction = exercise_probabilities(test_idx).argmax(1)
        rep_exercise_probability = exercise_probabilities(rep_idx)


        def internal_test_metrics(scores):
            prediction = np.asarray([SUPPORTED_CLASSES[c] if s >= FIXED_THRESHOLD else "unknown" for s, c in zip(scores, test_exercise_prediction)])
            truth = labels[test_idx].astype(str)
            unknown = truth == "unknown"
            return {
                "end_to_end_macro_f1": float(f1_score(truth, prediction, labels=ALL_CLASSES, average="macro", zero_division=0)),
                "end_to_end_accuracy": float(accuracy_score(truth, prediction)),
                "end_to_end_balanced_accuracy": float(balanced_accuracy_score(truth, prediction)),
                "unknown_recall": float((prediction[unknown] == "unknown").mean()),
                "supported_accuracy": float((prediction[~unknown] == truth[~unknown]).mean()),
            }


        def error_type(target, prediction):
            if prediction == target:
                return "correct"
            if target != "unknown" and prediction == "unknown":
                return "gate_false_unknown"
            if target == "unknown":
                return "gate_false_accept"
            return "wrong_supported_class"


        def clip_table(indices, scores):
            positions = np.asarray([rep_position[int(index)] for index in indices])
            video = clip_ids[indices]
            rows = []
            for video_id in pd.unique(video):
                mask = video == video_id
                oracle = SUPPORTED_CLASSES[int(rep_exercise_probability[positions[mask]].mean(axis=0).argmax())]
                gate = float(scores[mask].mean())
                rows.append({"video_id": video_id, "window_count": int(mask.sum()), "gate_supported_probability": gate,
                             "oracle_exercise": oracle, "prediction": oracle if gate >= FIXED_THRESHOLD else "unknown"})
            table = pd.DataFrame(rows).merge(folds[["video_id", "source_group_id", "visible_target", "visible_variant", "eval_fold"]], on="video_id", validate="one_to_one")
            table["error_type"] = [error_type(t, p) for t, p in zip(table.visible_target, table.prediction)]
            return table


        def clip_counts(table):
            assert len(table) == 30 and table.video_id.is_unique, "Out-of-fold table must cover all 30 clips once."
            supported = table.visible_target != "unknown"
            counts = {
                "clips": int(len(table)),
                "end_to_end_correct": int((table.error_type == "correct").sum()),
                "supported_clips": int(supported.sum()),
                "supported_correct": int((supported & (table.error_type == "correct")).sum()),
                "supported_false_unknown": int((table.error_type == "gate_false_unknown").sum()),
                "wrong_supported_class": int((table.error_type == "wrong_supported_class").sum()),
                "oracle_classifier_correct": int((table.oracle_exercise[supported] == table.visible_target[supported]).sum()),
                "unknown_clips": int((~supported).sum()),
                "unknown_rejected": int((~supported & (table.prediction == "unknown")).sum()),
                "gate_false_accept": int((table.error_type == "gate_false_accept").sum()),
            }
            for target in sorted(set(table.visible_target)):
                mask = table.visible_target == target
                counts[f"correct__{target}"] = int((mask & (table.error_type == "correct")).sum())
            assert counts["supported_clips"] == 18 and counts["unknown_clips"] == 12
            return counts
        '''
    ),
    md(
        """
        ## Parity checks before any training

        1. Frozen V6-F must reproduce Notebook 37's 30 clip predictions.
        2. Notebook 31's archived gates must reproduce Notebook 31's internal-test Macro F1.

        If either fails, the pipeline differs from the archived runs and the notebook stops.
        """
    ),
    code(
        r'''
        v6f_gates = {stream: load_gate(PATHS[f"v6f_{stream}_gate.pt"], stream) for stream in STREAMS}
        v6f_clips = clip_table(rep_idx, fused_score(v6f_gates, rep_idx))
        nb37 = pd.read_csv(REPCOUNT_REPORT / "video_diagnostics.csv").set_index("video_id")
        parity = v6f_clips.set_index("video_id").join(nb37[["frozen_v6f_prediction", "gate_supported_probability"]], rsuffix="_nb37")
        parity["gate_abs_diff"] = (parity.gate_supported_probability - parity.gate_supported_probability_nb37).abs()
        assert (parity.prediction == parity.frozen_v6f_prediction).all(), parity[parity.prediction != parity.frozen_v6f_prediction]
        assert parity.gate_abs_diff.max() < 1e-3, parity.gate_abs_diff.max()
        assert (folds.set_index("video_id").frozen_v6f_prediction == parity.prediction).all()
        v6f_counts = clip_counts(v6f_clips)
        assert v6f_counts["end_to_end_correct"] == 11 and v6f_counts["supported_false_unknown"] == 8
        print("V6-F parity passed; max gate difference", float(parity.gate_abs_diff.max()))
        print(v6f_counts)

        control_rows, control_tables, control_internal = [], [], []
        for seed in CONTROL_SEEDS:
            gates = {stream: load_gate(PATHS[f"control_seed_{seed}_{stream}_gate.pt"], stream) for stream in STREAMS}
            metrics = internal_test_metrics(fused_score(gates, test_idx))
            reference = float(nb31_seed_metrics.loc[nb31_seed_metrics.run_seed == seed, "test_end_to_end_macro_f1"].iloc[0])
            assert abs(metrics["end_to_end_macro_f1"] - reference) < 0.003, (seed, metrics["end_to_end_macro_f1"], reference)
            table = clip_table(rep_idx, fused_score(gates, rep_idx)).assign(arm="control", seed=seed)
            control_tables.append(table)
            control_rows.append({"arm": "control", "seed": seed, **clip_counts(table)})
            control_internal.append({"arm": "control", "seed": seed, "eval_fold": "", **metrics, "nb31_reference_macro_f1": reference})
            del gates
        control_counts = pd.DataFrame(control_rows)
        print("Notebook 31 control parity passed.")
        display(control_counts)
        '''
    ),
    md(
        """
        ## Treatment: retrain the gates once per fold and seed

        3 folds x 3 seeds x 3 streams. Training seeds match Notebook 31 (`run_seed + 100 + stream offset`).
        This is the long cell.
        """
    ),
    code(
        r'''
        REPORT = WORK / "calorie_repcount_gate_rotation_v1_report"
        if REPORT.exists():
            shutil.rmtree(REPORT)
        (REPORT / "gates").mkdir(parents=True)

        treatment_tables, treatment_internal, history_rows, stream_rows, window_frames = [], [], [], [], []
        for seed in RUN_SEEDS:
            for fold in range(N_FOLDS):
                gates = {}
                for offset, stream in enumerate(STREAMS):
                    training_seed = seed + 100 + offset
                    loaders = make_stream_loaders(stream, training_seed, fold_train_indices[fold], fold_train_weights[fold], validation_indices)
                    model, history, best_f1 = train_gate(stream, loaders, training_seed, f"fold{fold}")
                    gates[stream] = model
                    history_rows.extend({**row, "eval_fold": fold} for row in history)
                    stream_rows.append({"seed": seed, "eval_fold": fold, "stream": stream, "training_seed": training_seed, "best_validation_macro_f1": best_f1})
                    torch.save({"state_dict": model.state_dict(), "stream": stream, "input_features": STREAMS[stream], "run_seed": seed,
                                "training_seed": training_seed, "eval_fold": fold, "fusion": FIXED_FUSION, "threshold": FIXED_THRESHOLD},
                               REPORT / "gates" / f"seed_{seed}_fold_{fold}_{stream}_gate.pt")
                scored = rep_idx[repcount_fold[rep_idx] == fold]
                scores = fused_score(gates, scored)
                treatment_tables.append(clip_table(scored, scores).assign(arm="treatment", seed=seed))
                window_frames.append(pd.DataFrame({"seed": seed, "eval_fold": fold, "window_key": window_keys[scored],
                                                   "video_id": clip_ids[scored], "fused_supported_score": scores}))
                treatment_internal.append({"arm": "treatment", "seed": seed, "eval_fold": fold, **internal_test_metrics(fused_score(gates, test_idx))})
                del gates
                if DEVICE.type == "cuda":
                    torch.cuda.empty_cache()
        '''
    ),
    md(
        """
        ## Out-of-fold results and the predeclared stopping rule
        """
    ),
    code(
        r'''
        treatment_oof = pd.concat(treatment_tables, ignore_index=True)
        treatment_rows = [{"arm": "treatment", "seed": seed, **clip_counts(treatment_oof[treatment_oof.seed == seed])} for seed in RUN_SEEDS]
        treatment_counts = pd.DataFrame(treatment_rows)
        internal = pd.DataFrame(control_internal + treatment_internal)


        def median(frame, column):
            return float(np.median(frame[column].to_numpy(dtype=float)))


        summary = {
            "v6f_frozen": v6f_counts,
            "control_median": {key: median(control_counts, key) for key in control_counts.columns if key not in ("arm", "seed")},
            "treatment_median": {key: median(treatment_counts, key) for key in treatment_counts.columns if key not in ("arm", "seed")},
            "control_internal_mean_macro_f1": float(internal[internal.arm == "control"].end_to_end_macro_f1.mean()),
            "treatment_internal_mean_macro_f1": float(internal[internal.arm == "treatment"].end_to_end_macro_f1.mean()),
        }
        t, c = summary["treatment_median"], summary["control_median"]
        criteria = {
            "false_unknown_at_most_5_of_18": t["supported_false_unknown"] <= 5,
            "false_unknown_below_control_median": t["supported_false_unknown"] < c["supported_false_unknown"],
            "unknown_rejection_at_least_control_median": t["unknown_rejected"] >= c["unknown_rejected"],
            "unknown_rejection_at_least_5_of_12": t["unknown_rejected"] >= 5,
            "internal_macro_f1_within_1pp_of_control": summary["treatment_internal_mean_macro_f1"] >= summary["control_internal_mean_macro_f1"] - 0.01,
        }
        if DRY_RUN:
            verdict = "dry_run_not_a_result"
        else:
            verdict = "data_effect_supported" if all(criteria.values()) else "data_effect_not_supported"
        stopping_rule = {
            "verdict": verdict, "criteria": {k: bool(v) for k, v in criteria.items()},
            "rule": "All criteria must hold, using seed medians of out-of-fold clip counts. One run; no tuning follows.",
            "production_promotion_allowed": False,
        }
        print(json.dumps(stopping_rule, indent=2))
        display(pd.concat([control_counts, treatment_counts], ignore_index=True))
        display(internal)

        run_metadata = {
            "notebook": "39_colab_repcount_gate_rotation.ipynb",
            "experiment": "repcount_gate_rotation_v1",
            "design": "ml/data/repcount_development_v1/gate_rotation_v1/DESIGN.md",
            "training_commit": TRAINING_COMMIT, "design_commit": DESIGN_COMMIT,
            "dry_run": DRY_RUN, "device": str(DEVICE), "run_seeds": RUN_SEEDS, "control_seeds": CONTROL_SEEDS,
            "max_epochs": MAX_EPOCHS, "patience": PATIENCE, "fixed_fusion": FIXED_FUSION, "fixed_threshold": FIXED_THRESHOLD,
            "threshold_changed": False, "classifier_changed": False, "locked_benchmark_read": False,
            "repcount_used_for_early_stopping": False, "internal_test_used_for_selection": False,
            "evidence_rows_training_allowed_changed": False, "production_promoted": False,
            "input_hashes": {name: sha256(path) for name, path in PATHS.items()},
        }
        (REPORT / "run_metadata.json").write_text(json.dumps(run_metadata, indent=2) + "\n")
        (REPORT / "metrics.json").write_text(json.dumps({"summary": summary, "stopping_rule": stopping_rule}, indent=2) + "\n")
        (REPORT / "stopping_rule.json").write_text(json.dumps(stopping_rule, indent=2) + "\n")
        pd.concat([control_counts, treatment_counts], ignore_index=True).to_csv(REPORT / "clip_counts_by_seed.csv", index=False)
        pd.concat(control_tables, ignore_index=True).to_csv(REPORT / "control_clip_predictions.csv", index=False)
        treatment_oof.to_csv(REPORT / "treatment_oof_clip_predictions.csv", index=False)
        v6f_clips.to_csv(REPORT / "v6f_frozen_clip_predictions.csv", index=False)
        parity.reset_index().to_csv(REPORT / "v6f_parity_check.csv", index=False)
        internal.to_csv(REPORT / "internal_test_metrics.csv", index=False)
        pd.concat(window_frames, ignore_index=True).to_csv(REPORT / "treatment_window_scores.csv", index=False)
        sampler_audit.to_csv(REPORT / "sampler_audit.csv", index=False)
        pd.DataFrame(history_rows).to_csv(REPORT / "training_history.csv", index=False)
        pd.DataFrame(stream_rows).to_csv(REPORT / "stream_validation.csv", index=False)
        shutil.copy2(PATHS["folds.csv"], REPORT / "folds.csv")
        (REPORT / "README.md").write_text(
            "# cALorie RepCount gate rotation v1\n\n"
            + ("DRY RUN: one epoch on a subsample. Not a result.\n\n" if DRY_RUN else "")
            + "Gate-only retraining with RepCount clips outside each scored source-group fold. Classifier, fusion, "
            "and threshold 0.65 were frozen. Control = Notebook 31 archived gates. The locked creator benchmark "
            "was not read. Non-promotable development evidence. Verdict: " + verdict + "\n"
        )
        checksum_lines = [f"{sha256(path)}  {path.relative_to(REPORT)}" for path in sorted(p for p in REPORT.rglob("*") if p.is_file())]
        (REPORT / "SHA256SUMS.txt").write_text("\n".join(checksum_lines) + "\n")
        zip_name = "calorie_repcount_gate_rotation_v1_report" + ("_DRYRUN" if DRY_RUN else "")
        zip_path = Path(shutil.make_archive(str(WORK / zip_name), "zip", root_dir=REPORT))
        print("Created:", zip_path, round(zip_path.stat().st_size / 1e6, 1), "MB")
        try:
            from google.colab import files
            files.download(str(zip_path))
        except ImportError:
            print("Not on Colab; ZIP left at", zip_path)
        '''
    ),
    md(
        """
        ## Return the report

        Send back `calorie_repcount_gate_rotation_v1_report.zip` unchanged. Do not rerun because of the
        verdict. A crash or code bug is the only reason to run again.
        """
    ),
]

notebook = {
    "cells": cells,
    "metadata": {
        "accelerator": "GPU",
        "colab": {"name": OUTPUT.name, "provenance": [], "gpuType": "T4"},
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}
OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")
print(OUTPUT)
