"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Command Center" },
  { href: "/chapters", label: "Chapters" },
  { href: "/lore", label: "Lore Sync" },
  { href: "/timeline", label: "Timeline" },
  { href: "/canon", label: "Canon Graph" },
  { href: "/rules", label: "Rules" },
  { href: "/runs", label: "Runs" },
  { href: "/issues", label: "Issues" },
  { href: "/settings", label: "Settings" },
];

export function SidebarNav() {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col gap-1">
      {navItems.map((item) => {
        const active = pathname === item.href || pathname.startsWith(`${item.href}/`);

        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground",
              active && "bg-primary text-primary-foreground hover:bg-primary/90 hover:text-primary-foreground",
            )}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
