import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// Unmount components and clear storage between tests, so one test's session
// cannot leak into the next.
afterEach(() => {
  cleanup()
  localStorage.clear()
  sessionStorage.clear()
})
