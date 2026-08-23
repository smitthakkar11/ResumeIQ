const TAGS = {
  skills: { text: 'Skills', className: 'bg-alert-soft text-alert dark:bg-alert/12' },
  keywords: { text: 'Keywords', className: 'bg-warn-soft text-warn dark:bg-warn/12' },
  structure: { text: 'Structure', className: 'bg-paper-line text-ink-600 dark:bg-ink-800 dark:text-ink-300' },
  content: { text: 'Content', className: 'bg-paper-line text-ink-600 dark:bg-ink-800 dark:text-ink-300' },
  positive: { text: 'Good', className: 'bg-brand-50 text-brand-700 dark:bg-brand-500/12 dark:text-brand-300' },
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
    <ul className="space-y-4">
      {items.map((item, i) => {
        const tag = TAGS[item.category] ?? TAGS.content
        return (
          <li key={i} className="flex flex-col gap-2 sm:flex-row sm:gap-4">
            <span
              className={`h-fit w-fit shrink-0 rounded-md px-2.5 py-1 text-xs font-semibold sm:w-20 sm:text-center ${tag.className}`}
            >
              {tag.text}
            </span>
            <p className="text-[15px] leading-relaxed text-ink-700 dark:text-ink-300">
              {item.message}
            </p>
          </li>
        )
      })}
    </ul>
  )
}
