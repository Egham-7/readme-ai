import { useMutation, useQueryClient } from "@tanstack/react-query";
import { readmeService } from "@/services/readme";
import { useAuth } from "@clerk/clerk-react";
import { type ReadmeVersion } from "@/services/readme";
import { ApiError } from "@/services/utils";
import { useToast } from "../use-toast";

export const useUpdateReadme = () => {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: async ({
      readmeId,
      content,
    }: {
      readmeId: number;
      content: string;
    }) => {
      const token = await getToken();

      if (!token) throw new ApiError("No token", "AUTH_REQUIRED");
      return readmeService.updateReadme(token, readmeId, content);
    },
    onSuccess: async (data: ReadmeVersion) => {
      await queryClient.invalidateQueries({ queryKey: ["readmes"] });
      await queryClient.invalidateQueries({
        queryKey: ["readme", data.readme_id],
      });

      toast({
        title: "README updated successfully",
        description: "Your changes have been saved",
      });
    },
    onError: (error) => {
      toast({
        variant: "destructive",
        title: "Failed to update README",
        description:
          error instanceof Error ? error.message : "An unknown error occurred",
      });
    },
  });
};
