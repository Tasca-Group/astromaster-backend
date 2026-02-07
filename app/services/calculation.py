"""AstroMaster Backend — Berechnungs-Service."""

import logging

from app.modules.tropical import calculate_tropical
from app.modules.sidereal import calculate_sidereal
from app.modules.master_calculator import calculate_all

logger = logging.getLogger(__name__)

# Default-Koordinaten für Gratis-Check (Berlin, Mittagszeit)
DEFAULT_LAT = 52.52
DEFAULT_LON = 13.40
DEFAULT_TZ = "Europe/Berlin"
DEFAULT_TIME = "12:00"


def gratis_check(geburtsdatum: str) -> dict:
    """
    Schneller Vergleich: tropisch vs. siderisch Sonnenzeichen.

    Nutzt Default-Koordinaten (Berlin, 12:00) da das Sonnenzeichen
    primär vom Datum abhängt, nicht vom Ort.
    """
    try:
        tropisch = calculate_tropical(
            "Check", geburtsdatum, DEFAULT_TIME,
            DEFAULT_LAT, DEFAULT_LON, DEFAULT_TZ,
        )
        siderisch = calculate_sidereal(
            "Check", geburtsdatum, DEFAULT_TIME,
            DEFAULT_LAT, DEFAULT_LON, DEFAULT_TZ,
        )

        trop_sonne = tropisch["sonne"]["zeichen"]
        sid_sonne = siderisch["sonne"]["zeichen"]
        ophiuchus = siderisch["sonne"].get("ist_ophiuchus", False)

        return {
            "tropisch": trop_sonne,
            "siderisch": sid_sonne,
            "abweichung": trop_sonne != sid_sonne,
            "ophiuchus": ophiuchus,
        }
    except Exception as e:
        logger.error("Gratis-Check fehlgeschlagen: %s", e)
        raise


def full_calculation(
    name: str,
    geburtsdatum: str,
    geburtszeit: str,
    geburtsort: str,
) -> dict:
    """Führt die komplette Berechnung durch (alle 7 Module)."""
    return calculate_all(name, geburtsdatum, geburtszeit, geburtsort)
