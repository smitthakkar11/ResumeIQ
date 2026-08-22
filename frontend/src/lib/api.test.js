import { describe, expect, it, beforeEach } from 'vitest'
import { AxiosError } from 'axios'
import { api, errorMessage, tokenStorage } from '@/lib/api'

describe('tokenStorage', () => {
  beforeEach(() => localStorage.clear())

  it('round-trips a token', () => {
    tokenStorage.set('abc.def.ghi')
    expect(tokenStorage.get()).toBe('abc.def.ghi')
  })

  it('returns null when nothing is stored', () => {
    expect(tokenStorage.get()).toBeNull()
  })

  it('clears the token on logout', () => {
    tokenStorage.set('abc')
    tokenStorage.clear()
    expect(tokenStorage.get()).toBeNull()
  })
})

describe('request interceptor', () => {
  beforeEach(() => localStorage.clear())

  it('attaches the bearer token when one exists', async () => {
    tokenStorage.set('my-token')
    const config = await api.interceptors.request.handlers[0].fulfilled({ headers: {} })
    expect(config.headers.Authorization).toBe('Bearer my-token')
  })

  it('sends no Authorization header when logged out', async () => {
    const config = await api.interceptors.request.handlers[0].fulfilled({ headers: {} })
    expect(config.headers.Authorization).toBeUndefined()
  })
})

describe('errorMessage', () => {
  const axiosError = (data, status = 400) => {
    const err = new AxiosError('boom')
    err.response = { data, status }
    return err
  }

  it("surfaces FastAPI's string detail", () => {
    expect(errorMessage(axiosError({ detail: 'Incorrect email or password' }))).toBe(
      'Incorrect email or password',
    )
  })

  it('surfaces the first message from a 422 validation list', () => {
    const detail = [{ loc: ['body', 'email'], msg: 'value is not a valid email address' }]
    expect(errorMessage(axiosError({ detail }, 422))).toContain('valid email')
  })

  it('explains an unreachable server rather than showing a raw error', () => {
    const err = new AxiosError('Network Error')
    expect(errorMessage(err)).toMatch(/cannot reach the server/i)
  })

  it('falls back to the supplied message for anything unrecognised', () => {
    expect(errorMessage(new Error('nope'), 'Upload failed')).toBe('Upload failed')
  })
})
