#!/usr/bin/env python3
"""Build Notebooks 41_0..41_7: RepCount-A intake v2 full-intake shards.

The extraction code is Notebook 40's, unchanged except for the patches below,
because Notebook 40 already ran correctly on 94 real clips.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "ml/notebooks/40_colab_repcount_intake_v2_pilot.ipynb"
SELECTION_COMMIT = "f69a9c4a3d6ae565aed93c2e18ebfaae80a5cc17"
SELECTION_SHA256 = "0ce07188a8755d45c1bbea2b3b4fdbf5ce2892432e0e2ee9c42f0d1665f135f7"
N_SHARDS = 8


def header(shard):
    return f"""# cALorie Notebook 41 — RepCount-A intake v2, shard {shard} of {N_SHARDS - 1}

**Runtime: CPU. Run all.** Output: `calorie_repcount_intake_v2_shard{shard}.zip`.

Evidence only. No labels, training, model scoring, or locked-benchmark access.

- Shard {shard} of the 946 remaining RepCount-A clips (`ml/data/repcount_intake_v2/full_selection.csv`).
- For every clip: 15-FPS MediaPipe pose inside the annotated repetition bounds, a 12-frame contact
  sheet, and 3 scene thumbnails. The code is Notebook 40's, which ran on 94 real clips.
- Videos are read one at a time from the revision-pinned Hugging Face Lance mirror and deleted
  right after processing. Raw video never enters the ZIP.
- A clip that fails is recorded in `source_audit.csv` instead of stopping the run.

Plan: `ml/data/repcount_intake_v2/INTAKE_PLAN.md`; locked pilot results: `PILOT_RESULTS.md`.
"""


def patches(shard):
    return [
        ('/ "calorie_repcount_intake_v2_pilot_work"', f'/ "calorie_repcount_intake_v2_shard{shard}_work"'),
        ('PLAN_COMMIT = "1319d6f8eda4ad07c2972dca56d8242ca779b1f7"', f'PLAN_COMMIT = "{SELECTION_COMMIT}"'),
        ('SELECTION_PATH = "ml/data/repcount_intake_v2/pilot_selection.csv"', 'SELECTION_PATH = "ml/data/repcount_intake_v2/full_selection.csv"'),
        ('SELECTION_SHA256 = "64630d53e747eb91c65464782407c88e95347ea846f5a8820022217cef1bfd15"',
         f'SELECTION_SHA256 = "{SELECTION_SHA256}"\nSHARD = {shard}'),
        ('target = INPUTS / "pilot_selection.csv"', 'target = INPUTS / "full_selection.csv"'),
        ('"pilot_selection.csv changed; this notebook is pinned to the approved selection."',
         '"full_selection.csv changed; this notebook is pinned to the approved selection."'),
        ('assert (selection.role == "pilot").sum() == 64 and (selection.role == "v1_scene_reference").sum() == 30\n'
         'assert selection[selection.role == "pilot"].groupby("pilot_bucket").size().eq(8).all()\n',
         'assert len(selection) == 946 and selection.shard.between(0, 7).all()\n'
         'selection = selection[selection.shard == SHARD].assign(role="intake").reset_index(drop=True)\n'
         'assert 110 <= len(selection) <= 125, len(selection)\n'),
        ('selection = pd.concat([selection[selection.role == "pilot"].head(2), selection[selection.role != "pilot"].head(2)], ignore_index=True)',
         'selection = selection.head(3)'),
        ('display(selection.groupby(["role", "pilot_bucket"], dropna=False).size())', 'display(selection.groupby("bucket").size())'),
        ('if row.role == "pilot":', 'if row.role == "intake":'),
        ('[cv2.IMWRITE_JPEG_QUALITY, 88]', '[cv2.IMWRITE_JPEG_QUALITY, 80]'),
        ('"notebook": "40_colab_repcount_intake_v2_pilot.ipynb"', f'"notebook": "41_colab_repcount_intake_v2_shard{shard}.ipynb"'),
        ('"experiment": "repcount_intake_v2_pilot"', f'"experiment": "repcount_intake_v2_full", "shard": SHARD'),
        ('"pilot_rows": int((source_audit.role == "pilot").sum())', '"intake_rows": int((source_audit.role == "intake").sum())'),
        ('"# cALorie RepCount-A intake v2 pilot evidence\\n\\n"', 'f"# cALorie RepCount-A intake v2 evidence, shard {SHARD}\\n\\n"'),
        ('"DRY RUN: a 4-clip local test, not the pilot.\\n\\n"', '"DRY RUN: a 3-clip local test, not the shard.\\n\\n"'),
        ('"Pose, contact sheets, and scene thumbnails for 64 pilot clips, plus scene thumbnails for the 30 v1 "\n    "clips. ',
         'f"Pose, contact sheets, and scene thumbnails for {len(source_audit)} clips. '),
        ('shutil.copy2(INPUTS / "pilot_selection.csv", REPORT / "pilot_selection.csv")',
         'shutil.copy2(INPUTS / "full_selection.csv", REPORT / "full_selection.csv")'),
        ('("calorie_repcount_intake_v2_pilot" + ', f'("calorie_repcount_intake_v2_shard{shard}" + '),
    ]


def build(shard):
    notebook = json.loads(SOURCE.read_text())
    notebook["cells"][0]["source"] = header(shard).splitlines(True)
    notebook["cells"][-1]["source"] = (
        f"## Return the ZIP\n\nSend back `calorie_repcount_intake_v2_shard{shard}.zip` unchanged. "
        "A few clip errors are fine; they are listed in `source_audit.csv`.\n"
    ).splitlines(True)
    sources = ["".join(cell["source"]) for cell in notebook["cells"]]
    for old, new in patches(shard):
        count = sum(source.count(old) for source in sources)
        assert count == 1, (shard, old, count)
        sources = [source.replace(old, new) for source in sources]
    for cell, source in zip(notebook["cells"], sources):
        cell["source"] = source.splitlines(True)
    notebook["metadata"]["colab"]["name"] = f"41_colab_repcount_intake_v2_shard{shard}.ipynb"
    output = ROOT / f"ml/notebooks/41_colab_repcount_intake_v2_shard{shard}.ipynb"
    output.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")
    return output


if __name__ == "__main__":
    for shard in range(N_SHARDS):
        print(build(shard))
