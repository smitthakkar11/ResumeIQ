import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { ThemeToggle } from '@/components/ThemeToggle'
import { useAuth } from '@/lib/auth'

const NAV = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/resume/upload', label: 'Resumes' },
  { to: '/analyze', label: 'Analyze' },
  { to: '/history', label: 'History' },
]

export function Layout() {
  const { user, logout, initialising } = useAuth()
  const navigate = useNavigate()

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-20 border-b border-paper-line bg-paper/90 backdrop-blur
                         dark:border-ink-800 dark:bg-ink-950/90">
        <div className="mx-auto flex max-w-6xl items-center gap-8 px-8 py-4">
          <Link to={user ? '/dashboard' : '/'} className="flex shrink-0 items-center gap-2.5">
            <span className="grid size-8 place-items-center rounded-md bg-brand-600 text-[15px] font-bold text-white">
              R
            </span>
            <span className="font-display text-lg font-extrabold tracking-tight">ResumeIQ</span>
          </Link>

          {!initialising && user && (
            <nav className="hidden flex-1 items-center gap-1 md:flex">
              {NAV.map(({ to, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    `rounded-md px-3.5 py-2 text-[15px] font-medium transition-colors ${
                      isActive
                        ? 'bg-brand-50 text-brand-700 dark:bg-brand-500/12 dark:text-brand-300'
                        : 'text-ink-600 hover:bg-paper-line/60 hover:text-ink-950 dark:text-ink-400 dark:hover:bg-ink-800 dark:hover:text-ink-100'
                    }`
                  }
                >
                  {label}
                </NavLink>
              ))}
            </nav>
          )}

          <div className="ml-auto flex items-center gap-2.5">
            {!initialising &&
              (user ? (
                <button
                  type="button"
                  onClick={() => {
                    logout()
                    navigate('/', { replace: true })
                  }}
                  className="shrink-0 rounded-md px-3.5 py-2 text-[15px] font-medium text-ink-600
                             transition-colors hover:text-alert dark:text-ink-400"
                >
                  Log out
                </button>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="rounded-md px-3.5 py-2 text-[15px] font-medium text-ink-600 transition-colors
                               hover:text-ink-950 dark:text-ink-400 dark:hover:text-ink-100"
                  >
                    Sign in
                  </Link>
                  <Link
                    to="/signup"
                    className="rounded-md bg-brand-600 px-4 py-2.5 text-[15px] font-semibold text-white
                               transition-colors hover:bg-brand-700"
                  >
                    Get started
                  </Link>
                </>
              ))}
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-8 py-14">
        <Outlet />
      </main>

      <footer className="mt-auto border-t border-paper-line py-8 dark:border-ink-800">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-8">
          <span className="font-display text-sm font-bold">ResumeIQ</span>
          <span className="text-sm text-ink-400">© {new Date().getFullYear()}</span>
        </div>
      </footer>
    </div>
  )
}
