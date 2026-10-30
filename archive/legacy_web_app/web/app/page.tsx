import Link from "next/link";

const movements = ["Squat", "Push-up", "Pull-up", "Lunge", "Sit-up", "Jumping jack", "Mountain climber", "Burpee", "Plank"];

export default function Home() {
  return (
    <main>
      <header className="shell site-header">
        <Link href="/" className="brand">cALorie<span className="brand-dot" /></Link>
        <nav aria-label="Main navigation" className="flex items-center gap-7 text-sm">
          <a href="#method" className="quiet-link hidden sm:inline">How it works</a>
          <Link href="/upload" className="nav-action">Try cALorie ↗</Link>
        </nav>
      </header>
      <section className="shell home-hero">
        <p className="eyebrow">A little clarity for every workout.</p>
        <h1>Your movement.<br /><span>A clearer picture.</span></h1>
        <p className="hero-copy">From your first squat to your last push-up. Turn a workout video into a simple breakdown of movements, repetitions and estimated energy.</p>
        <div className="hero-actions"><Link href="/upload" className="button">Analyze your workout ↗</Link><a href="#method" className="text-link">Take a closer look ↓</a></div>
        <figure className="movement-study">
          <div className="study-caption"><span>One video. More than one movement.</span><span>Illustrative workout</span></div>
          <svg className="movement-art" viewBox="0 0 1000 300" role="img" aria-label="Illustrations of a squat, a push-up and a standing stretch">
            <ellipse cx="185" cy="266" rx="115" ry="9" fill="#dce4dc" />
            <ellipse cx="506" cy="266" rx="150" ry="9" fill="#dce4dc" />
            <ellipse cx="833" cy="266" rx="92" ry="9" fill="#dce4dc" />
            <g fill="none" strokeLinecap="round" strokeLinejoin="round">
              <g stroke="#608173" strokeWidth="26"><path d="M174 116 144 174 203 203 176 249" /><path d="M168 129 221 153 257 126" strokeWidth="18" /><path d="M150 174 111 205 124 251" stroke="#9bae9b" strokeWidth="22" /></g>
              <circle cx="183" cy="78" r="26" fill="#b88c70" /><path d="m160 58 26-8 19 13" stroke="#394e44" strokeWidth="13" />
              <path d="M163 255h34m-81 0h26" stroke="#394e44" strokeWidth="15" />
              <g stroke="#608173" strokeWidth="25"><path d="m393 195 113-10 100 57" /><path d="m502 185 29 60" stroke="#9bae9b" strokeWidth="20" /><path d="m397 194 14 56" strokeWidth="19" /></g>
              <circle cx="353" cy="187" r="24" fill="#b88c70" /><path d="m331 181 9-16 23-3" stroke="#394e44" strokeWidth="12" /><path d="M402 257h30m168-7h31" stroke="#394e44" strokeWidth="13" />
              <g stroke="#608173" strokeWidth="25"><path d="M832 115v65l-32 66m32-66 36 66" /><path d="m829 126-45-42-20-47m73 89 45-42 20-47" strokeWidth="18" /></g>
              <circle cx="832" cy="77" r="25" fill="#b88c70" /><path d="m812 58 24-6 16 13" stroke="#394e44" strokeWidth="12" /><path d="M783 255h25m53 0h25" stroke="#394e44" strokeWidth="14" />
            </g>
          </svg>
          <figcaption className="study-timeline"><span>Squat <small>12 reps</small></span><span className="rest">Rest</span><span>Push-up <small>8 reps</small></span><span>Jumping jack <small>18 reps</small></span></figcaption>
          <p className="sample-note">Example breakdown, not a live analysis.</p>
        </figure>
      </section>
      <section className="method-section" id="method"><div className="shell">
        <div className="section-intro"><p className="eyebrow">From video to understanding</p><h2>Less guesswork.<br />More perspective.</h2><p>No wearable needed. Just a short video with your full body in view.</p></div>
        <div className="method-steps">
          <article><span className="step-number">01</span><h3>Bring your workout.</h3><p>Upload up to three minutes of movement. Choose automatic mode for a mixed session, or select a single exercise.</p></article>
          <article><span className="step-number">02</span><h3>See it unfold.</h3><p>Pose tracking follows your joints over time. Rules identify supported movements, count repetitions and separate rest.</p></article>
          <article><span className="step-number">03</span><h3>Get the whole picture.</h3><p>Explore a timeline, exercise totals and an energy estimate—with quality notes that explain the limitations.</p></article>
        </div>
      </div></section>
      <section className="shell movement-section"><p className="eyebrow">Room for your routine</p><h2>Mix things up.</h2><p className="section-description">Nine supported movements. One place to review them.</p><ul className="movement-list">{movements.map(item => <li key={item}>{item}{item === "Burpee" && <sup>*</sup>}</li>)}</ul><p className="helper">Planks are timed, not counted. *Burpee detection is experimental. Camera angle and visibility affect results; unrecognized movement is marked unknown.</p></section>
      <section className="closing-section"><p className="eyebrow">Start with one video</p><h2>Make sense of<br />your next session.</h2><Link href="/upload" className="button">Try cALorie ↗</Link></section>
      <footer className="shell site-footer"><Link href="/" className="brand">cALorie</Link><p>A computer engineering project.<br />Activity estimates, not medical measurements.</p><a href="https://github.com/bariscelikk1/cALorie" className="text-link">Explore the project ↗</a></footer>
    </main>
  );
}
