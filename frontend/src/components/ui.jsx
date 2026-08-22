/** Small shared primitives so form styling lives in one place. */

export function Field({ label, error, ...props }) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
        {label}
      </span>
      <input
        {...props}
        aria-invalid={Boolean(error)}
        className={`w-full rounded-lg border px-3 py-2 text-sm outline-none transition
          placeholder:text-slate-400
          focus:ring-2 focus:ring-brand-500/30
          dark:bg-slate-900 dark:placeholder:text-slate-600
          ${error ? 'border-rose-400 focus:border-rose-500 dark:border-rose-500/60' : 'border-slate-300 focus:border-brand-500 dark:border-slate-700'}`}
      />
      {error && (
        <span className="mt-1 block text-xs text-rose-600 dark:text-rose-400">{error}</span>
      )}
    </label>
  )
}
export function Button({ loading, variant = 'primary', children, ...props }) {
  const base =
    'inline-flex w-full items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-60'
  const styles = {
    primary: 'bg-brand-600 text-white hover:bg-brand-700',
    secondary:
      'border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800',
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
      ? 'border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-300'
      : 'border-slate-200 bg-slate-50 text-slate-600 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400'
  return (
    <div role="alert" className={`rounded-lg border px-3.5 py-2.5 text-sm ${styles}`}>
      {children}
    </div>
  )
}
