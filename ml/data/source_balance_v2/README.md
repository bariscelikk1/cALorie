# Source balance v2 — independent-source intake

This folder is the active intake queue for the four source-confounded classes:
`dumbbell_row`, `sit_up`, `lat_pulldown`, and `pull_up`. It replaces neither the
v1 evidence nor the frozen V6-C checkpoint. Nothing in this folder is training
data.

`candidates.csv` contains metadata-verified YouTube candidates from distinct
creator/channel IDs. The list is intentionally redundant: three creators per
target class are retained so visual screening can reject weak sources without
immediately losing creator coverage. Titles and metadata are discovery
evidence only. Before any interval is usable, it still needs source/use review,
full-person RGB and pose screening, exact boundaries, and an independent human
motion review.

`adjudication/second_pass_codex_review.csv` records the 2026-10-18 Codex visual
adjudication of the three v1 quarantine clips. This is not an independent human
second review: the earlier first pass was also produced by Codex. Accordingly,
`independent_human_review_complete=false` and `training_allowed=false` for every
row. The record preserves useful findings without overstating review status:

- Nick's straight-leg sit-up interval is visually coherent and may be retained
  for a human decision.
- Rowan row 02 contains repeated camera cuts and should not be used as one
  training interval.
- Rowan row 03 should be split around the visible shot change before human
  review.

Run the structural guard from the repository root:

```bash
python3 ml/scripts/audit_source_balance_v2.py
```

The guard checks candidate identity separation, reserved-inventory conflicts,
per-class creator coverage, and adjudication interval safety. Passing it does
not promote a candidate or authorize training.

## 30A screening result and 30B queue

Notebook 30A produced visual evidence for all 12 initial candidates. The
unchanged report is archived under `ml/artifacts/source_balance_v2/` and the
Codex screen is recorded in `screening_review.csv`. Distinct channel IDs were
not sufficient to prove person separation: CHRIS HERIA and THENX feature the
same athlete and share one `person_identity_group`.

`dense_review_targets.csv` contains 17 conservative locators across six videos
that passed the first screen. `supplemental_candidates.csv` adds two replacement
sit-up creators and three replacement lat-pulldown creators because 30A yielded
only one advanced sit-up person and no advanced lat-pulldown person. Notebook
30B creates the next visual evidence package. Every row remains
`training_allowed=false`.

## 30B result and next evidence gate

Notebook 30B returned 2-FPS evidence for 16 of 17 dense regions and screening
evidence for all five replacement sources. The unchanged archive is stored in
`ml/artifacts/source_balance_v2_dense_and_replacements/`. Max Euceda's dense
pass was the only unavailable item (format/HTTP 403); it remains a retry, not a
silently accepted interval.

`dense_visual_review.csv` records the Codex dense motion screen. It advances
canonical row, sit-up, and dynamic pull-up intervals to pose audit while
excluding rests, instruction, chin-ups, isometric holds, kickbacks, and
noncanonical row variants. `replacement_screening_review.csv` advances Alex
Crockford for sit-up and Nona Bayat plus SilverSneakers for lat-pulldown dense
review. Tone and Tighten is rejected for target mismatch; Joanna Soh is held
for pose framing. These are not independent human decisions and do not unlock
training.

Notebook 30C is the next evidence-only step. It produces 2-FPS sheets for the
three advanced replacement locators and retries the unavailable Max Euceda
dense pass. It still does not export landmarks or authorize training.

## 30C result and pose-audit queue

Notebook 30C produced evidence for all four targets and successfully recovered
the previously unavailable Max Euceda source. `replacement_dense_visual_review.csv`
advances the long Alex Crockford sit-up block plus two conservative Max Euceda
row passages. Both lat-pulldown replacements are rejected for the current pose
pipeline: Nona Bayat omits the lower legs and feet, while SilverSneakers cuts
between side and tight upper-body views inside the demonstration.

`pose_audit_targets.csv` combines those three new passages with the 15 intervals
advanced from 30B. All 18 windows remain draft, independently unreviewed, and
training-disabled. The next step is a 15-FPS pose coverage audit, not training.

The first Notebook 30D run could not download any of the seven YouTube sources
because Colab received the same bot-confirmation response for every video. Its
unchanged failure report is archived under
`ml/artifacts/source_balance_v2_pose_audit_failed_download/`; it contains no
pose evidence and changes no review decision. The repaired 30D path runs a
coarse 2-FPS pose-visibility audit directly on the checksum-verified 30B/30C
contact-sheet frames already stored in the repository, without YouTube access.

