import * as React from "react";
import { Files, Home } from "lucide-react";
import { NavMain } from "@/components/nav-main";
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar";
import { Link } from "@tanstack/react-router";
import { siGithub as Github } from "simple-icons";
import { UserButton } from "@clerk/clerk-react";

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
];

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <div className="flex items-center gap-2 px-4 py-2 w-full">
          <Link className="font-semibold flex items-center gap-x-2" to="/home">
            <svg
              role="img"
              viewBox="0 0 24 24"
              width="24"
              height="24"
              fill="currentColor"
            >
              <path d={Github.path} />
            </svg>
            ReadYou
          </Link>
        </div>
      </SidebarHeader>
      <SidebarContent className="justify-between h-full">
        <NavMain items={navigationItems} />

        <div className="w-full flex justify-start items-center px-4 py-2">
          <UserButton />
        </div>
      </SidebarContent>
      <SidebarRail />
    </Sidebar>
  );
}
