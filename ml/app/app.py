"""Small local web page for cALorie: upload a workout video, get the exercise timeline.

Run:  streamlit run ml/app/app.py
The video is processed on this computer and never uploaded anywhere.
"""

import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st
import torch

import calorie_pipeline as cp

st.set_page_config(page_title="cALorie", page_icon="🏋️")
st.title("cALorie")
st.caption("Exercise timeline from a workout video (research prototype). Your video stays on this computer.")


@st.cache_resource
def get_models():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    return device, cp.load_final_model(torch.device(device))


upload = st.file_uploader("Workout video (one person, whole body in view)", type=["mp4", "mov", "m4v", "webm", "mkv"])
if upload is not None:
    device, models = get_models()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / upload.name
        path.write_bytes(upload.getbuffer())
        bar = st.progress(0.0, text="Finding the body in each frame...")
        pose, rate = cp.extract_pose(path, lambda p: bar.progress(p, text="Finding the body in each frame..."))
        bar.progress(1.0, text="Recognizing exercises...")
        table = cp.timeline(pose, device, models)
        bar.empty()

    if rate < 0.5:
        st.warning(f"The body was found in only {rate:.0%} of frames, so results will be unreliable. Use a video with the whole body in view.")

    exercise = table[table.label != "unknown"].copy()
    exercise["seconds"] = exercise.end_s - exercise.start_s
    total = len(pose) / cp.FPS
    st.subheader("Timeline")
    labels = sorted(set(table.label) - {"unknown"})
    colors = {name: plt.cm.tab20(i % 20) for i, name in enumerate(labels)}
    fig, ax = plt.subplots(figsize=(8, 1.4))
    for r in table.itertuples():
        ax.barh(0, (r.end_s - r.start_s) / 60, left=r.start_s / 60, color="#d9d9d9" if r.label == "unknown" else colors[r.label])
    ax.set_yticks([]); ax.set_xlim(0, total / 60); ax.set_xlabel("minutes")
    ax.legend([plt.Rectangle((0, 0), 1, 1, color=colors[n]) for n in labels], [n.replace("_", " ") for n in labels],
              ncol=4, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, -0.5), frameon=False)
    st.pyplot(fig, clear_figure=True)

    if exercise.empty:
        st.info("No supported exercise was recognized in this video.")
    else:
        st.subheader("Time per exercise")
        per = exercise.groupby("label").seconds.sum().sort_values(ascending=False)
        st.dataframe(per.rename("seconds").round(0).astype(int).rename_axis("exercise").reset_index().assign(
            exercise=lambda d: d.exercise.str.replace("_", " ")), hide_index=True)

    st.subheader("Segments")
    shown = table.assign(start=table.start_s.map(cp.fmt), end=table.end_s.map(cp.fmt),
                         label=table.label.str.replace("_", " "))[["start", "end", "label"]]
    st.dataframe(shown, hide_index=True)
    st.download_button("Download timeline (CSV)", table.to_csv(index=False), "timeline.csv", "text/csv")
    st.caption("Accuracy on unseen full workouts: 47.6% Macro F1; about 39% of real exercise time is missed and tricep extension is "
               "not recognized. Reps and calories are not estimated. See FINAL_REPORT.md.")
