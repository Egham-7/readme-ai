import { Plus, Lock, ChevronRight, Save, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface HeaderProps {
  currentVersion: number;
  onSave: () => void;
  onCopy: () => void;
}

export function Header({ currentVersion, onSave, onCopy }: HeaderProps) {
  return (
    <header className="flex h-14 items-center border-b px-4 lg:px-6">
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <Plus className="h-4 w-4" />
          <span className="sr-only">New Project</span>
        </Button>
        <div className="flex items-center gap-1 text-sm font-medium">
          <span>README Editor with AI Chat</span>
          <ChevronRight className="h-4 w-4 text-muted-foreground" />
        </div>
        <Button variant="ghost" size="sm" className="h-8 gap-1 text-xs">
          <Lock className="h-3.5 w-3.5" />
          <span>Private</span>
        </Button>
      </div>
      <div className="ml-auto flex items-center gap-2">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="h-8 gap-1">
              <span>Version {currentVersion}</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>Version 1 (Initial)</DropdownMenuItem>
            {currentVersion > 1 && (
              <DropdownMenuItem>
                Version {currentVersion} (Current)
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
        <Button
          variant="outline"
          size="sm"
          className="h-8 gap-1"
          onClick={onSave}
        >
          <Save className="h-4 w-4" />
          <span>Save</span>
        </Button>
        <Button
          variant="outline"
          size="sm"
          className="h-8 gap-1"
          onClick={onCopy}
        >
          <Copy className="h-4 w-4" />
          <span>Copy</span>
        </Button>
      </div>
    </header>
  );
}
