import { Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { SignInButton, SignUpButton } from "@clerk/clerk-react";

const navLinks = [
  { name: "Features", to: "features" },
  { name: "Templates", to: "templates" },
  { name: "Pricing", to: "pricing" },
  { name: "Docs", to: "docs" },
];

export default function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link
              to="/"
              className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent"
            >
              ReadYou
            </Link>
            <div className="hidden md:block ml-10">
              <div className="flex items-center space-x-8">
                {navLinks.map((link) => (
                  <Link
                    key={link.name}
                    to={"/"}
                    className="text-sm text-muted-foreground hover:text-foreground"
                  >
                    {link.name}
                  </Link>
                ))}
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <SignInButton forceRedirectUrl="/home">
              <Button variant="ghost" className="text-sm">
                Sign In
              </Button>
            </SignInButton>
            <SignUpButton forceRedirectUrl="/home">
              <Button className="text-sm bg-gradient-to-r from-primary to-accent hover:opacity-90">
                Get Started
              </Button>
            </SignUpButton>
          </div>
        </div>
      </div>
    </nav>
  );
}
