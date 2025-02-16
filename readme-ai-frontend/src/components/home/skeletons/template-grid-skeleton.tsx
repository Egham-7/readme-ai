import TemplateSkeleton from "./template-skeleton";

const TemplateGridSkeleton = () => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4">
    {Array.from({ length: 6 }).map((_, i) => (
      <TemplateSkeleton key={i} />
    ))}
  </div>
);

export default TemplateGridSkeleton;
