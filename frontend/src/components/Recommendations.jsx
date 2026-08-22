const LABELS = {
  skills: { text: 'SKILL', className: 'text-alert' },
  keywords: { text: 'KEYWD', className: 'text-warn' },
  structure: { text: 'STRUCT', className: 'text-ink-400 dark:text-ink-500' },
  content: { text: 'CONTENT', className: 'text-ink-400 dark:text-ink-500' },
  positive: { text: 'OK', className: 'text-acid-600 dark:text-acid-400' },
}

export function Recommendations({ items }) {
  if (items.length === 0) {
    return (
      <p className="text-sm text-ink-500 dark:text-ink-400">
        No suggestions — this resume matches the posting well.
      </p>
    )
  }

  return (
    <ol className="divide-y divide-paper-line dark:divide-ink-800">
      {items.map((item, i) => {
        const tag = LABELS[item.category] ?? LABELS.content
        return (
          <li key={i} className="grid grid-cols-[2rem_4.5rem_1fr] gap-3 py-4">
            <span className="num text-[11px] text-ink-300 dark:text-ink-700">
              {String(i + 1).padStart(2, '0')}
            </span>
            <span className={`num text-[10px] tracking-[0.12em] pt-px ${tag.className}`}>
              {tag.text}
            </span>
            <p className="text-sm leading-relaxed text-ink-700 dark:text-ink-300">{item.message}</p>
          </li>
        )
      })}
    </ol>
  )
}
