/// <reference types="vitest" />
import path from 'path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // React関連ライブラリを分離
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          // UI関連ライブラリを分離
          'ui-vendor': ['framer-motion', 'lucide-react', 'class-variance-authority', 'clsx', 'tailwind-merge'],
          // データフェッチ関連を分離
          'data-vendor': ['@tanstack/react-query', 'axios'],
          // フォーム関連を分離
          'form-vendor': ['react-hook-form', 'zod'],
        },
      },
    },
    // チャンクサイズ警告の閾値を引き上げ（500KB → 1000KB）
    chunkSizeWarningLimit: 1000,
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    // Only scan src directory for tests to avoid node_modules
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    exclude: ['node_modules', 'dist', 'e2e'],
    testTimeout: 10000,
    hookTimeout: 10000,
    teardownTimeout: 10000,
    // Prevent Vitest from watching node_modules
    server: {
      watch: {
        ignored: ['**/node_modules/**', '**/dist/**'],
      },
    },
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
  },
})
