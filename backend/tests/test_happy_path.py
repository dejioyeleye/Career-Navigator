from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app


def test_create_profile_and_generate_roadmap_happy_path():
    with TestClient(app) as client:
        payload = {
            "full_name": "Test User",
            "email": f"test.user.{uuid4().hex[:8]}@skillbridge.example.com",
            "current_role": "Support Engineer",
            "target_role": "Cloud Engineer",
            "years_experience": 1,
            "location": "Remote",
            "skills_current": ["Python", "Linux"],
            "skills_target": ["AWS", "Terraform"],
            "learning_preferences": ["self-paced"],
            "weekly_hours_available": 7,
            "budget_limit": 120,
        }

        profile_resp = client.post("/api/profiles", json=payload)
        assert profile_resp.status_code == 200
        profile_id = profile_resp.json()["id"]

        roadmap_resp = client.post("/api/roadmaps", json={"user_profile_id": profile_id})
        assert roadmap_resp.status_code == 200
        data = roadmap_resp.json()
        assert len(data["steps"]) > 0
        assert data["status"] == "draft"

        scorecard_resp = client.get(f"/api/profiles/{profile_id}/scorecard")
        assert scorecard_resp.status_code == 200
        scorecard = scorecard_resp.json()
        assert 0 <= scorecard["profile_completeness_score"] <= 100
        assert 0 <= scorecard["market_competitiveness_score"] <= 100
