"use client";

import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/hooks/queryKeys";
import { apiClient, type ApiIssueSeverity, type ApiIssueStatus } from "@/lib/api";
import { unwrapEnvelope } from "@/lib/api-envelope";

export type IssueListFilters = {
  status?: ApiIssueStatus;
  severity?: ApiIssueSeverity;
  scope?: string;
};

export function useIssueList(filters: IssueListFilters = {}) {
  return useQuery({
    queryKey: queryKeys.issues(filters),
    queryFn: async () => {
      const response = await apiClient.listIssues(filters);
      return unwrapEnvelope(response.data, "Could not load issues.");
    },
  });
}
