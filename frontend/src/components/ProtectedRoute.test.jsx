import { describe, expect, it, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { AuthProvider } from '@/lib/auth'
import { authApi, tokenStorage } from '@/lib/api'

vi.mock('@/lib/api', async () => {
  const actual = await vi.importActual('@/lib/api')
  return { ...actual, authApi: { ...actual.authApi, me: vi.fn() } }
})

function renderAt(path = '/dashboard') {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AuthProvider>
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<p>Secret dashboard</p>} />
          </Route>
          <Route path="/login" element={<p>Login page</p>} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  )
}

describe('ProtectedRoute', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('redirects to login when there is no token', async () => {
    renderAt()
    expect(await screen.findByText('Login page')).toBeInTheDocument()
    expect(screen.queryByText('Secret dashboard')).not.toBeInTheDocument()
  })

  it('renders the page once the server confirms the session', async () => {
    tokenStorage.set('a.valid.token')
    authApi.me.mockResolvedValue({ id: 1, name: 'Smit', email: 's@example.com' })

    renderAt()
    expect(await screen.findByText('Secret dashboard')).toBeInTheDocument()
  })

  it('does not flash the login page while the session is being verified', () => {
    tokenStorage.set('a.valid.token')
    authApi.me.mockReturnValue(new Promise(() => {})) // never resolves

    renderAt()
    // This is the bug the `initialising` state exists to prevent.
    expect(screen.queryByText('Login page')).not.toBeInTheDocument()
    expect(screen.queryByText('Secret dashboard')).not.toBeInTheDocument()
  })

  it('discards a token the server rejects', async () => {
    tokenStorage.set('an.expired.token')
    authApi.me.mockRejectedValue(new Error('401'))

    renderAt()
    expect(await screen.findByText('Login page')).toBeInTheDocument()
    await waitFor(() => expect(tokenStorage.get()).toBeNull())
  })
})
