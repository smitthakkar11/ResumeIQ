/** Narrow, quiet frame for sign-in and sign-up. */
export function AuthShell({ eyebrow, title, subtitle, children, footer }) {
  return (
    <div className="mx-auto max-w-sm py-10">
      <span className="label inline-flex items-center gap-2">
        <span className="size-1.5 bg-acid-400" />
        {eyebrow}
      </span>
      <h1 className="mt-5 font-display text-3xl font-bold tracking-tight">{title}</h1>
      <p className="mt-2 text-sm text-ink-500 dark:text-ink-400">{subtitle}</p>
      <div className="mt-8">{children}</div>
      <p className="mt-8 border-t border-paper-line pt-5 text-center text-sm text-ink-500 dark:border-ink-800 dark:text-ink-400">
        {footer}
      </p>
    </div>
  )
}
