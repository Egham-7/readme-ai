import EditTemplate from "@/pages/edit-template";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_home/templates/update/$templateId")({
  component: RouteComponent,
});

function RouteComponent() {
  return <EditTemplate />;
}
