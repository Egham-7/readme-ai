import { readmeService } from "@/services/readme";
import { useQuery } from "@tanstack/react-query";

export const useHealthCheck = () =>
  useQuery({
    queryKey: ["health-check"],
    queryFn: () => readmeService.checkHealth(),
  });
