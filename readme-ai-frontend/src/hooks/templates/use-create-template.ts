import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/clerk-react";
import type { Template, CreateTemplatePayload } from "@/services/templates";
import { ApiError } from "@/services/utils";
import templateService from "@/services/templates";

export const useCreateTemplate = () => {
  const queryClient = useQueryClient();
  const { getToken } = useAuth();
  return useMutation<Template, ApiError, CreateTemplatePayload>({
    mutationFn: async (payload) => {
      const token = await getToken();
      if (!token)
        throw new ApiError("Authentication required", "AUTH_REQUIRED");
      return templateService.createTemplate(payload, token);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["templates"] });
    },
  });
};
