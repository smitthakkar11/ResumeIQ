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
        <span className="label">Your files</span>
        <h1 className="mt-3 font-display text-4xl font-bold tracking-tight">Resumes</h1>
        <p className="mt-2 max-w-lg text-sm text-ink-500 dark:text-ink-400">
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
        className={`rounded-xs border border-dashed p-12 text-center transition-colors ${
          dragging
            ? 'border-acid-400 bg-acid-400/5'
            : 'border-paper-line dark:border-ink-700'
        }`}
      >
        <p className="text-sm text-ink-500 dark:text-ink-400">Drop a PDF here</p>
        <div className="mx-auto mt-4 max-w-[11rem]">
          <Button type="button" loading={uploading} onClick={() => inputRef.current?.click()}>
            {uploading ? 'Reading' : 'Choose file'}
          </Button>
        </div>
        <p className="label mt-4">PDF · max {MAX_MB} MB · not scanned</p>
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
          <p className="label">Loading…</p>
        ) : resumes.length === 0 ? (
          <p className="py-8 text-center text-sm text-ink-500 dark:text-ink-400">
            Nothing uploaded yet.
          </p>
        ) : (
          <ul className="divide-y divide-paper-line dark:divide-ink-800">
            {resumes.map((r) => (
              <li key={r.id} className="flex items-center gap-4 py-3.5">
                <span className="num shrink-0 rounded-xs border border-paper-line px-1.5 py-0.5 text-[10px] text-ink-500 dark:border-ink-700 dark:text-ink-400">
                  v{r.version}
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-sm">{r.filename}</span>
                  <span className="num mt-0.5 block text-[11px] text-ink-400 dark:text-ink-600">
                    {r.page_count} page{r.page_count === 1 ? '' : 's'} ·{' '}
                    {new Date(r.created_at).toLocaleDateString()}
                  </span>
                </span>
                <button
                  type="button"
                  onClick={() => resumeApi.get(r.id).then(setPreview).catch(() => {})}
                  className="shrink-0 px-2 py-1 font-mono text-[10px] uppercase tracking-[0.1em]
                             text-ink-400 transition-colors hover:text-acid-600 dark:hover:text-acid-400"
                >
                  Inspect
                </button>
                <button
                  type="button"
                  onClick={() => handleDelete(r.id)}
                  className="shrink-0 px-2 py-1 font-mono text-[10px] uppercase tracking-[0.1em]
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
                  className="label transition-colors hover:text-alert"
                >
                  Close
                </button>
              }
            >
              Extracted text
            </SectionHead>
            <pre className="panel max-h-96 overflow-auto p-5 font-mono text-[11px] leading-relaxed whitespace-pre-wrap">
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
