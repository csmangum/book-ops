"use client";

import { Button } from "@/components/ui/button";
import { useLoreApprove } from "@/hooks";
import type { LoreProposal } from "@/lib/lore";

export function ApproveRejectActions({
  proposal,
  onRejected,
}: {
  proposal: LoreProposal;
  onRejected?: (proposalId: string) => void;
}) {
  const approve = useLoreApprove();

  return (
    <div className="flex flex-wrap gap-2">
      <Button
        onClick={() =>
          approve.mutate({
            proposal: proposal.id,
            reviewer: "bookops-ui",
            note: "Approved from Lore Sync Studio.",
          })
        }
      >
        Approve
      </Button>
      <Button
        variant="outline"
        onClick={() => onRejected?.(proposal.id)}
      >
        Reject
      </Button>
    </div>
  );
}
