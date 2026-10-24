# RepCount external development intake v1

This is a development-only source-shift intake created after the locked creator
benchmark. It does not contain, derive from, or modify any locked benchmark
row. No row is approved for training.

The source is RepCount-A, mirrored as embedded video blobs in the public
`lmms-lab-eval/repcounta-lance` Hugging Face dataset. This avoids a YouTube
downloader and manual uploads. The video mirror is pinned to revision
`ae2e0b0496124d900d4e54a8e92f7ec15a292afd`. Metadata is pinned to
`lmms-lab-eval/repcount` revision
`d4c2ad3df38dfef3d1fca6f7b3fdfad6a38128e5`.

The candidate set has ten published `stuN` source codes and exactly one clip
per code for each of:

- `squat` -> provisional `squat`
- `situp` -> provisional `sit_up`
- `front_raise` -> provisional `unknown` because front raise is unsupported and
  is a useful confuser for lateral raise

For each source-code/action pair, the clip whose published repetition count is
closest to eight was selected; ties use lexical `video_id` order. The original
intake provisionally assigned `stu1` through `stu7` to a future train pool and
`stu8` through `stu10` to development validation. Post-run visual review
invalidated the identity assumption: `stuN` is not a verified person ID, three
`stu10` clips show different people, and `stu8_49`/`stu9_56` share an actor and
scene. Do not call the provisional roles person-disjoint or reuse them without
a new source-group audit.

Published action metadata is only a locator. Notebook 37 must extract RGB/pose
evidence and frozen V6-F diagnostics. Visible-motion and boundary review is
required before any clip can change to `training_allowed=true`. Create a new
versioned experiment manifest with predeclared source-group-disjoint roles; do
not mutate the evidence manifest.

Final dense visual decisions are in `final_visible_adjudication_v1.csv`. Two
known source groups must remain intact: `stu8_49` with `stu9_56`, and
`stu1_69` with `stu6_59`.

Pinned metadata hashes:

- `train.jsonl`: `a7fe063a71a502f1bd5e590a5d582c73455d1bb9f5d391ab8d9f0f2c5365d59d`
- `validation.jsonl`: `55b0b013f8eb5273cc40b84288bbbf538fdde4877ce22acf0cbe1b4a71531675`
- `test.jsonl`: `bbdafa6c81af396465b3e4a20c3d24a058a9d116fa67fa2dd91082eb5599fe3d`

This data source is marked `license: other`; do not redistribute raw video in
Git, model artifacts, or application packages. Compact derived pose arrays,
contact sheets, audits, and aggregate diagnostics may be returned for review.
