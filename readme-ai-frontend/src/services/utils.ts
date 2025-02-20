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

export const getErrorMessage = (error: ApiError): string => {
  switch (error.errorCode) {
    // Repository Related Errors
    case "REPO_ACCESS_ERROR":
      return "Unable to access this repository. Please verify it exists and you have proper permissions.";
    case "VALIDATION_ERROR":
      return "The GitHub repository URL provided is not valid. Please check the URL and try again.";
    case "ANALYSIS_ERROR":
      return "We couldn't analyze this repository. Please verify the repository contains valid code.";

    // Authentication/Authorization Errors
    case "FORBIDDEN":
      return "You don't have permission to perform this action.";
    case "NOT_FOUND":
      return "The requested resource was not found.";
    case "USER_NOT_FOUND":
      return "User account not found. Please ensure you're logged in.";

    // Rate Limiting Errors
    case "RATE_LIMIT_EXCEEDED":
      return "You've reached the rate limit. Please wait before trying again.";
    case "INSUFFICIENT_TOKENS":
      return "You've used all available tokens. Please wait for the next reset or purchase more tokens.";

    // Server Errors
    case "INTERNAL_SERVER_ERROR":
      return "Our service is experiencing technical difficulties. Please try again later.";

    // Template Errors
    case "TEMPLATE_NOT_FOUND":
      return "The requested template could not be found.";
    case "TEMPLATE_ACCESS_DENIED":
      return "You don't have permission to access this template.";

    default:
      return "An unexpected error occurred. Please try again or contact support if the issue persists.";
  }
};

export const getErrorAction = (error: ApiError): string => {
  switch (error.errorCode) {
    case "REPO_ACCESS_ERROR":
      return "Check Repository Access";
    case "VALIDATION_ERROR":
      return "Check Repository URL";
    case "ANALYSIS_ERROR":
      return "Verify Repository Content";
    case "FORBIDDEN":
      return "Check Permissions";
    case "NOT_FOUND":
      return "Verify Resource";
    case "USER_NOT_FOUND":
      return "Sign In";
    case "RATE_LIMIT_EXCEEDED":
      return "Wait and Retry";
    case "INSUFFICIENT_TOKENS":
      return "View Token Status";
    case "TEMPLATE_NOT_FOUND":
      return "Browse Templates";
    case "TEMPLATE_ACCESS_DENIED":
      return "Check Permissions";
    default:
      return "Try Again";
  }
};

export const getErrorSeverity = (
  error: ApiError,
): "error" | "warning" | "info" => {
  switch (error.errorCode) {
    case "INTERNAL_SERVER_ERROR":
    case "ANALYSIS_ERROR":
      return "error";
    case "RATE_LIMIT_EXCEEDED":
    case "INSUFFICIENT_TOKENS":
    case "FORBIDDEN":
      return "warning";
    case "VALIDATION_ERROR":
    case "NOT_FOUND":
    case "USER_NOT_FOUND":
      return "info";
    default:
      return "error";
  }
};

export const isRetryableError = (error: ApiError): boolean => {
  const retryableCodes = [
    "INTERNAL_SERVER_ERROR",
    "ANALYSIS_ERROR",
    "RATE_LIMIT_EXCEEDED",
  ];
  return retryableCodes.includes(error.errorCode);
};
