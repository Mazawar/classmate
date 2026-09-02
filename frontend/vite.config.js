import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 开发代理：/api 请求转发到后端 FastAPI
export default defineConfig({
  plugins: [vue()],
  server: {
    host: 'localhost',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        // 将 vendor 库拆成独立 chunk，利于缓存与首屏加载
        manualChunks: {
          vue: ['vue', 'vue-router', 'pinia'],
          'naive-ui': ['naive-ui'],
        },
      },
    },
  },
})
