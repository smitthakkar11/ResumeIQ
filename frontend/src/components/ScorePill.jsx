import { band } from '@/lib/score'

/** Compact score readout for lists. Mono, banded, with a mini meter. */
export function ScorePill({ score }) {
  const tone = band(score)

  return (
    <span className="flex shrink-0 items-center gap-2.5">
      <span className="hidden h-1 w-14 bg-paper-line sm:block dark:bg-ink-800">
        <span className={`block h-full ${tone.fill}`} style={{ width: `${Math.min(score, 100)}%` }} />
      </span>
      <span className={`num w-14 text-right text-sm font-medium ${tone.text}`}>{score}%</span>
    </span>
  )
}
