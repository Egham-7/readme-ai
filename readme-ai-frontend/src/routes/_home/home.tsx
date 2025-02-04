import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Check, Copy } from "lucide-react";
import { TemplateSelection } from "@/components/home/template-selection";
import MarkdownPreview from "@/components/markdown-preview";
import { siGithub as Github } from "simple-icons";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import { useForm } from "react-hook-form";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from "@/components/ui/form";
import { useGenerateReadme } from "@/hooks/readme/use-generate-readme";

import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";
import type { ApiErrorResponse } from "@/services/readme";

interface StepHeaderProps {
  currentStep: number;
  className?: string;
}
const formSchema = z.object({
  githubLink: z.string().url("Please enter a valid GitHub URL"),
  templateId: z.string().min(1, "Please select a template").optional(),
});

const LoadingSkeleton = () => (
  <Card className="w-full max-w-4xl mx-auto">
    <CardHeader>
      <div className="h-6 w-48 bg-muted animate-pulse rounded" />
      <div className="h-4 w-96 bg-muted animate-pulse rounded mt-2" />
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="flex justify-end">
        <div className="h-8 w-32 bg-muted animate-pulse rounded" />
      </div>
      <div className="space-y-4">
        <div className="h-8 w-48 bg-muted animate-pulse rounded" />
        <div className="h-96 w-full bg-muted animate-pulse rounded" />
      </div>
    </CardContent>
  </Card>
);

function StepHeader({ currentStep, className }: StepHeaderProps) {
  const steps = ["Select Template", "Enter Repository", "Generated Result"];

  return (
    <div className={cn("w-full max-w-4xl mx-auto mb-8", className)}>
      <h1 className="text-3xl font-bold text-center mb-4 text-foreground">
        Generate GitHub README
      </h1>
      <div className="flex justify-center items-center space-x-4">
        {steps.map((step, index) => (
          <div key={index} className="flex items-center">
            <div
              className={cn(
                "flex items-center justify-center w-8 h-8 rounded-full border-2",
                currentStep === index + 1
                  ? "border-primary bg-primary text-primary-foreground"
                  : "border-muted text-muted-foreground",
              )}
            >
              {index + 1}
            </div>
            <span
              className={cn(
                "ml-2",
                currentStep === index + 1
                  ? "font-medium text-foreground"
                  : "text-muted-foreground",
              )}
            >
              {step}
            </span>
            {index < steps.length - 1 && (
              <div className="w-8 h-px bg-border mx-2" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

const GithubLinkForm = ({
  form,
  onSubmit,
  onBack,
  isLoading,
}: {
  form: ReturnType<typeof useForm<z.infer<typeof formSchema>>>;
  onSubmit: (values: z.infer<typeof formSchema>) => void;
  onBack: () => void;
  isLoading: boolean;
}) =>
  isLoading ? (
    <LoadingSkeleton />
  ) : (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>Enter GitHub Repository Link</CardTitle>
        <CardDescription>
          Provide the link to the GitHub repository you want to generate a
          README for
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="githubLink"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <div className="flex items-center space-x-2">
                      <svg
                        role="img"
                        viewBox="0 0 24 24"
                        width="24"
                        height="24"
                        fill="currentColor"
                      >
                        <path d={Github.path} />
                      </svg>
                      <Input
                        placeholder="https://github.com/username/repo"
                        {...field}
                        className="flex-grow"
                      />
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="flex justify-between">
              <Button type="button" onClick={onBack} variant="outline">
                Back
              </Button>
              <Button type="submit" disabled={isLoading}>
                Generate Markdown
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );

const MarkdownResult = ({
  markdown,
  onStartOver,
  isCopied,
  onCopy,
}: {
  markdown?: string;
  onStartOver: () => void;
  isCopied: boolean;
  onCopy: () => Promise<void>;
}) => {
  if (!markdown || (markdown && markdown.length <= 0)) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>No Content Generated</CardTitle>
          <CardDescription>
            No markdown content was generated. Please try again.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={onStartOver} variant="outline">
            Start Over
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>Generated Markdown</CardTitle>
        <CardDescription>
          Your README markdown has been generated
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex justify-end">
          <Button
            onClick={(e) => {
              e.preventDefault();
              void onCopy();
            }}
            variant="outline"
            size="sm"
            className="flex items-center space-x-2"
          >
            {isCopied ? (
              <>
                <Check className="w-4 h-4" />
                <span>Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span>Copy Markdown</span>
              </>
            )}
          </Button>
        </div>
        <Tabs defaultValue="code">
          <TabsList>
            <TabsTrigger value="code">Markdown Code</TabsTrigger>
            <TabsTrigger value="preview">Preview</TabsTrigger>
          </TabsList>
          <TabsContent value="code">
            <Textarea
              value={markdown}
              readOnly
              className="w-full h-96 font-mono text-sm"
            />
          </TabsContent>
          <TabsContent value="preview">
            <div className="prose max-w-none border rounded-md p-4 h-96 overflow-y-auto">
              <MarkdownPreview content={markdown} />
            </div>
          </TabsContent>
        </Tabs>
        <div className="flex justify-between">
          <Button onClick={onStartOver} variant="outline">
            Start Over
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

// Main component
export function GitHubMarkdownGenerator() {
  const [step, setStep] = useState(1);
  const [templateId, setTemplateId] = useState<string | null>(null);
  const [isCopied, setIsCopied] = useState(false);
  const { toast } = useToast();
  const {
    mutate: generateReadme,
    isPending,
    data: markdownData,
  } = useGenerateReadme();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      githubLink: "",
      templateId: templateId ?? undefined,
    },
  });

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    generateReadme(
      { repo_url: values.githubLink },
      {
        onSuccess: () => {
          setStep(3);
        },
        onError: (error: ApiErrorResponse) => {
          toast({
            title: "Error generating markdown",
            description: error.message.toString(),
            variant: "destructive",
          });
        },
      },
    );
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(markdownData || "");
    setIsCopied(true);
    setTimeout(() => {
      setIsCopied(false);
    }, 2000);
  };

  return (
    <div className="p-8 space-y-8">
      <StepHeader currentStep={step} />

      {step === 1 && (
        <TemplateSelection
          onSelect={(id) => {
            setTemplateId(id);
            setStep(2);
          }}
        />
      )}
      {step === 2 && (
        <GithubLinkForm
          form={form}
          onSubmit={onSubmit}
          onBack={() => {
            setStep(1);
          }}
          isLoading={isPending}
        />
      )}
      {step === 3 && (
        <MarkdownResult
          markdown={markdownData}
          onStartOver={() => {
            setStep(1);
          }}
          isCopied={isCopied}
          onCopy={handleCopy}
        />
      )}
    </div>
  );
}

export const Route = createFileRoute("/_home/home")({
  component: GitHubMarkdownGenerator,
});
