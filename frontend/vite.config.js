import path from 'node:path'

export default {
  base: process.env.VITE_BASE_PATH ?? '/',
  cacheDir: path.join(process.env.TEMP ?? 'C:/Temp', 'vite-cache', 'youtube-mood-frontend'),
  server: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
  },
  preview: {
    host: '127.0.0.1',
    port: 5173,
    strictPort: true,
  },
  resolve: {
    preserveSymlinks: true,
  },
  optimizeDeps: {
    noDiscovery: true,
    include: ['react', 'react-dom/client', 'react/jsx-dev-runtime'],
    ignoreOutdatedRequests: true,
  },
  build: {
    emptyOutDir: false,
  },
}
