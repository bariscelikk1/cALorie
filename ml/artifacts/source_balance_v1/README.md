# CPU screening evidence

`calorie_source_balance_v1_screening.zip` is the user-returned Notebook 29D
output, SHA-256 `833ee35a53d91b0209aa4cdbe3abf3bb911914488fa38a1ebb90d44be38c5b30`.
ZIP integrity and all 82 internal checksums pass. All eight candidates yielded
360p video contact sheets (71 pages total), but no raw video or landmarks are
in the archive. Five/ten-second sampling is source screening, not action
annotation. The videos' reported YouTube license metadata is null/unspecified;
no reuse/license conclusion is made here.

`ml/data/source_balance_v1/screening_review.csv` records source-level visual
triage. `dense_review_targets.csv` contains generous locators only, each with
`training_allowed=false` inherited from the candidate manifest. No supported
label or boundary is locked. A CPU 2-FPS review must inspect actual motion,
camera cuts, person identity, pose visibility, and canonical variants before
any training use.

CPU `Run all` notebook `ml/notebooks/29e_colab_dense_source_balance_review.ipynb`
performs dense RGB extraction for the 17 pinned locators. It reuses 29D's Colab
video cache when present, downloads 360p sources otherwise, records unavailable
sources without failing the batch, and exports one ZIP without raw video or
landmarks.
