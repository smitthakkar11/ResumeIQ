export function Field({ label, error, ...props }) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-ink-700 dark:text-ink-300">{label}</span>
      <input
        {...props}
        aria-invalid={Boolean(error)}
        className={`w-full rounded-md border bg-white px-3.5 py-3 text-[15px] outline-none transition
          placeholder:text-ink-400 dark:bg-ink-900 dark:placeholder:text-ink-500
          focus:border-brand-500 focus:ring-4 focus:ring-brand-500/12
          ${error ? 'border-alert' : 'border-paper-line dark:border-ink-700'}`}
      />
      {error && <span className="mt-1.5 block text-[13px] text-alert">{error}</span>}
    </label>
  )
}

export function Button({ loading, variant = 'primary', children, ...props }) {
  const base =
    'inline-flex w-full items-center justify-center gap-2 rounded-md px-5 py-3 text-[15px] font-semibold transition-colors duration-150 disabled:cursor-not-allowed'

  const styles = {
    primary:
      'bg-brand-600 text-white hover:bg-brand-700 disabled:bg-paper-line disabled:text-ink-400 dark:disabled:bg-ink-800 dark:disabled:text-ink-500',
    secondary:
      'border border-paper-line bg-white text-ink-800 hover:border-ink-400 disabled:opacity-40 dark:border-ink-700 dark:bg-ink-900 dark:text-ink-200 dark:hover:border-ink-500',
  }[variant]

  return (
    <button {...props} disabled={props.disabled || loading} className={`${base} ${styles}`}>
      {loading && (
        <span className="size-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
      )}
      {children}
    </button>
  )
}

export function Alert({ children, tone = 'error' }) {
  const styles =
    tone === 'error'
      ? 'border-alert/25 bg-alert-soft text-alert dark:bg-alert/10'
      : 'border-paper-line text-ink-600 dark:border-ink-700 dark:text-ink-300'

  return (
    <div role="alert" className={`rounded-md border px-4 py-3.5 text-sm ${styles}`}>
      {children}
    </div>
  )
}

/** Section heading. A real heading, not a tiny mono tag. */
export function SectionHead({ children, right }) {
  return (
    <div className="mb-5 flex items-baseline justify-between gap-4">
      <h2 className="font-display text-lg font-bold tracking-tight">{children}</h2>
      {right}
    </div>
  )
}
