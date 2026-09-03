/**
 * What is holding the resume back, ranked by estimated points lost.
 *
 * The cost comes from the same weights the score uses, so the ordering is
 * defensible: the top item is genuinely the one worth fixing first.
 */
const TONE = {
  skills: 'bg-alert-soft text-alert dark:bg-alert/12',
  keywords: 'bg-warn-soft text-warn dark:bg-warn/12',
  wording: 'bg-warn-soft text-warn dark:bg-warn/12',
  experience: 'bg-paper-line text-ink-600 dark:bg-ink-800 dark:text-ink-300',
  education: 'bg-paper-line text-ink-600 dark:bg-ink-800 dark:text-ink-300',
}

export function Blockers({ blockers }) {
  if (blockers.length === 0) {
    return (
      <p className="text-sm text-ink-500 dark:text-ink-400">
        Nothing significant is holding this application back.
      </p>
    )
  }

  const total = blockers.reduce((sum, b) => sum + b.cost, 0)

  return (
    <div>
      <p className="mb-5 text-[15px] text-ink-600 dark:text-ink-300">
        These account for roughly{' '}
        <span className="num font-semibold">{total.toFixed(1)}</span> of the points
        you did not score, largest first.
      </p>

      <ol className="space-y-3">
        {blockers.map((b) => (
          <li key={b.title} className="panel p-5">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <h3 className="text-[15px] font-semibold">{b.title}</h3>
              <span
                className={`num shrink-0 rounded-md px-2.5 py-1 text-xs font-semibold ${
                  TONE[b.category] ?? TONE.experience
                }`}
              >
                −{b.cost} pts
              </span>
            </div>

            <p className="mt-2 text-sm leading-relaxed text-ink-600 dark:text-ink-300">
              {b.detail}
            </p>

            <p className="mt-3 border-l-2 border-brand-500 pl-3.5 text-sm leading-relaxed
                          text-ink-600 dark:text-ink-300">
              {b.fix}
            </p>
          </li>
        ))}
      </ol>
    </div>
  )
}
