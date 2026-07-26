import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";
import LoginView from "../views/LoginView.vue";
import ShellView from "../views/ShellView.vue";
import AdminUsersView from "../views/AdminUsersView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: LoginView, meta: { public: true } },
    { path: "/", name: "home", component: ShellView },
    { path: "/admin/users", name: "admin-users", component: AdminUsersView, meta: { admin: true } },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (!auth.bootstrapped) {
    await auth.restoreSession();
  }
  if (to.meta.public) {
    if (auth.isAuthenticated && to.name === "login") {
      return { name: "home" };
    }
    return true;
  }
  if (!auth.isAuthenticated) {
    return { name: "login", query: { redirect: to.fullPath } };
  }
  if (to.meta.admin && !auth.isAdmin) {
    auth.markForbidden();
    return { name: "home" };
  }
  return true;
});

export default router;
