# Source-balance v2 coarse pose audit

`calorie_source_balance_v2_pose_audit.zip` is the unchanged user-returned
output from the repaired CPU Notebook 30D. The original download name ended in
`-2`. Outer SHA-256:

`499a0106695ed6ed2fdbb79d97d4c3fdc03f70dda7cdacad5626a35632252a61`

ZIP structure and all 117 hashes in its internal `SHA256SUMS.txt` pass. The
notebook also verified 280 files from the archived 30B evidence and 82 files
from the archived 30C evidence before processing them.

All 18 requested windows produced coarse pose (`pose_ready=18`) from the
archived 2-FPS contact-sheet tiles. The run made zero YouTube requests and
contains no raw video. Its NPZ files are explicitly marked as non-training
audit landmarks. They are suitable for visibility triage only and cannot
replace continuous 15-FPS extraction from the source videos.

The Codex overlay review is recorded in
`ml/data/source_balance_v2/pose_visual_triage.csv`. Seven windows have strong
coarse coverage and eleven remain usable with visibility cautions caused by
side-view joint overlap, close framing, or intermittent pose misses. Every
window remains independently unreviewed and training-disabled.
