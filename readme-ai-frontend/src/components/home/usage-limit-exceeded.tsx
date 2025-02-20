import { useState, useEffect } from "react";
import { AlertCircle } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";

interface UsageLimitExceededProps {
  retryAfter: number;
}

export function UsageLimitExceeded({ retryAfter }: UsageLimitExceededProps) {
  const [timeRemaining, setTimeRemaining] = useState(retryAfter);

  useEffect(() => {
    if (timeRemaining <= 0) return;

    const timer = setInterval(() => {
      setTimeRemaining((prevTime) => prevTime - 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [timeRemaining]);

  const minutes = Math.floor(timeRemaining / 60);
  const seconds = timeRemaining % 60;

  return (
    <Alert variant="destructive" className="max-w-md mx-auto">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Usage Limit Exceeded</AlertTitle>
      <AlertDescription>
        <p className="mt-2 mb-4">
          You&apos;ve reached your token or usage limit. Please wait before
          trying again.
        </p>
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Time until retry:</span>
            <span>
              {minutes.toString().padStart(2, "0")}:
              {seconds.toString().padStart(2, "0")}
            </span>
          </div>
          <Progress
            value={(timeRemaining / retryAfter) * 100}
            className="h-2"
          />
        </div>
      </AlertDescription>
    </Alert>
  );
}
