"""
SyncMaster — Hilfsfunktionen

Gemeinsame Utilities für Dateinamen-Bereinigung etc.
"""

import re
import unicodedata


def safe_filename(name: str) -> str:
    """
    Bereinigt einen Namen für die Verwendung in Dateinamen.

    Beispiele:
        "Marcel Tasca"                  → "Marcel_Tasca"
        "Anna Maria Müller"             → "Anna_Maria_Mueller"
        "Jean-Pierre von der Heide"     → "Jean-Pierre_von_der_Heide"
        "Dr. Maria Christina Weber-Schmidt" → "Dr_Maria_Christina_Weber-Schmidt"
    """
    # Deutsche Umlaute und ß explizit ersetzen
    replacements = {
        "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
        "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
    }
    for char, repl in replacements.items():
        name = name.replace(char, repl)

    # Unicode-Akzente entfernen (é→e, ñ→n, etc.)
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")

    # Leerzeichen → Unterstrich
    name = name.replace(" ", "_")

    # Nur Buchstaben, Ziffern, Unterstrich und Bindestrich behalten
    name = re.sub(r"[^A-Za-z0-9_\-]", "", name)

    # Mehrfache Unterstriche zusammenfassen
    name = re.sub(r"_+", "_", name)

    return name.strip("_")
