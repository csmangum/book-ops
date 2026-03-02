"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import { apiClient, type ApiComponents } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

type IssueWaiveRequest = ApiComponents["schemas"]["IssueWaiveRequest"];

type MutationInput = {
  issueId: string;
  body: IssueWaiveRequest;
};

export function useIssueWaive() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ issueId, body }: MutationInput) => {
      const response = await apiClient.waiveIssue(issueId, body);
      return unwrapEnvelope(response.data, "Could not waive issue.");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.issues() });
    },
  });
}
