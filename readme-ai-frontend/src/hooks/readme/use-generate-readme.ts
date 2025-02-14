import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useAuth } from "@clerk/clerk-react";
import {
  API_BASE_URL,
  ApiError,
  type ProgressUpdate,
  type RepoRequestParams,
} from "@/services/readme";

export const useGenerateReadme = () => {
  const { getToken } = useAuth();
  const [progress, setProgress] = useState<ProgressUpdate | null>(null);

  const mutation = useMutation<string, ApiError, RepoRequestParams>({
    mutationFn: async (params: RepoRequestParams) => {
      const token = await getToken();
      if (!token)
        throw new ApiError("Authentication required", "AUTH_REQUIRED");

      return new Promise<string>((resolve, reject) => {
        const eventSource = new EventSource(
          `${API_BASE_URL}/generate-readme?${new URLSearchParams({
            repo_url: params.repo_url,
            ...(params.template_id && {
              template_id: params.template_id.toString(),
            }),
            token,
          })}`,
        );

        eventSource.addEventListener("progress", (event: MessageEvent) => {
          setProgress(JSON.parse(event.data));
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
      });
    },
  });

  return {
    ...mutation,
    progress,
  };
};
