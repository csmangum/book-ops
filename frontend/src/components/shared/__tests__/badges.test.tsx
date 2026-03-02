import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { GateBadge } from "@/components/shared/GateBadge";
import { SeverityBadge } from "@/components/shared/SeverityBadge";
import { StatusBadge } from "@/components/shared/StatusBadge";

describe("shared badges", () => {
  it("renders severity badge with value", () => {
    render(<SeverityBadge severity="critical" />);
    expect(screen.getByText("critical")).toBeInTheDocument();
  });

  it("renders gate badge with value", () => {
    render(<GateBadge gate="pass_with_waivers" />);
    expect(screen.getByText("pass_with_waivers")).toBeInTheDocument();
  });

  it("renders status badge with value", () => {
    render(<StatusBadge status="resolved" />);
    expect(screen.getByText("resolved")).toBeInTheDocument();
  });
});
