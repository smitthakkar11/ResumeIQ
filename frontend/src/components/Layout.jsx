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
    <div className="relative z-10 flex min-h-screen flex-col">
      <header className="sticky top-0 z-20 border-b border-paper-line bg-paper/85 backdrop-blur-md
                         dark:border-ink-800 dark:bg-ink-950/85">
        <div className="mx-auto flex max-w-6xl items-center gap-6 px-6 py-3.5">
          <Link to={user ? '/dashboard' : '/'} className="group flex shrink-0 items-center gap-2.5">
            {/* Mark: ascending bars — a readout, not a rounded letter tile.
                Vertical so it cannot be mistaken for a hamburger menu. */}
            <span className="flex h-5 w-5 items-end gap-[2px]">
              <span className="w-[3px] bg-ink-950 transition-all duration-300 group-hover:h-full dark:bg-ink-100" style={{ height: '40%' }} />
              <span className="w-[3px] bg-ink-950 transition-all duration-300 group-hover:h-2/5 dark:bg-ink-100" style={{ height: '70%' }} />
              <span className="w-[3px] bg-acid-400 transition-all duration-300 group-hover:h-3/5" style={{ height: '100%' }} />
            </span>
            <span className="font-display text-[15px] font-bold tracking-tight">
              Resume<span className="text-acid-600 dark:text-acid-400">IQ</span>
            </span>
          </Link>

          {!initialising && user && (
            <nav className="hidden flex-1 items-center gap-1 md:flex">
              {NAV.map(({ to, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    `relative px-3 py-2 font-mono text-[11px] uppercase tracking-[0.1em] transition-colors ${
                      isActive
                        ? 'text-ink-950 dark:text-ink-100'
                        : 'text-ink-400 hover:text-ink-950 dark:text-ink-500 dark:hover:text-ink-100'
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      {label}
                      {isActive && (
                        <span className="absolute inset-x-3 -bottom-[15px] h-px bg-acid-400" />
                      )}
                    </>
                  )}
                </NavLink>
              ))}
            </nav>
          )}

          <div className="ml-auto flex items-center gap-2">
            {!initialising &&
              (user ? (
                <button
                  type="button"
                  onClick={() => {
                    logout()
                    navigate('/', { replace: true })
                  }}
                  className="shrink-0 whitespace-nowrap px-3 py-2 font-mono text-[11px] uppercase tracking-[0.1em]
                             text-ink-400 transition-colors hover:text-alert dark:text-ink-500"
                >
                  Log out
                </button>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="px-3 py-2 font-mono text-[11px] uppercase tracking-[0.1em] text-ink-500 transition-colors
                               hover:text-ink-950 dark:text-ink-400 dark:hover:text-ink-100"
                  >
                    Sign in
                  </Link>
                  <Link
                    to="/signup"
                    className="rounded-xs bg-acid-400 px-3.5 py-2 font-mono text-[11px] font-medium uppercase
                               tracking-[0.1em] text-ink-950 transition-colors hover:bg-acid-300"
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

      <footer className="border-t border-paper-line py-5 dark:border-ink-800">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-6">
          <span className="label">ResumeIQ</span>
          <span className="label">© {new Date().getFullYear()}</span>
        </div>
      </footer>
    </div>
  )
}
