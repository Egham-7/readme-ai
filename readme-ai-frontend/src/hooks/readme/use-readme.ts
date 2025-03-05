import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@clerk/clerk-react";
import { type ApiError } from "@/services/utils";
import { readmeService, type Readme } from "@/services/readme";

export const useReadme = (readmeId: number) => {
  const { getToken } = useAuth();

  return useQuery<Readme, ApiError>({
    queryKey: ["readme", readmeId],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error("Authentication required");
      return readmeService.getReadme(token, readmeId);
    },
    enabled: !!readmeId,
  });
};
