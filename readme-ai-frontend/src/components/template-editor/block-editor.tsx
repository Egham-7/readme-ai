import { useState, type Dispatch, type SetStateAction } from "react";
import { type DragEndEvent, closestCenter } from "@dnd-kit/core";
import { arrayMove } from "@dnd-kit/sortable";
import Sidebar from "./sidebar";
import { Button } from "../ui/button";
import { DndContext } from "@dnd-kit/core";
import Preview from "./preview";
import { type BlockContent, BLOCKS } from "./markdown-blocks";

function BlockEditor({
  onSave,
  blocks,
  setBlocks,
}: {
  onSave: (markdown: string) => void;
  blocks: BlockContent[];
  setBlocks: Dispatch<SetStateAction<BlockContent[]>>;
}) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over) return;

    if (over.id === "preview") {
      const blockId = active.id.toString().split("-")[1];
      const uniqueId = `${blockId}-${Date.now().toString()}`;
      const block = BLOCKS.find((b) => b.id === blockId);

      setBlocks((items) => [
        ...items,
        { id: uniqueId, content: block?.content || "" },
      ]);
      return;
    }

    const activeId = active.id.toString();
    const overId = over.id.toString();

    if (activeId !== overId) {
      setBlocks((items) => {
        const oldIndex = items.findIndex((block) => block.id === activeId);
        const newIndex = items.findIndex((block) => block.id === overId);
        return arrayMove(items, oldIndex, newIndex);
      });
    }
  };

  const handleBlockAdd = (id: string) => {
    const block = BLOCKS.find((b) => b.id === id);
    const uniqueId = `${id}-${Date.now().toString()}`;
    setBlocks((items) => [
      ...items,
      { id: uniqueId, content: block?.content || "" },
    ]);
    setIsSidebarOpen(false);
  };

  return (
    <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <div className="flex h-full flex-col">
        <div className="lg:hidden">
          <Button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="m-4"
          >
            {isSidebarOpen ? "Close Blocks" : "Show Blocks"}
          </Button>
        </div>
        <div className="flex-1 flex flex-col lg:flex-row relative">
          <div
            className={`
            ${isSidebarOpen ? "block" : "hidden"} 
            lg:block
            absolute lg:relative
            z-10 w-full lg:w-auto
            bg-background lg:bg-transparent
          `}
          >
            <Sidebar onBlockAdd={handleBlockAdd} />
          </div>
          <Preview blocks={blocks} setBlocks={setBlocks} onSave={onSave} />
        </div>
      </div>
    </DndContext>
  );
}

export default BlockEditor;
