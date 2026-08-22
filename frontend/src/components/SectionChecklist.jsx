/**
 * Section detection is a heuristic on unstructured text, so the wording stays
 * "not detected" rather than "missing".
 */
export function SectionChecklist({ sections }) {
  return (
    <>
      <ul className="divide-y divide-paper-line dark:divide-ink-800">
        {Object.entries(sections).map(([name, present]) => (
          <li key={name} className="flex items-center justify-between py-2.5">
            <span className={`text-sm ${present ? '' : 'text-ink-400 dark:text-ink-600'}`}>
              {name}
            </span>
            <span
              className={`num text-[10px] uppercase tracking-[0.12em] ${
                present ? 'text-acid-600 dark:text-acid-400' : 'text-ink-400 dark:text-ink-600'
              }`}
            >
              {present ? 'detected' : 'not detected'}
            </span>
          </li>
        ))}
      </ul>
      <p className="mt-4 text-[11px] leading-relaxed text-ink-400 dark:text-ink-600">
        Read from headings in the extracted text. An unusual heading or a
        two-column layout can hide a section that is genuinely there.
      </p>
    </>
  )
}
