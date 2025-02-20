import { useUser as useClerkUser } from "@clerk/clerk-react";
import { userService } from "@/services/users";
import { type CombinedUser } from "@/services/users";
import { useQuery } from "@tanstack/react-query";
import { ApiError } from "@/services/utils";

export const useUser = () => {
  const { user: clerkUser } = useClerkUser();

  if (!clerkUser) {
    throw new ApiError("Not authorized", "Forbidden");
  }
  const userId = clerkUser.id;

  return useQuery({
    queryKey: ["users", userId],
    queryFn: async () => {
      const dbUser = await userService.getUserById(userId);

      if (!clerkUser) {
        throw new ApiError(
          "Failed to fetch user",
          "USER_NOT_FOUND",
          { status_code: 404, user_id: userId },
          new Date().toISOString(),
        );
      }

      const combinedUser: CombinedUser = {
        ...dbUser,
        clerkUser,
      };

      return combinedUser;
    },
    enabled: !!userId && !!clerkUser,
  });
};
