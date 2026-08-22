import { useEffect, useState } from 'react'
import { GoogleIcon } from '@/components/GoogleIcon'
import { Button } from '@/components/ui'
import { authApi } from '@/lib/api'
import { redirectToGoogle } from '@/lib/google'
const REDIRECT_URI = `${window.location.origin}/login`

/**
 * Renders nothing at all when the server reports Google is unconfigured —
 * better than showing a button that always errors.
 */
export function GoogleButton({ disabled }) {
  const [providers, setProviders] = useState(null)
  useEffect(() => {
    authApi
      .providers()
      .then(setProviders)
      .catch(() => setProviders(null))
  }, [])
  if (!providers?.google || !providers.google_client_id) return null
  return (
    <>
      <div className="flex items-center gap-3 py-1">
        <span className="h-px flex-1 bg-slate-200 dark:bg-slate-800" />
        <span className="text-xs text-slate-400 dark:text-slate-600">or</span>
        <span className="h-px flex-1 bg-slate-200 dark:bg-slate-800" />
      </div>

      <Button
        type="button"
        variant="secondary"
        disabled={disabled}
        onClick={() => redirectToGoogle(providers.google_client_id, REDIRECT_URI)}
      >
        <GoogleIcon />
        Continue with Google
      </Button>
    </>
  )
}
