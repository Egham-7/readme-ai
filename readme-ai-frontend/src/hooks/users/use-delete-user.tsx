import { useQueryClient } from "@tanstack/react-query";
import { userService } from "@/services/users";
import { useMutation } from "@tanstack/react-query";

export const useDeleteUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => userService.deleteUser(id),
    onSuccess: async (_, deletedId) => {
      await queryClient.invalidateQueries({ queryKey: ["users"] });
      queryClient.removeQueries({
        queryKey: ["users", deletedId],
      });
    },
  });
};
