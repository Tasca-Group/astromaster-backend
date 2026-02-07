"""
SyncMaster — Content-Loader

Lädt Textbausteine aus content/{kategorie}/{name}.txt.
Gibt Platzhaltertext zurück wenn eine Datei nicht existiert.

Dateiformat:
    TITEL: [Überschrift]
    ---
    [Fließtext]
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

CONTENT_DIR = Path(__file__).resolve().parent.parent.parent / "content"


def load_content(kategorie: str, name: str) -> dict:
    """
    Lädt Text aus content/{kategorie}/{name}.txt.

    Args:
        kategorie: Unterordner (z.B. "sternzeichen", "numerologie")
        name: Dateiname ohne .txt (z.B. "zwillinge", "lebenszahl_1")

    Returns:
        dict mit "titel" und "text"
    """
    filepath = CONTENT_DIR / kategorie / f"{name}.txt"

    if not filepath.exists():
        logger.warning("Content-Datei nicht gefunden: %s", filepath)
        return {
            "titel": name.replace("_", " ").title(),
            "text": f"[Text für {name} wird noch erstellt]",
        }

    content = filepath.read_text(encoding="utf-8").strip()

    # Format parsen: TITEL: ...\n---\n[Text]
    if "---" in content:
        header, body = content.split("---", 1)
        titel = header.strip()
        if titel.upper().startswith("TITEL:"):
            titel = titel[6:].strip()
        text = body.strip()
    else:
        titel = name.replace("_", " ").title()
        text = content

    return {"titel": titel, "text": text}
