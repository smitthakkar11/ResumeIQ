import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ScorePill } from '@/components/ScorePill'
import { analysisApi } from '@/lib/api'
import { useAuth } from '@/lib/auth'

/**
 * Placeholder dashboard. Phase 3 fills this with resume upload; Phase 7 adds
 * the analysis history. For now it proves the protected route and the
 * authenticated /auth/me call work.
 */
export function Dashboard() {
  const { user } = useAuth()
  const [recent, setRecent] = useState([])
  useEffect(() => {
    analysisApi
      .list()
      .then((all) => setRecent(all.slice(0, 5)))
      .catch(() => setRecent([]))
  }, [])
  if (!user) return null
  const NEXT = [
    {
      phase: 'Phase 8',
      title: 'Supervised model',
      note: 'only with a real dataset',
    },
    {
      phase: 'Phase 9',
      title: 'Semantic similarity',
      note: 'local sentence embeddings',
    },
    {
      phase: 'Phase 10',
      title: 'Deployment',
      note: 'Docker, security, docs',
    },
  ]
  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Hello, {user.name.split(' ')[0]}</h1>
        <p className="mt-1.5 text-slate-600 dark:text-slate-400">
          You&apos;re signed in as {user.email}.
        </p>
      </div>

      <Link
        to="/resume/upload"
        className="surface flex max-w-md items-center justify-between gap-4 p-5 transition hover:border-brand-400 dark:hover:border-brand-500/50"
      >
        <span>
          <span className="block font-medium">Upload a resume</span>
          <span className="block text-sm text-slate-500 dark:text-slate-400">
            PDF text extraction with PyMuPDF
          </span>
        </span>
        <span aria-hidden className="text-brand-600 dark:text-brand-400">
          &rarr;
        </span>
      </Link>

      <section className="surface max-w-md p-5">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Account
        </h2>
        <dl className="mt-4 space-y-2.5 text-sm">
          {[
            ['Name', user.name],
            ['Email', user.email],
            ['Sign-in method', user.has_password ? 'Email and password' : 'Google'],
            ['Member since', new Date(user.created_at).toLocaleDateString()],
          ].map(([label, value]) => (
            <div key={label} className="flex justify-between gap-4">
              <dt className="text-slate-500 dark:text-slate-400">{label}</dt>
              <dd className="font-medium">{value}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section>
        <div className="flex items-baseline justify-between">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Recent analyses
          </h2>
          {recent.length > 0 && (
            <Link
              to="/history"
              className="text-sm font-medium text-brand-600 hover:underline dark:text-brand-400"
            >
              View all
            </Link>
          )}
        </div>

        {recent.length === 0 ? (
          <div className="surface mt-4 p-6 text-center">
            <p className="text-sm text-slate-500 dark:text-slate-400">
              No analyses yet.{' '}
              <Link
                to="/analyze"
                className="font-medium text-brand-600 hover:underline dark:text-brand-400"
              >
                Run one
              </Link>
              .
            </p>
          </div>
        ) : (
          <ul className="mt-4 space-y-2">
            {recent.map((a) => (
              <li key={a.id}>
                <Link
                  to={`/results/${a.id}`}
                  className="surface flex items-center justify-between gap-4 p-4 transition hover:border-brand-400 dark:hover:border-brand-500/50"
                >
                  <span className="min-w-0">
                    <span className="block truncate font-medium">
                      {a.job_title || 'Untitled role'}
                    </span>
                    <span className="block truncate text-xs text-slate-500 dark:text-slate-400">
                      {a.resume_filename} ·{' '}
                      {new Date(a.created_at).toLocaleDateString(undefined, {
                        month: 'short',
                        day: 'numeric',
                      })}
                    </span>
                  </span>
                  <ScorePill score={a.match_score} />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Coming next
        </h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          {NEXT.map(({ phase, title, note }) => (
            <div key={phase} className="surface p-4 opacity-70">
              <span className="font-mono text-xs text-brand-600 dark:text-brand-400">{phase}</span>
              <p className="mt-1.5 font-medium">{title}</p>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{note}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
