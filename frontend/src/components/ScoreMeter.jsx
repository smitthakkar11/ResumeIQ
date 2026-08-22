/**
 * The headline score: a large mono figure over a segmented meter.
 *
 * Hand-built rather than a chart library. 40 discrete segments read as a
 * measured quantity — a smooth arc reads as decoration.
 */

import { band } from '@/lib/score'

const SEGMENTS = 40

export function ScoreMeter({ score }) {
  const tone = band(score)
  const lit = Math.round((score / 100) * SEGMENTS)

  return (
    <div>
      <div className="flex items-baseline justify-between gap-4">
        <span className="label">Overall match</span>
        <span className={`label ${tone.text}`}>{tone.label}</span>
      </div>

      <div className="mt-4 flex items-end gap-1">
        <span className={`num text-7xl leading-none font-medium ${tone.text}`}>
          {Math.floor(score)}
        </span>
        <span className={`num text-3xl leading-none font-medium ${tone.text} opacity-60`}>
          .{Math.round((score % 1) * 10)}
        </span>
        <span className="num mb-1 ml-1 text-lg text-ink-400 dark:text-ink-500">%</span>
      </div>

      {/* Segmented meter. Unlit segments stay visible so the scale is legible. */}
      <div className="mt-6 flex gap-[3px]" aria-hidden>
        {Array.from({ length: SEGMENTS }, (_, i) => (
          <span
            key={i}
            className={`h-8 flex-1 ${
              i < lit ? tone.fill : 'bg-paper-line dark:bg-ink-800'
            }`}
            style={{ transition: 'background-color 240ms ease', transitionDelay: `${i * 8}ms` }}
          />
        ))}
      </div>

      <div className="mt-2 flex justify-between">
        {[0, 25, 50, 75, 100].map((t) => (
          <span key={t} className="num text-[10px] text-ink-400 dark:text-ink-600">
            {t}
          </span>
        ))}
      </div>
    </div>
  )
}
