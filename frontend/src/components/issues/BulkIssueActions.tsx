"use client";

import { Button } from "@/components/ui/button";
import { useIssueUpdate, useIssueWaive } from "@/hooks";

export function BulkIssueActions({
  selectedIssueIds,
  onCleared,
}: {
  selectedIssueIds: string[];
  onCleared: () => void;
}) {
  const updateIssue = useIssueUpdate();
  const waiveIssue = useIssueWaive();

  if (selectedIssueIds.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-wrap items-center gap-2 rounded-md border p-3">
      <p className="text-sm text-muted-foreground">
        {selectedIssueIds.length} selected
      </p>
      <Button
        size="sm"
        variant="outline"
        onClick={async () => {
          await Promise.all(
            selectedIssueIds.map((issueId) =>
              updateIssue.mutateAsync({
                issueId,
                body: { status: "resolved", note: "Bulk resolved." },
              }),
            ),
          );
          onCleared();
        }}
      >
        Resolve selected
      </Button>
      <Button
        size="sm"
        variant="outline"
        onClick={async () => {
          await Promise.all(
            selectedIssueIds.map((issueId) =>
              waiveIssue.mutateAsync({
                issueId,
                body: {
                  reason: "Bulk waiver action.",
                  reviewer: "bookops-ui",
                },
              }),
            ),
          );
          onCleared();
        }}
      >
        Waive selected
      </Button>
    </div>
  );
}
