import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ScorePill } from '@/components/ScorePill'
import { Alert } from '@/components/ui'
import { analysisApi, errorMessage, type AnalysisSummary } from '@/lib/api'

export function History() {
  const [items, setItems] = useState<AnalysisSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    analysisApi
      .list()
      .then(setItems)
      .catch((e) => setError(errorMessage(e, 'Could not load your history')))
      .finally(() => setLoading(false))
  }, [])

  async function handleDelete(id: number) {
    try {
      await analysisApi.remove(id)
      setItems((prev) => prev.filter((a) => a.id !== id))
    } catch (e) {
      setError(errorMessage(e, 'Could not delete that analysis'))
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">History</h1>
        <p className="mt-1.5 text-slate-600 dark:text-slate-400">
          Every analysis you have run. Results are stored as computed, so past
          scores never change.
        </p>
      </div>

      {error && <Alert>{error}</Alert>}

      {loading ? (
        <p className="text-sm text-slate-500">Loading…</p>
      ) : items.length === 0 ? (
        <div className="surface p-10 text-center">
          <p className="text-sm text-slate-500 dark:text-slate-400">
            No analyses yet.
          </p>
          <Link
            to="/analyze"
            className="mt-4 inline-block rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700"
          >
            Run your first analysis
          </Link>
        </div>
      ) : (
        <ul className="space-y-2">
          {items.map((a) => (
            <li key={a.id} className="surface flex items-center gap-4 p-4">
              <Link to={`/results/${a.id}`} className="min-w-0 flex-1">
                <p className="truncate font-medium">{a.job_title || 'Untitled role'}</p>
                <p className="truncate text-xs text-slate-500 dark:text-slate-400">
                  {a.resume_filename} ·{' '}
                  {new Date(a.created_at).toLocaleDateString(undefined, {
                    month: 'short',
                    day: 'numeric',
                  })}
                </p>
              </Link>
              <ScorePill score={a.match_score} />
              <button
                type="button"
                onClick={() => handleDelete(a.id)}
                aria-label={`Delete analysis for ${a.job_title || 'untitled role'}`}
                className="rounded-lg px-2.5 py-1.5 text-sm font-medium text-slate-500 transition
                           hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-500/10 dark:hover:text-rose-400"
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
