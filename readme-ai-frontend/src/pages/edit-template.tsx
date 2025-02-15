import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { useState, useEffect } from "react";
import BlockEditor from "@/components/template-editor/block-editor";
import RawEditor from "@/components/template-editor/raw-editor";
import { useTemplate, useUpdateTemplate } from "@/hooks/readme/use-templates";
import { useNavigate } from "@tanstack/react-router";
import { ApiError } from "@/services/utils";
import {
  type BlockContent,
  parseMarkdownToBlocks,
} from "@/components/template-editor/markdown-blocks";
import { Route } from "@/routes/_home/templates/update/$templateId";

type EditorMode = "blocks" | "raw";

function EditTemplate() {
  const [mode, setMode] = useState<EditorMode>("blocks");
  const [blocks, setBlocks] = useState<BlockContent[]>([]);
  const { toast } = useToast();

  const { templateId } = Route.useParams();

  const navigate = useNavigate();

  const { data: template, isLoading } = useTemplate(Number(templateId));
  const { mutateAsync: updateTemplate } = useUpdateTemplate();

  useEffect(() => {
    if (template?.content) {
      const parsedBlocks = parseMarkdownToBlocks(template.content);
      setBlocks(parsedBlocks);
    }
  }, [template]);

  const handleSave = async (markdown: string) => {
    try {
      await updateTemplate({
        id: Number(templateId),
        payload: {
          content: markdown,
        },
      });

      toast({
        title: "Template Updated",
        description: "Your template has been updated successfully",
      });

      await navigate({ to: "/home" });
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        toast({
          title: "Failed to update template",
          description: err.message,
        });
      } else {
        toast({
          title: "Failed to update template",
          description: "Please try again later",
        });
      }
    }
  };

  const handleBlocksChange = (newBlocks: BlockContent[]) => {
    setBlocks(newBlocks);
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="h-screen flex flex-col bg-background">
      <Tabs
        value={mode}
        onValueChange={(value) => setMode(value as EditorMode)}
        className="w-full h-full space-y-6"
      >
        <TabsList className="w-full justify-start border-b border-border">
          <TabsTrigger value="blocks">Block Editor</TabsTrigger>
          <TabsTrigger value="raw">Raw Markdown</TabsTrigger>
        </TabsList>
        <TabsContent value="blocks" className="flex-1">
          <BlockEditor
            onSave={handleSave}
            blocks={blocks}
            onBlocksChange={handleBlocksChange}
          />
        </TabsContent>
        <TabsContent value="raw" className="flex-1">
          <RawEditor onSave={handleSave} markdown={template?.content} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default EditTemplate;
