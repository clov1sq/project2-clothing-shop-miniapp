import react from '@vitejs/plugin-react';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  const apiTarget = (
    env.VITE_API_URL ||
    env.VITE_API_BASE_URL ||
    'http://localhost:8000'
  ).replace(/\/$/, '');

  const proxy = {
    '/api': {
      target: apiTarget,
      changeOrigin: true,
      secure: apiTarget.startsWith('https://'),
    },
  };

  return {
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      port: 5173,
      proxy,
    },
    preview: {
      host: '0.0.0.0',
      proxy,
    },
  };
});
