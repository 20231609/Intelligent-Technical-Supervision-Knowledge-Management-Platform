export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export interface PaginatedList<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

export type UserRole = "user" | "admin" | "super_admin";

export interface AuthUser {
  id: number | string;
  username: string;
  role: UserRole;
}

export interface LoginResponseData {
  token: string;
  user: AuthUser;
}

export const API_ERROR_CODE = {
  SUCCESS: 200,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  SERVER_ERROR: 500
} as const;
