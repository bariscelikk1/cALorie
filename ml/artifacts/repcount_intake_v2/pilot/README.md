# RepCount-A intake v2 pilot evidence (Notebook 40)

`calorie_repcount_intake_v2_pilot.zip` is the unchanged Notebook 40 output. Its
outer hash is in `SHA256SUMS.txt`, and `report/SHA256SUMS.txt` inside it lists
all 414 files. Both were verified on 2026-10-25.

**Where it ran:** on the user's Mac (Apple M2, Python 3.12, CPU) through
`CALORIE_WORK` only, not on Colab. Colab rendered a blank page in the user's
browser, and this notebook needs no GPU. Inputs were fetched from the pinned
GitHub commit and Lance revision exactly as on Colab. Notebook commit:
`e5e539151e4f037eaeab55d0c721900abde918f5`. Local OpenCV runtime was 5.0.0 (Colab pins 4.11.0.86); MediaPipe was
0.10.35 as pinned. Pose model SHA-256:
`4eaa5eb7a98365221087693fcc286334cf0858e2eb6e15b506aa4a7ecdcec4ad`.

**Earlier attempt (discarded, not a result):** the first run lost 33 of 94 clips
after clip 61 to temporary Hugging Face read errors (ZIP SHA-256 `b4a6982b0cc57b335c0e403f509ac8810ca8e379a60f190c0d86ecfc7b8af885`). The
notebook gained fetch retries, and this rerun had 0 errors.

**Contents:** 64 pilot clips with 15-FPS pose (normalized and image-space) and
12-frame contact sheets. All 94 clips (64 pilot plus 30 v1) have 3 scene
thumbnails each. Status: 60 `ok` and 4 `low_pose_detection`
(`stu1_5` 74.5%, `stu4_4` 32.0%, `stu7_7` 79.8% bench press; `stu5_28`
73.3% other). No raw video, labels, training, model scoring, or locked
benchmark access.
