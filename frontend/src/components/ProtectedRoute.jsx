import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { Spinner } from '@/components/Spinner'
import { useAuth } from '@/lib/auth'

/**
 * Gate for authenticated routes.
 *
 * This is a UX guard, not a security boundary. Anyone can edit the JavaScript
 * in their browser and render whatever component they like — which is exactly
 * why every protected API endpoint enforces auth server-side as well. The
 * frontend check just avoids showing a broken page to a logged-out visitor.
 */
export function ProtectedRoute() {
  const { user, initialising } = useAuth()
  const location = useLocation()

  // Without this, a page refresh would bounce a logged-in user to /login
  // during the split second before GET /auth/me returns.
  if (initialising) {
    return <Spinner />
  }
  if (!user) {
    // `state.from` lets the login page send them back where they were headed.
    return (
      <Navigate
        to="/login"
        replace
        state={{
          from: location.pathname,
        }}
      />
    )
  }
  return <Outlet />
}
