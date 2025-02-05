import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { useDevice } from "@/hooks/use-device";
import MarkdownPreview from "../markdown-preview";
import { forwardRef } from "react";
import { Link } from "@tanstack/react-router";

interface Template {
  id: string;
  name: string;
  content: string;
}

interface TemplatePreviewProps {
  template: Template;
  onSelect: (templateId: string) => void;
}

const templates: Template[] = [
  {
    id: "default",
    name: "Default",
    content:
      "# Project Title\n\n## Description\nA clear and concise description of your project.\n\n## Installation\n```bash\nnpm install\n```\n\n## Usage\nHow to use the project.\n\n## Contributing\nGuidelines for contributing.\n\n## License\nMIT",
  },
  {
    id: "minimal",
    name: "Minimal",
    content:
      "# Project Title\nBrief description of your project.\n\n## Quick Start\n```bash\nnpm install\nnpm start\n```\n\n## License\nMIT",
  },
  {
    id: "detailed",
    name: "Detailed",
    content:
      "# Project Title\n\n## Description\nDetailed project description.\n\n## Table of Contents\n- [Installation](#installation)\n- [Usage](#usage)\n- [API Reference](#api-reference)\n- [Contributing](#contributing)\n- [Tests](#tests)\n- [License](#license)\n\n## Installation\nStep-by-step installation guide.\n\n## Usage\nComprehensive usage examples.\n\n## API Reference\nAPI documentation.\n\n## Contributing\nDetailed contribution guidelines.\n\n## Tests\n```bash\nnpm test\n```\n\n## License\nMIT",
  },
];

const TemplatePreviewContent = ({
  template,
  onSelect,
}: TemplatePreviewProps) => (
  <div className="flex flex-col h-full">
    <Tabs
      defaultValue="preview"
      className="w-full bg-muted/50 p-2 md:p-4 rounded-lg flex-1"
    >
      <TabsList className="grid w-full grid-cols-2 bg-background">
        <TabsTrigger value="preview" className="text-sm md:text-base">
          Preview
        </TabsTrigger>
        <TabsTrigger value="code" className="text-sm md:text-base">
          Markdown
        </TabsTrigger>
      </TabsList>
      <TabsContent value="preview" className="mt-2 md:mt-4">
        <div className="prose prose-sm dark:prose-invert max-w-none bg-background border rounded-md p-2 md:p-4 h-[40vh] md:h-[50vh] overflow-y-auto">
          <MarkdownPreview content={template.content} />
        </div>
      </TabsContent>
      <TabsContent value="code" className="mt-2 md:mt-4">
        <Textarea
          value={template.content}
          readOnly
          className="w-full h-[40vh] md:h-[50vh] font-mono text-xs md:text-sm bg-background"
        />
      </TabsContent>
    </Tabs>
    <Button
      onClick={() => {
        onSelect(template.id);
      }}
      className="mt-4 w-full"
    >
      Use Template
    </Button>
  </div>
);

const TemplatePreviewTrigger = forwardRef<
  HTMLButtonElement,
  { name: string; onClick?: () => void }
>(({ name, onClick }, ref) => (
  <Button
    ref={ref}
    variant="outline"
    className="w-full h-20 md:h-24 flex flex-col items-center justify-center hover:bg-accent hover:text-accent-foreground"
    onClick={onClick}
    type="button"
  >
    <span className="font-bold text-sm md:text-base">{name}</span>
    <span className="text-xs md:text-sm text-muted-foreground">
      Preview template
    </span>
  </Button>
));

TemplatePreviewTrigger.displayName = "TemplatePreviewTrigger";

const TemplateGrid = ({
  templates,
  onSelect,
}: {
  templates: Template[];
  onSelect: (templateId: string) => void;
}) => {
  const { isMobile } = useDevice();

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4">
      {templates.map((template) =>
        isMobile ? (
          <Drawer key={template.id}>
            <DrawerTrigger asChild>
              <TemplatePreviewTrigger name={template.name} />
            </DrawerTrigger>
            <DrawerContent className="bg-background">
              <DrawerHeader className="bg-muted/30 p-3 md:p-4">
                <DrawerTitle className="text-base md:text-lg">
                  {template.name} Template
                </DrawerTitle>
                <DrawerDescription className="text-sm">
                  Preview and use this template
                </DrawerDescription>
              </DrawerHeader>
              <div className="p-3 md:p-4 flex-1 overflow-y-auto">
                <TemplatePreviewContent
                  template={template}
                  onSelect={onSelect}
                />
              </div>
            </DrawerContent>
          </Drawer>
        ) : (
          <Dialog key={template.id}>
            <DialogTrigger asChild>
              <TemplatePreviewTrigger name={template.name} />
            </DialogTrigger>
            <DialogContent className="max-w-3xl overflow-hidden bg-background">
              <DialogHeader className="bg-muted/30 p-4 rounded-t-lg">
                <DialogTitle className="text-lg">
                  {template.name} Template
                </DialogTitle>
                <DialogDescription>
                  Preview and use this template
                </DialogDescription>
              </DialogHeader>
              <div className="p-4">
                <TemplatePreviewContent
                  template={template}
                  onSelect={onSelect}
                />
              </div>
            </DialogContent>
          </Dialog>
        ),
      )}
    </div>
  );
};

export function TemplateSelection({
  onSelect,
}: {
  onSelect: (templateId: string) => void;
}) {
  return (
    <div className="container mx-auto py-4 md:py-8 px-3 md:px-8 space-y-6 md:space-y-8">
      <Tabs defaultValue="featured" className="space-y-4 md:space-y-6">
        <TabsList className="flex  mb-12 w-full flex-wrap md:flex-nowrap gap-2 md:gap-0 md:justify-start md:bg-muted/30 md:mb-0">
          <TabsTrigger
            value="featured"
            className="flex-1 md:flex-none text-sm md:text-base"
          >
            Featured Templates
          </TabsTrigger>
          <TabsTrigger
            value="community"
            className="flex-1 md:flex-none text-sm md:text-base"
          >
            Community Templates
          </TabsTrigger>
          <TabsTrigger
            value="custom"
            className="flex-1 md:flex-none text-sm md:text-base"
          >
            My Templates
          </TabsTrigger>
        </TabsList>

        <TabsContent value="featured" className="space-y-4 md:space-y-6">
          <div className="p-3 md:p-6 border rounded-lg bg-card">
            <h3 className="text-base md:text-xl font-semibold mb-4">
              Featured Templates
            </h3>
            <TemplateGrid templates={templates} onSelect={onSelect} />
          </div>
        </TabsContent>

        <TabsContent value="community" className="space-y-4 md:space-y-6">
          <div className="flex flex-col md:flex-row gap-3 md:gap-0 md:justify-between md:items-center">
            <h3 className="text-base md:text-xl font-semibold">
              Community Templates
            </h3>
            <Button variant="outline" className="w-full md:w-auto">
              Submit Template
            </Button>
          </div>
          <div className="grid grid-cols-1 gap-4">
            <div className="p-3 md:p-6 border rounded-lg bg-card text-center text-muted-foreground text-sm md:text-base">
              Coming soon! Share and discover community-created templates.
            </div>
          </div>
        </TabsContent>

        <TabsContent value="custom" className="space-y-4 md:space-y-6">
          <div className="flex flex-col md:flex-row gap-3 md:gap-0 md:justify-between md:items-center">
            <h3 className="text-base md:text-xl font-semibold">
              My Custom Templates
            </h3>
            <Link to="/templates/create" className="w-full md:w-auto">
              <Button className="w-full md:w-auto">Create New Template</Button>
            </Link>
          </div>
          <div className="grid grid-cols-1 gap-4">
            <div className="p-3 md:p-6 border rounded-lg bg-card text-center text-muted-foreground text-sm md:text-base">
              Create and manage your custom templates here.
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
