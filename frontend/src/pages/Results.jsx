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
        if (data.job_description_id) {
          jobApi.get(data.job_description_id).then((j) => !cancelled && setJob(j)).catch(() => {})
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
      <div className="space-y-5">
        <Alert>{error || 'Analysis not found'}</Alert>
        <Link to="/history" className="text-sm font-semibold text-brand-600 transition-colors hover:underline dark:text-brand-400">
          ← Back to history
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div className="flex items-baseline justify-between gap-4">
        <Link to="/history" className="text-sm font-semibold text-brand-600 transition-colors hover:underline dark:text-brand-400">
          ← History
        </Link>
        <span className="text-sm text-ink-400">
          {new Date(result.created_at).toLocaleString()}
        </span>
      </div>

      <AnalysisReport result={result} />

      {job && (
        <details className="rule group pt-4">
          <summary className="cursor-pointer list-none font-display text-lg font-bold tracking-tight transition-colors hover:text-brand-600 dark:hover:text-brand-400">
            Job description
          </summary>
          <p className="mt-5 max-w-3xl text-[15px] leading-relaxed whitespace-pre-wrap text-ink-600 dark:text-ink-300">
            {job.description}
          </p>
        </details>
      )}
    </div>
  )
}
