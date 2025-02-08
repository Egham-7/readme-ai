import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
  Template,
  CreateTemplatePayload,
  UpdateTemplatePayload,
} from "@/services/readme";
import { readmeService } from "@/services/readme";

export const useTemplates = () =>
  useQuery<Template[]>({
    queryKey: ["templates"],
    queryFn: () => readmeService.getAllTemplates(),
  });

export const useTemplate = (id: number) =>
  useQuery<Template>({
    queryKey: ["templates", id],
    queryFn: () => readmeService.getTemplate(id),
  });

export const useCreateTemplate = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateTemplatePayload) =>
      readmeService.createTemplate(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["templates"] });
    },
  });
};

export const useUpdateTemplate = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: number;
      payload: UpdateTemplatePayload;
    }) => readmeService.updateTemplate(id, payload),
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

  return useMutation({
    mutationFn: (id: number) => readmeService.deleteTemplate(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["templates"] });
    },
  });
};
