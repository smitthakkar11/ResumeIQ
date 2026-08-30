/** What we could read out of the job description itself. */
export function JobIntelligence({ requirements }) {
  const { role, preferred_skills, soft_skills, education, experience, confidence } = requirements

  const facts = [
    ['Role', role, confidence.role],
    ['Education', education, confidence.education],
    ['Experience', experience, confidence.experience],
  ].filter(([, value]) => value)

  const nothingFound = facts.length === 0 && preferred_skills.length === 0 && soft_skills.length === 0

  if (nothingFound) {
    return (
      <p className="text-sm text-ink-500 dark:text-ink-400">
        This posting didn&apos;t state a role, degree or experience level in a form
        we could read.
      </p>
    )
  }

  return (
    <div className="space-y-6">
      {facts.length > 0 && (
        <dl className="grid gap-4 sm:grid-cols-3">
          {facts.map(([label, value]) => (
            <div key={label}>
              <dt className="text-xs font-semibold text-ink-400 uppercase tracking-wide">
                {label}
              </dt>
              <dd className="mt-1 text-[15px] font-semibold">{value}</dd>
            </div>
          ))}
        </dl>
      )}

      {preferred_skills.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-semibold text-ink-400 uppercase tracking-wide">
            Nice to have — not scored
          </p>
          <div className="flex flex-wrap gap-2">
            {preferred_skills.map((s) => (
              <span
                key={s.name}
                className="rounded-md border border-paper-line bg-white px-2.5 py-1.5 text-[13px]
                           font-medium text-ink-600 dark:border-ink-700 dark:bg-ink-850 dark:text-ink-300"
              >
                {s.name}
              </span>
            ))}
          </div>
        </div>
      )}

      {soft_skills.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-semibold text-ink-400 uppercase tracking-wide">
            Soft skills mentioned
          </p>
          <div className="flex flex-wrap gap-2">
            {soft_skills.map((s) => (
              <span
                key={s}
                className="rounded-md border border-paper-line bg-white px-2.5 py-1.5 text-[13px]
                           font-medium text-ink-600 dark:border-ink-700 dark:bg-ink-850 dark:text-ink-300"
              >
                {s}
              </span>
            ))}
          </div>
        </div>
      )}

      <p className="text-[13px] leading-relaxed text-ink-500 dark:text-ink-400">
        Read directly from the posting&apos;s wording. Job descriptions have no
        standard format, so anything not stated plainly is left blank rather
        than guessed.
      </p>
    </div>
  )
}
