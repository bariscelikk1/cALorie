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

`calorie_source_balance_v1_dense_review.zip` is the user-returned 29E output,
SHA-256 `0f868ab7fb27d0b812bd512a29393549f7eb8d7f6ddf27875ab77d57cc66052c`.
ZIP integrity and all 187 internal SHA-256 entries pass. All 17 requested
regions across seven available sources produced 2-FPS RGB sheets (187 pages).
The archive contains no raw video or landmarks. The first visual triage is in
`ml/data/source_balance_v1/dense_visual_first_pass.csv`; its windows are broad
locators, not exact temporal labels, and every row remains a draft excluded
from training. The promising passages require continuous pose and independent
canonical/boundary review. These candidates do not yet resolve source/class
confounding or justify a model retrain.
