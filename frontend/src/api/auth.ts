import { apiRequest, toApiError } from "./client";
import type { LoginResponse, UserSummary } from "../types/auth";

export async function loginRequest(identifier: string, password: string): Promise<LoginResponse> {
  const { status, body } = await apiRequest<LoginResponse>("/auth/login", {
    method: "POST",
    body: { identifier, password },
    auth: false,
  });
  if (!body.success || !body.data) {
    throw toApiError(status, body);
  }
  return body.data;
}

export async function fetchCurrentUser(): Promise<UserSummary> {
  const { status, body } = await apiRequest<UserSummary>("/auth/me");
  if (!body.success || !body.data) {
    throw toApiError(status, body);
  }
  return body.data;
}
