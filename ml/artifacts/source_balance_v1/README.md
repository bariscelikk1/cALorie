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

The first 29F ZIP, `calorie_source_balance_v1_pose_audit_colab_blocked.zip`,
has outer SHA-256 `36eb3584789f9b8fc30e5b6080fba01d3deba8522cbf3f50b72eeeacddd8a91e`.
All six internal hashes pass, but `pose_ready=0`: a fresh Colab runtime lost
the temporary 29D/29E videos and YouTube returned a bot-authentication block
for all five sources. This is access failure evidence, not a pose quality
result. On 2026-10-17 the exact five 360p video-only files were obtained from
the user's Mac, kept outside Git at
`/Users/bariscelik/Documents/Codex/2026-10-14/se/work/source_balance_v1/videos/`,
and privately backed up to the user's Drive folder
`cALorie_source_balance_v1` (folder ID `1dztxSj58OfKoSvCzQj5dnmpNq0-Mi7Hd`).
The repaired 29F notebook verifies their SHA-256 hashes and loads this Drive
backup before trying YouTube. Raw videos remain excluded from Git and report
ZIPs. Its Drive-first source acquisition was locally checked with a real
hash-matched 360p file. A Mac CPU MediaPipe attempt failed during task startup
with a Metal graph-service abort in this environment; pose extraction therefore
remains for Colab CPU. No local pose data was produced.

The rerun `calorie_source_balance_v1_pose_audit.zip` is the user-returned 29F
output (original download name ends in `-2`), SHA-256
`f8393f2b8c0de03a01121e544d502245cfa0729bd75e56eeac66a936bc013bf0`.
ZIP integrity and all 69 internal SHA-256 entries pass. All five sources were
available and all 17 windows yielded 15-FPS pose (`pose_ready=17`, 5,820 sampled
frames, frame-weighted detection rate 0.9639; minimum window rate 0.7519).
The archive contains 17 landmark NPZ files, 41 pose contact-sheet pages, and
no raw videos. Every window remains `review_status=draft`,
`needs_second_review=true`, and `training_allowed=false`.

Sample visual checks confirm plausible dumbbell rows in `rowan_row_03_01` and
straight-leg sit-ups in `nick_sit_01_01`, but do not establish exact start/end
boundaries. `goku_pull_02_01` visibly includes hanging knee raises alongside
bar work; classifying the entire window as pull-up would be unsafe. Other Goku
windows include camera/person changes and partial-body views. Ryan's pulldown
frames show upper-body motion with cropped lower joints. Sydney and Nick's
second sit-up candidates are variants requiring canonical review. No candidate
has been promoted to a reviewed label or training clip. The next gate is
independent motion/boundary review of the actual video and pose evidence,
followed by the strict annotation audit before any CPU clip build or T4 retrain.
