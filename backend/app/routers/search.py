from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import CourseResource, JobDescription
from ..schemas import CourseOut, JobOut
from ..services.taxonomy import canonicalize_skill


router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/jobs", response_model=list[JobOut])
def search_jobs(
    query: str | None = None,
    skill: str | None = None,
    remote_type: str | None = None,
    experience_level: str | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(JobDescription)
    if query:
        q = q.filter(JobDescription.title.ilike(f"%{query}%"))
    if remote_type:
        q = q.filter(JobDescription.remote_type == remote_type)
    if experience_level:
        q = q.filter(JobDescription.experience_level == experience_level)

    rows = q.all()
    out: list[JobOut] = []
    requested_skill = canonicalize_skill(skill) if skill else None
    for row in rows:
        required = json.loads(row.required_skills_json)
        if requested_skill and requested_skill not in {canonicalize_skill(s) for s in required}:
            continue
        out.append(
            JobOut(
                id=row.id,
                title=row.title,
                company=row.company,
                location=row.location,
                remote_type=row.remote_type,
                experience_level=row.experience_level,
                salary_min=row.salary_min,
                salary_max=row.salary_max,
                currency=row.currency,
                required_skills=required,
                preferred_skills=json.loads(row.preferred_skills_json),
                description=row.description,
            )
        )
    return out[:100]


@router.get("/courses", response_model=list[CourseOut])
def search_courses(
    skill: str | None = None,
    difficulty: str | None = None,
    max_cost: float | None = Query(default=None, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(CourseResource)
    if difficulty:
        q = q.filter(CourseResource.difficulty == difficulty)
    if max_cost is not None:
        q = q.filter(CourseResource.cost_amount <= max_cost)

    rows = q.limit(150).all()
    out: list[CourseOut] = []
    requested_skill = canonicalize_skill(skill) if skill else None
    for row in rows:
        skills = json.loads(row.skills_covered_json)
        if requested_skill and requested_skill not in {canonicalize_skill(s) for s in skills}:
            continue
        out.append(
            CourseOut(
                id=row.id,
                title=row.title,
                provider=row.provider,
                difficulty=row.difficulty,
                duration_hours=row.duration_hours,
                cost_amount=row.cost_amount,
                cost_currency=row.cost_currency,
                format=row.format,
                url=row.url,
                rating=row.rating,
                is_certificate=bool(row.is_certificate),
                skills_covered=skills,
            )
        )
    return out
