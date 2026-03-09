export type UserProfile = {
  id: number;
  full_name: string;
  email: string;
  current_role: string;
  target_role: string;
  years_experience: number;
  location: string;
  skills_current: string[];
  skills_target: string[];
  learning_preferences: string[];
  audience_mode?: "recent_graduate" | "career_switcher" | "mentor";
  weekly_hours_available: number;
  budget_limit: number;
};

export type ProfileScorecard = {
  profile_id: number;
  profile_completeness_score: number;
  market_competitiveness_score: number;
  readiness_label: "Emerging" | "Competitive" | "Strong";
  recommendations: string[];
  top_role_matches: Array<{
    job_id: number;
    title: string;
    company: string;
    fit_score: number;
  }>;
};

export type Job = {
  id: number;
  title: string;
  company: string;
  location: string;
  remote_type: string;
  experience_level: string;
  required_skills: string[];
  preferred_skills: string[];
  salary_min?: number;
  salary_max?: number;
  description: string;
};

export type Course = {
  id: number;
  title: string;
  provider: string;
  difficulty: string;
  duration_hours: number;
  cost_amount: number;
  format: string;
  url: string;
  rating: number;
  is_certificate: boolean;
  skills_covered: string[];
};

export type Roadmap = {
  id: number;
  title: string;
  summary: string;
  status: "draft" | "active" | "completed";
  generation_mode: "ai" | "fallback";
  generation_notes: string;
  ai_quality_indicator: "high" | "medium" | "fallback";
  confidence_score: number;
  target_job_id?: number;
  gap_analysis: {
    strengths: string[];
    missing_required_skills: string[];
    missing_preferred_skills: string[];
    required_coverage: number;
    preferred_coverage: number;
    match_score: number;
  };
  steps: Array<{
    order: number;
    goal: string;
    skill_focus: string[];
    recommended_course_ids: number[];
    recommended_courses?: Array<{
      title: string;
      url: string;
      provider?: string;
      cost_amount?: number;
      cost_currency?: string;
      skills_learned?: string[];
      duration_hours?: number;
      why_this_course?: string;
    }>;
    estimate_hours: number;
    completed?: boolean;
    rationale?: string;
    evidence?: string;
    confidence?: number;
  }>;
};

export type RoadmapSummary = {
  id: number;
  title: string;
  target_job_title: string;
  target_job_company: string;
  status: "draft" | "active" | "completed";
  generation_mode: "ai" | "fallback";
  ai_quality_indicator?: "high" | "medium" | "fallback";
  total_steps: number;
  completed_steps: number;
  created_at: string;
};

export type TransferableSkills = {
  profile_id: number;
  transferable_to_target: string[];
  high_demand_in_target: string[];
  suggested_bridges: string[];
};

export type ResumeImportResult = {
  mapped_profile: Omit<UserProfile, "id">;
  extracted_skills: string[];
  inferred_years_experience: number;
  inferred_from_projects: string[];
  transferable_skills: string[];
};

export type InterviewQuestions = {
  generation_mode: "ai" | "fallback";
  questions: Array<{
    question: string;
    category?: string;
    difficulty?: "easy" | "medium" | "hard";
  }>;
  notes?: string;
};

export type AnalyticsSummary = {
  profile_id: number;
  clarity_score: number;
  completion_percentage: number;
  roadmaps_generated: number;
  total_steps: number;
  steps_completed: number;
};
