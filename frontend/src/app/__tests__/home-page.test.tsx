import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/components/home", () => ({
  GateStatusCards: () => <div>Gate cards</div>,
  TopBlockersList: () => <div>Top blockers</div>,
  RecentRunsList: () => <div>Recent runs</div>,
  ChangedSinceLastRun: () => <div>Changed list</div>,
  QuickActions: () => <div>Quick actions</div>,
}));

vi.mock("@/hooks", () => ({
  useChapterArtifact: () => ({ data: {}, isLoading: false, error: null }),
  useChapterCatalog: () => ({
    data: [{ chapterId: 1, title: "One", path: "chapters/1_One.md", modifiedAt: 0, size: 0, lineCount: 0 }],
    isLoading: false,
    error: null,
  }),
  useProjectArtifact: () => ({ data: { issues: [] }, isLoading: false, error: null }),
  useRunHistory: () => ({ data: [], isLoading: false, error: null }),
}));

import HomePage from "@/app/page";

describe("HomePage", () => {
  it("renders command center heading", () => {
    render(<HomePage />);
    expect(screen.getByText("Command Center")).toBeInTheDocument();
    expect(screen.getByText("Gate cards")).toBeInTheDocument();
  });
});
