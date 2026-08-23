import { useEffect, useRef, useState } from 'react'
import { SkillBadges } from '@/components/SkillBadges'
import { Alert, Button, SectionHead } from '@/components/ui'
import { errorMessage, resumeApi } from '@/lib/api'

const MAX_MB = 5

export function ResumeUpload() {
  const [resumes, setResumes] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [preview, setPreview] = useState(null)
  const [skills, setSkills] = useState(null)
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef(null)

  useEffect(() => {
    resumeApi
      .list()
      .then(setResumes)
      .catch((e) => setError(errorMessage(e, 'Could not load your resumes')))
      .finally(() => setLoading(false))
  }, [])

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

  async function handleFile(file) {
    if (!file) return
    setError('')
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

  async function handleDelete(id) {
    try {
      await resumeApi.remove(id)
      setResumes((prev) => prev.filter((r) => r.id !== id))
      setPreview((p) => (p?.id === id ? null : p))
    } catch (e) {
      setError(errorMessage(e, 'Could not delete that resume'))
    }
  }

  return (
    <div className="space-y-12">
      <div>
        <h1 className="font-display text-4xl font-extrabold tracking-tight">Resumes</h1>
        <p className="mt-2 max-w-xl text-base text-ink-500 dark:text-ink-400">
          Upload a text-based PDF. Keep several versions and compare them against
          the same job.
        </p>
      </div>

      {error && <Alert>{error}</Alert>}

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
        className={`rounded-md border border-dashed p-12 text-center transition-colors ${
          dragging
            ? 'border-brand-500 bg-brand-500/5'
            : 'border-paper-line dark:border-ink-700'
        }`}
      >
        <p className="text-base font-medium">Drop a PDF here</p>
        <div className="mx-auto mt-4 max-w-[11rem]">
          <Button type="button" loading={uploading} onClick={() => inputRef.current?.click()}>
            {uploading ? 'Reading' : 'Choose file'}
          </Button>
        </div>
        <p className="mt-4 text-sm text-ink-400">PDF · max {MAX_MB} MB · not scanned</p>
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
      </div>

      <section>
        <SectionHead right={<span className="num text-xs text-ink-400">{resumes.length}</span>}>
          Uploaded
        </SectionHead>

        {loading ? (
          <p className="text-sm text-ink-500">Loading…</p>
        ) : resumes.length === 0 ? (
          <p className="py-8 text-center text-sm text-ink-500 dark:text-ink-400">
            Nothing uploaded yet.
          </p>
        ) : (
          <ul className="space-y-3">
            {resumes.map((r) => (
              <li key={r.id} className="panel flex items-center gap-4 p-4">
                <span className="num shrink-0 rounded-md bg-paper-line px-2 py-1 text-xs font-semibold text-ink-600 dark:bg-ink-800 dark:text-ink-300">
                  v{r.version}
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-[15px] font-semibold">{r.filename}</span>
                  <span className="mt-1 block text-sm text-ink-500 dark:text-ink-400">
                    {r.page_count} page{r.page_count === 1 ? '' : 's'} ·{' '}
                    {new Date(r.created_at).toLocaleDateString()}
                  </span>
                </span>
                <button
                  type="button"
                  onClick={() => resumeApi.get(r.id).then(setPreview).catch(() => {})}
                  className="shrink-0 px-2 py-1 text-sm font-medium
                             text-ink-400 transition-colors hover:text-brand-600 dark:hover:text-brand-400"
                >
                  Inspect
                </button>
                <button
                  type="button"
                  onClick={() => handleDelete(r.id)}
                  className="shrink-0 px-2 py-1 text-sm font-medium
                             text-ink-300 transition-colors hover:text-alert dark:text-ink-700"
                >
                  Del
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      {preview && (
        <div className="space-y-10">
          {skills && (
            <section>
              <SectionHead right={<span className="num text-xs text-ink-400">{skills.total}</span>}>
                Skills detected in {preview.filename}
              </SectionHead>
              <SkillBadges skills={skills.skills} />
            </section>
          )}

          <section>
            <SectionHead
              right={
                <button
                  type="button"
                  onClick={() => setPreview(null)}
                  className="text-sm font-medium text-ink-500 transition-colors hover:text-alert"
                >
                  Close
                </button>
              }
            >
              Extracted text
            </SectionHead>
            <pre className="panel max-h-96 overflow-auto p-5 font-mono text-[13px] leading-relaxed whitespace-pre-wrap">
              {preview.extracted_text}
            </pre>
            <p className="mt-2 text-[11px] text-ink-400 dark:text-ink-600">
              This is exactly what gets compared against the job description.
            </p>
          </section>
        </div>
      )}
    </div>
  )
}
