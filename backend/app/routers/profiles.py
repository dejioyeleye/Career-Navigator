from __future__ import annotations

import io
import json
import logging
import re

import PyPDF2
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import JobDescription, Roadmap, UserProfile
from ..schemas import (
    AnalyticsSummaryOut,
    ProfileScorecardOut,
    ResumeImportPayload,
    ResumeImportResult,
    TopRoleMatch,
    TransferableSkillsOut,
    UserProfileCreate,
    UserProfileOut,
    UserProfileUpdate,
)
from ..services.gap_analysis import score_job_fit
from ..services.gemini import gemini_service
from ..services.taxonomy import canonicalize_skills, extract_transferable_skills

logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


router = APIRouter(prefix="/api/profiles", tags=["profiles"])


def _normalize_preferences(preferences: list[str], audience_mode: str | None) -> list[str]:
    base = [p.strip() for p in preferences if p.strip()]
    if audience_mode:
        marker = f"audience:{audience_mode}"
        if marker not in base:
            base.append(marker)
    return base


def _extract_audience_mode(preferences: list[str]) -> str | None:
    for pref in preferences:
        if pref.startswith("audience:"):
            return pref.split(":", maxsplit=1)[1]
    return None


def to_out(model: UserProfile) -> UserProfileOut:
    preferences = json.loads(model.learning_preferences_json)
    return UserProfileOut(
        id=model.id,
        full_name=model.full_name,
        email=model.email,
        current_role=model.current_role,
        target_role=model.target_role,
        years_experience=model.years_experience,
        location=model.location,
        skills_current=canonicalize_skills(json.loads(model.skills_current_json)),
        skills_target=canonicalize_skills(json.loads(model.skills_target_json)),
        learning_preferences=preferences,
        audience_mode=_extract_audience_mode(preferences),
        weekly_hours_available=model.weekly_hours_available,
        budget_limit=model.budget_limit,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _build_scorecard(profile: UserProfile, db: Session) -> ProfileScorecardOut:
    skills_current = canonicalize_skills(json.loads(profile.skills_current_json))
    skills_target = canonicalize_skills(json.loads(profile.skills_target_json))
    preferences = json.loads(profile.learning_preferences_json)

    completeness = 0
    completeness += 20
    completeness += min(25, int((len(skills_current) / 8) * 25))
    completeness += min(15, int((len(skills_target) / 5) * 15))
    completeness += min(10, int((len(preferences) / 3) * 10))
    completeness += 10 if profile.weekly_hours_available >= 4 else 6
    completeness += 10 if profile.budget_limit > 0 else 7
    completeness += 10 if profile.years_experience >= 1 else 7
    completeness = min(100, completeness)

    jobs = db.query(JobDescription).all()
    ranked: list[tuple[JobDescription, float]] = []
    for job in jobs:
        fit = score_job_fit(
            user_skills=skills_current,
            required_skills=canonicalize_skills(json.loads(job.required_skills_json)),
            preferred_skills=canonicalize_skills(json.loads(job.preferred_skills_json)),
            target_role=profile.target_role,
            job_title=job.title,
            years_experience=profile.years_experience,
            experience_level=job.experience_level,
        )
        ranked.append((job, fit))

    ranked.sort(key=lambda item: item[1], reverse=True)
    top_three = ranked[:3]
    competitiveness = int(round((sum(score for _, score in top_three) / len(top_three)) * 100)) if top_three else 0

    top_matches = [
        TopRoleMatch(job_id=job.id, title=job.title, company=job.company, fit_score=score)
        for job, score in top_three
    ]

    recommendations: list[str] = []
    if len(skills_target) == 0:
        recommendations.append("Add target skills to improve roadmap personalization.")
    if len(preferences) == 0:
        recommendations.append("Add learning preferences so recommendations better match your style.")
    if competitiveness < 55 and top_three:
        top_job = top_three[0][0]
        required = canonicalize_skills(json.loads(top_job.required_skills_json))
        user = set(skills_current)
        missing = [s for s in required if s not in user][:3]
        if missing:
            recommendations.append(f"Prioritize these target-role skills: {', '.join(missing)}.")
    if profile.weekly_hours_available < 5:
        recommendations.append("Increase weekly learning time to at least 5 hours for faster role readiness.")
    if not recommendations:
        recommendations.append("Your profile is in strong shape. Keep executing roadmap milestones consistently.")

    readiness_label = "Emerging"
    if competitiveness >= 75:
        readiness_label = "Strong"
    elif competitiveness >= 55:
        readiness_label = "Competitive"

    return ProfileScorecardOut(
        profile_id=profile.id,
        profile_completeness_score=completeness,
        market_competitiveness_score=competitiveness,
        readiness_label=readiness_label,
        recommendations=recommendations,
        top_role_matches=top_matches,
    )


@router.post("/import", response_model=ResumeImportResult)
async def import_resume(
    file: UploadFile = File(...),
):  
    """Import resume data from PDF file using Gemini AI with rate limiting and validation."""
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    # Validate file size
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_resume_size_mb:
        raise HTTPException(
            status_code=400,
            detail=f"File size ({size_mb:.2f}MB) exceeds limit of {settings.max_resume_size_mb}MB"
        )
    
    try:
        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="PDF appears to be empty or unreadable")
        
        # Use Gemini to parse resume with fallback to basic extraction
        try:
            if settings.gemini_api_key:
                logger.info("Parsing resume with Gemini AI")
                parsed_data = await gemini_service.parse_resume(text)
            else:
                logger.warning("Gemini API key not configured, using basic extraction")
                raise ValueError("Gemini not configured")
        except Exception as e:
            logger.warning(f"Gemini parsing failed: {e}, falling back to keyword extraction")
            # Fallback: Basic keyword extraction
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            parsed_data = {
                "full_name": lines[0] if lines else None,
                "email": next((line for line in lines if "@" in line), None),
                "current_role": None,
                "target_role": None,
                "location": None,
                "years_experience": None,
                "skills": [],
            }
            # Extract common skills
            skill_keywords = ["python", "sql", "javascript", "aws", "docker", "kubernetes",
                            "fastapi", "react", "typescript", "git", "linux", "terraform"]
            text_lower = text.lower()
            parsed_data["skills"] = [skill for skill in skill_keywords if skill in text_lower]
        
        # Canonicalize skills
        extracted_skills = canonicalize_skills(parsed_data.get("skills", []))
        transferable = extract_transferable_skills(extracted_skills, ["sql", "python", "git"])
        
        # Helper function to safely extract and validate string fields
        def safe_str(value, default):
            if value and isinstance(value, str) and value.strip():
                return value.strip()
            return default
        
        # Helper to safely extract numeric values
        def safe_float(value, default):
            if value is None:
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        # Extract and validate email using regex pattern
        email = "unknown@example.com"
        email_raw = parsed_data.get("email", "")
        if email_raw and isinstance(email_raw, str):
            # Try to extract email using regex - looks for word@word.word pattern
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            matches = re.findall(email_pattern, email_raw)
            if matches:
                email = matches[0]  # Use first valid email found
        
        # Build a complete UserProfileCreate object with validated defaults
        mapped_profile = UserProfileCreate(
            full_name=safe_str(parsed_data.get("full_name"), "Unknown Candidate"),
            email=email,
            current_role=safe_str(parsed_data.get("current_role"), "Professional"),
            target_role=safe_str(parsed_data.get("target_role"), "Senior Professional"),
            years_experience=safe_float(parsed_data.get("years_experience"), 2.0),
            location=safe_str(parsed_data.get("location"), "Remote"),
            skills_current=extracted_skills[:30] if extracted_skills else ["general"],
            skills_target=[],
            learning_preferences=[],
            audience_mode=None,
            weekly_hours_available=8,
            budget_limit=100.0,
        )
        
        # Return structured result
        return ResumeImportResult(
            mapped_profile=mapped_profile,
            extracted_skills=extracted_skills,
            inferred_years_experience=float(parsed_data.get("years_experience") or 0),
            inferred_from_projects=[],
            transferable_skills=transferable,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to parse PDF: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")


@router.post("", response_model=UserProfileOut)
def create_profile(payload: UserProfileCreate, db: Session = Depends(get_db)):
    existing = db.query(UserProfile).filter(UserProfile.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail={"code": "VALIDATION", "message": "Email already exists"})

    profile = UserProfile(
        full_name=payload.full_name,
        email=payload.email,
        current_role=payload.current_role,
        target_role=payload.target_role,
        years_experience=payload.years_experience,
        location=payload.location,
        skills_current_json=json.dumps(canonicalize_skills(payload.skills_current)),
        skills_target_json=json.dumps(canonicalize_skills(payload.skills_target)),
        learning_preferences_json=json.dumps(_normalize_preferences(payload.learning_preferences, payload.audience_mode)),
        weekly_hours_available=payload.weekly_hours_available,
        budget_limit=payload.budget_limit,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return to_out(profile)


@router.get("/{profile_id}", response_model=UserProfileOut)
def get_profile(profile_id: int, db: Session = Depends(get_db)):
    profile = db.get(UserProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Profile not found"})
    return to_out(profile)


@router.put("/{profile_id}", response_model=UserProfileOut)
def update_profile(profile_id: int, payload: UserProfileUpdate, db: Session = Depends(get_db)):
    profile = db.get(UserProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Profile not found"})

    data = payload.model_dump(exclude_none=True)
    for key, value in data.items():
        if key in {"skills_current", "skills_target", "learning_preferences"}:
            if key == "learning_preferences":
                audience_mode = _extract_audience_mode(json.loads(profile.learning_preferences_json))
                value = _normalize_preferences(value, audience_mode)
            elif key in {"skills_current", "skills_target"}:
                value = canonicalize_skills(value)
            setattr(profile, f"{key}_json", json.dumps(value))
        else:
            setattr(profile, key, value)

    db.add(profile)
    db.commit()
    db.refresh(profile)
    return to_out(profile)


@router.get("/{profile_id}/scorecard", response_model=ProfileScorecardOut)
def get_profile_scorecard(profile_id: int, db: Session = Depends(get_db)):
    profile = db.get(UserProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Profile not found"})
    return _build_scorecard(profile, db)


@router.get("/{profile_id}/transferable-skills", response_model=TransferableSkillsOut)
def get_transferable_skills(profile_id: int, db: Session = Depends(get_db)):
    profile = db.get(UserProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Profile not found"})

    jobs = db.query(JobDescription).filter(JobDescription.title.ilike(f"%{profile.target_role}%")).all()
    if not jobs:
        jobs = db.query(JobDescription).all()

    target_required: list[str] = []
    target_preferred: list[str] = []
    for job in jobs[:5]:
        target_required.extend(json.loads(job.required_skills_json))
        target_preferred.extend(json.loads(job.preferred_skills_json))

    current_skills = canonicalize_skills(json.loads(profile.skills_current_json))
    transferable = extract_transferable_skills(current_skills, target_required)
    
    # High demand skills are those appearing frequently in target jobs
    target_all = target_required + target_preferred
    skill_frequency = {}
    for skill in canonicalize_skills(target_all):
        skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
    high_demand = sorted(skill_frequency.keys(), key=lambda s: -skill_frequency[s])[:5]
    
    # Bridge skills are target skills not yet possessed
    target_set = set(canonicalize_skills(target_required))
    missing = [skill for skill in sorted(target_set) if skill not in set(current_skills)]

    return TransferableSkillsOut(
        profile_id=profile.id,
        transferable_to_target=transferable,
        high_demand_in_target=high_demand,
        suggested_bridges=missing[:6],
    )


@router.get("/{profile_id}/analytics", response_model=AnalyticsSummaryOut)
def get_profile_analytics(profile_id: int, db: Session = Depends(get_db)):
    profile = db.get(UserProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Profile not found"})

    roadmaps = db.query(Roadmap).filter(Roadmap.user_profile_id == profile.id).all()
    
    # Compute clarity score based on profile completeness
    clarity = 0
    skills_target = json.loads(profile.skills_target_json) if profile.skills_target_json else []
    learning_prefs = json.loads(profile.learning_preferences_json) if profile.learning_preferences_json else []
    
    if skills_target and len(skills_target) > 0:
        clarity += 30
    if learning_prefs and len(learning_prefs) > 0:
        clarity += 20
    if profile.target_role:
        clarity += 30
    if len(roadmaps) > 0:
        clarity += 20
    
    # Compute total steps and completed steps across all roadmaps
    total_steps = 0
    steps_completed = 0
    for roadmap in roadmaps:
        steps = json.loads(roadmap.steps_json)
        total_steps += len(steps)
        steps_completed += sum(1 for s in steps if s.get("completed", False))
    
    # Compute completion percentage
    completion_pct = 0
    if total_steps > 0:
        completion_pct = int(round((steps_completed / total_steps) * 100))

    return AnalyticsSummaryOut(
        profile_id=profile.id,
        clarity_score=clarity,
        completion_percentage=completion_pct,
        roadmaps_generated=len(roadmaps),
        total_steps=total_steps,
        steps_completed=steps_completed,
    )
