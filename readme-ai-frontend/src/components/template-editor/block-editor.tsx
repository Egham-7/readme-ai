import { useState } from "react";
import { type DragEndEvent, closestCenter } from "@dnd-kit/core";
import { arrayMove } from "@dnd-kit/sortable";
import Sidebar from "./sidebar";
import { Button } from "../ui/button";
import { DndContext } from "@dnd-kit/core";
import Preview from "./preview";

function BlockEditor({ onSave }: { onSave: (markdown: string) => void }) {
  const [blocks, setBlocks] = useState<string[]>([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over) return;

    if (over.id === "preview") {
      const blockId = active.id.toString().split("-")[1];
      const uniqueId = `${blockId}-${Date.now().toString()}`;
      setBlocks((items) => [...items, uniqueId]);
      return;
    }

    const activeId = active.id.toString();
    const overId = over.id.toString();

    if (activeId !== overId) {
      setBlocks((items) => {
        const oldIndex = items.indexOf(activeId);
        const newIndex = items.indexOf(overId);
        return arrayMove(items, oldIndex, newIndex);
      });
    }
  };

  const handleBlockAdd = (id: string) => {
    setBlocks((items) => [...items, id]);
    setIsSidebarOpen(false); // Close sidebar after adding block on mobile
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
