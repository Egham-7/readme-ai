import { createFileRoute } from "@tanstack/react-router";
import CreateTemplate from "@/pages/create-template";

export const Route = createFileRoute("/_home/templates/create/")({
  component: CreateTemplate,
});
