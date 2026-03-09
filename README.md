# Career-Navigator
Candidate Name: Deji Oyeleye

Scenario Chosen: Career Navigation Platform

Estimated Time Spent: 6 hours

Quick Start:

Prerequisites:
● Python 3.10+ with pip
● Node.js 18+ with npm
● Git

Run Commands:
● Backend
  - cd backend
  - python -m venv .venv
  - .venv\Scripts\activate
  - pip install -r requirements.txt
  - uvicorn app.main:app --reload --port 8000

● Frontend
  - cd frontend
  - npm install
  - npm run dev

Test Commands:
● Backend tests: cd backend, then pytest -q
● Frontend tests: cd frontend, then npm run test

AI Disclosure:
● Did you use an AI assistant (Copilot, ChatGPT, etc.)? Yes
● How did you verify the suggestions?
  - Manual testing in browser and API responses
  - Error checks after each change
  - Code review for logic and security
  - Cross-check with FastAPI, Next.js, and Gemini docs
  - Type checking with TypeScript and Pydantic
● Give one example of a suggestion you rejected or changed:
  - Replaced OpenAI GPT suggestion with Gemini due to lower cost, faster responses, and simpler integration

Tradeoffs & Prioritization:
● What did you cut to stay within the 4–6 hour limit?
  - Authentication and account system
  - Migration tooling setup
  - Full automated test coverage
  - Advanced UI polish and animation
  - Full progress persistence wiring in UI

● What would you build next if you had more time?
  - Authentication and multi-profile dashboard
  - Progress analytics and milestones
  - Email notifications
  - Social and mentor tools
  - Mobile app support
  - Semantic AI matching and interview coach

● Known limitations:
  - SQLite is not ideal for large concurrent traffic
  - Scanned PDF OCR is not supported yet
  - AI provider limits can affect availability
  - No caching layer yet
  - Some edge-case error recovery paths can be improved

API overview:
Profile Management
● POST /api/profiles
● GET /api/profiles/{id}
● PUT /api/profiles/{id}
● GET /api/profiles/{id}/scorecard
● POST /api/profiles/import
● GET /api/profiles/{id}/transferable-skills
● GET /api/profiles/{id}/analytics

Roadmap Management
● POST /api/roadmaps
● GET /api/roadmaps?user_profile_id={id}
● GET /api/roadmaps/{id}
● PUT /api/roadmaps/{id}/steps
● PUT /api/roadmaps/{id}/status?status=active|draft|completed

Search and Discovery
● GET /api/search/jobs
● GET /api/search/courses

Interview Prep
● POST /api/interviews/questions

Mentor Tools
● GET /api/mentor/snapshot/{profile_id}

Notes:
● AI roadmap generation now tries multiple Gemini model names automatically, including gemini-flash-latest.
● If AI fails, deterministic fallback roadmap generation still works.
