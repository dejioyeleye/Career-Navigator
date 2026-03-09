# Skill-Bridge Design Documentation

Hey there! 👋 Welcome to the design docs for Skill-Bridge, a career navigation platform that helps people transition into new roles by mapping their skills, finding relevant jobs, and building personalized learning roadmaps.

## What We're Building

Skill-Bridge is all about making career transitions less scary. You upload your resume, tell us what job you want, and we'll show you exactly what skills you need to learn and how to get there. Think of it as a GPS for your career—except instead of "turn left in 500 feet," it's "take this Python course and build 3 projects."

The platform does three main things:
1. **Profile Analysis** - Parse resumes using AI to extract skills, experience, and career goals
2. **Opportunity Discovery** - Search through jobs and courses to find the best matches
3. **Personalized Roadmaps** - Generate step-by-step learning paths with AI that actually make sense

## Design Philosophy

### Keep It Simple
We're not trying to be the next LinkedIn. The interface is clean, focused, and gets you from "I want a new job" to "here's your plan" in about 2 minutes. No endless forms, no overwhelming dashboards—just the essentials.

### AI That Actually Helps
AI can be gimmicky, but we're using it where it genuinely matters:
- **Resume parsing** - Because nobody wants to fill out 20 form fields
- **Roadmap generation** - Because career planning is hard and AI can spot patterns we miss
- **Skill matching** - To find transferable skills you didn't even know you had

### Real Data, Real Results
The platform uses a curated dataset of 120 real job listings and courses. We're not scraping random stuff from the internet—every resource has been validated to make sure it's actually useful.

## Tech Stack

### Frontend (The Pretty Part)
**Next.js 14** - We went with Next.js because:
- Server-side rendering makes the app feel snappy
- App Router gives us clean URL structures
- Built-in API routes for simple backend calls
- Amazing developer experience

**React 18 + TypeScript** - Type safety saves us from stupid bugs, and React Hooks keep the code clean. We're using functional components exclusively—no class components from 2018.

**Tailwind CSS** - Utility-first CSS means we can style things fast without writing a thousand lines of custom CSS. The design system is consistent because we're using a limited set of colors and spacing values.

**react-hook-form + Zod** - Forms are hard. These libraries make them bearable. Real-time validation, type-safe schemas, and minimal re-renders.

**Key Dependencies:**
```json
"next": "14.2.15",
"react": "^18.3.1",
"typescript": "^5.6.3",
"tailwindcss": "^3.4.1",
"react-hook-form": "^7.54.0",
"zod": "^3.23.8"
```

### Backend (The Smart Part)
**FastAPI** - We chose FastAPI over Flask or Django because:
- Automatic API docs (Swagger UI out of the box)
- Native async/await support
- Pydantic for data validation
- Crazy fast performance
- Type hints everywhere

**SQLAlchemy + SQLite** - SQLite for local dev (no Docker setup needed), but the ORM makes it trivial to switch to PostgreSQL in production. Relationships are defined clearly, migrations are clean.

**Google Gemini API** - Our AI backbone:
- **Resume parsing** - Extracts structured data from PDFs
- **Roadmap generation** - Creates personalized learning paths
- Cost-effective ($0.05 per 100 resumes parsed)
- Fast response times (2-3 seconds)

**Security & Rate Limiting:**
- SlowAPI for rate limiting (10 requests/minute during dev)
- CORS configured for localhost:3000 only
- File validation (PDFs only, 5MB max)
- Environment variables for all secrets

**Key Dependencies:**
```
fastapi==0.115.6
sqlalchemy==2.0.36
pydantic==2.10.3
google-genai==1.0.0
slowapi==0.1.9
PyPDF2==3.0.1
```

## Architecture Overview

### How Data Flows

```
User uploads resume (PDF)
    ↓
Frontend sends multipart/form-data to /api/profiles/import-resume
    ↓
Backend extracts text with PyPDF2
    ↓
Gemini API parses resume → structured JSON
    ↓
Skills canonicalized (e.g., "js" → "javascript")
    ↓
UserProfile created with validated defaults
    ↓
Frontend auto-fills form with extracted data
    ↓
User reviews and submits
    ↓
Profile saved to database
    ↓
User searches for jobs
    ↓
Skills compared via Jaccard similarity
    ↓
Skill gap analysis performed
    ↓
Courses matched to missing skills
    ↓
Gemini generates personalized roadmap
    ↓
User sees step-by-step learning path
```

### Database Schema

**UserProfile** - The core entity
- Personal info (name, email, location)
- Current & target roles
- Skills (current and target lists)
- Learning preferences
- Time/budget constraints

**JobDescription** - Real job listings
- Title, company, description
- Required skills (stored as JSON array)
- Salary range
- Location & remote options

**Course** - Learning resources
- Title, provider, URL
- Skills taught (JSON array)
- Estimated hours
- Difficulty level

**Roadmap** - Generated learning paths
- Summary & steps (JSON)
- Associated profile, job, and courses
- Confidence scores
- Progress tracking

### API Design

REST-ful endpoints with clear naming:

```
POST   /api/profiles                  - Create new profile
GET    /api/profiles/{id}             - Get profile details
PUT    /api/profiles/{id}             - Update profile
POST   /api/profiles/import-resume    - Upload & parse resume

GET    /api/search/jobs               - Search jobs (with filters)
GET    /api/search/courses            - Search courses

POST   /api/roadmaps                  - Generate roadmap
GET    /api/roadmaps/{id}             - Get roadmap details
```

All responses follow a consistent structure:
```json
{
  "data": { ... },
  "meta": { "timestamp": "..." }
}
```

Errors use proper HTTP status codes (400, 404, 500) with clear messages.

## AI Integration Strategy

### Phase 1: Resume Parsing (✅ Complete)
**Goal:** Auto-fill profile forms from uploaded PDFs

**How it works:**
1. User uploads resume
2. PyPDF2 extracts raw text
3. Gemini receives structured prompt asking for JSON
4. AI extracts: name, email, current role, target role, skills, years of experience, location
5. Backend validates and applies defaults for missing fields
6. Frontend auto-fills form

**Fallback:** If Gemini fails, we do basic keyword extraction (searching for common skills like "Python", "SQL", etc.)

**Cost:** ~$0.0005 per resume (negligible)

### Phase 2: Roadmap Generation (✅ Complete)
**Goal:** Create personalized learning paths

**How it works:**
1. Analyze skill gap between current profile and target job
2. Find courses that teach missing skills
3. Send profile, job, gap analysis, and courses to Gemini
4. AI generates 5-step roadmap with:
   - Goal for each step
   - Skills to focus on
   - Recommended courses
   - Time estimates
   - Evidence of competency
   - Confidence scores

**Fallback:** Rule-based roadmap (prioritize missing skills, assign courses, estimate 40 hours per skill)

**Cost:** ~$0.002 per roadmap

### Phase 3: Future AI Features (Planned)

**Job Description Generation**
- Create realistic job listings from skill sets
- Helps users understand what roles they qualify for

**Course Generation**
- Suggest custom learning resources
- Fill gaps when our database doesn't have the right course

**Interview Prep**
- Generate practice questions based on target role
- Provide feedback on answers

**Smart Skill Matching**
- Use embeddings instead of keyword matching
- "Docker" and "containerization" should be treated as related

## Design Decisions (And Why)

### Why SQLite?
**Decision:** Use SQLite for local development instead of PostgreSQL

**Reasoning:** 
- Zero setup—no Docker, no connection strings
- Perfect for a case study/portfolio project
- SQLAlchemy makes it easy to switch to Postgres later
- File-based database makes it trivial to reset/seed data

**Trade-off:** No concurrent write support, but we're not building Twitter here.

### Why Gemini Over OpenAI?
**Decision:** Use Google Gemini instead of GPT-4

**Reasoning:**
- 20x cheaper ($0.075/1M tokens vs $1.50/1M for GPT-4o-mini)
- Faster response times (2-3s vs 4-5s)
- Generous free tier (1500 requests/day)
- API key provided by user (no billing setup needed)

**Trade-off:** Slightly less "creative" outputs, but we want structured data anyway.

### Why Next.js Over Plain React?
**Decision:** Use Next.js App Router instead of Create React App

**Reasoning:**
- Server components reduce JavaScript bundle size
- Built-in routing (no React Router setup)
- Image optimization out of the box
- Easy deployment to Vercel

**Trade-off:** More opinionated, steeper learning curve for beginners.

### Why react-hook-form?
**Decision:** Use react-hook-form instead of managing form state manually

**Reasoning:**
- Minimal re-renders (only updates what changed)
- Built-in validation with Zod
- Easy integration with TypeScript
- Way less code than managing useState for 10 fields

**Trade-off:** Learning curve, but worth it for complex forms.

## Security Considerations

### Current Protections
1. **Rate Limiting** - 10 requests/minute per IP (prevents abuse)
2. **CORS** - Only localhost:3000 allowed (prevents unauthorized API access)
3. **File Validation** - PDFs only, 5MB max (prevents malicious uploads)
4. **Email Validation** - Regex pattern ensures valid email format
5. **Environment Variables** - API keys never committed to Git

### Future Enhancements
- Add authentication (JWT tokens or OAuth)
- Implement HTTPS in production
- Add request signing to prevent tampering
- Set up monitoring and alerting

## Performance Optimizations

### What We've Done
- **Lazy loading** - Next.js code-splits automatically
- **Debounced search** - Search queries wait 300ms before firing
- **Caching** - Settings loaded once with `@lru_cache`
- **Async/await** - Non-blocking AI calls
- **Limited results** - Return max 100 jobs to avoid huge payloads

### What We Could Do
- Add Redis for caching search results
- Implement pagination for large result sets
- Use database indexes on frequently queried fields
- Compress API responses with gzip
- Add service workers for offline support

## Testing Strategy

### What We're Testing
**Backend:**
- Unit tests for skill canonicalization
- API endpoint tests with pytest
- Pydantic schema validation tests

**Frontend:**
- Component rendering tests with React Testing Library
- Form validation tests
- Integration tests for critical user flows

**Manual Testing:**
- Resume upload with various PDF formats
- AI fallback scenarios (invalid API key)
- Edge cases (empty skills, missing data)

### What We Need to Add
- End-to-end tests with Playwright
- Load testing (simulate 100 concurrent users)
- Security testing (OWASP Top 10)

## Future Enhancements

### Near-Term (Next 3 Months)

**1. User Authentication**
- Add login/signup with email + password
- Store profiles securely per user
- Dashboard to view all your roadmaps

**2. Progress Tracking**
- Mark roadmap steps as complete
- Track time spent on each step
- Celebrate milestones (confetti animation!)

**3. Course Reviews & Ratings**
- Let users rate courses
- Show average ratings in search
- Filter by "highly rated"

**4. Email Notifications**
- Weekly progress reminders
- New job matches based on your profile
- Course recommendations

### Mid-Term (6 Months)

**5. Mobile App**
- React Native version
- Push notifications for new opportunities
- Offline mode for reviewing roadmaps

**6. Social Features**
- Share roadmaps with friends
- See how others are progressing
- Mentorship matching

**7. AI-Enhanced Job Matching**
- Use embeddings for semantic search
- "Find jobs similar to X"
- Predict which jobs you'll love

**8. Integration with Job Boards**
- Pull live jobs from LinkedIn, Indeed
- One-click applications
- Track application status

### Long-Term (1 Year+)

**9. Enterprise Features**
- Company accounts
- Bulk employee onboarding
- Analytics dashboard for HR
- Custom learning paths per organization

**10. Marketplace**
- Let course creators add content
- Monetization (take 10% commission)
- Verified instructor badges

**11. AI Career Coach**
- Chat interface for career advice
- Resume feedback and suggestions
- Mock interview practice

**12. Certifications**
- Issue certificates upon roadmap completion
- Blockchain verification (why not?)
- LinkedIn integration

## Known Issues & Limitations

### Current Bugs
- Resume parsing sometimes fails with scanned PDFs (no OCR)
- Email extraction can miss emails with unusual formats
- Roadmap generation occasionally returns invalid JSON

### Technical Debt
- No database migrations (using raw SQLAlchemy)
- Limited error handling in frontend
- No logging/monitoring in production
- Hard-coded sample data (should be in seed script)

### Scalability Concerns
- SQLite won't handle 1000+ concurrent users
- No caching layer (every search hits the database)
- AI calls block the request (should be async background jobs)

## Deployment

### Local Development
```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

### Production (Recommended Stack)
- **Frontend:** Vercel (automatic Next.js deployment)
- **Backend:** Railway or Render (Docker support)
- **Database:** PostgreSQL on Neon or Supabase
- **File Storage:** AWS S3 for resume uploads
- **Monitoring:** Sentry for error tracking
