"""
SyncMaster — Siderische Astrologie (13 Zeichen inkl. Ophiuchus)

DAS HERZSTÜCK: Berechnet siderische Positionen mit Lahiri-Ayanamsa.
Nutzt kerykeions eingebauten Sidereal-Modus für korrekte 12-Zeichen-Zuordnung
(passend zu Astro-Seek). Ophiuchus wird als Zusatz-Check geprüft.
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

# Ophiuchus-Zone in siderischen Graden (zwischen Skorpion und Schütze)
# Siderisch: Skorpion endet bei ~240°, Schütze beginnt bei ~266°
OPHIUCHUS_START = 240.0
OPHIUCHUS_END = 266.0


def _translate_sign(code: str) -> str:
    """Übersetzt Kerykeion-Zeichencode in deutschen Namen."""
    return SIGN_MAP.get(code, code)


def _check_ophiuchus(abs_pos: float) -> bool:
    """Prüft ob eine siderische Position in der Ophiuchus-Zone liegt."""
    return OPHIUCHUS_START <= abs_pos < OPHIUCHUS_END


def calculate_sidereal(
    name: str,
    geburtsdatum: str,
    geburtszeit: str,
    lat: float,
    lon: float,
    timezone: str,
) -> dict:
    """
    Berechnet siderische Positionen (Lahiri-Ayanamsa).

    Nutzt kerykeions Sidereal-Modus direkt für die 12-Zeichen-Zuordnung
    (kompatibel mit Astro-Seek). Ophiuchus wird als Zusatz-Flag gesetzt
    wenn eine Position in der Zone 240°-266° liegt.

    Args:
        name: Name der Person
        geburtsdatum: DD.MM.YYYY
        geburtszeit: HH:MM
        lat: Breitengrad
        lon: Längengrad
        timezone: IANA Timezone

    Returns:
        dict mit ayanamsa_wert, sonne, mond, aszendent
    """
    # Datum parsen
    teile = geburtsdatum.split(".")
    tag, monat, jahr = int(teile[0]), int(teile[1]), int(teile[2])

    zeit_teile = geburtszeit.split(":")
    stunde, minute = int(zeit_teile[0]), int(zeit_teile[1])

    # Siderisches Chart mit Lahiri-Ayanamsa
    sidereal_subject = AstrologicalSubjectFactory.from_birth_data(
        name=name,
        year=jahr,
        month=monat,
        day=tag,
        hour=stunde,
        minute=minute,
        lng=lon,
        lat=lat,
        tz_str=timezone,
        zodiac_type="Sidereal",
        sidereal_mode="LAHIRI",
        online=False,
    )

    # Tropisches Chart für Ayanamsa-Berechnung
    tropical_subject = AstrologicalSubjectFactory.from_birth_data(
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

    # Ayanamsa = Differenz tropisch - siderisch
    ayanamsa_wert = round(
        tropical_subject.sun.abs_pos - sidereal_subject.sun.abs_pos, 4
    )

    # Positionen direkt von kerykeion übernehmen (12-Zeichen, Astro-Seek-kompatibel)
    sonne_abs = sidereal_subject.sun.abs_pos
    mond_abs = sidereal_subject.moon.abs_pos
    asc_abs = sidereal_subject.ascendant.abs_pos

    result = {
        "ayanamsa_wert": ayanamsa_wert,
        "sonne": {
            "zeichen": _translate_sign(sidereal_subject.sun.sign),
            "grad": round(sidereal_subject.sun.position, 2),
            "grad_absolut": round(sonne_abs, 2),
            "ist_ophiuchus": _check_ophiuchus(sonne_abs),
        },
        "mond": {
            "zeichen": _translate_sign(sidereal_subject.moon.sign),
            "grad": round(sidereal_subject.moon.position, 2),
            "grad_absolut": round(mond_abs, 2),
            "ist_ophiuchus": _check_ophiuchus(mond_abs),
        },
        "aszendent": {
            "zeichen": _translate_sign(sidereal_subject.ascendant.sign),
            "grad": round(sidereal_subject.ascendant.position, 2),
            "grad_absolut": round(asc_abs, 2),
            "ist_ophiuchus": _check_ophiuchus(asc_abs),
        },
    }

    logger.info(
        "Siderisch (Lahiri): %s -> Sonne=%s, Mond=%s, ASC=%s (Ayanamsa=%.4f)",
        name,
        result["sonne"]["zeichen"],
        result["mond"]["zeichen"],
        result["aszendent"]["zeichen"],
        ayanamsa_wert,
    )

    return result
