import { type Template } from "@/services/templates";
import TemplateCard from "./template-card";
import DefaultTemplateCard from "./default-template-card";

const TemplateGrid = ({
  templates,
  onSelect,
}: {
  templates: Template[];
  onSelect: (templateId?: number) => void;
}) => (
  <div className=" w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
    {templates.map((template) => (
      <TemplateCard key={template.id} template={template} onSelect={onSelect} />
    ))}
    <DefaultTemplateCard onSelect={() => onSelect(undefined)} />
  </div>
);

export default TemplateGrid;
