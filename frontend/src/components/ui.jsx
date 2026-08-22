/** Shared form primitives. Square, hairline, one accent. */

export function Field({ label, error, ...props }) {
  return (
    <label className="block">
      <span className="label mb-2 block text-ink-600 dark:text-ink-400">{label}</span>
      <input
        {...props}
        aria-invalid={Boolean(error)}
        className={`w-full rounded-xs border bg-transparent px-3 py-2.5 text-sm outline-none transition
          placeholder:text-ink-400 dark:placeholder:text-ink-600
          focus:border-acid-500 focus:ring-0
          ${error ? 'border-alert' : 'border-paper-line dark:border-ink-700'}`}
      />
      {error && <span className="num mt-1.5 block text-[11px] text-alert">{error}</span>}
    </label>
  )
}

export function Button({ loading, variant = 'primary', children, ...props }) {
  const base =
    'inline-flex w-full items-center justify-center gap-2 rounded-xs px-4 py-2.5 text-sm font-medium transition-colors duration-150 disabled:cursor-not-allowed'

  const styles = {
    // Acid on near-black is the one loud thing in the whole interface.
    // Disabled goes neutral rather than faded acid: pale acid on paper is
    // close to unreadable.
    primary:
      'bg-acid-400 text-ink-950 hover:bg-acid-300 disabled:bg-paper-line disabled:text-ink-400 dark:disabled:bg-ink-800 dark:disabled:text-ink-600',
    secondary:
      'border border-paper-line text-ink-700 hover:border-ink-950 hover:text-ink-950 disabled:opacity-40 dark:border-ink-700 dark:text-ink-300 dark:hover:border-ink-300 dark:hover:text-ink-100',
    ghost:
      'text-ink-500 hover:text-ink-950 dark:text-ink-400 dark:hover:text-ink-100',
  }[variant]

  return (
    <button {...props} disabled={props.disabled || loading} className={`${base} ${styles}`}>
      {loading && (
        <span className="size-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" />
      )}
      {children}
    </button>
  )
}

export function Alert({ children, tone = 'error' }) {
  const styles =
    tone === 'error'
      ? 'border-alert/40 bg-alert/8 text-alert'
      : 'border-paper-line text-ink-500 dark:border-ink-700 dark:text-ink-400'

  return (
    <div role="alert" className={`rounded-xs border-l-2 px-4 py-3 text-sm ${styles}`}>
      {children}
    </div>
  )
}

/** A labelled section heading sitting on a hairline rule. */
export function SectionHead({ children, right }) {
  return (
    <div className="rule mb-5 flex items-baseline justify-between gap-4 pt-4">
      <h2 className="label">{children}</h2>
      {right}
    </div>
  )
}
