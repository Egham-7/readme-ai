import { useAuth } from "@clerk/clerk-react";
import { useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";

export const useAuthGuard = () => {
  const { isLoaded, isSignedIn } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      void navigate({ to: "/" });
    }
  }, [isLoaded, isSignedIn, navigate]);

  return {
    isAuthenticated: isSignedIn,
    isLoading: !isLoaded,
  };
};
