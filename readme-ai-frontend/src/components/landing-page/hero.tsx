import { Button } from "@/components/ui/button";
import { Link } from "@tanstack/react-router";
import { motion } from "framer-motion";
import { SignUpButton, SignedIn, SignedOut } from "@clerk/clerk-react";

export default function Hero() {
  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-b from-background to-secondary/20">
      {/* Background decoration */}
      <div className="absolute inset-0 w-full h-full dark:bg-grid-white/[0.2] bg-grid-black/[0.2] bg-[size:60px_60px] pointer-events-none" />
      <div className="absolute inset-0 flex items-center justify-center bg-background [mask-image:radial-gradient(ellipse_at_center,transparent_20%,black)]" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-32 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-5xl sm:text-6xl lg:text-8xl font-bold tracking-tight mb-8 bg-clip-text text-transparent bg-gradient-to-r from-primary via-accent to-primary">
            Perfect READMEs
          </h1>
          <p className="max-w-2xl mx-auto text-xl sm:text-2xl text-muted-foreground mb-12 leading-relaxed">
            ReadYou uses advanced AI to analyze your repository and create
            beautiful, comprehensive documentation that truly represents your
            project.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
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
              <SignUpButton mode="modal" signInForceRedirectUrl="/home">
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
        </motion.div>

        {/* Decorative elements */}
        <div className="absolute top-1/2 left-0 -translate-y-1/2 w-1/3 h-1/3 bg-accent/20 rounded-full blur-3xl" />
        <div className="absolute top-1/2 right-0 -translate-y-1/2 w-1/3 h-1/3 bg-primary/20 rounded-full blur-3xl" />
      </div>
    </div>
  );
}
