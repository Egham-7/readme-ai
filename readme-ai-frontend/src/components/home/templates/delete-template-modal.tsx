import { TrashIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useDeleteTemplate } from "@/hooks/readme/use-templates";
import { useToast } from "@/hooks/use-toast";
import { ApiError } from "@/services/utils";
import { type Template } from "@/services/templates";
import DeleteModal from "@/components/delete-modal";

const DeleteTemplateModal = ({
  template,
  onClose,
}: {
  template: Template;
  onClose: () => void;
}) => {
  const deleteTemplate = useDeleteTemplate();
  const { toast } = useToast();

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
      onClose();
    }
  };

  return (
    <DeleteModal
      title="Delete Template"
      description={`Are you sure you want to delete Template ${template.id}? This action cannot be undone.`}
      trigger={
        <Button variant="outline" size="icon">
          <TrashIcon className="h-4 w-4" />
        </Button>
      }
      onDelete={handleDelete}
      isDeleting={deleteTemplate.isPending}
    />
  );
};

export default DeleteTemplateModal;
