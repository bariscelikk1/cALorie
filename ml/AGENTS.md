# cALorie ML contribution rules

## Temporal annotation work

Before creating, editing, approving, or consuming a long-video label CSV, read
`data/ANNOTATION_GUIDE.md` and follow it as the annotation contract.

- Use `data/templates/timeline_labels_v2.csv` for new annotation batches.
- Keep every interval from one original video and person in exactly one split.
- Base canonical labels on visible body motion available to the model. Chapters,
  transcripts, and titles may locate an interval but cannot override the video.
- Preserve unsupported, compound, ambiguous, rest, transition, intro, and outro
  intervals as `unknown` according to the guide.
- Record uncertainty honestly. Set `needs_second_review=true` for ambiguous
  labels or boundaries; do not guess a supported class.
- Never mark a row `reviewed` or `adjudicated` unless that review actually
  happened. User acceptance of a batch does not substitute for visual review.
- Never use a `draft`, `rejected`, or unresolved low-confidence row for a newly
  promoted training run.
- Keep locked evaluation sources out of training, augmentation, calibration,
  and threshold selection.

After every label change, run:

```bash
python3 ml/scripts/audit_timeline_annotations.py \
  ml/data/youtube_mixed_workouts_v1/annotations/reviewed \
  --report ml/data/youtube_mixed_workouts_v1/annotation_audit.json
```

Use `--strict` for a batch intended to enter training. If an independently
annotated review exists, pass its directory with `--second-root` and report the
agreement result. Do not bypass audit failures; fix the annotation or keep it
out of training and document the reason.

When augmentation changes, visualize representative transformed landmark
sequences before training and change one augmentation family at a time.

## Colab execution boundary

ML notebooks handed to the user must run end to end with `Run all` after the
stated CPU or T4 runtime is selected. Labels, review decisions, source lists,
manifests, hashes, and experiment configuration belong in the repository and
must be prepared before handoff. Inputs already in GitHub are downloaded from
a pinned commit and checksum-verified automatically. Do not require manual
uploads, file selection, repeated widget confirmation, or pasted recovery code
for the normal path. Keep optional inspection controls separate from the
automatic path and record exactly whether a decision came from human motion
review, visual contact-sheet review, or a deterministic policy.
