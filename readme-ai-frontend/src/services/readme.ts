const API_BASE_URL =
  (import.meta.env.VITE_BASE_API_URL as string) || "http://localhost:8000";

export interface RepoRequestParams {
  repo_url: string;
  branch?: string;
}

export interface HealthCheckResponse {
  status: string;
  version: string;
}

export interface ApiErrorResponse {
  status: "error";
  message: string;
  error_code: string;
}

export const readmeService = {
  generateReadme: async (params: RepoRequestParams): Promise<string> => {
    const response = await fetch(`${API_BASE_URL}/generate-readme`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const errorData = (await response.json()) as ApiErrorResponse;
      throw new Error(errorData.message || "Failed to generate README");
    }

    const data = await response.text();
    return data.replace(/^"|"$/g, "").replace(/\\n/g, "\n");
  },

  checkHealth: async (): Promise<HealthCheckResponse> => {
    const response = await fetch(`${API_BASE_URL}/`);

    if (!response.ok) {
      throw new Error("Health check failed");
    }

    return response.json() as Promise<HealthCheckResponse>;
  },
};

export default readmeService;
