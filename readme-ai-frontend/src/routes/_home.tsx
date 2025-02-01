import { createFileRoute } from "@tanstack/react-router";
import { AppSidebar } from "@/components/app-sidebar";
import { Outlet } from "@tanstack/react-router";
import { SidebarProvider } from "@/components/ui/sidebar";

export const Route = createFileRoute("/_home")({
  component: LayoutComponent,
});

function LayoutComponent() {
  return (
    <SidebarProvider>
      <div className="flex h-screen w-screen">
        <AppSidebar />
        <main className="flex-1 overflow-auto ">
          <Outlet />
        </main>
      </div>
    </SidebarProvider>
  );
}
