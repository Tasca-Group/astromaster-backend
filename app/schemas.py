"""AstroMaster Backend — Pydantic Request/Response Schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


# ─── Gratis-Check ───

class GratisCheckRequest(BaseModel):
    geburtsdatum: str  # DD.MM.YYYY

    @field_validator("geburtsdatum")
    @classmethod
    def validate_datum(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) != 3 or len(parts[0]) != 2 or len(parts[1]) != 2 or len(parts[2]) != 4:
            raise ValueError("Format muss DD.MM.YYYY sein")
        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        if not (1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2030):
            raise ValueError("Ungültiges Datum")
        return v


class GratisCheckResponse(BaseModel):
    tropisch: str
    siderisch: str
    abweichung: bool
    ophiuchus: bool


# ─── Bestellung ───

class BestellungRequest(BaseModel):
    name: str
    email: str
    geburtsdatum: str  # DD.MM.YYYY
    geburtszeit: str  # HH:MM
    geburtsort: str
    version: str = "normal"
    stripe_session_id: str | None = None

    @field_validator("geburtsdatum")
    @classmethod
    def validate_datum(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) != 3 or len(parts[0]) != 2 or len(parts[1]) != 2 or len(parts[2]) != 4:
            raise ValueError("Format muss DD.MM.YYYY sein")
        return v

    @field_validator("geburtszeit")
    @classmethod
    def validate_zeit(cls, v: str) -> str:
        parts = v.split(":")
        if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
            raise ValueError("Format muss HH:MM sein")
        h, m = int(parts[0]), int(parts[1])
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError("Ungültige Uhrzeit")
        return v

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        if v not in ("normal", "pro"):
            raise ValueError("Version muss 'normal' oder 'pro' sein")
        return v


class BestellungStatusResponse(BaseModel):
    id: uuid.UUID
    status: str
    pdf_bereit: bool
    erstellt_am: datetime

    model_config = {"from_attributes": True}


class BestellungCreateResponse(BaseModel):
    id: uuid.UUID
    status: str


# ─── Admin ───

class AdminBestellungResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    geburtsdatum: str
    geburtszeit: str
    geburtsort: str
    version: str
    status: str
    preis: float
    stripe_session_id: str | None
    stripe_payment_id: str | None
    pdf_pfad: str | None
    email_gesendet: bool
    fehler_nachricht: str | None
    erstellt_am: datetime
    aktualisiert_am: datetime

    model_config = {"from_attributes": True}


class StatistikResponse(BaseModel):
    monat: str
    anzahl: int
    umsatz: float


# ─── Health ───

class HealthResponse(BaseModel):
    status: str
    version: str
    db_connected: bool
