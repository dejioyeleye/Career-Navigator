from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Roadmap, UserProfile

router = APIRouter(prefix="/api/mentor", tags=["mentor"])


@router.get("/snapshot/{profile_id}")
def mentor_snapshot(profile_id: int, db: Session = Depends(get_db)):
    profile = db.get(UserProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Profile not found"})

    roadmaps = (
        db.query(Roadmap)
        .filter(Roadmap.user_profile_id == profile_id)
        .order_by(Roadmap.created_at.desc())
        .all()
    )

    return {
        "profile": {
            "id": profile.id,
            "full_name": profile.full_name,
            "current_role": profile.current_role,
            "target_role": profile.target_role,
        },
        "roadmaps": [
            {
                "id": r.id,
                "title": r.title,
                "status": r.status,
                "generation_mode": r.generation_mode,
                "created_at": r.created_at,
            }
            for r in roadmaps
        ],
        "share_note": "Mentor snapshot is synthetic and safe to share in assessment demos.",
    }
