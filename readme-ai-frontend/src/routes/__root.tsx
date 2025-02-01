import * as React from "react";
import { Outlet, createRootRoute } from "@tanstack/react-router";

export const Route = createRootRoute({
  component: RootComponent,
});

function RootComponent() {
  return (
    <React.Fragment>
      <main className="min-h-screen  min-w-screen pt-16 ">
        <Outlet />
      </main>
    </React.Fragment>
  );
}
