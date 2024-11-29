import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { resolve } from "path";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "./src"),
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`, // 全局 SCSS 变量
      },
    },
  },
  base: "./", // 将路径设置为相对路径
  build: {
    outDir: "../www", // 输出目录与 Cordova www 同步
    emptyOutDir: true,
  },
  server: {
    port: 3000,
    // proxy: {
    //   "/api": "http://localhost:5000", // 配置代理（如有需要）
    // },
  },
});
