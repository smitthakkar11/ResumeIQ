import { createBrowserRouter } from 'react-router-dom'
import { Layout } from '@/components/Layout'
import { Landing } from '@/pages/Landing'
import { NotFound } from '@/pages/NotFound'

/**
 * Route table. Phase 2 adds /login and /signup; Phase 3+ adds the protected
 * routes (/dashboard, /resume/*, /analyze, /results/:id, /history) as children
 * of a <ProtectedRoute> wrapper.
 */
export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Landing /> },
      { path: '*', element: <NotFound /> },
    ],
  },
])
