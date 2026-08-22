import axios, { AxiosError } from 'axios'

/**
 * One shared Axios instance for the whole app.
 *
 * Centralising it means the JWT is attached in exactly one place (the request
 * interceptor below) rather than in every component that makes a request.
 */
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8001/api',
  timeout: 15_000,
  headers: { 'Content-Type': 'application/json' },
})

// ---------------------------------------------------------------------------
// Token storage
//
// We keep the access token in localStorage and send it as a Bearer header.
// The honest tradeoff:
//   localStorage  — readable by any JavaScript on the page, so a single XSS
//                   bug leaks the token. Immune to CSRF (nothing is sent
//                   automatically by the browser).
//   httpOnly cookie — unreadable by JavaScript, so XSS cannot steal it, but
//                   the browser attaches it to every request, which is exactly
//                   what CSRF exploits, so it needs SameSite + CSRF tokens.
// Neither is strictly "correct"; they move the risk. We use localStorage for
// its simplicity with a cross-origin SPA, and rely on short token expiry.
// ---------------------------------------------------------------------------

const TOKEN_KEY = 'resumeiq-token'

export const tokenStorage = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token: string) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
}

api.interceptors.request.use((config) => {
  const token = tokenStorage.get()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

/** Set by AuthProvider so a 401 anywhere can drop the session exactly once. */
let onUnauthorized: (() => void) | null = null
export const setUnauthorizedHandler = (handler: (() => void) | null) => {
  onUnauthorized = handler
}

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // A 401 means the token is missing, expired or invalid. Anything else
    // (403, 404, 500) is a real error the caller should handle itself.
    if (error.response?.status === 401) {
      tokenStorage.clear()
      onUnauthorized?.()
    }
    return Promise.reject(error)
  },
)

/** Turns an Axios failure into a message safe to show a user. */
export function errorMessage(error: unknown, fallback = 'Something went wrong'): string {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    // FastAPI validation errors arrive as a list of {loc, msg, type}.
    if (Array.isArray(detail) && detail[0]?.msg) return String(detail[0].msg)
    if (error.code === 'ECONNABORTED') return 'The server took too long to respond'
    if (!error.response) return 'Cannot reach the server. Is the backend running?'
  }
  return fallback
}

// ---------------------------------------------------------------------------
// Types mirroring the backend's Pydantic schemas
// ---------------------------------------------------------------------------

export type User = {
  id: number
  name: string
  email: string
  is_active: boolean
  has_password: boolean
  created_at: string
}

export type TokenResponse = {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export type Providers = {
  password: boolean
  google: boolean
  google_client_id: string | null
}

export type HealthResponse = { status: string; app: string; environment: string }
export type DatabaseHealthResponse = { status: string; database: string; detail: string | null }

// ---------------------------------------------------------------------------
// Endpoints
// ---------------------------------------------------------------------------

export const authApi = {
  signup: (name: string, email: string, password: string) =>
    api.post<TokenResponse>('/auth/signup', { name, email, password }).then((r) => r.data),

  login: (email: string, password: string) =>
    api.post<TokenResponse>('/auth/login', { email, password }).then((r) => r.data),

  google: (code: string) =>
    api.post<TokenResponse>('/auth/google', { code }).then((r) => r.data),

  me: () => api.get<User>('/auth/me').then((r) => r.data),

  providers: () => api.get<Providers>('/auth/providers').then((r) => r.data),
}

export type ResumeSummary = {
  id: number
  filename: string
  page_count: number
  created_at: string
}

export type ResumeDetail = ResumeSummary & { extracted_text: string }

export type ExtractedSkill = { name: string; category: string }
export type ResumeSkills = {
  resume_id: number
  filename: string
  skills: ExtractedSkill[]
  total: number
}

export const resumeApi = {
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    // Let the browser set Content-Type — it must include the multipart boundary.
    return api
      .post<ResumeDetail>('/resumes/upload', form, { headers: { 'Content-Type': undefined } })
      .then((r) => r.data)
  },
  list: () => api.get<ResumeSummary[]>('/resumes').then((r) => r.data),
  get: (id: number) => api.get<ResumeDetail>(`/resumes/${id}`).then((r) => r.data),
  skills: (id: number) => api.get<ResumeSkills>(`/resumes/${id}/skills`).then((r) => r.data),
  remove: (id: number) => api.delete(`/resumes/${id}`).then(() => undefined),
}

export type AnalysisResponse = {
  resume_id: number
  resume_filename: string
  job_title: string
  overall_score: number
  text_similarity: number
  skill_match: number | null
  keyword_match: number
  weights: Record<string, number>
  matched_skills: ExtractedSkill[]
  missing_skills: ExtractedSkill[]
  extra_skills: ExtractedSkill[]
  keywords: { term: string; found: boolean }[]
  sections: Record<string, boolean>
  recommendations: { category: string; message: string }[]
}

export const analysisApi = {
  create: (resumeId: number, jobTitle: string, jobDescription: string) =>
    api
      .post<AnalysisResponse>('/analyses', {
        resume_id: resumeId,
        job_title: jobTitle,
        job_description: jobDescription,
      })
      .then((r) => r.data),
}

export const fetchHealth = () => api.get<HealthResponse>('/health').then((r) => r.data)
export const fetchDatabaseHealth = () =>
  api.get<DatabaseHealthResponse>('/health/db').then((r) => r.data)
