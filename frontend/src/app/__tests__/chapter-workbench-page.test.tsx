import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useParams: () => ({ chapterId: "3" }),
}));

vi.mock("@/components/chapters", () => ({
  ChapterNavigator: () => <div>Chapter navigator</div>,
  FindingsPanel: () => <div>Findings panel</div>,
  ManuscriptDiffToggle: () => <button type="button">Diff toggle</button>,
  ManuscriptEditor: ({ value }: { value: string }) => <pre>{value}</pre>,
}));

vi.mock("@/hooks", () => ({
  useChapterCatalog: () => ({
    data: [{ chapterId: 3, title: "Three", path: "chapters/3_Three.md", modifiedAt: 0, size: 0, lineCount: 0 }],
    isLoading: false,
    error: null,
  }),
  useChapterArtifact: () => ({
    data: { generated_findings: [], findings: [], proposals: [] },
    isLoading: false,
    error: null,
  }),
  useChapterContent: () => ({
    data: null,
    isLoading: false,
    error: null,
  }),
}));

import ChapterWorkbenchPage from "@/app/chapters/[chapterId]/page";

describe("ChapterWorkbenchPage", () => {
  it("renders chapter workbench and manuscript placeholder", () => {
    render(<ChapterWorkbenchPage />);
    expect(screen.getByText("Chapter Workbench")).toBeInTheDocument();
    expect(
      screen.getByText(/Chapter 3 manuscript placeholder/),
    ).toBeInTheDocument();
    expect(screen.getByText("Findings panel")).toBeInTheDocument();
  });
});
