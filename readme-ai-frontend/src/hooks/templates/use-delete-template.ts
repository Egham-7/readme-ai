import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/clerk-react";
import { ApiError } from "@/services/utils";
import templateService from "@/services/templates";

export const useDeleteTemplate = () => {
  const queryClient = useQueryClient();
  const { getToken } = useAuth();
  return useMutation<void, ApiError, number>({
    mutationFn: async (id) => {
      const token = await getToken();
      if (!token)
        throw new ApiError("Authentication required", "AUTH_REQUIRED");
      return templateService.deleteTemplate(id, token);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["templates"] });
    },
  });
};
