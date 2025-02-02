import { useDroppable } from "@dnd-kit/core";
import { SortableContext, useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { BLOCKS, CATEGORIES } from "./markdown-blocks";
import { Button } from "../ui/button";

interface Block {
  id: string;
  label: string;
  category: string;
  icon: React.ComponentType<{ className?: string }>;
}

interface DraggableItemProps {
  block: Block;
  index: number;
  category: string;
  onBlockSelect: (blockId: string) => void;
}

function DraggableItem({
  block,
  index,
  category,
  onBlockSelect,
}: DraggableItemProps) {
  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({
      id: `${category}-${block.id}-${index.toString()}`,
    });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const handleClick = () => {
    if (!transform) {
      onBlockSelect(block.id);
    }
  };

  return (
    <div className="flex items-center justify-between p-2">
      <div
        ref={setNodeRef}
        style={style}
        {...attributes}
        {...listeners}
        className="flex items-center p-2 m-2 bg-muted rounded-md cursor-pointer hover:bg-accent transition-colors active:bg-accent/90"
        role="button"
        tabIndex={0}
      >
        <block.icon className="mr-2 h-5 w-5 text-muted-foreground" />
        <span className="text-foreground">{block.label}</span>
      </div>
      <Button
        variant="outline"
        size="sm"
        onClick={handleClick}
        className="text-muted-foreground hover:text-foreground"
      >
        <span className="text-xs font-medium">Add</span>
      </Button>
    </div>
  );
}

interface SidebarProps {
  onBlockAdd: (blockId: string) => void;
}

export default function Sidebar({ onBlockAdd }: SidebarProps) {
  const { setNodeRef } = useDroppable({ id: "sidebar" });

  const handleBlockSelect = (blockId: string) => {
    const uniqueId = `${blockId}-${Date.now().toString()}`;
    onBlockAdd(uniqueId);
  };

  return (
    <div className="bg-card border-r border-border p-3 rounded-xl">
      <h2 className="text-xl font-bold p-4 text-foreground">Markdown Blocks</h2>
      <div ref={setNodeRef}>
        {CATEGORIES.map((category) => (
          <div key={category} className="mb-4">
            <h3 className="font-semibold px-4 py-2 bg-muted text-foreground">
              {category}
            </h3>
            <SortableContext
              items={BLOCKS.filter((block) => block.category === category).map(
                (block, index) => `${category}-${block.id}-${index.toString()}`,
              )}
            >
              {BLOCKS.filter((block) => block.category === category).map(
                (block, index) => (
                  <DraggableItem
                    key={`${category}-${block.id}-${index.toString()}`}
                    block={block}
                    index={index}
                    category={category}
                    onBlockSelect={handleBlockSelect}
                  />
                ),
              )}
            </SortableContext>
          </div>
        ))}
      </div>
    </div>
  );
}
