import { useEffect, useRef, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { GoogleButton } from '@/components/GoogleButton'
import { AuthShell } from '@/components/AuthShell'
import { Alert, Button, Field } from '@/components/ui'
import { errorMessage } from '@/lib/api'
import { useAuth } from '@/lib/auth'
import { consumeState } from '@/lib/google'
export function Login() {
  const { login, loginWithGoogle, user } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const redirectTo = location.state?.from ?? '/dashboard'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  // Already signed in? Don't show the form.
  useEffect(() => {
    if (user)
      navigate(redirectTo, {
        replace: true,
      })
  }, [user, navigate, redirectTo])

  // --- Google redirect handling -------------------------------------------
  // Google sends the user back here as /login?code=...&state=...
  const handledCode = useRef(false)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const code = params.get('code')
    const returnedState = params.get('state')
    const googleError = params.get('error')
    if (googleError) {
      setError(googleError === 'access_denied' ? 'Google sign-in was cancelled' : googleError)
      window.history.replaceState({}, '', '/login')
      return
    }
    if (!code || handledCode.current) return
    handledCode.current = true // React StrictMode mounts twice in dev; a code is one-time-use

    const expectedState = consumeState()
    // Strip the code from the URL immediately so it never lands in history,
    // a screenshot, or a Referer header.
    window.history.replaceState({}, '', '/login')
    if (!expectedState || expectedState !== returnedState) {
      setError('Google sign-in failed a security check. Please try again.')
      return
    }
    setLoading(true)
    loginWithGoogle(code)
      .then(() =>
        navigate('/dashboard', {
          replace: true,
        }),
      )
      .catch((err) => setError(errorMessage(err, 'Google sign-in failed')))
      .finally(() => setLoading(false))
  }, [loginWithGoogle, navigate])
  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate(redirectTo, {
        replace: true,
      })
    } catch (err) {
      setError(errorMessage(err, 'Could not sign in'))
    } finally {
      setLoading(false)
    }
  }
  return (
    <AuthShell
      eyebrow="Sign in"
      title="Welcome back"
      subtitle="Analyse a resume against a job description."
      footer={
        <>
          No account?{' '}
          <Link to="/signup" className="font-medium text-acid-600 hover:underline dark:text-acid-400">
            Create one
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <Alert>{error}</Alert>}

        <Field
          label="Email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
        />
        <Field
          label="Password"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="••••••••"
        />

        <Button type="submit" loading={loading}>
          Sign in
        </Button>

        <GoogleButton disabled={loading} />
      </form>
    </AuthShell>
  )
}
