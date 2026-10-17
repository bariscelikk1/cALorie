# First-pass exact-window review (2026-10-17)

The three CSVs in `first_pass/` cover only their named 29F candidate windows.
They are not full-video timelines. Their boundaries were inspected against
local 360p RGB at 4 FPS around state changes and 29F pose contact sheets at
1 FPS through the candidate passages. The source video files remain outside
Git, backed up privately in the user's Drive folder `cALorie_source_balance_v1`.
Six 4-FPS RGB boundary sheets are committed in
`ml/artifacts/source_balance_v1/first_pass_boundary_sheets/`.

| Window | Draft exercise interval (s) | 15-FPS pose frames | Direct detection | Caveat |
| --- | ---: | ---: | ---: | --- |
| `rowan_row_02_01` | 114.00–153.75 | 597 | 99.66% | The audit window begins after the set starts; 153.75–155.00 is transition. |
| `rowan_row_03_01` | 295.00–330.75 | 537 | 100% | The audit window begins during rowing; the athlete stops and crouches at 330.75. |
| `nick_sit_01_01` | 464.50–504.00 | 592 | 100% | 463.00–464.50 is supine setup; 29F pose data ends at 504.00. |

The video inspection establishes a real first-pass motion/boundary proposal,
not an independent second review. Every row is `draft`, requires second
review, and has `use_for_training=false`. The 3-window structural audit in
`first_pass_audit.json` has zero errors and warnings, but this does **not**
approve training. An independent reviewer must inspect the full local clips,
confirm canonical mappings and boundaries, resolve any disagreement, and keep
each original video/person wholly in one split before promotion. In particular,
the two Rowan passages are one creator group, not two independent creators.

For convenient review, three video-only 360p MP4 extracts are stored outside
Git under
`/Users/bariscelik/Documents/Codex/2026-10-14/se/work/source_balance_v1/review_clips/`.
They are excerpts of the private source copies, not model inputs or evidence
of independent review. No retrain has consumed these rows.

On 2026-10-17 the user confirmed the three proposed exercise names in chat,
then explicitly said they had **not yet watched** the linked clips. This is
recorded as label-name feedback only, not a visual second review. The
first-pass draft clip archive remains quarantined until a real independent
inspection resolves the motion and boundary checks.
