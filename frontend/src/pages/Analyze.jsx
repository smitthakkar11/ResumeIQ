import { useEffect, useState } from 'react'
import { AnalysisReport } from '@/components/AnalysisReport'
import { Alert, Button, Field } from '@/components/ui'
import { analysisApi, errorMessage, resumeApi } from '@/lib/api'
const MIN_JD_LENGTH = 50
export function Analyze() {
  const [resumes, setResumes] = useState([])
  const [resumeId, setResumeId] = useState('')
  const [jobTitle, setJobTitle] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [result, setResult] = useState(null)
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
  async function handleSubmit(event) {
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
                    v{r.version} — {r.filename}
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

      {result && <AnalysisReport result={result} divider />}
    </div>
  )
}
