import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";
import DeleteModal from "@/components/delete-modal";
import { useDeleteReadme } from "@/hooks/readme/use-delete-readme";

interface DeleteReadmeModalProps {
  readmeId: number;
  readmeTitle: string;
  onClose: () => void;
}

const DeleteReadmeModal = ({
  readmeId,
  readmeTitle,
  onClose,
}: DeleteReadmeModalProps) => {
  const { mutateAsync: deleteReadme, isPending } = useDeleteReadme();

  return (
    <DeleteModal
      title={`Delete ${readmeTitle}`}
      description="Are you sure you want to delete this README? This action cannot be undone."
      trigger={
        <Button variant="ghost" size="icon">
          <Trash2 className="h-4 w-4 text-destructive" />
        </Button>
      }
      onDelete={async () => {
        await deleteReadme(readmeId);
        onClose();
      }}
      isDeleting={isPending}
    />
  );
};

export default DeleteReadmeModal;
