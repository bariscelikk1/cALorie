#!/usr/bin/env python3
"""Build Notebook 36 from the verified frozen inference path in Notebook 35."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "ml/notebooks/35_colab_provisional_creator_diagnostic.ipynb"
TARGET = ROOT / "ml/notebooks/36_colab_locked_creator_region_benchmark.ipynb"
SOURCE_COMMIT = "27bc6898a9e466e9b36be0c0c9af94e0b5b5ceab"


def source(text: str) -> list[str]:
    return text.splitlines(keepends=True)


def main() -> None:
    notebook = json.loads(SOURCE.read_text(encoding="utf-8"))
    cells = notebook["cells"]

    cells[0]["source"] = source("""# cALorie — locked six-creator region benchmark v1

This notebook performs the one-time frozen **V6-C** versus **V6-F** evaluation
on the locked 36-region creator benchmark. It performs **no training,
calibration, threshold selection, relabeling, or checkpoint modification**.

The contract contains all 14 supported exercises plus four compound `unknown`
regions from six reserved creator videos. Its scope is region classification,
not continuous long-video segmentation. Run all cells; no upload is required.
The final cell downloads `calorie_locked_creator_region_benchmark_v1_report.zip`.
""")

    setup = "".join(cells[1]["source"])
    setup = setup.replace(
        'WORK = Path("/content/calorie_provisional_creator_diagnostic")',
        'WORK = Path("/content/calorie_locked_creator_region_benchmark_v1")',
    ).replace(
        'SOURCE_COMMIT = "922758e20c19f1a0330e4c65b3ae20806f5c71ca"',
        f'SOURCE_COMMIT = "{SOURCE_COMMIT}"',
    )
    cells[1]["source"] = source(setup)

    files = "".join(cells[3]["source"])
    marker = "}\n\ndef sha256"
    additions = '''    "locked_contract.csv": (
        "ml/data/youtube_creator_benchmark_v1/locked_region_benchmark_v1.csv",
        "86bb7780b17e7872e00fc427eed5de6267845b2b9a99e85e260486e039ff041d",
    ),
    "lock_audit.json": (
        "ml/data/youtube_creator_benchmark_v1/locked_region_benchmark_audit_v1.json",
        "20d2005ba4ffda1e2a7a1f7d4880df2b4894d70756950fafc086d4b0d38c56d2",
    ),
'''
    assert marker in files
    files = files.replace(marker, additions + marker)
    cells[3]["source"] = source(files)

    cells[4]["source"] = source("""## 2. Verify the locked region contract

The CSV and its lock audit are checksum-pinned. The notebook refuses to score
unless the contract is locked, contains exactly 36 regions from six videos,
covers all 15 output labels, and preserves every fail-closed prohibition.
""")
    cells[5]["source"] = source("""lock_audit = json.loads(downloaded["lock_audit.json"].read_text())
assert lock_audit["region_benchmark_locked"] is True
assert lock_audit["full_timeline_benchmark_locked"] is False
assert lock_audit["errors"] == []

segments = pd.read_csv(downloaded["locked_contract.csv"]).rename(
    columns={"region_id": "interval_id"}
)
assert len(segments) == 36
assert segments.video_id.nunique() == 6
assert segments.creator.nunique() == 6
assert set(segments.label) == set(ALL_CLASSES)
assert (segments.label == "unknown").sum() == 4
assert segments.interval_id.is_unique
assert segments.lock_status.eq("locked_region_classification_v1").all()
assert segments.benchmark_scope.eq("region_classification_only").all()
for field in (
    "use_for_training", "calibration_allowed", "threshold_selection_allowed",
    "predictions_used_for_labeling",
):
    assert segments[field].astype(str).str.lower().eq("false").all(), field

segments.to_csv(REPORT / "locked_region_benchmark_v1.csv", index=False)
display(segments.groupby(["creator", "label"]).size().unstack(fill_value=0))
print(
    "Locked regions:", len(segments),
    "| supported:", (segments.label != "unknown").sum(),
    "| unknown:", (segments.label == "unknown").sum(),
)
""")

    cells[6]["source"] = source("""## 3. Build deterministic 64-frame windows

Windows are extracted only from the locked region boundaries. The final short
window is included deterministically; sparse missing pose frames are linearly
interpolated exactly as in the verified Notebook 35 reproduction.
""")
    cells[8]["source"] = source("## 4. Load the frozen V6-C and V6-F systems\n")
    cells[10]["source"] = source("## 5. Run inference and aggregate windows to locked regions\n")
    cells[12]["source"] = source("""## 6. Frozen metrics and creator-bootstrap uncertainty

All 15 labels are present. The creator bootstrap resamples the six reserved
creators as units and computes paired V6-F minus V6-C intervals. These
intervals quantify source-level sampling uncertainty; they are not permission
to tune thresholds or rerun variants on this benchmark.
""")

    for index in (7, 11, 13, 14):
        text = "".join(cells[index]["source"])
        text = text.replace("segment_audit", "region_audit")
        text = text.replace("segment_predictions", "region_predictions")
        text = text.replace("segment_pose_audit.csv", "region_pose_audit.csv")
        text = text.replace("segment_predictions.csv", "region_predictions.csv")
        text = text.replace("segment_metrics.csv", "region_metrics.csv")
        text = text.replace("segment_confusion_matrix.png", "region_confusion_matrix.png")
        text = text.replace('"segments": int(len(y_true))', '"regions": int(len(y_true))')
        text = text.replace("Provisional first-pass label", "Locked region label")
        text = text.replace("provisional segment confusion matrix", "locked region confusion matrix")
        cells[index]["source"] = source(text)

    cells[15]["source"] = source("""## 7. Export the immutable benchmark report

The report records the pinned contract, checkpoints, fixed thresholds, metrics,
predictions, source-level bootstrap intervals, and checksums. It does not make
an automatic promotion decision and must never be used for threshold tuning.
""")
    cells[16]["source"] = source("""run_metadata = {
    "experiment": "locked_six_creator_region_benchmark_v1",
    "source_commit": SOURCE_COMMIT,
    "seed": SEED,
    "window_frames": WINDOW,
    "stride_frames": STRIDE,
    "target_fps": TARGET_FPS,
    "systems": {
        "v6c": {
            "gate_threshold": V6C_THRESHOLD,
            "checkpoint_sha256": FILES["v6c.pt"][1],
        },
        "v6f": {
            "fusion": "mean_probability",
            "gate_threshold": V6F_THRESHOLD,
            "classifier_checkpoint_sha256": FILES["v6f_classifier.pt"][1],
            "gate_checkpoint_sha256": {
                stream: FILES[f"{stream}_gate.pt"][1]
                for stream in ("joint", "bone", "velocity")
            },
        },
    },
    "contract": {
        "sha256": FILES["locked_contract.csv"][1],
        "lock_audit_sha256": FILES["lock_audit.json"][1],
        "regions": int(len(segments)),
        "supported_regions": int((segments.label != "unknown").sum()),
        "unknown_regions": int((segments.label == "unknown").sum()),
        "creators": int(segments.creator.nunique()),
        "labels": ALL_CLASSES,
        "lock_status": "locked_region_classification_v1",
        "benchmark_scope": "region_classification_only",
        "full_timeline_locked": False,
        "eligible_for_training": False,
        "eligible_for_calibration": False,
        "eligible_for_threshold_selection": False,
        "prediction_guided_relabeling_allowed": False,
    },
    "primary_metrics": metrics,
    "interpretation": (
        "One-time frozen region-classification benchmark. "
        "No continuous long-video segmentation claim and no tuning allowed."
    ),
}
(REPORT / "metrics.json").write_text(json.dumps(run_metadata, indent=2) + "\\n")

readme = (
    "# cALorie locked creator region benchmark v1\\n\\n"
    "This report compares frozen V6-C and V6-F on 36 locked regions from six "
    "reserved creator videos. All 14 supported labels plus unknown are present. "
    "No training, calibration, threshold selection, or relabeling occurred. "
    "The scope is region classification, not continuous long-video segmentation. "
    "See metrics.json, locked_region_benchmark_v1.csv, and region_predictions.csv.\\n"
)
(REPORT / "README.md").write_text(readme)

checksums = []
for path in sorted(REPORT.iterdir()):
    if path.is_file() and path.name != "SHA256SUMS.txt":
        checksums.append(f"{sha256(path)}  {path.name}")
(REPORT / "SHA256SUMS.txt").write_text("\\n".join(checksums) + "\\n")

archive_base = WORK / "calorie_locked_creator_region_benchmark_v1_report"
archive = Path(shutil.make_archive(str(archive_base), "zip", root_dir=REPORT))
print("Report:", archive)
print("SHA-256:", sha256(archive))
print("\\nPRIMARY RESULT")
display(metric_table)
try:
    from google.colab import files
    files.download(str(archive))
except Exception:
    print("Download manually from:", archive)
""")

    for cell in cells:
        if cell["cell_type"] == "code":
            cell["execution_count"] = None
            cell["outputs"] = []
    notebook.setdefault("metadata", {}).setdefault("colab", {})["name"] = TARGET.name
    notebook["metadata"]["colab"]["provenance"] = []
    TARGET.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(TARGET)


if __name__ == "__main__":
    main()
