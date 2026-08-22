/**
 * Section detection is a heuristic on unstructured text, so the wording is
 * deliberately "not detected" rather than "missing".
 */
export function SectionChecklist({ sections }) {
  return (
    <>
      <ul className="grid gap-x-6 gap-y-2 sm:grid-cols-2">
        {Object.entries(sections).map(([name, present]) => (
          <li key={name} className="flex items-center gap-2.5 text-sm">
            <span
              aria-hidden
              className={`grid size-4 shrink-0 place-items-center rounded-full text-[10px] font-bold ${present ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400' : 'bg-slate-100 text-slate-400 dark:bg-slate-800 dark:text-slate-500'}`}
            >
              {present ? '✓' : '–'}
            </span>
            <span className={present ? '' : 'text-slate-500 dark:text-slate-500'}>{name}</span>
            <span className="sr-only">{present ? 'detected' : 'not detected'}</span>
          </li>
        ))}
      </ul>
      <p className="mt-4 text-xs text-slate-500 dark:text-slate-500">
        Detected from headings in the extracted text. An unusual heading or a two-column layout can
        hide a section that is genuinely there.
      </p>
    </>
  )
}
