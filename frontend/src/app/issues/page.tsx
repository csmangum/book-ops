"use client";

import { useMemo, useState } from "react";

import {
  BulkIssueActions,
  IssueDrawer,
  IssueFilters,
  type IssueFilterState,
  IssuesKanban,
  IssuesTable,
} from "@/components/issues";
import { EmptyState, ErrorBanner, LoadingState } from "@/components/shared";
import { useIssueList } from "@/hooks";
import { asArray, asRecord } from "@/lib/guards";

const defaultFilters: IssueFilterState = {
  scope: "all",
  severity: "all",
  status: "all",
  query: "",
};

type Issue = {
  id: string;
  rule_id: string;
  severity: string;
  status: string;
  scope: string;
  message: string;
  evidence?: Array<{
    file?: string;
    line_start?: number;
    line_end?: number;
    excerpt?: string;
  }>;
};

export default function IssuesPage() {
  const [filters, setFilters] = useState<IssueFilterState>(defaultFilters);
  const [selectedIssueIds, setSelectedIssueIds] = useState<string[]>([]);
  const [openedIssueId, setOpenedIssueId] = useState<string | null>(null);

  const listQuery = useIssueList({
    scope: filters.scope === "all" ? undefined : filters.scope,
    severity: filters.severity === "all" ? undefined : filters.severity,
    status: filters.status === "all" ? undefined : filters.status,
  });

  const issues = useMemo(() => {
    const rawIssues = asArray<Issue>(asRecord(listQuery.data)?.issues);
    const q = filters.query.trim().toLowerCase();
    if (!q) {
      return rawIssues;
    }

    return rawIssues.filter(
      (issue) =>
        issue.id.toLowerCase().includes(q) ||
        issue.rule_id.toLowerCase().includes(q) ||
        issue.message.toLowerCase().includes(q),
    );
  }, [listQuery.data, filters.query]);

  const openedIssue = issues.find((issue) => issue.id === openedIssueId);

  return (
    <div className="space-y-4">
      <section>
        <h2 className="text-xl font-semibold">Issues</h2>
        <p className="text-sm text-muted-foreground">
          Kanban and table triage over issue lifecycle status.
        </p>
      </section>

      <IssueFilters value={filters} onChange={setFilters} />

      {listQuery.isLoading ? <LoadingState label="Loading issues..." /> : null}
      {listQuery.error ? <ErrorBanner error={listQuery.error} /> : null}

      <BulkIssueActions
        selectedIssueIds={selectedIssueIds}
        onCleared={() => setSelectedIssueIds([])}
      />

      {issues.length === 0 ? (
        <EmptyState title="No matching issues" description="Adjust filters or run analysis first." />
      ) : (
        <>
          <IssuesKanban issues={issues} onOpenIssue={setOpenedIssueId} />
          <IssuesTable
            issues={issues}
            selectedIssueIds={selectedIssueIds}
            onSelectIssue={(issueId, checked) =>
              setSelectedIssueIds((current) =>
                checked
                  ? Array.from(new Set([...current, issueId]))
                  : current.filter((id) => id !== issueId),
              )
            }
            onOpenIssue={setOpenedIssueId}
          />
        </>
      )}

      <IssueDrawer
        issue={openedIssue}
        open={Boolean(openedIssueId)}
        onOpenChange={(open) => {
          if (!open) {
            setOpenedIssueId(null);
          }
        }}
      />
    </div>
  );
}
