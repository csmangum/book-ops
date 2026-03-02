import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { EmptyState } from "@/components/shared/EmptyState";
import { FindingCard } from "@/components/chapters/FindingCard";

type FindingsPanelProps = {
  continuityFindings: Array<Record<string, unknown>>;
  styleFindings: Array<Record<string, unknown>>;
  analysisFindings: Array<Record<string, unknown>>;
  loreProposals: Array<Record<string, unknown>>;
};

function FindingsList({ findings }: { findings: Array<Record<string, unknown>> }) {
  if (findings.length === 0) {
    return <EmptyState title="No findings" description="No findings were returned for this section." />;
  }

  return (
    <div className="space-y-3">
      {findings.map((item, index) => (
        <FindingCard key={`${item.rule_id}-${index}`} finding={item} />
      ))}
    </div>
  );
}

export function FindingsPanel({
  continuityFindings,
  styleFindings,
  analysisFindings,
  loreProposals,
}: FindingsPanelProps) {
  return (
    <Tabs defaultValue="continuity" className="w-full">
      <TabsList className="grid w-full grid-cols-4">
        <TabsTrigger value="continuity">Continuity</TabsTrigger>
        <TabsTrigger value="style">Style</TabsTrigger>
        <TabsTrigger value="analysis">All findings</TabsTrigger>
        <TabsTrigger value="lore">Lore impact</TabsTrigger>
      </TabsList>
      <TabsContent value="continuity" className="mt-3">
        <FindingsList findings={continuityFindings} />
      </TabsContent>
      <TabsContent value="style" className="mt-3">
        <FindingsList findings={styleFindings} />
      </TabsContent>
      <TabsContent value="analysis" className="mt-3">
        <FindingsList findings={analysisFindings} />
      </TabsContent>
      <TabsContent value="lore" className="mt-3">
        {loreProposals.length === 0 ? (
          <EmptyState title="No lore proposals" description="Generate lore delta to populate this section." />
        ) : (
          <ul className="space-y-2 text-sm">
            {loreProposals.map((proposal) => (
              <li key={String(proposal.id)} className="rounded-md border p-2">
                <p className="font-medium">{String(proposal.id)}</p>
                <p className="text-muted-foreground">{String(proposal.reason ?? "")}</p>
              </li>
            ))}
          </ul>
        )}
      </TabsContent>
    </Tabs>
  );
}
