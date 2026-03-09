"use client";

import { AnalyticsSummary } from "@/lib/types";
import { useEffect, useState } from "react";
import { getAnalytics } from "@/lib/api";

export function ProfileAnalytics({ profileId }: { profileId: number }) {
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getAnalytics(profileId)
      .then(setAnalytics)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [profileId]);

  if (loading) {
    return (
      <div className="card p-5">
        <p className="text-slate-500">Loading analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card p-5">
        <p className="text-red-600">Failed to load analytics: {error}</p>
      </div>
    );
  }

  if (!analytics) return null;

  const clarityColor =
    analytics.clarity_score >= 80 ? "text-green-600" :
    analytics.clarity_score >= 60 ? "text-amber-600" :
    "text-red-600";

  const completionColor =
    analytics.completion_percentage >= 70 ? "text-green-600" :
    analytics.completion_percentage >= 40 ? "text-amber-600" :
    "text-red-600";

  return (
    <div className="card p-5">
      <h2 className="font-semibold mb-4">📊 Profile Analytics</h2>
      
      <div className="grid sm:grid-cols-3 gap-4">
        <div>
          <p className="text-sm text-slate-500">Clarity Score</p>
          <p className={`text-2xl font-bold ${clarityColor}`}>{analytics.clarity_score}%</p>
          <p className="text-xs text-slate-600 mt-1">
            {analytics.clarity_score >= 80 ? "Well-defined profile" :
             analytics.clarity_score >= 60 ? "Some gaps exist" :
             "Needs more detail"}
          </p>
        </div>

        <div>
          <p className="text-sm text-slate-500">Roadmap Progress</p>
          <p className={`text-2xl font-bold ${completionColor}`}>
            {analytics.completion_percentage}%
          </p>
          <p className="text-xs text-slate-600 mt-1">
            {analytics.roadmaps_generated > 0
              ? `${analytics.steps_completed} of ${analytics.total_steps} steps`
              : "No roadmaps yet"}
          </p>
        </div>

        <div>
          <p className="text-sm text-slate-500">Roadmaps Generated</p>
          <p className="text-2xl font-bold text-indigo-600">{analytics.roadmaps_generated}</p>
          <p className="text-xs text-slate-600 mt-1">
            {analytics.roadmaps_generated === 0 ? "Start your first roadmap" :
             analytics.roadmaps_generated === 1 ? "Keep exploring" :
             "Multiple paths explored"}
          </p>
        </div>
      </div>
    </div>
  );
}
