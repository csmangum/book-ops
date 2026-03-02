"use client";

import { useMemo, useState } from "react";

import { ProposalQueue, ProposalStatusTabs } from "@/components/lore";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ErrorBanner, LoadingState } from "@/components/shared";
import { useLoreDelta } from "@/hooks";
import type { LoreProposal } from "@/lib/lore";

export default function LorePage() {
  const generateDelta = useLoreDelta();
  const [scope, setScope] = useState<"chapter" | "project">("chapter");
  const [chapterId, setChapterId] = useState("1");
  const [statusFilter, setStatusFilter] = useState("all");
  const [proposals, setProposals] = useState<LoreProposal[]>([]);

  const filtered = useMemo(() => {
    if (statusFilter === "all") {
      return proposals;
    }
    return proposals.filter((proposal) => proposal.status === statusFilter);
  }, [proposals, statusFilter]);

  return (
    <div className="space-y-4">
      <section>
        <h2 className="text-xl font-semibold">Lore Sync Studio</h2>
        <p className="text-sm text-muted-foreground">
          Generate, review, approve, and apply lore synchronization proposals.
        </p>
      </section>

      <div className="grid gap-3 rounded-md border p-3 md:grid-cols-4">
        <div className="space-y-2">
          <Label>Scope</Label>
          <Select value={scope} onValueChange={(value) => setScope(value as "chapter" | "project")}>
            <SelectTrigger>
              <SelectValue placeholder="Select scope" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="chapter">Chapter</SelectItem>
              <SelectItem value="project">Project</SelectItem>
            </SelectContent>
          </Select>
        </div>
        {scope === "chapter" ? (
          <div className="space-y-2">
            <Label>Chapter ID</Label>
            <Input
              value={chapterId}
              onChange={(event) => setChapterId(event.target.value)}
            />
          </div>
        ) : null}
        <div className="md:col-span-2 flex items-end">
          <Button
            onClick={async () => {
              const result = await generateDelta.mutateAsync({
                scope,
                id: scope === "chapter" ? Number(chapterId) : null,
              });

              const responseProposals = (result as { proposals?: LoreProposal[] }).proposals ?? [];
              setProposals(responseProposals);
            }}
          >
            Generate lore delta
          </Button>
        </div>
      </div>

      {generateDelta.isPending ? <LoadingState label="Generating lore proposals..." /> : null}
      {generateDelta.error ? <ErrorBanner error={generateDelta.error} /> : null}

      <ProposalStatusTabs value={statusFilter} onChange={setStatusFilter} />
      <ProposalQueue proposals={filtered} />
    </div>
  );
}
