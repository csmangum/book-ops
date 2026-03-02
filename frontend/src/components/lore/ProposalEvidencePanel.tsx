import { EvidenceSnippet } from "@/components/chapters/EvidenceSnippet";
import { EmptyState } from "@/components/shared/EmptyState";
import type { LoreProposal } from "@/lib/lore";

export function ProposalEvidencePanel({ proposal }: { proposal: LoreProposal }) {
  if (!proposal.evidence || proposal.evidence.length === 0) {
    return (
      <EmptyState
        title="No evidence snippets"
        description="Evidence references are not available for this proposal."
      />
    );
  }

  return (
    <div className="space-y-2">
      {proposal.evidence.map((evidence, index) => (
        <EvidenceSnippet
          key={`${evidence.file}-${evidence.line_hint}-${index}`}
          evidence={{
            file: evidence.file,
            line_start: evidence.line_hint,
            line_end: evidence.line_hint,
            excerpt: evidence.excerpt,
          }}
        />
      ))}
    </div>
  );
}
