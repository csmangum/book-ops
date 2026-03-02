import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const { getIndexStatusMock } = vi.hoisted(() => ({
  getIndexStatusMock: vi.fn(),
}));

vi.mock("@/lib/api", () => ({
  apiClient: {
    getIndexStatus: getIndexStatusMock,
  },
}));

import { useChapterCatalog } from "@/hooks/useChapterCatalog";

describe("useChapterCatalog", () => {
  it("fetches and maps symbolic entries to chapter records", async () => {
    getIndexStatusMock.mockResolvedValue({
      data: {
        ok: true,
        exit_code: 0,
        data: {
          symbolic_exists: true,
          semantic_exists: false,
          symbolic_path: "/tmp",
          semantic_path: "/tmp",
          symbolic: [
            {
              path: "chapters/1_Opening.md",
              sha256: "x",
              size: 100,
              line_count: 10,
              modified_at: 12345,
            },
          ],
        },
        stderr: "",
      },
    });

    const queryClient = new QueryClient();
    const { result } = renderHook(() => useChapterCatalog(), {
      wrapper: ({ children }) => (
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
      ),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toHaveLength(1);
    expect(result.current.data![0].chapterId).toBe(1);
    expect(result.current.data![0].title).toBe("Opening");
  });
});
