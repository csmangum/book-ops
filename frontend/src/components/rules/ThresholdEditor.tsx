"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function ThresholdEditor() {
  return (
    <div className="space-y-3 rounded-md border p-3">
      <p className="text-sm font-semibold">Threshold Editor</p>
      <p className="text-xs text-muted-foreground">
        Threshold persistence requires backend support (`PATCH /rules`).
      </p>
      <div className="space-y-2">
        <Label htmlFor="rule-threshold">Threshold</Label>
        <Input id="rule-threshold" placeholder="e.g. 8" />
      </div>
      <Button variant="outline" disabled>
        Save threshold (backend required)
      </Button>
    </div>
  );
}
