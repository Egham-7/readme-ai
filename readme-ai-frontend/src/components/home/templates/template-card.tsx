import { type Template } from "@/services/templates";
import { useDevice } from "@/hooks/use-device";
import { useState } from "react";
import { useUser } from "@clerk/clerk-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardFooter,
  CardDescription,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerFooter,
} from "@/components/ui/drawer";
import { TabsContent, Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import MarkdownPreview from "@/components/markdown-preview";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { EyeIcon, PencilIcon } from "lucide-react";
import DeleteTemplateModal from "./delete-template-modal";
import { Link } from "@tanstack/react-router";

const TemplateCard = ({
  template,
  onSelect,
}: {
  template: Template;
  onSelect: (templateId: number) => void;
}) => {
  const { isMobile } = useDevice();
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const user = useUser().user;
  const userId = user?.id;
  const templateUserId = template.user_id;

  const PreviewModal = isMobile ? Drawer : Dialog;
  const ModalContent = isMobile ? DrawerContent : DialogContent;
  const ModalHeader = isMobile ? DrawerHeader : DialogHeader;
  const ModalFooter = isMobile ? DrawerFooter : DialogFooter;

  const previewContent = (
    <div className="flex flex-col h-full">
      <Tabs defaultValue="preview" className="flex-1">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="preview">Preview</TabsTrigger>
          <TabsTrigger value="code">Markdown</TabsTrigger>
        </TabsList>
        <TabsContent value="preview" className="mt-2 md:mt-4 flex-1">
          <div className="prose prose-sm h-[40vh] md:h-[60vh] dark:prose-invert max-w-none w-full bg-card border rounded-lg p-2 md:p-4 overflow-y-auto">
            <MarkdownPreview content={template.content} />
          </div>
        </TabsContent>
        <TabsContent value="code" className="mt-2 md:mt-4 flex-1">
          <Textarea
            value={template.content}
            readOnly
            className="w-full h-[40vh] md:h-[60vh] font-mono text-xs md:text-sm bg-card"
          />
        </TabsContent>
      </Tabs>
    </div>
  );

  const previewActions = (
    <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between w-full gap-2 md:gap-4">
      <Button
        onClick={() => onSelect(template.id)}
        variant="default"
        className="w-full md:w-auto"
      >
        Use Template
      </Button>

      {userId === templateUserId && (
        <div className="flex items-center gap-2 justify-end">
          <Link
            to="/templates/update/$templateId"
            params={{ templateId: template.id.toString() }}
          >
            <Button variant="outline" size="icon" className="h-9 w-9">
              <PencilIcon className="h-4 w-4" />
            </Button>
          </Link>
          <DeleteTemplateModal
            onClose={() => setIsPreviewOpen(false)}
            template={template}
          />
        </div>
      )}
    </div>
  );

  return (
    <>
      <Card className="group hover:border-primary/50 transition-colors w-full">
        <CardHeader className="p-3 md:p-6">
          <CardTitle className="text-base md:text-lg flex items-center justify-between">
            {template.title}
          </CardTitle>
          <CardDescription className="text-sm line-clamp-2 mt-1">
            {template.content.substring(0, 100)}...
          </CardDescription>
        </CardHeader>
        <CardFooter className="flex flex-col gap-2 p-3 md:p-6">
          <Button
            variant="outline"
            className="w-full md:flex-1"
            onClick={() => setIsPreviewOpen(true)}
          >
            <EyeIcon className="h-4 w-4 mr-2" />
            View Template
          </Button>
          <Button
            onClick={() => onSelect(template.id)}
            className="w-full md:flex-1"
          >
            Use Template
          </Button>
        </CardFooter>
      </Card>

      <PreviewModal open={isPreviewOpen} onOpenChange={setIsPreviewOpen}>
        <ModalContent className={`${isMobile ? "px-4" : "max-w-4xl"}`}>
          <ModalHeader>
            <DialogTitle>Template {template.title}</DialogTitle>
          </ModalHeader>
          {previewContent}
          <ModalFooter>{previewActions}</ModalFooter>
        </ModalContent>
      </PreviewModal>
    </>
  );
};

export default TemplateCard;
