import { createFileRoute } from "@tanstack/react-router";
import CreateTemplates from "@/pages/create-templates";

export const Route = createFileRoute("/_home/templates/create/")({
  component: CreateTemplates,
});
