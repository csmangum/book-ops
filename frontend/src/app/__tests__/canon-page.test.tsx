import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/components/canon", () => ({
  CanonGraphCanvas: () => <div>Canon graph canvas</div>,
  CanonGraphFilters: () => <div>Canon graph filters</div>,
  EntityInspector: () => <div>Entity inspector</div>,
  ProvenanceList: () => <div>Provenance list</div>,
}));

vi.mock("@/hooks", () => ({
  useCanonGraph: () => ({
    data: { node_count: 0, nodes: [], edges: [] },
    isLoading: false,
    error: null,
  }),
}));

import CanonPage from "@/app/canon/page";

function wrapper({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient();
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

describe("CanonPage", () => {
  it("renders canon graph heading and canvas", () => {
    render(<CanonPage />, { wrapper });
    expect(screen.getByText("Canon Graph")).toBeInTheDocument();
    expect(screen.getByText("Canon graph canvas")).toBeInTheDocument();
  });
});
