import { createFileRoute } from "@tanstack/react-router";
import { LandingPage } from "@/pages/landing-page";

export const Route = createFileRoute("/")({
  component: LandingPageRoute,
});

function LandingPageRoute() {
  return <LandingPage />;
}
