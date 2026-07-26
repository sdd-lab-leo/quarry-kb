import { defineStore } from "pinia";
import { computed, ref } from "vue";
import { fetchCurrentUser, loginRequest } from "../api/auth";
import { ApiError } from "../types/api";
import type { UserSummary } from "../types/auth";
import { clearAccessToken, getAccessToken, setAccessToken } from "../api/client";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<UserSummary | null>(null);
  const bootstrapped = ref(false);
  const forbidden = ref(false);
  const errorMessage = ref<string | null>(null);

  const isAuthenticated = computed(() => !!user.value && !!getAccessToken());
  const isAdmin = computed(() => user.value?.role === "Admin");

  async function restoreSession(): Promise<void> {
    errorMessage.value = null;
    forbidden.value = false;
    const token = getAccessToken();
    if (!token) {
      user.value = null;
      bootstrapped.value = true;
      return;
    }
    try {
      user.value = await fetchCurrentUser();
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        clearAccessToken();
        user.value = null;
      } else if (error instanceof ApiError && error.status === 403) {
        forbidden.value = true;
      } else {
        errorMessage.value = "Unable to restore session.";
      }
    } finally {
      bootstrapped.value = true;
    }
  }

  async function login(identifier: string, password: string): Promise<void> {
    errorMessage.value = null;
    forbidden.value = false;
    try {
      const result = await loginRequest(identifier, password);
      setAccessToken(result.access_token);
      user.value = result.user;
    } catch (error) {
      clearAccessToken();
      user.value = null;
      if (error instanceof ApiError) {
        errorMessage.value = "Invalid credentials.";
      } else {
        errorMessage.value = "Unable to reach API.";
      }
      throw error;
    }
  }

  function logout(): void {
    clearAccessToken();
    user.value = null;
    forbidden.value = false;
    errorMessage.value = null;
  }

  function markForbidden(): void {
    forbidden.value = true;
  }

  function handleUnauthorized(): void {
    logout();
  }

  return {
    user,
    bootstrapped,
    forbidden,
    errorMessage,
    isAuthenticated,
    isAdmin,
    restoreSession,
    login,
    logout,
    markForbidden,
    handleUnauthorized,
  };
});
