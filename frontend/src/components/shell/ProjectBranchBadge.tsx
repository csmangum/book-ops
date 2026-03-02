import { GitBranch } from "lucide-react";

import { Badge } from "@/components/ui/badge";

const branchName = process.env.NEXT_PUBLIC_BOOKOPS_BRANCH;

export function ProjectBranchBadge() {
  if (!branchName) {
    return null;
  }

  return (
    <Badge variant="outline" className="gap-1">
      <GitBranch className="size-3" />
      {branchName}
    </Badge>
  );
}
