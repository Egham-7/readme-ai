import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";
import BlockEditor from "@/components/template-editor/block-editor";
import RawEditor from "@/components/template-editor/raw-editor";
import { useCreateTemplate } from "@/hooks/readme/use-templates";
import { useNavigate } from "@tanstack/react-router";
import { ApiError } from "@/services/readme";
import { type BlockContent } from "@/components/template-editor/markdown-blocks";

type EditorMode = "blocks" | "raw";

function CreateTemplates() {
  const [mode, setMode] = useState<EditorMode>("blocks");
  const [blocks, setBlocks] = useState<BlockContent[]>([]);

  const { toast } = useToast();

  const { mutateAsync: createTemplate } = useCreateTemplate();
  const navigate = useNavigate();

  const handleSave = async (markdown: string) => {
    try {
      await createTemplate({
        content: markdown,
      });
      toast({
        title: "Template Saved",
        description: "Your template has been saved successfully",
      });
      await navigate({ to: "/home" });
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        toast({
          title: "Failed to save template",
          description: err.message,
        });
      } else {
        toast({
          title: "Failed to save template",
          description: "Please try again later",
        });
      }
    }
  };

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
            setBlocks={setBlocks}
          />
        </TabsContent>

        <TabsContent value="raw" className="flex-1">
          <RawEditor onSave={handleSave} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default CreateTemplates;
