"use client";

import { useMemo, useState } from "react";

import {
  MarkerDetailsDrawer,
  TimelineConflictList,
  TimelineFilters,
  type TimelineFilterState,
  TimelineRail,
} from "@/components/timeline";
import { EmptyState, ErrorBanner, LoadingState } from "@/components/shared";
import { useProjectArtifact } from "@/hooks";
import { asArray, asRecord } from "@/lib/guards";

type Marker = {
  chapter: number;
  day_markers?: string[];
  date_markers?: string[];
};

const defaultFilters: TimelineFilterState = {
  chapterMarkers: true,
  entityEvents: true,
  contradictions: true,
};

export default function TimelinePage() {
  const [filters, setFilters] = useState(defaultFilters);
  const [selectedMarker, setSelectedMarker] = useState<Marker | undefined>();
  const timelineArtifact = useProjectArtifact("timeline");

  const markers = useMemo(
    () => asArray<Marker>(asRecord(timelineArtifact.data)?.timeline_markers),
    [timelineArtifact.data],
  );

  return (
    <div className="space-y-4">
      <section>
        <h2 className="text-xl font-semibold">Timeline</h2>
        <p className="text-sm text-muted-foreground">
          Chapter/day rail with marker conflict overlays.
        </p>
      </section>

      <TimelineFilters value={filters} onChange={setFilters} />

      {timelineArtifact.isLoading ? <LoadingState label="Loading timeline artifact..." /> : null}
      {timelineArtifact.error ? <ErrorBanner error={timelineArtifact.error} /> : null}

      {markers.length === 0 ? (
        <EmptyState
          title="No timeline markers available"
          description="Generate project reports to populate timeline-status artifact."
        />
      ) : (
        <>
          <TimelineRail markers={markers} onSelectMarker={setSelectedMarker} />
          <TimelineConflictList markers={markers} />
        </>
      )}

      <MarkerDetailsDrawer
        marker={selectedMarker}
        open={Boolean(selectedMarker)}
        onOpenChange={(open) => {
          if (!open) {
            setSelectedMarker(undefined);
          }
        }}
      />
    </div>
  );
}
