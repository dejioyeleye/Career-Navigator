import { getProfile, getProfileScorecard } from "@/lib/api";
import { ProfileEditor } from "@/components/profile-editor";
import { ProfileScorecardCard } from "@/components/profile-scorecard";
import { ProfileAnalytics } from "@/components/profile-analytics";
import { RoadmapList } from "@/components/roadmap-list";
import { TransferableSkillsCard } from "@/components/transferable-skills";
import { RegenerateRoadmapButton } from "@/components/regenerate-roadmap-button";
import Link from "next/link";

export default async function ProfileViewPage({ params }: { params: { id: string } }) {
  const [profile, scorecard] = await Promise.all([
    getProfile(Number(params.id)),
    getProfileScorecard(Number(params.id)),
  ]);

  const profileId = Number(params.id);

  return (
    <section className="space-y-6">
      <div className="card p-6">
        <h1 className="text-2xl font-semibold">{profile.full_name}</h1>
        <p className="text-slate-600 mt-1">{profile.current_role} → {profile.target_role}</p>
        <p className="text-sm text-slate-500 mt-1">{profile.location} • {profile.years_experience} years experience</p>
        {profile.audience_mode && (
          <span className="inline-block mt-2 px-2 py-1 text-xs font-medium rounded-full bg-indigo-100 text-indigo-700">
            {profile.audience_mode === "recent_graduate" && "🎓 Recent Graduate"}
            {profile.audience_mode === "career_switcher" && "🔄 Career Switcher"}
            {profile.audience_mode === "mentor" && "👨‍🏫 Mentor"}
          </span>
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="card p-5">
          <h2 className="font-semibold">Current Skills</h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {profile.skills_current.map((skill) => (
              <span key={skill} className="badge bg-indigo-100 text-indigo-700">{skill}</span>
            ))}
          </div>
        </div>
        <div className="card p-5">
          <h2 className="font-semibold">Target Skills</h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {profile.skills_target.map((skill) => (
              <span key={skill} className="badge bg-violet-100 text-violet-700">{skill}</span>
            ))}
          </div>
        </div>
      </div>

      <ProfileAnalytics profileId={profileId} />

      <ProfileScorecardCard scorecard={scorecard} />

      {profile.audience_mode === "career_switcher" && (
        <TransferableSkillsCard profileId={profileId} />
      )}

      <div className="card p-5">
        <h2 className="font-semibold mb-4">🗺️ Roadmap Actions</h2>
        <div className="flex flex-wrap gap-3">
          <RegenerateRoadmapButton profileId={profileId} />
          <Link href="/profiles/import" className="btn-secondary">
            Import Resume Data
          </Link>
        </div>
      </div>

      <RoadmapList profileId={profileId} />

      <ProfileEditor profile={profile} />
    </section>
  );
}
