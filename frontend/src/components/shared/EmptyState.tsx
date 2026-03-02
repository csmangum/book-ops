import { Inbox } from "lucide-react";

type EmptyStateProps = {
  title: string;
  description?: string;
};

export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-md border border-dashed p-8 text-center">
      <Inbox className="mb-2 size-8 text-muted-foreground" />
      <h3 className="text-sm font-semibold">{title}</h3>
      {description ? (
        <p className="mt-1 max-w-lg text-sm text-muted-foreground">{description}</p>
      ) : null}
    </div>
  );
}
