"use client";

import { RoadmapSummary } from "@/lib/types";
import { useEffect, useState } from "react";
import { listRoadmaps } from "@/lib/api";
import Link from "next/link";

export function RoadmapList({ profileId }: { profileId: number }) {
  const [roadmaps, setRoadmaps] = useState<RoadmapSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listRoadmaps(profileId)
      .then(setRoadmaps)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [profileId]);

  if (loading) {
    return (
      <div className="card p-5">
        <p className="text-slate-500">Loading roadmaps...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card p-5">
        <p className="text-red-600">Failed to load roadmaps: {error}</p>
      </div>
    );
  }

  if (roadmaps.length === 0) {
    return (
      <div className="card p-5">
        <p className="text-slate-500">No roadmaps generated yet. Start one from the search page!</p>
      </div>
    );
  }

  return (
    <div className="card p-5">
      <h2 className="font-semibold mb-4">🗺️ Your Roadmaps ({roadmaps.length})</h2>
      
      <div className="space-y-3">
        {roadmaps.map((roadmap, idx) => {
          const completionPct = roadmap.total_steps > 0
            ? Math.round((roadmap.completed_steps / roadmap.total_steps) * 100)
            : 0;

          return (
            <Link
              key={roadmap.id}
              href={`/roadmaps/${roadmap.id}`}
              className="block p-4 border border-slate-200 rounded-lg hover:border-indigo-400 hover:shadow-sm transition"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-medium text-slate-900">{roadmap.target_job_title}</h3>
                  <p className="text-sm text-slate-600 mt-1">{roadmap.target_job_company}</p>
                  
                  <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                    <span className="font-medium text-indigo-600">v{roadmaps.length - idx}</span>
                    <span>•</span>
                    <span>{new Date(roadmap.created_at).toLocaleDateString()}</span>
                    <span>•</span>
                    <span>{roadmap.total_steps} steps</span>
                    {roadmap.ai_quality_indicator && (
                      <>
                        <span>•</span>
                        <span className={
                          roadmap.ai_quality_indicator === "high" ? "text-green-600" :
                          roadmap.ai_quality_indicator === "medium" ? "text-amber-600" :
                          "text-slate-500"
                        }>
                          {roadmap.ai_quality_indicator === "fallback" ? "Basic" : 
                           roadmap.ai_quality_indicator.charAt(0).toUpperCase() + roadmap.ai_quality_indicator.slice(1)} quality
                        </span>
                      </>
                    )}
                  </div>
                </div>

                <div className="ml-4 text-right">
                  <div className="text-2xl font-bold text-indigo-600">{completionPct}%</div>
                  <div className="text-xs text-slate-500">
                    {roadmap.completed_steps}/{roadmap.total_steps} done
                  </div>
                </div>
              </div>

              {roadmap.total_steps > 0 && (
                <div className="mt-3 bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className="h-full bg-indigo-500 transition-all"
                    style={{ width: `${completionPct}%` }}
                  />
                </div>
              )}
            </Link>
          );
        })}
      </div>
    </div>
  );
}
