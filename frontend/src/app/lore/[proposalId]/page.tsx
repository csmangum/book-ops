"use client";

import { useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { AlertTriangle } from "lucide-react";

import {
  ApplyProposalButton,
  ApproveRejectActions,
  LoreDiffViewer,
  ProposalEvidencePanel,
} from "@/components/lore";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { proposalHasConflict, type LoreProposal } from "@/lib/lore";

export default function LoreProposalDetailPage() {
  const params = useParams<{ proposalId: string }>();
  const [localStatus, setLocalStatus] = useState<string>("pending_review");

  const proposal = useMemo<LoreProposal>(
    () => ({
      id: params.proposalId,
      status: localStatus,
      reason:
        "Proposal detail endpoint is not available in the current backend contract. Showing scaffolded detail panel.",
      target_lore_file: "lore/placeholder.md",
      evidence: [],
    }),
    [localStatus, params.proposalId],
  );

  return (
    <div className="space-y-4">
      <section>
        <h2 className="text-xl font-semibold">Lore Proposal Detail</h2>
        <p className="text-sm text-muted-foreground">
          Proposal-level review, evidence, and gated apply controls.
        </p>
      </section>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {proposal.id}
            <Badge variant="outline">{proposal.status}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {proposalHasConflict(proposal) ? (
            <div className="rounded-md border border-amber-300 bg-amber-50 p-3 text-amber-900">
              <p className="flex items-center gap-2 text-sm font-medium">
                <AlertTriangle className="size-4" />
                Potential story-over-lore conflict detected.
              </p>
            </div>
          ) : null}
          <LoreDiffViewer proposal={proposal} />
          <ProposalEvidencePanel proposal={proposal} />
          <div className="flex flex-wrap gap-2">
            <ApproveRejectActions
              proposal={proposal}
              onRejected={() => setLocalStatus("rejected")}
            />
            <ApplyProposalButton proposal={proposal} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
