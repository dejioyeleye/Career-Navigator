from __future__ import annotations

CANONICAL_SKILL_ALIASES: dict[str, str] = {
    "py": "python",
    "python3": "python",
    "postgres": "sql",
    "postgresql": "sql",
    "mysql": "sql",
    "k8s": "kubernetes",
    "container orchestration": "kubernetes",
    "aws cloud": "aws",
    "amazon web services": "aws",
    "iac": "terraform",
    "infra as code": "terraform",
    "restful api": "rest",
    "rest api": "rest",
    "machine-learning": "machine learning",
    "ml": "machine learning",
    "ci/cd": "ci cd",
    "ci-cd": "ci cd",
    "github actions": "ci cd",
    "data viz": "data visualization",
    "storytelling": "communication",
}


def canonicalize_skill(skill: str) -> str:
    normalized = " ".join(skill.lower().replace("/", " ").replace("-", " ").strip().split())
    return CANONICAL_SKILL_ALIASES.get(normalized, normalized)


def canonicalize_skills(skills: list[str]) -> list[str]:
    return sorted({canonicalize_skill(skill) for skill in skills if skill and skill.strip()})


def extract_transferable_skills(current_skills: list[str], target_required: list[str]) -> list[str]:
    current = set(canonicalize_skills(current_skills))
    target = set(canonicalize_skills(target_required))

    soft = {"communication", "collaboration", "problem solving", "testing", "git", "sql", "python"}
    transferable = sorted([skill for skill in current if skill in target or skill in soft])
    return transferable
