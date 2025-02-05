import { Button } from "../ui/button";
import { useState } from "react";
import { Textarea } from "../ui/textarea";
import MarkdownPreview from "../markdown-preview";

function RawEditor({ onSave }: { onSave: (markdown: string) => void }) {
  const [rawMarkdown, setRawMarkdown] = useState("");
  const [isPreviewVisible, setIsPreviewVisible] = useState(false);

  return (
    <div className="h-full flex flex-col bg-background">
      <div className="flex justify-between p-4">
        <Button
          className="lg:hidden"
          onClick={() => setIsPreviewVisible(!isPreviewVisible)}
        >
          {isPreviewVisible ? "Show Editor" : "Show Preview"}
        </Button>
        <Button onClick={() => onSave(rawMarkdown)}>Save Template</Button>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 flex-1 p-4">
        <Textarea
          value={rawMarkdown}
          onChange={(e) => setRawMarkdown(e.target.value)}
          className={`
            h-full font-mono resize-none p-4 bg-card border-border
            ${isPreviewVisible ? "hidden" : "block"} lg:block
          `}
          placeholder="Enter your markdown here..."
        />
        <div
          className={`
          border border-border rounded-lg p-4 overflow-auto bg-card
          ${isPreviewVisible ? "block" : "hidden"} lg:block
        `}
        >
          <MarkdownPreview content={rawMarkdown} />
        </div>
      </div>
    </div>
  );
}

export default RawEditor;
