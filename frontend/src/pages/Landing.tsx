import { useEffect, useState } from 'react'
import { StatusRow, type StatusState } from '@/components/StatusRow'
import { fetchDatabaseHealth, fetchHealth } from '@/lib/api'

const PIPELINE = [
  { step: 'Extract', note: 'PDF → text (PyMuPDF)' },
  { step: 'Preprocess', note: 'clean, tokenise, lemmatise' },
  { step: 'Represent', note: 'TF-IDF vectors' },
  { step: 'Compare', note: 'cosine similarity + skill match' },
  { step: 'Score', note: 'transparent weighted breakdown' },
]

export function Landing() {
  const [apiState, setApiState] = useState<StatusState>('loading')
  const [apiDetail, setApiDetail] = useState('checking…')
  const [dbState, setDbState] = useState<StatusState>('loading')
  const [dbDetail, setDbDetail] = useState('checking…')

  useEffect(() => {
    let cancelled = false

    fetchHealth()
      .then((h) => {
        if (cancelled) return
        setApiState('ok')
        setApiDetail(`${h.status} · ${h.environment}`)
      })
      .catch(() => {
        if (cancelled) return
        setApiState('error')
        setApiDetail('unreachable')
      })

    fetchDatabaseHealth()
      .then((d) => {
        if (cancelled) return
        setDbState(d.status === 'ok' ? 'ok' : 'error')
        setDbDetail(d.detail ? `${d.database} · ${d.detail}` : d.database)
      })
      .catch(() => {
        if (cancelled) return
        setDbState('error')
        setDbDetail('unreachable')
      })

    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="space-y-14">
      {/* ---------- Hero ---------- */}
      <section className="max-w-2xl">
        <span className="inline-flex items-center rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700
                         dark:bg-brand-500/10 dark:text-brand-300">
          Phase 1 · Foundation
        </span>
        <h1 className="mt-5 text-4xl font-bold tracking-tight sm:text-5xl">
          Know exactly why your resume matches — or doesn&apos;t.
        </h1>
        <p className="mt-4 text-lg text-slate-600 dark:text-slate-400">
          ResumeIQ compares a resume against a job description using classical NLP: TF-IDF,
          cosine similarity and explicit skill matching. Every number in the score is one you
          can trace back to the text. No black box, no LLM.
        </p>
      </section>

      {/* ---------- Pipeline preview ---------- */}
      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Analysis pipeline
        </h2>
        <ol className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {PIPELINE.map(({ step, note }, i) => (
            <li key={step} className="surface p-4">
              <span className="font-mono text-xs text-brand-600 dark:text-brand-400">
                0{i + 1}
              </span>
              <p className="mt-1.5 font-medium">{step}</p>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{note}</p>
            </li>
          ))}
        </ol>
      </section>

      {/* ---------- Live system status ---------- */}
      <section className="max-w-xl">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          System status
        </h2>
        <div className="surface mt-4 px-5 py-2">
          <StatusRow label="FastAPI backend" state={apiState} detail={apiDetail} />
          <StatusRow label="MySQL database" state={dbState} detail={dbDetail} />
        </div>
        {(apiState === 'error' || dbState === 'error') && (
          <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">
            Backend not responding? Start it with{' '}
            <code className="rounded bg-slate-100 px-1.5 py-0.5 font-mono dark:bg-slate-800">
              uvicorn app.main:app --reload --port 8001
            </code>{' '}
            from <code className="font-mono">backend/</code>.
          </p>
        )}
      </section>
    </div>
  )
}
