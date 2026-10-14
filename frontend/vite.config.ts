import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    watch: {
      ignored: ['**/src-tauri/**'],
    },
    host: process.env.API_PROXY_TARGET ? '0.0.0.0' : '127.0.0.1',
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': process.env.API_PROXY_TARGET ?? 'http://localhost:8000',
    },
  },
})
