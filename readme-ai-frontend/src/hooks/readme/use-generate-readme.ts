import { useMutation } from "@tanstack/react-query";
import {
  type RepoRequestParams,
  type ApiError,
  readmeService,
} from "@/services/readme";
import { useAuth } from "@clerk/clerk-react";

export const useGenerateReadme = () => {
  const { getToken } = useAuth();

  return useMutation<string, ApiError, RepoRequestParams>({
    mutationKey: ["generate-readme"],
    mutationFn: async (params: RepoRequestParams) => {
      const token = await getToken();
      if (!token) {
        throw new Error("Token not available");
      }
      return readmeService.generateReadme(params, token);
    },
    gcTime: 0, // Disable garbage collection
  });
};
