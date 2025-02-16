import { readmeService, type ReadmesResponse } from "@/services/readme";
import { ApiError } from "@/services/utils";
import { useAuth } from "@clerk/clerk-react";
import { useQuery } from "@tanstack/react-query";

export const useUserReadmes = (page = 1, pageSize = 10) => {
  const { getToken, userId } = useAuth();

  return useQuery<ReadmesResponse, ApiError>({
    queryKey: ["readmes", userId, page, pageSize],
    queryFn: async () => {
      const token = await getToken();
      if (!token)
        throw new ApiError("Authentication required", "AUTH_REQUIRED");
      if (!userId) throw new ApiError("User ID required", "USER_ID_REQUIRED");
      return readmeService.getUserReadmes(token, page, pageSize);
    },
    enabled: !!userId,
  });
};
