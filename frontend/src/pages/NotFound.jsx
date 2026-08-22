import { Link } from 'react-router-dom'

export function NotFound() {
  return (
    <div className="py-28 text-center">
      <p className="num text-5xl font-medium text-ink-300 dark:text-ink-700">404</p>
      <h1 className="mt-5 font-display text-2xl font-bold tracking-tight">Page not found</h1>
      <p className="mt-2 text-sm text-ink-500 dark:text-ink-400">That route doesn&apos;t exist.</p>
      <Link
        to="/"
        className="mt-8 inline-block rounded-xs bg-acid-400 px-5 py-2.5 font-mono text-[11px] font-medium
                   uppercase tracking-[0.12em] text-ink-950 transition-colors hover:bg-acid-300"
      >
        Back to home
      </Link>
    </div>
  )
}
