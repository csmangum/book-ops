"use client";

import { Drawer, DrawerContent, DrawerDescription, DrawerHeader, DrawerTitle } from "@/components/ui/drawer";
import { StatusBadge, SeverityBadge } from "@/components/shared";
import { EvidenceSnippet } from "@/components/chapters/EvidenceSnippet";
import { TriageActions } from "@/components/chapters/TriageActions";

type Issue = {
  id: string;
  rule_id: string;
  severity: string;
  status: string;
  scope: string;
  message: string;
  evidence?: Array<{
    file?: string;
    line_start?: number;
    line_end?: number;
    excerpt?: string;
  }>;
};

export function IssueDrawer({
  issue,
  open,
  onOpenChange,
}: {
  issue?: Issue;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent>
        <div className="mx-auto w-full max-w-3xl p-4">
          {issue ? (
            <>
              <DrawerHeader className="px-0">
                <DrawerTitle className="flex items-center gap-2">
                  {issue.id}
                  <SeverityBadge severity={issue.severity} />
                  <StatusBadge status={issue.status} />
                </DrawerTitle>
                <DrawerDescription>
                  {issue.rule_id} · {issue.scope}
                </DrawerDescription>
              </DrawerHeader>
              <p className="mb-3 text-sm text-muted-foreground">{issue.message}</p>
              <div className="space-y-2">
                {(issue.evidence ?? []).map((evidence, index) => (
                  <EvidenceSnippet
                    key={`${evidence.file}-${evidence.line_start}-${index}`}
                    evidence={evidence}
                  />
                ))}
              </div>
              <div className="mt-4">
                <TriageActions issueId={issue.id} />
              </div>
            </>
          ) : null}
        </div>
      </DrawerContent>
    </Drawer>
  );
}
