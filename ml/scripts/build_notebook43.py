#!/usr/bin/env python3
"""Build Notebook 43: RepCount-A training v2, stage A.

Notebook 42 with exactly one change (TRAINING_PLAN_V2.md): RepCount is capped
at 50% of each class's sampler mass in the classifier and both gate targets.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "ml/notebooks/42_repcount_training_v1_stage_a.ipynb"
OUTPUT = ROOT / "ml/notebooks/43_repcount_training_v2_stage_a.ipynb"

CAP_CODE = '''
REPCOUNT_CAP = 0.5  # TRAINING_PLAN_V2.md: the only change from Notebook 42


def cap_repcount(indices, weights, hierarchy):
    """Scale RepCount and original windows so RepCount holds at most REPCOUNT_CAP of each class's mass."""
    w = weights.copy()
    rep = sources[indices] == "repcount"
    for target in set(hierarchy[indices]):
        m = hierarchy[indices] == target
        rep_mass, old_mass = w[m & rep].sum(), w[m & ~rep].sum()
        if rep_mass > 0 and old_mass > 0 and rep_mass / (rep_mass + old_mass) > REPCOUNT_CAP:
            total = rep_mass + old_mass  # class mass is preserved
            w[m & rep] *= REPCOUNT_CAP * total / rep_mass
            w[m & ~rep] *= (1 - REPCOUNT_CAP) * total / old_mass
    return w / w.mean()


gate_weights = cap_repcount(gate_train, gate_weights, gate_hierarchy)
exercise_weights = cap_repcount(exercise_train, exercise_weights, labels)
validation_indices = '''

PATCHES = [
    ("# cALorie Notebook 42 — RepCount-A training v1, stage A", "# cALorie Notebook 43 — RepCount-A training v2, stage A"),
    ("Output: `calorie_repcount_training_v1_stage_a_report.zip`.", "Output: `calorie_repcount_training_v2_stage_a_report.zip`."),
    ("Runs `ml/data/repcount_intake_v2/TRAINING_PLAN_V1.md`, stage A, once:",
     "Runs `ml/data/repcount_intake_v2/TRAINING_PLAN_V2.md`, stage A, once. It is Notebook 42 with one change:\n"
     "RepCount is capped at 50% of each class's sampler mass (classifier and gate)."),
    ("\nvalidation_indices = ", "\n" + CAP_CODE),
    ("sampler_audit = pd.DataFrame(audit_rows)\n",
     "sampler_audit = pd.DataFrame(audit_rows)\n"
     "assert (sampler_audit.repcount_sampler_mass <= REPCOUNT_CAP * sampler_audit.sampler_mass + 1e-9).all(), \"Cap not applied.\"\n"),
    ('REPORT = WORK / "calorie_repcount_training_v1_stage_a_report"', 'REPORT = WORK / "calorie_repcount_training_v2_stage_a_report"'),
    ('"notebook": "42_repcount_training_v1_stage_a.ipynb", "experiment": "repcount_training_v1"',
     '"notebook": "43_repcount_training_v2_stage_a.ipynb", "experiment": "repcount_training_v2", "repcount_cap": REPCOUNT_CAP'),
    ('"plan": "ml/data/repcount_intake_v2/TRAINING_PLAN_V1.md"', '"plan": "ml/data/repcount_intake_v2/TRAINING_PLAN_V2.md"'),
    ('"# cALorie RepCount-A training v1, stage A\\n\\n"', '"# cALorie RepCount-A training v2 (50% RepCount cap), stage A\\n\\n"'),
    ('("calorie_repcount_training_v1_stage_a_report" + ', '("calorie_repcount_training_v2_stage_a_report" + '),
]

notebook = json.loads(SOURCE.read_text())
sources = ["".join(cell["source"]) for cell in notebook["cells"]]
for old, new in PATCHES:
    count = sum(s.count(old) for s in sources)
    assert count == 1, (old[:60], count)
    sources = [s.replace(old, new) for s in sources]
for cell, source in zip(notebook["cells"], sources):
    cell["source"] = source.splitlines(True)
notebook["metadata"]["colab"]["name"] = OUTPUT.name
OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")
print(OUTPUT)
