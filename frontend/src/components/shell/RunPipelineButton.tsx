"use client";

import { useState } from "react";
import { Play } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { usePipelineRun } from "@/hooks/usePipelineRun";

export function RunPipelineButton() {
  const [scope, setScope] = useState<"project" | "chapter">("project");
  const [chapterId, setChapterId] = useState<string>("");
  const mutation = usePipelineRun();

  const isDisabled = mutation.isPending || (scope === "chapter" && !chapterId);

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button size="sm" className="gap-2">
          <Play className="size-4" />
          Run Pipeline
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Run pipeline</DialogTitle>
          <DialogDescription>
            Trigger a chapter or full project pipeline run.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-3">
          <div className="space-y-2">
            <Label htmlFor="pipeline-scope">Scope</Label>
            <Select
              value={scope}
              onValueChange={(value) => setScope(value as "project" | "chapter")}
            >
              <SelectTrigger id="pipeline-scope">
                <SelectValue placeholder="Select scope" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="project">Project</SelectItem>
                <SelectItem value="chapter">Chapter</SelectItem>
              </SelectContent>
            </Select>
          </div>
          {scope === "chapter" ? (
            <div className="space-y-2">
              <Label htmlFor="pipeline-chapter-id">Chapter ID</Label>
              <Input
                id="pipeline-chapter-id"
                inputMode="numeric"
                value={chapterId}
                onChange={(event) => setChapterId(event.target.value)}
                placeholder="e.g. 14"
              />
            </div>
          ) : null}
        </div>
        <DialogFooter>
          <Button
            disabled={isDisabled}
            onClick={() => {
              if (scope === "chapter") {
                mutation.mutate({
                  scope: "chapter",
                  body: {
                    chapter_id: Number(chapterId),
                    strict: false,
                  },
                });
                return;
              }

              mutation.mutate({
                scope: "project",
                body: { strict: false },
              });
            }}
          >
            {mutation.isPending ? "Running..." : "Run"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
