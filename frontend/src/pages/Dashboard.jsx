import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ScorePill } from '@/components/ScorePill'
import { SectionHead } from '@/components/ui'
import { analysisApi, resumeApi } from '@/lib/api'
import { useAuth } from '@/lib/auth'

export function Dashboard() {
  const { user } = useAuth()
  const [recent, setRecent] = useState([])
  const [resumeCount, setResumeCount] = useState(null)

  useEffect(() => {
    analysisApi.list().then((all) => setRecent(all)).catch(() => setRecent([]))
    resumeApi.list().then((r) => setResumeCount(r.length)).catch(() => setResumeCount(0))
  }, [])

  if (!user) return null

  const best = recent.length ? Math.max(...recent.map((a) => a.match_score)) : null

  const STATS = [
    ['Resumes', resumeCount ?? '—'],
    ['Analyses', recent.length],
    ['Best match', best === null ? '—' : `${best}%`],
  ]

  return (
    <div className="space-y-14">
      <div className="flex flex-wrap items-end justify-between gap-6">
        <div>
          <h1 className="font-display text-4xl font-extrabold tracking-tight">
            Hello, {user.name.split(' ')[0]}
          </h1>
          <p className="mt-2 text-base text-ink-500 dark:text-ink-400">{user.email}</p>
        </div>
        <Link
          to="/analyze"
          className="rounded-md bg-brand-600 px-6 py-3 text-[15px] font-semibold text-white transition-colors hover:bg-brand-700"
        >
          New analysis
        </Link>
      </div>

      {/* ---- counters ---- */}
      <div className="grid gap-5 sm:grid-cols-3">
        {STATS.map(([label, value]) => (
          <div key={label} className="panel p-6">
            <p className="text-sm font-medium text-ink-500 dark:text-ink-400">{label}</p>
            <p className="num mt-2 text-4xl font-semibold tracking-tight">{value}</p>
          </div>
        ))}
      </div>

      {/* ---- recent ---- */}
      <section>
        <SectionHead
          right={
            recent.length > 0 && (
              <Link to="/history" className="text-sm font-semibold text-brand-600 hover:underline dark:text-brand-400">
                View all
              </Link>
            )
          }
        >
          Recent analyses
        </SectionHead>

        {recent.length === 0 ? (
          <div className="panel px-6 py-14 text-center">
            <p className="text-base text-ink-500 dark:text-ink-400">Nothing analysed yet.</p>
            <Link
              to="/resume/upload"
              className="mt-5 inline-block rounded-md bg-brand-600 px-5 py-2.5 text-[15px]
                         font-semibold text-white transition-colors hover:bg-brand-700"
            >
              Upload a resume
            </Link>
          </div>
        ) : (
          <ul className="space-y-3">
            {recent.slice(0, 5).map((a) => (
              <li key={a.id}>
                <Link
                  to={`/results/${a.id}`}
                  className="panel flex items-center gap-4 p-4 transition-colors hover:border-brand-500/40"
                >
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-[15px] font-semibold">
                      {a.job_title || 'Untitled role'}
                    </span>
                    <span className="mt-1 block truncate text-sm text-ink-500 dark:text-ink-400">
                      {a.resume_filename} · {new Date(a.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                    </span>
                  </span>
                  <ScorePill score={a.match_score} />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
