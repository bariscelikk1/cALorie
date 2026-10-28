#!/usr/bin/env python3
"""Build Notebook 47: long-video round 2 (ml/data/long_video_round2_v1/PLAN.md).

Notebook 46's recipe (balanced gates) with one change: far more long-video data. The classifier (Notebook 45 flow)
and the three gates (Notebook 46 flow) are retrained on every labeled long video: round-1 train, dev, and locked-test
videos plus the new round-2 train videos. Control is the frozen Notebook 46 model. One scoring on the 6 new round-2
test videos with the predeclared four-part rule. While round-2 data is not in the repository the notebook can only
dry-run (a round-1 dev stand-in exercises the code path).
"""

import csv
import hashlib
import json
import subprocess
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
NB45, NB46 = (ROOT / f"ml/notebooks/{n}.ipynb" for n in ("45_long_video_training_v1", "46_long_video_gate_balance"))
OUTPUT = ROOT / "ml/notebooks/47_long_video_round2.ipynb"
R1_TRAIN, R2 = ROOT / "ml/data/long_video_train_v1", ROOT / "ml/data/long_video_round2_v1"
R1_TEST = ROOT / "ml/data/long_video_test_v1"
NB46_ZIP = "ml/artifacts/long_video_gate_balance_v1/calorie_long_video_gate_balance_report.zip"


def sha(relative):
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def roles(path):
    return [(r["video_id"], r["role"]) for r in csv.DictReader(path.open())]


r1 = roles(R1_TRAIN / "roles.csv")
R1_TRAIN_IDS = sorted(v for v, r in r1 if r == "train")
R1_DEV_IDS = sorted(v for v, r in r1 if r == "dev")
R1_TEST_IDS = sorted(p.stem for p in (R1_TEST / "annotations").glob("*.csv"))
assert (len(R1_TRAIN_IDS), len(R1_DEV_IDS), len(R1_TEST_IDS)) == (11, 5, 8)
ROUND2_READY = (R2 / "roles.csv").exists() and (R2 / "LOCK.json").exists()
r2 = roles(R2 / "roles.csv") if ROUND2_READY else []
R2_TRAIN_IDS = sorted(v for v, r in r2 if r == "train")
R2_TEST_IDS = sorted(v for v, r in r2 if r == "test")
if ROUND2_READY:
    assert (len(R2_TRAIN_IDS), len(R2_TEST_IDS)) == (8, 6)

subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "--", "ml/data", "ml/artifacts", "ml/scripts"], check=True)
COMMIT = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()

FILES = {  # input name -> repository path
    "nb46_report.zip": NB46_ZIP,
    **{f"long_{v}.zip": f"ml/artifacts/long_video_test_v1/long_video_test_v1_{v}.zip" for v in R1_TEST_IDS},
    **{f"long_ann_{v}.csv": f"ml/data/long_video_test_v1/annotations/{v}.csv" for v in R1_TEST_IDS},
}
for v in R2_TRAIN_IDS + R2_TEST_IDS:
    FILES[f"long_{v}.zip"] = f"ml/artifacts/long_video_round2_v1/long_video_round2_v1_{v}.zip"
    FILES[f"long_ann_{v}.csv"] = f"ml/data/long_video_round2_v1/annotations/{v}.csv"
if ROUND2_READY:
    FILES["round2_lock.json"] = "ml/data/long_video_round2_v1/LOCK.json"


def code(source):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": dedent(source).lstrip().splitlines(True)}


def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": dedent(source).lstrip().splitlines(True)}


def patched(source, replacements):
    for old, new in replacements:
        assert source.count(old) == 1, (old[:70], source.count(old))
        source = source.replace(old, new)
    return source


c45 = ["".join(c["source"]) for c in json.loads(NB45.read_text())["cells"]]
c46 = ["".join(c["source"]) for c in json.loads(NB46.read_text())["cells"]]

config = patched(c46[2], [
    ('STAGE = "long_video_dev_followup1"',
     'STAGE = "long_video_round2"\n'
     f"ROUND2_READY = {ROUND2_READY}\n"
     f"ROUND1_TRAIN_IDS, ROUND1_DEV_IDS, ROUND1_TEST_IDS = {R1_TRAIN_IDS}, {R1_DEV_IDS}, {R1_TEST_IDS}\n"
     f"ROUND2_TRAIN_IDS, ROUND2_TEST_IDS = {R2_TRAIN_IDS}, {R2_TEST_IDS}\n"
     "if ROUND2_READY:\n"
     "    LONG_TRAIN = ROUND1_TRAIN_IDS + ROUND1_DEV_IDS + ROUND1_TEST_IDS + ROUND2_TRAIN_IDS\n"
     "    LONG_TEST = ROUND2_TEST_IDS\n"
     "else:  # dry run only: a round-1 dev stand-in exercises the scoring code path; it is not a result\n"
     "    assert os.environ.get('CALORIE_DRY_RUN') == '1', 'Round-2 data is not in the repository yet; this notebook can only dry-run.'\n"
     "    LONG_TRAIN = ROUND1_TRAIN_IDS + ROUND1_TEST_IDS\n"
     "    LONG_TEST = ROUND1_DEV_IDS\n"
     "#"),
])

new_inputs = "".join(f'    "{n}": (LONG_COMMIT, "{p}", "{sha(p)}"),\n' for n, p in FILES.items())
inputs = patched(c46[4], [
    ('LONG_COMMIT = "93395df5df3b38eaf1c17680477c4ab8056e042d"\n', f'LONG_COMMIT = "{COMMIT}"\n'),
    ('assert not any(path.startswith("ml/data/long_video_test_v1") or "artifacts/long_video_test_v1" in path for _, path, _ in INPUTS.values()), "Locked long-video test must not be an input."\n',
     '# Round 2 plan section 2: the spent long-video test v1 videos are training data now; only their evidence and labels are read.\n'),
    ('    "nb45_report.zip":', new_inputs + '    "nb45_report.zip":'),
])

long_video = patched(c45[10], [
    ('LONG_ROLES = pd.read_csv(PATHS["long_roles.csv"])\n'
     'LONG_TRAIN = sorted(LONG_ROLES.loc[LONG_ROLES.role == "train", "video_id"])\n'
     'LONG_DEV = sorted(LONG_ROLES.loc[LONG_ROLES.role == "dev", "video_id"])\n'
     'assert len(LONG_TRAIN) == 11 and len(LONG_DEV) == 5 and not set(LONG_TRAIN) & set(LONG_DEV)\n'
     'assert not set(LONG_ROLES.channel[LONG_ROLES.role == "train"]) & set(LONG_ROLES.channel[LONG_ROLES.role == "dev"]), "A channel spans roles."\n',
     'LONG_DEV = list(LONG_TEST)  # kept name: the scoring cells score these videos\n'
     'assert not set(LONG_TRAIN) & set(LONG_DEV), "A video is both training and test data."\n'
     'if ROUND2_READY:\n'
     '    lock = json.loads(Path(PATHS["round2_lock.json"]).read_text())\n'
     '    for vid in LONG_TEST:\n'
     '        assert sha256(PATHS[f"long_ann_{vid}.csv"]) == lock["annotations"][vid + ".csv"], f"Lock broken: annotation {vid}"\n'
     '        assert sha256(PATHS[f"long_{vid}.zip"]) == lock["evidence"][vid], f"Lock broken: evidence {vid}"\n'
     '    print("Round-2 test lock verified for", len(LONG_TEST), "videos")\n'),
])

control = '''
def build_arm(classifier_state, gate_states):
    cls = SmallTCN(FEATURE_DIM, len(SUPPORTED_CLASSES)).to(DEVICE); cls.load_state_dict(classifier_state); cls.eval()
    gates = {}
    for s in STREAMS:
        g = SmallTCN(STREAMS[s], 2).to(DEVICE); g.load_state_dict(gate_states[s]); gates[s] = g.eval()
    return cls, gates


DEV_POSE = {vid: long_pose(vid)[0] for vid in LONG_DEV}
DEV_ANN = {vid: long_annotation(vid) for vid in LONG_DEV}


def dev_frames(model):
    """Evaluation-1 scorer on each test video: dense windows, smoothed decoder."""
    out = {}
    for vid in LONG_DEV:
        times, raw, gate_scores = lvscore.predict(DEV_POSE[vid], model, DEVICE)
        truth, seg, guard = lvscore.truth_at(times, DEV_ANN[vid])
        out[vid] = pd.DataFrame({"video_id": vid, "time_s": times, "truth": truth, "segment_type": seg, "guard": guard,
                                 "pred": lvscore.smooth(raw.copy()), "gate": gate_scores})
    return out


with zipfile.ZipFile(PATHS["nb46_report.zip"]) as archive:
    nb46_internal = pd.read_csv(archive.open("internal_test_metrics.csv"))
    nb46_states = {seed: (torch.load(io.BytesIO(archive.read(f"models/seed_{seed}_classifier_from_nb45.pt")), map_location=DEVICE, weights_only=False)["exercise_state_dict"],
                          {s: torch.load(io.BytesIO(archive.read(f"models/seed_{seed}_{s}_gate.pt")), map_location=DEVICE, weights_only=False)["state_dict"] for s in STREAMS})
                   for seed in CONTROL_SEEDS}
control_frames, control_dev, control_internal = {}, [], []
for seed in CONTROL_SEEDS:
    model = build_arm(*nb46_states[seed])
    cls, gates = model
    im = internal_metrics(fused_score(gates, test_idx), class_probabilities(cls, test_idx))
    ref = float(nb46_internal.loc[(nb46_internal.arm == "treatment") & (nb46_internal.seed == seed), "end_to_end_macro_f1"].iloc[0])
    assert abs(im["end_to_end_macro_f1"] - ref) < 0.003, (seed, im["end_to_end_macro_f1"], ref)
    control_frames[seed] = dev_frames(model)
    control_dev.append({"arm": "control_nb46", "seed": seed, **lvscore.metrics(list(control_frames[seed].values()))})
    control_internal.append({"arm": "control_nb46", "seed": seed, **im, "nb46_reference_macro_f1": ref})
print("Notebook 46 control parity passed (internal test).")
display(pd.DataFrame(control_dev)[["arm", "seed", "macro_f1", "supported_called_unknown", "downtime_called_unknown"]])
'''

treatment = patched(c45[20], [
    ('REPORT = WORK / "calorie_long_video_training_v1_report"', 'REPORT = WORK / "calorie_long_video_round2_report"'),
])

decision = '''
WEAK = ["tricep_extension", "lateral_raise", "bicep_curl", "dumbbell_row", "shoulder_press"]
control_dev_df, treatment_dev_df = pd.DataFrame(control_dev), pd.DataFrame(treatment_dev)
internal = pd.DataFrame(control_internal + treatment_internal)
med = lambda frame, column: float(np.median(frame[column].to_numpy(dtype=float)))


def weak_recall(frame):
    present = [w for w in WEAK if frame[f"recall__{w}"].notna().all()]
    return float(np.mean([med(frame, f"recall__{w}") for w in present])), present


rng = np.random.default_rng(20261028)
deltas = []
for _ in range(2000):
    sample = rng.choice(LONG_DEV, size=len(LONG_DEV), replace=True)
    arm = {name: np.median([lvscore.metrics([fr[v] for v in sample])["macro_f1"] for fr in frames.values()])
           for name, frames in (("control", control_frames), ("treatment", treatment_frames))}
    deltas.append(arm["treatment"] - arm["control"])
ci = (float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5)))

f1_gain = med(treatment_dev_df, "macro_f1") - med(control_dev_df, "macro_f1")
weak_t, present = weak_recall(treatment_dev_df)
weak_c, _ = weak_recall(control_dev_df)
unknown_change = med(treatment_dev_df, "supported_called_unknown") - med(control_dev_df, "supported_called_unknown")
downtime_change = med(treatment_dev_df, "downtime_called_unknown") - med(control_dev_df, "downtime_called_unknown")
ti, ci_int = internal[internal.arm == "treatment"], internal[internal.arm == "control_nb46"]
internal_change = float(ti.end_to_end_macro_f1.mean() - ci_int.end_to_end_macro_f1.mean())
criteria = {
    "smoothed_macro_f1_gain_at_least_3pp": f1_gain >= 0.03,
    "weak_class_mean_recall_gain_at_least_10pp": weak_t - weak_c >= 0.10,
    "supported_called_unknown_not_worse_than_3pp": unknown_change <= 0.03,
    "downtime_called_unknown_not_worse_than_5pp": downtime_change <= 0.05,
}
verdict = "dry_run_not_a_result" if DRY_RUN else ("replace_nb46" if all(criteria.values()) else "keep_nb46")
stopping_rule = {"stage": STAGE, "verdict": verdict, "criteria": {k: bool(v) for k, v in criteria.items()},
                 "smoothed_macro_f1_gain": f1_gain, "macro_f1_gain_bootstrap_95ci_reported_only": ci,
                 "weak_classes_scored": present, "weak_class_mean_recall_control": weak_c, "weak_class_mean_recall_treatment": weak_t,
                 "supported_called_unknown_change": unknown_change, "downtime_called_unknown_change": downtime_change,
                 "internal_macro_f1_change_reported_only": internal_change, "test_videos": LONG_DEV,
                 "production_promotion_allowed": False,
                 "rule": "Notebook 47 replaces Notebook 46 as the final model only if all four criteria hold."}
print(json.dumps(stopping_rule, indent=2))
summary = pd.concat([control_dev_df, treatment_dev_df], ignore_index=True)
display(summary[["arm", "seed", "macro_f1", "accuracy", "block_f1", "supported_called_unknown", "downtime_called_unknown"]])
display(internal[["arm", "seed", "end_to_end_macro_f1", "unknown_recall", "uncovered_mean_recall"]])

per_video = []
for name, frames in (("control_nb46", control_frames), ("treatment", treatment_frames)):
    for seed, fr in frames.items():
        for v in LONG_DEV:
            per_video.append({"arm": name, "seed": seed, "video_id": v, **lvscore.metrics([fr[v]])})
run_metadata = {
    "notebook": "47_long_video_round2.ipynb", "experiment": "long_video_round2", "stage": STAGE, "round2_ready": ROUND2_READY,
    "plan": "ml/data/long_video_round2_v1/PLAN.md", "inputs_commit": LONG_COMMIT, "training_commit": TRAINING_COMMIT,
    "dry_run": DRY_RUN, "device": str(DEVICE), "run_seeds": RUN_SEEDS, "control": "frozen Notebook 46 seeds",
    "max_epochs": MAX_EPOCHS, "patience": PATIENCE, "fixed_fusion": FIXED_FUSION, "fixed_threshold": FIXED_THRESHOLD,
    "repcount_cap": REPCOUNT_CAP, "long_gate_share": LONG_GATE_SHARE, "long_train_videos": LONG_TRAIN, "long_test_videos": LONG_DEV,
    "long_train_windows": int(len(long_train_idx)), "nothing_tuned": True, "internal_test_used_for_selection": False,
    "production_promoted": False, "input_hashes": {name: sha256(path) for name, path in PATHS.items()},
}
(REPORT / "run_metadata.json").write_text(json.dumps(run_metadata, indent=2) + "\\n")
(REPORT / "stopping_rule.json").write_text(json.dumps(stopping_rule, indent=2) + "\\n")
summary.to_csv(REPORT / "test_metrics_by_seed.csv", index=False)
pd.DataFrame(per_video).to_csv(REPORT / "test_metrics_by_video.csv", index=False)
for name, frames in (("control_nb46", control_frames), ("treatment", treatment_frames)):
    for seed, fr in frames.items():
        pd.concat(fr.values()).to_csv(REPORT / f"test_timeline_{name}_seed{seed}_smoothed.csv.gz", index=False)
internal.to_csv(REPORT / "internal_test_metrics.csv", index=False)
long_audit.to_csv(REPORT / "long_video_window_audit.csv", index=False)
sampler_audit.to_csv(REPORT / "sampler_audit.csv", index=False)
pd.DataFrame(history_rows).to_csv(REPORT / "training_history.csv", index=False)
pd.DataFrame(best_rows).to_csv(REPORT / "best_validation.csv", index=False)
pd.DataFrame({"delta": deltas}).to_csv(REPORT / "bootstrap_macro_f1_delta.csv", index=False)
(REPORT / "README.md").write_text(
    "# cALorie long-video round 2 (Notebook 47)\\n\\n"
    + ("DRY RUN: one epoch on subsamples. Not a result.\\n\\n" if DRY_RUN else "")
    + "Notebook 46 recipe on all labeled long videos; control is frozen Notebook 46; scored once on the round-2 test videos. "
    "Non-promotable. Verdict: " + verdict + "\\n")
lines = [f"{sha256(p)}  {p.relative_to(REPORT)}" for p in sorted(q for q in REPORT.rglob("*") if q.is_file())]
(REPORT / "SHA256SUMS.txt").write_text("\\n".join(lines) + "\\n")
zip_path = Path(shutil.make_archive(str(WORK / ("calorie_long_video_round2_report" + ("_DRYRUN" if DRY_RUN else ""))), "zip", root_dir=REPORT))
print("Created:", zip_path, round(zip_path.stat().st_size / 1e6, 1), "MB")
'''

cells = [
    md("""
        # cALorie Notebook 47 — long-video round 2

        **Runtime: GPU (the Mac GPU with `CALORIE_DEVICE=mps`, or a Colab T4). Run all.**
        Output: `calorie_long_video_round2_report.zip`.

        Runs `ml/data/long_video_round2_v1/PLAN.md` once. Notebook 46's recipe (v2 pool, 50% RepCount cap,
        long-video windows at 25% of each gate class), with one change: it trains on every labeled long video
        (round-1 train, dev, and old test videos plus the new round-2 training videos).

        - Control: the frozen Notebook 46 model.
        - One scoring on the 6 new round-2 test videos; the four-part rule decides whether it replaces Notebook 46.
        - Nothing is tuned. The creator benchmark and the old sealed tests are not read.
        """),
    code(c46[1]), code(config), md("## Download pinned inputs\n"), code(inputs), md("## Rebuild Notebook 31's exact training pool\n"), code(c46[6]),
    md("## Add RepCount train and dev clips (sealed test excluded)\n"), code(c46[8]),
    md("## Add every labeled long video (continuous windows)\n"), code(long_video),
    md("## Sampler, augmentation, and datasets (gate balanced)\n"), code(c46[12]),
    md("## Models and trainer\n"), code(c46[14]), md("## Fixed scoring\n"), code(c46[16]),
    md("## Control: frozen Notebook 46\n"), code(control),
    md("## Treatment: retrain classifier and gates, three seeds\n"), code(treatment),
    md("## Predeclared rule and report\n"), code(decision),
]
notebook = {
    "cells": cells,
    "metadata": {"accelerator": "GPU", "colab": {"name": OUTPUT.name, "provenance": [], "gpuType": "T4"},
                 "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python", "version": "3"}},
    "nbformat": 4, "nbformat_minor": 5,
}
OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")
print(OUTPUT, "| round2_ready:", ROUND2_READY, "| commit:", COMMIT[:8])
