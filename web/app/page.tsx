import Link from "next/link";

const methods=[
  ["01","Pose","Body landmarks and visibility are measured frame by frame."],
  ["02","Segment","Movement rules separate exercises, rest and uncertain periods."],
  ["03","Estimate","Repetitions, pace, duration and MET values produce an estimate."],
];

export default function Home(){return <main>
  <header className="shell site-header"><Link href="/" className="brand"><span className="brand-mark">C</span>cALorie</Link><Link href="/upload" className="text-sm font-bold no-underline">Analyze video ↗</Link></header>
  <section className="shell grid gap-12 py-16 md:grid-cols-[1fr_340px] md:py-20">
    <div><p className="eyebrow">Video movement analysis</p><h1 className="mt-5 max-w-3xl text-5xl font-black leading-[.98] tracking-[-.06em] sm:text-6xl">One video.<br/>Every set, separated.</h1><p className="mt-6 max-w-2xl text-lg leading-8 text-[#667068]">Upload a mixed workout. cALorie separates supported movements over time, counts complete repetitions and explains its calorie estimate.</p><div className="mt-8 flex flex-wrap gap-3"><Link href="/upload" className="button">Analyze a workout</Link><a href="#method" className="button secondary">How it works</a></div></div>
    <aside className="border-l border-[#d9ded9] pl-7"><p className="eyebrow">Supported in V2</p><ul className="mt-5 divide-y divide-[#d9ded9] text-sm font-bold"><li className="py-4">Squat</li><li className="py-4">Jumping jack</li><li className="py-4">Push-up</li><li className="py-4 text-[#667068]">Rest & unknown periods</li></ul><p className="mt-6 text-xs leading-5 text-[#667068]">Automatic mode is rule-based and explainable. Manual single-exercise mode remains available.</p></aside>
  </section>
  <section id="method" className="rule bg-white"><div className="shell py-12"><div className="grid divide-y divide-[#d9ded9] md:grid-cols-3 md:divide-x md:divide-y-0">{methods.map(([n,t,d])=><article className="py-6 md:px-7 md:first:pl-0" key={n}><span className="eyebrow">{n}</span><h2 className="mt-3 text-xl font-black">{t}</h2><p className="mt-2 max-w-xs text-sm leading-6 text-[#667068]">{d}</p></article>)}</div></div></section>
  <section className="shell flex flex-col justify-between gap-6 py-12 sm:flex-row sm:items-end"><div><h2 className="text-2xl font-black tracking-[-.03em]">Designed to show its work.</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-[#667068]">Results include a timestamped exercise timeline, pose coverage, confidence, warnings and the exact MET formula.</p></div><Link href="/upload" className="button secondary">Start analysis →</Link></section>
  <footer className="rule"><div className="shell flex flex-wrap justify-between gap-3 py-6 text-xs text-[#667068]"><span>cALorie · Computer Engineering project</span><span>Activity estimate, not a medical measurement</span></div></footer>
</main>}
