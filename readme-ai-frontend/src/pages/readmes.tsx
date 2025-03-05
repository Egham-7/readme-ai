import { useState, useEffect } from "react";
import { Book } from "lucide-react";
import {
  Card,
  CardHeader,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { useUserReadmes } from "@/hooks/readme/use-user-readmes";
import { Skeleton } from "@/components/ui/skeleton";
import ErrorDisplay from "@/components/home/error-display";
import { DataPagination } from "@/components/pagination";
import { SearchHeader } from "@/components/search-header";
import ReadmeCard from "@/components/home/readmes/readme-card";
import { useDebounce } from "@/hooks/use-debounce";

interface EmptyStateProps {
  message: string;
}

const ReadmeCardSkeleton = () => (
  <Card>
    <CardHeader>
      <div className="flex items-center">
        <Skeleton className="h-6 w-6 mr-2" />
        <Skeleton className="h-6 w-48" />
      </div>
    </CardHeader>
    <CardContent>
      <Skeleton className="h-4 w-full mb-2" />
      <Skeleton className="h-4 w-32" />
    </CardContent>
    <CardFooter>
      <Skeleton className="h-9 w-32" />
    </CardFooter>
  </Card>
);

const LoadingSkeletons = () => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {[...Array(9)].map((_, index) => (
      <ReadmeCardSkeleton key={index} />
    ))}
  </div>
);

const EmptyState = ({ message }: EmptyStateProps) => (
  <Card className="text-center p-8">
    <Book size={48} className="mx-auto mb-4 text-muted" />
    <p className="text-xl text-muted-foreground">{message}</p>
  </Card>
);

export default function Readmes() {
  const [searchTerm, setSearchTerm] = useState("");
  const [page, setPage] = useState(1);
  const pageSize = 9;

  // Debounce search term to avoid excessive API calls
  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  // Reset page to 1 when search term changes
  useEffect(() => {
    setPage(1);
  }, [debouncedSearchTerm]);

  const {
    data: userReadmes,
    isLoading,
    error,
  } = useUserReadmes(page, pageSize, debouncedSearchTerm);

  // Render the header consistently to prevent losing focus
  const header = (
    <SearchHeader
      title="Your READMEs"
      searchTerm={searchTerm}
      setSearchTerm={setSearchTerm}
      placeholder="Search READMEs..."
    />
  );

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        {header}
        <main className="container mx-auto px-4 py-8">
          <LoadingSkeletons />
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background">
        {header}
        <main className="container mx-auto px-4 py-8">
          <ErrorDisplay error={error} message="Failed to load READMEs" />
        </main>
      </div>
    );
  }

  if (
    !userReadmes ||
    (userReadmes &&
      (userReadmes.data.length === 0 || userReadmes.total_pages === 0))
  ) {
    return (
      <div className="min-h-screen bg-background">
        {header}
        <main className="container mx-auto px-4 py-8">
          <EmptyState message="No READMEs found. Create your first one!" />
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {header}
      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {userReadmes.data.map((readme) => (
            <ReadmeCard key={readme.id} readme={readme} />
          ))}
        </div>
        {userReadmes.total_pages > 0 && (
          <DataPagination
            className="w-full mt-8"
            page={page}
            totalPages={userReadmes.total_pages}
            setPage={setPage}
          />
        )}
      </main>
    </div>
  );
}
