"use client";

import { TransferableSkills } from "@/lib/types";
import { useEffect, useState } from "react";
import { getTransferableSkills } from "@/lib/api";

export function TransferableSkillsCard({ profileId }: { profileId: number }) {
  const [skills, setSkills] = useState<TransferableSkills | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getTransferableSkills(profileId)
      .then(setSkills)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [profileId]);

  if (loading) {
    return (
      <div className="card p-5">
        <p className="text-slate-500">Analyzing transferable skills...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card p-5">
        <p className="text-red-600">Failed to analyze: {error}</p>
      </div>
    );
  }

  if (!skills || skills.transferable_to_target.length === 0) {
    return (
      <div className="card p-5">
        <p className="text-slate-500">No transferable skills identified yet.</p>
      </div>
    );
  }

  return (
    <div className="card p-5">
      <h2 className="font-semibold mb-4">🔄 Transferable Skills Analysis</h2>
      
      <div className="space-y-4">
        <div>
          <h3 className="text-sm font-medium text-slate-700 mb-2">
            ✅ Already Applicable ({skills.transferable_to_target.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {skills.transferable_to_target.map((skill) => (
              <span key={skill} className="badge bg-green-100 text-green-700">
                {skill}
              </span>
            ))}
          </div>
          <p className="text-xs text-slate-600 mt-2">
            These skills from your current role directly apply to your target role.
          </p>
        </div>

        {skills.high_demand_in_target.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-slate-700 mb-2">
              🎯 High-Demand Target Skills ({skills.high_demand_in_target.length})
            </h3>
            <div className="flex flex-wrap gap-2">
              {skills.high_demand_in_target.map((skill) => (
                <span key={skill} className="badge bg-amber-100 text-amber-700">
                  {skill}
                </span>
              ))}
            </div>
            <p className="text-xs text-slate-600 mt-2">
              Focus your learning on these skills—they're commonly required in your target field.
            </p>
          </div>
        )}

        {skills.suggested_bridges.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-slate-700 mb-2">
              🌉 Bridge Skills ({skills.suggested_bridges.length})
            </h3>
            <div className="flex flex-wrap gap-2">
              {skills.suggested_bridges.map((skill) => (
                <span key={skill} className="badge bg-indigo-100 text-indigo-700">
                  {skill}
                </span>
              ))}
            </div>
            <p className="text-xs text-slate-600 mt-2">
              Learning these will help connect your current expertise to your target role.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
