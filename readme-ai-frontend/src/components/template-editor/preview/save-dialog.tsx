import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogClose,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerDescription,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { useDevice } from "@/hooks/use-device";
import { type UseFormReturn } from "react-hook-form";

const formSchema = z.object({
  title: z.string().min(1, "Title is required"),
});

interface SaveDialogProps {
  onSave: (title: string) => void;
}

export function SaveDialog({ onSave }: SaveDialogProps) {
  const { isMobile } = useDevice();
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      title: "",
    },
  });

  const onSubmit = (values: z.infer<typeof formSchema>) => {
    onSave(values.title);
    form.reset();
  };

  if (!isMobile) {
    return (
      <Dialog>
        <DialogTrigger asChild>
          <Button variant="default" className="flex-1 lg:flex-none">
            Save
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Save Template</DialogTitle>
            <DialogDescription>
              Give your template a title before saving.
            </DialogDescription>
          </DialogHeader>
          <SaveForm form={form} onSubmit={onSubmit} />
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Drawer>
      <DrawerTrigger asChild>
        <Button variant="default" className="flex-1 lg:flex-none">
          Save
        </Button>
      </DrawerTrigger>
      <DrawerContent>
        <DrawerHeader>
          <DrawerTitle>Save Template</DrawerTitle>
          <DrawerDescription>
            Give your template a title before saving.
          </DrawerDescription>
        </DrawerHeader>
        <div className="px-4">
          <SaveForm form={form} onSubmit={onSubmit} />
        </div>
      </DrawerContent>
    </Drawer>
  );
}

function SaveForm({
  form,
  onSubmit,
}: {
  form: UseFormReturn<z.infer<typeof formSchema>>;
  onSubmit: (values: z.infer<typeof formSchema>) => void;
}) {
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Template Title</FormLabel>
              <FormControl>
                <Input placeholder="Enter template title" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <div className="flex justify-end gap-4">
          <DialogClose asChild>
            <Button type="button" variant="outline">
              Cancel
            </Button>
          </DialogClose>
          <DialogClose asChild>
            <Button type="submit">Save Template</Button>
          </DialogClose>
        </div>
      </form>
    </Form>
  );
}
