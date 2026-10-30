const labels = [
  "bench_press", "bicep_curl", "deadlift", "dumbbell_row", "jumping_jack",
  "lat_pulldown", "lateral_raise", "lunge", "pull_up", "push_up",
  "shoulder_press", "sit_up", "squat", "tricep_extension", "unknown"
];

const reasonText = {
  medium_confidence_variant_boundary: "Varyant / sınır kontrolü",
  medium_confidence_corrected_first_pass: "İlk tur düzeltmesi",
  medium_confidence_slow_instructional_demo: "Yavaş öğretici gösterim",
  medium_confidence_supplemental_pose_plus_rgb: "RGB + pose kanıtı",
  compound_unknown_edge_case: "Bileşik hareket / unknown kontrolü",
  rotational_compound_unknown_edge_case: "Dönüşümlü bileşik hareket",
  stratified_high_confidence_and_wrong_ui_correction: "Yüksek güven kontrolü · eski UI hatası",
  stratified_high_confidence_boundary_check: "Yüksek güven sınır kontrolü",
  stratified_high_confidence_motion_change_check: "Hareket değişimi kontrolü"
};

const dense = id => ({ type: "dense", overview: `assets/dense/${id}.jpg` });
const supplemental = (id, context, count) => ({
  type: "supplemental",
  context: `assets/supplemental/coarse/${context}.jpg`,
  pages: Array.from({ length: count }, (_, i) => `assets/supplemental/${id}/${String(i).padStart(3, "0")}.jpg`)
});

const queue = [
  {order:1,id:"michelle_deadlift_01",reason:"medium_confidence_variant_boundary",decision:"accept_supported",label:"deadlift",start:665,end:755,evidence:dense("michelle_deadlift_01")},
  {order:2,id:"michelle_deadlift_02",reason:"medium_confidence_variant_boundary",decision:"accept_supported",label:"deadlift",start:831,end:865,evidence:dense("michelle_deadlift_02")},
  {order:3,id:"michelle_deadlift_03",reason:"medium_confidence_corrected_first_pass",decision:"accept_supported",label:"deadlift",start:995,end:1045,evidence:dense("michelle_deadlift_03")},
  {order:4,id:"critical_deadlift_01",reason:"medium_confidence_slow_instructional_demo",decision:"accept_supported",label:"deadlift",start:624,end:645,evidence:dense("critical_deadlift_01")},
  {order:5,id:"michelle_bench_01",reason:"medium_confidence_supplemental_pose_plus_rgb",decision:"accept_supported",label:"bench_press",start:278,end:327,evidence:supplemental("michelle_bench_01","002",12)},
  {order:6,id:"michelle_bench_02",reason:"medium_confidence_supplemental_pose_plus_rgb",decision:"accept_supported",label:"bench_press",start:362,end:399,evidence:supplemental("michelle_bench_02","003",10)},
  {order:7,id:"michelle_lateral_01",reason:"medium_confidence_supplemental_pose_plus_rgb",decision:"accept_supported",label:"lateral_raise",start:1940,end:1972,evidence:supplemental("michelle_lateral_01","016",10)},
  {order:8,id:"michelle_lateral_02",reason:"medium_confidence_supplemental_pose_plus_rgb",decision:"accept_supported",label:"lateral_raise",start:2052,end:2100,evidence:supplemental("michelle_lateral_02","017",11)},
  {order:9,id:"tiff_lateral_01",reason:"compound_unknown_edge_case",decision:"accept_unknown",label:"unknown",start:91,end:130,evidence:dense("tiff_lateral_01")},
  {order:10,id:"tiff_lateral_02",reason:"compound_unknown_edge_case",decision:"accept_unknown",label:"unknown",start:271,end:310,evidence:dense("tiff_lateral_02")},
  {order:11,id:"tiff_bench_01",reason:"rotational_compound_unknown_edge_case",decision:"accept_unknown",label:"unknown",start:1111,end:1148,evidence:dense("tiff_bench_01")},
  {order:12,id:"tiff_bench_02",reason:"rotational_compound_unknown_edge_case",decision:"accept_unknown",label:"unknown",start:1291,end:1328,evidence:dense("tiff_bench_02")},
  {order:13,id:"ojs_squat_01",reason:"stratified_high_confidence_and_wrong_ui_correction",decision:"accept_supported",label:"squat",start:93,end:123,evidence:dense("ojs_squat_01")},
  {order:14,id:"ojs_lunge_02",reason:"stratified_high_confidence_and_wrong_ui_correction",decision:"accept_supported",label:"lunge",start:724,end:783.5,evidence:dense("ojs_lunge_02")},
  {order:15,id:"tiff_press_01",reason:"stratified_high_confidence_boundary_check",decision:"accept_supported",label:"shoulder_press",start:31,end:68,evidence:dense("tiff_press_01")},
  {order:16,id:"striq_pullup_02",reason:"stratified_high_confidence_boundary_check",decision:"accept_supported",label:"pull_up",start:1418,end:1436,evidence:dense("striq_pullup_02")},
  {order:17,id:"gains_situp_01",reason:"stratified_high_confidence_motion_change_check",decision:"accept_supported",label:"sit_up",start:985,end:1028,evidence:dense("gains_situp_01")}
];

const storageKey = "calorie-independent-confirmation-v1";
let state = JSON.parse(localStorage.getItem(storageKey) || "{}") || {};
let current = Math.min(Number(localStorage.getItem(`${storageKey}-index`) || 0), queue.length - 1);

const $ = id => document.getElementById(id);
const labelSelect = $("label");
labels.forEach(value => labelSelect.add(new Option(value.replaceAll("_", " "), value)));

function decisionName(value) {
  return ({
    accept_supported: "desteklenen hareket",
    accept_unknown: "unknown / bileşik hareket",
    reject_no_target_motion: "reddet"
  })[value] || value;
}

function saveState() {
  localStorage.setItem(storageKey, JSON.stringify(state));
  localStorage.setItem(`${storageKey}-index`, String(current));
}

function renderEvidence(item) {
  const host = $("evidence");
  const toggle = $("toggleGallery");
  host.innerHTML = "";
  toggle.hidden = true;
  toggle.textContent = "Tüm pose sayfalarını göster";

  if (item.evidence.type === "dense") {
    $("evidenceHint").textContent = "Bu görsel, aralığın tamamından alınmış sıralı kareleri gösterir. Yukarıdan aşağıya ve soldan sağa zaman ilerler.";
    const img = new Image();
    img.src = item.evidence.overview;
    img.alt = `${item.id} zaman sıralı RGB kanıtı`;
    host.appendChild(img);
    return;
  }

  $("evidenceHint").textContent = "Önce kaba RGB bağlamı, ardından isteğe bağlı tüm pose sayfaları. Pose yalnızca hareket geometrisini destekler.";
  const context = new Image();
  context.src = item.evidence.context;
  context.alt = `${item.id} RGB bağlamı`;
  context.className = "context";
  host.appendChild(context);

  const gallery = document.createElement("div");
  gallery.className = "gallery";
  gallery.hidden = true;
  item.evidence.pages.forEach((src, i) => {
    const img = new Image();
    img.src = src;
    img.alt = `${item.id} pose sayfası ${i + 1}`;
    img.loading = "lazy";
    gallery.appendChild(img);
  });
  host.appendChild(gallery);
  toggle.hidden = false;
  toggle.onclick = () => {
    gallery.hidden = !gallery.hidden;
    toggle.textContent = gallery.hidden ? "Tüm pose sayfalarını göster" : "Pose sayfalarını gizle";
  };
}

function render() {
  const item = queue[current];
  const answer = state[item.id];
  const completed = Object.keys(state).filter(id => state[id]?.independent_decision).length;

  $("caseNumber").textContent = `${current + 1} / ${queue.length}`;
  $("reason").textContent = reasonText[item.reason] || item.reason;
  $("intervalId").textContent = item.id;
  $("proposal").innerHTML = `<span class="muted">Önerilen</span><br><b>${decisionName(item.decision)} · ${item.label.replaceAll("_", " ")}</b><br><span>${item.start}–${item.end} sn</span>`;
  $("progressText").textContent = `${completed} / ${queue.length}`;
  $("progressBar").style.width = `${completed / queue.length * 100}%`;
  $("savedState").textContent = answer?.independent_decision ? `Kaydedildi: ${decisionName(answer.independent_decision)} · ${answer.independent_label}` : "Henüz kaydedilmedi";
  $("prevBtn").disabled = current === 0;
  $("nextBtn").disabled = current === queue.length - 1;
  $("finishCard").hidden = completed !== queue.length;
  $("correctionForm").hidden = true;
  renderEvidence(item);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function record(payload) {
  const item = queue[current];
  const reviewer = $("reviewerId").value.trim();
  if (!reviewer) {
    alert("Önce inceleyen adını yaz.");
    $("reviewerId").focus();
    return;
  }
  localStorage.setItem(`${storageKey}-reviewer`, reviewer);
  state[item.id] = { reviewer_id: reviewer, ...payload };
  saveState();
  if (current < queue.length - 1) current += 1;
  saveState();
  render();
}

$("reviewerId").value = localStorage.getItem(`${storageKey}-reviewer`) || "baris";
$("agreeBtn").onclick = () => {
  const item = queue[current];
  record({
    independent_decision: item.decision,
    independent_label: item.label,
    independent_start_s: item.start,
    independent_end_s: item.end,
    confidence: "high",
    notes: "confirmed_as_proposed"
  });
};

$("correctBtn").onclick = () => {
  const item = queue[current];
  const answer = state[item.id] || {};
  $("decision").value = answer.independent_decision || item.decision;
  $("label").value = answer.independent_label || item.label;
  $("start").value = answer.independent_start_s ?? item.start;
  $("end").value = answer.independent_end_s ?? item.end;
  $("confidence").value = answer.confidence || "high";
  $("notes").value = answer.notes === "confirmed_as_proposed" ? "" : (answer.notes || "");
  $("label").disabled = $("decision").value !== "accept_supported";
  $("correctionForm").hidden = false;
  $("correctionForm").scrollIntoView({ behavior: "smooth", block: "center" });
};

$("unsureBtn").onclick = () => record({
  independent_decision: "needs_adjudication",
  independent_label: "unknown",
  independent_start_s: queue[current].start,
  independent_end_s: queue[current].end,
  confidence: "low",
  notes: "independent_reviewer_unsure"
});

$("correctionForm").onsubmit = event => {
  event.preventDefault();
  const decision = $("decision").value;
  let label = $("label").value;
  if (decision !== "accept_supported") label = "unknown";
  record({
    independent_decision: decision,
    independent_label: label,
    independent_start_s: Number($("start").value),
    independent_end_s: Number($("end").value),
    confidence: $("confidence").value,
    notes: $("notes").value.trim() || "corrected_by_independent_reviewer"
  });
};

$("decision").onchange = () => {
  const supported = $("decision").value === "accept_supported";
  $("label").disabled = !supported;
  if (!supported) $("label").value = "unknown";
};

$("prevBtn").onclick = () => { current -= 1; saveState(); render(); };
$("nextBtn").onclick = () => { current += 1; saveState(); render(); };

function csvEscape(value) {
  const text = String(value ?? "");
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

$("downloadBtn").onclick = () => {
  const columns = ["queue_order","interval_id","confirmation_reason","source_decision","source_label","source_start_s","source_end_s","reviewer_id","independent_decision","independent_label","independent_start_s","independent_end_s","confidence","notes"];
  const rows = queue.map(item => {
    const answer = state[item.id] || {};
    return [item.order,item.id,item.reason,item.decision,item.label,item.start,item.end,answer.reviewer_id,answer.independent_decision,answer.independent_label,answer.independent_start_s,answer.independent_end_s,answer.confidence,answer.notes];
  });
  const csv = [columns, ...rows].map(row => row.map(csvEscape).join(",")).join("\n") + "\n";
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "calorie_creator_independent_confirmation_completed.csv";
  link.click();
  URL.revokeObjectURL(link.href);
};

render();
