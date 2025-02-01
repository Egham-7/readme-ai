import { BookOpen, Sparkles, Palette } from "lucide-react";

const features = [
  {
    icon: <Sparkles className="h-8 w-8 text-primary" />,
    title: "AI-Powered Generation",
    description:
      "Smart README generation using advanced LLMs that understand your codebase.",
  },
  {
    icon: <Palette className="h-8 w-8 text-primary" />,
    title: "Custom Templates",
    description:
      "Choose from beautiful templates or create your own documentation style.",
  },
  {
    icon: <BookOpen className="h-8 w-8 text-primary" />,
    title: "Smart Documentation",
    description:
      "Automatically extract key features, dependencies, and setup instructions.",
  },
];

export default function Features() {
  return (
    <section id="features" className="py-20 bg-background">
      <div className="container mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12 text-foreground">
          Craft Perfect Documentation
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className="bg-card p-6 rounded-lg shadow-md">
              <div className="mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold mb-2 text-card-foreground">
                {feature.title}
              </h3>
              <p className="text-muted-foreground">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
