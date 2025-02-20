import { createFileRoute } from "@tanstack/react-router";
import CTA from "@/components/landing-page/cta";
import Hero from "@/components/landing-page/hero";
import ProductPreview from "@/components/landing-page/product-preview";
import Features from "@/components/landing-page/features";
import Navbar from "@/components/landing-page/navbar";

export const Route = createFileRoute("/")({
  component: LandingPageRoute,
});

function LandingPageRoute() {
  return (
    <div className="bg-background text-foreground">
      <Navbar />

      <Hero />
      <ProductPreview />
      <Features />
      <CTA />
    </div>
  );
}
