import { Link } from 'react-router-dom'
export function NotFound() {
  return (
    <div className="py-20 text-center">
      <p className="font-mono text-sm text-brand-600 dark:text-brand-400">404</p>
      <h1 className="mt-3 text-3xl font-bold tracking-tight">Page not found</h1>
      <p className="mt-2 text-slate-600 dark:text-slate-400">That route doesn&apos;t exist yet.</p>
      <Link
        to="/"
        className="mt-6 inline-block rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700"
      >
        Back to home
      </Link>
    </div>
  )
}
