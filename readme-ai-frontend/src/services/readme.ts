const API_BASE_URL =
  (import.meta.env.VITE_BASE_API_URL as string) || "http://localhost:8000";

export interface RepoRequestParams {
  repo_url: string;
  branch?: string;
}

export interface HealthCheckResponse {
  status: string;
  version: string;
  services: {
    analyzer: boolean;
    compiler: boolean;
  };
}

export interface ApiErrorResponse {
  status: "error";
  message: string;
  error_code: string;
  details?: Record<string, unknown>;
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
  user_id: string;
  preview_url?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateTemplatePayload {
  content: string;
  user_id: string;
  preview_file?: File;
}

export interface UpdateTemplatePayload {
  content?: string;
  preview_file?: File;
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
    case "VALIDATION_ERROR":
      return "The GitHub repository URL provided is not valid. Please check the URL and try again.";
    case "ANALYSIS_FAILED":
      return "We couldn't analyze this repository. Please verify the repository is public and contains code.";
    case "SERVICE_UNAVAILABLE":
      return "Our service is temporarily unavailable. Please try again in a few moments.";
    default:
      return "Something went wrong while generating your README. Please try again.";
  }
};

export const getErrorAction = (error: ApiError): string => {
  switch (error.errorCode) {
    case "VALIDATION_ERROR":
      return "Check Repository URL";
    case "ANALYSIS_FAILED":
      return "Verify Repository Access";
    case "SERVICE_UNAVAILABLE":
      return "Try Again Later";
    default:
      return "Try Again";
  }
};

export const readmeService = {
  generateReadme: async (params: RepoRequestParams): Promise<string> => {
    const response = await fetch(`${API_BASE_URL}/generate-readme`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(params),
    });

    const data = (await response.json()) as
      | ApiErrorResponse
      | ApiSuccessResponse;

    if (!response.ok) {
      const errorData = data as ApiErrorResponse;
      throw new ApiError(
        errorData.message,
        errorData.error_code,
        errorData.details,
        errorData.timestamp,
      );
    }

    const successData = data as ApiSuccessResponse;
    return successData.data;
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

  getAllTemplates: async (): Promise<Template[]> => {
    const response = await fetch(`${API_BASE_URL}/templates/`);

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

  // Get single template
  getTemplate: async (id: number): Promise<Template> => {
    const response = await fetch(`${API_BASE_URL}/templates/${id}`);

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

  // Create template
  createTemplate: async (payload: CreateTemplatePayload): Promise<Template> => {
    const formData = new FormData();
    formData.append("content", payload.content);
    formData.append("user_id", payload.user_id);
    if (payload.preview_file) {
      formData.append("preview_file", payload.preview_file);
    }

    const response = await fetch(`${API_BASE_URL}/templates/`, {
      method: "POST",
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

  // Update template
  updateTemplate: async (
    id: number,
    payload: UpdateTemplatePayload,
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

  // Delete template
  deleteTemplate: async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/templates/${id}`, {
      method: "DELETE",
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
};

export default readmeService;
