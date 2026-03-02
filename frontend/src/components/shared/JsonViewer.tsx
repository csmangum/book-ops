type JsonViewerProps = {
  label?: string;
  data: unknown;
  defaultOpen?: boolean;
};

export function JsonViewer({
  label = "JSON",
  data,
  defaultOpen = false,
}: JsonViewerProps) {
  return (
    <details
      className="w-full rounded-md border bg-muted/20 p-3 text-sm"
      open={defaultOpen}
    >
      <summary className="cursor-pointer font-medium">{label}</summary>
      <pre className="mt-2 max-h-80 overflow-auto rounded bg-black/90 p-3 text-xs text-zinc-50">
        {JSON.stringify(data, null, 2)}
      </pre>
    </details>
  );
}
