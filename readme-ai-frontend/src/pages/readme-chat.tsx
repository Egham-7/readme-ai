import { useState, useEffect, useMemo } from "react";
import { Header } from "@/components/readme-chat/header";
import { ChatInterface } from "@/components/readme-chat/chat-interface";
import MarkdownPreview from "@/components/markdown-preview";
import { useToast } from "@/hooks/use-toast";
import { Route } from "@/routes/_home/readmes/chat/$readmeId";
import { useReadme } from "@/hooks/readme/use-readme";
import { useUpdateReadme } from "@/hooks/readme/use-update-readme";
import ErrorDisplay from "@/components/home/error-display";
import ReadmeChatSkeleton from "@/components/readme-chat/readme-chat-skeleton";

export function ReadmeChat() {
  const { readmeId } = Route.useParams();
  const numericReadmeId = parseInt(readmeId);
  const { toast } = useToast();

  // Fetch readme data
  const { data: readme, isLoading, error } = useReadme(numericReadmeId);

  // Get update mutation
  const updateReadmeMutation = useUpdateReadme();

  // Get the latest version content and number
  const latestVersion = useMemo(() => {
    if (!readme?.versions?.length) return null;

    return [...readme.versions].sort(
      (a, b) => b.version_number - a.version_number,
    )[0];
  }, [readme?.versions]);

  // Only track edited content as state
  const [editedContent, setEditedContent] = useState<string>("");

  // Initialize edited content when latest version loads or changes
  useEffect(() => {
    if (latestVersion?.content) {
      setEditedContent(latestVersion.content);
    }
  }, [latestVersion]);

  const handleSave = () => {
    updateReadmeMutation.mutate({
      readmeId: numericReadmeId,
      content: editedContent,
    });
  };

  const copyToClipboard = () => {
    navigator.clipboard
      .writeText(editedContent)
      .then(() => {
        toast({
          title: "Copied to clipboard",
          description: "README content has been copied to your clipboard.",
        });
      })
      .catch((err) => {
        toast({
          title: "Failed to copy",
          description: String(err),
          variant: "destructive",
        });
      });
  };

  // Handle loading state
  if (isLoading) {
    return <ReadmeChatSkeleton />;
  }

  // Handle error state
  if (error) {
    return <ErrorDisplay error={error} message="Failed to load README" />;
  }

  // Handle case when README doesn't exist
  if (!readme || !latestVersion) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p className="text-muted-foreground">
          README not found or has no versions
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col">
      <Header
        currentVersion={latestVersion.version_number}
        onSave={handleSave}
        onCopy={copyToClipboard}
      />
      <div className="flex flex-1 overflow-hidden">
        <ChatInterface
          markdown={editedContent}
          onUpdateReadme={setEditedContent}
        />
        <div className="flex-1 border-l overflow-hidden">
          <MarkdownPreview
            content={editedContent}
            onChange={setEditedContent}
          />
        </div>
      </div>
    </div>
  );
}
