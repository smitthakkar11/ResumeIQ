/** Narrow frame for sign-in and sign-up. */
export function AuthShell({ eyebrow, title, subtitle, children, footer }) {
  return (
    <div className="mx-auto max-w-md py-10">
      <span className="inline-flex rounded-full bg-brand-50 px-3.5 py-1.5 text-[13px] font-semibold
                       text-brand-700 dark:bg-brand-500/12 dark:text-brand-300">
        {eyebrow}
      </span>
      <h1 className="mt-5 font-display text-4xl font-extrabold tracking-tight">{title}</h1>
      <p className="mt-2.5 text-base text-ink-500 dark:text-ink-400">{subtitle}</p>
      <div className="mt-9">{children}</div>
      <p className="mt-9 border-t border-paper-line pt-6 text-center text-[15px] text-ink-500
                    dark:border-ink-800 dark:text-ink-400">
        {footer}
      </p>
    </div>
  )
}
