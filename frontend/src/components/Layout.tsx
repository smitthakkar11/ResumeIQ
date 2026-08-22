import { Link, Outlet } from 'react-router-dom'
import { ThemeToggle } from '@/components/ThemeToggle'

/**
 * App shell: header + footer wrapped around whatever the current route renders.
 * React Router's <Outlet /> is the slot the matched child route fills.
 */
export function Layout() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/80 backdrop-blur
                         dark:border-slate-800 dark:bg-slate-950/80">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center gap-2.5">
            <span className="grid size-8 place-items-center rounded-lg bg-brand-600 font-bold text-white">
              R
            </span>
            <span className="text-lg font-semibold tracking-tight">
              Resume<span className="text-brand-600 dark:text-brand-400">IQ</span>
            </span>
          </Link>
          <ThemeToggle />
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-12">
        <Outlet />
      </main>

      <footer className="border-t border-slate-200 py-6 dark:border-slate-800">
        <p className="mx-auto max-w-6xl px-6 text-sm text-slate-500 dark:text-slate-500">
          ResumeIQ — resume ↔ job description analysis. Phase 1: foundation.
        </p>
      </footer>
    </div>
  )
}
