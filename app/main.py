"""AstroMaster Backend — FastAPI Application."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import Base, engine
from app.dependencies import limiter
from app.routers import admin, bestellung, gratis_check, health, stripe_webhook

# Logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# App
app = FastAPI(
    title="AstroMasters API",
    description="Kosmische Analyse-API — Siderische Astrologie, Numerologie, Human Design",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# Router
app.include_router(health.router)
app.include_router(gratis_check.router)
app.include_router(bestellung.router)
app.include_router(stripe_webhook.router)
app.include_router(admin.router)


@app.on_event("startup")
def on_startup():
    """Erstellt DB-Tabellen beim Start (falls nicht vorhanden)."""
    Base.metadata.create_all(bind=engine)
