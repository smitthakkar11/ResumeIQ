const STYLES = {
  skills: {
    label: 'Skills',
    className: 'bg-rose-50 text-rose-700 dark:bg-rose-500/10 dark:text-rose-300',
  },
  keywords: {
    label: 'Keywords',
    className: 'bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300',
  },
  structure: {
    label: 'Structure',
    className: 'bg-sky-50 text-sky-700 dark:bg-sky-500/10 dark:text-sky-300',
  },
  content: {
    label: 'Content',
    className: 'bg-violet-50 text-violet-700 dark:bg-violet-500/10 dark:text-violet-300',
  },
  positive: {
    label: 'Good',
    className: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300',
  },
}
export function Recommendations({ items }) {
  if (items.length === 0) {
    return (
      <p className="text-sm text-slate-500 dark:text-slate-400">
        No suggestions — this resume matches the posting well.
      </p>
    )
  }
  return (
    <ul className="space-y-3">
      {items.map((item, i) => {
        const style = STYLES[item.category] ?? STYLES.content
        return (
          <li key={i} className="flex gap-3">
            <span
              className={`mt-0.5 h-fit shrink-0 rounded-md px-2 py-0.5 text-[11px] font-medium ${style.className}`}
            >
              {style.label}
            </span>
            <p className="text-sm leading-relaxed text-slate-700 dark:text-slate-300">
              {item.message}
            </p>
          </li>
        )
      })}
    </ul>
  )
}
