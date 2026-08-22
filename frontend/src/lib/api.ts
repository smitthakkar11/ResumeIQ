import axios from 'axios'

/**
 * One shared Axios instance for the whole app.
 *
 * Centralising it means Phase 2 can attach the JWT in exactly one place
 * (an interceptor here) instead of in every component that makes a request.
 */
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8001/api',
  timeout: 15_000,
  headers: { 'Content-Type': 'application/json' },
})

// ---- Types mirroring the backend's Pydantic response schemas ----

export type HealthResponse = {
  status: string
  app: string
  environment: string
}

export type DatabaseHealthResponse = {
  status: string
  database: string
  detail: string | null
}

export async function fetchHealth(): Promise<HealthResponse> {
  const { data } = await api.get<HealthResponse>('/health')
  return data
}

export async function fetchDatabaseHealth(): Promise<DatabaseHealthResponse> {
  const { data } = await api.get<DatabaseHealthResponse>('/health/db')
  return data
}
