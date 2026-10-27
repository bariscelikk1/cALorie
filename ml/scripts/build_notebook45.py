#!/usr/bin/env python3
"""Build Notebook 45: long-video training v1 (PLAN.md section 3).

Notebook 43 (the v2 recipe) with one change: the 11 long-video train videos'
continuous windows join the classifier and gate pools. Control is the frozen
v2 seeds. Decision on the 5 dev videos with the full-session scorer and the
predeclared pass rule; the locked long-video test is never an input.
"""

import hashlib
import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "ml/notebooks/43_repcount_training_v2_stage_a.ipynb"
OUTPUT = ROOT / "ml/notebooks/45_long_video_training_v1.ipynb"
LONG_COMMIT = "93395df5df3b38eaf1c17680477c4ab8056e042d"
DATA = "ml/data/long_video_train_v1"


def sha(relative):
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


roles = [line.split(",")[:3] for line in (ROOT / DATA / "roles.csv").read_text().splitlines()[1:]]
VIDEOS = {vid: role for vid, _, role in roles}
assert sum(r == "train" for r in VIDEOS.values()) == 11 and sum(r == "dev" for r in VIDEOS.values()) == 5
LONG_INPUTS = {
    "long_roles.csv": f"{DATA}/roles.csv",
    "score_long_video_test_v1.py": "ml/scripts/score_long_video_test_v1.py",
    "v2_stage_a.zip": "ml/artifacts/repcount_training_v2_stage_a/calorie_repcount_training_v2_stage_a_report.zip",
    "dev_diagnosis_metrics.csv": "ml/artifacts/long_video_train_v1/dev_diagnosis_v1/dev_metrics_by_model_video.csv",
    **{f"long_{vid}.zip": f"ml/artifacts/long_video_train_v1/long_video_train_v1_{vid}.zip" for vid in VIDEOS},
    **{f"long_ann_{vid}.csv": f"{DATA}/annotations/{vid}.csv" for vid in VIDEOS},
}
assert not any("long_video_test_v1" in p and "score_" not in p for p in LONG_INPUTS.values()), "Locked test must not be an input."


def code(source):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": dedent(source).lstrip().splitlines(True)}


def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": dedent(source).lstrip().splitlines(True)}


def patched(source, replacements):
    for old, new in replacements:
        assert source.count(old) == 1, (old[:70], source.count(old))
        source = source.replace(old, new)
    return code(source)


nb43 = ["".join(c["source"]) for c in json.loads(SOURCE.read_text())["cells"]]

config = patched(nb43[2], [
    ('STAGE = "A"  # dev decision only; the sealed test is never loaded here\n',
     'STAGE = "long_video_dev"  # dev decision only; no sealed or locked test is loaded here\n'
     "LONG_LABEL_SHARE, LONG_DETECTED_SHARE = 0.75, 0.5  # PLAN.md section 3 details\n"
     "DRY_RUN_LONG_WINDOWS_PER_VIDEO = 60\n"),
])

long_lines = "".join(f'    "{n}": (LONG_COMMIT, "{p}", "{sha(p)}"),\n' for n, p in LONG_INPUTS.items())
inputs = patched(nb43[4], [
    ('ROLES_COMMIT = "24ed98d0dbc666510ee724acfa63186dad066710"\n',
     f'ROLES_COMMIT = "24ed98d0dbc666510ee724acfa63186dad066710"\nLONG_COMMIT = "{LONG_COMMIT}"\n'),
    ('INPUTS = {\n    # name: (commit, repository path, sha256)\n',
     "INPUTS = {\n    # name: (commit, repository path, sha256)\n" + long_lines),
    ('assert not any("youtube_creator_benchmark" in path for _, path, _ in INPUTS.values()), "Locked benchmark must not be an input."\n',
     'assert not any("youtube_creator_benchmark" in path for _, path, _ in INPUTS.values()), "Locked benchmark must not be an input."\n'
     'assert not any(path.startswith("ml/data/long_video_test_v1") or "artifacts/long_video_test_v1" in path for _, path, _ in INPUTS.values()), "Locked long-video test must not be an input."\n'),
])

long_video = code(r'''
    import importlib.util
    import io
    spec = importlib.util.spec_from_file_location("lvscore", PATHS["score_long_video_test_v1.py"])
    lvscore = importlib.util.module_from_spec(spec); spec.loader.exec_module(lvscore)
    assert lvscore.THRESHOLD == FIXED_THRESHOLD and lvscore.SUPPORTED == SUPPORTED_CLASSES

    LONG_ROLES = pd.read_csv(PATHS["long_roles.csv"])
    LONG_TRAIN = sorted(LONG_ROLES.loc[LONG_ROLES.role == "train", "video_id"])
    LONG_DEV = sorted(LONG_ROLES.loc[LONG_ROLES.role == "dev", "video_id"])
    assert len(LONG_TRAIN) == 11 and len(LONG_DEV) == 5 and not set(LONG_TRAIN) & set(LONG_DEV)
    assert not set(LONG_ROLES.channel[LONG_ROLES.role == "train"]) & set(LONG_ROLES.channel[LONG_ROLES.role == "dev"]), "A channel spans roles."


    def long_pose(vid):
        with zipfile.ZipFile(PATHS[f"long_{vid}.zip"]) as archive:
            listed = dict(line.split("  ", 1)[::-1] for line in archive.read(f"{vid}/SHA256SUMS.txt").decode().splitlines())
            payload = archive.read(f"{vid}/pose.npz")
        assert hashlib.sha256(payload).hexdigest() == listed["pose.npz"], f"Checksum failed: {vid}"
        with np.load(io.BytesIO(payload), allow_pickle=False) as item:
            assert abs(float(item["target_fps"]) - 15.0) < 1e-3
            return item["landmarks"].astype(np.float32), item["detected"].astype(bool)


    def long_annotation(vid):
        ann = pd.read_csv(PATHS[f"long_ann_{vid}.csv"]).sort_values("start_s").reset_index(drop=True)
        assert set(ann.review_status) <= {"reviewed", "adjudicated"} and not ann.needs_second_review.astype(str).str.lower().eq("true").any()
        return ann


    long_windows, long_rows, long_audit = [], [], []
    for vid in LONG_TRAIN:
        pose, detected = long_pose(vid)
        ann = long_annotation(vid)
        frame_label, _, _ = lvscore.truth_at(np.arange(len(pose)) / 15.0, ann)
        kept = dropped_mixed = dropped_pose = 0
        starts_ = list(range(0, len(pose) - WINDOW + 1, STRIDE))
        if DRY_RUN:
            starts_ = starts_[::max(1, len(starts_) // DRY_RUN_LONG_WINDOWS_PER_VIDEO)]
        for s in starts_:
            values, counts = np.unique(frame_label[s:s + WINDOW], return_counts=True)
            if counts.max() < LONG_LABEL_SHARE * WINDOW:
                dropped_mixed += 1; continue
            if detected[s:s + WINDOW].mean() < LONG_DETECTED_SHARE:
                dropped_pose += 1; continue
            long_windows.append(pose[s:s + WINDOW]); long_rows.append((vid, values[counts.argmax()], s)); kept += 1
        long_audit.append({"video_id": vid, "windows_kept": kept, "dropped_mixed_label": dropped_mixed, "dropped_low_pose": dropped_pose})
    long_meta = pd.DataFrame(long_rows, columns=["video_id", "label", "start"])
    assert set(long_meta.label) <= set(ALL_CLASSES)
    X = np.concatenate([X, np.asarray(long_windows, dtype=np.float32)])
    original_labels = np.concatenate([original_labels, long_meta.label.to_numpy(dtype=object)])
    labels = np.concatenate([labels, long_meta.label.to_numpy(dtype=object)])
    groups = np.concatenate([groups, ("longvideo:" + long_meta.video_id).to_numpy(dtype=object)])
    clip_ids = np.concatenate([clip_ids, long_meta.video_id.to_numpy(dtype=object)])
    sources = np.concatenate([sources, np.repeat("long_video", len(long_meta)).astype(object)])
    starts = np.concatenate([starts, long_meta.start.to_numpy(dtype=np.int64)])
    window_keys = np.concatenate([window_keys, ("longvideo|" + long_meta.video_id + "|" + long_meta.start.astype(str)).to_numpy(dtype=object)])
    assigned_split = np.concatenate([assigned_split, np.repeat("long_train", len(long_meta)).astype(object)])
    y_gate = (labels != "unknown").astype(np.int64)
    y_exercise = np.asarray([supported_to_id.get(name, -1) for name in labels], dtype=np.int64)
    long_train_idx = np.flatnonzero(assigned_split == "long_train")
    assert window_keys.size == len(set(window_keys))
    assert not set(clip_ids[long_train_idx]) & set(LONG_DEV)
    assert not set(groups[long_train_idx]) & set(groups[np.r_[train_idx, val_idx, test_idx, rep_train_idx, dev_idx]])
    long_audit = pd.DataFrame(long_audit)
    display(long_audit)
    display(long_meta.groupby("label").size().rename("windows").to_frame())
    ''')

sampler = patched(nb43[10], [
    ("gate_train = np.concatenate([dry_run_subset(train_idx, DRY_RUN_TRAIN_WINDOWS, 0), rep_train_idx])\n",
     "gate_train = np.concatenate([dry_run_subset(train_idx, DRY_RUN_TRAIN_WINDOWS, 0), rep_train_idx, long_train_idx])  # the one change\n"),
    ('    rep = sources[idx] == "repcount"\n    for target in sorted(set(hierarchy[idx])):\n',
     '    rep, longv = sources[idx] == "repcount", sources[idx] == "long_video"\n    for target in sorted(set(hierarchy[idx])):\n'),
    ('"repcount_sampler_mass": float(w[m & rep].sum() / w.sum())})\n',
     '"repcount_sampler_mass": float(w[m & rep].sum() / w.sum()),\n'
     '                           "long_video_windows": int((m & longv).sum()), "long_video_sampler_mass": float(w[m & longv].sum() / w.sum())})\n'),
])

control = code(r'''
    def build_arm(classifier_state, gate_states):
        cls = SmallTCN(FEATURE_DIM, len(SUPPORTED_CLASSES)).to(DEVICE); cls.load_state_dict(classifier_state); cls.eval()
        gates = {}
        for s in STREAMS:
            g = SmallTCN(STREAMS[s], 2).to(DEVICE); g.load_state_dict(gate_states[s]); gates[s] = g.eval()
        return cls, gates


    DEV_POSE = {vid: long_pose(vid)[0] for vid in LONG_DEV}
    DEV_ANN = {vid: long_annotation(vid) for vid in LONG_DEV}


    def dev_frames(model):
        """Evaluation-1 scorer on each dev video: dense windows, smoothed decoder."""
        out = {}
        for vid in LONG_DEV:
            times, raw, gate_scores = lvscore.predict(DEV_POSE[vid], model, DEVICE)
            truth, seg, guard = lvscore.truth_at(times, DEV_ANN[vid])
            out[vid] = pd.DataFrame({"video_id": vid, "time_s": times, "truth": truth, "segment_type": seg, "guard": guard,
                                     "pred": lvscore.smooth(raw.copy()), "gate": gate_scores})
        return out


    with zipfile.ZipFile(PATHS["v2_stage_a.zip"]) as archive:
        v2_internal = pd.read_csv(archive.open("internal_test_metrics.csv"))
        v2_states = {seed: (torch.load(io.BytesIO(archive.read(f"models/seed_{seed}_classifier.pt")), map_location=DEVICE, weights_only=False)["exercise_state_dict"],
                            {s: torch.load(io.BytesIO(archive.read(f"models/seed_{seed}_{s}_gate.pt")), map_location=DEVICE, weights_only=False)["state_dict"] for s in STREAMS})
                     for seed in CONTROL_SEEDS}
    diag = pd.read_csv(PATHS["dev_diagnosis_metrics.csv"])
    control_frames, control_dev, control_internal = {}, [], []
    for seed in CONTROL_SEEDS:
        model = build_arm(*v2_states[seed])
        cls, gates = model
        im = internal_metrics(fused_score(gates, test_idx), class_probabilities(cls, test_idx))
        ref = float(v2_internal.loc[(v2_internal.arm == "treatment") & (v2_internal.seed == seed), "end_to_end_macro_f1"].iloc[0])
        assert abs(im["end_to_end_macro_f1"] - ref) < 0.003, (seed, im["end_to_end_macro_f1"], ref)
        control_frames[seed] = dev_frames(model)
        dm = lvscore.metrics(list(control_frames[seed].values()))
        if not DRY_RUN:
            dref = diag[(diag.model == f"v2_seed{seed}") & (diag.decoder == "smoothed") & (diag.video_id == "ALL")].iloc[0]
            for k in ("macro_f1", "supported_called_unknown", "downtime_called_unknown"):
                assert abs(dm[k] - dref[k]) < 0.005, (seed, k, dm[k], dref[k])
        control_dev.append({"arm": "control_v2", "seed": seed, **dm})
        control_internal.append({"arm": "control_v2", "seed": seed, **im, "nb43_reference_macro_f1": ref})
    print("v2 control parity passed (internal test vs Notebook 43; dev vs the dev diagnosis).")
    display(pd.DataFrame(control_dev)[["arm", "seed", "macro_f1", "supported_called_unknown", "downtime_called_unknown"]])
    ''')

treatment = patched(nb43[18], [
    ('REPORT = WORK / "calorie_repcount_training_v2_stage_a_report"', 'REPORT = WORK / "calorie_long_video_training_v1_report"'),
    ("treatment_tables, treatment_dev, treatment_internal, history_rows, best_rows = {}, [], [], [], []",
     "treatment_frames, treatment_dev, treatment_internal, history_rows, best_rows = {}, [], [], [], []"),
    ("    t = clip_table(dev_idx, fused_score(gates, dev_idx), class_probabilities(classifier, dev_idx), dev_truth)\n"
     "    treatment_tables[seed] = t.assign(arm=\"treatment\", seed=seed)\n"
     "    treatment_dev.append({\"arm\": \"treatment\", \"seed\": seed, **dev_metrics(t)})\n",
     "    treatment_frames[seed] = dev_frames((classifier, gates))\n"
     "    treatment_dev.append({\"arm\": \"treatment\", \"seed\": seed, **lvscore.metrics(list(treatment_frames[seed].values()))})\n"),
    ("display(pd.DataFrame(treatment_dev))\n",
     'display(pd.DataFrame(treatment_dev)[["arm", "seed", "macro_f1", "supported_called_unknown", "downtime_called_unknown"]])\n'),
])

decision = code(r'''
    control_dev_df, treatment_dev_df = pd.DataFrame(control_dev), pd.DataFrame(treatment_dev)
    internal = pd.DataFrame(control_internal + treatment_internal)
    med = lambda frame, column: float(np.median(frame[column].to_numpy(dtype=float)))

    rng = np.random.default_rng(20261027)
    deltas = []
    for _ in range(2000):
        sample = rng.choice(LONG_DEV, size=len(LONG_DEV), replace=True)
        arm = {name: np.median([lvscore.metrics([fr[v] for v in sample])["macro_f1"] for fr in frames.values()])
               for name, frames in (("control", control_frames), ("treatment", treatment_frames))}
        deltas.append(arm["treatment"] - arm["control"])
    ci = (float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5)))

    unknown_drop = med(control_dev_df, "supported_called_unknown") - med(treatment_dev_df, "supported_called_unknown")
    f1_gain = med(treatment_dev_df, "macro_f1") - med(control_dev_df, "macro_f1")
    downtime_change = med(treatment_dev_df, "downtime_called_unknown") - med(control_dev_df, "downtime_called_unknown")
    ti, ci_int = internal[internal.arm == "treatment"], internal[internal.arm == "control_v2"]
    internal_change = float(ti.end_to_end_macro_f1.mean() - ci_int.end_to_end_macro_f1.mean())
    criteria = {
        "supported_called_unknown_drops_at_least_15pp": unknown_drop >= 0.15,
        "smoothed_macro_f1_gain_at_least_5pp": f1_gain >= 0.05,
        "macro_f1_gain_bootstrap_ci_above_zero": ci[0] > 0,
        "downtime_called_unknown_within_10pp_of_control": downtime_change >= -0.10,
        "internal_macro_f1_within_2pp_of_control": internal_change >= -0.02,
    }
    verdict = "dry_run_not_a_result" if DRY_RUN else ("dev_pass" if all(criteria.values()) else "dev_fail")
    stopping_rule = {"stage": STAGE, "verdict": verdict, "criteria": {k: bool(v) for k, v in criteria.items()},
                     "supported_called_unknown_drop": unknown_drop, "smoothed_macro_f1_gain": f1_gain,
                     "macro_f1_gain_bootstrap_95ci": ci, "downtime_called_unknown_change": downtime_change,
                     "internal_macro_f1_change": internal_change, "locked_long_video_test_loaded": False,
                     "repcount_sealed_test_loaded": False, "production_promotion_allowed": False,
                     "next_if_pass": "Evaluation 2: score these frozen models once on the locked long-video test.",
                     "next_if_fail": "Report; one documented follow-up allowed (PLAN.md section 3), then stop."}
    print(json.dumps(stopping_rule, indent=2))
    summary = pd.concat([control_dev_df, treatment_dev_df], ignore_index=True)
    display(summary[["arm", "seed", "macro_f1", "accuracy", "block_f1", "supported_called_unknown", "downtime_called_unknown"]])
    display(internal[["arm", "seed", "end_to_end_macro_f1", "unknown_recall", "uncovered_mean_recall"]])

    per_video = []
    for name, frames in (("control_v2", control_frames), ("treatment", treatment_frames)):
        for seed, fr in frames.items():
            for v in LONG_DEV:
                per_video.append({"arm": name, "seed": seed, "video_id": v, **lvscore.metrics([fr[v]])})
    run_metadata = {
        "notebook": "45_long_video_training_v1.ipynb", "experiment": "long_video_training_v1", "stage": STAGE,
        "plan": "ml/data/long_video_train_v1/PLAN.md", "long_commit": LONG_COMMIT, "training_commit": TRAINING_COMMIT,
        "roles_commit": ROLES_COMMIT, "dry_run": DRY_RUN, "device": str(DEVICE), "run_seeds": RUN_SEEDS,
        "control": "frozen v2 seeds (Notebook 43)", "max_epochs": MAX_EPOCHS, "patience": PATIENCE,
        "fixed_fusion": FIXED_FUSION, "fixed_threshold": FIXED_THRESHOLD, "threshold_changed": False, "repcount_cap": REPCOUNT_CAP,
        "long_label_share": LONG_LABEL_SHARE, "long_detected_share": LONG_DETECTED_SHARE,
        "long_train_videos": LONG_TRAIN, "long_dev_videos": LONG_DEV, "long_train_windows": int(len(long_train_idx)),
        "locked_benchmark_read": False, "locked_long_video_test_read": False, "repcount_sealed_test_loaded": False,
        "dev_used_for_early_stopping": False, "internal_test_used_for_selection": False, "production_promoted": False,
        "input_hashes": {name: sha256(path) for name, path in PATHS.items()},
    }
    (REPORT / "run_metadata.json").write_text(json.dumps(run_metadata, indent=2) + "\n")
    (REPORT / "stopping_rule.json").write_text(json.dumps(stopping_rule, indent=2) + "\n")
    summary.to_csv(REPORT / "dev_metrics_by_seed.csv", index=False)
    pd.DataFrame(per_video).to_csv(REPORT / "dev_metrics_by_video.csv", index=False)
    for name, frames in (("control_v2", control_frames), ("treatment", treatment_frames)):
        for seed, fr in frames.items():
            pd.concat(fr.values()).to_csv(REPORT / f"dev_timeline_{name}_seed{seed}_smoothed.csv.gz", index=False)
    internal.to_csv(REPORT / "internal_test_metrics.csv", index=False)
    long_audit.to_csv(REPORT / "long_video_window_audit.csv", index=False)
    sampler_audit.to_csv(REPORT / "sampler_audit.csv", index=False)
    pd.DataFrame(history_rows).to_csv(REPORT / "training_history.csv", index=False)
    pd.DataFrame(best_rows).to_csv(REPORT / "best_validation.csv", index=False)
    pd.DataFrame({"delta": deltas}).to_csv(REPORT / "bootstrap_macro_f1_delta.csv", index=False)
    (REPORT / "README.md").write_text(
        "# cALorie long-video training v1 (Notebook 45)\n\n"
        + ("DRY RUN: one epoch on subsamples. Not a result.\n\n" if DRY_RUN else "")
        + "v2 recipe plus the 11 long-video train videos' windows; control is frozen v2. Scored on the 5 dev videos "
        "(full-session scorer, smoothed) and the internal test. No locked or sealed test was read. Non-promotable. Verdict: " + verdict + "\n"
    )
    lines = [f"{sha256(p)}  {p.relative_to(REPORT)}" for p in sorted(q for q in REPORT.rglob("*") if q.is_file())]
    (REPORT / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n")
    zip_path = Path(shutil.make_archive(str(WORK / ("calorie_long_video_training_v1_report" + ("_DRYRUN" if DRY_RUN else ""))), "zip", root_dir=REPORT))
    print("Created:", zip_path, round(zip_path.stat().st_size / 1e6, 1), "MB")
    ''')

cells = [
    md("""
        # cALorie Notebook 45 — long-video training v1

        **Runtime: GPU (the Mac GPU with `CALORIE_DEVICE=mps`, or a Colab T4). Run all.**
        Output: `calorie_long_video_training_v1_report.zip`.

        Runs `ml/data/long_video_train_v1/PLAN.md` section 3 once. It is Notebook 43 (v2 recipe, 50%
        RepCount cap) with one change: the 11 long-video train videos' continuous windows join the
        classifier and gate pools.

        - Control: the frozen v2 seeds from Notebook 43 (parity-checked).
        - Decision on the 5 dev videos with the evaluation-1 full-session scorer and the predeclared rule.
        - Threshold 0.65 and fusion fixed; early stopping on V6-A validation only.
        - The locked long-video test, the RepCount sealed test, and the creator benchmark are never read.
        """),
    code(nb43[1]), config, md(nb43[3]), inputs, md(nb43[5]), code(nb43[6]), md(nb43[7]), code(nb43[8]),
    md("## Add the 11 long-video train videos (continuous windows)\n"), long_video,
    md(nb43[9]), sampler, md(nb43[11]), code(nb43[12]), md(nb43[13]), code(nb43[14]),
    md("## Control: frozen v2, with parity checks\n"), control,
    md("## Treatment: retrain classifier and gates, three seeds\n"), treatment,
    md("## Predeclared dev rule and report\n"), decision,
]
notebook = {
    "cells": cells,
    "metadata": {"accelerator": "GPU", "colab": {"name": OUTPUT.name, "provenance": [], "gpuType": "T4"},
                 "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python", "version": "3"}},
    "nbformat": 4, "nbformat_minor": 5,
}
OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")
print(OUTPUT)
