import * as React from "react";
import { Outlet, createRootRoute } from "@tanstack/react-router";
import { Toaster } from "@/components/ui/toaster";

export const Route = createRootRoute({
  component: RootComponent,
});

function RootComponent() {
  return (
    <React.Fragment>
      <main className="min-h-screen  min-w-screen py-8 px-8 ">
        <Outlet />
      </main>
      <Toaster />
    </React.Fragment>
  );
}
