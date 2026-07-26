import { ApiError, type ApiEnvelope } from "../types/api";

const DEFAULT_BASE = "/api/v1";
const TOKEN_STORAGE_KEY = "quarry_kb_access_token";

let memoryToken: string | null = null;

function baseUrl(): string {
  return import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || DEFAULT_BASE;
}

function shouldNeverLog(value: string): boolean {
  const lower = value.toLowerCase();
  return (
    lower.includes("authorization") ||
    lower.includes("password") ||
    lower.includes("api_key") ||
    lower.includes("token=")
  );
}

export function getAccessToken(): string | null {
  if (memoryToken) {
    return memoryToken;
  }
  try {
    const restored = sessionStorage.getItem(TOKEN_STORAGE_KEY);
    memoryToken = restored;
    return restored;
  } catch {
    return null;
  }
}

export function setAccessToken(token: string | null): void {
  memoryToken = token;
  try {
    if (token) {
      sessionStorage.setItem(TOKEN_STORAGE_KEY, token);
    } else {
      sessionStorage.removeItem(TOKEN_STORAGE_KEY);
    }
  } catch {
    // Ignore storage failures; memory remains source of truth.
  }
}

export function clearAccessToken(): void {
  setAccessToken(null);
}

export async function apiRequest<T>(
  path: string,
  options: {
    method?: "GET" | "POST" | "PATCH";
    body?: unknown;
    auth?: boolean;
  } = {},
): Promise<{
  status: number;
  body: ApiEnvelope<T>;
}> {
  const url = `${baseUrl()}${path.startsWith("/") ? path : `/${path}`}`;
  const headers: Record<string, string> = { Accept: "application/json" };
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (options.auth !== false) {
    const token = getAccessToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }

  let response: Response;
  try {
    response = await fetch(url, {
      method: options.method || "GET",
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    });
  } catch {
    throw new ApiError("API_UNREACHABLE", "Unable to reach API.", 0);
  }

  let body: ApiEnvelope<T>;
  try {
    body = (await response.json()) as ApiEnvelope<T>;
  } catch {
    throw new ApiError("API_UNREACHABLE", "Unable to parse API response.", response.status);
  }

  if (body.error?.message && shouldNeverLog(body.error.message)) {
    body = {
      ...body,
      error: {
        code: body.error.code,
        message: "A safe configuration or dependency error occurred.",
      },
    };
  }

  return { status: response.status, body };
}

export function toApiError(status: number, body: ApiEnvelope<unknown>): ApiError {
  return new ApiError(
    body.error?.code || "API_ERROR",
    body.error?.message || "Request failed.",
    status,
  );
}
