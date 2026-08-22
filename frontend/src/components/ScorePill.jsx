/** Compact score chip, colour-banded to match the gauge. */
export function ScorePill({ score }) {
  const tone =
    score >= 70
      ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300'
      : score >= 45
        ? 'bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-300'
        : 'bg-rose-50 text-rose-700 dark:bg-rose-500/10 dark:text-rose-300'
  return (
    <span className={`rounded-md px-2 py-1 text-sm font-semibold tabular-nums ${tone}`}>
      {score}%
    </span>
  )
}
