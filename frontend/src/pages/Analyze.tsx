import { useEffect, useState, type FormEvent } from 'react'
import { SkillBadges } from '@/components/SkillBadges'
import { Alert, Button, Field } from '@/components/ui'
import {
  analysisApi,
  errorMessage,
  resumeApi,
  type AnalysisResponse,
  type ResumeSummary,
} from '@/lib/api'

const MIN_JD_LENGTH = 50

function ScoreCard({ label, value, hint }: { label: string; value: number | null; hint?: string }) {
  return (
    <div className="surface p-5">
      <p className="text-xs font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
        {label}
      </p>
      <p className="mt-2 text-3xl font-bold tabular-nums">
        {value === null ? <span className="text-xl text-slate-400">n/a</span> : `${value}%`}
      </p>
      {hint && <p className="mt-1 text-xs text-slate-500 dark:text-slate-500">{hint}</p>}
    </div>
  )
}

export function Analyze() {
  const [resumes, setResumes] = useState<ResumeSummary[]>([])
  const [resumeId, setResumeId] = useState<number | ''>('')
  const [jobTitle, setJobTitle] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [result, setResult] = useState<AnalysisResponse | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    resumeApi
      .list()
      .then((list) => {
        setResumes(list)
        if (list.length) setResumeId(list[0].id)
      })
      .catch((e) => setError(errorMessage(e, 'Could not load your resumes')))
  }, [])

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (resumeId === '') return
    setError('')
    setLoading(true)
    try {
      setResult(await analysisApi.create(resumeId, jobTitle, jobDescription))
    } catch (e) {
      setError(errorMessage(e, 'Analysis failed'))
    } finally {
      setLoading(false)
    }
  }

  const tooShort = jobDescription.length > 0 && jobDescription.length < MIN_JD_LENGTH

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Analyze</h1>
        <p className="mt-1.5 text-slate-600 dark:text-slate-400">
          Compare a resume against a job description.
        </p>
      </div>

      {error && <Alert>{error}</Alert>}

      {resumes.length === 0 ? (
        <div className="surface p-8 text-center">
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Upload a resume first, then come back here.
          </p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="grid gap-4 lg:grid-cols-2">
          <div className="space-y-4">
            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
                Resume
              </span>
              <select
                value={resumeId}
                onChange={(e) => setResumeId(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm
                           dark:border-slate-700 dark:bg-slate-900"
              >
                {resumes.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.filename}
                  </option>
                ))}
              </select>
            </label>

            <Field
              label="Job title (optional)"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              placeholder="Software Engineer Intern"
            />
          </div>

          <div className="space-y-4">
            <label className="block">
              <span className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
                Job description
              </span>
              <textarea
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                rows={9}
                required
                placeholder="Paste the full job description here…"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none
                           focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30
                           dark:border-slate-700 dark:bg-slate-900"
              />
              <span className="mt-1 block text-xs text-slate-500 dark:text-slate-500">
                {jobDescription.length} characters
                {tooShort && ` · need at least ${MIN_JD_LENGTH}`}
              </span>
            </label>

            <Button type="submit" loading={loading} disabled={tooShort || !jobDescription}>
              Analyze
            </Button>
          </div>
        </form>
      )}

      {result && (
        <div className="space-y-8 border-t border-slate-200 pt-8 dark:border-slate-800">
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <ScoreCard label="Overall match" value={result.overall_score} />
            <ScoreCard
              label="Text similarity"
              value={result.text_similarity}
              hint={`weight ${result.weights.text_similarity ?? 0}`}
            />
            <ScoreCard
              label="Skill match"
              value={result.skill_match}
              hint={
                result.skill_match === null
                  ? 'no known skills in the job description'
                  : `weight ${result.weights.skill_match ?? 0}`
              }
            />
            <ScoreCard
              label="Keyword match"
              value={result.keyword_match}
              hint={`weight ${result.weights.keyword_match ?? 0}`}
            />
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <section className="surface p-5">
              <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                Matched skills ({result.matched_skills.length})
              </h2>
              <SkillBadges skills={result.matched_skills} />
            </section>

            <section className="surface p-5">
              <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-rose-600 dark:text-rose-400">
                Missing skills ({result.missing_skills.length})
              </h2>
              {result.missing_skills.length === 0 ? (
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Nothing missing — the resume covers every skill the job named.
                </p>
              ) : (
                <SkillBadges skills={result.missing_skills} />
              )}
            </section>
          </div>

          <section className="surface p-5">
            <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Important keywords
            </h2>
            <div className="flex flex-wrap gap-2">
              {result.keywords.map((k) => (
                <span
                  key={k.term}
                  className={`rounded-md px-2 py-1 font-mono text-xs ${
                    k.found
                      ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300'
                      : 'bg-rose-50 text-rose-700 dark:bg-rose-500/10 dark:text-rose-300'
                  }`}
                >
                  {k.found ? '✓' : '✗'} {k.term}
                </span>
              ))}
            </div>
          </section>
        </div>
      )}
    </div>
  )
}
