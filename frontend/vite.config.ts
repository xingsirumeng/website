import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
  base: './',   // 相对路径，适配 GitHub Pages 子目录
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // 正文里的图片用相对地址 /images/xxx，本地开发要靠这条代理打到本地后端
      '/images': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
