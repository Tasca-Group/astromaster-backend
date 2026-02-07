"""
SyncMaster — Master Calculator

Orchestriert alle Berechnungsmodule und gibt ein komplettes
Ergebnis-Dictionary für eine Person zurück.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from utils import safe_filename

from .geocoding import get_coordinates
from .numerology import calculate_lebenszahl
from .tropical import calculate_tropical
from .sidereal import calculate_sidereal
from .elements import get_element
from .egyptian_dekans import get_dekan
from .human_design import calculate_human_design_type

logger = logging.getLogger(__name__)


def calculate_all(
    name: str,
    geburtsdatum: str,
    geburtszeit: str,
    geburtsort: str,
    save_json: bool = False,
) -> dict:
    """
    Führt alle Berechnungen durch und gibt ein komplettes Ergebnis zurück.

    Jedes Modul wird in try/except gewrappt — bei Fehler in einem Modul
    wird der Rest trotzdem berechnet.

    Args:
        name: Vollständiger Name
        geburtsdatum: DD.MM.YYYY
        geburtszeit: HH:MM
        geburtsort: z.B. "Bensheim, Deutschland"
        save_json: Wenn True, wird das Ergebnis als .json gespeichert

    Returns:
        Komplettes Ergebnis-Dictionary
    """
    result = {
        "person": {
            "name": name,
            "geburtsdatum": geburtsdatum,
            "geburtszeit": geburtszeit,
            "geburtsort": geburtsort,
        },
        "geocoding": None,
        "numerologie": None,
        "tropisch": None,
        "siderisch": None,
        "element": None,
        "dekan": None,
        "human_design": None,
        "meta": {
            "version": "normal",
            "berechnet_am": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ayanamsa": "Lahiri",
            "ayanamsa_wert": None,
        },
        "fehler": [],
    }

    # 1. Geocoding
    try:
        geo = get_coordinates(geburtsort)
        result["geocoding"] = geo
    except Exception as e:
        logger.error("Geocoding fehlgeschlagen: %s", e)
        result["fehler"].append({"modul": "geocoding", "fehler": str(e)})
        return result  # Ohne Koordinaten geht nichts weiter

    lat = geo["lat"]
    lon = geo["lon"]
    timezone = geo["timezone"]

    # 2. Numerologie
    try:
        result["numerologie"] = calculate_lebenszahl(geburtsdatum)
    except Exception as e:
        logger.error("Numerologie fehlgeschlagen: %s", e)
        result["fehler"].append({"modul": "numerologie", "fehler": str(e)})

    # 3. Tropische Positionen
    try:
        result["tropisch"] = calculate_tropical(
            name, geburtsdatum, geburtszeit, lat, lon, timezone,
        )
    except Exception as e:
        logger.error("Tropisch fehlgeschlagen: %s", e)
        result["fehler"].append({"modul": "tropisch", "fehler": str(e)})

    # 4. Siderische Positionen (13 Zeichen)
    try:
        siderisch = calculate_sidereal(
            name, geburtsdatum, geburtszeit, lat, lon, timezone,
        )
        result["siderisch"] = siderisch
        result["meta"]["ayanamsa_wert"] = siderisch.get("ayanamsa_wert")
    except Exception as e:
        logger.error("Siderisch fehlgeschlagen: %s", e)
        result["fehler"].append({"modul": "siderisch", "fehler": str(e)})

    # 5. Element (basierend auf siderischem Sonnenzeichen)
    if result["siderisch"]:
        try:
            sonnenzeichen = result["siderisch"]["sonne"]["zeichen"]
            result["element"] = get_element(sonnenzeichen)
        except Exception as e:
            logger.error("Element fehlgeschlagen: %s", e)
            result["fehler"].append({"modul": "element", "fehler": str(e)})

    # 6. Ägyptischer Dekan (basierend auf siderischer Sonne)
    if result["siderisch"]:
        try:
            sonnenzeichen = result["siderisch"]["sonne"]["zeichen"]
            grad = result["siderisch"]["sonne"]["grad"]
            result["dekan"] = get_dekan(sonnenzeichen, grad)
        except Exception as e:
            logger.error("Dekan fehlgeschlagen: %s", e)
            result["fehler"].append({"modul": "dekan", "fehler": str(e)})

    # 7. Human Design
    try:
        result["human_design"] = calculate_human_design_type(
            geburtsdatum, geburtszeit, lat, lon, timezone,
        )
    except Exception as e:
        logger.error("Human Design fehlgeschlagen: %s", e)
        result["fehler"].append({"modul": "human_design", "fehler": str(e)})

    # Fehler-Liste leeren wenn keine Fehler
    if not result["fehler"]:
        del result["fehler"]

    # Optional: JSON speichern
    if save_json:
        _save_result_json(result, name, geburtsdatum)

    logger.info("Berechnung komplett für %s — %d Fehler",
                name, len(result.get("fehler", [])))

    return result


def _save_result_json(result: dict, name: str, geburtsdatum: str) -> Path:
    """Speichert das Ergebnis als JSON-Datei."""
    output_dir = Path(__file__).resolve().parent.parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Dateiname: Name_Datum.json
    safe_name = safe_filename(name)
    datum_clean = geburtsdatum.replace(".", "")
    filename = f"{safe_name}_{datum_clean}_result.json"
    filepath = output_dir / filename

    # _simplified und interne Felder für JSON entfernen
    clean_result = _clean_for_json(result)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(clean_result, f, ensure_ascii=False, indent=2)

    logger.info("Ergebnis gespeichert: %s", filepath)
    return filepath


def _clean_for_json(data):
    """Entfernt interne Felder (mit _ Prefix) für JSON-Export."""
    if isinstance(data, dict):
        return {
            k: _clean_for_json(v)
            for k, v in data.items()
            if not k.startswith("_")
        }
    if isinstance(data, list):
        return [_clean_for_json(item) for item in data]
    return data
