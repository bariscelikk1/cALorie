#!/usr/bin/env python3
"""Finalize long-video round 3 (3 videos): adjudicate flagged rows, audit, lock the test video, draw the 10% review sample.

Usage: finalize_long_video_round3_v1.py REPO_ROOT WORK_DIR PAGES_DIR
Only review_status, needs_second_review and notes change during adjudication; labels never change.
"""
import csv, glob, hashlib, json, math, sys
from pathlib import Path
import cv2, numpy as np

root, work, pages = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
data, evidence = root / "ml/data/long_video_round3_v1", root / "ml/artifacts/long_video_round3_v1"
ROLE = {"fEuM1XWZ068": "train", "BZiRx8zVPY8": "train", "HlnCRJ2Z-i8": "train", "QWNYZRt_K9g": "train", "WopbPBumelc": "test", "dVtAnYQynbU": "test"}
SUPPORTED = {"bench_press", "bicep_curl", "deadlift", "dumbbell_row", "jumping_jack", "lat_pulldown", "lateral_raise", "lunge",
             "pull_up", "push_up", "shoulder_press", "sit_up", "squat", "tricep_extension", "unknown"}
BASIS = {
    "squat_and_alternating_lunges": "rule 18", "w_press": "rule 13", "meadows_row_left": "rule 12", "meadows_row_right": "rule 12",
    "floor_chest_flyes": "rule 22 (a pure fly stays unknown)", "underhand_rows_left": "rule 3", "underhand_rows_right": "rule 3",
    "half_lateral_raises": "rule 17/19", "rdl_reaches": "rule 11", "renegade_row": "guide default: compound plank row stays unknown",
    "lateral_raise": "on-screen exercise label 'lateral raises'", "bent_over_two_dumbbell_row": "rule 3",
    "dumbbell_shoulder_press": "on-screen exercise label 'shoulder press'", "standing_pause_close_up": "guide default: unidentified stays unknown",
    "double_pulse_curls_and_pivot": "rule 14", "double_neutral_clean_and_press": "guide default: compound stays unknown",
    "tricep_push_up": "rule 15", "lying_dumbbell_press_variation": "rule 22", "alternating_skull_crushers": "class definition (skull crushers, as in rounds 1-2)",
    "kneeling_overhead_dumbbell_work": "guide default: ambiguous stays unknown", "kneeling_reverse_rows": "rule 3", "walking_rows": "rule 3/12",
    "romanian_deadlift_left": "rule 11", "romanian_deadlift_right": "rule 11", "walking_goblet_squat": "rule 5", "alt_curtsy_lunges_back_extensions": "rule 4/18",
    "crunch_hold_alt_heel_touch": "rule 7", "hip_thrust_hold_and_press": "rule 2", "sit_up_hold_with_weight": "rule 7",
    "hip_thrust_hold_alt_chest_press": "rule 2", "left_lunge_pulses": "rule 4", "right_lunge_pulses": "rule 4",
    "deadlift_to_bent_over_rows": "guide default: compound stays unknown", "kneeling_overhead_dumbbell_work": "guide default: ambiguous stays unknown",
    "diamond_press": "rule 22", "decline_chest_press": "rule 2", "prone_lat_pulldowns": "guide default: not the machine class, stays unknown",
    "rear_delt_rows": "rule 3", "supine_rows_as_bent_over_rows": "rule 3 (frames show bent-over two-dumbbell rows, not supine)",
    "bent_over_dumbbell_row": "rule 3", "lying_ab_crunch_variation": "rule 7",
    "rear_delt_fly_and_neutral_press": "guide default: compound stays unknown", "wide_curls": "rule 14", "stirrup_arnold_press": "rule 13",
}
ann = data / "annotations"
with (data / "roles.csv").open("w", newline="") as f:
    w = csv.writer(f, lineterminator="\n"); w.writerow(["video_id", "role"]); [w.writerow([v, r]) for v, r in ROLE.items()]
rows_all, pending = [], 0
for path in sorted(glob.glob(str(ann / "*.csv"))):
    rows = list(csv.DictReader(open(path))); fields = list(rows[0].keys()); prev = 0.0
    for r in rows:
        assert abs(float(r["start_s"]) - prev) < 0.05 and r["current_tcn_label"] in SUPPORTED, (path, r["start_s"])
        prev = float(r["end_s"])
        if r["needs_second_review"] == "true":
            basis = BASIS.get(r["fine_label"])
            if basis is None:
                pending += 1; print("pending:", Path(path).stem, r["start_s"], r["fine_label"]); continue
            r["review_status"], r["needs_second_review"] = "adjudicated", "false"
            note = f"adjudicated 2026-11-02 by {basis}"; r["notes"] = f"{r['notes']}; {note}" if r["notes"] else note
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    rows_all += rows
assert pending == 0
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
lock = {"locked_on": "2026-11-02", "status": "locked_test_set",
        "rules": "Never train, calibrate, choose thresholds or decoders, or relabel from predictions. Two test videos: any score is informational only.",
        "annotations": {f"{v}.csv": sha(ann / f"{v}.csv") for v in ("WopbPBumelc", "dVtAnYQynbU")},
        "evidence": {v: sha(evidence / f"long_video_round3_v1_{v}.zip") for v in ("WopbPBumelc", "dVtAnYQynbU")}, "second_review": "second_review_sample_v1.csv"}
(data / "LOCK.json").write_text(json.dumps(lock, indent=2) + "\n")
sample = []
for rl in ("train", "test"):
    seg = [r for r in rows_all if ROLE[r["video_id"]] == rl]
    seg.sort(key=lambda r: hashlib.sha256(f"long_video_round3_review|{r['video_id']}|{r['start_s']}".encode()).hexdigest())
    sample += seg[:math.ceil(0.10 * len(seg))]
sample.sort(key=lambda r: (r["video_id"], float(r["start_s"])))
with (data / "second_review_sample_v1.csv").open("w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["n", "video_id", "role", "start_s", "end_s", "segment_type", "fine_label", "current_tcn_label", "user_verdict", "user_note"])
    for n, r in enumerate(sample, 1):
        w.writerow([n, r["video_id"], ROLE[r["video_id"]], r["start_s"], r["end_s"], r["segment_type"], r["fine_label"], r["current_tcn_label"], "", ""])
print(len(sample), "segments")
pages.mkdir(parents=True, exist_ok=True)
W, H, N, PER = 200, 112, 8, 5
dense = {v: sorted((float(p.stem[:-1]), p) for p in (work / v / "dense").glob("*.jpg")) for v in ROLE}
for page, start in enumerate(range(0, len(sample), PER)):
    canvas = np.zeros((PER * (H + 22), N * W, 3), np.uint8)
    for i, r in enumerate(sample[start:start + PER]):
        a, b = float(r["start_s"]), float(r["end_s"]); y = i * (H + 22)
        cv2.putText(canvas, f"#{start+i+1}  {r['video_id']}  {int(a)//60}:{int(a)%60:02d}-{int(b)//60}:{int(b)%60:02d}  [{r['segment_type']}] {r['fine_label']}  ->  LABEL: {r['current_tcn_label']}",
                    (4, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 80, 255) if r["current_tcn_label"] != "unknown" else (60, 220, 60), 1)
        for k in range(N):
            t = a + (b - a) * (k + 0.5) / N
            _, p = min(dense[r["video_id"]], key=lambda x: abs(x[0] - t))
            canvas[y + 22:y + 22 + H, k * W:(k + 1) * W] = cv2.resize(cv2.imread(str(p)), (W, H))
    cv2.imwrite(str(pages / f"round3_review_{page+1:02d}.jpg"), canvas, [cv2.IMWRITE_JPEG_QUALITY, 85])
print(math.ceil(len(sample) / PER), "pages ->", pages)
