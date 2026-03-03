"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import { apiClient } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

type AgentRunRequest = {
  agent_name: string;
  scope: "chapter" | "project";
  scope_id?: number;
};

type AgentResultData = {
  name: string;
  summary: string;
  findings: unknown[];
  proposals: unknown[];
  confidence: number;
  needs_human_decision: boolean;
};

export function useAgentRun() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (body: AgentRunRequest) => {
      const response = await apiClient.runAgent(body);
      return unwrapEnvelope<AgentResultData>(
        response.data,
        "Could not run agent.",
      );
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.agents() });
      if (variables.scope === "chapter" && variables.scope_id != null) {
        queryClient.invalidateQueries({
          queryKey: queryKeys.chapterArtifact(variables.scope_id, "agent-results"),
        });
        queryClient.invalidateQueries({
          queryKey: queryKeys.chapterArtifact(variables.scope_id, "analysis"),
        });
      }
      queryClient.invalidateQueries({ queryKey: queryKeys.runs });
    },
  });
}
