import type { DragEndEvent } from "@dnd-kit/core";
import { DndContext, closestCenter } from "@dnd-kit/core";
import { arrayMove } from "@dnd-kit/sortable";
import { useState } from "react";
import Preview from "@/components/template-editor/preview";
import Sidebar from "@/components/template-editor/sidebar";
import { createFileRoute } from "@tanstack/react-router";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import MarkdownPreview from "@/components/markdown-preview";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

type EditorMode = "blocks" | "raw";

function BlockEditor({ onSave }: { onSave: (markdown: string) => void }) {
  const [blocks, setBlocks] = useState<string[]>([]);

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over) return;

    if (over.id === "preview") {
      const blockId = active.id.toString().split("-")[1];
      const uniqueId = `${blockId}-${Date.now().toString()}`;
      setBlocks((items) => [...items, uniqueId]);
      return;
    }

    const activeId = active.id.toString();
    const overId = over.id.toString();

    if (activeId !== overId) {
      setBlocks((items) => {
        const oldIndex = items.indexOf(activeId);
        const newIndex = items.indexOf(overId);
        return arrayMove(items, oldIndex, newIndex);
      });
    }
  };

  const handleBlockAdd = (id: string) => {
    setBlocks((items) => [...items, id]);
  };

  return (
    <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <div className="flex h-full flex-col">
        <div className="flex-1 flex">
          <Sidebar onBlockAdd={handleBlockAdd} />
          <Preview blocks={blocks} setBlocks={setBlocks} onSave={onSave} />
        </div>
      </div>
    </DndContext>
  );
}

function RawEditor({ onSave }: { onSave: (markdown: string) => void }) {
  const [rawMarkdown, setRawMarkdown] = useState("");

  return (
    <div className="h-full flex flex-col bg-background">
      <div className="flex justify-end p-4">
        <Button
          onClick={() => {
            onSave(rawMarkdown);
          }}
        >
          Save Template
        </Button>
      </div>
      <div className="grid grid-cols-2 gap-4 flex-1 p-4">
        <Textarea
          value={rawMarkdown}
          onChange={(e) => {
            setRawMarkdown(e.target.value);
          }}
          className="h-full font-mono resize-none p-4 bg-card border-border"
          placeholder="Enter your markdown here..."
        />
        <div className="border border-border rounded-lg p-4 overflow-auto bg-card">
          <MarkdownPreview content={rawMarkdown} />
        </div>
      </div>
    </div>
  );
}

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
    <div className="h-screen flex flex-col bg-background ">
      <Tabs
        value={mode}
        onValueChange={(value) => {
          setMode(value as EditorMode);
        }}
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

export const Route = createFileRoute("/_home/templates/create/")({
  component: CreateTemplates,
});
