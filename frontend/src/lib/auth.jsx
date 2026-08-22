import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { authApi, setUnauthorizedHandler, tokenStorage } from '@/lib/api'
const AuthContext = createContext(null)
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
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
  const applySession = (token, nextUser) => {
    tokenStorage.set(token)
    setUser(nextUser)
  }
  const value = {
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
export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
