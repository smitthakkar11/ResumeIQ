import { band } from '@/lib/score'

/** The headline score. Large enough to be the first thing you see. */
export function ScoreMeter({ score }) {
  const tone = band(score)

  return (
    <div>
      <div className="flex items-center justify-between gap-4">
        <span className="label">Overall match</span>
        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${tone.soft} ${tone.text}`}>
          {tone.label}
        </span>
      </div>

      <div className="mt-6 flex items-baseline gap-1.5">
        <span className={`num text-8xl leading-none font-semibold tracking-tighter ${tone.text}`}>
          {score.toFixed(1)}
        </span>
        <span className="num text-2xl font-medium text-ink-400">%</span>
      </div>

      <div className="mt-8 h-3 overflow-hidden rounded-full bg-paper-line dark:bg-ink-800">
        <div
          className={`h-full rounded-full ${tone.fill}`}
          style={{ width: `${Math.min(score, 100)}%`, transition: 'width 700ms cubic-bezier(.2,.8,.2,1)' }}
        />
      </div>

      <div className="mt-2.5 flex justify-between">
        {[0, 25, 50, 75, 100].map((t) => (
          <span key={t} className="num text-[11px] text-ink-400">
            {t}
          </span>
        ))}
      </div>
    </div>
  )
}
