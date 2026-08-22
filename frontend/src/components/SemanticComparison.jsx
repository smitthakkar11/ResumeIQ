/**
 * TF-IDF similarity next to sentence-embedding similarity.
 *
 * Shown for comparison only. The embedding score is deliberately not part of
 * the overall match: it cannot be traced back to specific words, and folding
 * it in would make the score unexplainable.
 */
export function SemanticComparison({ result }) {
  const rows = [
    {
      label: 'TF-IDF (word overlap)',
      value: result.text_similarity,
      note: 'Counts shared words. Cannot see that "ML" and "machine learning" mean the same thing.',
      bar: 'bg-brand-500',
    },
    {
      label: 'Embeddings (meaning)',
      value: result.semantic_similarity,
      note: 'A local neural model compares meaning, so paraphrases still match. Not traceable to specific words.',
      bar: 'bg-teal-500',
    },
  ]

  const gap = Math.round((result.semantic_similarity - result.text_similarity) * 10) / 10

  return (
    <section className="surface p-5">
      <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
        Two ways of measuring similarity
      </h3>

      <div className="mt-4 space-y-4">
        {rows.map((row) => (
          <div key={row.label}>
            <div className="flex items-baseline justify-between gap-4">
              <span className="text-sm font-medium">{row.label}</span>
              <span className="text-sm font-semibold tabular-nums">{row.value}%</span>
            </div>
            <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
              <div
                className={`h-full rounded-full ${row.bar}`}
                style={{ width: `${Math.min(row.value, 100)}%` }}
              />
            </div>
            <p className="mt-1.5 text-xs text-slate-500 dark:text-slate-500">{row.note}</p>
          </div>
        ))}
      </div>

      <p className="mt-4 border-t border-slate-100 pt-3 text-xs text-slate-500 dark:border-slate-800 dark:text-slate-500">
        {gap > 5
          ? `The embedding model rates this ${gap} points higher — it is recognising wording that means the same thing but shares no words.`
          : gap < -5
            ? `TF-IDF rates this ${Math.abs(gap)} points higher — the two documents share vocabulary without describing the same work.`
            : 'Both methods agree closely on this pair.'}{' '}
        Only the TF-IDF score counts toward the overall match, so every point
        remains traceable to specific words. The model runs locally; nothing is
        sent anywhere.
      </p>
    </section>
  )
}
