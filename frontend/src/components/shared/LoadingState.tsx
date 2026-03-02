import { Loader2 } from "lucide-react";

import { Skeleton } from "@/components/ui/skeleton";

export function LoadingState({
  label = "Loading...",
  withSkeleton = true,
}: {
  label?: string;
  withSkeleton?: boolean;
}) {
  return (
    <div className="space-y-3 rounded-md border p-4">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Loader2 className="size-4 animate-spin" />
        <span>{label}</span>
      </div>
      {withSkeleton ? (
        <div className="space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </div>
      ) : null}
    </div>
  );
}
