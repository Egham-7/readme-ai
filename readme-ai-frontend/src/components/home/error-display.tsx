import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import { getErrorMessage } from "@/services/utils";
import { type ApiError } from "@/services/utils";
import { UsageLimitExceeded } from "./usage-limit-exceeded";

interface ErrorDisplayProps {
  error: ApiError;
  message?: string;
}

const ErrorDisplay = ({ error, message }: ErrorDisplayProps) => {
  if (error.errorCode === "RATE_LIMIT_EXCEEDED") {
    return <UsageLimitExceeded retryAfter={60} />;
  }

  if (
    error.errorCode === "INSUFFICIENT_TOKENS" &&
    error.details?.time_remaining
  ) {
    return (
      <UsageLimitExceeded
        retryAfter={error.details?.time_remaining as number}
      />
    );
  }

  return (
    <Alert variant="destructive" className="mb-4">
      <AlertCircle className="h-5 w-5" />
      <AlertTitle className="text-lg font-semibold">
        {message || "Generation Failed"}
      </AlertTitle>
      <AlertDescription className="mt-2">
        <div className="space-y-2">
          <p className="text-base">{getErrorMessage(error)}</p>
          {error.details && (
            <div className="text-sm bg-destructive/10 p-2 rounded-md mt-2">
              <strong>Additional Info:</strong>
              <p className="mt-1 opacity-90">
                {JSON.stringify(error.details, null, 2)}
              </p>
            </div>
          )}
        </div>
      </AlertDescription>
    </Alert>
  );
};

export default ErrorDisplay;
