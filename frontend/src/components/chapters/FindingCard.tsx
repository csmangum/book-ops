import { SeverityBadge } from "@/components/shared/SeverityBadge";
import { EvidenceSnippet } from "@/components/chapters/EvidenceSnippet";
import { TriageActions } from "@/components/chapters/TriageActions";

type Finding = {
  id?: string;
  rule_id?: string;
  severity?: string;
  message?: string;
  evidence?: Array<{
    file?: string;
    line_start?: number;
    line_end?: number;
    excerpt?: string;
  }>;
};

export function FindingCard({ finding }: { finding: Finding }) {
  return (
    <article className="space-y-3 rounded-md border p-3">
      <header className="flex items-center justify-between gap-2">
        <p className="text-sm font-semibold">{finding.rule_id ?? "Unknown rule"}</p>
        <SeverityBadge severity={finding.severity ?? "info"} />
      </header>
      <p className="text-sm text-muted-foreground">{finding.message}</p>
      <div className="space-y-2">
        {(finding.evidence ?? []).map((item, index) => (
          <EvidenceSnippet
            key={`${item.file}-${item.line_start}-${index}`}
            evidence={item}
          />
        ))}
      </div>
      {finding.id ? <TriageActions issueId={finding.id} /> : null}
    </article>
  );
}
