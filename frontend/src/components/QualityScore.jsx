import { useState } from 'react'
import { band } from '@/lib/score'

/**
 * Resume quality, independent of any job.
 *
 * Each component expands to show the individual checks behind its score —
 * that is the whole point of a rule-based score, so it should not be hidden.
 */
export function QualityScore({ overall, components, weights = null }) {
  const [open, setOpen] = useState(null)
  const tone = band(overall)

  return (
    <div className="panel p-6 sm:p-8">
      <div className="flex flex-wrap items-end justify-between gap-6">
        <div>
          <p className="label">Resume quality</p>
          <div className="mt-3 flex items-baseline gap-1.5">
            <span className={`num text-6xl leading-none font-semibold tracking-tighter ${tone.text}`}>
              {overall}
            </span>
            <span className="num text-xl font-medium text-ink-400">/100</span>
          </div>
        </div>
        <p className="max-w-xs text-[13px] leading-relaxed text-ink-500 dark:text-ink-400">
          Scored on the resume alone — no job description involved. Tap a row to
          see the checks behind it.
        </p>
      </div>

      <div className="mt-8 space-y-1">
        {components.map((c) => {
          const isOpen = open === c.key
          const rowTone = band(c.score)
          return (
            <div key={c.key} className="border-b border-paper-line last:border-0 dark:border-ink-800">
              <button
                type="button"
                onClick={() => setOpen(isOpen ? null : c.key)}
                aria-expanded={isOpen}
                className="flex w-full items-center gap-4 py-3 text-left"
              >
                <span className="w-24 shrink-0 text-sm font-medium">{c.label}</span>
                <span className="h-2 flex-1 overflow-hidden rounded-full bg-paper-line dark:bg-ink-800">
                  <span
                    className={`block h-full rounded-full ${rowTone.fill}`}
                    style={{ width: `${c.score}%`, transition: 'width 600ms cubic-bezier(.2,.8,.2,1)' }}
                  />
                </span>
                <span className="num w-14 shrink-0 text-right text-sm font-semibold">
                  {c.score}
                </span>
                {weights && (
                  <span className="num w-10 shrink-0 text-right text-xs text-ink-400">
                    ×{weights[c.key]}
                  </span>
                )}
              </button>

              {isOpen && (
                <ul className="space-y-2 pb-4 pl-24">
                  {c.checks.map((check) => (
                    <li key={check.label} className="flex items-baseline gap-3 text-[13px]">
                      <span className="num w-16 shrink-0 text-right text-ink-500">
                        {check.earned}/{check.maximum}
                      </span>
                      <span>
                        <span className="font-medium">{check.label}</span>
                        <span className="text-ink-500 dark:text-ink-400"> — {check.detail}</span>
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
