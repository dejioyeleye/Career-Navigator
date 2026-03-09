from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict | None = None


class UserProfileBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    current_role: str = Field(min_length=2, max_length=120)
    target_role: str = Field(min_length=2, max_length=120)
    years_experience: float = Field(ge=0, le=40)
    location: str = Field(min_length=2, max_length=120)
    skills_current: list[str] = Field(min_length=1)
    skills_target: list[str] = Field(default_factory=list)
    learning_preferences: list[str] = Field(default_factory=list)
    audience_mode: Literal["recent_graduate", "career_switcher", "mentor"] | None = None
    weekly_hours_available: int = Field(ge=1, le=60)
    budget_limit: float = Field(ge=0, le=100000)


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    current_role: str | None = Field(default=None, min_length=2, max_length=120)
    target_role: str | None = Field(default=None, min_length=2, max_length=120)
    years_experience: float | None = Field(default=None, ge=0, le=40)
    location: str | None = Field(default=None, min_length=2, max_length=120)
    skills_current: list[str] | None = None
    skills_target: list[str] | None = None
    learning_preferences: list[str] | None = None
    weekly_hours_available: int | None = Field(default=None, ge=1, le=60)
    budget_limit: float | None = Field(default=None, ge=0, le=100000)


class UserProfileOut(UserProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ResumeImportPayload(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    current_role: str | None = None
    target_role: str | None = None
    location: str | None = None
    years_experience: float | None = Field(default=None, ge=0, le=40)
    skills: list[str] = Field(default_factory=list)
    experience: list[dict] = Field(default_factory=list)
    projects: list[dict] = Field(default_factory=list)
    repos: list[dict] = Field(default_factory=list)
    learning_preferences: list[str] = Field(default_factory=list)
    audience_mode: Literal["recent_graduate", "career_switcher", "mentor"] | None = None


class ResumeImportResult(BaseModel):
    mapped_profile: UserProfileCreate
    extracted_skills: list[str]
    inferred_years_experience: float
    inferred_from_projects: list[str]
    transferable_skills: list[str]


class TopRoleMatch(BaseModel):
    job_id: int
    title: str
    company: str
    fit_score: float = Field(ge=0, le=1)


class ProfileScorecardOut(BaseModel):
    profile_id: int
    profile_completeness_score: int = Field(ge=0, le=100)
    market_competitiveness_score: int = Field(ge=0, le=100)
    readiness_label: Literal["Emerging", "Competitive", "Strong"]
    recommendations: list[str]
    top_role_matches: list[TopRoleMatch]


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: str
    location: str
    remote_type: str
    experience_level: str
    salary_min: int | None
    salary_max: int | None
    currency: str
    required_skills: list[str]
    preferred_skills: list[str]
    description: str


class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    provider: str
    difficulty: str
    duration_hours: float
    cost_amount: float
    cost_currency: str
    format: str
    url: HttpUrl
    rating: float
    is_certificate: bool
    skills_covered: list[str]


class RecommendedCourse(BaseModel):
    title: str
    url: str
    provider: str | None = None
    cost_amount: float | None = None
    cost_currency: str | None = "USD"
    skills_learned: list[str] = Field(default_factory=list)
    duration_hours: float | None = None
    why_this_course: str | None = None


class RoadmapStep(BaseModel):
    order: int
    goal: str
    skill_focus: list[str]
    recommended_course_ids: list[int] = Field(default_factory=list)
    recommended_courses: list[RecommendedCourse] = Field(default_factory=list)
    estimate_hours: float
    rationale: str | None = None
    evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.7, ge=0, le=1)


class GapAnalysis(BaseModel):
    strengths: list[str]
    missing_required_skills: list[str]
    missing_preferred_skills: list[str]
    required_coverage: float = Field(default=0, ge=0, le=1)
    preferred_coverage: float = Field(default=0, ge=0, le=1)
    match_score: float = Field(ge=0, le=1)


class RoadmapCreate(BaseModel):
    user_profile_id: int
    target_job_id: int | None = None
    audience_mode: Literal["recent_graduate", "career_switcher", "mentor"] | None = None


class RoadmapStepsUpdate(BaseModel):
    steps: list[RoadmapStep]


class RoadmapSummary(BaseModel):
    id: int
    title: str
    target_job_title: str
    target_job_company: str
    status: Literal["draft", "active", "completed"]
    generation_mode: Literal["ai", "fallback"]
    ai_quality_indicator: Literal["high", "medium", "fallback"] | None = None
    total_steps: int
    completed_steps: int
    created_at: datetime


class RoadmapOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_profile_id: int
    target_job_id: int | None
    title: str
    summary: str
    status: Literal["draft", "active", "completed"]
    steps: list[RoadmapStep]
    gap_analysis: GapAnalysis
    generation_mode: Literal["ai", "fallback"]
    generation_notes: str
    ai_quality_indicator: Literal["high", "medium", "fallback"]
    confidence_score: float = Field(ge=0, le=1)
    created_at: datetime
    updated_at: datetime


class TransferableSkillsOut(BaseModel):
    profile_id: int
    transferable_to_target: list[str]
    high_demand_in_target: list[str]
    suggested_bridges: list[str]


class InterviewQuestion(BaseModel):
    question: str
    category: str | None = None
    difficulty: Literal["easy", "medium", "hard"] | None = None


class InterviewQuestionsRequest(BaseModel):
    user_profile_id: int
    newly_added_skills: list[str] = Field(default_factory=list)
    count: int = Field(default=5, ge=3, le=10)


class InterviewQuestionsOut(BaseModel):
    generation_mode: Literal["ai", "fallback"]
    questions: list[InterviewQuestion]
    notes: str | None = None


class AnalyticsSummaryOut(BaseModel):
    profile_id: int
    clarity_score: int = Field(ge=0, le=100)
    completion_percentage: int = Field(ge=0, le=100)
    roadmaps_generated: int
    total_steps: int
    steps_completed: int
