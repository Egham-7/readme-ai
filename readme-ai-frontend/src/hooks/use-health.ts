import { useQuery } from "@tanstack/react-query";
import { healthService } from "@/services/health";

export const useHealthCheck = () =>
  useQuery({
    queryKey: ["health-check"],
    queryFn: () => healthService.checkHealth(),
  });
