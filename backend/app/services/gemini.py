"""Gemini AI service for intelligent content generation"""
import json
import logging
from typing import Any

from google import genai
from google.genai import types

from ..config import settings

logger = logging.getLogger(__name__)

# Configure Gemini client
if settings.gemini_api_key:
    client = genai.Client(api_key=settings.gemini_api_key)
else:
    client = None


class GeminiService:
    """Service for interacting with Google Gemini API"""
    
    def __init__(self):
        self.model_name = settings.gemini_model
        self.timeout = settings.gemini_timeout
        self.client = client
        
    async def parse_resume(self, resume_text: str) -> dict[str, Any]:
        """
        Parse resume text and extract structured profile data.
        
        Args:
            resume_text: Full text extracted from PDF
            
        Returns:
            Dict with profile fields and extracted skills
        """
        if not self.client:
            raise ValueError("Gemini client not configured")
            
        prompt = f"""Extract structured profile data from this resume text:

{resume_text}

Return ONLY valid JSON with this exact structure (no markdown, no explanations):
{{
  "full_name": "string or null",
  "email": "string or null",
  "phone": "string or null",
  "current_role": "string or null",
  "target_role": "string (infer logical next step) or null",
  "location": "string (city/state or Remote) or null",
  "years_experience": number (total years, calculate from dates) or null,
  "skills": ["skill1", "skill2", ...],
  "education": "string or null",
  "certifications": ["cert1", "cert2", ...]
}}

Rules:
- Extract email even if it has spaces or unusual formatting
- For years_experience, add up all work experience durations
- Infer target_role as a logical career progression from current experience
- Extract ALL technical skills, tools, frameworks, languages mentioned
- Use null for truly missing fields (not empty strings)
- Skills should be specific (e.g., "Python", "AWS", "React", not "programming")
- Return ONLY the JSON object, nothing else
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,  # Low temperature for consistent extraction
                    top_p=0.95,
                    max_output_tokens=1024,
                )
            )
            
            # Extract JSON from response
            text = response.text.strip()
            
            # Remove markdown code blocks if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            
            parsed = json.loads(text)
            logger.info("Successfully parsed resume with Gemini")
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Gemini returned invalid JSON: {e}")
            logger.error(f"Response text: {response.text if 'response' in locals() else 'N/A'}")
            raise ValueError("Failed to parse Gemini response as JSON")
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise


gemini_service = GeminiService()
