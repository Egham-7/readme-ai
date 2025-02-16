import { useState } from "react";
import { motion } from "framer-motion";
import { Book, Pencil } from "lucide-react";
import { Link } from "@tanstack/react-router";
import {
  Card,
  CardHeader,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
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
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import MarkdownPreview from "@/components/markdown-preview";
import DeleteReadmeModal from "./delete-readme-modal";
import { type Readme } from "@/services/readme";
import { useDevice } from "@/hooks/use-device";
import { useUpdateReadme } from "@/hooks/readme/use-update-readme";

interface ReadmeCardProps {
  readme: Readme;
}

const ReadmeCard = ({ readme }: ReadmeCardProps) => {
  const { isMobile } = useDevice();
  const [editContent, setEditContent] = useState(
    readme.versions.at(-1)?.content ?? "",
  );
  const [isEditing, setIsEditing] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  const { mutateAsync: updateReadme } = useUpdateReadme();

  const Modal = isMobile ? Drawer : Dialog;
  const ModalTrigger = isMobile ? DrawerTrigger : DialogTrigger;
  const ModalContent = isMobile ? DrawerContent : DialogContent;
  const ModalHeader = isMobile ? DrawerHeader : DialogHeader;
  const ModalTitle = isMobile ? DrawerTitle : DialogTitle;

  const detailsContent = (
    <>
      <ModalHeader>
        <ModalTitle>{readme.title}</ModalTitle>
      </ModalHeader>
      <div className="p-4 space-y-4 h-">
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Repository: {readme.repository_url}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsEditing(true)}
            >
              <Pencil className="h-4 w-4 mr-2" />
              Edit
            </Button>
            <DeleteReadmeModal
              onClose={() => setIsOpen(false)}
              readmeId={readme.id}
              readmeTitle={readme.title}
            />
          </div>
        </div>
        <div className="prose prose-sm dark:prose-invert max-h-96 overflow-auto">
          <MarkdownPreview content={readme.versions.at(-1)?.content ?? ""} />
        </div>
      </div>
    </>
  );

  const editTabContent = (
    <>
      <ModalHeader>
        <ModalTitle>Edit: {readme.title}</ModalTitle>
      </ModalHeader>
      <div className="p-4">
        <Tabs defaultValue="edit" className="flex-1">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="edit">Edit</TabsTrigger>
            <TabsTrigger value="preview">Preview</TabsTrigger>
          </TabsList>
          <TabsContent value="edit" className="mt-4">
            <Textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              className="min-h-[60vh] font-mono text-sm"
            />
          </TabsContent>
          <TabsContent value="preview" className="mt-4">
            <div className="prose prose-sm dark:prose-invert max-w-none  max-h-96 w-full bg-card border rounded-lg p-4 overflow-y-auto">
              <MarkdownPreview content={editContent} />
            </div>
          </TabsContent>
        </Tabs>
        <div className="flex justify-between mt-4">
          <Button
            variant="ghost"
            onClick={() => {
              setEditContent(readme.versions.at(-1)?.content ?? "");
              setIsEditing(false);
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={async () => {
              await updateReadme({
                readmeId: readme.id,
                content: editContent,
              });
              setIsEditing(false);
            }}
          >
            Save Changes
          </Button>
        </div>
      </div>
    </>
  );

  return (
    <motion.div
      whileHover={{ y: -5 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Book className="text-primary mr-2" size={24} />
              <h2 className="text-xl font-semibold truncate">{readme.title}</h2>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-2 truncate">
            Repository: {readme.repository_url}
          </p>
          <p className="text-sm text-muted-foreground">
            Last updated:{" "}
            {readme.updated_at &&
              new Date(readme.updated_at).toLocaleDateString()}
          </p>
        </CardContent>
        <CardFooter className="flex flex-col justify-center items-start gap-2">
          <Modal open={isOpen} onOpenChange={setIsOpen}>
            <ModalTrigger asChild>
              <Button variant="secondary">View Details</Button>
            </ModalTrigger>
            <ModalContent className="max-w-4xl">
              {isEditing ? editTabContent : detailsContent}
            </ModalContent>
          </Modal>
          <Button variant="default" asChild>
            <Link to="/readmes" params={{ readmeId: readme.id.toString() }}>
              Improve README
            </Link>
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  );
};

export default ReadmeCard;
