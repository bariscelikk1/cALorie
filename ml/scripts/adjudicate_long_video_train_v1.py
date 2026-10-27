"""Adjudicate needs_second_review rows in long_video_train_v1 by written rule.

Each flagged fine_label maps to the basis that settles it: one of the ten
user-approved edge-case rules (ANNOTATION_GUIDE.md), the guide's compound or
unsupported default, or a type the user verified directly in the 95-row
second-review sample (2026-10-27, 95/95 correct). Types that rest only on the
proposed rules 11-16 stay flagged until the user confirms those rules.
Labels never change here; only review_status, needs_second_review and notes.
"""
from __future__ import annotations

import csv
import glob
import sys
from pathlib import Path

RULES = {
    "rule 2": ["chest_press_with_glute_bridge", "glute_bridge_chest_press",
               "lying_dumbbell_chest_press", "lying_dumbbell_floor_press",
               "lying_single_arm_floor_press"],
    "rule 3": ["bent_over_dumbbell_row"],
    "rule 4": ["bulgarian_split_squat", "bulgarian_split_squat_left",
               "bulgarian_split_squat_right", "curtsy_lunge_with_goblet",
               "reverse_lunge_with_rotation"],
    "rule 5": ["dumbbell_sumo_squat", "sumo_squat", "wide_sumo_squat_hold_pulse"],
    "rule 6": ["bent_over_tricep_kickback", "tricep_kickback"],
    "rule 7": ["crunch_pulses", "lying_dumbbell_crunch",
               "lying_dumbbell_crunch_legs_up", "zombie_sit_up", "sit_up_reach"],
    "rule 8": ["kneeling_dumbbell_press", "kneeling_kettlebell_press",
               "kneeling_overhead_press"],
    "rule 9": ["dead_stop_staggered_push_up", "dumbbell_push_up", "knee_push_up",
               "push_up_knee_down", "push_up_pulses"],
    "class definition": ["single_arm_overhead_tricep_extension",
                         "skull_crusher_tabletop_legs"],
    "compound/unsupported default": [
        "alternating_biceps_curl_to_front_raise", "bent_over_lateral_raise_row",
        "bent_over_rear_delt_row", "bent_over_row_plus_good_morning",
        "bent_over_wide_row", "bicep_curl_to_romanian_deadlift",
        "deadlift_and_bent_over_row", "goblet_squat_to_reverse_lunge",
        "kneeling_overhead_tricep_extension_to_front_raise",
        "lateral_lunge_with_curl", "lateral_raise_to_front_raise",
        "lateral_raise_to_overhead", "side_lunge_with_goblet",
        "squat_jump_and_touch", "staggered_curl_with_side_step",
        "y_raise", "y_raise_left", "y_raise_right"],
    "user-verified type in review sample": [
        "reverse_lunge_with_curl", "reverse_lunge_with_bicep_curl",
        "standing_shoulder_press_and_raise", "staggered_stance_dumbbell_deadlift",
        "smith_machine_front_squat", "kettlebell_bent_over_row",
        "in_and_out_press", "in_and_out_press_left", "in_and_out_press_right",
        "single_leg_romanian_deadlift"],
}
BASIS = {label: basis for basis, labels in RULES.items() for label in labels}


def main(annotation_dir: str) -> int:
    done = pending = 0
    for path in sorted(glob.glob(str(Path(annotation_dir) / "*.csv"))):
        with open(path, newline="") as fh:
            reader = csv.DictReader(fh)
            fields, rows = reader.fieldnames, list(reader)
        for row in rows:
            if row["needs_second_review"].strip().lower() != "true":
                continue
            basis = BASIS.get(row["fine_label"])
            if basis is None:
                pending += 1
                print(f"pending: {Path(path).stem} {row['start_s']}-{row['end_s']} "
                      f"{row['fine_label']} -> {row['current_tcn_label']}")
                continue
            row["review_status"] = "adjudicated"
            row["needs_second_review"] = "false"
            note = f"adjudicated 2026-10-27 by {basis}"
            row["notes"] = f"{row['notes']}; {note}" if row["notes"] else note
            done += 1
        with open(path, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    print(f"adjudicated {done}, pending {pending}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
