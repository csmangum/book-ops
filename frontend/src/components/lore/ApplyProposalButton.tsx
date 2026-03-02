"use client";

import { Button } from "@/components/ui/button";
import { useLoreSync } from "@/hooks";
import type { LoreProposal } from "@/lib/lore";

export function ApplyProposalButton({ proposal }: { proposal: LoreProposal }) {
  const apply = useLoreSync();
  const canApply = proposal.status === "approved";

  return (
    <Button
      variant="outline"
      disabled={!canApply || apply.isPending}
      onClick={() => {
        const confirmed = window.confirm(
          "Apply this lore proposal? This writes to lore files.",
        );
        if (!confirmed) {
          return;
        }

        apply.mutate({
          proposal: proposal.id,
          apply: true,
        });
      }}
    >
      Apply proposal
    </Button>
  );
}
