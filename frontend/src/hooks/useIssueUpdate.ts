"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import { apiClient, type ApiComponents } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

type IssueUpdateRequest = ApiComponents["schemas"]["IssueUpdateRequest"];

type MutationInput = {
  issueId: string;
  body: IssueUpdateRequest;
};

export function useIssueUpdate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ issueId, body }: MutationInput) => {
      const response = await apiClient.updateIssue(issueId, body);
      return unwrapEnvelope(response.data, "Could not update issue.");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.issues() });
    },
  });
}
