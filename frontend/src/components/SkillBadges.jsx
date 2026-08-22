/** Groups skills by category and renders them as badges. */
export function SkillBadges({ skills }) {
  if (skills.length === 0) {
    return (
      <p className="text-sm text-slate-500 dark:text-slate-400">
        No skills from our dictionary were detected in this resume.
      </p>
    )
  }
  const byCategory = new Map()
  for (const s of skills) {
    byCategory.set(s.category, [...(byCategory.get(s.category) ?? []), s.name])
  }
  return (
    <div className="space-y-4">
      {[...byCategory].map(([category, names]) => (
        <div key={category}>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-400 dark:text-slate-500">
            {category}
          </p>
          <div className="mt-2 flex flex-wrap gap-1.5">
            {names.map((name) => (
              <span
                key={name}
                className="rounded-md bg-brand-50 px-2 py-1 text-xs font-medium text-brand-700
                           dark:bg-brand-500/10 dark:text-brand-300"
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
