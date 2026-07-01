import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite configuration for docuFetch frontend — includes Vitest setup for unit tests.
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    exclude: ['**/node_modules/**', '**/tests/e2e/**'],
  },
})
