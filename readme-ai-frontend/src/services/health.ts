import { API_BASE_URL, ApiError, type ApiErrorResponse } from "./utils";

interface HealthCheckResponse {
  status: string;
  version: string;
  services: {
    analyzer: boolean;
    compiler: boolean;
  };
}

export const healthService = {
  checkHealth: async (): Promise<HealthCheckResponse> => {
    const response = await fetch(`${API_BASE_URL}/`);
    if (!response.ok) {
      const errorData = (await response.json()) as ApiErrorResponse;
      throw new ApiError(
        errorData.message,
        errorData.error_code,
        errorData.details,
        errorData.timestamp,
      );
    }
    return response.json() as Promise<HealthCheckResponse>;
  },
};
