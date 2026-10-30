"""Adjudicate needs_second_review rows in long_video_round2_v1 (2026-10-28).

Every flagged fine_label maps to the basis that settles it: an ANNOTATION_GUIDE rule (5, 13, 17, 19-23),
the guide default (unidentified or compound moves stay unknown), or the user's acceptance of the
pose-identified segments of 74B9SxqtMug. Labels never change here; only review_status,
needs_second_review and notes.
"""
import csv, glob, sys
from pathlib import Path

BASIS = {
    "in_and_out_squats": "rule 5", "standing_dumbbell_overhead_press": "rule 13", "kettlebell_overhead_press": "rule 20",
    "close_grip_floor_press": "rule 20", "gorilla_row": "rule 20", "bent_arm_lateral": "rule 19",
    "cross_body_dumbbell_curls": "rule 21", "close_grip_dumbbell_press": "rule 22", "lying_chest_press_and_fly": "rule 22",
    "lying_chest_fly": "guide default: a pure fly is unknown (rule 22)", "jumping_jacks_active_rest": "rule 23",
    "lying_dumbbell_pullover_or_extension": "guide default: unidentified move stays unknown",
    "bicep_curl_variation": "guide default: unidentified move stays unknown", "warm_up_reverse_lunges": "rule 4/18",
    "standing_dumbbell_shoulder_press": "user acceptance of pose-identified 74B9SxqtMug segments",
    "standing_arms_out_to_sides_raise": "user acceptance of pose-identified 74B9SxqtMug segments",
    "alternating_arm_raise_to_side": "rule 19 and user acceptance of pose-identified segments",
    "bent_over_dumbbell_row": "user acceptance of pose-identified 74B9SxqtMug segments",
    "overhead_dumbbell_triceps_extension": "user acceptance of pose-identified 74B9SxqtMug segments",
    "standing_dumbbell_curl": "user acceptance of pose-identified 74B9SxqtMug segments",
}
done = pending = 0
for path in sorted(glob.glob(str(Path(sys.argv[1]) / "*.csv"))):
    rows = list(csv.DictReader(open(path)))
    fields = list(rows[0].keys())
    for r in rows:
        if r["needs_second_review"].strip().lower() != "true":
            continue
        basis = BASIS.get(r["fine_label"])
        if basis is None:
            pending += 1; print("pending:", Path(path).stem, r["start_s"], r["fine_label"]); continue
        r["review_status"], r["needs_second_review"] = "adjudicated", "false"
        note = f"adjudicated 2026-10-28 by {basis}"
        r["notes"] = f"{r['notes']}; {note}" if r["notes"] else note
        done += 1
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n"); w.writeheader(); w.writerows(rows)
print(f"adjudicated {done}, pending {pending}")
