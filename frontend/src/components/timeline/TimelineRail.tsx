import { scaleLinear } from "@visx/scale";

type Marker = {
  chapter: number;
  day_markers?: string[];
  date_markers?: string[];
};

export function TimelineRail({
  markers,
  onSelectMarker,
}: {
  markers: Marker[];
  onSelectMarker: (marker: Marker) => void;
}) {
  const width = 900;
  const height = 160;
  const margin = { left: 40, right: 20, top: 30, bottom: 30 };

  const chapters = markers.map((marker) => marker.chapter);
  const minChapter = Math.min(...chapters, 1);
  const maxChapter = Math.max(...chapters, 1);
  const xScale = scaleLinear<number>({
    domain: [minChapter, maxChapter],
    range: [margin.left, width - margin.right],
  });

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className="h-44 w-full rounded-md border bg-muted/10"
      role="img"
      aria-label="Timeline rail"
    >
      <line
        x1={margin.left}
        x2={width - margin.right}
        y1={height / 2}
        y2={height / 2}
        stroke="currentColor"
        opacity={0.4}
      />
      {markers.map((marker) => {
        const x = xScale(marker.chapter);
        return (
          <g key={`${marker.chapter}-${marker.day_markers?.[0] ?? "none"}`}>
            <circle
              cx={x}
              cy={height / 2}
              r={7}
              className="cursor-pointer fill-blue-500"
              onClick={() => onSelectMarker(marker)}
            />
            <text x={x} y={height / 2 + 26} textAnchor="middle" className="fill-foreground text-[11px]">
              Ch {marker.chapter}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
