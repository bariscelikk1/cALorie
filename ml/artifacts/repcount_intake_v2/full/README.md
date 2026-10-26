# RepCount-A intake v2 full evidence (Notebooks 41, 2026-10-26)

Nine unchanged notebook outputs. Outer hashes are in `SHA256SUMS.txt`; every
ZIP's internal `report/SHA256SUMS.txt` was verified on 2026-10-26.

- `calorie_repcount_intake_v2_shard0.zip` … `shard7.zip`: the 946 clips of
  `ml/data/repcount_intake_v2/full_selection.csv`, one shard each, produced by
  Notebooks `41_colab_repcount_intake_v2_shard{0..7}` at commit `bfca6af`.
- `calorie_repcount_intake_v2_makeup.zip`: re-fetch of the 5 clips that failed
  in the shard runs, produced by `41_colab_repcount_intake_v2_makeup` at commit
  `baa4aaa` (retries `ValueError` reads; steps back when a frame fails to
  decode).

**Where it ran:** on the user's Mac (Apple M2, Python 3.12, CPU, two parallel
lanes), not on Colab, which renders blank in the user's browser. Inputs were
fetched from the pinned GitHub commit and Lance revision exactly as on Colab.

**Coverage:** 945 of 946 clips have pose, a contact sheet, and scene
thumbnails. In the shard runs, 817 were `ok`, 124 `low_pose_detection`, and 5
`error`; the make-up recovered 4 of the 5. `stu1_10` remains unrecoverable:
its annotated repetitions run to the final second, which does not decode. For
the 4 recovered clips, use the make-up ZIP, not the shard error rows.

No raw video, labels, training, model scoring, or locked-benchmark access.
