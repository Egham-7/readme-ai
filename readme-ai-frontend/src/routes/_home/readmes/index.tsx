import Readmes from "@/pages/readmes";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_home/readmes/")({
  component: RouteComponent,
});

function RouteComponent() {
  return <Readmes />;
}
