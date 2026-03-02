type Evidence = {
  file?: string;
  line_start?: number;
  line_end?: number;
  excerpt?: string;
};

export function EvidenceSnippet({ evidence }: { evidence: Evidence }) {
  return (
    <div className="rounded-md border bg-muted/20 p-2 text-xs">
      <p className="font-medium">
        {evidence.file}:{evidence.line_start}-{evidence.line_end}
      </p>
      <p className="mt-1 whitespace-pre-wrap text-muted-foreground">
        {evidence.excerpt}
      </p>
    </div>
  );
}
