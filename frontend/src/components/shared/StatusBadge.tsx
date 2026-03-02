import { Badge } from "@/components/ui/badge";

const statusToVariantClass: Record<string, string> = {
  open: "bg-red-100 text-red-700 border-red-200",
  in_progress: "bg-blue-100 text-blue-700 border-blue-200",
  resolved: "bg-emerald-100 text-emerald-700 border-emerald-200",
  waived: "bg-amber-100 text-amber-700 border-amber-200",
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <Badge
      variant="outline"
      className={statusToVariantClass[status] ?? statusToVariantClass.open}
    >
      {status}
    </Badge>
  );
}
