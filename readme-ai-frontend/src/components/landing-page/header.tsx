import { Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";

const navLinks = [
  { name: "Features", to: "features" },
  { name: "Templates", to: "templates" },
  { name: "Pricing", to: "pricing" },
];

export default function Header() {
  return (
    <header className="py-4 px-6 bg-background border-b border-border">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold text-primary">
          ReadYou
        </Link>

        <nav className="hidden md:flex space-x-6">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              to={link.to}
              className="text-muted-foreground hover:text-primary"
            >
              {link.name}
            </Link>
          ))}
        </nav>

        <Button>Try ReadYou</Button>
      </div>
    </header>
  );
}
