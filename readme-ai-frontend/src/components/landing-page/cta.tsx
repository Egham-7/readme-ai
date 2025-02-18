import { Button } from "@/components/ui/button";
import { SignedIn, SignUpButton, SignedOut } from "@clerk/clerk-react";
import { Link } from "@tanstack/react-router";

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

        <SignedIn>
          <Link className="relative z-10" to="/home">
            <Button
              className="relative group px-8 py-6 text-lg rounded-full bg-gradient-to-r from-primary via-accent to-primary bg-[length:200%_200%] bg-left hover:bg-right transition-all duration-500"
              size="lg"
            >
              Generate Your First README
              <div className="absolute inset-0 rounded-full bg-white/20 blur-xl group-hover:blur-2xl transition-all duration-300 opacity-0 group-hover:opacity-100" />
            </Button>
          </Link>
        </SignedIn>
        <SignedOut>
          <SignUpButton mode="modal">
            <Button
              className="relative group px-8 py-6 text-lg rounded-full bg-gradient-to-r from-primary via-accent to-primary bg-[length:200%_200%] bg-left hover:bg-right transition-all duration-500"
              size="lg"
            >
              Generate Your First README
              <div className="absolute inset-0 rounded-full bg-white/20 blur-xl group-hover:blur-2xl transition-all duration-300 opacity-0 group-hover:opacity-100" />
            </Button>
          </SignUpButton>
        </SignedOut>
      </div>
    </section>
  );
}
