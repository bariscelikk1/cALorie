#!/usr/bin/env python3
"""Build Notebook 46: long-video training v1, follow-up 1 (gate balance).

Notebook 45 with one change (PLAN.md "Follow-up 1"): long-video windows hold
exactly 25% of each gate class in the gate sampler. Notebook 45's classifiers
are reused frozen; only the three gates are retrained. Same pass rule against
the same frozen v2 control; Notebook 45 is reported for comparison only.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "ml/notebooks/45_long_video_training_v1.ipynb"
OUTPUT = ROOT / "ml/notebooks/46_long_video_gate_balance.ipynb"
NB45_COMMIT = "5e77a260a4a48c00f399455052731e79895e8d6e"
NB45_ZIP = "ml/artifacts/long_video_training_v1/calorie_long_video_training_v1_report.zip"
NB45_SHA = hashlib.sha256((ROOT / NB45_ZIP).read_bytes()).hexdigest()

BALANCE_CODE = '''exercise_weights = cap_repcount(exercise_train, exercise_weights, labels)

LONG_GATE_SHARE = 0.25  # PLAN.md follow-up 1: the only change from Notebook 45


def balance_long_video(indices, weights, hierarchy):
    """Rescale so long-video windows hold exactly LONG_GATE_SHARE of each class's mass (class mass preserved)."""
    w = weights.copy()
    longv = sources[indices] == "long_video"
    for target in set(hierarchy[indices]):
        m = hierarchy[indices] == target
        long_mass, other_mass = w[m & longv].sum(), w[m & ~longv].sum()
        assert long_mass > 0 and other_mass > 0, target
        total = long_mass + other_mass
        w[m & longv] *= LONG_GATE_SHARE * total / long_mass
        w[m & ~longv] *= (1 - LONG_GATE_SHARE) * total / other_mass
    return w / w.mean()


gate_weights = balance_long_video(gate_train, gate_weights, gate_hierarchy)
'''

PATCHES = {
    0: [("# cALorie Notebook 45 — long-video training v1", "# cALorie Notebook 46 — long-video gate balance (follow-up 1)"),
        ("Output: `calorie_long_video_training_v1_report.zip`.", "Output: `calorie_long_video_gate_balance_report.zip`."),
        ("Runs `ml/data/long_video_train_v1/PLAN.md` section 3 once. It is Notebook 43 (v2 recipe, 50%\n"
         "RepCount cap) with one change: the 11 long-video train videos' continuous windows join the\n"
         "classifier and gate pools.",
         "Runs `ml/data/long_video_train_v1/PLAN.md` follow-up 1 once (post-hoc, the only one allowed). It is\n"
         "Notebook 45 with one change: long-video windows hold exactly 25% of each gate class. Notebook 45's\n"
         "classifiers are reused frozen; only the three gates are retrained.")],
    2: [('STAGE = "long_video_dev"', 'STAGE = "long_video_dev_followup1"')],
    4: [('LONG_COMMIT = "93395df5df3b38eaf1c17680477c4ab8056e042d"\n',
         f'LONG_COMMIT = "93395df5df3b38eaf1c17680477c4ab8056e042d"\nNB45_COMMIT = "{NB45_COMMIT}"\n'),
        ("INPUTS = {\n    # name: (commit, repository path, sha256)\n",
         f'INPUTS = {{\n    # name: (commit, repository path, sha256)\n    "nb45_report.zip": (NB45_COMMIT, "{NB45_ZIP}", "{NB45_SHA}"),\n')],
    12: [("exercise_weights = cap_repcount(exercise_train, exercise_weights, labels)\n", BALANCE_CODE),
         ('assert (sampler_audit.repcount_sampler_mass <= REPCOUNT_CAP * sampler_audit.sampler_mass + 1e-9).all(), "Cap not applied."\n',
          'assert (sampler_audit.repcount_sampler_mass <= REPCOUNT_CAP * sampler_audit.sampler_mass + 1e-9).all(), "Cap not applied."\n'
          'gate_audit = sampler_audit[sampler_audit.model == "gate"]\n'
          'assert np.allclose(gate_audit.long_video_sampler_mass, LONG_GATE_SHARE * gate_audit.sampler_mass), "Gate balance not applied."\n')],
    19: [("## Treatment: retrain classifier and gates, three seeds", "## Treatment: frozen Notebook 45 classifiers, retrained balanced gates")],
    20: [('REPORT = WORK / "calorie_long_video_training_v1_report"', 'REPORT = WORK / "calorie_long_video_gate_balance_report"'),
         ('    classifier, history, best = train_classifier(make_exercise_loaders(seed + 1, exercise_train, exercise_weights, exercise_validation), seed + 1, "cls")\n'
          '    history_rows += history\n'
          '    best_rows.append({"seed": seed, "model": "exercise", "best_validation_macro_f1": best})\n'
          '    torch.save({"exercise_state_dict": classifier.state_dict(), "supported_classes": SUPPORTED_CLASSES, "run_seed": seed},\n'
          '               REPORT / "models" / f"seed_{seed}_classifier.pt")\n',
          '    with zipfile.ZipFile(PATHS["nb45_report.zip"]) as archive:  # frozen Notebook 45 classifier\n'
          '        payload = archive.read(f"models/seed_{seed}_classifier.pt")\n'
          '    nb45_cls = torch.load(io.BytesIO(payload), map_location=DEVICE, weights_only=False)\n'
          '    assert list(nb45_cls["supported_classes"]) == SUPPORTED_CLASSES and nb45_cls["run_seed"] == seed\n'
          '    classifier = SmallTCN(FEATURE_DIM, len(SUPPORTED_CLASSES)).to(DEVICE)\n'
          '    classifier.load_state_dict(nb45_cls["exercise_state_dict"]); classifier.eval()\n'
          '    (REPORT / "models" / f"seed_{seed}_classifier_from_nb45.pt").write_bytes(payload)\n')],
    22: [('"next_if_fail": "Report; one documented follow-up allowed (PLAN.md section 3), then stop."}',
          '"next_if_fail": "Report and close this arc (PLAN.md follow-up 1).",\n'
          '                 "post_hoc_followup": True, "vs_notebook45_reported_only": vs_nb45}'),
         ('verdict = "dry_run_not_a_result" if DRY_RUN',
          'with zipfile.ZipFile(PATHS["nb45_report.zip"]) as archive:\n'
          '    nb45_dev = pd.read_csv(archive.open("dev_metrics_by_seed.csv"))\n'
          'nb45_dev = nb45_dev[nb45_dev.arm == "treatment"]\n'
          'vs_nb45 = {k: med(treatment_dev_df, k) - med(nb45_dev, k) for k in ("macro_f1", "supported_called_unknown", "downtime_called_unknown")}\n'
          'verdict = "dry_run_not_a_result" if DRY_RUN'),
         ('"notebook": "45_long_video_training_v1.ipynb", "experiment": "long_video_training_v1"',
          '"notebook": "46_long_video_gate_balance.ipynb", "experiment": "long_video_training_v1_followup1", "long_gate_share": LONG_GATE_SHARE,\n'
          '    "frozen_classifiers": "Notebook 45 seeds", "nb45_commit": NB45_COMMIT'),
         ('"# cALorie long-video training v1 (Notebook 45)\\n\\n"', '"# cALorie long-video gate balance, follow-up 1 (Notebook 46)\\n\\n"'),
         ('"v2 recipe plus the 11 long-video train videos\' windows; control is frozen v2. ',
          '"Notebook 45 classifiers frozen; gates retrained with long-video windows at 25% of each gate class; control is frozen v2. '),
         ('("calorie_long_video_training_v1_report" + ', '("calorie_long_video_gate_balance_report" + ')],
}

notebook = json.loads(SOURCE.read_text())
for index, replacements in PATCHES.items():
    source = "".join(notebook["cells"][index]["source"])
    for old, new in replacements:
        assert source.count(old) == 1, (index, old[:70], source.count(old))
        source = source.replace(old, new)
    notebook["cells"][index]["source"] = source.splitlines(True)
notebook["metadata"]["colab"]["name"] = OUTPUT.name
OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")
print(OUTPUT)
