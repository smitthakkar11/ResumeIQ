/**
 * Required skills the resume doesn't name, but shows related experience for.
 *
 * These earn partial credit rather than counting as a flat gap — the evidence
 * is shown so the user can judge whether it really applies.
 */
export function PartialSkills({ partials }) {
  if (partials.length === 0) {
    return (
      <p className="text-sm text-ink-500 dark:text-ink-400">
        No partial matches — every requirement is either met or missing outright.
      </p>
    )
  }

  return (
    <ul className="space-y-3">
      {partials.map((p) => (
        <li
          key={p.name}
          className="rounded-md border border-warn/25 bg-warn-soft/60 px-3.5 py-3 dark:bg-warn/10"
        >
          <p className="text-[15px] font-semibold text-warn">{p.name}</p>
          <p className="mt-1 text-sm text-ink-600 dark:text-ink-300">
            Not named directly, but your resume shows{' '}
            <span className="font-medium">{p.evidence.join(', ')}</span>
            {p.shared_tags.length > 0 && <> — related {p.shared_tags.join(', ')} work</>}.
          </p>
        </li>
      ))}
    </ul>
  )
}
