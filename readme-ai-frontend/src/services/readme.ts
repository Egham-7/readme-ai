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
};
