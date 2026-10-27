# Long-video test set v1 — plan (approved 2026-10-27)

Status: approved by the user on 2026-10-27, including YouTube as the source with raw video deleted after processing.

## Why

Every long workout video in the repo is already used for training
(`youtube_mixed_workouts_v1`, `youtube_long_workouts_v2`) or is the locked
creator benchmark, which covers only labeled regions and has been used once.
The app's real job is a full session: exercises, rests, transitions, and
camera changes. No honest measurement of that exists. This set is a held-out
**ruler** for full-session behavior. It is never used for training or tuning.

## 1. Sourcing

- **Source:** YouTube follow-along workout videos. Downloading may conflict
  with YouTube's terms, and creators own their videos. **The user decides
  whether that is acceptable.** If not, the plan needs another source.
- **Evidence boundary (as for earlier YouTube work):** raw video is held
  temporarily on the Mac, normalized to H.264 360p, processed, and deleted.
  Only 15-FPS pose, compact still frames, labels, and metrics are kept. Raw
  video never enters Git or an artifact.
- **Download path:** the yt-dlp + Deno + ffmpeg route that eventually worked
  in Notebook 28, run locally on the Mac instead of Colab. The file hash,
  duration, and download date are recorded at acquisition. YouTube files are
  not immutable, so the pose archive is the permanent artifact.

## 2. Selection (rules fixed before watching anything)

- **Size:** 8 videos, 20–45 minutes each, about 3–4 hours total.
- **New creators only:** a channel is rejected if its channel ID or creator
  name appears in any existing YouTube manifest (mixed v1, long v2, creator
  benchmark, source balance v1/v2, excluded inventory). The exclusion list is
  built by a script and committed first.
- **Content (from title, description, and chapters only):** each video lists
  at least 3 of the 14 supported exercises. Across the 8, all 6
  RepCount-covered classes (squat, sit-up, push-up, pull-up, bench press,
  jumping jack) appear, and at least 4 of the 8 uncovered classes (curl,
  deadlift, row, lat pulldown, lateral raise, lunge, shoulder press, tricep
  extension) appear.
- **Variety:** at least 3 home or bodyweight videos and at least 3 gym or
  equipment videos, with varied presenters, rooms, and camera angles. Group
  classes (several people exercising) are excluded; one main performer per
  video.
- **Anti-cherry-picking:** metadata search builds a shortlist of about 20
  that pass the rules. The final 8 are taken in SHA-256 hash order of video
  ID, skipping any that would break the coverage or variety rules. The user
  sees the final list of 8 before anything is downloaded.

## 3. Full-timeline labeling

- **Evidence per video:** 15-FPS pose for the whole video; overview pages at
  1 frame per 2 seconds (60 frames = 2 minutes per page, about 120 pages for
  4 hours); 4-FPS strips around each change of activity, to place boundaries.
- **Schema:** the timeline schema in `ml/data/ANNOTATION_GUIDE.md`
  (`start_s`, `end_s`, `segment_type` exercise / rest / transition / intro /
  outro, `fine_label`, `current_tcn_label`, confidence, reviewer,
  `review_status`, `needs_second_review`). Every second is covered; no gaps.
- **Rules:** visible motion decides. Chapters and titles are locators only.
  Rest, setup, walking, demonstrations, and unsupported or compound moves are
  `unknown`. Boundary precision is recorded honestly (target ±2 s).
- **Who:** Claude labels every second from the evidence. The user
  independently re-checks about 10% of segments, drawn by hash, plus every
  low-confidence segment, as the guide's second review. Disagreements are
  resolved and logged. `audit_timeline_annotations.py --strict` must pass.
- The labels are committed and the set is **locked** before any model sees
  it.

## 4. What gets measured

Both V6-F (official) and v2 (best RepCount model, not promoted), scored on
every video:

- **Dense predictions:** a 64-frame window centered every 8 frames (about
  0.5 s), with the model's fixed 0.65 gate.
- **Two decoders, fixed now and never tuned on this set:**
  1. **Raw:** the window prediction as-is.
  2. **Smoothed:** majority vote over a 5-second sliding window, then any run
     shorter than 4 seconds merges into its neighbor. These are round values
     chosen in advance. Tuning a decoder later needs a separate long-video
     dev set.

| Metric | What it answers |
| --- | --- |
| Time-weighted accuracy and Macro F1 (15 labels), with and without a ±2 s boundary guard | How much of the session is labeled right |
| Exercise-block F1 (IoU at least 0.5, same label) | Does it find each set, start to end? |
| Label switches per minute vs truth (over-segmentation) | Does it flicker mid-set? |
| Rest/transition time called `unknown`; exercise time during rests | Does it handle downtime? |
| Per-class time recall, covered vs uncovered classes | Where does it fail? |
| Per-video tables plus a video-level bootstrap of v2 − V6-F | How sure are we? |

**Predeclared question:** is v2 better than V6-F on full sessions? Primary
metric: smoothed time-weighted Macro F1. Answer "yes" only if the 95%
video-level bootstrap interval of the difference is above zero. This is a
measurement only. Nothing is promoted on this basis alone.

## 5. Rules for reuse

- Never trained on, never used to pick thresholds, decoders, or settings.
- Every evaluation is logged in the handoff. If it is consulted more than
  about 5 times, or anything is tuned against it, a fresh set is needed.

## 6. Effort and runtime

- Download and pose: roughly real-time on the Mac with two lanes, about 2
  hours for 4 hours of video.
- Labeling: about 120 overview pages plus boundary strips (similar to the
  RepCount review). The user's part: about 10% of segments, around 30–45
  minutes.

## Order of work after approval

1. Commit the exclusion-list script and output.
2. Metadata-only search (no downloads); commit the shortlist and the hash
   pick; show the user the final 8.
3. After the user's OK: download, pose, and evidence locally; archive.
4. Claude labels; user second review; audit; lock.
5. Build and dry-run the scorer, run it once per model, archive, report.

## Selection log

- 2026-10-27: The exclusion list (`exclusions.csv`) covers 48 videos, 45
  channels, and 47 creator names. The first metadata search (12 queries,
  snapshot in `search_snapshot.json`) left 20 passing videos (12 after one
  per channel). No valid set of 8 exists, because no passing video mentions
  pull-ups.
- Revision 1, before any video was watched: 3 pull-up queries appended to the
  same snapshot. Still no passing pull-up video. The 8 pull-up videos found
  were rejected for listing fewer than 3 supported exercises (6), a group
  scene (1), or an unclear setting (1). Waiting on a user decision about the
  coverage rule.
- Revision 2 (user decision): one video listing only 2 supported exercises
  may enter if one is pull-up; all other rules unchanged. Two script bugs
  were fixed at the same time: the shortlist loop did not run when fewer than
  20 videos were eligible, and the exception had bypassed the setting check.
  Rerun from the unchanged snapshot: 348 hits, 21 passing, 13 after one per
  channel; the first valid 8 in hash order are marked `selected=True` in
  `candidates.csv` (about 4 hours). Awaiting the user's OK before any
  download.
- Screening (user rule: replace mostly-talking, edited, or multi-person
  videos with the next valid set): `ED5EaUC5EkA` (Muscle & Strength / Sadik
  Hadzovic) was rejected after viewing 1 frame per 10 s. It is a vlog with
  mostly talking to camera, ad and title cards, frequent cuts, and other
  people in frame. The rerun from the unchanged snapshot replaces it with
  `BEO5oeYg8q4` (ACHV PEAK); the other 7 are unchanged. The log is in
  `screening.csv`. The intake pipeline is
  `ml/scripts/long_video_intake_v1.py` (local Mac; raw video deleted per
  video).
- Screening 2: `VqHtkQWLBvg` (the pull-up exception video) is rejected: it
  shows an animated 3D figure, not real footage, with rest and title cards
  every minute. `q_vXOV1BmIQ` is kept. The rerun finds no valid set, because
  no remaining eligible video brings pull-ups. The other 6 videos stay
  selected and are being processed. Waiting on a user decision about
  pull-ups.
- Revision 3 (user decision): 4 more pull-up queries appended to the
  snapshot (434 hits total), with a 5-of-6 fallback only if no full set
  exists. The fallback was not needed: 9 eligible videos now list pull-ups.
  The first valid 8 in hash order (6 of 6 covered) are `fWT-_jx41Jc`
  (Analis Cruz), `wVW6iF82Yrk`, `q_vXOV1BmIQ`, `LlUU6ZscVYk` (Old Dog
  Fitness), `DlemEQnOvnM` (The Ordinary Boy), `jDj0h5JfEiE`, `Acy3T5ikjAE`,
  and `GY1JhB9BEkk`. `ayAG8Zwzzbw` and `BEO5oeYg8q4` dropped out under the
  same rule; their partial processing was stopped and deleted. Every new pick
  must still pass screening (real person, not mostly talking, cuts, or
  crowds).
- Screening 3: `fWT-_jx41Jc` is kept (real performer; some opening talk and
  angle cuts will be labeled unknown/transition). `jDj0h5JfEiE` (Roberta's
  Gym) is rejected as an animated figure. The rule-based rerun picks
  `CIxNJbit9BA`, another Roberta's Gym video, which needs screening too.
- Screening 4: `DlemEQnOvnM` is kept. `CIxNJbit9BA` (a second animated
  Roberta's Gym video) and `GY1JhB9BEkk` (two performers side by side) are
  rejected. Clarification: a video rejected as animated now excludes its
  whole channel. The rerun picks `82SSypK-pao` (Chris & Edi) and
  `9vXCA2i982Q` (Lucie Braunschweig), which need screening.
- Screening 5: `82SSypK-pao` and `9vXCA2i982Q` are kept. `wVW6iF82Yrk` is
  rejected: full-screen 60 s countdown graphics cover about half its runtime.
  The rerun adds `v0aPyBQMgIE` (KineticsTrainer), which is kept.
- **Final set (all 8 screened and kept, 6 of 6 covered classes):**
  `fWT-_jx41Jc`, `q_vXOV1BmIQ`, `LlUU6ZscVYk`, `DlemEQnOvnM`, `Acy3T5ikjAE`,
  `v0aPyBQMgIE`, `82SSypK-pao`, `9vXCA2i982Q`, about 4.0 h in total.
  Evidence is in `ml/artifacts/long_video_test_v1/`. Next: full-timeline
  labeling.
- Labeling (2026-10-27): all 8 timelines written from the 2 s overview
  pages (`annotations/*.csv`, compact specs in `annotations/spec/`); strict
  audit passes. Note: `9vXCA2i982Q` listed pull-ups in its description but no
  pull-up is visible, so none is labeled; pull-ups remain in 3 videos.
- Second review (2026-10-27): the user judged all 44 hash-sampled segments
  correct and approved 10 edge-case rules (now in `ANNOTATION_GUIDE.md`). All
  58 flagged rows were adjudicated by rule or guide default. **The set is
  locked** (`LOCK.json` holds the hashes of every annotation file and evidence
  ZIP). Evaluations so far: 0.

## Scoring details (predeclared 2026-10-27, before any evaluation)

- Models: **V6-F** (V6-E classifier + original V6-F gates,
  `ml/artifacts/v6f_multistream_gate/model/`) and **v2** (the 3 frozen seeds
  from `ml/artifacts/repcount_training_v2_stage_a/`). Gate threshold 0.65,
  mean of 3 gate streams.
- Dense windows: a 64-frame window centered every 8 frames (0.53 s); edges
  are padded by repeating the first/last frame. Truth is the label at the
  window center.
- Decoders: raw; smoothed = majority vote over 9 consecutive centers (about
  5 s; ties keep the raw label), then any run shorter than 4 s merges into
  its longer neighbor (repeat until none).
- Metrics are pooled over all 8 videos (every center weighs the same):
  15-label Macro F1 and accuracy, both with and without a ±2 s boundary
  guard; exercise-block F1 (same label, IoU at least 0.5, one-to-one
  greedy); label switches per minute versus truth; share of rest, transition,
  intro, and outro time called `unknown`; share of supported-exercise time
  called `unknown`; per-class recall. Per-video tables are reported.
- v2 summary = median over its 3 seeds of each metric.
- **Primary question:** smoothed pooled Macro F1, v2 minus V6-F. Answer
  "v2 better" only if the 95% interval from 2,000 video-level bootstrap
  resamples is above zero. This is a measurement only; nothing is promoted or
  tuned from it.
- The scorer is dry-run first on stitched non-test RepCount clips. The
  locked set is then scored exactly once; that counts as evaluation 1.
- **Evaluation 1 (2026-10-27):** V6-F vs v2, scored once. Primary answer: not
  shown better (−0.3 pp, CI −6.2 to +7.6). Details are in
  `ml/artifacts/long_video_test_v1/eval1/README.md`. Evaluations used: 1.
