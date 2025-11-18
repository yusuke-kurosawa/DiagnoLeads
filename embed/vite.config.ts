import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      name: 'DiagnoLeads',
      formats: ['es', 'umd'],
      fileName: (format) => `diagnoleads-widget.${format}.js`
    },
    rollupOptions: {
      // External dependencies that shouldn't be bundled
      external: [],
      output: {
        // Global variables for UMD build
        globals: {}
      }
    },
    // Target modern browsers for smaller bundle
    target: 'es2015',
    // Minify for production
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },
    // Source maps for debugging
    sourcemap: true
  },
  server: {
    port: 3001,
    open: '/demo.html'
  }
});
