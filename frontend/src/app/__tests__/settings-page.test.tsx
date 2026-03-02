import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/hooks", () => ({
  useSettings: () => ({
    data: {
      project: { chapters_dir: "chapters", lore_dir: "lore" },
      paths: { excluded_dirs: [] },
    },
    isLoading: false,
    error: null,
  }),
  usePatchSettings: () => ({
    mutate: vi.fn(),
    isPending: false,
    error: null,
  }),
}));

import SettingsPage from "@/app/settings/page";

describe("SettingsPage", () => {
  it("renders settings heading and project paths", () => {
    render(<SettingsPage />);
    expect(screen.getByText("Settings")).toBeInTheDocument();
    expect(screen.getByText("Project paths")).toBeInTheDocument();
  });
});
