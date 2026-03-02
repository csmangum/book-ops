import { Badge } from "@/components/ui/badge";

const gateToVariantClass: Record<string, string> = {
  pass: "bg-emerald-600 text-white hover:bg-emerald-600/90",
  fail: "bg-red-600 text-white hover:bg-red-600/90",
  pass_with_waivers: "bg-amber-500 text-black hover:bg-amber-500/90",
};

export function GateBadge({ gate }: { gate: string }) {
  return (
    <Badge className={gateToVariantClass[gate] ?? gateToVariantClass.fail}>
      {gate}
    </Badge>
  );
}
