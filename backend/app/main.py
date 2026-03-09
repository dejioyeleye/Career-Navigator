from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from .config import settings
from .db import Base, SessionLocal, engine
from .routers import interviews, mentor, profiles, roadmaps, search
from .seed_data import load_seed_data

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"])

app = FastAPI(
    title="Skill-Bridge Career Navigator API",
    version="0.1.0",
    docs_url="/api/docs" if settings.app_env == "dev" else None,  # Hide docs in production
    redoc_url="/api/redoc" if settings.app_env == "dev" else None,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS with dynamic origins from config
allowed_origins = [origin.strip() for origin in settings.allowed_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Explicit methods only
    allow_headers=["Content-Type", "Authorization"],  # Explicit headers only
    max_age=600,  # Cache preflight requests for 10 minutes
)

app.include_router(profiles.router)
app.include_router(roadmaps.router)
app.include_router(search.router)
app.include_router(interviews.router)
app.include_router(mentor.router)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_dir = Path(__file__).resolve().parents[1] / "seed"
        load_seed_data(db, seed_dir)
    finally:
        db.close()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/security-check")
@limiter.limit("5/minute")
def security_check(request: Request) -> dict:
    """Check if API keys are configured (without exposing them)"""
    return {
        "gemini_configured": bool(settings.gemini_api_key and not settings.gemini_api_key.startswith("your_")),
        "openai_configured": bool(settings.openai_api_key),
        "rate_limit": f"{settings.rate_limit_per_minute}/minute",
        "allowed_origins": allowed_origins,
    }
