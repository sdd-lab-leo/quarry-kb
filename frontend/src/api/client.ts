import { ApiError, type ApiEnvelope } from "../types/api";

const DEFAULT_BASE = "/api/v1";

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

export async function apiRequest<T>(path: string): Promise<{
  status: number;
  body: ApiEnvelope<T>;
}> {
  const url = `${baseUrl()}${path.startsWith("/") ? path : `/${path}`}`;
  let response: Response;
  try {
    response = await fetch(url, {
      method: "GET",
      headers: { Accept: "application/json" },
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
    // Keep UI message generic if a secret-shaped string ever leaks.
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
