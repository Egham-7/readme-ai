import { ApiError, type ApiErrorResponse, API_BASE_URL } from "./utils";

export interface Template {
  id: number;
  title: string;
  content: string;
  preview_url?: string;
  featured: boolean;
  user_id: string;
}

export interface CreateTemplatePayload {
  title: string;
  content: string;
  preview_file?: File;
}

export interface UpdateTemplatePayload {
  title?: string;
  content?: string;
  preview_file?: File;
}

export interface TemplatesResponse {
  data: Template[];
  total_pages: number;
}

export const templateService = {
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
    formData.append("title", payload.title);
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
    if (payload.title) {
      formData.append("title", payload.title);
    }
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

export default templateService;
