import { Link } from 'react-router-dom'

const STEPS = [
  ['01', 'Upload your resume', 'A PDF is all we need.'],
  ['02', 'Paste the job post', 'Any role you are applying for.'],
  ['03', 'See what is missing', 'Skills, keywords and phrasing.'],
  ['04', 'Fix it and re-check', 'Watch the score move.'],
]

const DEMO = [
  ['Wording', 31.5],
  ['Skills', 85.0],
  ['Keywords', 70.0],
]

export function Landing() {
  return (
    <div className="space-y-28">
      {/* ---------------- hero ---------------- */}
      <section className="grid items-center gap-14 lg:grid-cols-[1.05fr_.95fr]">
        <div>
          <h1 className="font-display text-5xl leading-[1.04] font-bold tracking-[-0.03em] sm:text-6xl">
            Know exactly
            <br />
            <span className="text-acid-600 dark:text-acid-400">why</span> your resume
            <br />
            matches.
          </h1>

          <p className="mt-6 max-w-md text-[15px] leading-relaxed text-ink-500 dark:text-ink-400">
            Most tools hand you one number and no explanation. ResumeIQ shows you
            the skills you are missing, the words the employer used that you
            didn&apos;t, and exactly where the score comes from.
          </p>

          <div className="mt-9 flex flex-wrap items-center gap-3">
            <Link
              to="/signup"
              className="rounded-xs bg-acid-400 px-5 py-3 font-mono text-[11px] font-medium uppercase
                         tracking-[0.12em] text-ink-950 transition-colors hover:bg-acid-300"
            >
              Check your resume
            </Link>
            <Link
              to="/login"
              className="px-4 py-3 font-mono text-[11px] uppercase tracking-[0.12em] text-ink-500
                         transition-colors hover:text-ink-950 dark:hover:text-ink-100"
            >
              Sign in →
            </Link>
          </div>

          <p className="mt-6 text-[11px] text-ink-400 dark:text-ink-600">
            Free · your resume stays private to your account
          </p>
        </div>

        {/* The product itself as the hero image. */}
        <div className="panel p-6 sm:p-7">
          <div className="flex items-baseline justify-between">
            <span className="label">Senior Frontend Engineer</span>
            <span className="label text-acid-600 dark:text-acid-400">Strong match</span>
          </div>

          <div className="mt-5 flex items-end gap-1">
            <span className="num text-6xl leading-none font-medium text-acid-600 dark:text-acid-400">
              76
            </span>
            <span className="num mb-1 text-base text-ink-400">%</span>
          </div>

          <div className="mt-5 flex gap-[3px]" aria-hidden>
            {Array.from({ length: 32 }, (_, i) => (
              <span
                key={i}
                className={`h-6 flex-1 ${i < 24 ? 'bg-acid-400' : 'bg-paper-line dark:bg-ink-800'}`}
              />
            ))}
          </div>

          <div className="mt-6 space-y-3 border-t border-paper-line pt-5 dark:border-ink-800">
            {DEMO.map(([label, value]) => (
              <div key={label} className="grid grid-cols-[5rem_1fr_auto] items-center gap-3">
                <span className="text-[11px] text-ink-500 dark:text-ink-400">{label}</span>
                <span className="h-[5px] bg-paper-line dark:bg-ink-800">
                  <span className="block h-full bg-ink-950 dark:bg-ink-100" style={{ width: `${value}%` }} />
                </span>
                <span className="num text-[11px]">{value}</span>
              </div>
            ))}
          </div>

          <div className="mt-5 border-t border-paper-line pt-5 dark:border-ink-800">
            <span className="label">You have</span>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {['React', 'TypeScript', 'Node.js', 'AWS'].map((s) => (
                <span key={s} className="rounded-xs border border-acid-500/40 bg-acid-400/10 px-2 py-1 font-mono text-[11px] text-acid-700 dark:text-acid-300">
                  {s}
                </span>
              ))}
            </div>
            <span className="label mt-4 block">They asked for</span>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {['GraphQL', 'Kubernetes'].map((s) => (
                <span key={s} className="rounded-xs border border-paper-line px-2 py-1 font-mono text-[11px] text-ink-500 line-through decoration-alert dark:border-ink-700 dark:text-ink-400">
                  {s}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ---------------- how it works ---------------- */}
      <section>
        <div className="rule pt-4">
          <h2 className="label">How it works</h2>
        </div>

        <ol className="mt-8 grid gap-px bg-paper-line sm:grid-cols-2 lg:grid-cols-4 dark:bg-ink-800">
          {STEPS.map(([n, title, note]) => (
            <li key={n} className="group bg-paper p-6 transition-colors hover:bg-white dark:bg-ink-950 dark:hover:bg-ink-900">
              <span className="num text-[11px] text-ink-300 transition-colors group-hover:text-acid-500 dark:text-ink-700">
                {n}
              </span>
              <p className="mt-3 font-display text-base font-semibold">{title}</p>
              <p className="mt-1.5 text-[12px] leading-relaxed text-ink-400 dark:text-ink-500">{note}</p>
            </li>
          ))}
        </ol>
      </section>

      {/* ---------------- closing ---------------- */}
      <section className="rule flex flex-wrap items-center justify-between gap-6 pt-12">
        <h2 className="max-w-md font-display text-2xl leading-snug font-bold tracking-tight">
          Stop guessing why you didn&apos;t hear back.
        </h2>
        <Link
          to="/signup"
          className="rounded-xs bg-acid-400 px-5 py-3 font-mono text-[11px] font-medium uppercase
                     tracking-[0.12em] text-ink-950 transition-colors hover:bg-acid-300"
        >
          Check your resume
        </Link>
      </section>
    </div>
  )
}
