"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAnalyzeChapter } from "@/hooks";

export function RuleSandboxRunner() {
  const [chapterId, setChapterId] = useState("1");
  const analyzeChapter = useAnalyzeChapter();

  return (
    <div className="space-y-3 rounded-md border p-3">
      <p className="text-sm font-semibold">Rule sandbox</p>
      <p className="text-xs text-muted-foreground">
        Runs chapter analysis to emulate rule checks against selected chapter.
      </p>
      <div className="space-y-2">
        <Label htmlFor="sandbox-chapter">Chapter ID</Label>
        <Input
          id="sandbox-chapter"
          value={chapterId}
          onChange={(event) => setChapterId(event.target.value)}
        />
      </div>
      <Button
        onClick={() =>
          analyzeChapter.mutate({
            chapter_id: Number(chapterId),
            checks: ["tense", "invariants", "repetition", "motifs", "voice"],
          })
        }
      >
        Run sandbox analysis
      </Button>
    </div>
  );
}
