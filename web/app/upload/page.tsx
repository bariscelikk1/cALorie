"use client";

import Link from "next/link";
import { useRef, useState } from "react";
import { useRouter } from "next/navigation";

const MAX_BYTES = 100 * 1024 * 1024;
const allowed = ["video/mp4", "video/quicktime", "video/webm"];
const choices = [
  { value: "squat", name: "Squat", guide: "Film your full body from the side or 45°." },
  { value: "jumping_jack", name: "Jumping jack", guide: "Face the camera with hands and feet visible." },
  { value: "push_up", name: "Push-up", guide: "Use a stable, unobstructed side view." },
];

function videoDuration(file: File) {
  return new Promise<number>((resolve, reject) => {
    const video = document.createElement("video");
    const url = URL.createObjectURL(file);
    video.preload = "metadata";
    video.onloadedmetadata = () => { URL.revokeObjectURL(url); resolve(video.duration); };
    video.onerror = () => { URL.revokeObjectURL(url); reject(new Error("This video could not be read.")); };
    video.src = url;
  });
}

export default function UploadPage() {
  const router = useRouter();
  const abortRef = useRef<AbortController | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [weightKg, setWeightKg] = useState("");
  const [exercise, setExercise] = useState("squat");
  const [phase, setPhase] = useState<"idle" | "preparing" | "uploading" | "starting">("idle");
  const [error, setError] = useState<string | null>(null);
  const busy = phase !== "idle";

  function chooseFile(next: File | null) {
    setError(null);
    if (!next) return setFile(null);
    if (!allowed.includes(next.type)) return setError("Choose an MP4, MOV, or WebM video.");
    if (next.size > MAX_BYTES) return setError("The video must be smaller than 100 MB.");
    setFile(next);
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault(); setError(null);
    const weight = Number(weightKg);
    if (!file) return setError("Choose a workout video first.");
    if (!Number.isFinite(weight) || weight < 30 || weight > 250) return setError("Enter a body weight between 30 and 250 kg.");
    const controller = new AbortController(); abortRef.current = controller;
    try {
      setPhase("preparing");
      const duration = await videoDuration(file);
      if (!Number.isFinite(duration) || duration <= 0 || duration > 180) throw new Error("Video duration must be between 1 second and 3 minutes.");
      const urlRes = await fetch("/api/upload-url", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ contentType: file.type, size: file.size }), signal: controller.signal });
      const urlData = await urlRes.json();
      if (!urlRes.ok) throw new Error(urlData.error ?? "Could not prepare the upload.");
      setPhase("uploading");
      const putRes = await fetch(urlData.uploadUrl, { method: "PUT", headers: { "Content-Type": file.type }, body: file, signal: controller.signal });
      if (!putRes.ok) throw new Error("Video upload failed. Please try again.");
      setPhase("starting");
      const jobRes = await fetch("/api/create-job", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ videoKey: urlData.key, uploadToken: urlData.uploadToken, weightKg: weight, exercise }), signal: controller.signal });
      const jobData = await jobRes.json();
      if (!jobRes.ok) throw new Error(jobData.error ?? "Could not start analysis.");
      router.push(`/results/${jobData.jobId}?token=${jobData.accessToken}`);
    } catch (reason) {
      setError(reason instanceof DOMException && reason.name === "AbortError" ? "Upload cancelled." : reason instanceof Error ? reason.message : "Something went wrong.");
      setPhase("idle");
    }
  }

  return <main className="min-h-screen bg-[radial-gradient(circle_at_80%_0%,#e8fac2,transparent_30%)]">
    <header className="shell flex items-center justify-between py-6"><Link href="/" className="brand"><span className="brand-mark">C</span>cALorie</Link><span className="text-xs font-bold text-[#68716b]">POSE ANALYSIS · V1</span></header>
    <div className="shell grid gap-10 py-10 lg:grid-cols-[.72fr_1.28fr] lg:py-16">
      <section><p className="eyebrow">New analysis</p><h1 className="mt-3 text-5xl font-black leading-[1] tracking-[-.06em]">Give the model a clear view.</h1><p className="mt-5 max-w-md leading-7 text-[#68716b]">Short, steady clips work best. Keep the joints needed for your exercise inside the frame.</p>
        <div className="mt-8 space-y-3 text-sm text-[#56605a]"><p>✓ One person in frame</p><p>✓ 1 second–3 minutes</p><p>✓ MP4, MOV or WebM · max 100 MB</p><p>✓ Stable camera and even lighting</p></div>
      </section>
      <form onSubmit={handleSubmit} className="card p-5 sm:p-8">
        <fieldset disabled={busy}><legend className="label">1. Choose the exercise</legend><div className="mt-3 grid gap-3 sm:grid-cols-3">{choices.map(choice=><label key={choice.value} className={`cursor-pointer rounded-2xl border p-4 transition ${exercise===choice.value?"border-[#5e7d20] bg-[#f2fadf]":"border-[#dfe4dc] bg-white"}`}><input className="sr-only" type="radio" name="exercise" value={choice.value} checked={exercise===choice.value} onChange={()=>setExercise(choice.value)}/><b className="block text-sm">{choice.name}</b><span className="mt-2 block text-xs leading-5 text-[#68716b]">{choice.guide}</span></label>)}</div>
        <div className="mt-7 grid gap-6 sm:grid-cols-2"><div className="field"><label htmlFor="video">2. Workout video</label><input id="video" type="file" accept="video/mp4,video/quicktime,video/webm" onChange={e=>chooseFile(e.target.files?.[0]??null)} className="input py-3 text-sm"/><span className="helper">{file?`${file.name} · ${(file.size/1024/1024).toFixed(1)} MB`:"No file selected"}</span></div>
        <div className="field"><label htmlFor="weight">3. Body weight (kg)</label><input id="weight" className="input" type="number" min="30" max="250" step="0.1" placeholder="70" value={weightKg} onChange={e=>setWeightKg(e.target.value)}/><span className="helper">Used only in the MET calculation.</span></div></div></fieldset>
        {error&&<p role="alert" className="error mt-6">{error}</p>}
        {busy&&<div className="mt-6 rounded-xl bg-[#eef5e8] p-4" role="status"><p className="text-sm font-bold">{phase==="preparing"?"Checking video…":phase==="uploading"?"Uploading securely…":"Starting analysis…"}</p><div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white"><div className={`h-full bg-[#71962a] transition-all ${phase==="preparing"?"w-1/3":phase==="uploading"?"w-2/3":"w-full"}`}/></div></div>}
        <div className="mt-7 flex flex-wrap gap-3"><button className="button flex-1" type="submit" disabled={busy}>{busy?"Working…":"Analyze workout →"}</button>{busy&&<button type="button" className="button secondary" onClick={()=>abortRef.current?.abort()}>Cancel</button>}</div>
        <p className="mt-5 text-xs leading-5 text-[#7b837d]">Your result is an activity estimate, not a medical measurement. Video is stored privately for processing.</p>
      </form>
    </div>
  </main>;
}
