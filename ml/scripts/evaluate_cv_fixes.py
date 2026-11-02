#!/usr/bin/env python3
"""Test the cheap fixes (E1-E4) on saved per-window scores. Pass rules: ml/data/improvement_cv_v1/PLAN.md (fixed before any run).

Input: a folder of `<run>_<video_id>.npz` files written by extract_window_scores.py (cls_logits, gate_joint/bone/velocity, time_s).
A "run" is one trained model (for the cross-validation every video has exactly one run, named `cv`; for a code check on v2 it is
`nb47_seed42` etc.). Truth comes from the annotation CSVs. Nothing here trains a model.

Methods (all end in the same 15 labels as the old pipeline):
  baseline  old rule: mean gate P(exercise) >= 0.65 -> argmax class, else unknown; then the 9-window vote (smooth()).
  E1        hysteresis: switch on at gate >= HI, off at gate < LO; then the vote. Also a per-video percentile cutoff.
  E2        Viterbi over 15 states, one switch cost, instead of the vote.
  E1E2      Viterbi with a higher cost to enter than to leave exercise (the hysteresis idea inside the decoder).
Parameters are chosen leaving the scored video out (pooled Macro F1 on the other videos).
E4 is an AUROC comparison (exercise vs not): mean gate probability vs classifier energy vs classifier max-softmax.

Usage: evaluate_cv_fixes.py REPO_ROOT SCORES_DIR OUT_DIR [--runs-are-seeds]
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, roc_auc_score

from score_long_video_test_v1 import LABELS, SUPPORTED, STEP, THRESHOLD, STREAMS, metrics, smooth, truth_at

HYST = [(hi, lo) for hi in (0.55, 0.65, 0.75) for lo in (0.25, 0.35, 0.45, 0.55) if lo < hi]
PERCENTILES = (30, 40, 50)
SWITCH = (2.0, 4.0, 6.0, 8.0)
ENTER_EXTRA = (0.0, 1.0, 2.0, 3.0)


def softmax(a):
    e = np.exp(a - a.max(1, keepdims=True))
    return e / e.sum(1, keepdims=True)


def load_scores(path):
    z = np.load(path)
    gate = np.mean([softmax(z[f"gate_{s}"])[:, 1] for s in STREAMS], axis=0)
    return z["time_s"], z["cls_logits"], gate


def old_rule(cls_p, gate):
    ex = cls_p.argmax(1)
    return np.array([SUPPORTED[e] if g >= THRESHOLD else "unknown" for e, g in zip(ex, gate)], dtype=object)


def hysteresis(cls_p, gate, hi, lo):
    ex, on, out = cls_p.argmax(1), False, []
    for e, g in zip(ex, gate):
        on = g >= hi if not on else g >= lo
        out.append(SUPPORTED[e] if on else "unknown")
    return np.array(out, dtype=object)


def percentile_rule(cls_p, gate, q):
    thr = float(np.percentile(gate, q))
    ex = cls_p.argmax(1)
    return np.array([SUPPORTED[e] if g >= thr else "unknown" for e, g in zip(ex, gate)], dtype=object)


def viterbi(cls_p, gate, cost_in, cost_out):
    """Best 15-state path. Emission: exercise e -> log(gate * p_e); unknown -> log(1 - gate). Switching between two exercises
    costs cost_in + cost_out (leave one, enter the other); unknown -> exercise costs cost_in; exercise -> unknown costs cost_out."""
    n, eps = len(gate), 1e-6
    g = np.clip(gate, eps, 1 - eps)
    emit = np.concatenate([np.log(g[:, None] * np.clip(cls_p, eps, 1)), np.log(1 - g)[:, None]], axis=1)
    k = emit.shape[1]
    trans = np.zeros((k, k))
    trans[:k - 1, :k - 1] = cost_in + cost_out
    trans[k - 1, :k - 1] = cost_in
    trans[:k - 1, k - 1] = cost_out
    np.fill_diagonal(trans, 0.0)
    score, back = emit[0].copy(), np.zeros((n, k), dtype=np.int16)
    for t in range(1, n):
        cand = score[:, None] - trans
        back[t] = cand.argmax(0)
        score = cand.max(0) + emit[t]
    path = np.empty(n, dtype=np.int16)
    path[-1] = score.argmax()
    for t in range(n - 1, 0, -1):
        path[t - 1] = back[t, path[t]]
    return np.array([LABELS[i] for i in path], dtype=object)


def annotations(root, vid):
    for p in sorted((root / "ml/data").glob(f"long_video_*/annotations/{vid}.csv")):
        return pd.read_csv(p).sort_values("start_s").reset_index(drop=True)
    raise FileNotFoundError(vid)


def frame(vid, times, truth, seg, guard, pred, gate):
    return pd.DataFrame({"video_id": vid, "time_s": times, "truth": truth, "segment_type": seg, "guard": guard, "pred": pred, "gate": gate})


def fast_f1(frames):
    d = pd.concat(frames, ignore_index=True)
    return f1_score(d.truth.to_numpy(object), d.pred.to_numpy(object), labels=LABELS, average="macro", zero_division=0)


def grid_for(method):
    if method == "E1_hysteresis": return [dict(hi=h, lo=l) for h, l in HYST]
    if method == "E1_percentile": return [dict(q=q) for q in PERCENTILES]
    if method == "E2_viterbi": return [dict(c=c) for c in SWITCH]
    if method == "E1E2_viterbi_asym": return [dict(c=c, extra=x) for c, x in itertools.product(SWITCH, ENTER_EXTRA) if x > 0]
    return [dict()]


def decode(method, params, cls_p, gate):
    if method == "baseline": return smooth(old_rule(cls_p, gate))
    if method == "E1_hysteresis": return smooth(hysteresis(cls_p, gate, params["hi"], params["lo"]))
    if method == "E1_percentile": return smooth(percentile_rule(cls_p, gate, params["q"]))
    if method == "E2_viterbi": return viterbi(cls_p, gate, params["c"] / 2, params["c"] / 2)
    if method == "E1E2_viterbi_asym": return viterbi(cls_p, gate, params["c"] / 2 + params["extra"], params["c"] / 2)
    raise ValueError(method)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=Path); ap.add_argument("scores", type=Path); ap.add_argument("out", type=Path)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    runs = {}
    for p in sorted(args.scores.glob("*.npz")):
        run, vid = p.stem.rsplit("_", 1)
        runs.setdefault(run, {})[vid] = p
    methods = ["baseline", "E1_hysteresis", "E1_percentile", "E2_viterbi", "E1E2_viterbi_asym"]
    results, aucs = [], []
    for run, files in runs.items():
        vids = sorted(files)
        data = {}
        for v in vids:
            times, logits, gate = load_scores(files[v])
            truth, seg, guard = truth_at(times, annotations(args.root, v))
            data[v] = (times, softmax(logits), logits, gate, truth, seg, guard)
        per = {}  # (method, params_json) -> {video: frame}
        for m in methods:
            for params in grid_for(m):
                per[(m, json.dumps(params))] = {v: frame(v, d[0], d[4], d[5], d[6], decode(m, params, d[1], d[3]), d[3]) for v, d in data.items()}
        chosen = {m: {} for m in methods}
        for m in methods:
            keys = [k for k in per if k[0] == m]
            for held in vids:
                others = [v for v in vids if v != held] or vids
                best = max(keys, key=lambda k: fast_f1([per[k][v] for v in others]))
                chosen[m][held] = best
        for m in methods:
            frames = [per[chosen[m][v]][v] for v in vids]
            base = [per[("baseline", "{}")][v] for v in vids]
            wins = np.mean([metrics([f])["macro_f1"] > metrics([b])["macro_f1"] for f, b in zip(frames, base)])
            results.append({"run": run, "method": m, "videos": len(vids), "win_rate_vs_baseline": float(wins),
                            "params_chosen": json.dumps(sorted({chosen[m][v][1] for v in vids})), **metrics(frames)})
        for v, d in data.items():
            t = d[4] != "unknown"
            ok = d[6]
            if t[ok].all() or (~t[ok]).all():
                continue
            energy = np.log(np.exp(d[2]).sum(1))
            aucs.append({"run": run, "video_id": v, "auroc_gate": roc_auc_score(t[ok], d[3][ok]),
                         "auroc_energy": roc_auc_score(t[ok], energy[ok]), "auroc_maxsoftmax": roc_auc_score(t[ok], d[1].max(1)[ok])})
        print("done run", run, flush=True)
    res, auc = pd.DataFrame(results), pd.DataFrame(aucs)
    res.to_csv(args.out / "metrics_by_run_method.csv", index=False)
    auc.to_csv(args.out / "auroc_by_video.csv", index=False)
    med = res.groupby("method").median(numeric_only=True)
    med.to_csv(args.out / "summary_seed_median.csv")
    b = med.loc["baseline"]
    verdict = {"rules_source": "ml/data/improvement_cv_v1/PLAN.md", "baseline_macro_f1": float(b.macro_f1)}
    for m in methods[1:]:
        r = med.loc[m]
        crit = {"macro_f1_gain_at_least_2pp": bool(r.macro_f1 - b.macro_f1 >= 0.02),
                "supported_called_unknown_down_at_least_5pp": bool(b.supported_called_unknown - r.supported_called_unknown >= 0.05),
                "downtime_called_unknown_not_worse_than_5pp": bool(r.downtime_called_unknown - b.downtime_called_unknown <= 0.05),
                "better_in_at_least_60pct_of_videos": bool(r.win_rate_vs_baseline >= 0.60)}
        verdict[m] = {"criteria": crit, "passes": all(crit.values()), "macro_f1": float(r.macro_f1), "gain": float(r.macro_f1 - b.macro_f1)}
    if len(auc):
        a = auc[["auroc_gate", "auroc_energy", "auroc_maxsoftmax"]].mean()
        verdict["E4_auroc"] = {**{k: float(v) for k, v in a.items()}, "passes": bool(a.auroc_energy - a.auroc_gate >= 0.03)}
    (args.out / "verdict.json").write_text(json.dumps(verdict, indent=2) + "\n")
    print(json.dumps(verdict, indent=2))


if __name__ == "__main__":
    main()
