"use client";

import { ProjectBranchBadge } from "@/components/shell/ProjectBranchBadge";
import { RunPipelineButton } from "@/components/shell/RunPipelineButton";
import { GlobalSearch } from "@/components/shell/GlobalSearch";
import { useVersion } from "@/hooks";

export function TopBar() {
  const versionQuery = useVersion();
  const version = versionQuery.data?.bookops_version;

  return (
    <header className="sticky top-0 z-10 flex flex-wrap items-center justify-between gap-3 border-b bg-background/95 px-4 py-3 backdrop-blur">
      <div className="flex items-center gap-2">
        <h1 className="text-base font-semibold">BookOps Console</h1>
        <ProjectBranchBadge />
        {version ? (
          <span className="rounded-md border px-2 py-1 text-xs text-muted-foreground">
            v{version}
          </span>
        ) : null}
      </div>
      <div className="flex flex-1 items-center justify-end gap-3">
        <GlobalSearch />
        <RunPipelineButton />
      </div>
    </header>
  );
}
