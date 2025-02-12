import { Facebook, Twitter, Instagram, Linkedin } from "lucide-react";
import { Link } from "@tanstack/react-router";

const productLinks = [
  { name: "Features", href: "#features" },
  { name: "Pricing", href: "#pricing" },
  { name: "Templates", href: "#templates" },
  { name: "Documentation", href: "#docs" },
];

const companyLinks = [
  { name: "About Us", href: "#about" },
  { name: "Blog", href: "#blog" },
  { name: "GitHub", href: "#github" },
  { name: "Contact", href: "#contact" },
];

const socialLinks = [
  { icon: Facebook, href: "#" },
  { icon: Twitter, href: "#" },
  { icon: Instagram, href: "#" },
  { icon: Linkedin, href: "#" },
];

export default function Footer() {
  return (
    <footer className="bg-background text-foreground py-12">
      <div className="container mx-auto grid grid-cols-1 md:grid-cols-4 gap-8">
        <div>
          <h3 className="text-lg font-semibold mb-4">ReadYou</h3>
          <p className="text-muted-foreground">
            Crafting perfect documentation with AI.
          </p>
        </div>

        <div>
          <h4 className="text-lg font-semibold mb-4">Product</h4>
          <ul className="space-y-2">
            {productLinks.map((link) => (
              <li key={link.name}>
                <Link
                  to={link.href}
                  className="text-muted-foreground hover:text-foreground"
                >
                  {link.name}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h4 className="text-lg font-semibold mb-4">Company</h4>
          <ul className="space-y-2">
            {companyLinks.map((link) => (
              <li key={link.name}>
                <Link
                  to={link.href}
                  className="text-muted-foreground hover:text-foreground"
                >
                  {link.name}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h4 className="text-lg font-semibold mb-4">Connect</h4>
          <div className="flex space-x-4">
            {socialLinks.map((social, index) => (
              <Link
                key={`social-${index.toString()}`}
                to={social.href}
                className="text-muted-foreground hover:text-foreground"
              >
                <social.icon className="h-6 w-6" />
              </Link>
            ))}
          </div>
        </div>
      </div>

      <div className="container mx-auto mt-8 pt-8 border-t border-border text-center text-muted-foreground">
        <p>&copy; {new Date().getFullYear()} ReadYou. All rights reserved.</p>
      </div>
    </footer>
  );
}
