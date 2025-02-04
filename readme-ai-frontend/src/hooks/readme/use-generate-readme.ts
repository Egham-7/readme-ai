import { useMutation } from "@tanstack/react-query";
import {
  type RepoRequestParams,
  type ApiError,
  readmeService,
} from "@/services/readme";

export const useGenerateReadme = () =>
  useMutation<string, ApiError, RepoRequestParams>({
    mutationKey: ["generate-readme"],
    mutationFn: (params: RepoRequestParams) =>
      readmeService.generateReadme(params),
  });
