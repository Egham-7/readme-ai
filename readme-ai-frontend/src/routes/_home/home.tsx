import { HomePage } from "@/pages/home-page";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_home/home")({
  component: HomePage,
});
