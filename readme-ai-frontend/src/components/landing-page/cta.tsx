import { Button } from "@/components/ui/button";

export default function CTA() {
  return (
    <section className="py-20 bg-primary text-white">
      <div className="container mx-auto text-center">
        <h2 className="text-3xl font-bold mb-6">
          Transform Your Repository Documentation
        </h2>
        <p className="text-xl mb-8 max-w-2xl mx-auto">
          Let ReadYou's AI craft the perfect README for your projects in
          seconds.
        </p>
        <Button size="lg" variant="secondary">
          Generate Your First README
        </Button>
      </div>
    </section>
  );
}
