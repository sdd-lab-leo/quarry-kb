<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { fetchFoundationStatus, type FoundationStatus } from "./api/health";

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

onMounted(() => {
  void refresh();
});
</script>

<template>
  <div class="shell">
    <header class="header">
      <h1 class="brand">Quarry KB</h1>
      <p class="tagline">Local foundation shell · bootstrap environment</p>
    </header>
    <main class="main">
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
        </div>
      </section>
    </main>
  </div>
</template>
