"""
SyncMaster — Human Design Modul (Vereinfacht für MVP)

Berechnet den Human Design Typ basierend auf den Planetenpositionen.
Nutzt die Ekliptik-zu-I-Ching-Gate-Zuordnung und prüft Zentren/Kanäle.

VEREINFACHUNG FÜR MVP:
- Nur Personality-Sonne und Design-Sonne (88° vorher) werden für
  die Gate-Aktivierung genutzt, plus Mond, Nordknoten, und die
  klassischen Planeten.
- Dies ist eine Approximation — die Pro-Version wird alle 26 Aktivierungen
  (13 Personality + 13 Design) vollständig berechnen.

Intern als "simplified" markiert.
"""

import logging
from datetime import datetime, timedelta

from kerykeion import AstrologicalSubjectFactory

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# I-CHING GATE WHEEL: Ekliptische Grad → Gate (1–64)
# Jedes Gate belegt 5.625° (360° / 64 = 5.625°)
# Die Reihenfolge folgt dem Human Design Mandala.
# Start bei Gate 41 bei 2° Aquarius (tropisch ca. 302°)
# ═══════════════════════════════════════════════════════════════════

# Geordnete Liste der 64 Gates im Rad, startend bei 0° ekliptisch
# Jedes Gate: (start_grad, gate_nummer)
GATE_WHEEL = [
    (0.000, 17), (5.625, 21), (11.250, 51), (16.875, 42),
    (22.500, 3), (28.125, 27), (33.750, 24), (39.375, 2),
    (45.000, 23), (50.625, 8), (56.250, 20), (61.875, 16),
    (67.500, 35), (73.125, 45), (78.750, 12), (84.375, 15),
    (90.000, 52), (95.625, 39), (101.250, 53), (106.875, 62),
    (112.500, 56), (118.125, 31), (123.750, 33), (129.375, 7),
    (135.000, 4), (140.625, 29), (146.250, 59), (151.875, 40),
    (157.500, 64), (163.125, 47), (168.750, 6), (174.375, 46),
    (180.000, 18), (185.625, 48), (191.250, 57), (196.875, 32),
    (202.500, 50), (208.125, 28), (213.750, 44), (219.375, 1),
    (225.000, 43), (230.625, 14), (236.250, 34), (241.875, 9),
    (247.500, 5), (253.125, 26), (258.750, 11), (264.375, 10),
    (270.000, 58), (275.625, 38), (281.250, 54), (286.875, 61),
    (292.500, 60), (298.125, 41), (303.750, 19), (309.375, 13),
    (315.000, 49), (320.625, 30), (326.250, 55), (331.875, 37),
    (337.500, 63), (343.125, 22), (348.750, 36), (354.375, 25),
]


def _ecliptic_to_gate(longitude: float) -> int:
    """Wandelt ekliptische Länge (tropisch, 0–360°) in ein I-Ching Gate."""
    longitude = longitude % 360.0

    for i in range(len(GATE_WHEEL) - 1, -1, -1):
        if longitude >= GATE_WHEEL[i][0]:
            return GATE_WHEEL[i][1]

    return GATE_WHEEL[-1][1]


# ═══════════════════════════════════════════════════════════════════
# KANÄLE UND ZENTREN
# Ein Kanal verbindet zwei Zentren und braucht BEIDE Gates aktiviert.
# ═══════════════════════════════════════════════════════════════════

# Format: (gate_a, gate_b): ("zentrum_a", "zentrum_b")
CHANNELS = {
    # Kehle-Verbindungen von Motoren
    (36, 35): ("solar_plexus", "kehle"),
    (22, 12): ("solar_plexus", "kehle"),
    (34, 20): ("sakral", "kehle"),
    (34, 10): ("sakral", "g_zentrum"),  # Indirekt via G
    (45, 21): ("kehle", "herz"),
    (26, 44): ("herz", "milz"),
    (51, 25): ("herz", "g_zentrum"),
    # Sakral-Kanäle
    (5, 15): ("sakral", "g_zentrum"),
    (14, 2): ("sakral", "g_zentrum"),
    (29, 46): ("sakral", "g_zentrum"),
    (59, 6): ("sakral", "solar_plexus"),
    (27, 50): ("sakral", "milz"),
    (3, 60): ("sakral", "wurzel"),
    (42, 53): ("sakral", "wurzel"),
    (9, 52): ("sakral", "wurzel"),
    # Kehle-Verbindungen (nicht-motorisch)
    (16, 48): ("kehle", "milz"),
    (20, 57): ("kehle", "milz"),
    (20, 10): ("kehle", "g_zentrum"),
    (31, 7): ("kehle", "g_zentrum"),
    (8, 1): ("kehle", "g_zentrum"),
    (33, 13): ("kehle", "g_zentrum"),
    (23, 43): ("kehle", "ajna"),
    (56, 11): ("kehle", "ajna"),
    (62, 17): ("kehle", "ajna"),
    # Motor → Kehle (Wurzel)
    (54, 32): ("wurzel", "milz"),
    (38, 28): ("wurzel", "milz"),
    (58, 18): ("wurzel", "milz"),
    (19, 49): ("wurzel", "solar_plexus"),
    (39, 55): ("wurzel", "solar_plexus"),
    (41, 30): ("wurzel", "solar_plexus"),
    # Ajna
    (47, 64): ("ajna", "kopf"),
    (24, 61): ("ajna", "kopf"),
    (4, 63): ("ajna", "kopf"),
    (11, 56): ("ajna", "kehle"),
    (17, 62): ("ajna", "kehle"),
    (43, 23): ("ajna", "kehle"),
    # Milz
    (57, 20): ("milz", "kehle"),
    (48, 16): ("milz", "kehle"),
    (44, 26): ("milz", "herz"),
    (50, 27): ("milz", "sakral"),
    (32, 54): ("milz", "wurzel"),
    (28, 38): ("milz", "wurzel"),
    (18, 58): ("milz", "wurzel"),
    # Herz → Kehle
    (21, 45): ("herz", "kehle"),
    (25, 51): ("herz", "g_zentrum"),
    (40, 37): ("herz", "solar_plexus"),
    # G-Zentrum
    (10, 34): ("g_zentrum", "sakral"),
    (10, 20): ("g_zentrum", "kehle"),
    (7, 31): ("g_zentrum", "kehle"),
    (1, 8): ("g_zentrum", "kehle"),
    (13, 33): ("g_zentrum", "kehle"),
    (2, 14): ("g_zentrum", "sakral"),
    (46, 29): ("g_zentrum", "sakral"),
    (15, 5): ("g_zentrum", "sakral"),
}

# Motorische Zentren
MOTOR_ZENTREN = {"sakral", "solar_plexus", "herz", "wurzel"}


def _get_activated_gates(subject) -> set[int]:
    """Extrahiert alle aktivierten Gates aus einem kerykeion-Subject."""
    gates = set()
    planets = [
        subject.sun, subject.moon, subject.mercury, subject.venus,
        subject.mars, subject.jupiter, subject.saturn,
        subject.uranus, subject.neptune, subject.pluto,
    ]

    # Nordknoten
    if subject.mean_north_lunar_node:
        planets.append(subject.mean_north_lunar_node)

    for planet in planets:
        if planet and planet.abs_pos is not None:
            gate = _ecliptic_to_gate(planet.abs_pos)
            gates.add(gate)

    return gates


def _find_defined_channels(active_gates: set[int]) -> list[tuple]:
    """Findet alle komplett definierten Kanäle (beide Gates aktiv)."""
    defined = []
    seen = set()

    for (gate_a, gate_b), (zentrum_a, zentrum_b) in CHANNELS.items():
        key = tuple(sorted((gate_a, gate_b)))
        if key in seen:
            continue
        seen.add(key)

        if gate_a in active_gates and gate_b in active_gates:
            defined.append((gate_a, gate_b, zentrum_a, zentrum_b))

    return defined


def _find_defined_zentren(channels: list[tuple]) -> set[str]:
    """Bestimmt welche Zentren durch Kanäle definiert sind."""
    zentren = set()
    for _, _, z_a, z_b in channels:
        zentren.add(z_a)
        zentren.add(z_b)
    return zentren


def _is_motor_to_throat(channels: list[tuple], defined_zentren: set[str]) -> bool:
    """Prüft ob ein motorisches Zentrum direkt oder indirekt mit der Kehle verbunden ist."""
    # Adjazenzliste aufbauen
    adjacency: dict[str, set[str]] = {}
    for _, _, z_a, z_b in channels:
        adjacency.setdefault(z_a, set()).add(z_b)
        adjacency.setdefault(z_b, set()).add(z_a)

    # BFS von jedem Motor zur Kehle
    for motor in MOTOR_ZENTREN:
        if motor not in defined_zentren:
            continue

        visited = set()
        queue = [motor]
        while queue:
            current = queue.pop(0)
            if current == "kehle":
                return True
            if current in visited:
                continue
            visited.add(current)
            for neighbor in adjacency.get(current, []):
                if neighbor not in visited:
                    queue.append(neighbor)

    return False


def _determine_type(
    sakral_defined: bool,
    motor_to_throat: bool,
    any_zentrum_defined: bool,
) -> dict:
    """Bestimmt HD-Typ, Strategie und Autorität."""
    if not any_zentrum_defined:
        return {
            "typ": "Reflektor",
            "strategie": "Warte einen Mondzyklus (28 Tage)",
            "autoritaet": "Lunar",
            "kurzinfo": "Du bist ein Spiegel deiner Umgebung — einzigartig und weise.",
        }

    if sakral_defined and motor_to_throat:
        return {
            "typ": "Manifestierender Generator",
            "strategie": "Warte auf Response, dann informiere",
            "autoritaet": "Sakral",
            "kurzinfo": "Du bist hier um vieles gleichzeitig zu tun — folge deiner Begeisterung.",
        }

    if sakral_defined:
        return {
            "typ": "Generator",
            "strategie": "Warte auf Response",
            "autoritaet": "Sakral",
            "kurzinfo": "Du bist hier um zu tun, was dich begeistert.",
        }

    if motor_to_throat:
        return {
            "typ": "Manifestor",
            "strategie": "Informiere bevor du handelst",
            "autoritaet": "Emotional oder Milz",
            "kurzinfo": "Du bist hier um zu initiieren — informiere dein Umfeld.",
        }

    return {
        "typ": "Projektor",
        "strategie": "Warte auf die Einladung",
        "autoritaet": "Selbst-projiziert oder Milz",
        "kurzinfo": "Du bist hier um andere zu leiten — warte auf Anerkennung.",
    }


def calculate_human_design_type(
    geburtsdatum: str,
    geburtszeit: str,
    lat: float,
    lon: float,
    timezone: str,
) -> dict:
    """
    Berechnet den Human Design Typ (vereinfacht für MVP).

    Args:
        geburtsdatum: DD.MM.YYYY
        geburtszeit: HH:MM
        lat, lon: Koordinaten
        timezone: IANA Timezone

    Returns:
        dict mit typ, strategie, autoritaet, kurzinfo, _simplified
    """
    teile = geburtsdatum.split(".")
    tag, monat, jahr = int(teile[0]), int(teile[1]), int(teile[2])

    zeit_teile = geburtszeit.split(":")
    stunde, minute = int(zeit_teile[0]), int(zeit_teile[1])

    # Personality-Chart (Geburtsmoment)
    personality = AstrologicalSubjectFactory.from_birth_data(
        name="Personality",
        year=jahr, month=monat, day=tag,
        hour=stunde, minute=minute,
        lng=lon, lat=lat, tz_str=timezone,
        zodiac_type="Tropical",
        online=False,
    )

    # Design-Chart (~88 Tage / ~88° Sonnenbogen vorher)
    geburt_dt = datetime(jahr, monat, tag, stunde, minute)
    design_dt = geburt_dt - timedelta(days=88)

    design = AstrologicalSubjectFactory.from_birth_data(
        name="Design",
        year=design_dt.year, month=design_dt.month, day=design_dt.day,
        hour=design_dt.hour, minute=design_dt.minute,
        lng=lon, lat=lat, tz_str=timezone,
        zodiac_type="Tropical",
        online=False,
    )

    # Gates sammeln
    personality_gates = _get_activated_gates(personality)
    design_gates = _get_activated_gates(design)
    all_gates = personality_gates | design_gates

    # Kanäle und Zentren bestimmen
    channels = _find_defined_channels(all_gates)
    defined_zentren = _find_defined_zentren(channels)

    sakral_defined = "sakral" in defined_zentren
    motor_to_throat = _is_motor_to_throat(channels, defined_zentren)

    # Typ bestimmen
    result = _determine_type(sakral_defined, motor_to_throat, bool(defined_zentren))

    # Meta-Info hinzufügen
    result["_simplified"] = True
    result["_personality_gates"] = sorted(personality_gates)
    result["_design_gates"] = sorted(design_gates)
    result["_defined_channels"] = [(a, b) for a, b, _, _ in channels]
    result["_defined_zentren"] = sorted(defined_zentren)

    logger.info(
        "Human Design: Typ=%s (Sakral=%s, Motor→Kehle=%s, Zentren=%s)",
        result["typ"], sakral_defined, motor_to_throat, defined_zentren,
    )

    return result
