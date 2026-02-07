"""Initial migration — bestellungen + gratis_checks

Revision ID: 001
Create Date: 2026-02-08
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "bestellungen",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(200), nullable=False),
        sa.Column("geburtsdatum", sa.String(10), nullable=False),
        sa.Column("geburtszeit", sa.String(5), nullable=False),
        sa.Column("geburtsort", sa.String(300), nullable=False),
        sa.Column("version", sa.String(20), server_default="normal"),
        sa.Column("status", sa.String(20), server_default="neu"),
        sa.Column("preis", sa.Float, server_default="39.0"),
        sa.Column("stripe_session_id", sa.String(200), nullable=True),
        sa.Column("stripe_payment_id", sa.String(200), nullable=True),
        sa.Column("berechnung_json", postgresql.JSONB, nullable=True),
        sa.Column("pdf_pfad", sa.String(500), nullable=True),
        sa.Column("email_gesendet", sa.Boolean, server_default="false"),
        sa.Column("fehler_nachricht", sa.Text, nullable=True),
        sa.Column("erstellt_am", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("aktualisiert_am", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "gratis_checks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("geburtsdatum", sa.String(10), nullable=False),
        sa.Column("tropisch_sonne", sa.String(50), nullable=False),
        sa.Column("siderisch_sonne", sa.String(50), nullable=False),
        sa.Column("abweichung", sa.Boolean, nullable=False),
        sa.Column("email", sa.String(200), nullable=True),
        sa.Column("ip_hash", sa.String(64), nullable=True),
        sa.Column("erstellt_am", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # Indices
    op.create_index("idx_bestellungen_status", "bestellungen", ["status"])
    op.create_index("idx_bestellungen_email", "bestellungen", ["email"])
    op.create_index("idx_bestellungen_stripe", "bestellungen", ["stripe_session_id"])
    op.create_index("idx_gratis_checks_datum", "gratis_checks", ["erstellt_am"])


def downgrade():
    op.drop_table("gratis_checks")
    op.drop_table("bestellungen")
