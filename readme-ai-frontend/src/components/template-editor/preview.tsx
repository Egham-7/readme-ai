import { useDroppable } from "@dnd-kit/core";
import { SortableContext, useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { BLOCKS } from "./markdown-blocks";
import { TrashIcon } from "lucide-react";
import { Button } from "../ui/button";
import { useState, useEffect } from "react";
import MarkdownPreview from "../markdown-preview";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "../ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "../ui/textarea";
import { type BlockContent } from "./markdown-blocks";

interface PreviewProps {
  blocks: BlockContent[];
  setBlocks: (blocks: BlockContent[]) => void;
  onSave: (markdown: string) => void;
}

interface SortableBlockProps {
  id: string;
  onRemove: (id: string) => void;
  onContentUpdate: (id: string, content: string) => void;
  initialContent?: string;
}

const formatBlockContent = (blockId: string, content: string) => {
  switch (blockId) {
    case "heading1":
      return `# ${content}`;
    case "heading2":
      return `## ${content}`;
    case "heading3":
      return `### ${content}`;
    case "unordered_list":
      return content
        .split("\n")
        .map((line) => `- ${line}`)
        .join("\n");
    case "ordered_list":
      return content
        .split("\n")
        .map((line, i) => {
          const newIdx = i + 1;
          return `${newIdx.toString()}. ${line}`;
        })
        .join("\n");
    case "blockquote":
      return content
        .split("\n")
        .map((line) => `> ${line}`)
        .join("\n");
    case "code":
      return `\`\`\`\n${content}\n\`\`\``;
    case "image":
      return `![${content}](https://example.com/image.jpg)`;
    case "link":
      return `[${content}](https://example.com)`;
    default:
      return content;
  }
};

const BlockEditor = ({
  content,
  onChange,
  onFinish,
}: {
  content: string;
  onChange: (content: string) => void;
  onFinish: () => void;
}) => {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onFinish();
    }
  };

  return (
    <Textarea
      value={content}
      onChange={(e) => {
        onChange(e.target.value);
      }}
      onKeyDown={handleKeyDown}
      placeholder="Enter your content here"
      className="w-full min-h-[100px] bg-background"
    />
  );
};

function SortableBlock({
  id,
  onRemove,
  onContentUpdate,
  initialContent,
}: SortableBlockProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id });
  const baseBlockId = id.split("-").slice(0, -1).join("-");
  const block = BLOCKS.find((b) => b.id === baseBlockId);
  const [rawContent, setRawContent] = useState(initialContent || "");
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (initialContent) {
      onContentUpdate(id, formatBlockContent(block?.id || "", initialContent));
    }
  });

  if (!block) return null;

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  return (
    <div className="group flex flex-col lg:flex-row items-start lg:items-center gap-2 mb-3 lg:mb-2">
      <div
        ref={setNodeRef}
        style={style}
        className="w-full lg:flex-1 bg-card rounded-lg shadow-sm border border-border"
      >
        <div
          className="flex items-center p-3 lg:p-4 border-b border-border"
          {...attributes}
          {...listeners}
        >
          <div className="flex items-center flex-1">
            <block.icon className="w-4 h-4 lg:w-5 lg:h-5 mr-2 text-muted-foreground" />
            <span className="font-medium text-foreground">{block.label}</span>
          </div>
        </div>
        <div className="p-3 lg:p-4">
          {isEditing ? (
            <BlockEditor
              content={rawContent}
              onChange={(newContent) => {
                setRawContent(newContent);
                onContentUpdate(id, formatBlockContent(block.id, newContent));
              }}
              onFinish={() => setIsEditing(false)}
            />
          ) : (
            <div className="prose prose-base lg:prose-sm max-w-none dark:prose-invert">
              <MarkdownPreview
                content={formatBlockContent(block.id, rawContent)}
              />
            </div>
          )}
        </div>
      </div>
      <BlockActions
        isEditing={isEditing}
        onEditToggle={() => setIsEditing(!isEditing)}
        onRemove={() => onRemove(id)}
      />
    </div>
  );
}

const BlockActions = ({
  isEditing,
  onEditToggle,
  onRemove,
}: {
  isEditing: boolean;
  onEditToggle: () => void;
  onRemove: () => void;
}) => (
  <div className="flex flex-row lg:flex-col w-full lg:w-auto justify-end lg:items-center gap-2">
    <Button
      onClick={onEditToggle}
      variant="ghost"
      className="flex-1 lg:flex-none text-muted-foreground hover:text-primary"
    >
      {isEditing ? "Preview" : "Edit"}
    </Button>
    <Button
      onClick={onRemove}
      variant="ghost"
      className="flex-1 lg:flex-none lg:opacity-0 lg:group-hover:opacity-100 p-1 text-muted-foreground hover:text-destructive transition-all shrink-0"
    >
      <TrashIcon className="w-4 h-4 lg:w-5 lg:h-5" />
    </Button>
  </div>
);

const PreviewDialog = ({
  open,
  onClose,
  content,
  onCopy,
}: {
  open: boolean;
  onClose: () => void;
  content: string;
  onCopy: () => Promise<void>;
}) => (
  <Dialog open={open} onOpenChange={onClose}>
    <DialogContent className="max-w-4xl h-[80vh]">
      <DialogHeader>
        <DialogTitle>Full Template Preview</DialogTitle>
      </DialogHeader>
      <ScrollArea className="flex-1 h-[calc(80vh-8rem)]">
        <div className="prose max-w-none dark:prose-invert p-4">
          <MarkdownPreview content={content} />
        </div>
      </ScrollArea>
      <DialogFooter>
        <Button variant="outline" onClick={onClose}>
          Close
        </Button>
        <Button
          onClick={(e) => {
            e.preventDefault();
            void onCopy();
          }}
        >
          Copy Markdown
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
);

export default function Preview({ blocks, setBlocks, onSave }: PreviewProps) {
  const { setNodeRef, isOver } = useDroppable({ id: "preview" });
  const [showFullPreview, setShowFullPreview] = useState(false);
  const { toast } = useToast();

  const handleRemoveBlock = (id: string) => {
    setBlocks(blocks.filter((block) => block.id !== id));
  };

  const updateBlockContent = (id: string, content: string) => {
    setBlocks(
      blocks.map((block) => (block.id === id ? { ...block, content } : block)),
    );
  };

  const getAllMarkdownContent = () =>
    blocks
      .map((block) => block.content)
      .filter(Boolean)
      .join("\n\n");

  const handleCopyMarkdown = async () => {
    await navigator.clipboard.writeText(getAllMarkdownContent());
    toast({
      title: "Copied to clipboard",
      description: "Markdown content has been copied successfully",
      duration: 2000,
    });
  };

  return (
    <>
      <div className="flex-1 p-2 lg:p-3 bg-background">
        <div
          ref={setNodeRef}
          className={`max-w-3xl mx-auto min-h-[calc(100vh-4rem)] lg:min-h-[calc(100vh-6rem)] rounded-lg transition-all duration-200 bg-card shadow-sm border border-border
            ${isOver ? "ring-2 ring-primary ring-opacity-50 bg-primary/5" : ""} 
            ${blocks.length === 0 ? "flex items-center justify-center" : ""}`}
        >
          {blocks.length > 0 && (
            <div className="border-b border-border">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between p-3 lg:p-4 space-y-3 lg:space-y-0">
                <h2 className="text-lg lg:text-xl font-bold text-foreground">
                  Template Preview
                </h2>
                <div className="flex flex-wrap gap-2">
                  <Button
                    onClick={(e) => {
                      e.preventDefault();
                      void handleCopyMarkdown();
                    }}
                    variant="outline"
                    className="flex-1 lg:flex-none"
                  >
                    Copy Markdown
                  </Button>
                  <Button
                    onClick={() => setShowFullPreview(true)}
                    variant="outline"
                    className="flex-1 lg:flex-none"
                  >
                    Preview
                  </Button>
                  <Button
                    onClick={() => onSave(getAllMarkdownContent())}
                    variant="default"
                    className="flex-1 lg:flex-none"
                  >
                    Save
                  </Button>
                </div>
              </div>
            </div>
          )}

          <ScrollArea className="h-[calc(100vh-8rem)] lg:h-[calc(100vh-12rem)]">
            <SortableContext items={blocks}>
              <div className="p-3 lg:p-4">
                {blocks.map((block) => {
                  const [baseBlockId] = block.id.split("-");
                  const initialBlock = BLOCKS.find(
                    (block) => block.id === baseBlockId,
                  );
                  return (
                    <SortableBlock
                      key={block.id}
                      id={block.id}
                      onRemove={handleRemoveBlock}
                      onContentUpdate={updateBlockContent}
                      initialContent={initialBlock?.content || ""}
                    />
                  );
                })}
              </div>
              <div className="p-4 lg:p-8 text-center text-muted-foreground border-2 border-dashed border-border rounded-lg mx-3 lg:mx-4 mb-4 min-h-[150px] lg:min-h-[200px] flex items-center justify-center">
                <div>
                  <p className="text-base lg:text-lg font-medium">
                    {blocks.length === 0
                      ? "Start Building Your README Template"
                      : "Drop More Blocks Here"}
                  </p>
                  <p className="text-xs lg:text-sm mt-2">
                    Drag and drop blocks from the sidebar to add to your
                    template
                  </p>
                </div>
              </div>
            </SortableContext>
          </ScrollArea>
        </div>
      </div>

      <PreviewDialog
        open={showFullPreview}
        onClose={() => setShowFullPreview(false)}
        content={getAllMarkdownContent()}
        onCopy={handleCopyMarkdown}
      />
    </>
  );
}
