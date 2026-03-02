import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const { listIssuesMock } = vi.hoisted(() => ({
  listIssuesMock: vi.fn(),
}));

vi.mock("@/lib/api", () => ({
  apiClient: {
    listIssues: listIssuesMock,
  },
}));

import { useIssueList } from "@/hooks/useIssueList";

describe("useIssueList", () => {
  it("fetches and unwraps issue list payload", async () => {
    listIssuesMock.mockResolvedValue({
      data: {
        ok: true,
        exit_code: 0,
        data: {
          count: 1,
          issues: [
            {
              id: "ISSUE-1",
              rule_id: "HARD.TEST",
              severity: "high",
              status: "open",
              scope: "chapter:1",
              message: "Test",
            },
          ],
        },
        stderr: "",
      },
    });

    const queryClient = new QueryClient();
    const { result } = renderHook(() => useIssueList({ status: "open" }), {
      wrapper: ({ children }) => (
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
      ),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect((result.current.data as { count: number } | undefined)?.count).toBe(1);
    expect(listIssuesMock).toHaveBeenCalledWith({ status: "open" });
  });
});
