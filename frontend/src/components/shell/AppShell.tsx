import { SidebarNav } from "@/components/shell/SidebarNav";
import { TopBar } from "@/components/shell/TopBar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="grid min-h-screen grid-cols-1 md:grid-cols-[240px_1fr]">
        <aside className="hidden border-r p-3 md:block">
          <div className="mb-4 px-2 py-1">
            <p className="text-sm font-semibold">BookOps</p>
            <p className="text-xs text-muted-foreground">Writer Ops Console</p>
          </div>
          <SidebarNav />
        </aside>
        <div className="flex min-w-0 flex-col">
          <TopBar />
          <main className="flex-1 p-4">{children}</main>
        </div>
      </div>
    </div>
  );
}
