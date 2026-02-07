"""
SyncMaster — Elemente-Modul

Mappt siderisches Sonnenzeichen auf sein Element.
5 Elemente: Feuer, Erde, Luft, Wasser, Feuer-Wasser (Ophiuchus).
"""

import logging

logger = logging.getLogger(__name__)

ELEMENTS = {
    "Feuer": {
        "zeichen": ["Widder", "Löwe", "Schütze"],
        "eigenschaften": "Dynamisch, initiativ, leidenschaftlich",
        "schatten": "Impulsiv, aggressiv, ungeduldig",
    },
    "Erde": {
        "zeichen": ["Stier", "Jungfrau", "Steinbock"],
        "eigenschaften": "Stabil, praktisch, zuverlässig",
        "schatten": "Starr, materialistisch, langsam",
    },
    "Luft": {
        "zeichen": ["Zwillinge", "Waage", "Wassermann"],
        "eigenschaften": "Intellektuell, kommunikativ, sozial",
        "schatten": "Oberflächlich, unbeständig, distanziert",
    },
    "Wasser": {
        "zeichen": ["Krebs", "Skorpion", "Fische"],
        "eigenschaften": "Emotional, intuitiv, empathisch",
        "schatten": "Launisch, manipulativ, abhängig",
    },
    "Feuer-Wasser": {
        "zeichen": ["Ophiuchus"],
        "eigenschaften": "Transformativ, heilend, alchemistisch",
        "schatten": "Konfliktgeladen, intensiv, extrem",
    },
}

# Reverse-Lookup: Zeichen → Element
_ZEICHEN_ZU_ELEMENT: dict[str, str] = {}
for element_name, data in ELEMENTS.items():
    for zeichen in data["zeichen"]:
        _ZEICHEN_ZU_ELEMENT[zeichen] = element_name


def get_element(zeichen: str) -> dict:
    """
    Gibt das Element für ein Sternzeichen zurück.

    Args:
        zeichen: Name des Zeichens (z.B. "Zwillinge", "Ophiuchus")

    Returns:
        dict mit element, eigenschaften, schatten

    Raises:
        ValueError: Wenn das Zeichen unbekannt ist.
    """
    element_name = _ZEICHEN_ZU_ELEMENT.get(zeichen)
    if element_name is None:
        raise ValueError(f"Unbekanntes Zeichen: '{zeichen}'")

    data = ELEMENTS[element_name]
    result = {
        "element": element_name,
        "eigenschaften": data["eigenschaften"],
        "schatten": data["schatten"],
    }

    logger.info("Element: %s → %s", zeichen, element_name)
    return result
