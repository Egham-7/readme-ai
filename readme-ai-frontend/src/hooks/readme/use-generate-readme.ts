import { useMutation } from "@tanstack/react-query";
import {
  type RepoRequestParams,
  type ApiErrorResponse,
} from "@/services/readme";
import { readmeService } from "@/services/readme";

export const useGenerateReadme = () =>
  useMutation<string, ApiErrorResponse, RepoRequestParams>({
    mutationKey: ["generate-readme"],
    mutationFn: (params: RepoRequestParams) =>
      readmeService.generateReadme(params),
  });
