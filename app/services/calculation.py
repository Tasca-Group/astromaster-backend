"""AstroMaster Backend — Berechnungs-Service."""

import logging

from app.modules.tropical import calculate_tropical
from app.modules.sidereal import calculate_sidereal
from app.modules.master_calculator import calculate_all
from app.modules.geocoding import get_coordinates

logger = logging.getLogger(__name__)

# Default-Koordinaten für Gratis-Check (Berlin, Mittagszeit)
DEFAULT_LAT = 52.52
DEFAULT_LON = 13.40
DEFAULT_TZ = "Europe/Berlin"
DEFAULT_TIME = "12:00"


def gratis_check(geburtsdatum: str, geburtszeit: str | None = None, geburtsort: str | None = None) -> dict:
    """
    Vergleich: tropisch vs. siderisch — Sonne, Mond, optional Aszendent.
    """
    try:
        # Koordinaten bestimmen
        if geburtsort:
            geo = get_coordinates(geburtsort)
            lat, lon, tz = geo["lat"], geo["lon"], geo["timezone"]
        else:
            lat, lon, tz = DEFAULT_LAT, DEFAULT_LON, DEFAULT_TZ

        zeit = geburtszeit or DEFAULT_TIME
        hat_uhrzeit = geburtszeit is not None

        tropisch = calculate_tropical(
            "Check", geburtsdatum, zeit, lat, lon, tz,
        )
        siderisch = calculate_sidereal(
            "Check", geburtsdatum, zeit, lat, lon, tz,
        )

        trop_sonne = tropisch["sonne"]["zeichen"]
        sid_sonne = siderisch["sonne"]["zeichen"]
        ophiuchus = siderisch["sonne"].get("ist_ophiuchus", False)

        trop_mond = tropisch["mond"]["zeichen"]
        sid_mond = siderisch["mond"]["zeichen"]

        result = {
            # Backward compat
            "tropisch": trop_sonne,
            "siderisch": sid_sonne,
            "abweichung": trop_sonne != sid_sonne,
            "ophiuchus": ophiuchus,
            # Extended
            "sonne": {
                "tropisch": trop_sonne,
                "siderisch": sid_sonne,
                "abweichung": trop_sonne != sid_sonne,
            },
            "mond": {
                "tropisch": trop_mond,
                "siderisch": sid_mond,
                "abweichung": trop_mond != sid_mond,
            },
            "aszendent": None,
            "hat_uhrzeit": hat_uhrzeit,
        }

        if hat_uhrzeit:
            trop_asc = tropisch["aszendent"]["zeichen"]
            sid_asc = siderisch["aszendent"]["zeichen"]
            result["aszendent"] = {
                "tropisch": trop_asc,
                "siderisch": sid_asc,
                "abweichung": trop_asc != sid_asc,
            }

        return result
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
