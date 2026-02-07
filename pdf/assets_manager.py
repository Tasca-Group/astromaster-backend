"""
SyncMaster — Assets Manager

Lädt und skaliert Bilder für PDFs.
Gibt Platzhalter zurück wenn ein Bild nicht existiert.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def get_logo_path() -> Path | None:
    """Gibt den Pfad zum SyncMaster-Logo zurück oder None."""
    path = ASSETS_DIR / "logos" / "syncmaster_logo.png"
    if path.exists():
        return path
    logger.debug("Logo nicht gefunden: %s", path)
    return None


def get_sternzeichen_path(zeichen: str) -> Path | None:
    """Gibt den Pfad zum Sternzeichen-Bild zurück oder None."""
    name = (
        zeichen.lower()
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ä", "ae")
    )
    for ext in (".png", ".jpg", ".jpeg"):
        path = ASSETS_DIR / "sternzeichen" / f"{name}{ext}"
        if path.exists():
            return path
    logger.debug("Sternzeichen-Bild nicht gefunden: %s", zeichen)
    return None


def get_gott_path(gott: str) -> Path | None:
    """Gibt den Pfad zum Götter-Bild zurück oder None."""
    name = (
        gott.lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ä", "ae")
    )
    for ext in (".png", ".jpg", ".jpeg"):
        path = ASSETS_DIR / "aegyptische_goetter" / f"{name}{ext}"
        if path.exists():
            return path
    logger.debug("Götter-Bild nicht gefunden: %s", gott)
    return None


def get_element_path(element: str) -> Path | None:
    """Gibt den Pfad zum Element-Bild zurück oder None."""
    name = (
        element.lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("ä", "ae")
    )
    for ext in (".png", ".jpg", ".jpeg"):
        path = ASSETS_DIR / "elemente" / f"{name}{ext}"
        if path.exists():
            return path
    logger.debug("Element-Bild nicht gefunden: %s", element)
    return None
