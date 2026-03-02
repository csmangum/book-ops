import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/components/runs", () => ({
  RunsTable: () => <div>Runs table</div>,
}));

vi.mock("@/hooks", () => ({
  useRunsList: () => ({
    data: { runs: [], count: 0 },
    isSuccess: true,
    isLoading: false,
    error: null,
  }),
  useRunHistory: () => ({ data: [], isLoading: false, error: null }),
}));

import RunsPage from "@/app/runs/page";

describe("RunsPage", () => {
  it("renders runs heading", () => {
    render(<RunsPage />);
    expect(screen.getByText("Runs")).toBeInTheDocument();
  });
});
