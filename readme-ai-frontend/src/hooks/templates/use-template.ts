import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@clerk/clerk-react";
import type { Template } from "@/services/templates";
import { ApiError } from "@/services/utils";
import templateService from "@/services/templates";

export const useTemplate = (id: number) => {
  const { getToken } = useAuth();
  return useQuery<Template, ApiError>({
    queryKey: ["templates", id],
    queryFn: async () => {
      const token = await getToken();
      if (!token)
        throw new ApiError("Authentication required", "AUTH_REQUIRED");
      return templateService.getTemplate(id, token);
    },
  });
};
