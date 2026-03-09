from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import CourseResource, JobDescription, Roadmap, UserProfile
from ..schemas import GapAnalysis, RoadmapCreate, RoadmapOut, RoadmapStep, RoadmapStepsUpdate, RoadmapSummary
from ..services.ai_service import AIServiceError, generate_ai_roadmap
from ..services.gap_analysis import calculate_gap, score_job_fit
from ..services.mvp_static import build_mvp_static_roadmap
from ..services.roadmap_builder import build_fallback_roadmap


router = APIRouter(prefix="/api/roadmaps", tags=["roadmaps"])


def to_out(model: Roadmap) -> RoadmapOut:
    steps = [RoadmapStep(**s) for s in json.loads(model.steps_json)]
    gap = GapAnalysis(**json.loads(model.gap_analysis_json))
    if model.generation_mode == "ai":
        quality = "high" if gap.match_score >= 0.7 else "medium"
        confidence = 0.86 if gap.match_score >= 0.7 else 0.74
    else:
        quality = "fallback"
        confidence = 0.68

    return RoadmapOut(
        id=model.id,
        user_profile_id=model.user_profile_id,
        target_job_id=model.target_job_id,
        title=model.title,
        summary=model.summary,
        status=model.status,
        steps=steps,
        gap_analysis=gap,
        generation_mode=model.generation_mode,
        generation_notes=model.generation_notes,
        ai_quality_indicator=quality,
        confidence_score=confidence,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


@router.get("", response_model=list[RoadmapSummary])
def list_roadmaps(user_profile_id: int, db: Session = Depends(get_db)):
    roadmaps = (
        db.query(Roadmap)
        .filter(Roadmap.user_profile_id == user_profile_id)
        .order_by(Roadmap.created_at.desc())
        .all()
    )
    
    summaries = []
    for r in roadmaps:
        steps = json.loads(r.steps_json)
        total_steps = len(steps)
        completed_steps = sum(1 for s in steps if s.get("completed", False))
        
        # Get job details
        job = db.get(JobDescription, r.target_job_id) if r.target_job_id else None
        
        # Compute quality indicator
        gap = json.loads(r.gap_analysis_json)
        match_score = gap.get("match_score", 0)
        ai_quality = None
        if r.generation_mode == "ai":
            ai_quality = "high" if match_score > 0.7 else "medium"
        elif r.generation_mode == "fallback":
            ai_quality = "fallback"
        
        summaries.append(
            RoadmapSummary(
                id=r.id,
                title=r.title,
                target_job_title=job.title if job else "General",
                target_job_company=job.company if job else "",
                status=r.status,
                generation_mode=r.generation_mode,
                ai_quality_indicator=ai_quality,
                total_steps=total_steps,
                completed_steps=completed_steps,
                created_at=r.created_at,
            )
        )
    
    return summaries


@router.post("", response_model=RoadmapOut)
async def generate_roadmap(payload: RoadmapCreate, db: Session = Depends(get_db)):
    profile = db.get(UserProfile, payload.user_profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Profile not found"})

    profile_skills = json.loads(profile.skills_current_json)
    stored_preferences = json.loads(profile.learning_preferences_json)
    effective_audience_mode = payload.audience_mode
    if not effective_audience_mode:
        for item in stored_preferences:
            if isinstance(item, str) and item.startswith("audience:"):
                effective_audience_mode = item.split(":", maxsplit=1)[1]
                break

    job = db.get(JobDescription, payload.target_job_id) if payload.target_job_id else None
    if not job:
        targeted_candidates = db.query(JobDescription).filter(JobDescription.title.ilike(f"%{profile.target_role}%")).all()
        candidates = targeted_candidates or db.query(JobDescription).all()

        ranked = sorted(
            candidates,
            key=lambda candidate: score_job_fit(
                user_skills=profile_skills,
                required_skills=json.loads(candidate.required_skills_json),
                preferred_skills=json.loads(candidate.preferred_skills_json),
                target_role=profile.target_role,
                job_title=candidate.title,
                years_experience=profile.years_experience,
                experience_level=candidate.experience_level,
            ),
            reverse=True,
        )
        job = ranked[0] if ranked else None

    if not job:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "No matching job found"})

    courses_db = db.query(CourseResource).limit(200).all()
    courses = [
        {
            "id": c.id,
            "title": c.title,
            "provider": c.provider,
            "skills_covered": json.loads(c.skills_covered_json),
            "duration_hours": c.duration_hours,
            "cost_amount": c.cost_amount,
            "cost_currency": c.cost_currency,
            "url": c.url,
            "is_certificate": bool(c.is_certificate),
        }
        for c in courses_db
    ]

    required = json.loads(job.required_skills_json)
    preferred = json.loads(job.preferred_skills_json)
    gap = calculate_gap(profile_skills, required, preferred)

    generation_mode = "fallback"
    generation_notes = ""
    if settings.use_static_mvp:
        summary, steps, generation_notes = build_mvp_static_roadmap()
        generation_mode = "ai"
    else:
        try:
            summary, steps, generation_notes = await generate_ai_roadmap(
                profile={
                    "id": profile.id,
                    "target_role": profile.target_role,
                    "skills_current": profile_skills,
                    "weekly_hours_available": profile.weekly_hours_available,
                    "budget_limit": profile.budget_limit,
                },
                job={
                    "id": job.id,
                    "title": job.title,
                    "required_skills": required,
                    "preferred_skills": preferred,
                },
                courses=courses,
                gap=gap,
                audience_mode=effective_audience_mode,
            )
            generation_mode = "ai"
        except AIServiceError as exc:
            summary, steps, _ = build_fallback_roadmap(gap=gap, courses=courses, audience_mode=effective_audience_mode)
            generation_notes = "AI temporarily unavailable. A fallback roadmap was generated."

    roadmap = Roadmap(
        user_profile_id=profile.id,
        target_job_id=job.id,
        title=f"{profile.target_role} Readiness Plan",
        summary=summary,
        status="draft",
        steps_json=json.dumps(steps),
        gap_analysis_json=json.dumps(gap),
        generation_mode=generation_mode,
        generation_notes=generation_notes,
    )
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    return to_out(roadmap)


@router.get("/{roadmap_id}", response_model=RoadmapOut)
def get_roadmap(roadmap_id: int, db: Session = Depends(get_db)):
    roadmap = db.get(Roadmap, roadmap_id)
    if not roadmap:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Roadmap not found"})
    return to_out(roadmap)


@router.put("/{roadmap_id}/steps", response_model=RoadmapOut)
def update_roadmap_steps(roadmap_id: int, payload: RoadmapStepsUpdate, db: Session = Depends(get_db)):
    roadmap = db.get(Roadmap, roadmap_id)
    if not roadmap:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Roadmap not found"})

    roadmap.steps_json = json.dumps([step.model_dump() for step in payload.steps])
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    return to_out(roadmap)


@router.put("/{roadmap_id}/status", response_model=RoadmapOut)
def update_roadmap_status(roadmap_id: int, status: str, db: Session = Depends(get_db)):
    if status not in {"draft", "active", "completed"}:
        raise HTTPException(status_code=400, detail={"code": "VALIDATION", "message": "Invalid status"})
    roadmap = db.get(Roadmap, roadmap_id)
    if not roadmap:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Roadmap not found"})
    roadmap.status = status
    db.add(roadmap)
    db.commit()
    db.refresh(roadmap)
    return to_out(roadmap)
