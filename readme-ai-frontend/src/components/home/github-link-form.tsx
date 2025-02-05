import type { useForm } from "react-hook-form";
import LoadingSkeleton from "./skeletons/readme-generation";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "../ui/card";
import {
  FormField,
  Form,
  FormControl,
  FormItem,
  FormMessage,
} from "../ui/form";
import { siGithub as Github } from "simple-icons";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import type { FormSchema } from "@/pages/home-page";

interface GithubLinkFormProps {
  form: ReturnType<typeof useForm<FormSchema>>;
  onSubmit: (values: FormSchema) => void;
  onBack: () => void;
  isLoading: boolean;
}

const GithubLinkForm = ({
  form,
  onSubmit,
  onBack,
  isLoading,
}: GithubLinkFormProps) => {
  if (isLoading) return <LoadingSkeleton />;

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>Enter GitHub Repository Link</CardTitle>
        <CardDescription>
          Provide the link to the GitHub repository you want to generate a
          README for
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="githubLink"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <div className="flex items-center space-x-2">
                      <svg
                        role="img"
                        viewBox="0 0 24 24"
                        width="24"
                        height="24"
                        fill="currentColor"
                      >
                        <path d={Github.path} />
                      </svg>
                      <Input
                        placeholder="https://github.com/username/repo"
                        {...field}
                        className="flex-grow"
                      />
                    </div>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="flex flex-col md:flex-row gap-4 md:justify-between">
              <Button
                type="button"
                onClick={onBack}
                variant="outline"
                className="w-full md:w-auto"
              >
                Back
              </Button>
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full md:w-auto"
              >
                Generate README
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
};

export default GithubLinkForm;
