import { getErrorAction } from "@/services/templates";
import { Tabs, TabsList, TabsContent, TabsTrigger } from "../ui/tabs";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "../ui/card";
import { Button } from "../ui/button";
import ErrorDisplay from "./error-display";
import { RefreshCw, Check, Copy } from "lucide-react";
import { Textarea } from "../ui/textarea";
import MarkdownPreview from "../markdown-preview";
import { type ApiError } from "@/services/utils";

interface MarkdownResultProps {
  markdown?: string;
  error?: ApiError;
  onStartOver: () => void;
  isCopied: boolean;
  onCopy: () => Promise<void>;
  handleSubmit: () => void;
}

const MarkdownResult = ({
  markdown,
  error,
  onStartOver,
  isCopied,
  onCopy,
  handleSubmit,
}: MarkdownResultProps) => {
  if (error) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>README Generation Failed</CardTitle>
          <CardDescription>
            We encountered an issue while generating your README
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <ErrorDisplay error={error} />
          <div className="flex flex-col md:flex-row gap-4 md:justify-between">
            <Button
              onClick={onStartOver}
              variant="outline"
              className="w-full md:w-auto"
            >
              Start Over
            </Button>
            <Button
              onClick={handleSubmit}
              variant="default"
              className="w-full md:w-auto flex items-center justify-center gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              {getErrorAction(error)}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!markdown || markdown.length <= 0) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardHeader>
          <CardTitle>No Content Generated</CardTitle>
          <CardDescription>
            The README generation process didn't produce any content. Let's try
            again.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button
            onClick={onStartOver}
            variant="outline"
            className="w-full md:w-auto"
          >
            Start Over
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>README Generated Successfully</CardTitle>
        <CardDescription>
          Your README is ready! Preview it below or copy the markdown to use it
          in your repository.
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
                <Check className="h-4 w-4" />
                <span>Copied to Clipboard</span>
              </>
            ) : (
              <>
                <Copy className="h-4 w-4" />
                <span>Copy Markdown</span>
              </>
            )}
          </Button>
        </div>
        <Tabs defaultValue="preview" className="w-full">
          <TabsList className="w-full md:w-auto">
            <TabsTrigger value="preview" className="flex-1 md:flex-none">
              Live Preview
            </TabsTrigger>
            <TabsTrigger value="code" className="flex-1 md:flex-none">
              Markdown Source
            </TabsTrigger>
          </TabsList>
          <TabsContent value="code">
            <Textarea
              value={markdown}
              readOnly
              className="w-full h-96 font-mono text-sm"
            />
          </TabsContent>
          <TabsContent value="preview">
            <div className="prose max-w-none border rounded-md p-4 h-96 overflow-y-auto dark:prose-invert">
              <MarkdownPreview content={markdown} />
            </div>
          </TabsContent>
        </Tabs>
        <div className="flex flex-col md:flex-row gap-4 md:justify-between">
          <Button
            onClick={onStartOver}
            variant="outline"
            className="w-full md:w-auto"
          >
            Generate Another
          </Button>
          <Button
            onClick={handleSubmit}
            variant="secondary"
            className="w-full md:w-auto flex items-center justify-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Regenerate README
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default MarkdownResult;
