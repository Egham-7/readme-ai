export const API_BASE_URL =
  (import.meta.env.VITE_BASE_API_URL as string) || "http://localhost:8000";

export interface RepoRequestParams {
  repo_url: string;
  branch?: string;
  template_id?: number;
  title?: string;
}

export interface HealthCheckResponse {
  status: string;
  version: string;
  services: {
    analyzer: boolean;
    compiler: boolean
}
};

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

export interface Template {
  id: number;
  content: string;
  preview_url?: string;
  featured: boolean;
  user_id: string;
}

export interface CreateTemplatePayload {
  content: string;
  preview_file?: File;
}

export interface UpdateTemplatePayload {
  content?: string;
  preview_file?: File;
}

export interface TemplatesResponse {
  data: Template[];
  total_pages: number;
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

export interface ProgressUpdate {
  stage: string;
  message: string;
  progress: number;
  timestamp: string;
}

export const getErrorMessage = (error: ApiError): string => {
  switch (error.errorCode) {
    case "REPO_ACCESS_ERROR":
      return "Unable to access this repository. Please verify it exists and you have proper permissions.";
    case "VALIDATION_ERROR":
      return "The GitHub repository URL provided is not valid. Please check the URL and try again.";
    case "ANALYSIS_ERROR":
      return "We couldn't analyze this repository. Please verify the repository contains valid code.";
    case "INTERNAL_SERVER_ERROR":
      return "Our service is experiencing an issue. Please try again later.";

    case "RATE_LIMIT_EXCEEDED":
      return "You have made too many requests, please try again in 10 minutes.";
    default:
      return "Something went wrong while generating your README. Please try again.";
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
    default:
      return "Try Again";
  }
};

export const readmeService = {
  generateReadme: async (
    params: RepoRequestParams,
    token: string,
    onProgress?: (update: ProgressUpdate) => void,
  ): Promise<string> => {
    const response = await fetch(`${API_BASE_URL}/generate-readme`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(params),
    });

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error("Failed to initialize stream reader");
    }

    let result = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split("\n");

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const eventData = JSON.parse(line.slice(6));
          if (eventData.event === "progress" && onProgress) {
            onProgress(JSON.parse(eventData.data));
          } else if (eventData.event === "complete") {
            result = JSON.parse(eventData.data).data;
          } else if (eventData.event === "error") {
            const errorData = JSON.parse(eventData.data);
            throw new ApiError(
              errorData.message,
              errorData.error_code,
              errorData.details,
              errorData.timestamp,
            );
          }
        }
      }
    }

    return result;
  },

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

  getAllTemplates: async (
    token: string,
    page: number,
    pageSize: number,
  ): Promise<TemplatesResponse> => {
    const response = await fetch(
      `${API_BASE_URL}/templates/?page=${page}&page_size=${pageSize}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    if (!response.ok) {
      const errorData = (await response.json()) as ApiErrorResponse;
      throw new ApiError(
        errorData.message,
        errorData.error_code,
        errorData.details,
        errorData.timestamp,
      );
    }

    return response.json();
  },

  getTemplate: async (id: number, token: string): Promise<Template> => {
    const response = await fetch(`${API_BASE_URL}/templates/${id}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = (await response.json()) as ApiErrorResponse;
      throw new ApiError(
        errorData.message,
        errorData.error_code,
        errorData.details,
        errorData.timestamp,
      );
    }

    return response.json();
  },

  createTemplate: async (
    payload: CreateTemplatePayload,
    token: string,
  ): Promise<Template> => {
    const formData = new FormData();
    formData.append("content", payload.content);
    if (payload.preview_file) {
      formData.append("preview_file", payload.preview_file);
    }

    const response = await fetch(`${API_BASE_URL}/templates/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = (await response.json()) as ApiErrorResponse;
      throw new ApiError(
        errorData.message,
        errorData.error_code,
        errorData.details,
        errorData.timestamp,
      );
    }

    return response.json();
  },

  updateTemplate: async (
    id: number,
    payload: UpdateTemplatePayload,
    token: string,
  ): Promise<Template> => {
    const formData = new FormData();
    if (payload.content) {
      formData.append("content", payload.content);
    }
    if (payload.preview_file) {
      formData.append("preview_file", payload.preview_file);
    }

    const response = await fetch(`${API_BASE_URL}/templates/${id}`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = (await response.json()) as ApiErrorResponse;
      throw new ApiError(
        errorData.message,
        errorData.error_code,
        errorData.details,
        errorData.timestamp,
      );
    }

    return response.json();
  },

  deleteTemplate: async (id: number, token: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/templates/${id}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = (await response.json()) as ApiErrorResponse;
      throw new ApiError(
        errorData.message,
        errorData.error_code,
        errorData.details,
        errorData.timestamp,
      );
    }
  },

  getUserTemplates: async (
    userId: string,
    token: string,
    page: number,
    pageSize: number,
  ): Promise<TemplatesResponse> => {
    const response = await fetch(
      `${API_BASE_URL}/templates/user/${userId}?page=${page}&page_size=${pageSize}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    if (!response.ok) {
      const errorData = (await response.json()) as ApiErrorResponse;
      throw new ApiError(
        errorData.message,
        errorData.error_code,
        errorData.details,
        errorData.timestamp,
      );
    }

    return response.json();
  },
};

export default readmeService;
