"use client";

import { useMemo, useState } from "react";

import {
  RuleDetailDrawer,
  RuleList,
  RuleSandboxRunner,
  RulesVersionDiff,
  ThresholdEditor,
} from "@/components/rules";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const staticRules = [
  {
    id: "HARD.TIMELINE.DAY_SEQUENCE",
    kind: "hard" as const,
    severity: "high",
    message: "Chapter day sequence is incoherent.",
  },
  {
    id: "HARD.CHARACTER.INVARIANTS",
    kind: "hard" as const,
    severity: "critical",
    message: "Character invariant violation.",
  },
  {
    id: "SOFT.REPETITION.PHRASE_FAMILY",
    kind: "soft" as const,
    severity: "medium",
    message: "Phrase-family repetition exceeds target.",
  },
];

export default function RulesPage() {
  const [selectedRuleId, setSelectedRuleId] = useState<string | null>(null);
  const selectedRule = useMemo(
    () => staticRules.find((rule) => rule.id === selectedRuleId),
    [selectedRuleId],
  );

  return (
    <div className="space-y-4">
      <section>
        <h2 className="text-xl font-semibold">Rules</h2>
        <p className="text-sm text-muted-foreground">
          Rules API endpoints are not yet available. This page provides a scaffolded console.
        </p>
      </section>

      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        <Card>
          <CardHeader>
            <CardTitle>Rule list</CardTitle>
          </CardHeader>
          <CardContent>
            <RuleList rules={staticRules} onSelect={(rule) => setSelectedRuleId(rule.id)} />
          </CardContent>
        </Card>
        <div className="space-y-4">
          <ThresholdEditor />
          <RuleSandboxRunner />
        </div>
      </div>

      <RulesVersionDiff />

      <RuleDetailDrawer
        rule={selectedRule}
        open={Boolean(selectedRuleId)}
        onOpenChange={(open) => {
          if (!open) {
            setSelectedRuleId(null);
          }
        }}
      />
    </div>
  );
}
