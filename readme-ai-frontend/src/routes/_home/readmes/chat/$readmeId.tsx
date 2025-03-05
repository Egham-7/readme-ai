import { ReadmeChat } from "@/pages/readme-chat";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_home/readmes/chat/$readmeId")({
  component: ReadmeChat,
});
