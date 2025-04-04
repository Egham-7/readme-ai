import Navbar from "@/components/landing-page/navbar";
import Hero from "@/components/landing-page/hero";
import ProductPreview from "@/components/landing-page/product-preview";
import Features from "@/components/landing-page/features";
import CTA from "@/components/landing-page/cta";

export function LandingPage() {
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
