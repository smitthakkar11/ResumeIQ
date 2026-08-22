import { createBrowserRouter } from 'react-router-dom'
import { Layout } from '@/components/Layout'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { Analyze } from '@/pages/Analyze'
import { Dashboard } from '@/pages/Dashboard'
import { Landing } from '@/pages/Landing'
import { Login } from '@/pages/Login'
import { NotFound } from '@/pages/NotFound'
import { ResumeUpload } from '@/pages/ResumeUpload'
import { Signup } from '@/pages/Signup'

/**
 * Route table.
 *
 * Everything under the <ProtectedRoute> element requires a session. Nesting
 * them means a new protected page is added by putting it in that array — there
 * is no separate list of "which paths need auth" to keep in sync.
 *
 * Phases 3-7 add: /resume/upload, /analyze, /results/:id, /history, /profile.
 */
export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Landing /> },
      { path: 'login', element: <Login /> },
      { path: 'signup', element: <Signup /> },
      {
        element: <ProtectedRoute />,
        children: [
          { path: 'dashboard', element: <Dashboard /> },
          { path: 'resume/upload', element: <ResumeUpload /> },
          { path: 'analyze', element: <Analyze /> },
        ],
      },
      { path: '*', element: <NotFound /> },
    ],
  },
])
