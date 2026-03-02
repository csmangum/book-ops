"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { useIssueUpdate, useIssueWaive } from "@/hooks";

export function TriageActions({ issueId }: { issueId: string }) {
  const [isWaiving, setIsWaiving] = useState(false);
  const updateIssue = useIssueUpdate();
  const waiveIssue = useIssueWaive();

  return (
    <div className="flex flex-wrap gap-2">
      <Button
        size="sm"
        variant="outline"
        onClick={() =>
          updateIssue.mutate({
            issueId,
            body: { status: "resolved", note: "Resolved from chapter workbench." },
          })
        }
      >
        Resolve
      </Button>
      <Button
        size="sm"
        variant="outline"
        onClick={() =>
          updateIssue.mutate({
            issueId,
            body: { status: "in_progress", note: "Triage in progress." },
          })
        }
      >
        In progress
      </Button>
      <Button
        size="sm"
        variant="outline"
        disabled={isWaiving}
        onClick={async () => {
          setIsWaiving(true);
          await waiveIssue.mutateAsync({
            issueId,
            body: {
              reason: "Accepted with editorial waiver.",
              reviewer: "bookops-ui",
            },
          });
          setIsWaiving(false);
        }}
      >
        Waive
      </Button>
    </div>
  );
}
