import { Link } from 'react-router-dom'
import { useAuth } from '@/lib/auth'

/**
 * Placeholder dashboard. Phase 3 fills this with resume upload; Phase 7 adds
 * the analysis history. For now it proves the protected route and the
 * authenticated /auth/me call work.
 */
export function Dashboard() {
  const { user } = useAuth()
  if (!user) return null

  const NEXT = [
    { phase: 'Phase 4', title: 'Skill extraction', note: 'dictionary + normalisation' },
    { phase: 'Phase 5', title: 'Match engine', note: 'TF-IDF, cosine similarity, scoring' },
  ]

  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          Hello, {user.name.split(' ')[0]}
        </h1>
        <p className="mt-1.5 text-slate-600 dark:text-slate-400">
          You&apos;re signed in as {user.email}.
        </p>
      </div>

      <Link
        to="/resume/upload"
        className="surface flex max-w-md items-center justify-between gap-4 p-5 transition hover:border-brand-400 dark:hover:border-brand-500/50"
      >
        <span>
          <span className="block font-medium">Upload a resume</span>
          <span className="block text-sm text-slate-500 dark:text-slate-400">
            PDF text extraction with PyMuPDF
          </span>
        </span>
        <span aria-hidden className="text-brand-600 dark:text-brand-400">&rarr;</span>
      </Link>

      <section className="surface max-w-md p-5">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Account
        </h2>
        <dl className="mt-4 space-y-2.5 text-sm">
          {[
            ['Name', user.name],
            ['Email', user.email],
            ['Sign-in method', user.has_password ? 'Email and password' : 'Google'],
            ['Member since', new Date(user.created_at).toLocaleDateString()],
          ].map(([label, value]) => (
            <div key={label} className="flex justify-between gap-4">
              <dt className="text-slate-500 dark:text-slate-400">{label}</dt>
              <dd className="font-medium">{value}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section>
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
          Coming next
        </h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          {NEXT.map(({ phase, title, note }) => (
            <div key={phase} className="surface p-4 opacity-70">
              <span className="font-mono text-xs text-brand-600 dark:text-brand-400">{phase}</span>
              <p className="mt-1.5 font-medium">{title}</p>
              <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{note}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
