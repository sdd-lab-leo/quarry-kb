<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { createUser, listUsers, updateUser } from "../api/adminUsers";
import { ApiError } from "../types/api";
import type { UserRole, UserSummary } from "../types/auth";
import { useAuthStore } from "../stores/auth";

const auth = useAuthStore();
const router = useRouter();
const users = ref<UserSummary[]>([]);
const errorMessage = ref<string | null>(null);
const identifier = ref("");
const displayName = ref("");
const password = ref("");
const role = ref<UserRole>("Viewer");

async function refresh(): Promise<void> {
  errorMessage.value = null;
  try {
    users.value = await listUsers();
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      auth.handleUnauthorized();
      await router.replace({ name: "login" });
      return;
    }
    if (error instanceof ApiError && error.status === 403) {
      auth.markForbidden();
      await router.replace({ name: "home" });
      return;
    }
    errorMessage.value = error instanceof ApiError ? error.message : "Unable to load users.";
  }
}

async function onCreate(): Promise<void> {
  errorMessage.value = null;
  try {
    await createUser({
      identifier: identifier.value,
      display_name: displayName.value,
      password: password.value,
      role: role.value,
    });
    identifier.value = "";
    displayName.value = "";
    password.value = "";
    role.value = "Viewer";
    await refresh();
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : "Unable to create user.";
    password.value = "";
  }
}

async function toggleStatus(user: UserSummary): Promise<void> {
  errorMessage.value = null;
  const next = user.status === "active" ? "deactivated" : "active";
  if (next === "deactivated" && !window.confirm(`Deactivate ${user.identifier}?`)) {
    return;
  }
  try {
    await updateUser(user.user_id, { status: next });
    await refresh();
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : "Unable to update user.";
  }
}

async function changeRole(user: UserSummary, nextRole: UserRole): Promise<void> {
  errorMessage.value = null;
  try {
    await updateUser(user.user_id, { role: nextRole });
    await refresh();
  } catch (error) {
    errorMessage.value = error instanceof ApiError ? error.message : "Unable to update role.";
  }
}

onMounted(() => {
  void refresh();
});
</script>

<template>
  <div class="shell">
    <header class="header">
      <h1 class="brand">Quarry KB</h1>
      <p class="tagline">Admin user management</p>
    </header>
    <main class="main">
      <section class="status-panel">
        <p class="status-label">Create account</p>
        <form class="stack" @submit.prevent="onCreate">
          <label>
            Identifier
            <input v-model="identifier" required />
          </label>
          <label>
            Display name
            <input v-model="displayName" required />
          </label>
          <label>
            Initial password
            <input v-model="password" type="password" required />
          </label>
          <label>
            Role
            <select v-model="role">
              <option value="Admin">Admin</option>
              <option value="Editor">Editor</option>
              <option value="Viewer">Viewer</option>
            </select>
          </label>
          <div class="actions">
            <button type="submit">Create</button>
            <button type="button" @click="router.push({ name: 'home' })">Back</button>
          </div>
        </form>
        <p v-if="errorMessage" class="message error">{{ errorMessage }}</p>
      </section>

      <section class="status-panel">
        <p class="status-label">Accounts</p>
        <table class="users-table">
          <thead>
            <tr>
              <th>Identifier</th>
              <th>Name</th>
              <th>Role</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.user_id">
              <td>{{ user.identifier }}</td>
              <td>{{ user.display_name }}</td>
              <td>
                <select
                  :value="user.role"
                  @change="changeRole(user, ($event.target as HTMLSelectElement).value as UserRole)"
                >
                  <option value="Admin">Admin</option>
                  <option value="Editor">Editor</option>
                  <option value="Viewer">Viewer</option>
                </select>
              </td>
              <td>{{ user.status }}</td>
              <td>
                <button type="button" @click="toggleStatus(user)">
                  {{ user.status === "active" ? "Deactivate" : "Reactivate" }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>
  </div>
</template>
