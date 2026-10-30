#!/usr/bin/env python3
"""Draw the 10% hash-sampled second-review sample for long-video round 2 and render review pages.

Sample: per role (train, test) the segments whose SHA-256(salt|video|start) rank in the lowest 10%.
Pages (5 segments each, 8 evenly spaced stills per segment) are written outside version control
because they contain creators' frames.
Usage: draw_review_sample_round2.py REPO_ROOT WORK_DIR PAGES_DIR
"""
import csv, glob, hashlib, math, sys
from pathlib import Path
import cv2, numpy as np

root, work, pages = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
SALT = "long_video_round2_review"
data = root / "ml/data/long_video_round2_v1"
role = {r["video_id"]: r["role"] for r in csv.DictReader((data / "roles.csv").open())}
rows = []
for f in sorted(glob.glob(str(data / "annotations/*.csv"))):
    rows += [r for r in csv.DictReader(open(f))]
sample = []
for rl in ("train", "test"):
    seg = [r for r in rows if role[r["video_id"]] == rl]
    seg.sort(key=lambda r: hashlib.sha256(f"{SALT}|{r['video_id']}|{r['start_s']}".encode()).hexdigest())
    sample += seg[:math.ceil(0.10 * len(seg))]
sample.sort(key=lambda r: (r["video_id"], float(r["start_s"])))
out = data / "second_review_sample_v1.csv"
with out.open("w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["n", "video_id", "role", "start_s", "end_s", "segment_type", "fine_label", "current_tcn_label", "user_verdict", "user_note"])
    for n, r in enumerate(sample, 1):
        w.writerow([n, r["video_id"], role[r["video_id"]], r["start_s"], r["end_s"], r["segment_type"], r["fine_label"], r["current_tcn_label"], "", ""])
print(len(sample), "segments:", {rl: sum(role[r['video_id']] == rl for r in sample) for rl in ('train', 'test')})
pages.mkdir(parents=True, exist_ok=True)
W, H, N, PER = 200, 112, 8, 5
dense = {}
for n, r in enumerate(sample, 1):
    v = r["video_id"]
    if v not in dense:
        dense[v] = sorted((float(p.stem[:-1]), p) for p in (work / v / "dense").glob("*.jpg"))
for page, start in enumerate(range(0, len(sample), PER)):
    canvas = np.zeros((PER * (H + 22), N * W, 3), np.uint8)
    for i, r in enumerate(sample[start:start + PER]):
        a, b = float(r["start_s"]), float(r["end_s"]); y = i * (H + 22)
        cv2.putText(canvas, f"#{start+i+1}  {r['video_id']}  {int(a)//60}:{int(a)%60:02d}-{int(b)//60}:{int(b)%60:02d}  [{r['segment_type']}] {r['fine_label']}  ->  LABEL: {r['current_tcn_label']}",
                    (4, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80, 80, 255) if r["current_tcn_label"] != "unknown" else (60, 220, 60), 1)
        for k in range(N):
            t = a + (b - a) * (k + 0.5) / N
            _, p = min(dense[r["video_id"]], key=lambda x: abs(x[0] - t))
            canvas[y + 22:y + 22 + H, k * W:(k + 1) * W] = cv2.resize(cv2.imread(str(p)), (W, H))
    cv2.imwrite(str(pages / f"round2_review_{page+1:02d}.jpg"), canvas, [cv2.IMWRITE_JPEG_QUALITY, 85])
print(math.ceil(len(sample) / PER), "pages ->", pages)
