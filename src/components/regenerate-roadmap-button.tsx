"use client";

import { generateRoadmap } from "@/lib/api";
import { useRouter } from "next/navigation";
import { useState } from "react";

export function RegenerateRoadmapButton({ profileId }: { profileId: number }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleRegenerate = async () => {
    if (!confirm("Generate a new roadmap version for this profile?")) return;

    try {
      setLoading(true);
      setError("");
      const roadmap = await generateRoadmap(profileId);
      router.push(`/roadmaps/${roadmap.id}?profile=${profileId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to regenerate");
      setTimeout(() => setError(""), 3000);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button
        onClick={handleRegenerate}
        disabled={loading}
        className="btn-primary disabled:opacity-50"
      >
        {loading ? "Generating..." : "🔄 Regenerate Roadmap"}
      </button>
      {error && <p className="text-sm text-red-600 mt-1">{error}</p>}
    </div>
  );
}
