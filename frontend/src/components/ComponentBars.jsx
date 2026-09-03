/**
 * The three score components. Seeing which one drags the total down is the
 * whole point of a transparent score, so each gets its own row and weight.
 */
export function ComponentBars({ result }) {
  const rows = [
    { key: 'text_similarity', label: 'Text similarity', value: result.text_similarity },
    { key: 'skill_match', label: 'Skill match', value: result.skill_match ?? 0 },
    { key: 'keyword_match', label: 'Keyword match', value: result.keyword_match },
    {
      key: 'experience_match',
      label: 'Experience',
      value: result.experience_match ?? 0,
      note: result.experience_detail,
    },
    {
      key: 'education_match',
      label: 'Education',
      value: result.education_match ?? 0,
      note: result.education_detail,
    },
    // A component the posting did not support is dropped, not scored zero.
  ].filter((r) => result.weights[r.key] !== undefined)

  return (
    <div className="space-y-6">
      {rows.map((row) => (
        <div key={row.key}>
          <div className="flex items-baseline justify-between gap-4">
            <span className="text-sm font-medium">{row.label}</span>
            <span className="flex items-baseline gap-2.5">
              <span className="num text-lg font-semibold">{row.value}%</span>
              <span className="num w-10 text-right text-xs text-ink-400">
                ×{result.weights[row.key]}
              </span>
            </span>
          </div>
          <div className="mt-2 h-2 overflow-hidden rounded-full bg-paper-line dark:bg-ink-800">
            <div
              className="h-full rounded-full bg-ink-900 dark:bg-ink-300"
              style={{ width: `${Math.min(row.value, 100)}%`, transition: 'width 600ms cubic-bezier(.2,.8,.2,1)' }}
            />
          </div>
          {row.note && (
            <p className="mt-1.5 text-[12px] text-ink-400 dark:text-ink-500">{row.note}</p>
          )}
        </div>
      ))}
    </div>
  )
}
