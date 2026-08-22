import { useEffect, useRef, useState } from 'react'
import { SkillBadges } from '@/components/SkillBadges'
import { Alert, Button } from '@/components/ui'
import {
  errorMessage,
  resumeApi,
  type ResumeDetail,
  type ResumeSkills,
  type ResumeSummary,
} from '@/lib/api'

const MAX_MB = 5

export function ResumeUpload() {
  const [resumes, setResumes] = useState<ResumeSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [preview, setPreview] = useState<ResumeDetail | null>(null)
  const [skills, setSkills] = useState<ResumeSkills | null>(null)
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  // Skills are fetched alongside whichever resume is being previewed.
  useEffect(() => {
    if (!preview) {
      setSkills(null)
      return
    }
    let cancelled = false
    resumeApi
      .skills(preview.id)
      .then((s) => !cancelled && setSkills(s))
      .catch(() => !cancelled && setSkills(null))
    return () => {
      cancelled = true
    }
  }, [preview])

  useEffect(() => {
    resumeApi
      .list()
      .then(setResumes)
      .catch((e) => setError(errorMessage(e, 'Could not load your resumes')))
      .finally(() => setLoading(false))
  }, [])

  async function handleFile(file: File | undefined) {
    if (!file) return
    setError('')

    // Fail fast in the browser; the server enforces the same limit anyway.
    if (file.size > MAX_MB * 1024 * 1024) {
      setError(`"${file.name}" is larger than ${MAX_MB} MB.`)
      return
    }

    setUploading(true)
    try {
      const created = await resumeApi.upload(file)
      setResumes((prev) => [created, ...prev])
      setPreview(created)
    } catch (e) {
      setError(errorMessage(e, 'Upload failed'))
    } finally {
      setUploading(false)
      if (inputRef.current) inputRef.current.value = ''
    }
  }

  async function handleDelete(id: number) {
    try {
      await resumeApi.remove(id)
      setResumes((prev) => prev.filter((r) => r.id !== id))
      setPreview((p) => (p?.id === id ? null : p))
    } catch (e) {
      setError(errorMessage(e, 'Could not delete that resume'))
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Resumes</h1>
        <p className="mt-1.5 text-slate-600 dark:text-slate-400">
          Upload a text-based PDF. We extract the text and keep it for analysis.
        </p>
      </div>

      {error && <Alert>{error}</Alert>}

      {/* ---- drop zone ---- */}
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragging(false)
          handleFile(e.dataTransfer.files[0])
        }}
        className={`rounded-xl border-2 border-dashed p-10 text-center transition ${
          dragging
            ? 'border-brand-500 bg-brand-50 dark:bg-brand-500/10'
            : 'border-slate-300 dark:border-slate-700'
        }`}
      >
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Drag a PDF here, or
        </p>
        <div className="mx-auto mt-3 max-w-[12rem]">
          <Button type="button" loading={uploading} onClick={() => inputRef.current?.click()}>
            {uploading ? 'Extracting…' : 'Choose file'}
          </Button>
        </div>
        <p className="mt-3 text-xs text-slate-500 dark:text-slate-500">
          PDF only · up to {MAX_MB} MB · scanned resumes are not supported
        </p>
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
      </div>

      {/* ---- list ---- */}
      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Your resumes
        </h2>

        {loading ? (
          <p className="mt-4 text-sm text-slate-500">Loading…</p>
        ) : resumes.length === 0 ? (
          <div className="surface mt-4 p-8 text-center">
            <p className="text-sm text-slate-500 dark:text-slate-400">
              No resumes yet. Upload one above to get started.
            </p>
          </div>
        ) : (
          <ul className="mt-4 space-y-2">
            {resumes.map((r) => (
              <li key={r.id} className="surface flex items-center justify-between gap-4 p-4">
                <div className="min-w-0">
                  <p className="flex items-center gap-2 truncate font-medium">
                    <span className="shrink-0 rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[11px] text-slate-600 dark:bg-slate-800 dark:text-slate-400">
                      v{r.version}
                    </span>
                    <span className="truncate">{r.filename}</span>
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {r.page_count} page{r.page_count === 1 ? '' : 's'} ·{' '}
                    {new Date(r.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex shrink-0 gap-2 text-sm">
                  <button
                    type="button"
                    onClick={() => resumeApi.get(r.id).then(setPreview).catch(() => {})}
                    className="rounded-lg px-2.5 py-1.5 font-medium text-brand-600 hover:bg-brand-50 dark:text-brand-400 dark:hover:bg-brand-500/10"
                  >
                    View text
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDelete(r.id)}
                    className="rounded-lg px-2.5 py-1.5 font-medium text-slate-500 hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-500/10 dark:hover:text-rose-400"
                  >
                    Delete
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* ---- extracted text ---- */}
      {preview && (
        <section>
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Analysis · {preview.filename}
            </h2>
            <button
              type="button"
              onClick={() => setPreview(null)}
              className="text-sm text-slate-500 hover:text-slate-900 dark:hover:text-slate-200"
            >
              Close
            </button>
          </div>
          {skills && (
            <div className="surface mt-4 p-5">
              <p className="mb-4 text-sm">
                <span className="font-semibold">{skills.total}</span> skill
                {skills.total === 1 ? '' : 's'} detected
              </p>
              <SkillBadges skills={skills.skills} />
            </div>
          )}

          <pre className="surface mt-4 max-h-96 overflow-auto p-5 text-xs leading-relaxed whitespace-pre-wrap">
            {preview.extracted_text}
          </pre>
          <p className="mt-2 text-xs text-slate-500 dark:text-slate-500">
            This is exactly what the matching engine will see in Phase 5.
          </p>
        </section>
      )}
    </div>
  )
}
