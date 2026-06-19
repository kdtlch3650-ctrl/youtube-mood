import path from 'node:path'

export default {
  cacheDir: path.join(process.env.TEMP ?? 'C:/Temp', 'vite-cache', 'youtube-mood-frontend'),
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
