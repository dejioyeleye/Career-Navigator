from __future__ import annotations

import csv
import json
from pathlib import Path

from sqlalchemy.orm import Session

from .models import CourseResource, JobDescription, UserProfile
from .services.taxonomy import canonicalize_skills


def _split_pipe(value: str) -> list[str]:
    return [x.strip() for x in value.split("|") if x.strip()]


def _expand_jobs(base_jobs: list[dict], target_count: int = 120) -> list[dict]:
    if len(base_jobs) >= target_count:
        return base_jobs

    company_suffixes = ["Labs", "Systems", "Works", "Dynamics", "Cloud", "Data", "AI"]
    locations = ["Remote", "New York", "Chicago", "Austin", "Atlanta", "Seattle", "Denver"]
    remote_types = ["remote", "hybrid", "onsite"]
    levels = ["junior", "mid", "senior"]

    expanded = list(base_jobs)
    idx = 0
    while len(expanded) < target_count:
        base = base_jobs[idx % len(base_jobs)]
        title = base["title"]
        role_variants = [
            title,
            f"Associate {title}",
            f"{title} I",
            f"{title} II",
            f"Applied {title}",
        ]
        variant = role_variants[(idx // len(base_jobs)) % len(role_variants)]

        expanded.append(
            {
                **base,
                "title": variant,
                "company": f"{base['company'].split()[0]} {company_suffixes[idx % len(company_suffixes)]}",
                "location": locations[idx % len(locations)],
                "remote_type": remote_types[idx % len(remote_types)],
                "experience_level": levels[idx % len(levels)],
                "salary_min": int(base["salary_min"] or 70000) + ((idx % 8) * 1500),
                "salary_max": int(base["salary_max"] or 100000) + ((idx % 8) * 1800),
                "description": f"Synthetic listing variant #{idx + 1}: {base['description']}",
            }
        )
        idx += 1

    return expanded[:target_count]


def load_seed_data(db: Session, seed_dir: Path) -> None:
    if db.query(JobDescription).count() == 0:
        with (seed_dir / "jobs.csv").open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            base_jobs = list(reader)
            for row in _expand_jobs(base_jobs, target_count=120):
                db.add(
                    JobDescription(
                        title=row["title"],
                        company=row["company"],
                        location=row["location"],
                        remote_type=row["remote_type"],
                        experience_level=row["experience_level"],
                        salary_min=int(row["salary_min"]) if row["salary_min"] else None,
                        salary_max=int(row["salary_max"]) if row["salary_max"] else None,
                        currency=row.get("currency", "USD"),
                        required_skills_json=json.dumps(canonicalize_skills(_split_pipe(row["required_skills"]))),
                        preferred_skills_json=json.dumps(canonicalize_skills(_split_pipe(row["preferred_skills"]))),
                        description=row["description"],
                    )
                )

    if db.query(CourseResource).count() == 0:
        with (seed_dir / "courses.csv").open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                db.add(
                    CourseResource(
                        title=row["title"],
                        provider=row["provider"],
                        difficulty=row["difficulty"],
                        duration_hours=float(row["duration_hours"]),
                        cost_amount=float(row["cost_amount"]),
                        cost_currency=row.get("cost_currency", "USD"),
                        format=row["format"],
                        url=row["url"],
                        rating=float(row["rating"]),
                        is_certificate=1 if row.get("is_certificate", "false").lower() == "true" else 0,
                        skills_covered_json=json.dumps(canonicalize_skills(_split_pipe(row["skills_covered"]))),
                    )
                )

    if db.query(UserProfile).count() == 0:
        with (seed_dir / "profiles.json").open("r", encoding="utf-8") as f:
            profiles = json.load(f)
            for p in profiles:
                db.add(
                    UserProfile(
                        full_name=p["full_name"],
                        email=p["email"],
                        current_role=p["current_role"],
                        target_role=p["target_role"],
                        years_experience=float(p["years_experience"]),
                        location=p["location"],
                        skills_current_json=json.dumps(canonicalize_skills(p["skills_current"])),
                        skills_target_json=json.dumps(canonicalize_skills(p.get("skills_target", []))),
                        learning_preferences_json=json.dumps(p.get("learning_preferences", [])),
                        weekly_hours_available=int(p["weekly_hours_available"]),
                        budget_limit=float(p["budget_limit"]),
                    )
                )

    db.commit()
