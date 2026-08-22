/**
 * Word-overlap score against meaning-based score.
 *
 * Shown for comparison only — the meaning score is not part of the overall
 * match, because it cannot be traced back to specific words.
 */
export function SemanticComparison({ result }) {
  const rows = [
    {
      label: 'Word overlap',
      value: result.text_similarity,
      note: 'How much of the posting’s actual vocabulary appears in your resume.',
      fill: 'bg-ink-950 dark:bg-ink-100',
    },
    {
      label: 'Meaning',
      value: result.semantic_similarity,
      note: 'Whether you describe the same work, even in different words.',
      fill: 'bg-acid-400',
    },
  ]

  const gap = Math.round((result.semantic_similarity - result.text_similarity) * 10) / 10

  return (
    <section>
      <div className="rule mb-5 pt-4">
        <h3 className="label">Wording vs meaning</h3>
      </div>

      <div className="grid gap-8 sm:grid-cols-2">
        {rows.map((row) => (
          <div key={row.label}>
            <div className="flex items-baseline gap-2">
              <span className="num text-4xl font-medium">{row.value}</span>
              <span className="num text-sm text-ink-400">%</span>
              <span className="ml-auto label">{row.label}</span>
            </div>
            <span className="mt-2 block h-[6px] bg-paper-line dark:bg-ink-800">
              <span
                className={`block h-full ${row.fill}`}
                style={{ width: `${Math.min(row.value, 100)}%`, transition: 'width 600ms cubic-bezier(.2,.8,.2,1)' }}
              />
            </span>
            <p className="mt-2.5 text-[11px] leading-relaxed text-ink-400 dark:text-ink-600">
              {row.note}
            </p>
          </div>
        ))}
      </div>

      <p className="mt-6 border-l-2 border-acid-400 pl-4 text-[11px] leading-relaxed text-ink-500 dark:text-ink-400">
        {gap > 5
          ? `You describe this work well, but in different words than the posting uses — worth borrowing their phrasing where it is honest.`
          : gap < -5
            ? `You share the posting’s vocabulary without describing the same work — worth checking the substance matches.`
            : 'Wording and substance line up closely here.'}
      </p>
    </section>
  )
}
