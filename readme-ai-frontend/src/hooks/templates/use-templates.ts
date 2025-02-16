import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@clerk/clerk-react";
import type { TemplatesResponse } from "@/services/templates";
import { ApiError } from "@/services/utils";
import templateService from "@/services/templates";

export const useTemplates = (page = 1, pageSize = 10) => {
  const { getToken } = useAuth();
  return useQuery<TemplatesResponse, ApiError>({
    queryKey: ["templates", page, pageSize],
    queryFn: async () => {
      const token = await getToken();
      if (!token)
        throw new ApiError("Authentication required", "AUTH_REQUIRED");
      return templateService.getAllTemplates(token, page, pageSize);
    },
  });
};
