import { ApiError } from "./utils";
import { API_BASE_URL } from "./utils";

export interface ProgressUpdate {
  stage: string;
  message: string;
  progress: number;
  timestamp: string;
}

export interface RepoRequestParams {
  repo_url: string;
  template_id?: number;
  title?: string;
}

export interface ReadmeVersion {
  content: string;
  id: number;
  readme_id: number;
  version_number: number;
  created_at: string;
}

export interface ChatMessage {
  content: string;
  role: string;
  readme_id: number;
  created_at: string;
  readme_version_id?: number;
}

export interface Readme {
  id: number;
  user_id: string;
  title: string;
  repository_url: string;
  created_at: string;
  updated_at: string | null;
  versions: ReadmeVersion[];
  chat_messages: ChatMessage[];
}

export interface ReadmesResponse {
  data: Readme[];
  total_pages: number;
}

export const readmeService = {
  generateReadme: (
    params: RepoRequestParams,
    token: string,
    onProgress?: (update: ProgressUpdate) => void,
  ): Promise<string> =>
    new Promise((resolve, reject) => {
      const eventSource = new EventSource(
        `${API_BASE_URL}/generate-readme?${new URLSearchParams({
          repo_url: params.repo_url,
          ...(params.template_id && {
            template_id: params.template_id.toString(),
          }),
          ...(params.title && {
            title: params.title,
          }),
          token,
        })}`,
      );

      eventSource.addEventListener("progress", (event: MessageEvent) => {
        onProgress?.(JSON.parse(event.data));
      });

      eventSource.addEventListener("complete", (event: MessageEvent) => {
        const result = JSON.parse(event.data);
        resolve(result.data);
        eventSource.close();
      });

      eventSource.addEventListener("error", (event: MessageEvent) => {
        if (event.data) {
          const errorData = JSON.parse(event.data);
          reject(
            new ApiError(
              errorData.message,
              errorData.error_code,
              errorData.details,
              errorData.timestamp,
            ),
          );
        } else {
          reject(
            new ApiError("Failed to connect to server", "CONNECTION_ERROR"),
          );
        }
        eventSource.close();
      });

      return eventSource;
    }),

  getUserReadmes: async (
    token: string,
    page: number = 1,
    pageSize: number = 10,
  ): Promise<ReadmesResponse> => {
    const response = await fetch(
      `${API_BASE_URL}/readmes?${new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
      })}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    if (!response.ok) {
      const error = await response.json();
      throw new ApiError(
        error.message,
        error.error_code,
        error.details,
        error.timestamp,
      );
    }

    return response.json();
  },

  updateReadme: async (
    token: string,
    id: number,
    content: string,
  ): Promise<ReadmeVersion> => {
    const response = await fetch(`${API_BASE_URL}/readmes/${id}`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        content,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new ApiError(
        error.message,
        error.error_code,
        error.details,
        error.timestamp,
      );
    }

    const result = await response.json();
    return result.data;
  },

  deleteReadme: async (token: string, readmeId: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/readmes/${readmeId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new ApiError(
        error.message,
        error.error_code,
        error.details,
        error.timestamp,
      );
    }
  },
};
