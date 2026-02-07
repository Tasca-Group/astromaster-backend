"""AstroMaster Backend — SQLAlchemy Models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Bestellung(Base):
    __tablename__ = "bestellungen"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    geburtsdatum: Mapped[str] = mapped_column(String(10), nullable=False)  # DD.MM.YYYY
    geburtszeit: Mapped[str] = mapped_column(String(5), nullable=False)  # HH:MM
    geburtsort: Mapped[str] = mapped_column(String(300), nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="normal")
    status: Mapped[str] = mapped_column(String(20), default="neu")
    preis: Mapped[float] = mapped_column(Float, default=39.0)

    # Stripe
    stripe_session_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    stripe_payment_id: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Berechnung
    berechnung_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    pdf_pfad: Mapped[str | None] = mapped_column(String(500), nullable=True)
    email_gesendet: Mapped[bool] = mapped_column(Boolean, default=False)
    fehler_nachricht: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    erstellt_am: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
    )
    aktualisiert_am: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
    )


class GratisCheck(Base):
    __tablename__ = "gratis_checks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    geburtsdatum: Mapped[str] = mapped_column(String(10), nullable=False)
    tropisch_sonne: Mapped[str] = mapped_column(String(50), nullable=False)
    siderisch_sonne: Mapped[str] = mapped_column(String(50), nullable=False)
    abweichung: Mapped[bool] = mapped_column(Boolean, nullable=False)
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    ip_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # SHA256

    erstellt_am: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("now()"),
    )
