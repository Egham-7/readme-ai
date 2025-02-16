import TemplateGridSkeleton from "./template-grid-skeleton";

const TemplatesContentSkeleton = () => (
  <div className="space-y-4">
    <div className="flex flex-col md:flex-row gap-3 md:gap-0 md:justify-between md:items-center">
      <div className="h-7 w-48 bg-muted rounded animate-pulse" />
      <div className="h-10 w-32 bg-muted rounded animate-pulse" />
    </div>
    <TemplateGridSkeleton />
  </div>
);

export default TemplatesContentSkeleton;
