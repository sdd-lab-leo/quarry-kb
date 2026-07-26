<script setup lang="ts">
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const identifier = ref("");
const password = ref("");
const submitting = ref(false);

async function onSubmit(): Promise<void> {
  submitting.value = true;
  try {
    await auth.login(identifier.value, password.value);
    password.value = "";
    const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "/";
    await router.replace(redirect || "/");
  } catch {
    password.value = "";
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <div class="shell">
    <header class="header">
      <h1 class="brand">Quarry KB</h1>
      <p class="tagline">Sign in to continue</p>
    </header>
    <main class="main">
      <form class="status-panel" @submit.prevent="onSubmit">
        <p class="status-label">Account login</p>
        <label>
          Identifier
          <input v-model="identifier" name="identifier" autocomplete="username" required />
        </label>
        <label>
          Password
          <input
            v-model="password"
            name="password"
            type="password"
            autocomplete="current-password"
            required
          />
        </label>
        <p v-if="auth.errorMessage" class="message error">{{ auth.errorMessage }}</p>
        <div class="actions">
          <button type="submit" :disabled="submitting">
            {{ submitting ? "Signing in…" : "Sign in" }}
          </button>
        </div>
      </form>
    </main>
  </div>
</template>
