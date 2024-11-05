// vite.config.js
import { defineConfig } from "file:///Users/flybywindwen/Projects/llm-wechat/frontend/webview/html/node_modules/vite/dist/node/index.js";
import vue from "file:///Users/flybywindwen/Projects/llm-wechat/frontend/webview/html/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import path from "path";
var __vite_injected_original_dirname = "/Users/flybywindwen/Projects/llm-wechat/frontend/webview/html";
var vite_config_default = defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": path.resolve(__vite_injected_original_dirname, "./src"),
      "@styles": path.resolve(__vite_injected_original_dirname, "./src/assets/styles")
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `
          @use "@styles/_variables.scss" as *;
          @use "@styles/_mixins.scss" as *;
        `
      }
    }
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvVXNlcnMvZmx5Ynl3aW5kd2VuL1Byb2plY3RzL2xsbS13ZWNoYXQvZnJvbnRlbmQvd2Vidmlldy9odG1sXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCIvVXNlcnMvZmx5Ynl3aW5kd2VuL1Byb2plY3RzL2xsbS13ZWNoYXQvZnJvbnRlbmQvd2Vidmlldy9odG1sL3ZpdGUuY29uZmlnLmpzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9Vc2Vycy9mbHlieXdpbmR3ZW4vUHJvamVjdHMvbGxtLXdlY2hhdC9mcm9udGVuZC93ZWJ2aWV3L2h0bWwvdml0ZS5jb25maWcuanNcIjtpbXBvcnQgeyBkZWZpbmVDb25maWcgfSBmcm9tICd2aXRlJ1xuaW1wb3J0IHZ1ZSBmcm9tICdAdml0ZWpzL3BsdWdpbi12dWUnXG5pbXBvcnQgcGF0aCBmcm9tICdwYXRoJ1xuXG4vLyBodHRwczovL3ZpdGVqcy5kZXYvY29uZmlnL1xuZXhwb3J0IGRlZmF1bHQgZGVmaW5lQ29uZmlnKHtcbiAgcGx1Z2luczogW3Z1ZSgpXSxcbiAgcmVzb2x2ZToge1xuICAgIGFsaWFzOiB7XG4gICAgICAnQCc6IHBhdGgucmVzb2x2ZShfX2Rpcm5hbWUsICcuL3NyYycpLFxuICAgICAgJ0BzdHlsZXMnOiBwYXRoLnJlc29sdmUoX19kaXJuYW1lLCAnLi9zcmMvYXNzZXRzL3N0eWxlcycpLFxuICAgIH0sXG4gIH0sXG4gIGNzczoge1xuICAgIHByZXByb2Nlc3Nvck9wdGlvbnM6IHtcbiAgICAgIHNjc3M6IHtcbiAgICAgICAgYWRkaXRpb25hbERhdGE6IGBcbiAgICAgICAgICBAdXNlIFwiQHN0eWxlcy9fdmFyaWFibGVzLnNjc3NcIiBhcyAqO1xuICAgICAgICAgIEB1c2UgXCJAc3R5bGVzL19taXhpbnMuc2Nzc1wiIGFzICo7XG4gICAgICAgIGBcbiAgICAgIH1cbiAgICB9XG4gIH1cbn0pIl0sCiAgIm1hcHBpbmdzIjogIjtBQUF5VyxTQUFTLG9CQUFvQjtBQUN0WSxPQUFPLFNBQVM7QUFDaEIsT0FBTyxVQUFVO0FBRmpCLElBQU0sbUNBQW1DO0FBS3pDLElBQU8sc0JBQVEsYUFBYTtBQUFBLEVBQzFCLFNBQVMsQ0FBQyxJQUFJLENBQUM7QUFBQSxFQUNmLFNBQVM7QUFBQSxJQUNQLE9BQU87QUFBQSxNQUNMLEtBQUssS0FBSyxRQUFRLGtDQUFXLE9BQU87QUFBQSxNQUNwQyxXQUFXLEtBQUssUUFBUSxrQ0FBVyxxQkFBcUI7QUFBQSxJQUMxRDtBQUFBLEVBQ0Y7QUFBQSxFQUNBLEtBQUs7QUFBQSxJQUNILHFCQUFxQjtBQUFBLE1BQ25CLE1BQU07QUFBQSxRQUNKLGdCQUFnQjtBQUFBO0FBQUE7QUFBQTtBQUFBLE1BSWxCO0FBQUEsSUFDRjtBQUFBLEVBQ0Y7QUFDRixDQUFDOyIsCiAgIm5hbWVzIjogW10KfQo=
