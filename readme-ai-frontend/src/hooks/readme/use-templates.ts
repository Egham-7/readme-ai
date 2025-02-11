import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/clerk-react";
import type {
  Template,
  CreateTemplatePayload,
  UpdateTemplatePayload,
  TemplatesResponse,
} from "@/services/readme";
import { ApiError } from "@/services/readme";
import { readmeService } from "@/services/readme";

export const useTemplates = (page = 1, pageSize = 10) => {
  const { getToken } = useAuth();

  return useQuery<TemplatesResponse, ApiError>({
    queryKey: ["templates", page, pageSize],
    queryFn: async () => {
      const token = await getToken();
      if (!token)
        throw new ApiError("Authentication required", "AUTH_REQUIRED");
      return readmeService.getAllTemplates(token, page, pageSize);
    },
  });
};

export const useTemplate = (id: number) => {
  const { getToken } = useAuth();

  return useQuery<Template, ApiError>({
    queryKey: ["templates", id],
    queryFn: async () => {
      const token = await getToken();
      if (!token)
        throw new ApiError("Authentication required", "AUTH_REQUIRED");
      return readmeService.getTemplate(id, token);
    },
  });
};

export const useCreateTemplate = () => {
  const queryClient = useQueryClient();
  const { getToken } = useAuth();

  return useMutation<Template, ApiError, CreateTemplatePayload>({
    mutationFn: async (payload) => {
      const token = await getToken();
      if (!token)
        throw new ApiError("Authentication required", "AUTH_REQUIRED");
      return readmeService.createTemplate(payload, token);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["templates"] });
    },
  });
};

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
      return readmeService.updateTemplate(id, payload, token);
    },
    onSuccess: async (_, variables) => {
      await queryClient.invalidateQueries({ queryKey: ["templates"] });
      await queryClient.invalidateQueries({
        queryKey: ["templates", variables.id],
      });
    },
  });
};

export const useDeleteTemplate = () => {
  const queryClient = useQueryClient();
  const { getToken } = useAuth();

  return useMutation<void, ApiError, number>({
    mutationFn: async (id) => {
      const token = await getToken();
      if (!token)
        throw new ApiError("Authentication required", "AUTH_REQUIRED");
      return readmeService.deleteTemplate(id, token);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["templates"] });
    },
  });
};

export const useUserTemplates = (page = 1, pageSize = 10) => {
  const { getToken, userId } = useAuth();

  return useQuery<TemplatesResponse, ApiError>({
    queryKey: ["user-templates", userId, page, pageSize],
    queryFn: async () => {
      const token = await getToken();
      if (!token)
        throw new ApiError("Authentication required", "AUTH_REQUIRED");
      if (!userId) throw new ApiError("User ID required", "USER_ID_REQUIRED");
      return readmeService.getUserTemplates(userId, token, page, pageSize);
    },
    enabled: !!userId,
  });
};
