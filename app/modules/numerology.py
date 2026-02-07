"""
SyncMaster — Numerologie-Modul (Pythagoräisch)

Berechnet die Lebenszahl aus dem Geburtsdatum.
Meisterzahlen (11, 22, 33) werden NICHT weiter reduziert.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

MEISTERZAHLEN = {11, 22, 33}


def _quersumme(zahl: int) -> int:
    """Bildet die Quersumme einer Zahl."""
    return sum(int(d) for d in str(abs(zahl)))


def calculate_lebenszahl(geburtsdatum: str) -> dict:
    """
    Berechnet die pythagoräische Lebenszahl.

    Args:
        geburtsdatum: Datum im Format DD.MM.YYYY

    Returns:
        dict mit lebenszahl, berechnung (String), meisterzahl (bool)

    Raises:
        ValueError: Bei ungültigem Datum.
    """
    # Validierung
    try:
        datetime.strptime(geburtsdatum, "%d.%m.%Y")
    except ValueError:
        raise ValueError(
            f"Ungültiges Datum: '{geburtsdatum}'. Erwartet: DD.MM.YYYY"
        )

    # Alle Ziffern des Datums einzeln summieren
    ziffern = [int(d) for d in geburtsdatum if d.isdigit()]
    summe = sum(ziffern)

    # Berechnungs-String aufbauen
    ziffern_str = "+".join(str(d) for d in ziffern)
    schritte = [f"{ziffern_str} = {summe}"]

    # Reduzieren bis einstellig oder Meisterzahl
    while summe > 9 and summe not in MEISTERZAHLEN:
        neue_summe = _quersumme(summe)
        schritte.append(f"{'+'.join(str(d) for d in str(summe))} = {neue_summe}")
        summe = neue_summe

    ist_meisterzahl = summe in MEISTERZAHLEN
    berechnung = " → ".join(schritte)

    logger.info(
        "Numerologie: %s → Lebenszahl %d%s",
        geburtsdatum, summe,
        " (Meisterzahl)" if ist_meisterzahl else "",
    )

    return {
        "lebenszahl": summe,
        "berechnung": berechnung,
        "meisterzahl": ist_meisterzahl,
    }
