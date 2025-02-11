import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { useDevice } from "@/hooks/use-device";
import { useTemplates, useUserTemplates } from "@/hooks/readme/use-templates";
import MarkdownPreview from "../markdown-preview";
import { Link } from "@tanstack/react-router";
import { ApiError, type Template } from "@/services/readme";
import { useState } from "react";
import ErrorDisplay from "./error-display";
import { useToast } from "@/hooks/use-toast";
import { useDeleteTemplate } from "@/hooks/readme/use-templates";
import {
  Card,
  CardTitle,
  CardFooter,
  CardContent,
  CardHeader,
} from "../ui/card";
import { TrashIcon, PencilIcon, EyeIcon } from "lucide-react";
import { useUser } from "@clerk/clerk-react";

const TemplateSkeleton = () => (
  <div className="w-full h-20 md:h-24 rounded-lg bg-muted animate-pulse" />
);

const TemplateGridSkeleton = () => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4">
    {Array.from({ length: 6 }).map((_, i) => (
      <TemplateSkeleton key={i} />
    ))}
  </div>
);

const TemplatesContentSkeleton = () => (
  <div className="space-y-4">
    <div className="flex flex-col md:flex-row gap-3 md:gap-0 md:justify-between md:items-center">
      <div className="h-7 w-48 bg-muted rounded animate-pulse" />
      <div className="h-10 w-32 bg-muted rounded animate-pulse" />
    </div>
    <TemplateGridSkeleton />
  </div>
);

const DeleteTemplateModal = ({
  template,
  onClose,
}: {
  template: Template;
  onClose: () => void;
}) => {
  const { isMobile } = useDevice();
  const deleteTemplate = useDeleteTemplate();
  const { toast } = useToast();
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  const handleDelete = async () => {
    try {
      await deleteTemplate.mutateAsync(template.id);
      toast({
        title: "Success",
        description: "Template deleted successfully",
      });
    } catch (error) {
      if (error instanceof ApiError) {
        toast({
          title: "Error",
          description: error.message,
          variant: "destructive",
        });
        return;
      }
      toast({
        title: "Error",
        description: "Failed to delete template",
        variant: "destructive",
      });
    } finally {
      setIsDeleteModalOpen(false);
      onClose();
    }
  };

  const trigger = (
    <Button variant="outline" size="icon">
      <TrashIcon className="h-4 w-4" />
    </Button>
  );

  const content = (
    <div className="space-y-4">
      <p className="text-sm md:text-base">
        Are you sure you want to delete Template {template.id}? This action
        cannot be undone.
      </p>
      <div className="flex gap-2 justify-end">
        <Button variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button
          variant="destructive"
          onClick={handleDelete}
          disabled={deleteTemplate.isPending}
        >
          {deleteTemplate.isPending ? "Deleting..." : "Delete"}
        </Button>
      </div>
    </div>
  );

  if (isMobile) {
    return (
      <Drawer open={isDeleteModalOpen} onOpenChange={setIsDeleteModalOpen}>
        <DrawerTrigger asChild>{trigger}</DrawerTrigger>
        <DrawerContent>
          <DrawerHeader>
            <DrawerTitle>Delete Template</DrawerTitle>
          </DrawerHeader>
          <div className="p-4">{content}</div>
        </DrawerContent>
      </Drawer>
    );
  }

  return (
    <Dialog>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Delete Template</DialogTitle>
        </DialogHeader>
        {content}
      </DialogContent>
    </Dialog>
  );
};

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

  const previewContent = (
    <Card className="flex flex-col h-full w-full">
      <CardHeader>
        <CardTitle className="text-xl font-semibold">{template.id}</CardTitle>
      </CardHeader>
      <CardContent className="flex-1">
        <Tabs defaultValue="preview" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="preview">Preview</TabsTrigger>
            <TabsTrigger value="code">Markdown</TabsTrigger>
          </TabsList>

          <TabsContent value="preview" className="mt-4">
            <div className="prose prose-sm dark:prose-invert max-w-none bg-card border rounded-lg p-4 h-[40vh] md:h-[50vh] overflow-y-auto">
              <MarkdownPreview content={template.content} />
            </div>
          </TabsContent>

          <TabsContent value="code" className="mt-4">
            <Textarea
              value={template.content}
              readOnly
              className="w-full h-[40vh] md:h-[50vh] font-mono text-sm bg-card"
            />
          </TabsContent>
        </Tabs>
      </CardContent>

      <CardFooter className="gap-2">
        <Button
          onClick={() => onSelect(template.id)}
          className="flex-1"
          variant="default"
        >
          Use Template
        </Button>

        {userId === templateUserId && (
          <>
            <Link
              to="/templates/update/$templateId"
              params={{ templateId: template.id.toString() }}
            >
              <Button variant="outline" size="icon">
                <PencilIcon className="h-4 w-4" />
              </Button>
            </Link>

            <DeleteTemplateModal
              onClose={() => setIsPreviewOpen(false)}
              template={template}
            ></DeleteTemplateModal>
          </>
        )}
      </CardFooter>
    </Card>
  );

  if (isMobile) {
    return (
      <Card className="group hover:border-primary/50 transition-colors">
        <CardHeader>
          <CardTitle className="text-lg">{template.id}</CardTitle>
        </CardHeader>
        <CardFooter className="gap-2">
          <Button
            variant="outline"
            className="flex-1"
            onClick={() => setIsPreviewOpen(true)}
          >
            <EyeIcon className="h-4 w-4 mr-2" />
            Preview
          </Button>
          <Button onClick={() => onSelect(template.id)}>Use</Button>
        </CardFooter>

        {isPreviewOpen && previewContent}
      </Card>
    );
  }

  return previewContent;
};

const TemplateGrid = ({
  templates,
  onSelect,
}: {
  templates: Template[];
  onSelect: (templateId: number) => void;
}) => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4">
    {templates.map((template) => (
      <TemplateCard key={template.id} template={template} onSelect={onSelect} />
    ))}
  </div>
);

const CommunityTemplatesContent = ({
  onSelect,
}: {
  onSelect: (templateId: number) => void;
}) => {
  const [page, setPage] = useState(1);
  const { data, isLoading, error } = useTemplates(page);

  if (isLoading) return <TemplatesContentSkeleton />;
  if (error) return <ErrorDisplay error={error} />;

  if (!data || (data && data.data && data.data.length <= 0)) {
    return (
      <div className="p-3 md:p-6 border rounded-lg bg-card text-center text-muted-foreground text-sm md:text-base">
        No templates available
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <TemplateGrid templates={data.data} onSelect={onSelect} />
      <Pagination>
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            />
          </PaginationItem>
          {Array.from({ length: data.total_pages }, (_, i) => (
            <PaginationItem key={i + 1}>
              <PaginationLink
                isActive={page === i + 1}
                onClick={() => setPage(i + 1)}
              >
                {i + 1}
              </PaginationLink>
            </PaginationItem>
          ))}
          <PaginationItem>
            <PaginationNext
              onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
};

const UserTemplatesContent = ({
  onSelect,
}: {
  onSelect: (templateId: number) => void;
}) => {
  const [page, setPage] = useState(1);
  const { data, isLoading, error } = useUserTemplates(page);

  if (isLoading) return <TemplatesContentSkeleton />;
  if (error) return <ErrorDisplay error={error} />;
  if (!data?.data.length) {
    return (
      <div className="p-3 md:p-6 border rounded-lg bg-card text-center text-muted-foreground text-sm md:text-base">
        Create your first template to get started
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <TemplateGrid templates={data.data} onSelect={onSelect} />
      <Pagination>
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            />
          </PaginationItem>
          {Array.from({ length: data.total_pages }, (_, i) => (
            <PaginationItem key={i + 1}>
              <PaginationLink
                isActive={page === i + 1}
                onClick={() => setPage(i + 1)}
              >
                {i + 1}
              </PaginationLink>
            </PaginationItem>
          ))}
          <PaginationItem>
            <PaginationNext
              onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
};

export function TemplateSelection({
  onSelect,
}: {
  onSelect: (templateId: number) => void;
}) {
  return (
    <div className="container mx-auto py-4 md:py-8 px-3 md:px-8 space-y-6 md:space-y-8">
      <Tabs defaultValue="community" className="space-y-4 md:space-y-6">
        <TabsList className="flex mb-20 w-full flex-wrap md:flex-nowrap gap-2 md:gap-0 md:justify-start md:bg-muted/30 md:mb-0">
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
        <TabsContent value="community" className="space-y-4 md:space-y-6">
          <div className="flex flex-col md:flex-row gap-3 md:gap-0 md:justify-between md:items-center">
            <h3 className="text-base md:text-xl font-semibold">
              Community Templates
            </h3>
            <Button variant="outline" className="w-full md:w-auto">
              Submit Template
            </Button>
          </div>
          <CommunityTemplatesContent onSelect={onSelect} />
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
          <UserTemplatesContent onSelect={onSelect} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
