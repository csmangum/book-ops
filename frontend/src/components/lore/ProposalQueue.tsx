import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/shared/EmptyState";
import type { LoreProposal } from "@/lib/lore";

export function ProposalQueue({ proposals }: { proposals: LoreProposal[] }) {
  if (proposals.length === 0) {
    return (
      <EmptyState
        title="No proposals"
        description="Generate lore delta for chapter or project scope to populate this queue."
      />
    );
  }

  return (
    <ul className="space-y-2">
      {proposals.map((proposal) => (
        <li key={proposal.id} className="rounded-md border p-3">
          <div className="flex items-center justify-between gap-2">
            <Link className="text-sm font-medium hover:underline" href={`/lore/${proposal.id}`}>
              {proposal.id}
            </Link>
            <Badge variant="outline">{proposal.status ?? "pending_review"}</Badge>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">{proposal.reason}</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Target: {proposal.target_lore_file ?? "unknown"}
          </p>
        </li>
      ))}
    </ul>
  );
}
