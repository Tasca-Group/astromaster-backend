"""AstroMaster Backend — Konfiguration via Umgebungsvariablen."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/astromaster"

    # Security
    ADMIN_API_KEY: str = "change-me-in-production"

    # Stripe
    STRIPE_WEBHOOK_SECRET: str = ""

    # Brevo (Email)
    BREVO_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: list[str] = [
        "https://astro-masters.com",
        "https://www.astro-masters.com",
    ]

    # PDF Output
    PDF_OUTPUT_DIR: str = "./output"

    # App
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
