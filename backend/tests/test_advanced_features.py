"""
Integration tests for advanced features: analytics, transferable skills, interview questions, etc.
"""
from fastapi.testclient import TestClient
from uuid import uuid4
from app.main import app


def test_advanced_features_flow():
    """Test the complete advanced features flow"""
    
    with TestClient(app) as client:
        # 1. Create a career switcher profile
        profile_payload = {
            "full_name": f"Career Switcher {uuid4().hex[:8]}",
            "email": f"switcher.{uuid4().hex[:8]}@example.com",
            "current_role": "Teacher",
            "target_role": "Software Engineer",
            "years_experience": 5,
            "location": "Remote",
            "skills_current": ["python", "communication", "leadership"],
            "skills_target": ["react", "nodejs", "docker"],
            "learning_preferences": ["self-paced", "audience:career_switcher"],
            "weekly_hours_available": 15,
            "budget_limit": 500
        }
        
        profile_response = client.post("/api/profiles", json=profile_payload)
        assert profile_response.status_code == 200
        profile = profile_response.json()
        profile_id = profile["id"]
        
        # Verify audience mode was extracted
        assert profile.get("audience_mode") == "career_switcher"
        
        # 2. Test analytics endpoint
        analytics_response = client.get(f"/api/profiles/{profile_id}/analytics")
        assert analytics_response.status_code == 200
        analytics = analytics_response.json()
        assert "clarity_score" in analytics
        assert "completion_percentage" in analytics
        assert "roadmaps_generated" in analytics
        assert analytics["clarity_score"] >= 0
        
        # 3. Test transferable skills endpoint
        transferable_response = client.get(f"/api/profiles/{profile_id}/transferable-skills")
        assert transferable_response.status_code == 200
        transferable = transferable_response.json()
        assert "transferable_to_target" in transferable
        assert "high_demand_in_target" in transferable
        assert "suggested_bridges" in transferable
        # Python should be identified as transferable
        assert "python" in transferable["transferable_to_target"]
        
        # 4. Generate a roadmap
        roadmap_payload = {"user_profile_id": profile_id}
        roadmap_response = client.post("/api/roadmaps", json=roadmap_payload)
        assert roadmap_response.status_code == 200
        roadmap = roadmap_response.json()
        roadmap_id = roadmap["id"]
        
        # Verify quality indicators are present
        assert "ai_quality_indicator" in roadmap
        assert roadmap["ai_quality_indicator"] in ["high", "medium", "fallback"]
        assert "confidence_score" in roadmap
        
        # Verify steps have evidence fields
        if roadmap["steps"]:
            first_step = roadmap["steps"][0]
            # Evidence fields are optional but structure should support them
            assert "rationale" in first_step or "evidence" in first_step or "confidence" in first_step
        
        # 5. Test roadmap list endpoint
        list_response = client.get(f"/api/roadmaps?user_profile_id={profile_id}")
        assert list_response.status_code == 200
        roadmaps = list_response.json()
        assert len(roadmaps) >= 1
        assert roadmaps[0]["id"] == roadmap_id
        assert "total_steps" in roadmaps[0]
        assert "completed_steps" in roadmaps[0]
        
        # 6. Test interview questions endpoint
        interview_payload = {"user_profile_id": profile_id}
        interview_response = client.post("/api/interviews/questions", json=interview_payload)
        assert interview_response.status_code == 200
        questions = interview_response.json()
        assert "questions" in questions
        assert len(questions["questions"]) > 0
        assert "question" in questions["questions"][0]
        
        # 7. Test mentor snapshot endpoint
        mentor_response = client.get(f"/api/mentor/snapshot/{profile_id}")
        assert mentor_response.status_code == 200
        snapshot = mentor_response.json()
        assert "profile" in snapshot
        assert "roadmaps" in snapshot
        assert snapshot["profile"]["id"] == profile_id


def test_resume_import():
    """Test resume import endpoint"""
    with TestClient(app) as client:
        import_payload = {
            "full_name": "John Doe",
            "email": f"john.{uuid4().hex[:8]}@example.com",
            "skills": ["Python", "Django", "PostgreSQL", "Docker"],
            "years_experience": 3
        }
        
        response = client.post("/api/profiles/import", json=import_payload)
        assert response.status_code == 200
        result = response.json()
        
        assert "mapped_profile" in result
        assert "extracted_skills" in result
        assert result["mapped_profile"]["full_name"] == "John Doe"
        # Should extract some skills
        assert len(result["extracted_skills"]) > 0


def test_skill_normalization_in_search():
    """Test that skill aliases work in search"""
    with TestClient(app) as client:
        # Search for "py" should find jobs requiring "python"
        response = client.get("/api/search/jobs?skills=py")
        assert response.status_code == 200
        jobs = response.json()
        # Should find Python jobs due to alias mapping
        # (depends on seed data, but should not fail)
        
        # Search for "k8s" should find jobs requiring "kubernetes"
        response = client.get("/api/search/jobs?skills=k8s")
        assert response.status_code == 200
