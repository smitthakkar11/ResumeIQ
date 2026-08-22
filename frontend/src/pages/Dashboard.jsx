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
          <span className="label">Signed in as {user.email}</span>
          <h1 className="mt-3 font-display text-4xl font-bold tracking-tight">
            {user.name.split(' ')[0]}
          </h1>
        </div>
        <Link
          to="/analyze"
          className="rounded-xs bg-acid-400 px-5 py-3 font-mono text-[11px] font-medium uppercase
                     tracking-[0.12em] text-ink-950 transition-colors hover:bg-acid-300"
        >
          New analysis
        </Link>
      </div>

      {/* ---- counters ---- */}
      <div className="grid gap-px bg-paper-line sm:grid-cols-3 dark:bg-ink-800">
        {STATS.map(([label, value]) => (
          <div key={label} className="bg-paper px-5 py-6 dark:bg-ink-950">
            <span className="label">{label}</span>
            <p className="num mt-2 text-4xl font-medium">{value}</p>
          </div>
        ))}
      </div>

      {/* ---- recent ---- */}
      <section>
        <SectionHead
          right={
            recent.length > 0 && (
              <Link to="/history" className="label transition-colors hover:text-acid-600 dark:hover:text-acid-400">
                View all →
              </Link>
            )
          }
        >
          Recent analyses
        </SectionHead>

        {recent.length === 0 ? (
          <div className="panel px-6 py-12 text-center">
            <p className="text-sm text-ink-500 dark:text-ink-400">
              Nothing analysed yet.
            </p>
            <Link
              to="/resume/upload"
              className="mt-4 inline-block font-mono text-[11px] uppercase tracking-[0.12em]
                         text-acid-600 hover:underline dark:text-acid-400"
            >
              Upload a resume →
            </Link>
          </div>
        ) : (
          <ul className="divide-y divide-paper-line dark:divide-ink-800">
            {recent.slice(0, 5).map((a) => (
              <li key={a.id}>
                <Link
                  to={`/results/${a.id}`}
                  className="group flex items-center gap-4 py-3.5 transition-colors"
                >
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-sm font-medium transition-colors group-hover:text-acid-600 dark:group-hover:text-acid-400">
                      {a.job_title || 'Untitled role'}
                    </span>
                    <span className="num mt-0.5 block truncate text-[11px] text-ink-400 dark:text-ink-600">
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
