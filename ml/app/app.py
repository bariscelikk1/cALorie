"""cALorie: a small local web page. Upload a workout video (long ones are fine) and get the exercise timeline.

Run:  ./ml/app/run_app.sh      (opens http://localhost:8501)
Everything runs on this computer; the video is never uploaded anywhere.
"""

import hashlib
import io
import tempfile
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import torch

import calorie_pipeline as cp
import reps_and_calories as rc

ORANGE, VIOLET, BLUE, AQUA, YELLOW = "#EB6834", "#8F84F0", "#5B9BEB", "#2FCB93", "#EDA100"
PALETTE = {"squat": BLUE, "push_up": ORANGE, "jumping_jack": YELLOW, "pull_up": AQUA, "lunge": "#E87BA4", "sit_up": VIOLET,
           "bench_press": "#C98500", "deadlift": "#6EC1E4", "shoulder_press": "#F2A65A", "dumbbell_row": "#7DD3A8",
           "tricep_extension": "#D96BB6", "bicep_curl": "#9FB4FF", "lateral_raise": "#FFD166", "lat_pulldown": "#B8A1FF"}
REST = "#2B3042"

st.set_page_config(page_title="cALorie", page_icon="🏋️", layout="centered")
st.markdown(f"""
<style>
.block-container {{ padding-top: 2.2rem; max-width: 880px; }}
.hero h1 {{ font-size: 3.1rem; margin: 0; letter-spacing: -1px; }}
.hero h1 span {{ color: {ORANGE}; }}
.hero p {{ color: #B9BDD0; font-size: 1.1rem; margin: .2rem 0 1.2rem; }}
.steps {{ display: flex; gap: .6rem; margin-bottom: 1.2rem; }}
.step {{ flex: 1; background: #1C2130; border-radius: 12px; padding: .7rem .9rem; font-size: .9rem; color: #B9BDD0; }}
.step b {{ color: #F2F3F7; display: block; }}
.card {{ background: #1C2130; border-radius: 14px; padding: 1rem 1.1rem; }}
.card .big {{ font-size: 2rem; font-weight: 700; line-height: 1.1; }}
.card .small {{ color: #B9BDD0; font-size: .85rem; }}
div[data-testid="stFileUploader"] section {{ border: 2px dashed #3A4160; border-radius: 16px; padding: 1.6rem; }}
</style>
<div class="hero"><h1>c<span>AL</span>orie</h1><p>Drop in a workout video. Get the exercises, minute by minute.</p></div>
<div class="steps"><div class="step"><b>1 · Upload</b>any workout video, long ones too</div>
<div class="step"><b>2 · Analyze</b>on your computer, nothing leaves it</div>
<div class="step"><b>3 · Timeline</b>exercises, reps, calories (estimates)</div></div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Settings")
    weight = st.number_input("Your body weight (kg), only for the calorie estimate", 30.0, 250.0, 70.0, 1.0)
    effort_name = st.select_slider("How hard was the workout?", options=list(rc.EFFORT), value="Moderate",
                                   help="Scales the calorie estimate: light about 3.5 MET, moderate 5, hard 6 for weight training.")
    effort = rc.EFFORT[effort_name]
    with st.expander("Optional: use your heart rate"):
        avg_hr = st.number_input("Average heart rate during the workout (bpm), 0 = skip", 0, 220, 0, 1)
        age = st.number_input("Age", 10, 90, 22, 1)
        male = st.radio("Sex (for the formula)", ["Male", "Female"], horizontal=True) == "Male"
    st.caption("Processing takes roughly a quarter to a half of the video's length on a laptop. Keep this tab open.")
    st.divider()
    st.caption("Works best with one person, whole body in view, steady camera.")


@st.cache_resource
def get_models():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    return device, cp.load_final_model(torch.device(device))


def fmt(seconds):
    return f"{int(seconds // 60)}:{int(seconds % 60):02d}"


def analyze(upload):
    """Return (pose, detection rate, timeline table); cached by file hash for this session."""
    data = upload.getvalue()
    key = hashlib.sha256(data).hexdigest()
    cache = st.session_state.setdefault("results", {})
    if key in cache:
        return cache[key]
    device, models = get_models()
    started = time.time()
    with st.status("Analyzing your video…", expanded=True) as status:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / upload.name
            path.write_bytes(data)
            st.write("Reading the video and finding the body in every frame…")
            bar = st.progress(0.0)
            pose, rate = cp.extract_pose(path, lambda p: bar.progress(min(p, 1.0), text=f"{p:.0%} of frames  ·  {fmt(time.time() - started)} elapsed"))
            bar.progress(1.0)
        st.write("Recognizing the exercises…")
        table = cp.timeline(pose, device, models)
        status.update(label=f"Done in {fmt(time.time() - started)}", state="complete", expanded=False)
    cache[key] = (pose, rate, table)
    return cache[key]


def timeline_figure(table, total):
    fig, ax = plt.subplots(figsize=(9, 1.5)); fig.patch.set_alpha(0); ax.set_facecolor("none")
    for r in table.itertuples():
        w = (r.end_s - r.start_s) / 60
        ax.barh(0, w, left=r.start_s / 60, height=0.7, color=REST if r.label == "unknown" else PALETTE.get(r.label, VIOLET), edgecolor="#12151C", linewidth=1)
        if r.label != "unknown" and w > total / 60 * 0.045:
            ax.text(r.start_s / 60 + w / 2, 0, r.label.replace("_", " "), ha="center", va="center", fontsize=7, color="#12151C", fontweight="bold", rotation=0)
    ax.set_xlim(0, total / 60); ax.set_yticks([]); ax.set_xlabel("minutes", color="#B9BDD0")
    ax.tick_params(colors="#B9BDD0")
    for spine in ax.spines.values():
        spine.set_visible(False)
    return fig


upload = st.file_uploader("Choose a workout video", type=["mp4", "mov", "m4v", "webm", "mkv"], label_visibility="collapsed")
if upload is None:
    st.info("Pick a video above to start. A 30-minute workout takes roughly 8–15 minutes to analyze.")
    st.stop()

pose, rate, table = analyze(upload)
total = len(pose) / cp.FPS
if rate < 0.5:
    st.warning(f"The body was found in only {rate:.0%} of frames, so results will be unreliable. Use a video with the whole body in view.")

summary = rc.summarize_exercises(table, pose, weight, effort)
exercise_s = float(summary.seconds.sum()) if len(summary) else 0.0
# Calories two ways: only the exercise the model recognized (a floor, because missed time counts as zero), and a rough
# whole-session figure at a general strength-training MET (3.5) over the full video length.
session_kcal = rc.MET_SESSION * effort * 3.5 * weight / 200.0 * (total / 60.0)
hr_kcal = rc.heart_rate_kcal(avg_hr, weight, age, male, total / 60.0) if avg_hr > 0 else None
cols = st.columns(3)
cards = [(fmt(total), "workout length"), (fmt(exercise_s), "exercise time found"), (str(len(summary)), "exercises found")]

for col, (big, small) in zip(cols, cards):
    col.markdown(f'<div class="card"><div class="big">{big}</div><div class="small">{small}</div></div>', unsafe_allow_html=True)
st.write("")
cols2 = st.columns(3 if avg_hr > 0 else 2)
cards2 = [(f"{int(summary.kcal.sum())}" if len(summary) else "0", "kcal from the exercises found (a minimum: missed time counts as zero)"),
          (f"{int(session_kcal)}", f"kcal for the whole session ({effort_name.lower()} effort, rough)")]
if hr_kcal is not None:
    cards2.append((f"{int(hr_kcal)}", "kcal from your average heart rate (Keytel formula, whole session)"))
for col, (big, small) in zip(cols2, cards2):
    col.markdown(f'<div class="card"><div class="big">{big}</div><div class="small">{small}</div></div>', unsafe_allow_html=True)
st.write("")
st.subheader("Timeline")
buf = io.BytesIO()
timeline_figure(table, total).savefig(buf, format="png", transparent=True, dpi=200, bbox_inches="tight")
plt.close("all")
st.image(buf)

if summary.empty:
    st.info("No supported exercise was recognized in this video.")
else:
    st.subheader("Exercises")
    shown = pd.DataFrame({"exercise": summary.exercise.str.replace("_", " "), "time": summary.seconds.map(fmt),
                          "reps": summary.reps.map(lambda v: "not validated" if v != v or v is None else str(int(v))),
                          "calories (range)": summary.apply(lambda r: f"{r.kcal}  ({r.kcal_low}–{r.kcal_high})", axis=1)})
    st.dataframe(shown, hide_index=True, width="stretch")

with st.expander("All segments"):
    seg = table.assign(start=table.start_s.map(fmt), end=table.end_s.map(fmt), label=table.label.str.replace("_", " "))[["start", "end", "label"]]
    st.dataframe(seg, hide_index=True, width="stretch")
st.download_button("Download timeline (CSV)", table.to_csv(index=False), "timeline.csv", "text/csv")

with st.expander("How accurate is this?"):
    st.write("Research prototype. On 6 unseen full workouts it scores 43.5% Macro F1; about 30% of real exercise time is still missed and "
             "dumbbell row is weak. Reps are shown only for the five exercises where the counter was checked (about 68% of RepCount test clips "
             "were within one rep). Calories use one fixed MET value per exercise with a ±35% range and were not validated. See FINAL_REPORT.md.")
