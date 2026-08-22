/**
 * The three score components as labelled rows.
 *
 * The point of a transparent score is seeing which part drags it down, so the
 * weight is printed next to each figure rather than hidden in a tooltip.
 */
export function ComponentBars({ result }) {
  const rows = [
    { key: 'text_similarity', label: 'Text similarity', value: result.text_similarity },
    { key: 'skill_match', label: 'Skill match', value: result.skill_match ?? 0 },
    { key: 'keyword_match', label: 'Keyword match', value: result.keyword_match },
  ].filter((r) => result.weights[r.key] !== undefined)

  return (
    <div className="divide-y divide-paper-line dark:divide-ink-800">
      {rows.map((row) => (
        <div key={row.key} className="grid grid-cols-[7.5rem_1fr_auto] items-center gap-4 py-3.5">
          <span className="label !normal-case !tracking-normal !text-[11px] text-ink-500 dark:text-ink-400">
            {row.label}
          </span>

          <span className="relative h-[6px] bg-paper-line dark:bg-ink-800">
            <span
              className="absolute inset-y-0 left-0 bg-ink-950 dark:bg-ink-100"
              style={{ width: `${Math.min(row.value, 100)}%`, transition: 'width 500ms cubic-bezier(.2,.8,.2,1)' }}
            />
          </span>

          <span className="flex items-baseline gap-2">
            <span className="num w-14 text-right text-sm font-medium">{row.value}%</span>
            <span className="num w-9 text-right text-[10px] text-ink-400 dark:text-ink-600">
              ×{result.weights[row.key]}
            </span>
          </span>
        </div>
      ))}
    </div>
  )
}
