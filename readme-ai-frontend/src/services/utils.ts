export const API_BASE_URL =
  (import.meta.env.VITE_BASE_API_URL as string) || "http://localhost:8000";

export interface ApiErrorResponse {
  status: "error";
  message: string;
  error_code: string;
  details?: {
    status_code?: number;
    [key: string]: unknown;
  };
  timestamp: string;
}

export interface ApiSuccessResponse {
  status: "success";
  data: string;
  timestamp: string;
}

export class ApiError extends Error {
  constructor(
    public message: string,
    public errorCode: string,
    public details?: Record<string, unknown>,
    public timestamp?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
