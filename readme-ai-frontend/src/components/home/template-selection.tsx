import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { Link } from "@tanstack/react-router";
import { useState } from "react";
import ErrorDisplay from "./error-display";
import TemplatesContentSkeleton from "./skeletons/template-content-skeleton";
import TemplateGrid from "./templates/template-grid";
import { SearchHeader } from "../search-header";
import { useTemplates } from "@/hooks/templates/use-templates";
import { useUserTemplates } from "@/hooks/templates/use-user-template";

const CommunityTemplatesContent = ({
  onSelect,
  searchTerm,
}: {
  onSelect: (templateId?: number) => void;
  searchTerm: string;
}) => {
  const [page, setPage] = useState(1);
  // Pass searchTerm as query parameter
  const { data, isLoading, error } = useTemplates(page, undefined, searchTerm);

  if (isLoading) return <TemplatesContentSkeleton />;

  if (error)
    return <ErrorDisplay message={"Failed to get templates"} error={error} />;

  // No need to filter client-side as search is now handled by the API
  return (
    <div className="space-y-4">
      <TemplateGrid templates={data?.data ?? []} onSelect={onSelect} />
      <Pagination>
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            />
          </PaginationItem>
          {Array.from({ length: data?.total_pages || 0 }, (_, i) => (
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
              onClick={() =>
                setPage((p) => Math.min(data?.total_pages ?? 0, p + 1))
              }
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
};

const UserTemplatesContent = ({
  onSelect,
  searchTerm,
}: {
  onSelect: (templateId?: number) => void;
  searchTerm: string;
}) => {
  const [page, setPage] = useState(1);
  // Pass searchTerm as query parameter
  const { data, isLoading, error } = useUserTemplates(
    page,
    undefined,
    searchTerm,
  );

  if (isLoading) return <TemplatesContentSkeleton />;

  if (error)
    return (
      <ErrorDisplay message={"Failed to get your templates"} error={error} />
    );

  if (!data?.data.length) {
    return (
      <div className="p-3 border rounded-lg bg-card text-center text-muted-foreground text-sm md:text-base">
        Create your first template to get started
      </div>
    );
  }

  // No need to filter client-side as search is now handled by the API
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
  onSelect: (templateId?: number) => void;
}) {
  const [searchTerm, setSearchTerm] = useState("");

  return (
    <div className="space-y-4">
      <SearchHeader
        title="Templates"
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        placeholder="Search templates..."
      />
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
            <Link to="/templates/create">
              <Button variant="outline" className="w-full md:w-auto">
                Submit Template
              </Button>
            </Link>
          </div>
          <CommunityTemplatesContent
            onSelect={onSelect}
            searchTerm={searchTerm}
          />
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
          <UserTemplatesContent onSelect={onSelect} searchTerm={searchTerm} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
