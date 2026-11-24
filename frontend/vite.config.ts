import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/wave-overlays": "http://localhost:8000",
    },
  },
  test: {
    environment: "jsdom"
  },
})
