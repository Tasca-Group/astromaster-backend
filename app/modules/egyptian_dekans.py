"""
SyncMaster — Ägyptische Dekane

Mappt siderische Sonnenposition auf einen von 37 Dekanen (36 + Asklepios).
Konfiguration wird aus config/dekans.yaml geladen.
"""

import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

# YAML-Konfiguration laden
CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "dekans.yaml"

_dekans_data: dict | None = None


def _load_dekans() -> dict:
    """Lädt die Dekan-Konfiguration aus YAML (lazy, einmalig)."""
    global _dekans_data
    if _dekans_data is not None:
        return _dekans_data

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        _dekans_data = yaml.safe_load(f)

    logger.debug("Dekane geladen aus %s", CONFIG_PATH)
    return _dekans_data


# Zeichen → YAML-Key Mapping
_ZEICHEN_ZU_KEY = {
    "Widder": "widder",
    "Stier": "stier",
    "Zwillinge": "zwillinge",
    "Krebs": "krebs",
    "Löwe": "loewe",
    "Jungfrau": "jungfrau",
    "Waage": "waage",
    "Skorpion": "skorpion",
    "Schütze": "schuetze",
    "Steinbock": "steinbock",
    "Wassermann": "wassermann",
    "Fische": "fische",
    "Ophiuchus": "ophiuchus",
}

# Dekan-Nummern pro Zeichen (absolute Nummerierung 1–37)
_DEKAN_OFFSET = {
    "Widder": 0, "Stier": 3, "Zwillinge": 6, "Krebs": 9,
    "Löwe": 12, "Jungfrau": 15, "Waage": 18, "Skorpion": 21,
    "Schütze": 24, "Steinbock": 27, "Wassermann": 30, "Fische": 33,
    "Ophiuchus": 36,  # Sonder-Dekan Nr. 37
}


def get_dekan(zeichen: str, grad_im_zeichen: float) -> dict:
    """
    Bestimmt den ägyptischen Dekan basierend auf Zeichen und Grad.

    Args:
        zeichen: Siderisches Zeichen (z.B. "Krebs", "Ophiuchus")
        grad_im_zeichen: Position innerhalb des Zeichens (0–30°)

    Returns:
        dict mit dekan_nummer, dekan_bereich, gott, titel, werkzeug
    """
    dekans = _load_dekans()
    yaml_key = _ZEICHEN_ZU_KEY.get(zeichen)

    if yaml_key is None:
        raise ValueError(f"Unbekanntes Zeichen für Dekan-Zuordnung: '{zeichen}'")

    zeichen_dekane = dekans.get(yaml_key, [])

    # Ophiuchus: immer Dekan 1 (= Asklepios)
    if zeichen == "Ophiuchus":
        if not zeichen_dekane:
            raise ValueError("Ophiuchus-Dekan nicht in Konfiguration gefunden")
        dekan = zeichen_dekane[0]
        return {
            "dekan_nummer": 37,
            "dekan_bereich": f"Ophiuchus (Sonder-Dekan)",
            "gott": dekan["gott"],
            "titel": dekan["titel"],
            "werkzeug": dekan["werkzeug"],
        }

    # Standard: 3 Dekane pro Zeichen à 10°
    if grad_im_zeichen < 10.0:
        dekan_index = 0
        bereich = f"1. Dekan {zeichen} (0°–10°)"
    elif grad_im_zeichen < 20.0:
        dekan_index = 1
        bereich = f"2. Dekan {zeichen} (10°–20°)"
    else:
        dekan_index = 2
        bereich = f"3. Dekan {zeichen} (20°–30°)"

    if dekan_index >= len(zeichen_dekane):
        raise ValueError(
            f"Dekan {dekan_index + 1} für {zeichen} nicht in Konfiguration"
        )

    dekan = zeichen_dekane[dekan_index]
    dekan_nummer = _DEKAN_OFFSET[zeichen] + dekan_index + 1

    result = {
        "dekan_nummer": dekan_nummer,
        "dekan_bereich": bereich,
        "gott": dekan["gott"],
        "titel": dekan["titel"],
        "werkzeug": dekan["werkzeug"],
    }

    logger.info("Dekan: %s %.1f° → %s (%s)", zeichen, grad_im_zeichen, dekan["gott"], bereich)
    return result
