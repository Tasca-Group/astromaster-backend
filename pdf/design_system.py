"""
SyncMaster — PDF Design-System

Farben, Fonts, Abstände und Helper-Funktionen für ReportLab.
Lädt Konfiguration aus config/design.yaml.
"""

import logging
from pathlib import Path

import yaml
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════
# Konfiguration laden
# ═══════════════════════════════════════════

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "design.yaml"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    _config = yaml.safe_load(f)

# ═══════════════════════════════════════════
# Farben
# ═══════════════════════════════════════════

BACKGROUND = HexColor(_config["colors"]["background"])
GOLD = HexColor(_config["colors"]["gold"])
GOLD_LIGHT = HexColor(_config["colors"]["gold_light"])
TEXT_PRIMARY = HexColor(_config["colors"]["text_primary"])
TEXT_SECONDARY = HexColor(_config["colors"]["text_secondary"])
ACCENT_TEAL = HexColor(_config["colors"]["accent_teal"])
DIVIDER = HexColor(_config["colors"]["divider"])
TABLE_HEADER = HexColor(_config["colors"]["table_header"])
TABLE_ROW_ALT = HexColor(_config["colors"]["table_row_alt"])

# Zusätzliche Farben
SUCCESS = HexColor("#4CAF50")
WARNING = HexColor("#FF9800")
DANGER = HexColor("#F44336")
WHITE = HexColor("#FFFFFF")
TRANSPARENT = HexColor("#00000000")

# ═══════════════════════════════════════════
# Fonts
# ═══════════════════════════════════════════

FONT_FAMILY = _config["fonts"]["family"]
TITLE_SIZE = _config["fonts"]["title_size"]
SUBTITLE_SIZE = _config["fonts"]["subtitle_size"]
HEADING_SIZE = _config["fonts"]["heading_size"]
BODY_SIZE = _config["fonts"]["body_size"]
SMALL_SIZE = _config["fonts"]["small_size"]

# ═══════════════════════════════════════════
# Layout
# ═══════════════════════════════════════════

PAGE_WIDTH, PAGE_HEIGHT = A4  # 595.27 x 841.89 points
MARGIN_TOP = _config["layout"]["margin_top"]
MARGIN_BOTTOM = _config["layout"]["margin_bottom"]
MARGIN_LEFT = _config["layout"]["margin_left"]
MARGIN_RIGHT = _config["layout"]["margin_right"]
LINE_SPACING = _config["layout"]["line_spacing"]

# Nutzbare Fläche
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT
CONTENT_TOP = PAGE_HEIGHT - MARGIN_TOP
CONTENT_BOTTOM = MARGIN_BOTTOM

# ═══════════════════════════════════════════
# Unicode-Symbole für Sternzeichen
# ═══════════════════════════════════════════

ZEICHEN_SYMBOLE = {
    "Widder": "\u2648",
    "Stier": "\u2649",
    "Zwillinge": "\u264A",
    "Krebs": "\u264B",
    "Löwe": "\u264C",
    "Jungfrau": "\u264D",
    "Waage": "\u264E",
    "Skorpion": "\u264F",
    "Ophiuchus": "\u26CE",
    "Schütze": "\u2650",
    "Steinbock": "\u2651",
    "Wassermann": "\u2652",
    "Fische": "\u2653",
}


# ═══════════════════════════════════════════
# Helper-Funktionen
# ═══════════════════════════════════════════

def draw_background(canvas):
    """Zeichnet den dunklen Hintergrund auf die gesamte Seite."""
    canvas.setFillColor(BACKGROUND)
    canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)


def draw_gold_line(canvas, y, width=None, thickness=0.5):
    """Zeichnet eine goldene horizontale Linie."""
    if width is None:
        width = CONTENT_WIDTH
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(thickness)
    canvas.line(MARGIN_LEFT, y, MARGIN_LEFT + width, y)


def draw_page_number(canvas, page_num):
    """Zeichnet die Seitenzahl unten mittig in Gold."""
    canvas.setFont(FONT_FAMILY, SMALL_SIZE)
    canvas.setFillColor(GOLD)
    canvas.drawCentredString(PAGE_WIDTH / 2, MARGIN_BOTTOM - 25, str(page_num))


def draw_title(canvas, text, y, size=None, color=None, centered=True):
    """Zeichnet einen Titel in Gold."""
    if size is None:
        size = TITLE_SIZE
    if color is None:
        color = GOLD
    canvas.setFont(f"{FONT_FAMILY}-Bold", size)
    canvas.setFillColor(color)
    if centered:
        canvas.drawCentredString(PAGE_WIDTH / 2, y, text)
    else:
        canvas.drawString(MARGIN_LEFT, y, text)
    return y - size - 5


def draw_subtitle(canvas, text, y, color=None):
    """Zeichnet eine Unterüberschrift."""
    if color is None:
        color = GOLD_LIGHT
    canvas.setFont(f"{FONT_FAMILY}-Bold", SUBTITLE_SIZE)
    canvas.setFillColor(color)
    canvas.drawString(MARGIN_LEFT, y, text)
    return y - SUBTITLE_SIZE - 8


def draw_heading(canvas, text, y, color=None):
    """Zeichnet eine Abschnitts-Überschrift in Gold."""
    if color is None:
        color = GOLD
    canvas.setFont(f"{FONT_FAMILY}-Bold", HEADING_SIZE)
    canvas.setFillColor(color)
    canvas.drawString(MARGIN_LEFT, y, text)
    return y - HEADING_SIZE - 6


def draw_body_text(canvas, text, y, max_width=None, color=None, size=None):
    """
    Zeichnet mehrzeiligen Fließtext mit automatischem Umbruch.

    Returns:
        Neue y-Position nach dem Text.
    """
    if max_width is None:
        max_width = CONTENT_WIDTH
    if color is None:
        color = TEXT_PRIMARY
    if size is None:
        size = BODY_SIZE

    canvas.setFont(FONT_FAMILY, size)
    canvas.setFillColor(color)

    words = text.split()
    line = ""
    line_height = size + (LINE_SPACING - size)

    for word in words:
        test_line = f"{line} {word}".strip()
        if canvas.stringWidth(test_line, FONT_FAMILY, size) <= max_width:
            line = test_line
        else:
            if y < CONTENT_BOTTOM + 20:
                return y  # Seitenende erreicht
            canvas.drawString(MARGIN_LEFT, y, line)
            y -= line_height
            line = word

    if line:
        if y >= CONTENT_BOTTOM + 20:
            canvas.drawString(MARGIN_LEFT, y, line)
            y -= line_height

    return y


def draw_box(canvas, x, y, width, height, fill_color=None, border_color=None,
             border_width=1, corner_radius=5):
    """Zeichnet eine abgerundete Box."""
    if fill_color:
        canvas.setFillColor(fill_color)
    if border_color:
        canvas.setStrokeColor(border_color)
        canvas.setLineWidth(border_width)

    fill = 1 if fill_color else 0
    stroke = 1 if border_color else 0

    canvas.roundRect(x, y, width, height, corner_radius, fill=fill, stroke=stroke)


def draw_info_card(canvas, y, icon, label, value):
    """Zeichnet eine Info-Karte (Icon + Label + Wert)."""
    box_height = 45
    box_y = y - box_height

    # Box Hintergrund
    draw_box(canvas, MARGIN_LEFT, box_y, CONTENT_WIDTH, box_height,
             fill_color=TABLE_HEADER, border_color=DIVIDER)

    # Icon + Label
    canvas.setFont(FONT_FAMILY, BODY_SIZE)
    canvas.setFillColor(TEXT_SECONDARY)
    canvas.drawString(MARGIN_LEFT + 15, box_y + 27, f"{icon}  {label}")

    # Wert
    canvas.setFont(f"{FONT_FAMILY}-Bold", HEADING_SIZE)
    canvas.setFillColor(GOLD)
    canvas.drawString(MARGIN_LEFT + 15, box_y + 8, str(value))

    return box_y - 8
