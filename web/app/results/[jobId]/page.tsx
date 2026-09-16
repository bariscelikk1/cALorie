"use client";

import Link from "next/link";
import { Suspense, useEffect, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";

type Result = { exercise:string; duration_seconds:number; repetitions:number; repetitions_per_minute:number; intensity:string; met_value:number; calories_estimated:number; calories_low:number; calories_high:number; confidence:string; frames_analyzed:number; valid_pose_frame_ratio:number; warnings:string[] };
type State = { status:"queued"|"processing"|"done"|"error"; result:Result|null; error:string|null };
const names:Record<string,string>={squat:"Squat",jumping_jack:"Jumping jack",push_up:"Push-up"};

function ResultsContent() {
  const { jobId } = useParams<{jobId:string}>();
  const token = useSearchParams().get("token");
  const [state,setState]=useState<State>({status:"queued",result:null,error:null});
  const [networkNote,setNetworkNote]=useState<string|null>(null);

  useEffect(()=>{
    let stopped=false; let timer:ReturnType<typeof setTimeout>; let failures=0; const started=Date.now();
    async function poll(){
      if(stopped)return;
      if(!token){setState({status:"error",result:null,error:"This result link is incomplete."});return;}
      if(Date.now()-started>10*60_000){setState({status:"error",result:null,error:"Analysis timed out. Please try again."});return;}
      try{
        const res=await fetch(`/api/job-status/${jobId}?token=${encodeURIComponent(token)}`,{cache:"no-store"});
        const data=await res.json(); if(!res.ok)throw new Error(data.error??"Could not load this job.");
        failures=0; setNetworkNote(null); setState({status:data.status,result:data.result??null,error:data.error??null});
        if(data.status==="done"||data.status==="error")return;
      }catch(reason){failures++;setNetworkNote("Connection interrupted — retrying automatically.");if(failures>=5){setState({status:"error",result:null,error:reason instanceof Error?reason.message:"Could not load results."});return;}}
      timer=setTimeout(poll,Math.min(2000+failures*1000,7000));
    }
    poll(); return()=>{stopped=true;clearTimeout(timer);};
  },[jobId,token]);

  const r=state.result;
  return <main className="min-h-screen bg-[radial-gradient(circle_at_15%_10%,#e8fac2,transparent_25%)]"><header className="shell flex items-center justify-between py-6"><Link href="/" className="brand"><span className="brand-mark">C</span>cALorie</Link><span className="text-xs font-bold text-[#68716b]">ANALYSIS RESULT</span></header>
    <div className="shell py-12">
      {state.status!=="done"&&state.status!=="error"&&<section className="mx-auto max-w-2xl text-center"><div className="mx-auto grid h-20 w-20 animate-pulse place-items-center rounded-3xl bg-[#193c2d] text-3xl text-[#cafa58]">⌁</div><p className="eyebrow mt-8">{state.status==="queued"?"Waiting for worker":"Reading movement"}</p><h1 className="mt-3 text-4xl font-black tracking-[-.05em]">{state.status==="queued"?"Your video is queued.":"Pose analysis in progress."}</h1><p className="mx-auto mt-4 max-w-md leading-7 text-[#68716b]">You can keep this page open. Processing time depends on video length.</p>{networkNote&&<p className="mt-5 text-sm text-amber-700">{networkNote}</p>}</section>}
      {state.status==="error"&&<section className="card mx-auto max-w-xl p-8 text-center"><span className="text-4xl">!</span><p className="eyebrow mt-5">Analysis stopped</p><h1 className="mt-2 text-3xl font-black tracking-[-.04em]">We could not finish this video.</h1><p className="mt-4 leading-7 text-[#68716b]">{state.error??"An unexpected error occurred."}</p><Link href="/upload" className="button mt-7">Try another video</Link></section>}
      {state.status==="done"&&r&&<><section className="grid gap-5 lg:grid-cols-[1.15fr_.85fr]"><div className="card p-8 text-white sm:p-10" style={{ background: "#193c2d" }}><p className="text-xs font-black tracking-[.15em] text-[#cafa58]">ESTIMATED ENERGY</p><div className="mt-8 flex items-end gap-3"><span className="text-7xl font-black tracking-[-.07em]">{r.calories_estimated}</span><span className="pb-2 text-lg text-white/60">kcal</span></div><p className="mt-3 text-sm text-white/60">Estimated range: {r.calories_low}–{r.calories_high} kcal</p><div className="mt-10 border-t border-white/15 pt-6 text-sm leading-6 text-white/70">{r.met_value} MET × 3.5 × body weight ÷ 200 × {(r.duration_seconds/60).toFixed(2)} minutes</div></div>
      <div className="card grid grid-cols-2 overflow-hidden">{[["Exercise",names[r.exercise]??r.exercise],["Repetitions",r.repetitions],["Duration",`${r.duration_seconds.toFixed(1)} sec`],["Pace",`${r.repetitions_per_minute.toFixed(1)} / min`],["Intensity",r.intensity],["Confidence",r.confidence]].map(([label,value])=><div className="border-b border-r border-[#e3e7e1] p-5" key={label}><span className="text-xs text-[#7b837d]">{label}</span><b className="mt-2 block capitalize">{value}</b></div>)}</div></section>
      <section className="mt-5 grid gap-5 md:grid-cols-2"><div className="card p-7"><h2 className="text-lg font-bold">Analysis quality</h2><p className="mt-5 text-3xl font-black">{Math.round(r.valid_pose_frame_ratio*100)}%</p><p className="mt-1 text-sm text-[#68716b]">valid pose frames · {r.frames_analyzed} frames analyzed</p></div><div className="card p-7"><h2 className="text-lg font-bold">What this means</h2><p className="mt-4 text-sm leading-6 text-[#68716b]">The estimate combines video duration, your body weight and an exercise-specific MET value selected from the measured pace. It is not individualized medical data.</p></div></section>
      {r.warnings.length>0&&<section className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 p-6"><h2 className="font-bold text-amber-900">Quality notes</h2><ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-amber-800">{r.warnings.map(w=><li key={w}>{w}</li>)}</ul></section>}
      <div className="mt-8"><Link href="/upload" className="button">Analyze another video</Link></div></>}
    </div></main>;
}

export default function ResultsPage(){return <Suspense fallback={<main className="shell py-20">Loading result…</main>}><ResultsContent/></Suspense>}
