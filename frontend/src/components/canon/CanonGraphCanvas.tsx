"use client";

import { useEffect, useRef } from "react";
import cytoscape from "cytoscape";

export function CanonGraphCanvas({
  hasGraphData,
  nodes = [],
  edges = [],
}: {
  hasGraphData: boolean;
  nodes?: Array<{ id: string; label: string }>;
  edges?: Array<{ id?: string; source: string; target: string }>;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current || !hasGraphData) {
      return;
    }

    const graph = cytoscape({
      container: containerRef.current,
      elements: [
        ...nodes.map((node) => ({
          data: { id: node.id, label: node.label },
        })),
        ...edges.map((edge, index) => ({
          data: {
            id: edge.id ?? `edge-${index}`,
            source: edge.source,
            target: edge.target,
          },
        })),
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
      layout: { name: "cose" },
    });

    return () => {
      graph.destroy();
    };
  }, [edges, hasGraphData, nodes]);

  return (
    <div
      ref={containerRef}
      className="h-[420px] w-full rounded-md border bg-muted/10"
    />
  );
}
