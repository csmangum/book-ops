"use client";

import { useEffect, useRef } from "react";
import cytoscape from "cytoscape";

export function CanonGraphCanvas({
  hasGraphData,
}: {
  hasGraphData: boolean;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current || !hasGraphData) {
      return;
    }

    const graph = cytoscape({
      container: containerRef.current,
      elements: [
        { data: { id: "a", label: "Entity A" } },
        { data: { id: "b", label: "Entity B" } },
        { data: { id: "ab", source: "a", target: "b" } },
      ],
      style: [
        {
          selector: "node",
          style: {
            label: "data(label)",
            "background-color": "#2563eb",
            color: "#111827",
          },
        },
        {
          selector: "edge",
          style: {
            width: 2,
            "line-color": "#9ca3af",
          },
        },
      ],
      layout: { name: "grid" },
    });

    return () => {
      graph.destroy();
    };
  }, [hasGraphData]);

  return (
    <div
      ref={containerRef}
      className="h-[420px] w-full rounded-md border bg-muted/10"
    />
  );
}
