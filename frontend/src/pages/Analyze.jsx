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
    <div className="space-y-12">
      <div>
        <span className="label">New analysis</span>
        <h1 className="mt-3 font-display text-4xl font-bold tracking-tight">Analyze</h1>
      </div>

      {error && <Alert>{error}</Alert>}

      {resumes.length === 0 ? (
        <div className="panel px-6 py-16 text-center">
          <p className="text-sm text-ink-500 dark:text-ink-400">
            Upload a resume first, then come back here.
          </p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-8">
          <div className="grid gap-8 lg:grid-cols-[minmax(0,20rem)_1fr]">
          <div className="space-y-5">
            <label className="block">
              <span className="label mb-2 block text-ink-600 dark:text-ink-400">Resume</span>
              <select
                value={resumeId}
                onChange={(e) => setResumeId(Number(e.target.value))}
                className="w-full rounded-xs border border-paper-line bg-transparent px-3 py-2.5 text-sm
                           outline-none focus:border-acid-500 dark:border-ink-700"
              >
                {resumes.map((r) => (
                  <option key={r.id} value={r.id} className="bg-white dark:bg-ink-900">
                    v{r.version} — {r.filename}
                  </option>
                ))}
              </select>
            </label>

            <Field
              label="Job title"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              placeholder="Software Engineer Intern"
            />

          </div>

          <label className="block">
            <span className="label mb-2 flex items-baseline justify-between text-ink-600 dark:text-ink-400">
              <span>Job description</span>
              <span className={`num ${tooShort ? 'text-alert' : 'text-ink-400 dark:text-ink-600'}`}>
                {jobDescription.length}
                {tooShort && ` / ${MIN_JD_LENGTH} min`}
              </span>
            </span>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={14}
              required
              placeholder="Paste the full job description here…"
              className="w-full rounded-xs border border-paper-line bg-transparent px-3.5 py-3 text-sm
                         leading-relaxed outline-none placeholder:text-ink-400
                         focus:border-acid-500 dark:border-ink-700 dark:placeholder:text-ink-600"
            />
          </label>
          </div>

          <div className="max-w-xs">
            <Button type="submit" loading={loading} disabled={tooShort || !jobDescription}>
              {loading ? 'Analysing' : 'Analyze'}
            </Button>
          </div>
        </form>
      )}

      {result && <AnalysisReport result={result} divider />}
    </div>
  )
}
