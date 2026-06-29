import axios, { type AxiosError } from "axios";

import type { ApiResponse } from "@/types/api";
import { API_ERROR_CODE } from "@/types/api";
import { ensureAuthToken } from "@/api/auth";

const request = axios.create({
  baseURL: "/api",
  timeout: 60000
});

request.interceptors.request.use(async (config) => {
  const token = await ensureAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

request.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiResponse<unknown>>) => {
    const status = error.response?.status;

    if (status === API_ERROR_CODE.UNAUTHORIZED) {
      console.warn("[auth] Session expired or missing token.");
    }

    if (status === API_ERROR_CODE.FORBIDDEN) {
      console.warn("[auth] Permission denied.");
    }

    return Promise.reject(error);
  }
);

export { request };

export function isApiSuccess<T>(response: ApiResponse<T>): boolean {
  return response.code === API_ERROR_CODE.SUCCESS;
}

export default request;
