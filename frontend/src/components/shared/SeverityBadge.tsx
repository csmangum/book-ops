import { Badge } from "@/components/ui/badge";

const severityToVariantClass: Record<string, string> = {
  critical: "bg-red-600 text-white hover:bg-red-600/90",
  high: "bg-orange-500 text-white hover:bg-orange-500/90",
  medium: "bg-amber-500 text-black hover:bg-amber-500/90",
  low: "bg-blue-500 text-white hover:bg-blue-500/90",
  info: "bg-zinc-500 text-white hover:bg-zinc-500/90",
};

export function SeverityBadge({ severity }: { severity: string }) {
  return (
    <Badge className={severityToVariantClass[severity] ?? severityToVariantClass.info}>
      {severity}
    </Badge>
  );
}
