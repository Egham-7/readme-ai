import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/clerk-react";
import type { Template, UpdateTemplatePayload } from "@/services/templates";
import { ApiError } from "@/services/utils";
import templateService from "@/services/templates";

export const useUpdateTemplate = () => {
  const queryClient = useQueryClient();
  const { getToken } = useAuth();
  return useMutation<
    Template,
    ApiError,
    {
      id: number;
      payload: UpdateTemplatePayload;
    }
  >({
    mutationFn: async ({ id, payload }) => {
      const token = await getToken();
      if (!token)
        throw new ApiError("Authentication required", "AUTH_REQUIRED");
      return templateService.updateTemplate(id, payload, token);
    },
    onSuccess: async (_, variables) => {
      await queryClient.invalidateQueries({ queryKey: ["templates"] });
      await queryClient.invalidateQueries({
        queryKey: ["templates", variables.id],
      });
    },
  });
};
