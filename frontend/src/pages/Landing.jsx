import { Link } from 'react-router-dom'

const STEPS = [
  ['Upload your resume', 'A PDF is all we need. Keep several versions and compare them.'],
  ['Paste the job post', 'Any role you are applying for, in full.'],
  ['See what is missing', 'The exact skills, keywords and phrasing you left out.'],
  ['Fix it and re-check', 'Re-upload and watch the score move.'],
]

const DEMO = [
  ['Text similarity', 31.5],
  ['Skill match', 85.0],
  ['Keyword match', 70.0],
]

export function Landing() {
  return (
    <div className="space-y-28">
      {/* ---------------- hero ---------------- */}
      <section className="grid items-center gap-16 lg:grid-cols-2">
        <div>
          <span className="inline-flex items-center gap-2 rounded-full bg-brand-50 px-3.5 py-1.5
                           text-[13px] font-semibold text-brand-700
                           dark:bg-brand-500/12 dark:text-brand-300">
            Free to use
          </span>

          <h1 className="mt-6 font-display text-[3.4rem] leading-[1.05] font-extrabold tracking-[-0.03em]">
            Know exactly{' '}
            <span className="text-brand-600 dark:text-brand-400">why</span> your
            resume matches.
          </h1>

          <p className="mt-6 max-w-lg text-lg leading-relaxed text-ink-600 dark:text-ink-300">
            Most tools hand you one number and no explanation. ResumeIQ shows you
            the skills you are missing, the words the employer used that you
            didn&apos;t, and exactly where the score comes from.
          </p>

          <div className="mt-9 flex flex-wrap items-center gap-4">
            <Link
              to="/signup"
              className="rounded-md bg-brand-600 px-7 py-3.5 text-base font-semibold text-white
                         transition-colors hover:bg-brand-700"
            >
              Check your resume
            </Link>
            <Link
              to="/login"
              className="text-base font-medium text-ink-600 transition-colors hover:text-ink-950
                         dark:text-ink-400 dark:hover:text-ink-100"
            >
              Sign in
            </Link>
          </div>

          <p className="mt-6 text-sm text-ink-400">
            Your resume stays private to your account.
          </p>
        </div>

        {/* The product itself as the hero image. */}
        <div className="panel p-8">
          <div className="flex items-center justify-between gap-4">
            <span className="text-sm font-semibold text-ink-500">Senior Frontend Engineer</span>
            <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700
                             dark:bg-brand-500/12 dark:text-brand-300">
              Strong match
            </span>
          </div>

          <div className="mt-5 flex items-baseline gap-1.5">
            <span className="num text-7xl leading-none font-semibold tracking-tighter text-brand-600 dark:text-brand-400">
              76.4
            </span>
            <span className="num text-xl font-medium text-ink-400">%</span>
          </div>

          <div className="mt-6 h-3 overflow-hidden rounded-full bg-paper-line dark:bg-ink-800">
            <div className="h-full rounded-full bg-brand-500" style={{ width: '76.4%' }} />
          </div>

          <div className="mt-8 space-y-5 border-t border-paper-line pt-7 dark:border-ink-800">
            {DEMO.map(([label, value]) => (
              <div key={label}>
                <div className="flex items-baseline justify-between">
                  <span className="text-sm font-medium">{label}</span>
                  <span className="num text-sm font-semibold">{value}%</span>
                </div>
                <div className="mt-2 h-2 overflow-hidden rounded-full bg-paper-line dark:bg-ink-800">
                  <div className="h-full rounded-full bg-ink-900 dark:bg-ink-300" style={{ width: `${value}%` }} />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-7 grid gap-5 border-t border-paper-line pt-7 sm:grid-cols-2 dark:border-ink-800">
            <div>
              <p className="mb-2.5 text-xs font-semibold text-ink-400 uppercase tracking-wide">You have</p>
              <div className="flex flex-wrap gap-2">
                {['React', 'TypeScript', 'Node.js'].map((s) => (
                  <span key={s} className="rounded-md border border-brand-500/25 bg-brand-50 px-2.5 py-1.5 text-[13px] font-medium text-brand-700 dark:border-brand-500/30 dark:bg-brand-500/12 dark:text-brand-300">
                    {s}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <p className="mb-2.5 text-xs font-semibold text-ink-400 uppercase tracking-wide">Missing</p>
              <div className="flex flex-wrap gap-2">
                {['GraphQL', 'Kubernetes'].map((s) => (
                  <span key={s} className="rounded-md border border-alert/20 bg-alert-soft px-2.5 py-1.5 text-[13px] font-medium text-alert dark:bg-alert/10">
                    {s}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ---------------- how it works ---------------- */}
      <section>
        <h2 className="font-display text-3xl font-extrabold tracking-tight">How it works</h2>
        <ol className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {STEPS.map(([title, note], i) => (
            <li key={title} className="panel p-6">
              <span className="grid size-9 place-items-center rounded-md bg-brand-50 font-display text-base
                               font-bold text-brand-700 dark:bg-brand-500/12 dark:text-brand-300">
                {i + 1}
              </span>
              <p className="mt-4 font-display text-lg font-bold tracking-tight">{title}</p>
              <p className="mt-2 text-sm leading-relaxed text-ink-500 dark:text-ink-400">{note}</p>
            </li>
          ))}
        </ol>
      </section>

      {/* ---------------- closing ---------------- */}
      <section className="panel flex flex-wrap items-center justify-between gap-8 p-10">
        <div>
          <h2 className="max-w-lg font-display text-3xl leading-snug font-extrabold tracking-tight">
            Stop guessing why you didn&apos;t hear back.
          </h2>
          <p className="mt-3 text-base text-ink-500 dark:text-ink-400">
            Upload a resume and get a full breakdown in seconds.
          </p>
        </div>
        <Link
          to="/signup"
          className="rounded-md bg-brand-600 px-7 py-3.5 text-base font-semibold text-white
                     transition-colors hover:bg-brand-700"
        >
          Check your resume
        </Link>
      </section>
    </div>
  )
}
