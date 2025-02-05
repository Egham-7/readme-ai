import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";
import BlockEditor from "@/components/template-editor/block-editor";
import RawEditor from "@/components/template-editor/raw-editor";

type EditorMode = "blocks" | "raw";

function CreateTemplates() {
  const [mode, setMode] = useState<EditorMode>("blocks");
  const { toast } = useToast();

  const handleSave = (_markdown: string) => {
    toast({
      title: "Template Saved",
      description: "Your template has been saved successfully",
    });
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
          <BlockEditor onSave={handleSave} />
        </TabsContent>

        <TabsContent value="raw" className="flex-1">
          <RawEditor onSave={handleSave} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default CreateTemplates;
