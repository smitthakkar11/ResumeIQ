import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ScorePill } from '@/components/ScorePill'
import { Alert } from '@/components/ui'
import { analysisApi, errorMessage } from '@/lib/api'

export function History() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    analysisApi
      .list()
      .then(setItems)
      .catch((e) => setError(errorMessage(e, 'Could not load your history')))
      .finally(() => setLoading(false))
  }, [])

  async function handleDelete(id) {
    try {
      await analysisApi.remove(id)
      setItems((prev) => prev.filter((a) => a.id !== id))
    } catch (e) {
      setError(errorMessage(e, 'Could not delete that analysis'))
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-4xl font-extrabold tracking-tight">History</h1>
        <p className="mt-2 max-w-xl text-base text-ink-500 dark:text-ink-400">
          Results are stored exactly as computed, so a past score never changes
          when the skill dictionary does.
        </p>
      </div>

      {error && <Alert>{error}</Alert>}

      {loading ? (
        <p className="text-sm text-ink-500">Loading…</p>
      ) : items.length === 0 ? (
        <div className="panel px-6 py-16 text-center">
          <p className="text-base text-ink-500 dark:text-ink-400">No analyses yet.</p>
          <Link
            to="/analyze"
            className="rounded-md bg-brand-600 px-6 py-3 text-[15px] font-semibold text-white transition-colors hover:bg-brand-700"
          >
            Run your first analysis
          </Link>
        </div>
      ) : (
        <ul className="divide-y divide-paper-line border-t border-paper-line dark:divide-ink-800 dark:border-ink-800">
          {items.map((a, i) => (
            <li key={a.id} className="group flex items-center gap-4 py-4">
              <span className="num hidden w-8 shrink-0 text-[11px] text-ink-300 sm:block dark:text-ink-700">
                {String(items.length - i).padStart(2, '0')}
              </span>
              <Link to={`/results/${a.id}`} className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium transition-colors group-hover:text-brand-600 dark:group-hover:text-brand-400">
                  {a.job_title || 'Untitled role'}
                </p>
                <p className="num mt-0.5 truncate text-[11px] text-ink-400 dark:text-ink-600">
                  {a.resume_filename} · {new Date(a.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                </p>
              </Link>
              <ScorePill score={a.match_score} />
              <button
                type="button"
                onClick={() => handleDelete(a.id)}
                aria-label={`Delete analysis for ${a.job_title || 'untitled role'}`}
                className="shrink-0 px-2 py-1 text-sm font-medium
                           text-ink-300 transition-colors hover:text-alert dark:text-ink-700"
              >
                Del
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
