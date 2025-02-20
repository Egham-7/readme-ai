import { useQueryClient } from "@tanstack/react-query";
import { type UserUpdate } from "@/services/users";
import { userService } from "@/services/users";
import { useMutation } from "@tanstack/react-query";

export const useUpdateUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UserUpdate }) =>
      userService.updateUser(id, data),
    onSuccess: async (updatedUser) => {
      await queryClient.invalidateQueries({ queryKey: ["users"] });
      await queryClient.invalidateQueries({
        queryKey: ["users", updatedUser.id],
      });
    },
  });
};
