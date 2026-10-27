#!/usr/bin/env python3
"""Build Notebook 42: RepCount-A training v1, stage A (dev decision only).

Reuses Notebook 39's tested cells (inputs, Notebook 31 training pool, sampler,
augmentation, models, trainer) with checked patches, and adds the RepCount
role data, classifier retraining, dev scoring, and the predeclared rule from
ml/data/repcount_intake_v2/TRAINING_PLAN_V1.md.
"""

import json
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "ml/notebooks/39_colab_repcount_gate_rotation.ipynb"
OUTPUT = ROOT / "ml/notebooks/42_repcount_training_v1_stage_a.ipynb"
ROLES_COMMIT = "24ed98d0dbc666510ee724acfa63186dad066710"
INTAKE_ZIPS = {
    "intake_pilot.zip": ("ml/artifacts/repcount_intake_v2/pilot/calorie_repcount_intake_v2_pilot.zip", "e9bb439a62ea224120aab256809a6d3dd6e737cb487d7a7a4b7cf8c5cbf54bae"),
    **{f"intake_shard{i}.zip": (f"ml/artifacts/repcount_intake_v2/full/calorie_repcount_intake_v2_shard{i}.zip", h) for i, h in enumerate([
        "a967ee4e460b71b8b417fac5bf0995a5681ec904f4ac22c30f521ffb8dd44157",
        "17e55e624a923689dec923fc5f4b2ec98cbdcea0b83742351271aa5324c74805",
        "1bfe214e8fa300848bf36a0b0d3d128dbfb05e3b640f345ebabe4421e903529c",
        "ff0c1537ccc87d6bfd9c5538e092047e86a1d08a76cf4576148f022787fc6bdf",
        "b16aa78ffa706cdb898805930b2930db779963b531e7fa61ba152c0a4d4d0708",
        "7cda0e72856e6f49660c557322983d1cc9d549bedae6b236a63e39f1972559f5",
        "4cc4e1ed4f0d7e82fd611e9322fb87baaa36f285158efb7e1bc5637fa7ce4b36",
        "325be3d532e6aad92079a633500e5ccb8ed7f86a57fe44f5887f95b24fd2af9a",
    ])},
    # Make-up last: it overrides the shard error rows for the 4 recovered clips.
    "intake_makeup.zip": ("ml/artifacts/repcount_intake_v2/full/calorie_repcount_intake_v2_makeup.zip", "94a73cbf1177c8a1428135e54b337952e8eb6eebef89d8c4a974cd82c57870c9"),
}
ROLES_SHA256 = "16f4008b9322c6c92c91192f050ea5d58a9b5dde231b1bcaa8a8b8f20ff6186e"


def md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": dedent(source).lstrip().splitlines(True)}


def code(source):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": dedent(source).lstrip().splitlines(True)}


def patched(source, replacements):
    for old, new in replacements:
        assert source.count(old) == 1, (old[:70], source.count(old))
        source = source.replace(old, new)
    return code(source)


nb39 = [("".join(c["source"])) for c in json.loads(SOURCE.read_text())["cells"]]

config = patched(nb39[2], [
    ("N_FOLDS = 3\n", 'STAGE = "A"  # dev decision only; the sealed test is never loaded here\n'),
    ("DRY_RUN_VALIDATION_WINDOWS = 400\n", "DRY_RUN_VALIDATION_WINDOWS = 400\nDRY_RUN_REP_TRAIN_CLIPS, DRY_RUN_REP_DEV_CLIPS = 40, 20\n"),
])

intake_lines = "".join(
    f'    "{name}": (ROLES_COMMIT, "{path}", "{sha}"),\n' for name, (path, sha) in INTAKE_ZIPS.items()
)
inputs = patched(nb39[4], [
    ('DESIGN_COMMIT = "9544dfb4436148bed3328a2854b055f52b82893d"\n',
     f'DESIGN_COMMIT = "9544dfb4436148bed3328a2854b055f52b82893d"\nROLES_COMMIT = "{ROLES_COMMIT}"\n'),
    ('    "folds.csv": (DESIGN_COMMIT, "ml/data/repcount_development_v1/gate_rotation_v1/folds.csv", "37cb91d473d7a940673f0cfe09a59db9a21fe7a2c60577091c619dc11478751c"),\n',
     f'    "training_v1_roles.csv": (ROLES_COMMIT, "ml/data/repcount_intake_v2/training_v1_roles.csv", "{ROLES_SHA256}"),\n' + intake_lines),
])

repcount = code(r'''
    ROLES = pd.read_csv(PATHS["training_v1_roles.csv"])
    assert ROLES.video_id.is_unique and set(ROLES.role) == {"train", "dev", "sealed_test"}
    assert (ROLES.groupby("role_group").role.nunique() == 1).all(), "A role group spans roles."
    assert set(ROLES.label) <= set(ALL_CLASSES), set(ROLES.label) - set(ALL_CLASSES)
    active = ROLES[ROLES.role != "sealed_test"].copy()  # stage A never reads sealed-test pose
    if DRY_RUN:
        active = pd.concat([active[active.role == "train"].sample(DRY_RUN_REP_TRAIN_CLIPS, random_state=0),
                            active[active.role == "dev"].sample(DRY_RUN_REP_DEV_CLIPS, random_state=0)])
    import io
    need = set(active.video_id)


    def zip_pose_index(name, prefix="report/"):
        """Map video_id -> (zip path, member, expected sha) using the archive's own checksum list."""
        with zipfile.ZipFile(PATHS[name]) as archive:
            listed = dict(line.split("  ", 1)[::-1] for line in archive.read(prefix + "SHA256SUMS.txt").decode().splitlines())
            index = {}
            for member in archive.namelist():
                if member.startswith(prefix + "pose/") and member.endswith(".npz"):
                    relative = member[len(prefix):]
                    index[Path(member).stem] = (PATHS[name], member, listed[relative])
        return index


    pose_source = {}
    for name in [n for n in INPUTS if n.startswith("intake_")]:  # make-up is last and wins
        pose_source.update(zip_pose_index(name))
    v1_source = zip_pose_index("repcount_report.zip")
    pose_source.update({k: v for k, v in v1_source.items() if k in need})
    missing = need - set(pose_source)
    assert not missing, f"No pose for {sorted(missing)[:5]}"


    def load_pose(entry):
        path, member, expected = entry
        with zipfile.ZipFile(path) as archive:
            payload = archive.read(member)
        assert hashlib.sha256(payload).hexdigest() == expected, f"Checksum failed: {member}"
        with np.load(io.BytesIO(payload), allow_pickle=False) as item:
            assert abs(float(item["target_fps"]) - 15.0) < 1e-3
            pose = item["landmarks"].astype(np.float32)
        assert pose.ndim == 3 and pose.shape[1:] == (17, 4) and len(pose) > 0 and np.isfinite(pose).all()
        return pose


    def resample_window(pose):
        old = np.arange(len(pose), dtype=np.float32)
        new = np.linspace(0, len(pose) - 1, WINDOW, dtype=np.float32)
        flat = pose.reshape(len(pose), -1)
        return np.stack([np.interp(new, old, flat[:, j]) for j in range(flat.shape[1])], 1).reshape(WINDOW, 17, 4).astype(np.float32)


    def eval_windows(pose):
        """Notebook 37 rule (used for clip-level scoring)."""
        if len(pose) < WINDOW:
            return [0], [resample_window(pose)]
        starts_ = list(range(0, len(pose) - WINDOW + 1, STRIDE))
        if starts_[-1] != len(pose) - WINDOW:
            starts_.append(len(pose) - WINDOW)
        return starts_, [pose[s:s + WINDOW] for s in starts_]


    def train_windows(pose, label):
        """Notebook 31 rule: fixed windows (padded when short) plus phase cycles for supported clips."""
        starts_ = list(range(0, max(1, len(pose) - WINDOW + 1), STRIDE))
        if len(pose) > WINDOW and starts_[-1] != len(pose) - WINDOW:
            starts_.append(len(pose) - WINDOW)
        out = []
        for s in starts_:
            w = pose[s:s + WINDOW]
            if len(w) < WINDOW:
                w = np.concatenate([w, np.repeat(w[-1:], WINDOW - len(w), axis=0)])
            out.append((f"fixed|{s}", s, w))
        if label != "unknown" and len(pose) >= 24:
            period = estimate_period(pose)
            cands = list(range(0, max(1, len(pose) - period + 1), period))
            if len(cands) > 6:
                cands = [cands[i] for i in np.linspace(0, len(cands) - 1, 6, dtype=int)]
            for k, s in enumerate(cands):
                e = min(len(pose), s + period)
                if e - s >= 12:
                    out.append((f"phase64|{k}", s, phase_resample(pose[s:e])))
        return out


    new_windows, rows = [], []
    for r in active.itertuples(index=False):
        pose = load_pose(pose_source[r.video_id])
        if r.role == "train":
            for tag, s, w in train_windows(pose, r.label):
                new_windows.append(w); rows.append((r.video_id, r.label, r.role_group, "repcount_train", s, f"repcount|train|{r.video_id}|{tag}"))
        else:
            for s, w in zip(*eval_windows(pose)):
                new_windows.append(w); rows.append((r.video_id, r.label, r.role_group, "repcount_dev", s, f"repcount|dev|{r.video_id}|{s}"))
    # V1 parity windows: the 30 Notebook 37 clips, scored only to reproduce frozen V6-F (never trained here).
    with zipfile.ZipFile(PATHS["repcount_report.zip"]) as archive:
        v1_ids = sorted(pd.read_csv(archive.open("report/video_diagnostics.csv")).video_id)
    for vid in v1_ids:
        for s, w in zip(*eval_windows(load_pose(v1_source[vid]))):
            new_windows.append(w); rows.append((vid, "v1", "v1", "v1_parity", s, f"repcount|v1parity|{vid}|{s}"))

    meta = pd.DataFrame(rows, columns=["video_id", "label", "role_group", "split", "start", "window_key"])
    rep_start = len(X)
    X = np.concatenate([X, np.asarray(new_windows, dtype=np.float32)])
    meta_labels = meta.label.where(meta.split != "v1_parity", "unknown").to_numpy(dtype=object)  # v1 parity rows are never trained
    original_labels = np.concatenate([original_labels, meta_labels])
    labels = np.concatenate([labels, meta_labels])
    groups = np.concatenate([groups, ("repcount:" + meta.role_group).to_numpy(dtype=object)])
    clip_ids = np.concatenate([clip_ids, meta.video_id.to_numpy(dtype=object)])
    sources = np.concatenate([sources, np.repeat("repcount", len(meta)).astype(object)])
    starts = np.concatenate([starts, meta.start.to_numpy(dtype=np.int64)])
    window_keys = np.concatenate([window_keys, meta.window_key.to_numpy(dtype=object)])
    assigned_split = np.concatenate([assigned_split, meta.split.to_numpy(dtype=object)])
    y_gate = (labels != "unknown").astype(np.int64)
    y_exercise = np.asarray([supported_to_id.get(name, -1) for name in labels], dtype=np.int64)
    rep_train_idx = np.flatnonzero(assigned_split == "repcount_train")
    dev_idx = np.flatnonzero(assigned_split == "repcount_dev")
    v1p_idx = np.flatnonzero(assigned_split == "v1_parity")
    assert window_keys.size == len(set(window_keys)), "Window keys must be unique."
    assert len(test_idx) == 1971 and np.array_equal(test_idx, np.flatnonzero(assigned_split == "test"))
    assert not set(groups[rep_train_idx]) & set(groups[dev_idx]), "Train and dev share a role group."
    assert not set(groups[np.r_[rep_train_idx, dev_idx]]) & set(groups[np.r_[train_idx, val_idx, test_idx]])
    assert not set(clip_ids[np.r_[rep_train_idx, dev_idx]]) & set(ROLES.loc[ROLES.role == "sealed_test", "video_id"])
    dev_truth = dict(zip(active.video_id, active.label))
    print("RepCount train windows:", len(rep_train_idx), "| dev windows:", len(dev_idx), "| v1 parity windows:", len(v1p_idx))
    display(meta[meta.split != "v1_parity"].groupby(["split", "label"]).video_id.nunique().unstack(0, fill_value=0))
    ''')

aug_and_streams = nb39[10].split("fold_train_indices, fold_train_weights, sampler_rows = {}, {}, []")[0]
assert aug_and_streams.count("set(window_keys[rep_idx])") == 1
aug_and_streams = aug_and_streams.replace("set(window_keys[rep_idx])", "set(window_keys[np.r_[rep_train_idx, dev_idx]])")
sampler = code(aug_and_streams + r'''
class ExerciseDataset(Dataset):
    def __init__(self, indices, training):
        self.indices, self.training = np.asarray(indices), training

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, item):
        actual = self.indices[item]
        sample = X[actual].copy()
        if self.training:
            sample = augment_pose_window(sample)
        return torch.from_numpy(pose_to_features(sample).T), torch.tensor(y_exercise[actual], dtype=torch.long)


def make_exercise_loaders(seed, train_indices, train_weights, validation_indices):
    generator = torch.Generator().manual_seed(seed)
    sampler = WeightedRandomSampler(torch.as_tensor(train_weights, dtype=torch.double), len(train_weights), replacement=True, generator=generator)
    return (
        DataLoader(ExerciseDataset(train_indices, True), batch_size=BATCH_SIZE, sampler=sampler),
        DataLoader(ExerciseDataset(validation_indices, False), batch_size=BATCH_SIZE, shuffle=False),
    )


gate_train = np.concatenate([dry_run_subset(train_idx, DRY_RUN_TRAIN_WINDOWS, 0), rep_train_idx])
gate_weights = hierarchical_window_weights(gate_train, gate_hierarchy, hard_positive_weights)
exercise_train = gate_train[y_exercise[gate_train] >= 0]
exercise_weights = hierarchical_window_weights(exercise_train, labels)
validation_indices = dry_run_subset(val_idx, DRY_RUN_VALIDATION_WINDOWS, 99)
exercise_validation = validation_indices[y_exercise[validation_indices] >= 0]

audit_rows = []
for name, idx, w, hierarchy in [("gate", gate_train, gate_weights, gate_hierarchy), ("exercise", exercise_train, exercise_weights, labels)]:
    rep = sources[idx] == "repcount"
    for target in sorted(set(hierarchy[idx])):
        m = hierarchy[idx] == target
        audit_rows.append({"model": name, "target": target, "windows": int(m.sum()), "repcount_windows": int((m & rep).sum()),
                           "sampler_mass": float(w[m].sum() / w.sum()), "repcount_sampler_mass": float(w[m & rep].sum() / w.sum())})
sampler_audit = pd.DataFrame(audit_rows)
display(sampler_audit)
''')

trainer = patched(nb39[12], [
    ("def train_gate(stream, loaders, seed, tag):\n", "def train_network(input_features, num_classes, loaders, seed, tag, stream):\n"),
    ("    model = SmallTCN(STREAMS[stream], 2).to(DEVICE)\n    criterion", "    model = SmallTCN(input_features, num_classes).to(DEVICE)\n    criterion"),
])
trainer["source"] += dedent('''


    def train_gate(stream, loaders, seed, tag):
        return train_network(STREAMS[stream], 2, loaders, seed, tag, stream)


    def train_classifier(loaders, seed, tag):
        return train_network(FEATURE_DIM, len(SUPPORTED_CLASSES), loaders, seed, tag, "exercise")
''').splitlines(True)

scoring = code(r'''
    TEST_CLASSES = ["unknown", "squat", "jumping_jack", "bench_press", "pull_up", "sit_up", "push_up"]
    UNCOVERED = ["bicep_curl", "deadlift", "dumbbell_row", "lat_pulldown", "lateral_raise", "lunge", "shoulder_press", "tricep_extension"]


    def infer_stream(model, indices, stream, batch_size=256):
        out = []
        with torch.no_grad():
            for s in range(0, len(indices), batch_size):
                batch = np.stack([pose_to_stream(X[i], stream) for i in indices[s:s + batch_size]]).transpose(0, 2, 1)
                out.append(model(torch.from_numpy(batch).to(DEVICE)).softmax(1).cpu().numpy())
        return np.concatenate(out)[:, 1]


    def fused_score(gates, indices):
        return np.stack([infer_stream(gates[s], indices, s) for s in STREAMS], axis=1).mean(axis=1)


    def class_probabilities(model, indices, batch_size=256):
        out = []
        with torch.no_grad():
            for s in range(0, len(indices), batch_size):
                batch = np.stack([pose_to_features(X[i]) for i in indices[s:s + batch_size]]).transpose(0, 2, 1)
                out.append(model(torch.from_numpy(batch).to(DEVICE)).softmax(1).cpu().numpy())
        return np.concatenate(out)


    def internal_metrics(gate_scores, class_prob):
        pred = np.asarray([SUPPORTED_CLASSES[c] if s >= FIXED_THRESHOLD else "unknown" for s, c in zip(gate_scores, class_prob.argmax(1))])
        truth = labels[test_idx].astype(str)
        recall = {c: float((pred[truth == c] == c).mean()) for c in ALL_CLASSES if (truth == c).any()}
        return {"end_to_end_macro_f1": float(f1_score(truth, pred, labels=ALL_CLASSES, average="macro", zero_division=0)),
                "end_to_end_accuracy": float(accuracy_score(truth, pred)),
                "unknown_recall": recall["unknown"],
                "uncovered_mean_recall": float(np.mean([recall[c] for c in UNCOVERED if c in recall])),
                **{f"recall__{c}": v for c, v in recall.items()}}


    def error_type(target, prediction):
        if prediction == target:
            return "correct"
        if target != "unknown" and prediction == "unknown":
            return "gate_false_unknown"
        if target == "unknown":
            return "gate_false_accept"
        return "wrong_supported_class"


    def clip_table(indices, gate_scores, class_prob, truth):
        """Notebook 37 rule: mean window gate score vs 0.65; mean window class probability."""
        video = clip_ids[indices]
        rows = []
        for vid in pd.unique(video):
            m = video == vid
            oracle = SUPPORTED_CLASSES[int(class_prob[m].mean(0).argmax())]
            gate = float(gate_scores[m].mean())
            rows.append({"video_id": vid, "window_count": int(m.sum()), "gate_supported_probability": gate,
                         "oracle_exercise": oracle, "prediction": oracle if gate >= FIXED_THRESHOLD else "unknown"})
        t = pd.DataFrame(rows)
        if truth is not None:
            t["label"] = t.video_id.map(truth)
            t["role_group"] = t.video_id.map(dict(zip(ROLES.video_id, ROLES.role_group)))
            t["error_type"] = [error_type(a, b) for a, b in zip(t.label, t.prediction)]
        return t


    def dev_metrics(t):
        recall = {c: float((t.prediction[t.label == c] == c).mean()) for c in TEST_CLASSES if (t.label == c).any()}
        sup = t.label != "unknown"
        return {"clips": int(len(t)),
                "macro_f1_7": float(f1_score(t.label, t.prediction, labels=TEST_CLASSES, average="macro", zero_division=0)),
                "accuracy": float((t.label == t.prediction).mean()),
                "unknown_rejection": recall.get("unknown", float("nan")),
                "gate_false_unknown": int((t.error_type == "gate_false_unknown").sum()),
                "gate_false_accept": int((t.error_type == "gate_false_accept").sum()),
                "wrong_supported_class": int((t.error_type == "wrong_supported_class").sum()),
                "oracle_correct_supported": int((t.oracle_exercise[sup] == t.label[sup]).sum()),
                **{f"recall__{c}": v for c, v in recall.items()}}
    ''')

parity = code(r'''
    frozen_classifier = frozen_exercise_model
    v6f_gates = {s: load_gate(PATHS[f"v6f_{s}_gate.pt"], s) for s in STREAMS}
    v1_clips = clip_table(v1p_idx, fused_score(v6f_gates, v1p_idx), class_probabilities(frozen_classifier, v1p_idx), None)
    with zipfile.ZipFile(PATHS["repcount_report.zip"]) as archive:
        nb37 = pd.read_csv(archive.open("report/video_diagnostics.csv")).set_index("video_id")
    parity = v1_clips.set_index("video_id").join(nb37[["frozen_v6f_prediction", "gate_supported_probability"]], rsuffix="_nb37")
    parity["gate_abs_diff"] = (parity.gate_supported_probability - parity.gate_supported_probability_nb37).abs()
    assert (parity.prediction == parity.frozen_v6f_prediction).all(), parity[parity.prediction != parity.frozen_v6f_prediction]
    assert parity.gate_abs_diff.max() < 1e-3, parity.gate_abs_diff.max()
    print("V6-F parity passed; max gate difference", float(parity.gate_abs_diff.max()))

    dev_class_prob_control = class_probabilities(frozen_classifier, dev_idx)
    test_class_prob_control = class_probabilities(frozen_classifier, test_idx)
    control_tables, control_dev, control_internal = {}, [], []
    for seed in CONTROL_SEEDS:
        gates = {s: load_gate(PATHS[f"control_seed_{seed}_{s}_gate.pt"], s) for s in STREAMS}
        im = internal_metrics(fused_score(gates, test_idx), test_class_prob_control)
        ref = float(nb31_seed_metrics.loc[nb31_seed_metrics.run_seed == seed, "test_end_to_end_macro_f1"].iloc[0])
        assert abs(im["end_to_end_macro_f1"] - ref) < 0.003, (seed, im["end_to_end_macro_f1"], ref)
        t = clip_table(dev_idx, fused_score(gates, dev_idx), dev_class_prob_control, dev_truth)
        control_tables[seed] = t.assign(arm="control", seed=seed)
        control_dev.append({"arm": "control", "seed": seed, **dev_metrics(t)})
        control_internal.append({"arm": "control", "seed": seed, **im, "nb31_reference_macro_f1": ref})
    print("Notebook 31 control parity passed.")
    display(pd.DataFrame(control_dev))
    ''')

treatment = code(r'''
    REPORT = WORK / "calorie_repcount_training_v1_stage_a_report"
    if REPORT.exists():
        shutil.rmtree(REPORT)
    (REPORT / "models").mkdir(parents=True)
    treatment_tables, treatment_dev, treatment_internal, history_rows, best_rows = {}, [], [], [], []
    for seed in RUN_SEEDS:
        classifier, history, best = train_classifier(make_exercise_loaders(seed + 1, exercise_train, exercise_weights, exercise_validation), seed + 1, "cls")
        history_rows += history
        best_rows.append({"seed": seed, "model": "exercise", "best_validation_macro_f1": best})
        torch.save({"exercise_state_dict": classifier.state_dict(), "supported_classes": SUPPORTED_CLASSES, "run_seed": seed},
                   REPORT / "models" / f"seed_{seed}_classifier.pt")
        gates = {}
        for offset, stream in enumerate(STREAMS):
            ts = seed + 100 + offset
            gate, history, best = train_gate(stream, make_stream_loaders(stream, ts, gate_train, gate_weights, validation_indices), ts, "gate")
            gates[stream] = gate
            history_rows += history
            best_rows.append({"seed": seed, "model": stream, "best_validation_macro_f1": best})
            torch.save({"state_dict": gate.state_dict(), "stream": stream, "input_features": STREAMS[stream], "run_seed": seed,
                        "training_seed": ts, "fusion": FIXED_FUSION, "threshold": FIXED_THRESHOLD}, REPORT / "models" / f"seed_{seed}_{stream}_gate.pt")
        t = clip_table(dev_idx, fused_score(gates, dev_idx), class_probabilities(classifier, dev_idx), dev_truth)
        treatment_tables[seed] = t.assign(arm="treatment", seed=seed)
        treatment_dev.append({"arm": "treatment", "seed": seed, **dev_metrics(t)})
        treatment_internal.append({"arm": "treatment", "seed": seed, **internal_metrics(fused_score(gates, test_idx), class_probabilities(classifier, test_idx))})
        del classifier, gates
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        elif DEVICE.type == "mps":
            torch.mps.empty_cache()
    display(pd.DataFrame(treatment_dev))
    ''')

decision = code(r'''
    control_dev_df, treatment_dev_df = pd.DataFrame(control_dev), pd.DataFrame(treatment_dev)
    internal = pd.DataFrame(control_internal + treatment_internal)


    def med(frame, column):
        return float(np.median(frame[column].to_numpy(dtype=float))) if column in frame else float("nan")


    # Role-group bootstrap of the seed-median Macro F1 difference.
    rng = np.random.default_rng(20261027)
    dev_groups = np.array(sorted(set(control_tables[CONTROL_SEEDS[0]].role_group)))
    by_group = {arm: {s: {g: t[t.role_group == g] for g in dev_groups} for s, t in tables.items()}
                for arm, tables in (("control", control_tables), ("treatment", treatment_tables))}
    deltas = []
    for _ in range(2000):
        sample = rng.choice(dev_groups, size=len(dev_groups), replace=True)
        arm_f1 = {}
        for arm in ("control", "treatment"):
            f1s = []
            for s, gmap in by_group[arm].items():
                t = pd.concat([gmap[g] for g in sample])
                f1s.append(f1_score(t.label, t.prediction, labels=TEST_CLASSES, average="macro", zero_division=0))
            arm_f1[arm] = np.median(f1s)
        deltas.append(arm_f1["treatment"] - arm_f1["control"])
    ci = (float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5)))

    delta = med(treatment_dev_df, "macro_f1_7") - med(control_dev_df, "macro_f1_7")
    ti, ci_int = internal[internal.arm == "treatment"], internal[internal.arm == "control"]
    criteria = {
        "macro_f1_gain_at_least_10pp": delta >= 0.10,
        "macro_f1_gain_bootstrap_ci_above_zero": ci[0] > 0,
        "sit_up_recall_at_least_50pct": med(treatment_dev_df, "recall__sit_up") >= 0.50,
        "squat_recall_at_least_60pct": med(treatment_dev_df, "recall__squat") >= 0.60,
        "unknown_rejection_within_5pp_of_control": med(treatment_dev_df, "unknown_rejection") >= med(control_dev_df, "unknown_rejection") - 0.05,
        "internal_macro_f1_within_2pp_of_control": ti.end_to_end_macro_f1.mean() >= ci_int.end_to_end_macro_f1.mean() - 0.02,
        "uncovered_mean_recall_within_5pp_of_control": ti.uncovered_mean_recall.mean() >= ci_int.uncovered_mean_recall.mean() - 0.05,
    }
    verdict = "dry_run_not_a_result" if DRY_RUN else ("stage_a_pass" if all(criteria.values()) else "stage_a_fail")
    stopping_rule = {"stage": STAGE, "verdict": verdict, "criteria": {k: bool(v) for k, v in criteria.items()},
                     "macro_f1_delta": delta, "macro_f1_delta_bootstrap_95ci": ci,
                     "sealed_test_loaded": False, "production_promotion_allowed": False,
                     "next_if_pass": "Stage B: score these frozen models once on the sealed test with the same rule."}
    print(json.dumps(stopping_rule, indent=2))
    summary = pd.concat([control_dev_df, treatment_dev_df], ignore_index=True)
    display(summary)
    display(internal[["arm", "seed", "end_to_end_macro_f1", "unknown_recall", "uncovered_mean_recall"]])

    run_metadata = {
        "notebook": "42_repcount_training_v1_stage_a.ipynb", "experiment": "repcount_training_v1", "stage": STAGE,
        "plan": "ml/data/repcount_intake_v2/TRAINING_PLAN_V1.md", "training_commit": TRAINING_COMMIT,
        "design_commit": DESIGN_COMMIT, "roles_commit": ROLES_COMMIT, "dry_run": DRY_RUN, "device": str(DEVICE),
        "run_seeds": RUN_SEEDS, "control_seeds": CONTROL_SEEDS, "max_epochs": MAX_EPOCHS, "patience": PATIENCE,
        "fixed_fusion": FIXED_FUSION, "fixed_threshold": FIXED_THRESHOLD, "threshold_changed": False,
        "locked_benchmark_read": False, "sealed_test_loaded": False, "repcount_used_for_early_stopping": False,
        "internal_test_used_for_selection": False, "production_promoted": False,
        "repcount_train_windows": int(len(rep_train_idx)), "dev_windows": int(len(dev_idx)),
        "input_hashes": {name: sha256(path) for name, path in PATHS.items()},
    }
    (REPORT / "run_metadata.json").write_text(json.dumps(run_metadata, indent=2) + "\n")
    (REPORT / "stopping_rule.json").write_text(json.dumps(stopping_rule, indent=2) + "\n")
    summary.to_csv(REPORT / "dev_metrics_by_seed.csv", index=False)
    pd.concat(list(control_tables.values()) + list(treatment_tables.values()), ignore_index=True).to_csv(REPORT / "dev_clip_predictions.csv", index=False)
    internal.to_csv(REPORT / "internal_test_metrics.csv", index=False)
    parity.reset_index().to_csv(REPORT / "v6f_parity_check.csv", index=False)
    sampler_audit.to_csv(REPORT / "sampler_audit.csv", index=False)
    pd.DataFrame(history_rows).to_csv(REPORT / "training_history.csv", index=False)
    pd.DataFrame(best_rows).to_csv(REPORT / "best_validation.csv", index=False)
    pd.DataFrame({"delta": deltas}).to_csv(REPORT / "bootstrap_macro_f1_delta.csv", index=False)
    shutil.copy2(PATHS["training_v1_roles.csv"], REPORT / "training_v1_roles.csv")
    (REPORT / "README.md").write_text(
        "# cALorie RepCount-A training v1, stage A\n\n"
        + ("DRY RUN: one epoch on subsamples. Not a result.\n\n" if DRY_RUN else "")
        + "Classifier and gates retrained with RepCount train clips; scored on RepCount dev clips and the internal test. "
        "The sealed test and locked benchmark were not read. Non-promotable. Verdict: " + verdict + "\n"
    )
    lines = [f"{sha256(p)}  {p.relative_to(REPORT)}" for p in sorted(q for q in REPORT.rglob("*") if q.is_file())]
    (REPORT / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n")
    zip_path = Path(shutil.make_archive(str(WORK / ("calorie_repcount_training_v1_stage_a_report" + ("_DRYRUN" if DRY_RUN else ""))), "zip", root_dir=REPORT))
    print("Created:", zip_path, round(zip_path.stat().st_size / 1e6, 1), "MB")
    ''')

cells = [
    md("""
        # cALorie Notebook 42 — RepCount-A training v1, stage A

        **Runtime: GPU (T4 on Colab, or the Mac GPU with `CALORIE_DEVICE=mps`). Run all.**
        Output: `calorie_repcount_training_v1_stage_a_report.zip`.

        Runs `ml/data/repcount_intake_v2/TRAINING_PLAN_V1.md`, stage A, once:

        - Retrains the 14-class classifier (Notebook 26 recipe) and the joint, bone, and velocity
          gates (Notebook 31 recipe), adding RepCount train clips to the existing pool.
        - Scores on RepCount **dev** clips and the internal test. The sealed test is never loaded.
        - Control: frozen V6-F (V6-E classifier plus Notebook 31's archived gates).
        - Threshold 0.65 and fusion fixed; early stopping on the existing V6-A validation only.
        - Non-promotable. No rerun except for a crash or bug.
        """),
    code("%pip install -q scikit-learn pandas==2.2.3\n"),
    config,
    md("## Download pinned inputs\n"),
    inputs,
    md("## Rebuild Notebook 31's exact training pool\n"),
    code(nb39[6]),
    md("## Add RepCount train and dev clips (sealed test excluded)\n"),
    repcount,
    md("## Sampler, augmentation, and datasets\n"),
    sampler,
    md("## Models and trainer (Notebooks 26 and 31)\n"),
    trainer,
    md("## Fixed scoring\n"),
    scoring,
    md("## Parity checks and control\n"),
    parity,
    md("## Treatment: retrain classifier and gates, three seeds\n"),
    treatment,
    md("## Predeclared stage-A rule and report\n"),
    decision,
]
notebook = {
    "cells": cells,
    "metadata": {"accelerator": "GPU", "colab": {"name": OUTPUT.name, "provenance": [], "gpuType": "T4"},
                 "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python", "version": "3"}},
    "nbformat": 4, "nbformat_minor": 5,
}
OUTPUT.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n")
print(OUTPUT)
