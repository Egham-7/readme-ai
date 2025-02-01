import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
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
import { Github, Loader2, Check, Copy } from "lucide-react";
import { TemplateSelection } from "@/components/home/template-selection";
import MarkdownPreview from "@/components/markdown-preview";

import { cn } from "@/lib/utils";

type GenerateMarkdownParams = {
  githubLink: string;
  templateId: string;
};

type StepHeaderProps = {
  currentStep: number;
  className?: string;
};

export function StepHeader({ currentStep, className }: StepHeaderProps) {
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
  githubLink,
  onLinkChange,
  onSubmit,
  onBack,
  isLoading,
}: {
  githubLink: string;
  onLinkChange: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  onBack: () => void;
  isLoading: boolean;
}) => (
  <Card className="w-full max-w-4xl mx-auto">
    <CardHeader>
      <CardTitle>Enter GitHub Repository Link</CardTitle>
      <CardDescription>
        Provide the link to the GitHub repository you want to generate a README
        for
      </CardDescription>
    </CardHeader>
    <CardContent>
      <form onSubmit={onSubmit} className="space-y-4">
        <div className="flex items-center space-x-2">
          <Github className="w-5 h-5 text-gray-500" />
          <Input
            type="url"
            placeholder="https://github.com/username/repo"
            value={githubLink}
            onChange={(e) => onLinkChange(e.target.value)}
            required
            className="flex-grow"
          />
        </div>
        <div className="flex justify-between">
          <Button type="button" onClick={onBack} variant="outline">
            Back
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              "Generate Markdown"
            )}
          </Button>
        </div>
      </form>
    </CardContent>
  </Card>
);

const MarkdownResult = ({
  markdown,
  onStartOver,
  isCopied,
  onCopy,
}: {
  markdown: string;
  onStartOver: () => void;
  isCopied: boolean;
  onCopy: () => void;
}) => (
  <Card className="w-full max-w-4xl mx-auto">
    <CardHeader>
      <CardTitle>Generated Markdown</CardTitle>
      <CardDescription>Your README markdown has been generated</CardDescription>
    </CardHeader>
    <CardContent className="space-y-4">
      <div className="flex justify-end">
        <Button
          onClick={onCopy}
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

// API function
const generateMarkdown = async ({
  githubLink,
  templateId,
}: GenerateMarkdownParams) => {
  await new Promise((resolve) => setTimeout(resolve, 2000));
  return `# Generated Markdown for ${githubLink}\n\nUsing template: ${templateId}\n\nThis is a placeholder for the generated markdown content.`;
};

// Main component
export function GitHubMarkdownGenerator() {
  const [step, setStep] = useState(1);
  const [templateId, setTemplateId] = useState<string | null>(null);
  const [githubLink, setGithubLink] = useState("");
  const [isCopied, setIsCopied] = useState(false);

  const mutation = useMutation({
    mutationFn: generateMarkdown,
    onSuccess: () => setStep(3),
    onError: (error) => console.error("Error generating markdown:", error),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (templateId && githubLink) {
      mutation.mutate({ githubLink, templateId });
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(mutation.data || "");
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
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
          githubLink={githubLink}
          onLinkChange={setGithubLink}
          onSubmit={handleSubmit}
          onBack={() => setStep(1)}
          isLoading={mutation.isPending}
        />
      )}
      {step === 3 && mutation.data && (
        <MarkdownResult
          markdown={mutation.data}
          onStartOver={() => setStep(1)}
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
