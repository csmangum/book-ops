"use client";

import { useMemo, useState } from "react";

import {
  RuleDetailDrawer,
  RuleList,
  RuleSandboxRunner,
  RulesVersionDiff,
  ThresholdEditor,
} from "@/components/rules";
import { ErrorBanner, LoadingState } from "@/components/shared";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useRules } from "@/hooks";
import { asArray, asRecord } from "@/lib/guards";

type RuleItem = {
  id: string;
  kind: "hard" | "soft";
  severity: string;
  message: string;
};

export default function RulesPage() {
  const rulesQuery = useRules();
  const rules = useMemo<RuleItem[]>(
    () =>
      asArray<Record<string, unknown>>(asRecord(rulesQuery.data)?.rules).map(
        (rule) => ({
          id: String(rule.id ?? "UNKNOWN.RULE"),
          kind: String(rule.kind ?? "soft") === "hard" ? "hard" : "soft",
          severity: String(rule.severity ?? "info"),
          message: String(rule.message ?? "No description."),
        }),
      ),
    [rulesQuery.data],
  );
  const [selectedRuleId, setSelectedRuleId] = useState<string | null>(null);
  const selectedRule = useMemo(
    () => rules.find((rule) => rule.id === selectedRuleId),
    [rules, selectedRuleId],
  );

  return (
    <div className="space-y-4">
      <section>
        <h2 className="text-xl font-semibold">Rules</h2>
        <p className="text-sm text-muted-foreground">
          Rule definitions loaded from backend rule payload.
        </p>
      </section>

      {rulesQuery.isLoading ? <LoadingState label="Loading rules..." /> : null}
      {rulesQuery.error ? <ErrorBanner error={rulesQuery.error} /> : null}

      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        <Card>
          <CardHeader>
            <CardTitle>Rule list</CardTitle>
          </CardHeader>
          <CardContent>
            <RuleList rules={rules} onSelect={(rule) => setSelectedRuleId(rule.id)} />
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
