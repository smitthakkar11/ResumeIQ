import { band } from '@/lib/score'

/** Compact score readout for lists. */
export function ScorePill({ score }) {
  const tone = band(score)
  return (
    <span
      className={`num shrink-0 rounded-md px-2.5 py-1 text-sm font-semibold ${tone.soft} ${tone.text}`}
    >
      {score}%
    </span>
  )
}
