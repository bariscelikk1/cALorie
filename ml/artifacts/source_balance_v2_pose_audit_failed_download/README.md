# Source balance v2 pose audit — failed source download

`calorie_source_balance_v2_pose_audit.zip` is the unchanged output of the
first CPU Notebook 30D run. The archive and all seven internal payload hashes
pass, but the run produced no pose evidence: all seven YouTube downloads were
blocked by the same sign-in / bot-confirmation response.

Run summary:

- pinned input commit: `cde9292b3154a7b54f015c86274c3f0ff168d6ea`
- requested windows: 18
- pose-ready windows: 0
- source-ready videos: 0/7
- training remained disabled
- outer ZIP SHA-256:
  `c9f473663d98176127fd344ab756e5f1e840074b59b7a3a8da093d6b694185d0`

This is an infrastructure failure, not evidence about pose quality or model
performance. Notebook 30D is repaired to audit the already archived and
checksum-verified 2-FPS contact-sheet frames, avoiding another YouTube request.
