/**
 * Section detection is a heuristic on unstructured text, so the wording stays
 * "not detected" rather than "missing".
 */
export function SectionChecklist({ sections }) {
  return (
    <>
      <ul className="grid gap-2.5 sm:grid-cols-2">
        {Object.entries(sections).map(([name, present]) => (
          <li key={name} className="flex items-center gap-2.5">
            <span
              className={`grid size-5 shrink-0 place-items-center rounded-full text-[11px] font-bold ${
                present
                  ? 'bg-brand-50 text-brand-600 dark:bg-brand-500/15 dark:text-brand-400'
                  : 'bg-paper-line text-ink-400 dark:bg-ink-800 dark:text-ink-500'
              }`}
            >
              {present ? '✓' : '–'}
            </span>
            <span className={`text-sm ${present ? '' : 'text-ink-400 dark:text-ink-500'}`}>
              {name}
            </span>
            <span className="sr-only">{present ? 'detected' : 'not detected'}</span>
          </li>
        ))}
      </ul>
      <p className="mt-5 text-[13px] leading-relaxed text-ink-500 dark:text-ink-400">
        Read from headings in the extracted text. An unusual heading or a
        two-column layout can hide a section that is genuinely there.
      </p>
    </>
  )
}
