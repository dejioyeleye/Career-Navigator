"use client";

import { getProfileScorecard, updateProfile } from "@/lib/api";
import { UserProfile } from "@/lib/types";
import { useEffect, useMemo, useState } from "react";

export function ProfileEditor({ profile }: { profile: UserProfile }) {
  const historyKey = `skillbridge:score-history:${profile.id}`;
  const [hours, setHours] = useState(profile.weekly_hours_available);
  const [budget, setBudget] = useState(profile.budget_limit);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [scoreDelta, setScoreDelta] = useState<number | null>(null);
  const [latestScore, setLatestScore] = useState<number | null>(null);
  const [scoreHistory, setScoreHistory] = useState<number[]>([]);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(historyKey);
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) {
        const valid = parsed.filter((x) => typeof x === "number" && x >= 0 && x <= 100);
        setScoreHistory(valid.slice(-5));
      }
    } catch {
      // ignore malformed local storage
    }
  }, [historyKey]);

  const sparklinePoints = useMemo(() => {
    if (scoreHistory.length === 0) return "";
    const width = 120;
    const height = 36;
    const max = Math.max(...scoreHistory, 100);
    const min = Math.min(...scoreHistory, 0);
    const spread = Math.max(1, max - min);
    return scoreHistory
      .map((value, index) => {
        const x = scoreHistory.length === 1 ? 0 : (index / (scoreHistory.length - 1)) * width;
        const y = height - ((value - min) / spread) * height;
        return `${x},${y}`;
      })
      .join(" ");
  }, [scoreHistory]);

  const onSave = async () => {
    try {
      setLoading(true);
      setError("");
      setMessage("");
      setScoreDelta(null);

      const before = await getProfileScorecard(profile.id);
      const updated = await updateProfile(profile.id, {
        weekly_hours_available: Number(hours),
        budget_limit: Number(budget),
      });
      const after = await getProfileScorecard(profile.id);

      setHours(updated.weekly_hours_available);
      setBudget(updated.budget_limit);
      setMessage("Profile updated successfully.");
      setLatestScore(after.market_competitiveness_score);
      setScoreDelta(after.market_competitiveness_score - before.market_competitiveness_score);

      const nextHistory = [...scoreHistory, after.market_competitiveness_score].slice(-5);
      setScoreHistory(nextHistory);
      window.localStorage.setItem(historyKey, JSON.stringify(nextHistory));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Update failed");
    } finally {
      setLoading(false);
    }
  };

  const resetTrendHistory = () => {
    setScoreHistory([]);
    setScoreDelta(null);
    setLatestScore(null);
    window.localStorage.removeItem(historyKey);
  };

  return (
    <div className="card p-5 space-y-3">
      <h2 className="font-semibold">Update Constraints</h2>
      {message && <p className="text-sm text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg p-2">{message}</p>}
      {error && <p className="text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg p-2">{error}</p>}
      {scoreDelta !== null && (
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-3 space-y-2">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-700">Market competitiveness trend</p>
            <span
              className={`badge ${
                scoreDelta > 0
                  ? "bg-emerald-100 text-emerald-700"
                  : scoreDelta < 0
                    ? "bg-red-100 text-red-700"
                    : "bg-slate-200 text-slate-700"
              }`}
            >
              {scoreDelta > 0 ? `+${scoreDelta}` : scoreDelta}% ({latestScore}%)
            </span>
          </div>
          {scoreHistory.length > 1 && (
            <div className="rounded-md border border-slate-200 bg-white p-2">
              <svg viewBox="0 0 120 36" className="h-10 w-full" role="img" aria-label="Competitiveness score trend">
                <polyline fill="none" stroke="#4f46e5" strokeWidth="2" points={sparklinePoints} />
              </svg>
              <div className="mt-1 flex items-center justify-between">
                <p className="text-xs text-slate-500">Last {scoreHistory.length} snapshots</p>
                <button
                  type="button"
                  onClick={resetTrendHistory}
                  className="text-xs text-slate-600 hover:text-slate-900 underline"
                >
                  Reset trend history
                </button>
              </div>
            </div>
          )}
        </div>
      )}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-sm">Hours / Week</label>
          <input type="number" className="input mt-1" value={hours} onChange={(e) => setHours(Number(e.target.value))} />
        </div>
        <div>
          <label className="text-sm">Budget (USD)</label>
          <input type="number" className="input mt-1" value={budget} onChange={(e) => setBudget(Number(e.target.value))} />
        </div>
      </div>
      <button className="btn-primary disabled:opacity-50" disabled={loading} onClick={onSave}>
        {loading ? "Saving..." : "Save Updates"}
      </button>
    </div>
  );
}
