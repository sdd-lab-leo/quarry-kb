export type UserRole = "Admin" | "Editor" | "Viewer";
export type UserStatus = "active" | "deactivated";

export interface UserSummary {
  user_id: string;
  identifier: string;
  display_name: string;
  role: UserRole;
  status: UserStatus;
  created_at: string;
  updated_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  expires_at: string;
  user: UserSummary;
}

export interface UserListResponse {
  items: UserSummary[];
}
