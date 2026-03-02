import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GateStatusCards } from "../GateStatusCards";

describe("GateStatusCards", () => {
  it("renders project and chapter gate sections", () => {
    render(
      <GateStatusCards projectGate={{ status: "pass" }} chapterGate={null} />,
    );
    expect(screen.getByText("Project Gate")).toBeInTheDocument();
    expect(screen.getByText("Chapter Gate Snapshot")).toBeInTheDocument();
  });

  it("shows pass status when provided", () => {
    render(
      <GateStatusCards
        projectGate={{ status: "pass" }}
        chapterGate={{ status: "pass" }}
      />,
    );
    expect(screen.getAllByText(/pass/i).length).toBeGreaterThan(0);
  });
});
