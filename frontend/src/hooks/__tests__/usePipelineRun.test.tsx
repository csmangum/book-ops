import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const { runChapterPipelineMock, runProjectPipelineMock, addRunHistoryEntryMock } =
  vi.hoisted(() => ({
    runChapterPipelineMock: vi.fn(),
    runProjectPipelineMock: vi.fn(),
    addRunHistoryEntryMock: vi.fn(),
  }));

vi.mock("@/lib/api", () => ({
  apiClient: {
    runChapterPipeline: runChapterPipelineMock,
    runProjectPipeline: runProjectPipelineMock,
  },
}));

vi.mock("@/lib/run-history", () => ({
  addRunHistoryEntry: addRunHistoryEntryMock,
}));

import { usePipelineRun } from "@/hooks/usePipelineRun";

describe("usePipelineRun", () => {
  it("runs chapter pipeline and stores local run history", async () => {
    runChapterPipelineMock.mockResolvedValue({
      data: {
        ok: true,
        exit_code: 0,
        data: { gate: "pass", scope: "chapter:9" },
        stderr: "",
      },
    });

    const queryClient = new QueryClient();
    const { result } = renderHook(() => usePipelineRun(), {
      wrapper: ({ children }) => (
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
      ),
    });

    await result.current.mutateAsync({
      scope: "chapter",
      body: { chapter_id: 9, strict: false },
    });

    expect(runChapterPipelineMock).toHaveBeenCalledWith({
      chapter_id: 9,
      strict: false,
    });
    expect(addRunHistoryEntryMock).toHaveBeenCalled();
  });

  it("runs project pipeline and stores local run history", async () => {
    runProjectPipelineMock.mockResolvedValue({
      data: {
        ok: true,
        exit_code: 0,
        data: { gate: "pass_with_waivers", scope: "project" },
        stderr: "",
      },
    });

    const queryClient = new QueryClient();
    const { result } = renderHook(() => usePipelineRun(), {
      wrapper: ({ children }) => (
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
      ),
    });

    await result.current.mutateAsync({
      scope: "project",
      body: { strict: false },
    });

    expect(runProjectPipelineMock).toHaveBeenCalledWith({ strict: false });
    expect(addRunHistoryEntryMock).toHaveBeenCalled();
  });
});
