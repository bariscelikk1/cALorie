# YouTube long workouts v2 reviewed clips

Notebook 23 produced this training-compatible landmark package from the two
continuous 720p-derived pose archives exported by Notebook 22. The returned ZIP
was preserved byte-for-byte and verified against both its outer SHA-256 and all
internal entries listed in `SHA256SUMS.txt`.

## Verification

- Outer SHA-256: `84fb55b981820af702a94f0c0070960b24fdd1acb617097f1838c782cd942284`
- 32 exported clips from two source-video groups
- 20 supported clips / 715 seconds across nine active classes
- 12 unknown clips / 326 seconds
- 15,195 total 15 FPS frames
- all arrays are finite and shaped `[frames, 17, 4]`
- minimum supported-clip detection rate: 99.33%
- minimum unknown-clip detection rate: 98.79%
- every manifest path and internal checksum passed

## Label provenance

All decisions use reviewer identifier
`codex_contact_sheet_audit_2026_10_16`. The 20 supported intervals retain the
audited class and remove two seconds at each boundary. The 12 deterministic
unknown intervals remove four seconds at each boundary. This is a conservative
contact-sheet review and pose audit; it does not claim a frame-accurate,
full-motion human review.

The package is allowed only as new **training** evidence. Both new `group_id`
values must remain wholly in the training partition. Existing V6-C training,
validation, and test group assignments remain frozen so Notebook 24 measures
only the effect of adding these sources.

## Included evidence

- `calorie_youtube_long_workouts_v2_reviewed_clips.zip`: original returned package
- `manifest.csv`: clip paths, classes, source groups, durations, and pose coverage
- `independent_review_decisions.csv`: decisions, trims, confidence, and reviewer
- `pose_interval_audit.csv`: inherited interval pose-quality evidence
- `run_metadata.json`: Notebook 23 source and execution metadata
- `SHA256SUMS.txt`: checksums inside the returned package
- `ARCHIVE_SHA256.txt`: checksum of the preserved outer ZIP
