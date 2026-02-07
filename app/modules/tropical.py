"""
SyncMaster — Tropische Astrologie (12 Zeichen, westlich)

Berechnet tropische Planetenpositionen mit kerykeion.
Dient als Vergleichsreferenz für den System-Check.
"""

import logging
from kerykeion import AstrologicalSubjectFactory

logger = logging.getLogger(__name__)

# Kerykeion 3-Letter-Codes → Deutsche Zeichennamen
SIGN_MAP = {
    "Ari": "Widder",
    "Tau": "Stier",
    "Gem": "Zwillinge",
    "Can": "Krebs",
    "Leo": "Löwe",
    "Vir": "Jungfrau",
    "Lib": "Waage",
    "Sco": "Skorpion",
    "Sag": "Schütze",
    "Cap": "Steinbock",
    "Aqu": "Wassermann",
    "Pis": "Fische",
}


def _translate_sign(code: str) -> str:
    """Übersetzt Kerykeion-Zeichencode in deutschen Namen."""
    return SIGN_MAP.get(code, code)


def calculate_tropical(
    name: str,
    geburtsdatum: str,
    geburtszeit: str,
    lat: float,
    lon: float,
    timezone: str,
) -> dict:
    """
    Berechnet tropische Positionen für Sonne, Mond, Aszendent.

    Args:
        name: Name der Person
        geburtsdatum: DD.MM.YYYY
        geburtszeit: HH:MM
        lat: Breitengrad
        lon: Längengrad
        timezone: IANA Timezone (z.B. "Europe/Berlin")

    Returns:
        dict mit sonne, mond, aszendent — jeweils zeichen, grad, grad_absolut
    """
    # Datum parsen
    teile = geburtsdatum.split(".")
    tag, monat, jahr = int(teile[0]), int(teile[1]), int(teile[2])

    zeit_teile = geburtszeit.split(":")
    stunde, minute = int(zeit_teile[0]), int(zeit_teile[1])

    # Kerykeion-Chart erstellen (tropical ist Standard)
    subject = AstrologicalSubjectFactory.from_birth_data(
        name=name,
        year=jahr,
        month=monat,
        day=tag,
        hour=stunde,
        minute=minute,
        lng=lon,
        lat=lat,
        tz_str=timezone,
        zodiac_type="Tropical",
        online=False,
    )

    result = {
        "sonne": {
            "zeichen": _translate_sign(subject.sun.sign),
            "grad": round(subject.sun.position, 2),
            "grad_absolut": round(subject.sun.abs_pos, 2),
        },
        "mond": {
            "zeichen": _translate_sign(subject.moon.sign),
            "grad": round(subject.moon.position, 2),
            "grad_absolut": round(subject.moon.abs_pos, 2),
        },
        "aszendent": {
            "zeichen": _translate_sign(subject.ascendant.sign),
            "grad": round(subject.ascendant.position, 2),
            "grad_absolut": round(subject.ascendant.abs_pos, 2),
        },
    }

    logger.info(
        "Tropisch: %s → Sonne=%s, Mond=%s, ASC=%s",
        name,
        result["sonne"]["zeichen"],
        result["mond"]["zeichen"],
        result["aszendent"]["zeichen"],
    )

    return result
