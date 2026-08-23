import { Link } from 'react-router-dom'

export function NotFound() {
  return (
    <div className="py-28 text-center">
      <p className="num text-5xl font-medium text-ink-300 dark:text-ink-700">404</p>
      <h1 className="mt-5 font-display text-2xl font-bold tracking-tight">Page not found</h1>
      <p className="mt-2 text-sm text-ink-500 dark:text-ink-400">That route doesn&apos;t exist.</p>
      <Link
        to="/"
        className="rounded-md bg-brand-600 px-6 py-3 text-[15px] font-semibold text-white transition-colors hover:bg-brand-700"
      >
        Back to home
      </Link>
    </div>
  )
}
