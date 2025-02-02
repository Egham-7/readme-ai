import * as React from "react";
import { BookOpen, Files, FileText, Github, Home } from "lucide-react";
import { NavMain } from "@/components/nav-main";
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";
import { Link } from "@tanstack/react-router";

const navigationItems = [
  {
    title: "Home",
    url: "/home/",
    icon: Home,
    isActive: true,
  },
  {
    title: "Templates",
    url: "/templates",
    icon: Files,
    items: [
      {
        title: "Featured",
        url: "/templates/featured",
      },
      {
        title: "Community",
        url: "/templates/community",
      },
    ],
  },
  {
    title: "Documentation",
    url: "/docs",
    icon: BookOpen,
    items: [
      {
        title: "Getting Started",
        url: "/docs/getting-started",
      },
      {
        title: "Markdown Guide",
        url: "/docs/markdown-guide",
      },
    ],
  },
  {
    title: "Examples",
    url: "/examples",
    icon: FileText,
    items: [
      {
        title: "Basic README",
        url: "/examples/basic",
      },
      {
        title: "Project README",
        url: "/examples/project",
      },
    ],
  },
];

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <div className="flex items-center gap-2 px-4 py-2">
          <Github className="h-6 w-6" />
          <Link className="font-semibold" to="/home">
            README Generator
          </Link>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={navigationItems} />
      </SidebarContent>
      <SidebarRail />
    </Sidebar>
  );
}
