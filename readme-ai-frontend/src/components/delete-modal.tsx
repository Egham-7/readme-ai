import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogClose,
} from "@/components/ui/dialog";
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
  DrawerClose,
} from "@/components/ui/drawer";
import { Button } from "@/components/ui/button";
import { useDevice } from "@/hooks/use-device";

interface DeleteModalProps {
  title: string;
  description: string;
  trigger: React.ReactNode;
  onDelete: () => Promise<void>;
  isDeleting: boolean;
}

const DeleteModal = ({
  title,
  description,
  trigger,
  onDelete,
  isDeleting,
}: DeleteModalProps) => {
  const { isMobile } = useDevice();
  const [isOpen, setIsOpen] = useState(false);

  const content = (
    <div className="space-y-4">
      <p className="text-sm md:text-base">{description}</p>
      <div className="flex gap-2 justify-end">
        {isMobile ? (
          <DrawerClose asChild>
            <Button variant="outline">Cancel</Button>
          </DrawerClose>
        ) : (
          <DialogClose asChild>
            <Button variant="outline">Cancel</Button>
          </DialogClose>
        )}
        <Button
          variant="destructive"
          onClick={async () => {
            await onDelete();
            setIsOpen(false);
          }}
          disabled={isDeleting}
        >
          {isDeleting ? "Deleting..." : "Delete"}
        </Button>
      </div>
    </div>
  );

  if (isMobile) {
    return (
      <Drawer open={isOpen} onOpenChange={setIsOpen}>
        <DrawerTrigger asChild>{trigger}</DrawerTrigger>
        <DrawerContent>
          <DrawerHeader>
            <DrawerTitle>{title}</DrawerTitle>
          </DrawerHeader>
          <div className="p-4">{content}</div>
        </DrawerContent>
      </Drawer>
    );
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        {content}
      </DialogContent>
    </Dialog>
  );
};

export default DeleteModal;
