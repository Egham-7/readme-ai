import { createFileRoute } from "@tanstack/react-router";
import { AppSidebar } from "@/components/app-sidebar";
import { Outlet } from "@tanstack/react-router";
import { SidebarProvider } from "@/components/ui/sidebar";
import { useAuthGuard } from "@/hooks/use-auth";

export const Route = createFileRoute("/_home")({
  component: LayoutComponent,
});

function LayoutComponent() {
  const { isAuthenticated, isLoading } = useAuthGuard();

  if (isLoading) return null;

  if (!isAuthenticated) {
    return null;
  }

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
