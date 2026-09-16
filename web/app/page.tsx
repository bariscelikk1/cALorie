import Link from "next/link";

const exercises = [
  ["Squats", "Knee-angle state machine", "Side or 45° view"],
  ["Jumping jacks", "Arm and leg position", "Front, full-body view"],
  ["Push-ups", "Elbow angle and body line", "Clear side view"],
];

export default function Home() {
  return <main>
    <header className="shell flex items-center justify-between py-6">
      <div className="brand"><span className="brand-mark">C</span>cALorie</div>
      <Link href="/upload" className="button secondary !min-h-10 !px-4">Analyze a video</Link>
    </header>
    <section className="shell grid min-h-[620px] items-center gap-12 py-16 lg:grid-cols-[1.15fr_.85fr]">
      <div>
        <p className="eyebrow mb-5">Explainable workout analysis</p>
        <h1 className="max-w-3xl text-5xl font-black leading-[.98] tracking-[-.065em] sm:text-7xl">Movement in.<br/><span className="text-[#5e7d20]">Useful estimates out.</span></h1>
        <p className="mt-7 max-w-xl text-lg leading-8 text-[#68716b]">Upload a workout video. cALorie follows body landmarks, counts complete repetitions, measures pace, and applies a transparent MET formula.</p>
        <div className="mt-9 flex flex-wrap gap-3"><Link href="/upload" className="button">Start analysis →</Link><a href="#method" className="button secondary">See how it works</a></div>
        <p className="mt-5 text-xs text-[#7b837d]">Fitness estimate only — not a medical or wearable-grade measurement.</p>
      </div>
      <div className="card relative overflow-hidden p-8 text-white" style={{ background: "#193c2d" }}>
        <div className="absolute -right-16 -top-16 h-56 w-56 rounded-full bg-[#cafa58] opacity-90" />
        <p className="relative text-sm font-bold text-[#cafa58]">ANALYSIS PREVIEW</p>
        <p className="relative mt-14 text-7xl font-black tracking-[-.07em]">18</p><p className="relative text-white/60">complete repetitions</p>
        <div className="relative mt-10 grid grid-cols-2 gap-3">
          <div className="rounded-2xl bg-white/10 p-4"><b>5.0 MET</b><span className="mt-1 block text-xs text-white/60">moderate squat</span></div>
          <div className="rounded-2xl bg-white/10 p-4"><b>86%</b><span className="mt-1 block text-xs text-white/60">valid pose frames</span></div>
        </div>
      </div>
    </section>
    <section id="method" className="border-y border-[#dfe4dc] bg-white py-20">
      <div className="shell"><p className="eyebrow">Three understandable steps</p><h2 className="mt-3 text-4xl font-black tracking-[-.05em]">No mystery number.</h2>
        <div className="mt-10 grid gap-4 md:grid-cols-3">{[["01","Track","MediaPipe estimates body landmarks frame by frame."],["02","Count","Exercise-specific state machines count complete motion cycles."],["03","Estimate","Duration, body weight and intensity select a MET-based estimate."]].map(([n,t,d])=><article className="card p-6" key={n}><span className="text-xs font-black text-[#709225]">{n}</span><h3 className="mt-8 text-xl font-bold">{t}</h3><p className="mt-2 text-sm leading-6 text-[#68716b]">{d}</p></article>)}</div>
      </div>
    </section>
    <section className="shell py-20"><p className="eyebrow">V1 exercise set</p><div className="mt-8 grid gap-4 md:grid-cols-3">{exercises.map(([name,method,view])=><article className="card p-6" key={name}><h3 className="text-xl font-bold">{name}</h3><p className="mt-5 text-sm">{method}</p><p className="mt-1 text-sm text-[#68716b]">Camera: {view}</p></article>)}</div></section>
    <footer className="border-t border-[#dfe4dc] py-8"><div className="shell flex flex-wrap justify-between gap-4 text-sm text-[#68716b]"><span>cALorie · University software project</span><span>Estimates, not medical measurements</span></div></footer>
  </main>;
}
