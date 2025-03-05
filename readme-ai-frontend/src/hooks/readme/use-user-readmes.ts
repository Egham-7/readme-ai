import { readmeService, type ReadmesResponse } from "@/services/readme";
import { ApiError } from "@/services/utils";
import { useAuth } from "@clerk/clerk-react";
import { useQuery } from "@tanstack/react-query";

export const useUserReadmes = (page = 1, pageSize = 10, query = "") => {
  const { getToken, userId } = useAuth();

  return useQuery<ReadmesResponse, ApiError>({
    queryKey: ["readmes", userId, page, pageSize, query],
    queryFn: async () => {
      const token = await getToken();
      if (!token)
        throw new ApiError("Authentication required", "AUTH_REQUIRED");
      if (!userId) throw new ApiError("User ID required", "USER_ID_REQUIRED");
      return readmeService.getUserReadmes(token, query, page, pageSize);
    },
    enabled: !!userId,
  });
};
