"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

const MAX_BYTES=100*1024*1024;
const allowed=["video/mp4","video/quicktime","video/webm"];
const manualExercises=[{value:"squat",label:"Squat"},{value:"jumping_jack",label:"Jumping jack"},{value:"push_up",label:"Push-up"}];

export default function UploadPage(){
  const router=useRouter(); const abortRef=useRef<AbortController|null>(null);
  const [file,setFile]=useState<File|null>(null); const [preview,setPreview]=useState<string|null>(null); const [duration,setDuration]=useState<number|null>(null);
  const [weight,setWeight]=useState(""); const [mode,setMode]=useState<"auto"|"manual">("auto"); const [manualExercise,setManualExercise]=useState("squat");
  const [phase,setPhase]=useState<"idle"|"checking"|"uploading"|"starting">("idle"); const [error,setError]=useState<string|null>(null); const busy=phase!=="idle";
  useEffect(()=>()=>{if(preview)URL.revokeObjectURL(preview)},[preview]);

  function choose(next:File|null){
    setError(null); setDuration(null); if(preview)URL.revokeObjectURL(preview); setPreview(null);
    if(!next){setFile(null);return} if(!allowed.includes(next.type)){setError("Choose an MP4, MOV, or WebM file.");return} if(next.size>MAX_BYTES){setError("Video must be smaller than 100 MB.");return}
    const url=URL.createObjectURL(next); const video=document.createElement("video"); video.preload="metadata"; video.onloadedmetadata=()=>{if(video.duration>180||video.duration<=0){setError("Video must be between 1 second and 3 minutes.");URL.revokeObjectURL(url);return}setFile(next);setPreview(url);setDuration(video.duration)}; video.onerror=()=>{setError("This video could not be read.");URL.revokeObjectURL(url)}; video.src=url;
  }
  async function submit(event:React.FormEvent){event.preventDefault();setError(null);const kg=Number(weight);if(!file)return setError("Choose a workout video first.");if(!Number.isFinite(kg)||kg<30||kg>250)return setError("Enter a body weight between 30 and 250 kg.");const controller=new AbortController();abortRef.current=controller;
    try{setPhase("checking");const prepared=await fetch("/api/upload-url",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({contentType:file.type,size:file.size}),signal:controller.signal});const upload=await prepared.json();if(!prepared.ok)throw new Error(upload.error??"Could not prepare upload.");setPhase("uploading");const sent=await fetch(upload.uploadUrl,{method:"PUT",headers:{"Content-Type":file.type},body:file,signal:controller.signal});if(!sent.ok)throw new Error("Video upload failed.");setPhase("starting");const created=await fetch("/api/create-job",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({videoKey:upload.key,uploadToken:upload.uploadToken,weightKg:kg,exercise:mode==="auto"?"auto":manualExercise}),signal:controller.signal});const job=await created.json();if(!created.ok)throw new Error(job.error??"Could not start analysis.");router.push(`/results/${job.jobId}?token=${job.accessToken}`)}catch(reason){setError(reason instanceof DOMException&&reason.name==="AbortError"?"Upload cancelled.":reason instanceof Error?reason.message:"Something went wrong.");setPhase("idle")}}
  return <main><header className="shell site-header"><Link href="/" className="brand"><span className="brand-mark">C</span>cALorie</Link><span className="text-xs font-bold text-[#667068]">NEW ANALYSIS</span></header>
    <form onSubmit={submit} className="shell grid min-h-[calc(100vh-64px)] lg:grid-cols-[1.35fr_.65fr]">
      <section className="py-10 lg:border-r lg:border-[#d9ded9] lg:pr-10"><p className="eyebrow">Workout video</p><h1 className="mt-3 text-3xl font-black tracking-[-.04em]">Show the full movement.</h1><p className="mt-2 text-sm text-[#667068]">One person, steady camera, all working joints visible.</p>
        <label htmlFor="video" onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();choose(e.dataTransfer.files[0]??null)}} className="mt-7 block cursor-pointer border border-dashed border-[#9da79e] bg-white p-6 text-center hover:border-[#557d27]"><input id="video" className="sr-only" type="file" accept="video/mp4,video/quicktime,video/webm" onChange={e=>choose(e.target.files?.[0]??null)}/><b className="block text-sm">Drop a video here or choose a file</b><span className="helper mt-2 block">MP4, MOV, WebM · 100 MB · 3 minutes maximum</span></label>
        {preview?<div className="mt-5"><video className="aspect-video w-full bg-black object-contain" src={preview} controls preload="metadata"/><div className="mt-3 flex flex-wrap justify-between gap-2 text-xs"><b className="max-w-[70%] truncate">{file?.name}</b><span className="text-[#667068]">{(file!.size/1024/1024).toFixed(1)} MB · {duration?.toFixed(1)} sec</span></div></div>:<div className="mt-5 grid aspect-video place-items-center border-y border-[#d9ded9] text-sm text-[#7b837c]">Video preview</div>}
        <div className="mt-6 grid grid-cols-2 gap-x-6 gap-y-3 text-xs text-[#667068] sm:grid-cols-4"><span>One person</span><span>Full body visible</span><span>Stable camera</span><span>Even lighting</span></div>
      </section>
      <aside className="py-10 lg:pl-10"><div><label htmlFor="weight" className="label">Body weight (kg)</label><input id="weight" className="input" type="number" min="30" max="250" step="0.1" placeholder="70" value={weight} onChange={e=>setWeight(e.target.value)}/><p className="helper mt-2">Used only in the MET calculation.</p></div>
        <fieldset className="mt-8"><legend className="label">Analysis mode</legend><label className="flex cursor-pointer gap-3 border-t border-[#d9ded9] py-4"><input type="radio" checked={mode==="auto"} onChange={()=>setMode("auto")}/><span><b className="block text-sm">Automatic mixed workout</b><span className="helper">Separates supported exercises, rest and unknown periods.</span></span></label><label className="flex cursor-pointer gap-3 border-y border-[#d9ded9] py-4"><input type="radio" checked={mode==="manual"} onChange={()=>setMode("manual")}/><span><b className="block text-sm">Manual single exercise</b><span className="helper">Use when the full video contains one known movement.</span></span></label></fieldset>
        {mode==="manual"&&<div className="mt-5"><label className="label" htmlFor="exercise">Exercise override</label><select id="exercise" className="input" value={manualExercise} onChange={e=>setManualExercise(e.target.value)}>{manualExercises.map(item=><option value={item.value} key={item.value}>{item.label}</option>)}</select></div>}
        <details className="mt-7 border-y border-[#d9ded9] py-4"><summary className="cursor-pointer text-sm font-bold">Supported movements & camera guide</summary><ul className="mt-4 space-y-3 text-xs leading-5 text-[#667068]"><li><b className="text-[#171a17]">Squat</b> — side or 45° view</li><li><b className="text-[#171a17]">Jumping jack</b> — front, full-body view</li><li><b className="text-[#171a17]">Push-up</b> — unobstructed side view</li></ul></details>
        {error&&<p role="alert" className="error mt-6">{error}</p>}{busy&&<div className="mt-6" role="status"><div className="flex justify-between text-xs font-bold"><span>{phase==="checking"?"Preparing":phase==="uploading"?"Uploading":"Starting analysis"}</span><span>{phase==="checking"?"25%":phase==="uploading"?"65%":"100%"}</span></div><div className="mt-2 h-1 bg-[#d9ded9]"><div className={`h-full bg-[#517c25] ${phase==="checking"?"w-1/4":phase==="uploading"?"w-2/3":"w-full"}`}/></div></div>}
        <div className="mt-7 flex gap-2"><button className="button flex-1" type="submit" disabled={busy}>{busy?"Working…":"Analyze video →"}</button>{busy&&<button className="button secondary" type="button" onClick={()=>abortRef.current?.abort()}>Cancel</button>}</div><p className="helper mt-4">Results are activity estimates, not medical measurements.</p>
      </aside>
    </form>
  </main>;
}
