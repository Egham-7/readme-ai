import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CheckCircle, Circle, CircleDot, XCircle } from "lucide-react";
import { type ProgressUpdate } from "@/services/readme";

interface ProgressIndicatorProps {
  progress: ProgressUpdate | null;
  onCancel: () => void;
}

const stages = ["init", "analysis", "template", "generation"] as const;

export function ProgressIndicator({
  progress,
  onCancel,
}: ProgressIndicatorProps) {
  if (!progress) return null;

  const getStepNumber = (stage: string) =>
    stages.indexOf(stage as (typeof stages)[number]) + 1;

  const currentStep = getStepNumber(progress.stage);

  const getStageIcon = (index: number) => {
    if (index < currentStep - 1)
      return <CheckCircle className="w-6 h-6 text-primary" />;
    if (index === currentStep - 1)
      return <CircleDot className="w-6 h-6 text-primary animate-pulse" />;
    return <Circle className="w-6 h-6 text-muted-foreground" />;
  };

  return (
    <div className="space-y-6 w-full max-w-xl mx-auto bg-card p-6 rounded-lg shadow-md">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Badge
            variant="secondary"
            className="text-sm font-semibold px-3 py-1"
          >
            Step {currentStep} of {stages.length}
          </Badge>
          <Button
            variant="destructive"
            size="sm"
            onClick={onCancel}
            className="flex items-center gap-2"
          >
            <XCircle className="w-4 h-4" />
            Cancel
          </Button>
        </div>
        <span className="text-2xl font-bold text-primary">
          {Math.round(progress.progress * 100)}%
        </span>
      </div>

      <Progress value={progress.progress * 100} className="h-2" />
      <p className="text-sm text-muted-foreground italic">{progress.message}</p>

      <div className="flex justify-between">
        {stages.map((stage, index) => (
          <div key={stage} className="flex flex-col items-center">
            {getStageIcon(index)}
            <span className="text-xs mt-1 capitalize">{stage}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
