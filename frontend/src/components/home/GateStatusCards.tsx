import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { GateBadge } from "@/components/shared/GateBadge";

type GatePayload = {
  status?: string;
  blocking_issue_ids?: string[];
  warning_issue_ids?: string[];
  message?: string;
};

export function GateStatusCards({
  projectGate,
  chapterGate,
}: {
  projectGate?: GatePayload;
  chapterGate?: GatePayload;
}) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Project Gate
            <GateBadge gate={projectGate?.status ?? "fail"} />
          </CardTitle>
          <CardDescription>{projectGate?.message ?? "No project gate artifact found yet."}</CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Blocking: {projectGate?.blocking_issue_ids?.length ?? 0} · Warnings:{" "}
          {projectGate?.warning_issue_ids?.length ?? 0}
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Chapter Gate Snapshot
            <GateBadge gate={chapterGate?.status ?? "pass_with_waivers"} />
          </CardTitle>
          <CardDescription>{chapterGate?.message ?? "Run a chapter pipeline to populate this card."}</CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Blocking: {chapterGate?.blocking_issue_ids?.length ?? 0} · Warnings:{" "}
          {chapterGate?.warning_issue_ids?.length ?? 0}
        </CardContent>
      </Card>
    </div>
  );
}
