#!/usr/bin/env python3
"""Build Notebook 44: RepCount-A training v2, stage B (sealed test, scored once).

Notebook 43 with training removed: it loads the frozen v2 stage-A models from
their archived ZIP, checks they reproduce stage A's internal-test numbers, and
scores the sealed-test clips once under the same predeclared rule.
"""

import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "ml/notebooks/43_repcount_training_v2_stage_a.ipynb"
OUTPUT = ROOT / "ml/notebooks/44_repcount_training_v2_stage_b.ipynb"
V2_COMMIT = "9f9d830"  # archive commit of the v2 stage-A report; expanded to the full hash below
V2_PATH = "ml/artifacts/repcount_training_v2_stage_a/calorie_repcount_training_v2_stage_a_report.zip"
V2_SHA256 = "83737851a0349e746a948bf1600095d494f588a1f3086e1548bd32b8fc131add"

LOAD_MODELS = dedent('''
    REPORT = WORK / "calorie_repcount_training_v2_stage_b_report"
    if REPORT.exists():
        shutil.rmtree(REPORT)
    REPORT.mkdir(parents=True)
    import io
    with zipfile.ZipFile(PATHS["v2_stage_a_report.zip"]) as archive:
        v2_sums = dict(line.split("  ", 1)[::-1] for line in archive.read("SHA256SUMS.txt").decode().splitlines())
        v2_files = {}
        for member, digest in v2_sums.items():
            payload = archive.read(member)
            assert hashlib.sha256(payload).hexdigest() == digest, f"Stage-A file changed: {member}"
            v2_files[member] = payload
    stage_a_internal = pd.read_csv(io.BytesIO(v2_files["internal_test_metrics.csv"]))


    def load_frozen(member):
        return torch.load(io.BytesIO(v2_files[member]), map_location=DEVICE, weights_only=False)


    treatment_tables, treatment_dev, treatment_internal, history_rows, best_rows = {}, [], [], [], []
    for seed in RUN_SEEDS:
        ck = load_frozen(f"models/seed_{seed}_classifier.pt")
        assert list(ck["supported_classes"]) == SUPPORTED_CLASSES
        classifier = SmallTCN(FEATURE_DIM, len(SUPPORTED_CLASSES)).to(DEVICE)
        classifier.load_state_dict(ck["exercise_state_dict"])
        classifier.eval()
        gates = {}
        for stream in STREAMS:
            gk = load_frozen(f"models/seed_{seed}_{stream}_gate.pt")
            assert gk["stream"] == stream and int(gk["input_features"]) == STREAMS[stream]
            gate = SmallTCN(STREAMS[stream], 2).to(DEVICE)
            gate.load_state_dict(gk["state_dict"])
            gates[stream] = gate.eval()
        internal_now = internal_metrics(fused_score(gates, test_idx), class_probabilities(classifier, test_idx))
        reference = stage_a_internal[(stage_a_internal.arm == "treatment") & (stage_a_internal.seed == seed)].end_to_end_macro_f1
        assert len(reference) == 1 and abs(internal_now["end_to_end_macro_f1"] - float(reference.iloc[0])) < 1e-3, \\
            (seed, internal_now["end_to_end_macro_f1"], reference.tolist())
        t = clip_table(dev_idx, fused_score(gates, dev_idx), class_probabilities(classifier, dev_idx), dev_truth)
        treatment_tables[seed] = t.assign(arm="treatment", seed=seed)
        treatment_dev.append({"arm": "treatment", "seed": seed, **dev_metrics(t)})
        treatment_internal.append({"arm": "treatment", "seed": seed, **internal_now})
    print("Frozen v2 models reproduce their stage-A internal-test scores.")
    display(pd.DataFrame(treatment_dev))
''')

PATCHES = [
    # (old, new, expected count)
    ("# cALorie Notebook 43 — RepCount-A training v2, stage A", "# cALorie Notebook 44 — RepCount-A training v2, stage B (sealed test)", 1),
    ("Output: `calorie_repcount_training_v2_stage_a_report.zip`.", "Output: `calorie_repcount_training_v2_stage_b_report.zip`.", 1),
    ('STAGE = "A"  # dev decision only; the sealed test is never loaded here', 'STAGE = "B"  # sealed test, scored once; no training', 1),
    ('    "training_v1_roles.csv": (ROLES_COMMIT,', f'    "v2_stage_a_report.zip": ("{{V2_COMMIT}}", "{V2_PATH}", "{V2_SHA256}"),\n    "training_v1_roles.csv": (ROLES_COMMIT,', 1),
    ('active = ROLES[ROLES.role != "sealed_test"].copy()  # stage A never reads sealed-test pose',
     'active = ROLES[ROLES.role == "sealed_test"].copy()  # stage B reads only sealed-test clips', 1),
    ('    active = pd.concat([active[active.role == "train"].sample(DRY_RUN_REP_TRAIN_CLIPS, random_state=0),\n'
     '                        active[active.role == "dev"].sample(DRY_RUN_REP_DEV_CLIPS, random_state=0)])',
     '    active = ROLES[ROLES.role == "dev"].sample(DRY_RUN_REP_DEV_CLIPS, random_state=0)  # a dry run never reads the sealed test', 1),
    ('"repcount_dev"', '"repcount_sealed"', 2),
    ('f"repcount|dev|{r.video_id}|{s}"', 'f"repcount|sealed|{r.video_id}|{s}"', 1),
    ('assert not set(clip_ids[np.r_[rep_train_idx, dev_idx]]) & set(ROLES.loc[ROLES.role == "sealed_test", "video_id"])\n',
     'assert len(rep_train_idx) == 0 and (DRY_RUN or set(clip_ids[dev_idx]) <= set(ROLES.loc[ROLES.role == "sealed_test", "video_id"]))\n', 1),
    ("@@TREATMENT@@", "", 0),  # placeholder; the treatment cell is replaced wholesale below
    ('("stage_a_pass" if all(criteria.values()) else "stage_a_fail")', '("stage_b_pass" if all(criteria.values()) else "stage_b_fail")', 1),
    ('"sealed_test_loaded": False, "production_promotion_allowed": False,', '"sealed_test_loaded": True, "production_promotion_allowed": False,', 1),
    ('"next_if_pass": "Stage B: score these frozen models once on the sealed test with the same rule."}',
     '"evaluation_set": "sealed_test", "frozen_models_from": "v2_stage_a_report.zip"}', 1),
    ('"notebook": "43_repcount_training_v2_stage_a.ipynb"', '"notebook": "44_repcount_training_v2_stage_b.ipynb"', 1),
    ('"locked_benchmark_read": False, "sealed_test_loaded": False,', '"locked_benchmark_read": False, "sealed_test_loaded": True,', 1),
    ('"repcount_train_windows": int(len(rep_train_idx)), "dev_windows": int(len(dev_idx)),', '"sealed_windows": int(len(dev_idx)),', 1),
    ('REPORT / "dev_metrics_by_seed.csv"', 'REPORT / "sealed_metrics_by_seed.csv"', 1),
    ('REPORT / "dev_clip_predictions.csv"', 'REPORT / "sealed_clip_predictions.csv"', 1),
    ('"# cALorie RepCount-A training v2 (50% RepCount cap), stage A\\n\\n"', '"# cALorie RepCount-A training v2 (50% RepCount cap), stage B: sealed test\\n\\n"', 1),
    ('"Classifier and gates retrained with RepCount train clips; scored on RepCount dev clips and the internal test. "',
     '"Frozen v2 stage-A models scored once on the RepCount sealed test and the internal test. No training. "', 1),
    ('"The sealed test and locked benchmark were not read. Non-promotable. Verdict: "', '"The locked benchmark was not read. Non-promotable. Verdict: "', 1),
    ('("calorie_repcount_training_v2_stage_a_report" + ', '("calorie_repcount_training_v2_stage_b_report" + ', 1),
]


def main():
    import subprocess
    v2_commit = subprocess.run(["git", "-C", str(ROOT), "rev-parse", V2_COMMIT[:7]], capture_output=True, text=True, check=True).stdout.strip()
    notebook = json.loads(SOURCE.read_text())
    cells = notebook["cells"]
    sources = ["".join(c["source"]) for c in cells]
    for old, new, expected in PATCHES:
        if expected == 0:
            continue
        new = new.replace("{V2_COMMIT}", v2_commit)
        count = sum(s.count(old) for s in sources)
        assert count == expected, (old[:70], count)
        sources = [s.replace(old, new) for s in sources]
    treatment = [i for i, s in enumerate(sources) if s.lstrip().startswith("REPORT = WORK /")]
    assert len(treatment) == 1, treatment
    sources[treatment[0]] = LOAD_MODELS.lstrip()
    cells[treatment[0] - 1]["source"] = ["## Load the frozen v2 models and score the sealed test\n"]
    # Drop the "Runs ... stage A" bullet list: describe stage B instead.
    head = sources[0].split("Runs `", 1)[0]
    sources[0] = head + dedent("""
        Stage B of `ml/data/repcount_intake_v2/TRAINING_PLAN_V2.md`, run once:

        - No training. Loads the frozen v2 stage-A models (classifier plus 3 gates, 3 seeds) from their
          checksummed archive, and checks they reproduce their stage-A internal-test scores.
        - Scores the 140 **sealed-test** clips and the internal test against frozen V6-F with the same
          seven predeclared criteria.
        - The locked creator benchmark is not read. Non-promotable.
        """)
    for cell, source in zip(cells, sources):
        if cell["source"] != ["## Load the frozen v2 models and score the sealed test\n"]:
            cell["source"] = source.splitlines(True)
    notebook["metadata"]["colab"]["name"] = OUTPUT.name
    OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")
    print(OUTPUT)


main()
