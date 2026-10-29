#!/usr/bin/env python3
"""Make the three report/slide charts from the archived result files (no numbers are typed in by hand).

1. model_progression.png  - smoothed Macro F1 on the two locked long-video tests
2. weak_classes.png       - time recall per exercise on the round-2 test, v1 vs v2
3. timeline_example.png   - truth vs prediction on one unseen workout
Usage: make_final_figures.py REPO_ROOT OUT_DIR
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

root, out = Path(sys.argv[1]), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
BLUE, AQUA, ORANGE, VIOLET, YELLOW, GRAY = "#2a78d6", "#1baf7a", "#eb6834", "#6250d6", "#eda100", "#d9d9d6"
INK, MUTED, SURFACE = "#0b0b0b", "#52514e", "#fcfcfb"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False, "figure.facecolor": SURFACE,
                     "axes.facecolor": SURFACE, "text.color": INK})

# ---- 1. progression --------------------------------------------------------------------------------------------
e2 = pd.read_csv(root / "ml/artifacts/long_video_test_v1/eval2/summary.csv")
e2 = e2[e2.decoder == "smoothed"].set_index("model")
r2 = pd.read_csv(root / "ml/artifacts/long_video_round2_test_v1/eval1/summary.csv", index_col=0)
panels = [("Locked test 1: 8 workouts (3.9 h)", [("Early model\n(V6-F)", e2.loc["v6f", "macro_f1"], BLUE),
                                              ("Short-clip + RepCount\nmodel", e2.loc["v2_seed_median", "macro_f1"], AQUA),
                                              ("Final v1\n(+11 long videos)", e2.loc["final_nb46_seed_median", "macro_f1"], ORANGE)]),
          ("Locked test 2: 6 new workouts (2.6 h)", [("Final v1", r2.loc["nb46_seed_median", "macro_f1"], ORANGE),
                                                    ("Final v2\n(+32 long videos)", r2.loc["nb47_seed_median", "macro_f1"], VIOLET)])]
fig, axes = plt.subplots(1, 2, figsize=(10, 4.4), gridspec_kw={"width_ratios": [3, 2]})
for ax, (title, bars) in zip(axes, panels):
    for i, (name, v, c) in enumerate(bars):
        ax.bar(i, v * 100, width=0.62, color=c, zorder=2)
        ax.text(i, v * 100 + 1.2, f"{v * 100:.1f}%", ha="center", fontsize=11, fontweight="bold")
    ax.set_xticks(range(len(bars))); ax.set_xticklabels([b[0] for b in bars], fontsize=9)
    ax.set_ylim(0, 60); ax.set_title(title, fontsize=11, loc="left"); ax.yaxis.grid(True, color="#e6e5e0", zorder=0); ax.set_axisbelow(True)
axes[0].set_ylabel("Macro F1 (higher is better)")
fig.suptitle("Each round of real-workout data raised the score on workouts the model had never seen", x=0.01, ha="left", fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.94)); fig.savefig(out / "model_progression.png", dpi=170); plt.close(fig)

# ---- 2. per-exercise recall --------------------------------------------------------------------------------------
classes = ["lateral_raise", "bicep_curl", "tricep_extension", "shoulder_press", "dumbbell_row", "bench_press", "deadlift", "squat"]
old = [r2.loc["nb46_seed_median", f"recall__{c}"] * 100 for c in classes]; new = [r2.loc["nb47_seed_median", f"recall__{c}"] * 100 for c in classes]
fig, ax = plt.subplots(figsize=(10, 4.8)); x = np.arange(len(classes)); w = 0.38
ax.bar(x - w / 2, old, w - 0.04, color=ORANGE, label="Final v1", zorder=2); ax.bar(x + w / 2, new, w - 0.04, color=VIOLET, label="Final v2", zorder=2)
for xi, a, b in zip(x, old, new):
    ax.text(xi - w / 2, a + 1.5, f"{a:.0f}", ha="center", fontsize=9); ax.text(xi + w / 2, b + 1.5, f"{b:.0f}", ha="center", fontsize=9, fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels([c.replace("_", " ") for c in classes], fontsize=9); ax.set_ylim(0, 112); ax.set_ylabel("Share of exercise time recognized (%)")
ax.yaxis.grid(True, color="#e6e5e0", zorder=0); ax.set_axisbelow(True); ax.legend(frameon=False, loc="upper right", ncol=2)
ax.set_title("Weak exercises gained most from more real workouts (round-2 test, 6 unseen videos); dumbbell row got worse", fontsize=11, loc="left")
fig.tight_layout(); fig.savefig(out / "weak_classes.png", dpi=170); plt.close(fig)

# ---- 3. timeline -------------------------------------------------------------------------------------------------
t = pd.read_csv(root / "ml/artifacts/long_video_round2_test_v1/eval1/timeline_nb47_seed42_smoothed.csv.gz")
t = t[t.video_id == "YEG6y9r-ELM"].sort_values("time_s")
cols = {"bicep_curl": BLUE, "tricep_extension": ORANGE, "lateral_raise": AQUA, "dumbbell_row": VIOLET, "shoulder_press": YELLOW, "unknown": GRAY}
fig, ax = plt.subplots(figsize=(11, 2.6)); step = float(t.time_s.diff().median())
for row, (name, col) in enumerate((("Truth (labeled by hand)", "truth"), ("Model prediction", "pred"))):
    y = 1 - row
    for lab, grp in t.groupby(t[col].ne(t[col].shift()).cumsum()):
        label = grp[col].iloc[0]; a, b = grp.time_s.iloc[0] / 60, (grp.time_s.iloc[-1] + step) / 60
        ax.barh(y, b - a, left=a, height=0.62, color=cols.get(label, "#9c9c97"), edgecolor=SURFACE, linewidth=1)
ax.set_yticks([1, 0]); ax.set_yticklabels(["Truth (labeled by hand)", "Model prediction"]); ax.set_xlabel("minutes into the workout"); ax.set_xlim(0, t.time_s.max() / 60 + 0.1)
present = [k for k in cols if k in set(t.truth) | set(t.pred)]
handles = [plt.Rectangle((0, 0), 1, 1, color=cols[k]) for k in present]
ax.legend(handles, [k.replace("_", " ") for k in present], ncol=6, frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.38))
ax.set_title("One unseen workout, minute by minute (grey = rest or unsupported move)", fontsize=11, loc="left"); ax.spines["left"].set_visible(False)
fig.tight_layout(); fig.savefig(out / "timeline_example.png", dpi=170); plt.close(fig)
print("wrote", sorted(p.name for p in out.glob("*.png")))
