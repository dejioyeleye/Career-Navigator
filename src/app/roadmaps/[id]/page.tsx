import Link from "next/link";

import { getRoadmap } from "@/lib/api";
import { RoadmapHeader } from "@/components/roadmap-header";
import { InterviewQuestionsCard } from "@/components/interview-questions";
import { RoadmapStepEditor } from "@/components/roadmap-step-editor";

export default async function RoadmapPage({ params, searchParams }: { params: { id: string }; searchParams?: { profile?: string } }) {
  const roadmap = await getRoadmap(Number(params.id));
  const requiredCoveragePct = Math.round(roadmap.gap_analysis.required_coverage * 100);
  const preferredCoveragePct = Math.round(roadmap.gap_analysis.preferred_coverage * 100);

  return (
    <section className="space-y-6">
      <RoadmapHeader
        title={roadmap.title}
        summary={roadmap.summary}
        generationMode={roadmap.generation_mode}
        generationNotes={roadmap.generation_notes}
      />

      {roadmap.ai_quality_indicator && (
        <div className="card p-4 bg-slate-50">
          <div className="flex items-center gap-3">
            <span
              className={`px-2 py-1 text-xs font-medium rounded-full ${
                roadmap.ai_quality_indicator === "high"
                  ? "bg-green-100 text-green-700"
                  : roadmap.ai_quality_indicator === "medium"
                  ? "bg-amber-100 text-amber-700"
                  : "bg-slate-200 text-slate-700"
              }`}
            >
              {roadmap.ai_quality_indicator === "fallback" ? "Basic" : 
               roadmap.ai_quality_indicator.charAt(0).toUpperCase() + roadmap.ai_quality_indicator.slice(1)} Quality
            </span>
            {roadmap.confidence_score !== undefined && (
              <span className="text-sm text-slate-600">
                Confidence: {Math.round(roadmap.confidence_score * 100)}%
              </span>
            )}
          </div>
        </div>
      )}

      <div className="card p-5">
        <RoadmapStepEditor roadmap={roadmap} />
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="card p-5 md:col-span-1">
          <h2 className="font-semibold">Match Score</h2>
          <p className="text-3xl mt-2 font-bold text-brand-700">{Math.round(roadmap.gap_analysis.match_score * 100)}%</p>
          <div className="mt-4 space-y-3">
            <div>
              <p className="text-xs text-slate-500 mb-1">Required Skill Coverage</p>
              <div className="h-2 rounded-full bg-slate-200 overflow-hidden">
                <div className="h-2 bg-indigo-500" style={{ width: `${requiredCoveragePct}%` }} />
              </div>
              <p className="text-xs mt-1 text-slate-600">{requiredCoveragePct}%</p>
            </div>
            <div>
              <p className="text-xs text-slate-500 mb-1">Preferred Skill Coverage</p>
              <div className="h-2 rounded-full bg-slate-200 overflow-hidden">
                <div className="h-2 bg-violet-500" style={{ width: `${preferredCoveragePct}%` }} />
              </div>
              <p className="text-xs mt-1 text-slate-600">{preferredCoveragePct}%</p>
            </div>
          </div>
          <h3 className="font-medium mt-4">Missing Required Skills</h3>
          <div className="mt-2 flex flex-wrap gap-2">
            {roadmap.gap_analysis.missing_required_skills.map((s) => (
              <span key={s} className="badge bg-red-100 text-red-700">{s}</span>
            ))}
          </div>
        </div>
        <div className="card p-5 md:col-span-2">
          <h2 className="font-semibold">Roadmap Timeline</h2>
          <ol className="mt-4 space-y-4 relative before:absolute before:left-4 before:top-2 before:bottom-2 before:w-px before:bg-slate-200">
            {roadmap.steps.map((step) => (
              <li key={step.order} className="pl-10 relative">
                <span className="absolute left-0 top-4 h-8 w-8 rounded-full bg-brand-500 text-white text-sm font-semibold grid place-items-center shadow-sm">
                  {step.order}
                </span>
                <div className="rounded-2xl border border-slate-200 p-4 hover:shadow-md transition bg-white">
                  <p className="font-medium">{step.goal}</p>
                  <p className="text-sm text-slate-600 mt-1">Estimated effort: {step.estimate_hours} hours</p>
                  
                  {step.rationale && (
                    <p className="text-xs text-slate-500 mt-2 italic">💡 {step.rationale}</p>
                  )}
                  
                  {step.evidence && (
                    <p className="text-xs text-green-700 mt-1">✓ Evidence: {step.evidence}</p>
                  )}
                  
                  {step.confidence !== undefined && (
                    <div className="mt-2">
                      <span className="text-xs text-slate-500">
                        Confidence: {Math.round(step.confidence * 100)}%
                      </span>
                    </div>
                  )}

                  {step.recommended_courses && step.recommended_courses.length > 0 && (
                    <div className="mt-3 space-y-2">
                      <p className="text-xs font-medium text-slate-700">Recommended courses</p>
                      <div className="grid gap-2 md:grid-cols-2">
                        {step.recommended_courses.slice(0, 4).map((course) => (
                          <div key={`${step.order}-${course.title}-${course.url}`} className="rounded-lg border border-slate-200 p-3 bg-slate-50">
                            <p className="text-sm font-medium text-slate-900">{course.title}</p>
                            <p className="text-xs text-slate-600 mt-1">
                              {course.provider || "Provider"}
                              {typeof course.cost_amount === "number" ? ` • ${course.cost_currency || "USD"} ${course.cost_amount}` : ""}
                            </p>
                            {course.skills_learned && course.skills_learned.length > 0 && (
                              <p className="text-xs text-slate-600 mt-1">
                                Skills: {course.skills_learned.slice(0, 4).join(", ")}
                              </p>
                            )}
                            {course.why_this_course && (
                              <p className="text-xs text-slate-500 mt-1 italic">{course.why_this_course}</p>
                            )}
                            <a
                              href={course.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex mt-2 text-xs px-2 py-1 rounded bg-indigo-600 text-white hover:bg-indigo-700"
                            >
                              Open course
                            </a>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <p className="text-xs text-slate-500 mt-2">Recommended resources: {step.recommended_course_ids.length}</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {step.skill_focus.map((skill) => (
                      <span key={skill} className="badge bg-indigo-100 text-indigo-700">{skill}</span>
                    ))}
                  </div>
                </div>
              </li>
            ))}
          </ol>
          {roadmap.gap_analysis.missing_preferred_skills.length > 0 && (
            <div className="mt-5 rounded-xl border border-violet-200 bg-violet-50 p-4">
              <p className="text-sm font-medium text-violet-900">Optional Differentiators</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {roadmap.gap_analysis.missing_preferred_skills.map((skill) => (
                  <span key={skill} className="badge bg-violet-100 text-violet-700">{skill}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {searchParams?.profile && (
        <InterviewQuestionsCard
          profileId={Number(searchParams.profile)}
          targetJobId={roadmap.target_job_id}
        />
      )}

      {searchParams?.profile && (
        <Link href={`/profiles/${searchParams.profile}`} className="text-brand-700 hover:underline">View profile details</Link>
      )}
    </section>
  );
}
