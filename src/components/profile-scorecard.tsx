import { ProfileScorecard } from "@/lib/types";

export function ProfileScorecardCard({ scorecard }: { scorecard: ProfileScorecard }) {
  const readinessTone =
    scorecard.readiness_label === "Strong"
      ? "bg-emerald-100 text-emerald-700"
      : scorecard.readiness_label === "Competitive"
        ? "bg-blue-100 text-blue-700"
        : "bg-amber-100 text-amber-700";

  return (
    <div className="card p-5 space-y-4">
      <div className="flex items-center justify-between gap-3">
        <h2 className="font-semibold">Recruiter-Style Snapshot</h2>
        <span className={`badge ${readinessTone}`}>{scorecard.readiness_label}</span>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-slate-500 mb-1">Profile Completeness</p>
          <div className="h-2 rounded-full bg-slate-200 overflow-hidden">
            <div className="h-2 bg-indigo-500" style={{ width: `${scorecard.profile_completeness_score}%` }} />
          </div>
          <p className="text-sm font-medium mt-2">{scorecard.profile_completeness_score}%</p>
        </div>
        <div>
          <p className="text-xs text-slate-500 mb-1">Market Competitiveness</p>
          <div className="h-2 rounded-full bg-slate-200 overflow-hidden">
            <div className="h-2 bg-violet-500" style={{ width: `${scorecard.market_competitiveness_score}%` }} />
          </div>
          <p className="text-sm font-medium mt-2">{scorecard.market_competitiveness_score}%</p>
        </div>
      </div>

      <div>
        <p className="text-sm font-medium">Top Role Matches</p>
        <div className="mt-2 space-y-2">
          {scorecard.top_role_matches.map((match) => (
            <div key={match.job_id} className="rounded-lg border border-slate-200 p-3 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">{match.title}</p>
                <p className="text-xs text-slate-500">{match.company}</p>
              </div>
              <p className="text-sm font-semibold text-brand-700">{Math.round(match.fit_score * 100)}%</p>
            </div>
          ))}
        </div>
      </div>

      <div>
        <p className="text-sm font-medium">Recommended Next Moves</p>
        <ul className="mt-2 list-disc pl-5 text-sm text-slate-700 space-y-1">
          {scorecard.recommendations.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
