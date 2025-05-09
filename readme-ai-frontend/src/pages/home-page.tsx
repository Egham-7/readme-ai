import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { useGenerateReadme } from "@/hooks/readme/use-generate-readme";
import { useToast } from "@/hooks/use-toast";
import { type ApiError } from "@/services/utils";
import { getErrorMessage } from "@/services/utils";
import { z } from "zod";
import type { Step } from "@/components/home/step-header";
import StepHeader from "@/components/home/step-header";
import { TemplateSelection } from "@/components/home/template-selection";
import GithubLinkForm from "@/components/home/github-link-form";
import MarkdownResult from "@/components/home/markdown-result";
import { ProgressIndicator } from "@/components/progress-indicator";

const COPY_TIMEOUT = 2000;

const formSchema = z.object({
  githubLink: z.string().url("Please enter a valid GitHub repository URL"),
  templateId: z.number().optional(),
});

export type FormSchema = z.infer<typeof formSchema>;

export function HomePage() {
  const [step, setStep] = useState<Step>(1);
  const [templateId, setTemplateId] = useState<number | undefined>(undefined);
  const [isCopied, setIsCopied] = useState(false);
  const [error, setError] = useState<ApiError | undefined>();
  const { toast } = useToast();

  const {
    mutate: generateReadme,
    isPending,
    data: markdownData,
    progress,
    cancel,
  } = useGenerateReadme();

  const form = useForm<FormSchema>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      githubLink: "",
      templateId: templateId ?? undefined,
    },
  });

  const onSubmit = (values: FormSchema) => {
    setError(undefined);
    generateReadme(
      { repo_url: values.githubLink, template_id: templateId },
      {
        onSuccess: () => {
          setStep(3);
          toast({
            title: "Success!",
            description: "Your README has been generated successfully.",
          });
        },
        onError: (error: ApiError) => {
          setError(error);
          setStep(3);
          toast({
            title: "Generation Failed",
            description: getErrorMessage(error),
            variant: "destructive",
          });
        },
      },
    );
  };

  const handleCopy = async () => {
    if (!markdownData) return;
    await navigator.clipboard.writeText(markdownData);
    setIsCopied(true);
    toast({
      title: "Copied!",
      description: "README markdown copied to clipboard",
    });
    setTimeout(() => {
      setIsCopied(false);
    }, COPY_TIMEOUT);
  };

  return (
    <div className="p-4 md:p-8 space-y-6 md:space-y-8">
      <StepHeader currentStep={step} />
      {step === 1 && (
        <TemplateSelection
          onSelect={(id) => {
            setTemplateId(id);
            setStep(2);
          }}
        />
      )}
      {step === 2 && !isPending && (
        <GithubLinkForm
          form={form}
          onSubmit={onSubmit}
          onBack={() => {
            setStep(1);
          }}
        />
      )}

      {isPending && (
        <div className="mt-8">
          <ProgressIndicator progress={progress} onCancel={cancel} />
        </div>
      )}

      {step === 3 && !isPending && (
        <MarkdownResult
          markdown={markdownData ?? ""}
          error={error}
          onStartOver={() => {
            form.reset();
            setError(undefined);
            setStep(1);
          }}
          isCopied={isCopied}
          onCopy={handleCopy}
          handleSubmit={form.handleSubmit(onSubmit)}
        />
      )}
    </div>
  );
}
