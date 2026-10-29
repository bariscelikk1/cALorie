// Builds ml/artifacts/final_model_v2/cALorie_final_presentation.pptx with pptxgenjs. Run from the repo root with NODE_PATH set
// to a pptxgenjs install; apply_theme.js comes from the Claude pptx skill (path at the top of this file).
const pptxgen = require("pptxgenjs");
const SK = "/Users/bariscelik/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/b465db97-b9a0-4dbf-befb-432c39c8b208/f259e31d-127a-4748-9036-c00313f03f40/skills/pptx";
const { applyTheme } = require(SK + "/scripts/apply_theme.js");
const FIG = "ml/artifacts/final_model_v2/figures/";
const THEME = { name: "cALorie", headFontFace: "Cambria", bodyFontFace: "Calibri",
  colors: { dk1: "1B1F2A", lt1: "FFFFFF", dk2: "2E3447", lt2: "F2F3F7", accent1: "EB6834", accent2: "6250D6", accent3: "2A78D6",
            accent4: "1BAF7A", accent5: "EDA100", accent6: "9C9C97", hlink: "2A78D6", folHlink: "6250D6" } };
const pres = new pptxgen(); pres.layout = "LAYOUT_16x9"; pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "cALorie: teaching a computer to name your exercise"; pres.author = "cALorie project";
const C = pres.SchemeColor;

pres.defineSlideMaster({ title: "TITLE_DARK", background: { color: "1B1F2A" },
  objects: [], slideNumber: undefined });
pres.defineSlideMaster({ title: "CONTENT", background: { color: "FFFFFF" },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 8.8, h: 0.9, fontSize: 32, bold: true, color: C.text1, fontFace: "Cambria", align: "left", valign: "top", margin: 0 }, text: "" } }],
  slideNumber: { x: 9.1, y: 5.2, w: 0.5, h: 0.3, fontSize: 10, color: C.accent6, fontFace: "Calibri", align: "right" } });

const section = (t) => pres.addSection({ title: t });
const notes = (s, t) => s.addNotes(t);
const stat = (s, x, y, w, big, label, color) => {
  s.addText(big, { x, y, w, h: 1.0, fontSize: 54, bold: true, fontFace: "Cambria", color, align: "left", valign: "top", margin: 0, isTextBox: true, objectName: "stat " + big });
  s.addText(label, { x, y: y + 1.0, w, h: 0.9, fontSize: 16, fontFace: "Calibri", color: C.text2, align: "left", valign: "top", margin: 0, isTextBox: true, objectName: "label " + big });
};

// 1 ---------------------------------------------------------------------------------------------------------
section("Intro");
let s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Intro" });
s.addText("cALorie", { x: 0.7, y: 1.5, w: 8.6, h: 1.0, fontSize: 54, bold: true, fontFace: "Cambria", color: C.background1, margin: 0, isTextBox: true, objectName: "title" });
s.addText("Teaching a computer to name your exercise from a workout video", { x: 0.7, y: 2.6, w: 8.0, h: 0.9, fontSize: 24, fontFace: "Calibri", color: "CFD3E3", margin: 0, isTextBox: true, objectName: "subtitle" });
s.addText("Pose-based exercise recognition · final project · 2026", { x: 0.7, y: 4.6, w: 8.0, h: 0.4, fontSize: 14, fontFace: "Calibri", color: C.accent6, margin: 0, isTextBox: true, objectName: "footer" });
for (let i = 0; i < 5; i++) s.addShape(pres.shapes.OVAL, { x: 7.35 + i * 0.4, y: 0.6, w: 0.22, h: 0.22, fill: { color: [C.accent1, C.accent2, C.accent3, C.accent4, C.accent5][i] }, line: { type: "none" }, objectName: "dot " + i });
notes(s, "cALorie watches a workout video and says which exercise you are doing, minute by minute. This talk covers how it works, what we measured, and where it still fails.");

// 2 ---------------------------------------------------------------------------------------------------------
section("Method");
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Method" });
s.addText("From video to an exercise timeline", { placeholder: "title" });
const steps = [["Video", "a workout, 20–45 min", C.accent3], ["Pose", "17 body joints found in every frame (MediaPipe)", C.accent4],
  ["Gate", "is this a known exercise, or rest or something else?", C.accent5], ["Classifier", "which of 14 exercises is it?", C.accent1], ["Timeline", "“0:45–1:30 squats …”", C.accent2]];
steps.forEach((st, i) => {
  const x = 0.6 + i * 1.84;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.75, w: 1.5, h: 2.1, rectRadius: 0.08, fill: { color: C.background2 }, line: { type: "none" }, objectName: "step card " + i });
  s.addShape(pres.shapes.OVAL, { x: x + 0.55, y: 1.95, w: 0.4, h: 0.4, fill: { color: st[2] }, line: { type: "none" }, objectName: "step dot " + i });
  s.addText(st[0], { x: x + 0.08, y: 2.45, w: 1.34, h: 0.4, fontSize: 18, bold: true, fontFace: "Cambria", color: C.text1, align: "center", margin: 0, isTextBox: true, objectName: "step name " + i });
  s.addText(st[1], { x: x + 0.1, y: 2.9, w: 1.3, h: 0.9, fontSize: 12, fontFace: "Calibri", color: C.text2, align: "center", valign: "top", margin: 0, isTextBox: true, objectName: "step text " + i });
  if (i < 4) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 1.53, y: 2.65, w: 0.27, h: 0.28, fill: { color: C.accent6 }, line: { type: "none" }, objectName: "arrow " + i });
});
s.addText("Two small neural networks read how the body moves over about 4 seconds. Rests, warm-ups, and moves we don’t support should come out as “unknown”.", { x: 0.6, y: 4.2, w: 8.8, h: 0.8, fontSize: 16, fontFace: "Calibri", color: C.text2, margin: 0, isTextBox: true, objectName: "caption" });
notes(s, "The model never looks at pixels. MediaPipe turns each frame into 17 body points. A gate decides if a moment is a supported exercise. A classifier names it. A smoothing step turns the flickering predictions into clean segments.");

// 3 ---------------------------------------------------------------------------------------------------------
section("Problem");
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Problem" });
s.addText("Short clips looked great. Real workouts did not", { placeholder: "title" });
stat(s, 0.6, 1.7, 2.7, "82%", "score on short, trimmed clips (the usual test)", C.accent3);
stat(s, 3.65, 1.7, 2.7, "33%", "score on full, real workouts it had never seen", C.accent1);
stat(s, 6.7, 1.7, 2.7, "55%", "of real exercise time thrown away as “unknown”", C.accent2);
s.addText("Real sessions have rests, timers, intros, camera changes, and exercises the model barely knew: sit-up, row, lunge, shoulder press, and triceps all scored 0%.", { x: 0.6, y: 3.95, w: 8.8, h: 0.9, fontSize: 16, fontFace: "Calibri", color: C.text2, margin: 0, isTextBox: true, objectName: "caption" });
notes(s, "Macro F1 averages the score over exercises so rare ones count equally. 82 percent was the old internal test of short clips. On eight full follow-along workouts, the same model scored 33 percent, and more than half of the real exercise time was rejected.");

// 4 ---------------------------------------------------------------------------------------------------------
section("Data");
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Data" });
s.addText("The fix: label real workouts, second by second", { placeholder: "title" });
stat(s, 0.6, 1.7, 2.7, "38", "workout videos, labeled by hand-written rules", C.accent1);
stat(s, 3.65, 1.7, 2.7, "19 h", "of real follow-along workouts, raw video deleted", C.accent2);
stat(s, 6.7, 1.7, 2.7, "100%", "of 210 random segments spot-checked by hand were correct", C.accent4);
s.addText("Every second is rest, warm-up, a supported exercise, or “unknown”. Two sets of videos were locked away and never used to train or tune anything.", { x: 0.6, y: 3.95, w: 8.8, h: 0.9, fontSize: 16, fontFace: "Calibri", color: C.text2, margin: 0, isTextBox: true, objectName: "caption" });
notes(s, "We collected 38 follow-along videos from creators we had not used before, screened out vlogs and montages, and labeled every second using a 23-rule annotation guide. The spot checks were 44 of 44, 95 of 95, and 71 of 71 correct. Two test sets were locked with file fingerprints before any model was scored.");

// 5 ---------------------------------------------------------------------------------------------------------
section("Results");
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Results" });
s.addText("More real workouts raised the score every time", { placeholder: "title" });
s.addImage({ path: FIG + "model_progression.png", x: 0.6, y: 1.3, w: 8.8, h: 3.87, altText: "Bar charts of Macro F1 on two locked test sets: 32.6, 32.3 and 47.6 percent on test 1; 38.7 and 43.5 percent on test 2", objectName: "chart progression" });
notes(s, "Left: eight unseen workouts. The early model and the short-clip model scored about 32 percent. Adding eleven long videos gave 47.6 percent. Right: six brand-new workouts from new creators. Final v1 scored 38.7 percent; adding more data gave 43.5 percent, with all four pre-set criteria met. The two tests are different videos, so compare bars within a panel.");

// 6 ---------------------------------------------------------------------------------------------------------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Results" });
s.addText("Weak exercises improved; row slipped", { placeholder: "title" });
s.addImage({ path: FIG + "weak_classes.png", x: 0.9, y: 1.3, w: 8.2, h: 3.94, altText: "Grouped bars of recognized time per exercise for final v1 and v2: lateral raise 5 to 64, bicep curl 65 to 81, tricep extension 60 to 72, dumbbell row 41 to 22", objectName: "chart weak classes" });
notes(s, "Lateral raise went from 5 to 64 percent, curls 65 to 81, triceps 60 to 72. Dumbbell row dropped from 41 to 22, and squat from 95 to 88. We report that honestly: more data is not better for every exercise at once.");

// 7 ---------------------------------------------------------------------------------------------------------
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Results" });
s.addText("What the model sees, minute by minute", { placeholder: "title" });
s.addImage({ path: FIG + "timeline_example.png", x: 0.6, y: 1.3, w: 8.8, h: 2.08, altText: "Timeline of one unseen workout: hand-labeled exercise blocks on top, model prediction below", objectName: "chart timeline" });
s.addText([{ text: "Gets right", options: { bold: true, color: C.accent4, fontSize: 18, fontFace: "Cambria", breakLine: true } },
  { text: "Most curl and triceps blocks are found in the right place.", options: { bullet: true, breakLine: true } },
  { text: "Rests and timer screens mostly stay “unknown”.", options: { bullet: true } }],
  { x: 0.6, y: 3.65, w: 4.2, h: 1.5, fontSize: 14, fontFace: "Calibri", color: C.text2, valign: "top", paraSpaceAfter: 4, margin: 0, isTextBox: true, objectName: "right column" });
s.addText([{ text: "Still gets wrong", options: { bold: true, color: C.accent1, fontSize: 18, fontFace: "Cambria", breakLine: true } },
  { text: "About 30% of real exercise time is still missed.", options: { bullet: true, breakLine: true } },
  { text: "Many rows and lateral raises become “unknown”.", options: { bullet: true } }],
  { x: 5.2, y: 3.65, w: 4.2, h: 1.5, fontSize: 14, fontFace: "Calibri", color: C.text2, valign: "top", paraSpaceAfter: 4, margin: 0, isTextBox: true, objectName: "wrong column" });
notes(s, "This is one real unseen workout from the second test. Top row is what a human labeled; bottom row is the model. The match is imperfect, which is why we also report the numbers, not just pictures.");

// 8 ---------------------------------------------------------------------------------------------------------
section("Method honesty");
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Method honesty" });
s.addText("How we kept the results honest", { placeholder: "title" });
const rows = [["Rules before results", "Every experiment’s pass rule was written and pushed before it ran.", C.accent1],
  ["Locked tests", "Test videos were fingerprinted and never used for training or tuning.", C.accent2],
  ["Failures kept", "Experiments that missed a bar are reported as failures, not hidden.", C.accent3],
  ["Humans in the loop", "Labels follow a written guide; I checked random samples by eye.", C.accent4]];
rows.forEach((r, i) => {
  const y = 1.45 + i * 0.88;
  s.addShape(pres.shapes.OVAL, { x: 0.6, y: y + 0.05, w: 0.55, h: 0.55, fill: { color: r[2] }, line: { type: "none" }, objectName: "number circle " + i });
  s.addText(String(i + 1), { x: 0.6, y: y + 0.05, w: 0.55, h: 0.55, fontSize: 20, bold: true, fontFace: "Cambria", color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "number " + i });
  s.addText(r[0], { x: 1.4, y, w: 7.9, h: 0.35, fontSize: 18, bold: true, fontFace: "Cambria", color: C.text1, margin: 0, isTextBox: true, objectName: "row title " + i });
  s.addText(r[1], { x: 1.4, y: y + 0.36, w: 7.9, h: 0.4, fontSize: 14, fontFace: "Calibri", color: C.text2, margin: 0, isTextBox: true, objectName: "row text " + i });
});
notes(s, "Two earlier experiments missed their pass rule and were reported as failures. The first full retraining failed on the gate; the rebalanced one came close but also missed the bar by five points. We froze it anyway, labeled as not passing, and scored it once on the locked test.");

// 9 ---------------------------------------------------------------------------------------------------------
section("Demo");
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Demo" });
s.addText("A small local app: upload a video, get the timeline", { placeholder: "title" });
s.addText([{ text: "Runs on your own computer. One command starts it.", options: { bullet: true, breakLine: true } },
  { text: "Shows the exercise timeline and time per exercise.", options: { bullet: true, breakLine: true } },
  { text: "Counts reps for 5 exercises and estimates calories with a ±35% range.", options: { bullet: true, breakLine: true } },
  { text: "Your video is never uploaded anywhere.", options: { bullet: true } }],
  { x: 0.6, y: 1.5, w: 4.6, h: 2.6, fontSize: 16, fontFace: "Calibri", color: C.text2, valign: "top", paraSpaceAfter: 8, margin: 0, isTextBox: true, objectName: "demo bullets" });
stat(s, 5.7, 1.5, 3.6, "68%", "of unseen clips counted within one rep of a human (sealed test)", C.accent2);
s.addText("Calories use one fixed MET value per exercise and could not be validated.", { x: 5.7, y: 3.7, w: 3.6, h: 0.9, fontSize: 14, fontFace: "Calibri", color: C.text2, margin: 0, isTextBox: true, objectName: "calorie note" });
notes(s, "The web page is a Streamlit script. Reps come from a simple peak counter tuned on dev clips and scored once on a sealed test: 68 percent within one rep, 39 percent exact. Calories use the standard formula with a fixed MET per exercise and a plus or minus 35 percent range, because we have no ground truth for them.");

// 10 --------------------------------------------------------------------------------------------------------
section("Wrap-up");
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Wrap-up" });
s.addText("Limits, and what comes next", { placeholder: "title" });
s.addText([{ text: "Limits", options: { bold: true, color: C.accent1, fontSize: 20, fontFace: "Cambria", breakLine: true } },
  { text: "Tested on only 6 (and 8) unseen workouts.", options: { bullet: true, breakLine: true } },
  { text: "About 30% of real exercise time is still missed.", options: { bullet: true, breakLine: true } },
  { text: "Dumbbell row and squat got worse in round 2.", options: { bullet: true, breakLine: true } },
  { text: "Reps and calories are approximate.", options: { bullet: true } }],
  { x: 0.6, y: 1.5, w: 4.2, h: 3.3, fontSize: 15, fontFace: "Calibri", color: C.text2, valign: "top", paraSpaceAfter: 6, margin: 0, isTextBox: true, objectName: "limits" });
s.addText([{ text: "Next", options: { bold: true, color: C.accent2, fontSize: 20, fontFace: "Cambria", breakLine: true } },
  { text: "More workouts from more people for the weak exercises.", options: { bullet: true, breakLine: true } },
  { text: "A fresh locked test, since these are now spent.", options: { bullet: true, breakLine: true } },
  { text: "Better rep counting and a real calorie check.", options: { bullet: true, breakLine: true } },
  { text: "A friendlier app on top.", options: { bullet: true } }],
  { x: 5.2, y: 1.5, w: 4.2, h: 3.3, fontSize: 15, fontFace: "Calibri", color: C.text2, valign: "top", paraSpaceAfter: 6, margin: 0, isTextBox: true, objectName: "next" });
notes(s, "The honest summary: each round of real workout data helped, the model is still research-grade, and the next step is more varied data and a fresh test set.");

(async () => { await pres.writeFile({ fileName: "cALorie_final.pptx" }); await applyTheme("cALorie_final.pptx", THEME); console.log("built"); })();
