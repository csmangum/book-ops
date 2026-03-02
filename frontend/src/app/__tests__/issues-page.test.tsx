import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/components/issues", () => ({
  IssueFilters: () => <div>Issue filters</div>,
  BulkIssueActions: () => <div>Bulk issue actions</div>,
  IssuesKanban: ({ issues }: { issues: Array<{ id: string }> }) => (
    <div>Kanban issues: {issues.length}</div>
  ),
  IssuesTable: ({ issues }: { issues: Array<{ id: string }> }) => (
    <div>Table issues: {issues.length}</div>
  ),
  IssueDrawer: () => <div>Issue drawer</div>,
}));

vi.mock("@/hooks", () => ({
  useIssueList: () => ({
    data: {
      issues: [
        {
          id: "ISSUE-123",
          rule_id: "HARD.TEST",
          severity: "high",
          status: "open",
          scope: "chapter:1",
          message: "example issue",
        },
      ],
    },
    isLoading: false,
    error: null,
  }),
}));

import IssuesPage from "@/app/issues/page";

describe("IssuesPage", () => {
  it("renders issue route and mocked data containers", () => {
    render(<IssuesPage />);
    expect(screen.getByText("Issues")).toBeInTheDocument();
    expect(screen.getByText("Issue filters")).toBeInTheDocument();
    expect(screen.getByText("Kanban issues: 1")).toBeInTheDocument();
    expect(screen.getByText("Table issues: 1")).toBeInTheDocument();
  });
});
