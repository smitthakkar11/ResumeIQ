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
  headers: {
    'Content-Type': 'application/json',
  },
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
  set: (token) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
}

api.interceptors.request.use((config) => {
  const token = tokenStorage.get()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

/** Set by AuthProvider so a 401 anywhere can drop the session exactly once. */
let onUnauthorized = null

export const setUnauthorizedHandler = (handler) => {
  onUnauthorized = handler
}

api.interceptors.response.use(
  (response) => response,
  (error) => {
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
export function errorMessage(error, fallback = 'Something went wrong') {
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
// Shapes returned by the backend, mirroring its Pydantic schemas.
// JSDoc rather than TypeScript: no build step, but editors still autocomplete
// these and it documents the contract for anyone reading the file.
// ---------------------------------------------------------------------------

/**
 * @typedef {Object} User
 * @property {number} id
 * @property {string} name
 * @property {string} email
 * @property {boolean} is_active
 * @property {boolean} has_password  false for Google-only accounts
 * @property {string}  created_at
 */

/**
 * @typedef {Object} ResumeSummary
 * @property {number} id
 * @property {string} filename
 * @property {number} page_count
 * @property {number} version      per-user: v1, v2, v3...
 * @property {string} created_at
 */

/**
 * @typedef {Object} ExtractedSkill
 * @property {string} name      canonical name, e.g. "Node.js"
 * @property {string} category  e.g. "Backend"
 */

/**
 * @typedef {Object} Analysis
 * @property {number}  id
 * @property {string}  job_title
 * @property {string}  resume_filename
 * @property {number}  match_score       0-100
 * @property {number}  text_similarity   0-100
 * @property {number|null} skill_match    null when the job names no known skills
 * @property {number}  keyword_match     0-100
 * @property {Object.<string, number>}  weights
 * @property {ExtractedSkill[]} matched_skills
 * @property {ExtractedSkill[]} missing_skills
 * @property {ExtractedSkill[]} extra_skills
 * @property {{term: string, found: boolean}[]} keywords
 * @property {Object.<string, boolean>} sections
 * @property {{category: string, message: string}[]} recommendations
 * @property {number|null} resume_id
 * @property {number|null} job_description_id
 * @property {string}  created_at
 */

// ---------------------------------------------------------------------------
// Endpoints
// ---------------------------------------------------------------------------

export const authApi = {
  signup: (name, email, password) =>
    api
      .post('/auth/signup', {
        name,
        email,
        password,
      })
      .then((r) => r.data),
  login: (email, password) =>
    api
      .post('/auth/login', {
        email,
        password,
      })
      .then((r) => r.data),
  google: (code) =>
    api
      .post('/auth/google', {
        code,
      })
      .then((r) => r.data),
  me: () => api.get('/auth/me').then((r) => r.data),
  providers: () => api.get('/auth/providers').then((r) => r.data),
}

export const resumeApi = {
  upload: (file) => {
    const form = new FormData()
    form.append('file', file)
    // Let the browser set Content-Type — it must include the multipart boundary.
    return api
      .post('/resumes/upload', form, {
        headers: {
          'Content-Type': undefined,
        },
      })
      .then((r) => r.data)
  },
  list: () => api.get('/resumes').then((r) => r.data),
  get: (id) => api.get(`/resumes/${id}`).then((r) => r.data),
  skills: (id) => api.get(`/resumes/${id}/skills`).then((r) => r.data),
  remove: (id) => api.delete(`/resumes/${id}`).then(() => undefined),
}

export const analysisApi = {
  create: (resumeId, jobTitle, jobDescription) =>
    api
      .post('/analyses', {
        resume_id: resumeId,
        job_title: jobTitle,
        job_description: jobDescription,
      })
      .then((r) => r.data),
  list: () => api.get('/analyses').then((r) => r.data),
  get: (id) => api.get(`/analyses/${id}`).then((r) => r.data),
  remove: (id) => api.delete(`/analyses/${id}`).then(() => undefined),
}

export const jobApi = {
  get: (id) => api.get(`/jobs/${id}`).then((r) => r.data),
}

export const fetchHealth = () => api.get('/health').then((r) => r.data)

export const fetchDatabaseHealth = () => api.get('/health/db').then((r) => r.data)
