import type { LoreProposal } from "@/lib/lore";

export function LoreDiffViewer({ proposal }: { proposal: LoreProposal }) {
  return (
    <div className="grid gap-3 md:grid-cols-2">
      <section className="rounded-md border p-3">
        <h3 className="text-sm font-semibold">Current lore</h3>
        <pre className="mt-2 whitespace-pre-wrap text-xs text-muted-foreground">
{`# ${proposal.target_lore_file ?? "lore/unknown.md"}

<current lore snapshot unavailable>
`}
        </pre>
      </section>
      <section className="rounded-md border p-3">
        <h3 className="text-sm font-semibold">Proposed change</h3>
        <pre className="mt-2 whitespace-pre-wrap text-xs text-muted-foreground">
{`# Proposed update

Reason: ${proposal.reason ?? "No reason provided."}

<!-- diff-first placeholder until run-scoped diff artifact is available -->`}
        </pre>
      </section>
    </div>
  );
}
