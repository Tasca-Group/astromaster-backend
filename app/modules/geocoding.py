"""
SyncMaster — Geocoding-Modul

Wandelt Ortsnamen in Koordinaten (lat/lon) und Zeitzone um.
Nutzt geopy (Nominatim) und timezonefinder.
"""

import logging
from typing import Optional

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

logger = logging.getLogger(__name__)

# Einfacher In-Memory-Cache
_cache: dict[str, dict] = {}

# Einmalig initialisieren
_geolocator = Nominatim(user_agent="syncmaster_astro_v1", timeout=10)
_timezone_finder = TimezoneFinder()


def get_coordinates(ort: str) -> dict:
    """
    Wandelt einen Ortsnamen in Koordinaten und Zeitzone um.

    Args:
        ort: Ortsname, z.B. "Bensheim, Deutschland"

    Returns:
        dict mit lat, lon, timezone, ort_vollstaendig

    Raises:
        ValueError: Wenn der Ort nicht gefunden wurde.
    """
    # Cache prüfen
    cache_key = ort.strip().lower()
    if cache_key in _cache:
        logger.debug("Cache-Hit für: %s", ort)
        return _cache[cache_key]

    # Geocoding
    location = _geolocator.geocode(ort, language="de")
    if location is None:
        raise ValueError(f"Ort nicht gefunden: '{ort}'")

    lat = location.latitude
    lon = location.longitude

    # Zeitzone bestimmen
    timezone = _timezone_finder.timezone_at(lat=lat, lng=lon)
    if timezone is None:
        raise ValueError(
            f"Zeitzone konnte nicht bestimmt werden für: '{ort}' ({lat}, {lon})"
        )

    result = {
        "lat": round(lat, 4),
        "lon": round(lon, 4),
        "timezone": timezone,
        "ort_vollstaendig": location.address,
    }

    # Cachen
    _cache[cache_key] = result
    logger.info("Geocoding: '%s' → %s, %s (%s)", ort, lat, lon, timezone)

    return result
