<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { fetchFoundationStatus, type FoundationStatus } from "../api/health";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const status = ref<FoundationStatus>({
  state: "loading",
  message: "Checking foundation readiness…",
});

const title = computed(() => {
  switch (status.value.state) {
    case "ready":
      return "Ready";
    case "needs_attention":
      return "Needs attention";
    case "unreachable":
      return "Unable to reach API";
    default:
      return "Loading";
  }
});

async function refresh(): Promise<void> {
  status.value = {
    state: "loading",
    message: "Checking foundation readiness…",
  };
  status.value = await fetchFoundationStatus();
}

function logout(): void {
  auth.logout();
  void router.replace({ name: "login" });
}

onMounted(() => {
  void refresh();
});
</script>

<template>
  <div class="shell">
    <header class="header">
      <h1 class="brand">Quarry KB</h1>
      <p class="tagline">
        Signed in as {{ auth.user?.display_name }} · {{ auth.user?.role }}
      </p>
    </header>
    <main class="main">
      <section v-if="auth.forbidden" class="status-panel">
        <p class="status-label">Authorization</p>
        <h2 class="status-title needs_attention">Forbidden</h2>
        <p class="message">You do not have permission for that page.</p>
      </section>
      <section class="status-panel" aria-live="polite">
        <p class="status-label">Foundation status</p>
        <h2 class="status-title" :class="status.state">{{ title }}</h2>
        <p class="message">{{ status.message }}</p>
        <ul v-if="status.components" class="components">
          <li v-for="(value, key) in status.components" :key="key">
            <span>{{ key }}</span>
            <strong>{{ value }}</strong>
          </li>
        </ul>
        <div class="actions">
          <button type="button" @click="refresh">Retry</button>
          <button v-if="auth.isAdmin" type="button" @click="router.push({ name: 'admin-users' })">
            Manage users
          </button>
          <button type="button" @click="logout">Log out</button>
        </div>
      </section>
    </main>
  </div>
</template>
