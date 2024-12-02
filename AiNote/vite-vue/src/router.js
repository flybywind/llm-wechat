import { createRouter, createWebHistory } from "vue-router";
import Settings from "./components/Settings.vue";
import AiBotDialog from "./components/AiBotDialog.vue";
const routes = [
  {
    path: "/settings",
    component: Settings,
  },
  { path: "/", component: AiBotDialog },
];

// 创建路由器实例并导出
const router = createRouter({
  history: createWebHistory(),
  routes, // 简写为 `routes: routes`
});

export default router;
