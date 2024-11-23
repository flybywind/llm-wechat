import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  const isDev = command === "preview" || mode === "development";
  // console.log(`command: ${command}, mode: ${mode}, isDev: ${isDev}`);
  const baseRolloutOptions = {
    input: {
      index: path.resolve(__dirname, "index.html"),
      agents_conf: path.resolve(__dirname, "agents_conf.html"),
    },
  };
  const baseConfig = {
    plugins: [vue()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
        "@styles": path.resolve(__dirname, "./src/assets/styles"),
      },
    },
    test: {
      environment: "jsdom", // 设置测试环境为 JSDOM
      globals: true, // 启用全局变量
      setupFiles: "./setupTest.js",
      include: ["**/*.test.js"], // 包含测试文件的模式
    },
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `
          @use "@styles/_variables.scss" as *;
          @use "@styles/_mixins.scss" as *;
        `,
        },
      },
    },
    optimizeDeps: {
      include: [],
      exclude: [],
      disabled: true, // 禁用开发环境中的缓存
    },
  };
  const devConfig = {
    ...baseConfig,
    build: {
      sourcemap: "source-map",
      // 禁用压缩
      minify: false,
      // 开发环境的构建配置
      rollupOptions: {
        ...baseRolloutOptions,
        output: {
          // 保持文件名不被 hash
          entryFileNames: `assets/[name].js`,
          chunkFileNames: `assets/[name].js`,
          assetFileNames: `assets/[name].[ext]`,
        },
      },
    },
  };

  const prodConfig = {
    ...baseConfig,
    build: {
      // 禁用源码映射以减小体积
      sourcemap: false,
      // 启用压缩
      minify: "terser",
      terserOptions: {
        compress: {
          drop_console: true, // 移除 console
          drop_debugger: true, // 移除 debugger
          pure_funcs: ["console.log", "console.info", "console.debug", "console.warn"],
          // 生产环境时移除代码块
          dead_code: true,
          // 移除未使用的变量
          unused: true,
          // 移除无法访问的代码
          passes: 2,
        },
        mangle: {
          // 混淆变量名
          toplevel: true,
          safari10: true,
        },
        format: {
          // 移除注释
          comments: false,
          // 压缩空格
          beautify: false,
        },
      },
      // 生产环境构建配置
      rollupOptions: {
        ...baseRolloutOptions,
        output: {
          // 文件名添加 hash
          entryFileNames: "assets/[name].[hash].js",
          chunkFileNames: "assets/[name].[hash].js",
          assetFileNames: "assets/[name].[hash].[ext]",
          // 代码分割配置
          manualChunks: {
            // 将 Vue 相关库分割成单独的 chunk
            "vue-vendor": ["vue"],
            // 将其他大型第三方库分割
            vendor: [
              // 其他常用库...
            ],
          },
        },
      },
      // 设置块大小警告的限制
      chunkSizeWarningLimit: 1000,
      // 启用 gzip 压缩
      reportCompressedSize: true,
      // 禁用 brotli 压缩大小报告以提升构建性能
      brotliSize: false,
    },
  };
  const conf = isDev ? devConfig : prodConfig;
  console.log(`isDev: ${isDev}, config: ${JSON.stringify(conf)}`);
  return conf;
});