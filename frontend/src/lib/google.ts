/**
 * Google OAuth 2.0 — the browser's half of the authorization code flow.
 *
 * We build the authorization URL and redirect. Google authenticates the user
 * (we never see their Google password), then sends them back to
 * GOOGLE_REDIRECT_URI carrying a one-time `code`. Our backend redeems that
 * code using GOOGLE_CLIENT_SECRET, which never exists in this bundle.
 */

const GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
const STATE_KEY = 'resumeiq-oauth-state'

/**
 * The `state` parameter is CSRF protection for OAuth.
 *
 * Without it, an attacker could send you a link containing THEIR authorization
 * code; your browser would post it to our backend and silently link your
 * session to the attacker's Google account. Binding a random value to this
 * browser tab and checking it on return makes that forgery detectable.
 */
function createState(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(16))
  const state = Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('')
  sessionStorage.setItem(STATE_KEY, state)
  return state
}

export function consumeState(): string | null {
  const state = sessionStorage.getItem(STATE_KEY)
  sessionStorage.removeItem(STATE_KEY) // one-time use
  return state
}

export function redirectToGoogle(clientId: string, redirectUri: string): void {
  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: redirectUri,
    response_type: 'code', // the authorization CODE flow, not the implicit flow
    scope: 'openid email profile', // the minimum we need to identify the user
    state: createState(),
    prompt: 'select_account',
  })
  window.location.href = `${GOOGLE_AUTH_URL}?${params.toString()}`
}
