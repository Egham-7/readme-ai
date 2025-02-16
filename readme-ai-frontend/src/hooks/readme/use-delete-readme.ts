import { useMutation, useQueryClient } from "@tanstack/react-query";
import { readmeService } from "@/services/readme";
import { useAuth } from "@clerk/clerk-react";
import { ApiError } from "@/services/utils";
import { useToast } from "@/hooks/use-toast";

export const useDeleteReadme = () => {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: async (readmeId: number) => {
      const token = await getToken();
      if (!token) {
        throw new ApiError("Authentication required", "AUTH_REQUIRED");
      }
      return readmeService.deleteReadme(token, readmeId);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["readmes"] });
      toast({
        title: "README deleted successfully",
        description: "The README has been removed",
      });
    },
    onError: (error) => {
      toast({
        variant: "destructive",
        title: "Failed to delete README",
        description:
          error instanceof Error ? error.message : "An unknown error occurred",
      });
    },
  });
};
