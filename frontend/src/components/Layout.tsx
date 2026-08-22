import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { ThemeToggle } from '@/components/ThemeToggle'
import { useAuth } from '@/lib/auth'

export function Layout() {
  const { user, logout, initialising } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/', { replace: true })
  }

  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/80 backdrop-blur
                         dark:border-slate-800 dark:bg-slate-950/80">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-4">
          <Link to={user ? '/dashboard' : '/'} className="flex shrink-0 items-center gap-2.5">
            <span className="grid size-8 place-items-center rounded-lg bg-brand-600 font-bold text-white">
              R
            </span>
            <span className="text-lg font-semibold tracking-tight">
              Resume<span className="text-brand-600 dark:text-brand-400">IQ</span>
            </span>
          </Link>

          <div className="flex items-center gap-2">
            {!initialising &&
              (user ? (
                <>
                  <NavLink
                    to="/dashboard"
                    className={({ isActive }) =>
                      `hidden rounded-lg px-3 py-2 text-sm font-medium transition sm:block ${
                        isActive
                          ? 'text-brand-600 dark:text-brand-400'
                          : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100'
                      }`
                    }
                  >
                    Dashboard
                  </NavLink>
                  <NavLink
                    to="/resume/upload"
                    className={({ isActive }) =>
                      `hidden rounded-lg px-3 py-2 text-sm font-medium transition sm:block ${
                        isActive
                          ? 'text-brand-600 dark:text-brand-400'
                          : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100'
                      }`
                    }
                  >
                    Resumes
                  </NavLink>
                  <NavLink
                    to="/analyze"
                    className={({ isActive }) =>
                      `hidden rounded-lg px-3 py-2 text-sm font-medium transition sm:block ${
                        isActive
                          ? 'text-brand-600 dark:text-brand-400'
                          : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100'
                      }`
                    }
                  >
                    Analyze
                  </NavLink>
                  <span className="hidden max-w-[14rem] truncate text-sm text-slate-500 md:block dark:text-slate-500">
                    {user.email}
                  </span>
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 transition
                               hover:bg-slate-100 hover:text-slate-900
                               dark:border-slate-800 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100"
                  >
                    Log out
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition
                               hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
                  >
                    Sign in
                  </Link>
                  <Link
                    to="/signup"
                    className="rounded-lg bg-brand-600 px-3.5 py-2 text-sm font-medium text-white transition hover:bg-brand-700"
                  >
                    Get started
                  </Link>
                </>
              ))}
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-12">
        <Outlet />
      </main>

      <footer className="border-t border-slate-200 py-6 dark:border-slate-800">
        <p className="mx-auto max-w-6xl px-6 text-sm text-slate-500 dark:text-slate-500">
          ResumeIQ — resume ↔ job description analysis. Phase 5: matching engine.
        </p>
      </footer>
    </div>
  )
}
