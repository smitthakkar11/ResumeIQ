/** Skills grouped by category. Mono chips — these are identifiers, not prose. */
export function SkillBadges({ skills, tone = 'neutral' }) {
  if (skills.length === 0) {
    return (
      <p className="text-sm text-ink-500 dark:text-ink-400">
        No skills from our dictionary were detected in this resume.
      </p>
    )
  }

  const chip = {
    neutral: 'border-paper-line text-ink-700 dark:border-ink-700 dark:text-ink-300',
    matched: 'border-acid-500/40 bg-acid-400/10 text-acid-700 dark:text-acid-300',
    missing: 'border-alert/30 bg-alert/8 text-alert',
  }[tone]

  const byCategory = new Map()
  for (const s of skills) {
    byCategory.set(s.category, [...(byCategory.get(s.category) ?? []), s.name])
  }

  return (
    <div className="space-y-4">
      {[...byCategory].map(([category, names]) => (
        <div key={category} className="grid grid-cols-[6.5rem_1fr] gap-3">
          <span className="label pt-1.5">{category}</span>
          <div className="flex flex-wrap gap-1.5">
            {names.map((name) => (
              <span
                key={name}
                className={`rounded-xs border px-2 py-1 font-mono text-[11px] ${chip}`}
              >
                {name}
              </span>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
