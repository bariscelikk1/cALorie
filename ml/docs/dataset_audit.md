# Dataset audit

No dataset may enter training until its license, person identifiers, labels,
video availability, and duplication risk have been reviewed.

| Dataset | Candidate exercises | Person IDs | Raw video | License/access | Status | Main risk |
|---|---|---:|---:|---|---|---|
| MM-Fit | squat, push-up, shoulder press, lunge, dumbbell row, sit-up, tricep extension, bicep curl, lateral raise, jumping jack, non-activity | workout/session IDs | precomputed 2D/3D pose in small archive; RGB-D separately | official download; verify dataset redistribution terms | primary candidate | continuous sessions require correct segmentation; pose has 17 joints rather than MediaPipe's 33 |
| Workout/Fitness Video (Kaggle) | bicep curl, bench press, deadlift, lat pulldown, lateral raise, plank, pull-up, push-up, shoulder press, squat | not documented | yes | Kaggle dataset; verify license and source provenance | development source | 378 selected clips are imbalanced and source/person grouping is unclear, so this source cannot support the final person-separated claim by itself |
| UI-PRMD | squat, lunge and related rehabilitation movements | yes | RGB/skeleton | PDDL 1.0 for dataset | pending | capture domain differs from phone videos |
| HSiPu2 | push-up, sit-up, pull-up | verify | image sequences/video-derived data | academic/public; verify package terms | pending | front and side variants need canonical mapping |
| WAVd | squat, push-up, jumping jack, pull-up, glute bridge and others | verify | request required | academic research only | pending | social-media source and access delay |
| QEVD | broad exercise coverage and negative activities | yes in benchmark subset | yes | research data license agreement | pending | license/access and dataset size |
| PushUpBench | burpee, mountain climber, plank variants, glute bridge variants, repetition-counting examples and hard negatives | source-video prefix only | yes | CC BY 4.0 dataset card | external-test candidate | only 227 clips total and few examples for each needed canonical class; preserve as benchmark rather than forcing variants into training labels |
| Real-Time Exercise Recognition (HF) | squat, push-up, bicep curl, shoulder press | not documented | yes | CC BY-NC-SA 4.0 | backup only | mixes synthetic, Kaggle, stock and online clips; viewer currently fails and provenance needs per-clip audit |
| Own recordings | all target classes and unknown | yes | yes | written participant consent required | pending | limited people and camera diversity |

## Acceptance checklist

- [ ] The original source and license are recorded.
- [ ] Academic use and local processing are permitted.
- [ ] Every included clip has a stable `person_id`.
- [ ] Canonical exercise mappings have been manually reviewed.
- [ ] Duplicate and near-duplicate source videos are identified.
- [ ] No source video crosses train, validation, and test splits.
- [ ] At least one dataset source is held out for a domain-shift evaluation.
- [ ] Class, person, source, and camera-view distributions are documented.

## Download order

1. MM-Fit small archive (1.74 GB): https://s3.eu-west-2.amazonaws.com/vradu.uk/mm-fit.zip
2. Workout/Fitness Video on Kaggle: https://www.kaggle.com/datasets/hasyimabdillah/workoutfitness-video
3. PushUpBench on Hugging Face: https://huggingface.co/datasets/anonymousatom/pushupbench
4. UCF101 only if pull-up or cross-domain coverage is still insufficient: https://www.crcv.ucf.edu/research/data-sets/ucf101/
5. Record consented phone videos from people who will not appear across multiple splits.

## Canonical representation decision

Use a common 17-joint pose representation for the first baseline. MM-Fit already
provides 17-joint pose arrays. MediaPipe produces 33 landmarks, so video imports
and local inference must select and map the corresponding 17 joints before
normalization. This avoids downloading the 39 GB MM-Fit RGB archive merely to
rerun pose estimation.
