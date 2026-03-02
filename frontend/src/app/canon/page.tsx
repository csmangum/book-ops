"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";

import {
  CanonGraphCanvas,
  CanonGraphFilters,
  EntityInspector,
  ProvenanceList,
} from "@/components/canon";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { EmptyState, ErrorBanner, JsonViewer, LoadingState } from "@/components/shared";
import { useCanonGraph } from "@/hooks";
import { apiClient } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";
import { asArray } from "@/lib/guards";

export default function CanonPage() {
  const [selectedTypes, setSelectedTypes] = useState<string[]>([
    "character",
    "object",
    "event",
    "faction",
    "location",
  ]);
  const [fromSnapshot, setFromSnapshot] = useState("");
  const [toSnapshot, setToSnapshot] = useState("");
  const canonGraph = useCanonGraph();

  const buildCanon = useMutation({
    mutationFn: async () => unwrapEnvelope((await apiClient.buildCanon()).data),
  });
  const validateCanon = useMutation({
    mutationFn: async () => unwrapEnvelope((await apiClient.validateCanon()).data),
  });
  const diffCanon = useMutation({
    mutationFn: async () =>
      unwrapEnvelope(
        (
          await apiClient.diffCanon({
            from_snapshot: fromSnapshot,
            to_snapshot: toSnapshot,
          })
        ).data,
      ),
  });

  return (
    <div className="space-y-4">
      <section>
        <h2 className="text-xl font-semibold">Canon Graph</h2>
        <p className="text-sm text-muted-foreground">
          Interactive graph is scaffolded. Backend graph-read endpoint is still required.
        </p>
      </section>

      <div className="flex flex-wrap gap-2">
        <Button onClick={() => buildCanon.mutate()}>Build canon snapshot</Button>
        <Button variant="outline" onClick={() => validateCanon.mutate()}>
          Validate canon
        </Button>
      </div>

      <div className="grid gap-3 rounded-md border p-3 md:grid-cols-2">
        <div className="space-y-2">
          <Label>From snapshot</Label>
          <Input value={fromSnapshot} onChange={(event) => setFromSnapshot(event.target.value)} />
        </div>
        <div className="space-y-2">
          <Label>To snapshot</Label>
          <Input value={toSnapshot} onChange={(event) => setToSnapshot(event.target.value)} />
        </div>
        <div className="md:col-span-2">
          <Button
            variant="outline"
            disabled={!fromSnapshot || !toSnapshot}
            onClick={() => diffCanon.mutate()}
          >
            Diff canon snapshots
          </Button>
        </div>
      </div>

      <CanonGraphFilters
        selectedTypes={selectedTypes}
        onToggle={(type, checked) =>
          setSelectedTypes((current) =>
            checked
              ? Array.from(new Set([...current, type]))
              : current.filter((item) => item !== type),
          )
        }
      />

      {canonGraph.isLoading ? <LoadingState label="Loading canon graph..." /> : null}
      {canonGraph.error ? (
        <ErrorBanner error={canonGraph.error} title="Canon graph unavailable" />
      ) : null}
      <CanonGraphCanvas
        hasGraphData={(canonGraph.data?.node_count ?? 0) > 0}
        nodes={asArray<{ id: string; label: string }>(canonGraph.data?.nodes)}
        edges={asArray<{ id?: string; source: string; target: string }>(
          canonGraph.data?.edges,
        )}
      />
      {(canonGraph.data?.node_count ?? 0) === 0 ? (
        <EmptyState
          title="Graph data unavailable"
          description="No canon graph nodes found yet. Build canon snapshot first."
        />
      ) : null}

      <div className="grid gap-4 md:grid-cols-2">
        <EntityInspector />
        <ProvenanceList provenance={[]} />
      </div>

      {buildCanon.data ? <JsonViewer label="Build canon result" data={buildCanon.data} /> : null}
      {validateCanon.data ? <JsonViewer label="Validate canon result" data={validateCanon.data} /> : null}
      {diffCanon.data ? <JsonViewer label="Canon diff result" data={diffCanon.data} /> : null}
    </div>
  );
}
