import { EmptyState } from "@/components/shared/EmptyState";

type Entity = {
  id: string;
  name: string;
  type: string;
};

export function EntityInspector({ entity }: { entity?: Entity }) {
  if (!entity) {
    return (
      <EmptyState
        title="No entity selected"
        description="Select a graph node to inspect entity details."
      />
    );
  }

  return (
    <div className="space-y-2 rounded-md border p-3 text-sm">
      <p>
        <span className="font-medium">ID:</span> {entity.id}
      </p>
      <p>
        <span className="font-medium">Name:</span> {entity.name}
      </p>
      <p>
        <span className="font-medium">Type:</span> {entity.type}
      </p>
    </div>
  );
}
