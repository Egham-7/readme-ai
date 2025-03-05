import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@clerk/clerk-react";
import type { TemplatesResponse } from "@/services/templates";
import { ApiError } from "@/services/utils";
import templateService from "@/services/templates";

export const useUserTemplates = (page = 1, pageSize = 10, query = "") => {
  const { getToken, userId } = useAuth();
  return useQuery<TemplatesResponse, ApiError>({
    queryKey: ["user-templates", userId, page, pageSize, query],
    queryFn: async () => {
      const token = await getToken();
      if (!token)
        throw new ApiError("Authentication required", "AUTH_REQUIRED");
      if (!userId) throw new ApiError("User ID required", "USER_ID_REQUIRED");
      return templateService.getUserTemplates(
        userId,
        token,
        page,
        pageSize,
        query,
      );
    },
    enabled: !!userId,
  });
};
