export type LoreProposal = {
  id: string;
  status?: string;
  chapter?: number;
  target_lore_file?: string;
  reason?: string;
  evidence?: Array<{
    file?: string;
    line_hint?: number;
    excerpt?: string;
  }>;
  conflict?: boolean;
};

export function proposalHasConflict(proposal: LoreProposal) {
  if (proposal.conflict) {
    return true;
  }

  const reason = (proposal.reason ?? "").toLowerCase();
  return reason.includes("conflict") || reason.includes("contradiction");
}
