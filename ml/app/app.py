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
import reps_and_calories as rc

st.set_page_config(page_title="cALorie", page_icon="🏋️")
st.title("cALorie")
st.caption("Exercise timeline from a workout video (research prototype). Your video stays on this computer.")


@st.cache_resource
def get_models():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    return device, cp.load_final_model(torch.device(device))


weight = st.number_input("Your body weight (kg), used only for the calorie estimate", 30.0, 250.0, 70.0, 1.0)
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
        st.subheader("Per exercise")
        summary = rc.summarize_exercises(table, pose, weight)
        shown_summary = summary.assign(
            exercise=summary.exercise.str.replace("_", " "),
            reps=summary.reps.map(lambda v: "not validated" if v != v or v is None else str(int(v))),
            calories=summary.apply(lambda r: f"{r.kcal} ({r.kcal_low}-{r.kcal_high})", axis=1))[["exercise", "seconds", "reps", "calories"]]
        st.dataframe(shown_summary, hide_index=True)
        st.metric("Estimated calories (recognized exercise time only)", f"{int(summary.kcal.sum())} kcal",
                  f"range {int(summary.kcal_low.sum())}-{int(summary.kcal_high.sum())}", delta_color="off")

    st.subheader("Segments")
    shown = table.assign(start=table.start_s.map(cp.fmt), end=table.end_s.map(cp.fmt),
                         label=table.label.str.replace("_", " "))[["start", "end", "label"]]
    st.dataframe(shown, hide_index=True)
    st.download_button("Download timeline (CSV)", table.to_csv(index=False), "timeline.csv", "text/csv")
    st.caption("Accuracy on unseen full workouts: 47.6% Macro F1; about 39% of real exercise time is missed and tricep extension is "
               "not recognized. Reps are shown only for the five exercises where the counter was checked (about 68% of RepCount test clips were within one rep) "
               "and calories use one fixed MET per exercise with a ±35% range. See FINAL_REPORT.md.")
