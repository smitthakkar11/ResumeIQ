/** Skills grouped by category. */
export function SkillBadges({ skills, tone = 'neutral' }) {
  if (skills.length === 0) {
    return (
      <p className="text-sm text-ink-500 dark:text-ink-400">
        No skills from our dictionary were detected in this resume.
      </p>
    )
  }

  const chip = {
    neutral:
      'border-paper-line bg-white text-ink-700 dark:border-ink-700 dark:bg-ink-850 dark:text-ink-200',
    matched:
      'border-brand-500/25 bg-brand-50 text-brand-700 dark:border-brand-500/30 dark:bg-brand-500/12 dark:text-brand-300',
    missing:
      'border-alert/20 bg-alert-soft text-alert dark:bg-alert/10',
  }[tone]

  const byCategory = new Map()
  for (const s of skills) {
    byCategory.set(s.category, [...(byCategory.get(s.category) ?? []), s.name])
  }

  return (
    <div className="space-y-4">
      {[...byCategory].map(([category, names]) => (
        <div key={category}>
          <p className="mb-2 text-xs font-semibold text-ink-400 uppercase tracking-wide">
            {category}
          </p>
          <div className="flex flex-wrap gap-2">
            {names.map((name) => (
              <span
                key={name}
                className={`rounded-md border px-2.5 py-1.5 text-[13px] font-medium ${chip}`}
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
