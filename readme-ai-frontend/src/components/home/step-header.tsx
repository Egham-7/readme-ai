import { cn } from "@/lib/utils";

export type Step = 1 | 2 | 3;

interface StepHeaderProps {
  currentStep: Step;
  className?: string;
}

const STEPS = [
  "Select Template",
  "Enter Repository",
  "Generated Result",
] as const;

const StepHeader = ({ currentStep, className }: StepHeaderProps) => (
  <div className={cn("w-full max-w-4xl mx-auto mb-4 md:mb-8 px-4", className)}>
    <h1 className="text-2xl md:text-3xl font-bold text-center mb-4 text-foreground">
      Generate GitHub README
    </h1>
    <div className="flex flex-wrap justify-center items-center gap-4 md:gap-2">
      {STEPS.map((step, index) => (
        <div key={index} className="flex items-center">
          <div
            className={cn(
              "flex items-center justify-center w-6 md:w-8 h-6 md:h-8 rounded-full border-2",
              currentStep === index + 1
                ? "border-primary bg-primary text-primary-foreground"
                : "border-muted text-muted-foreground",
            )}
          >
            {index + 1}
          </div>
          <span
            className={cn(
              "ml-2 text-sm md:text-base",
              currentStep === index + 1
                ? "font-medium text-foreground"
                : "text-muted-foreground",
            )}
          >
            {step}
          </span>
          {index < STEPS.length - 1 && (
            <div className="hidden md:block w-8 h-px bg-border mx-2" />
          )}
        </div>
      ))}
    </div>
  </div>
);

export default StepHeader;
