import { ChevronRight, Lock, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

export default function ReadmeChatSkeleton() {
  return (
    <div className="flex h-screen flex-col">
      {/* Header Skeleton */}
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
          {/* Version dropdown skeleton */}
          <Skeleton className="h-8 w-24" />
          {/* Save button skeleton */}
          <Skeleton className="h-8 w-20" />
          {/* Copy button skeleton */}
          <Skeleton className="h-8 w-20" />
        </div>
      </header>

      {/* Main content skeleton */}
      <div className="flex flex-1 overflow-hidden">
        {/* Chat interface skeleton */}
        <div className="flex w-1/2 flex-col border-r">
          <div className="border-b p-4">
            <h2 className="text-lg font-semibold">
              Chat with README Assistant
            </h2>
            <p className="text-sm text-muted-foreground">
              Ask me to help improve your README file
            </p>
          </div>

          {/* Chat messages skeleton */}
          <div className="flex-1 p-4">
            <div className="flex justify-start mb-4">
              <Skeleton className="h-[80px] w-[80%] rounded-lg" />
            </div>
            <div className="flex justify-end mb-4">
              <Skeleton className="h-[60px] w-[70%] rounded-lg" />
            </div>
            <div className="flex justify-start">
              <Skeleton className="h-[100px] w-[80%] rounded-lg" />
            </div>
          </div>

          {/* Chat input skeleton */}
          <div className="border-t p-4">
            <div className="flex items-center gap-2">
              <Skeleton className="h-10 flex-1" />
              <Skeleton className="h-10 w-10 rounded-md" />
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              Try: "Add badges", "Add table of contents", "Improve code
              examples", "Expand features"
            </div>
          </div>
        </div>

        {/* Markdown preview skeleton */}
        <div className="flex-1 border-l overflow-hidden p-4">
          <Skeleton className="h-10 w-3/4 mb-6" />
          <Skeleton className="h-6 w-full mb-4" />
          <Skeleton className="h-6 w-full mb-4" />
          <Skeleton className="h-6 w-4/5 mb-4" />
          <Skeleton className="h-32 w-full mb-6 rounded-md" />
          <Skeleton className="h-8 w-2/3 mb-4" />
          <Skeleton className="h-6 w-full mb-2" />
          <Skeleton className="h-6 w-full mb-2" />
          <Skeleton className="h-6 w-3/4 mb-6" />
        </div>
      </div>
    </div>
  );
}
