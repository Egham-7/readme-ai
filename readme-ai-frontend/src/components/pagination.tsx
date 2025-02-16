import {
  Pagination,
  PaginationContent,
  PaginationLink,
  PaginationItem,
} from "./ui/pagination";

interface PaginationProps {
  page: number;
  setPage: (page: number | ((prev: number) => number)) => void;
  totalPages: number;
  className?: string;
}

export const DataPagination = ({
  page,
  setPage,
  totalPages,
  className = "mt-8",
}: PaginationProps) => {
  const handlePrevPage = () => setPage((p) => Math.max(1, p - 1));
  const handleNextPage = () => setPage((p) => Math.min(totalPages, p + 1));

  return (
    <div className={`flex justify-center ${className}`}>
      <Pagination>
        <PaginationContent className="gap-6">
          <PaginationItem>
            <PaginationLink onClick={handlePrevPage} aria-disabled={page === 1}>
              Previous
            </PaginationLink>
          </PaginationItem>
          {Array.from({ length: totalPages }, (_, i) => (
            <PaginationItem key={i + 1}>
              <PaginationLink
                onClick={() => setPage(i + 1)}
                isActive={page === i + 1}
              >
                {i + 1}
              </PaginationLink>
            </PaginationItem>
          ))}
          <PaginationItem>
            <PaginationLink
              onClick={handleNextPage}
              aria-disabled={page === totalPages}
            >
              Next
            </PaginationLink>
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
};
