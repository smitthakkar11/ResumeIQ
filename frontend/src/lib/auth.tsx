import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { authApi, setUnauthorizedHandler, tokenStorage, type User } from '@/lib/api'

type AuthContextValue = {
  user: User | null
  /** True only while the initial "am I already logged in?" check is running. */
  initialising: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (name: string, email: string, password: string) => Promise<void>
  loginWithGoogle: (code: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  // Derived at init rather than set in an effect: with no stored token there
  // is nothing to verify, so we are never in an "initialising" state.
  const [initialising, setInitialising] = useState(() => Boolean(tokenStorage.get()))

  const logout = useCallback(() => {
    // Logout is purely client-side: a JWT cannot be revoked server-side, so
    // "logging out" means discarding the token. The token itself stays
    // technically valid until it expires — which is why expiry is short.
    tokenStorage.clear()
    setUser(null)
  }, [])

  // Let a 401 from any request drop the session, without every caller
  // having to handle it.
  useEffect(() => {
    setUnauthorizedHandler(() => setUser(null))
    return () => setUnauthorizedHandler(null)
  }, [])

  // On first load, a token in localStorage is only a *claim* that we are
  // logged in. We ask the server to confirm it before trusting it — the token
  // may be expired, or signed by a key the server has since rotated.
  useEffect(() => {
    if (!tokenStorage.get()) return

    let cancelled = false
    authApi
      .me()
      .then((me) => !cancelled && setUser(me))
      .catch(() => !cancelled && tokenStorage.clear())
      .finally(() => !cancelled && setInitialising(false))

    return () => {
      cancelled = true
    }
  }, [])

  const applySession = (token: string, nextUser: User) => {
    tokenStorage.set(token)
    setUser(nextUser)
  }

  const value: AuthContextValue = {
    user,
    initialising,
    logout,
    login: async (email, password) => {
      const data = await authApi.login(email, password)
      applySession(data.access_token, data.user)
    },
    signup: async (name, email, password) => {
      const data = await authApi.signup(name, email, password)
      applySession(data.access_token, data.user)
    },
    loginWithGoogle: async (code) => {
      const data = await authApi.google(code)
      applySession(data.access_token, data.user)
    },
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
