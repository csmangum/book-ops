type RuleItem = {
  id: string;
  kind: "hard" | "soft";
  severity: string;
  message: string;
};

export function RuleList({
  rules,
  onSelect,
}: {
  rules: RuleItem[];
  onSelect: (rule: RuleItem) => void;
}) {
  return (
    <ul className="space-y-2">
      {rules.map((rule) => (
        <li key={rule.id}>
          <button
            type="button"
            className="w-full rounded-md border p-3 text-left"
            onClick={() => onSelect(rule)}
          >
            <p className="text-sm font-semibold">{rule.id}</p>
            <p className="text-xs text-muted-foreground">
              {rule.kind.toUpperCase()} · {rule.severity}
            </p>
            <p className="mt-1 text-sm text-muted-foreground">{rule.message}</p>
          </button>
        </li>
      ))}
    </ul>
  );
}
