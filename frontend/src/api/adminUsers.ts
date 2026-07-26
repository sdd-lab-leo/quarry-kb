import { apiRequest, toApiError } from "./client";
import type { UserListResponse, UserRole, UserStatus, UserSummary } from "../types/auth";

export async function listUsers(): Promise<UserSummary[]> {
  const { status, body } = await apiRequest<UserListResponse>("/admin/users");
  if (!body.success || !body.data) {
    throw toApiError(status, body);
  }
  return body.data.items;
}

export async function createUser(input: {
  identifier: string;
  display_name: string;
  password: string;
  role: UserRole;
}): Promise<UserSummary> {
  const { status, body } = await apiRequest<UserSummary>("/admin/users", {
    method: "POST",
    body: input,
  });
  if (!body.success || !body.data) {
    throw toApiError(status, body);
  }
  return body.data;
}

export async function updateUser(
  userId: string,
  input: Partial<{ display_name: string; role: UserRole; status: UserStatus }>,
): Promise<UserSummary> {
  const { status, body } = await apiRequest<UserSummary>(`/admin/users/${userId}`, {
    method: "PATCH",
    body: input,
  });
  if (!body.success || !body.data) {
    throw toApiError(status, body);
  }
  return body.data;
}
