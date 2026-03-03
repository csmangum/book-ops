"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ErrorBanner, LoadingState } from "@/components/shared";
import { useAgents, useAgentRun, useChapterCatalog } from "@/hooks";

export default function AgentsPage() {
  const agentsQuery = useAgents();
  const chaptersQuery = useChapterCatalog();
  const runAgent = useAgentRun();

  const [agentName, setAgentName] = useState<string>("");
  const [scope, setScope] = useState<"chapter" | "project">("chapter");
  const [chapterId, setChapterId] = useState<string>("");

  const agents = agentsQuery.data ?? {};
  const agentEntries = Object.entries(agents);
  const chapters = chaptersQuery.data ?? [];

  const handleRun = () => {
    if (!agentName) return;
    runAgent.mutate({
      agent_name: agentName,
      scope,
      scope_id: scope === "chapter" && chapterId ? Number(chapterId) : undefined,
    });
  };

  const canRun =
    agentName &&
    (scope === "project" || (scope === "chapter" && chapterId));

  return (
    <div className="space-y-4">
      <section>
        <h2 className="text-xl font-semibold">Agents</h2>
        <p className="text-sm text-muted-foreground">
          Run editorial agents on a chapter or project scope.
        </p>
      </section>

      {agentsQuery.isLoading && <LoadingState label="Loading agents…" />}
      {agentsQuery.error && (
        <ErrorBanner error={agentsQuery.error} title="Could not load agents" />
      )}

      <Card>
        <CardHeader>
          <CardTitle>Run agent</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="space-y-2">
              <label className="text-sm font-medium">Agent</label>
              <Select value={agentName} onValueChange={setAgentName}>
                <SelectTrigger>
                  <SelectValue placeholder="Select agent" />
                </SelectTrigger>
                <SelectContent>
                  {agentEntries.map(([name]) => (
                    <SelectItem key={name} value={name}>
                      {name.replace(/_/g, " ")}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Scope</label>
              <Select
                value={scope}
                onValueChange={(v) => setScope(v as "chapter" | "project")}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="chapter">Chapter</SelectItem>
                  <SelectItem value="project">Project</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {scope === "chapter" && (
              <div className="space-y-2">
                <label className="text-sm font-medium">Chapter</label>
                <Select value={chapterId} onValueChange={setChapterId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select chapter" />
                  </SelectTrigger>
                  <SelectContent>
                    {chapters.map((ch) => (
                      <SelectItem key={ch.chapterId} value={String(ch.chapterId)}>
                        {ch.chapterId}: {ch.title}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>
          <Button
            disabled={!canRun || runAgent.isPending}
            onClick={handleRun}
          >
            {runAgent.isPending ? "Running…" : "Run agent"}
          </Button>
          {runAgent.isError && (
            <ErrorBanner error={runAgent.error} title="Agent run failed" />
          )}
          {runAgent.isSuccess && runAgent.data && (
            <div className="rounded-md border p-3 space-y-2">
              <p className="text-sm font-medium">Result</p>
              <p className="text-sm text-muted-foreground">
                {runAgent.data.summary}
              </p>
              <p className="text-xs text-muted-foreground">
                Confidence: {(runAgent.data.confidence * 100).toFixed(0)}% ·
                Findings: {runAgent.data.findings?.length ?? 0} ·
                Proposals: {runAgent.data.proposals?.length ?? 0}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Available agents</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {agentEntries.map(([name, description]) => (
              <li key={name} className="flex flex-col gap-0.5">
                <span className="font-medium">{name.replace(/_/g, " ")}</span>
                <span className="text-sm text-muted-foreground">{description}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
