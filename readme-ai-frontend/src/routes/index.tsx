import { createFileRoute } from "@tanstack/react-router";
import CTA from "@/components/landing-page/cta";
import Hero from "@/components/landing-page/hero";
import ProductPreview from "@/components/landing-page/product-preview";
import Features from "@/components/landing-page/features";
import Footer from "@/components/landing-page/footer";
import Navbar from "@/components/landing-page/navbar";

export const Route = createFileRoute("/")({
  component: HomeRoute,
});

function HomeRoute() {
  return (
    <div className="bg-background text-foreground">
      <Navbar />

      <Hero />
      <ProductPreview />
      <Features />
      <CTA />
      <Footer />
    </div>
  );
}
