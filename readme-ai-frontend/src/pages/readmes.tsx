import { useState } from "react";
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

  const {
    data: userReadmes,
    isLoading,
    error,
  } = useUserReadmes(page, pageSize);

  if (isLoading) {
    return <LoadingSkeletons />;
  }

  if (error) {
    return <ErrorDisplay error={error} message="Failed to load READMEs" />;
  }

  if (
    !userReadmes ||
    (userReadmes &&
      (userReadmes.data.length === 0 || userReadmes.total_pages === 0))
  ) {
    return <EmptyState message="No READMEs found. Create your first one!" />;
  }

  const filteredReadmes = userReadmes.data.filter((readme) =>
    readme.title.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  return (
    <div className="min-h-screen bg-background">
      <SearchHeader
        title="Your READMEs"
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
        placeholder="Search READMEs..."
      />

      <main className="container mx-auto px-4 py-8">
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredReadmes.map((readme) => (
              <ReadmeCard key={readme.id} readme={readme} />
            ))}
          </div>

          {userReadmes.total_pages && (
            <DataPagination
              className="w-full mt-8"
              page={page}
              totalPages={userReadmes.total_pages}
              setPage={setPage}
            />
          )}
        </>
      </main>
    </div>
  );
}
