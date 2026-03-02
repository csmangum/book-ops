"use client";

import { Button } from "@/components/ui/button";

export function ManuscriptDiffToggle({
  showDiff,
  onToggle,
}: {
  showDiff: boolean;
  onToggle: () => void;
}) {
  return (
    <Button variant="outline" size="sm" onClick={onToggle}>
      {showDiff ? "Show current manuscript" : "Show diff placeholder"}
    </Button>
  );
}
