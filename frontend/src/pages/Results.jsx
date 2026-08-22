import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { AnalysisReport } from '@/components/AnalysisReport'
import { Spinner } from '@/components/Spinner'
import { Alert } from '@/components/ui'
import { analysisApi, errorMessage, jobApi } from '@/lib/api'
export function Results() {
  const { id } = useParams()
  const [result, setResult] = useState(null)
  const [job, setJob] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  useEffect(() => {
    if (!id) return
    let cancelled = false
    analysisApi
      .get(Number(id))
      .then((data) => {
        if (cancelled) return
        setResult(data)
        // The saved job description, so the user can see what they compared against.
        if (data.job_description_id) {
          jobApi
            .get(data.job_description_id)
            .then((j) => !cancelled && setJob(j))
            .catch(() => {})
        }
      })
      .catch((e) => !cancelled && setError(errorMessage(e, 'Analysis not found')))
      .finally(() => !cancelled && setLoading(false))
    return () => {
      cancelled = true
    }
  }, [id])
  if (loading) return <Spinner />
  if (error || !result) {
    return (
      <div className="space-y-4">
        <Alert>{error || 'Analysis not found'}</Alert>
        <Link
          to="/history"
          className="text-sm font-medium text-brand-600 hover:underline dark:text-brand-400"
        >
          ← Back to history
        </Link>
      </div>
    )
  }
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <Link
          to="/history"
          className="text-sm font-medium text-brand-600 hover:underline dark:text-brand-400"
        >
          ← History
        </Link>
        <span className="text-xs text-slate-500 dark:text-slate-500">
          Analysed {new Date(result.created_at).toLocaleString()}
        </span>
      </div>

      <AnalysisReport result={result} />

      {job && (
        <details className="surface p-5">
          <summary className="cursor-pointer text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
            Job description
          </summary>
          <p className="mt-4 text-sm leading-relaxed whitespace-pre-wrap text-slate-700 dark:text-slate-300">
            {job.description}
          </p>
        </details>
      )}
    </div>
  )
}
