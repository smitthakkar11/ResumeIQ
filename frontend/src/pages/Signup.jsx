import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { GoogleButton } from '@/components/GoogleButton'
import { AuthShell } from '@/components/AuthShell'
import { Alert, Button, Field } from '@/components/ui'
import { errorMessage } from '@/lib/api'
import { useAuth } from '@/lib/auth'

/** Mirrors the backend's SignupRequest rules so users see errors before a round trip. */
const MIN_PASSWORD_LENGTH = 8
export function Signup() {
  const { signup, user } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  useEffect(() => {
    if (user)
      navigate('/dashboard', {
        replace: true,
      })
  }, [user, navigate])
  const passwordError =
    password.length > 0 && password.length < MIN_PASSWORD_LENGTH
      ? `At least ${MIN_PASSWORD_LENGTH} characters`
      : undefined
  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setLoading(true)
    try {
      await signup(name, email, password)
      navigate('/dashboard', {
        replace: true,
      })
    } catch (err) {
      setError(errorMessage(err, 'Could not create your account'))
    } finally {
      setLoading(false)
    }
  }
  return (
    <AuthShell
      eyebrow="Create account"
      title="Get started"
      subtitle="Free, and your analyses stay private to you."
      footer={
        <>
          Already registered?{' '}
          <Link to="/login" className="font-medium text-brand-600 hover:underline dark:text-brand-400">
            Sign in
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <Alert>{error}</Alert>}

        <Field
          label="Name"
          autoComplete="name"
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Smit Thakkar"
        />
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
          autoComplete="new-password"
          required
          minLength={MIN_PASSWORD_LENGTH}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          error={passwordError}
          placeholder="At least 8 characters"
        />

        <Button type="submit" loading={loading} disabled={Boolean(passwordError)}>
          Create account
        </Button>

        <GoogleButton disabled={loading} />
      </form>
    </AuthShell>
  )
}
