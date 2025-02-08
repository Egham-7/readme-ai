import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  readmeService,
  Template,
  CreateTemplatePayload,
  UpdateTemplatePayload,
} from "@/services/readme";

export const useTemplates = () => {
  return useQuery<Template[]>({
    queryKey: ["templates"],
    queryFn: () => readmeService.getAllTemplates(),
  });
};

export const useTemplate = (id: number) => {
  return useQuery<Template>({
    queryKey: ["templates", id],
    queryFn: () => readmeService.getTemplate(id),
  });
};

export const useCreateTemplate = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateTemplatePayload) =>
      readmeService.createTemplate(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["templates"] });
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
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["templates"] });
      queryClient.invalidateQueries({ queryKey: ["templates", variables.id] });
    },
  });
};

export const useDeleteTemplate = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => readmeService.deleteTemplate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["templates"] });
    },
  });
};
