"""
SyncMaster — PDF Normal-Version (39€, 8–10 Seiten)

Generiert die komplette Astro-Analyse als professionelle PDF
im Dark/Gold Design-System.
"""

import logging
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas

from .design_system import (
    BACKGROUND, GOLD, GOLD_LIGHT, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_TEAL, DIVIDER, TABLE_HEADER, TABLE_ROW_ALT,
    WHITE, SUCCESS, WARNING, DANGER,
    FONT_FAMILY, TITLE_SIZE, SUBTITLE_SIZE, HEADING_SIZE, BODY_SIZE, SMALL_SIZE,
    PAGE_WIDTH, PAGE_HEIGHT, MARGIN_LEFT, MARGIN_RIGHT, MARGIN_TOP, MARGIN_BOTTOM,
    CONTENT_WIDTH, CONTENT_TOP, CONTENT_BOTTOM, LINE_SPACING,
    draw_background, draw_gold_line, draw_page_number, draw_title,
    draw_subtitle, draw_heading, draw_body_text, draw_box, draw_info_card,
)
from .assets_manager import get_logo_path

from app.modules.content_loader import load_content

logger = logging.getLogger(__name__)


def generate(data: dict, output_path: str | Path) -> Path:
    """
    Generiert die Normal-Version PDF.

    Args:
        data: Komplettes Ergebnis-Dict von master_calculator.calculate_all()
        output_path: Ziel-Dateipfad für die PDF

    Returns:
        Path zum generierten PDF
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    c = pdf_canvas.Canvas(str(output_path), pagesize=A4)
    c.setTitle(f"SyncMaster Analyse — {data['person']['name']}")
    c.setAuthor("SyncMaster")

    page_num = [0]  # Mutable für Closure

    def new_page():
        """Startet eine neue Seite mit Hintergrund."""
        if page_num[0] > 0:
            c.showPage()
        page_num[0] += 1
        draw_background(c)
        if page_num[0] > 1:
            draw_page_number(c, page_num[0])
        return CONTENT_TOP

    # ═══════════════════════════════════════════
    # SEITE 1: DECKBLATT
    # ═══════════════════════════════════════════
    y = new_page()

    # Obere goldene Linie
    draw_gold_line(c, PAGE_HEIGHT - 40, thickness=1.0)

    # Logo (falls vorhanden)
    logo = get_logo_path()
    if logo:
        c.drawImage(str(logo), PAGE_WIDTH / 2 - 60, y - 50, width=120, height=120,
                     preserveAspectRatio=True, mask="auto")
        y -= 160
    else:
        # Text-Logo als Fallback
        y -= 40
        c.setFont(f"{FONT_FAMILY}-Bold", 14)
        c.setFillColor(GOLD)
        c.drawCentredString(PAGE_WIDTH / 2, y, "SYNCMASTER")
        y -= 80

    # Haupttitel
    c.setFont(f"{FONT_FAMILY}-Bold", 32)
    c.setFillColor(GOLD)
    c.drawCentredString(PAGE_WIDTH / 2, y, "DEINE")
    y -= 40
    c.drawCentredString(PAGE_WIDTH / 2, y, "ASTRO-ANALYSE")
    y -= 60

    # Goldene Trennlinie (zentriert)
    x_center = PAGE_WIDTH / 2
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(x_center - 100, y, x_center + 100, y)
    y -= 40

    # Personendaten
    person = data["person"]
    c.setFont(f"{FONT_FAMILY}-Bold", 18)
    c.setFillColor(WHITE)
    c.drawCentredString(PAGE_WIDTH / 2, y, person["name"])
    y -= 30

    c.setFont(FONT_FAMILY, 13)
    c.setFillColor(TEXT_SECONDARY)
    c.drawCentredString(PAGE_WIDTH / 2, y,
                        f"Geboren am {person['geburtsdatum']} um {person['geburtszeit']} Uhr")
    y -= 20
    c.drawCentredString(PAGE_WIDTH / 2, y, person["geburtsort"])
    y -= 80

    # Untere Info
    c.setFont(FONT_FAMILY, SMALL_SIZE)
    c.setFillColor(TEXT_SECONDARY)
    c.drawCentredString(PAGE_WIDTH / 2, MARGIN_BOTTOM + 40,
                        f"Erstellt am {datetime.now().strftime('%d.%m.%Y')}")
    c.drawCentredString(PAGE_WIDTH / 2, MARGIN_BOTTOM + 25,
                        "powered by SyncMaster")

    # Untere goldene Linie
    draw_gold_line(c, MARGIN_BOTTOM + 55, thickness=1.0)

    # ═══════════════════════════════════════════
    # SEITE 2: MISSION STATEMENT
    # ═══════════════════════════════════════════
    y = new_page()

    y = draw_title(c, "WARUM DIESE ANALYSE", y, size=24)
    y = draw_title(c, "ANDERS IST", y - 5, size=24)
    y -= 15
    draw_gold_line(c, y)
    y -= 25

    content = load_content("system_erklaerungen", "praezession")
    y = draw_body_text(c, content["text"], y)
    y -= 20

    # Zusätzlicher Erklärungstext
    extra = (
        "Die meisten Menschen kennen ihr Sternzeichen aus Zeitschriften und Horoskop-Apps. "
        "Doch dieses Zeichen basiert auf dem tropischen System — einem 2.000 Jahre alten "
        "Modell, das die astronomische Realität nicht mehr widerspiegelt. "
        "In dieser Analyse zeigen wir dir, was die Sterne WIRKLICH über dich sagen."
    )
    y = draw_body_text(c, extra, y)
    y -= 30

    # Hinweis-Box
    draw_box(c, MARGIN_LEFT, y - 50, CONTENT_WIDTH, 50,
             fill_color=TABLE_HEADER, border_color=GOLD)
    c.setFont(f"{FONT_FAMILY}-Bold", BODY_SIZE)
    c.setFillColor(GOLD)
    c.drawCentredString(PAGE_WIDTH / 2, y - 25,
                        "Lass uns prüfen, ob auch du betroffen bist ...")

    # ═══════════════════════════════════════════
    # SEITE 3–4: SYSTEM-CHECK (DER USP!)
    # ═══════════════════════════════════════════
    y = new_page()

    y = draw_title(c, "DEIN SYSTEM-CHECK", y, size=26)
    y -= 10
    draw_gold_line(c, y)
    y -= 30

    tropisch = data.get("tropisch", {})
    siderisch = data.get("siderisch", {})

    # Einleitungstext
    intro = (
        "Hier siehst du den direkten Vergleich: Links dein tropisches Zeichen "
        "(das, was du bisher kanntest), rechts dein siderisches Zeichen "
        "(astronomisch korrekt, basierend auf den echten Sternpositionen)."
    )
    y = draw_body_text(c, intro, y, color=TEXT_SECONDARY)
    y -= 25

    # Vergleichstabelle
    col1_x = MARGIN_LEFT
    col2_x = MARGIN_LEFT + 170
    col3_x = MARGIN_LEFT + 340
    row_height = 55

    # Header
    draw_box(c, col1_x, y - 30, CONTENT_WIDTH, 30,
             fill_color=TABLE_HEADER)
    c.setFont(f"{FONT_FAMILY}-Bold", 11)
    c.setFillColor(TEXT_SECONDARY)
    c.drawString(col1_x + 10, y - 20, "")
    c.drawString(col2_x + 10, y - 20, "TROPISCH (westlich)")
    c.drawString(col3_x + 10, y - 20, "SIDERISCH (astronomisch)")
    y -= 35

    # Zeilen: Sonne, Mond, Aszendent
    planeten = [
        ("Sonne", "sonne"),
        ("Mond", "mond"),
        ("Aszendent", "aszendent"),
    ]

    abweichungen = 0
    for i, (label, key) in enumerate(planeten):
        row_y = y - row_height

        # Alternierende Hintergrundfarbe
        bg = TABLE_ROW_ALT if i % 2 == 0 else BACKGROUND
        draw_box(c, col1_x, row_y, CONTENT_WIDTH, row_height,
                 fill_color=bg, border_color=DIVIDER, border_width=0.3)

        # Label
        c.setFont(f"{FONT_FAMILY}-Bold", 13)
        c.setFillColor(TEXT_SECONDARY)
        c.drawString(col1_x + 10, row_y + 32, label)

        # Tropisch
        trop_zeichen = tropisch.get(key, {}).get("zeichen", "—")
        c.setFont(f"{FONT_FAMILY}-Bold", 15)
        c.setFillColor(TEXT_PRIMARY)
        c.drawString(col2_x + 10, row_y + 30, f"{trop_zeichen}")
        c.setFont(FONT_FAMILY, 10)
        c.setFillColor(TEXT_SECONDARY)
        trop_grad = tropisch.get(key, {}).get("grad", 0)
        c.drawString(col2_x + 10, row_y + 12, f"{trop_grad:.1f} Grad")

        # Siderisch
        sid_zeichen = siderisch.get(key, {}).get("zeichen", "—")
        ist_anders = trop_zeichen != sid_zeichen

        c.setFont(f"{FONT_FAMILY}-Bold", 15)
        c.setFillColor(GOLD if ist_anders else TEXT_PRIMARY)
        c.drawString(col3_x + 10, row_y + 30, f"{sid_zeichen}")

        c.setFont(FONT_FAMILY, 10)
        c.setFillColor(TEXT_SECONDARY)
        sid_grad = siderisch.get(key, {}).get("grad", 0)
        c.drawString(col3_x + 10, row_y + 12, f"{sid_grad:.1f} Grad")

        # Abweichungs-Marker
        if ist_anders:
            abweichungen += 1
            c.setFont(f"{FONT_FAMILY}-Bold", 10)
            c.setFillColor(WARNING)
            c.drawString(col1_x + 10, row_y + 12, "ABWEICHUNG")

        y = row_y - 5

    y -= 20

    # Abweichungs-Box
    if abweichungen > 0:
        box_h = 45
        draw_box(c, MARGIN_LEFT, y - box_h, CONTENT_WIDTH, box_h,
                 fill_color=HexColor("#1A1500"), border_color=GOLD, border_width=1.5)
        c.setFont(f"{FONT_FAMILY}-Bold", 14)
        c.setFillColor(GOLD)
        c.drawCentredString(PAGE_WIDTH / 2, y - 22,
                            f"ABWEICHUNG GEFUNDEN — {abweichungen} von 3 Zeichen stimmen nicht!")
        c.setFont(FONT_FAMILY, 10)
        c.setFillColor(TEXT_SECONDARY)
        c.drawCentredString(PAGE_WIDTH / 2, y - 38,
                            "Dein wahres kosmisches Profil unterscheidet sich vom tropischen System.")
        y -= box_h + 15

    # Ophiuchus-Check
    hat_ophiuchus = False
    for key in ["sonne", "mond", "aszendent"]:
        if siderisch.get(key, {}).get("ist_ophiuchus", False):
            hat_ophiuchus = True
            break

    if hat_ophiuchus:
        box_h = 45
        draw_box(c, MARGIN_LEFT, y - box_h, CONTENT_WIDTH, box_h,
                 fill_color=HexColor("#0A1520"), border_color=ACCENT_TEAL, border_width=1.5)
        c.setFont(f"{FONT_FAMILY}-Bold", 14)
        c.setFillColor(ACCENT_TEAL)
        c.drawCentredString(PAGE_WIDTH / 2, y - 20,
                            "DU TRÄGST DAS 13. ZEICHEN: OPHIUCHUS!")
        c.setFont(FONT_FAMILY, 10)
        c.setFillColor(TEXT_SECONDARY)
        c.drawCentredString(PAGE_WIDTH / 2, y - 38,
                            "Weniger als 7% der Menschen tragen dieses seltene Zeichen.")
        y -= box_h + 15

    # Erklärungstext
    y -= 10
    erklaerung = (
        "Die Abweichung entsteht durch die Präzession — eine langsame Verschiebung der "
        "Erdachse, die sich über 25.800 Jahre vollzieht. Seit der Festlegung des tropischen "
        "Systems hat sich der Frühlingspunkt um fast 24 Grad verschoben. Das siderische System "
        "korrigiert diese Verschiebung und zeigt dir dein astronomisch korrektes Zeichen."
    )
    y = draw_body_text(c, erklaerung, y, color=TEXT_SECONDARY, size=10)

    # Ayanamsa-Info
    ayanamsa = data.get("meta", {}).get("ayanamsa_wert", "—")
    y -= 10
    c.setFont(FONT_FAMILY, SMALL_SIZE)
    c.setFillColor(TEXT_SECONDARY)
    c.drawString(MARGIN_LEFT, y,
                 f"Lahiri-Ayanamsa: {ayanamsa} Grad (berechnet für {data['person']['geburtsdatum']})")

    # ═══════════════════════════════════════════
    # SEITE 4: DEIN PROFIL (ÜBERBLICK)
    # ═══════════════════════════════════════════
    y = new_page()

    y = draw_title(c, "DEIN KOSMISCHES PROFIL", y, size=24)
    y -= 10
    draw_gold_line(c, y)
    y -= 30

    # Info-Karten
    numerologie = data.get("numerologie", {})
    sid_sonne = siderisch.get("sonne", {}).get("zeichen", "—")
    element = data.get("element", {}).get("element", "—")
    gott = data.get("dekan", {}).get("gott", "—")
    hd_typ = data.get("human_design", {}).get("typ", "—")

    # Lebenszahl
    lz = numerologie.get("lebenszahl", "—")
    lz_text = f"{lz}"
    if numerologie.get("meisterzahl", False):
        lz_text += "  (Meisterzahl)"
    y = draw_info_card(c, y, "1-9", "Lebenszahl (Numerologie)", lz_text)

    # Siderisches Sonnenzeichen
    y = draw_info_card(c, y, "SZ", "Siderisches Sonnenzeichen", sid_sonne)

    # Element
    y = draw_info_card(c, y, "~", "Dein Element", element)

    # Ägyptischer Wächter
    y = draw_info_card(c, y, "Ka", "Ägyptischer Wächter", gott)

    # Human Design Typ
    y = draw_info_card(c, y, "HD", "Human Design Typ", hd_typ)

    # Berechnung anzeigen
    y -= 20
    berechnung = numerologie.get("berechnung", "")
    if berechnung:
        c.setFont(FONT_FAMILY, SMALL_SIZE)
        c.setFillColor(TEXT_SECONDARY)
        c.drawString(MARGIN_LEFT, y, f"Numerologie-Berechnung: {berechnung}")

    # ═══════════════════════════════════════════
    # SEITE 5–7: KURZANALYSEN
    # ═══════════════════════════════════════════
    y = new_page()

    y = draw_title(c, "DEINE ANALYSE", y, size=24)
    y -= 10
    draw_gold_line(c, y)
    y -= 25

    # Abschnitte
    analysen = _build_analysen(data)

    for i, (titel, text) in enumerate(analysen):
        # Prüfen ob genug Platz ist (min ~150pt)
        if y < CONTENT_BOTTOM + 150:
            y = new_page()
            y -= 20

        y = draw_heading(c, titel, y)
        draw_gold_line(c, y + 3, thickness=0.3)
        y -= 8
        y = draw_body_text(c, text, y)
        y -= 20

    # ═══════════════════════════════════════════
    # SEITE 8: MINI-SYNTHESE
    # ═══════════════════════════════════════════
    y = new_page()

    y = draw_title(c, "DEINE KOSMISCHE SIGNATUR", y, size=24)
    y -= 10
    draw_gold_line(c, y)
    y -= 25

    synthese = _build_synthese(data)
    y = draw_body_text(c, synthese, y)

    y -= 30
    draw_gold_line(c, y, thickness=0.3)
    y -= 20

    # Zusätzliche Reflexion
    reflexion = (
        "Diese fünf Systeme — Numerologie, siderische Astrologie, Elemente, ägyptische "
        "Dekane und Human Design — bilden zusammen dein einzigartiges kosmisches Profil. "
        "Kein anderer Mensch auf der Welt hat exakt diese Kombination. Nutze dieses Wissen "
        "als Kompass, nicht als Korsett. Dein Potenzial ist das Universum — dein Weg ist "
        "deine Entscheidung."
    )
    y = draw_body_text(c, reflexion, y, color=TEXT_SECONDARY, size=10)

    # ═══════════════════════════════════════════
    # SEITE 9: UPGRADE-ANGEBOT
    # ═══════════════════════════════════════════
    y = new_page()

    y = draw_title(c, "WILLST DU DAS VOLLE BILD?", y, size=24)
    y -= 10
    draw_gold_line(c, y)
    y -= 25

    upgrade_intro = (
        "Diese Analyse hat dir die wichtigsten Eckpunkte deines kosmischen Profils gezeigt. "
        "Doch das ist erst die Spitze des Eisbergs. Die Pro-Version geht deutlich tiefer:"
    )
    y = draw_body_text(c, upgrade_intro, y)
    y -= 15

    pro_features = [
        "Alle Planeten — nicht nur Sonne, Mond und Aszendent",
        "Alle 12 Häuser und ihre Bedeutung in deinem Chart",
        "Aspekte zwischen Planeten (Konjunktionen, Oppositionen, ...)",
        "Nakshatra — dein vedisches Mondhaus",
        "Human Design komplett: Zentren, Kanäle, Profil, Inkarnationskreuz",
        "50–60 Seiten statt 8–10",
        "Operative Protokolle und Journaling-Übungen",
    ]

    for feature in pro_features:
        if y < CONTENT_BOTTOM + 30:
            break
        c.setFont(FONT_FAMILY, BODY_SIZE)
        c.setFillColor(GOLD)
        c.drawString(MARGIN_LEFT + 10, y, "+")
        c.setFillColor(TEXT_PRIMARY)
        c.drawString(MARGIN_LEFT + 30, y, feature)
        y -= LINE_SPACING + 4

    y -= 25

    # CTA-Box
    box_h = 55
    draw_box(c, MARGIN_LEFT, y - box_h, CONTENT_WIDTH, box_h,
             fill_color=TABLE_HEADER, border_color=GOLD, border_width=2)
    c.setFont(f"{FONT_FAMILY}-Bold", 16)
    c.setFillColor(GOLD)
    c.drawCentredString(PAGE_WIDTH / 2, y - 25, "Jetzt für nur 50 EUR upgraden")
    c.setFont(FONT_FAMILY, 10)
    c.setFillColor(TEXT_SECONDARY)
    c.drawCentredString(PAGE_WIDTH / 2, y - 45, "(Kontaktdaten und Link folgen per E-Mail)")

    # ═══════════════════════════════════════════
    # SEITE 10: ABSCHLUSS
    # ═══════════════════════════════════════════
    y = new_page()

    y -= 80

    c.setFont(f"{FONT_FAMILY}-Bold", 22)
    c.setFillColor(GOLD)
    c.drawCentredString(PAGE_WIDTH / 2, y, "Danke für dein Vertrauen.")
    y -= 50

    center = PAGE_WIDTH / 2
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(center - 75, y, center + 75, y)
    y -= 40

    c.setFont(FONT_FAMILY, BODY_SIZE)
    c.setFillColor(TEXT_SECONDARY)
    lines = [
        "Diese Analyse wurde mit astronomischer Präzision erstellt.",
        "Die siderischen Positionen basieren auf dem Lahiri-Ayanamsa",
        f"und sind auf das Geburtsdatum {data['person']['geburtsdatum']} berechnet.",
        "",
        "Die Berechnungen nutzen die Swiss Ephemeris — den Goldstandard",
        "der astronomischen Positionsberechnung.",
    ]
    for line in lines:
        c.drawCentredString(PAGE_WIDTH / 2, y, line)
        y -= LINE_SPACING + 2

    y -= 30

    # Disclaimer
    draw_gold_line(c, y, thickness=0.3)
    y -= 15
    c.setFont(FONT_FAMILY, SMALL_SIZE)
    c.setFillColor(TEXT_SECONDARY)
    disclaimer_lines = [
        "DISCLAIMER: Diese Analyse dient der Selbstreflexion und persönlichen Entwicklung.",
        "Sie ersetzt keine professionelle medizinische, psychologische oder rechtliche Beratung.",
    ]
    for line in disclaimer_lines:
        c.drawCentredString(PAGE_WIDTH / 2, y, line)
        y -= 12

    y -= 30

    # Logo/Branding
    c.setFont(f"{FONT_FAMILY}-Bold", 14)
    c.setFillColor(GOLD)
    c.drawCentredString(PAGE_WIDTH / 2, y, "SYNCMASTER")
    y -= 18
    c.setFont(FONT_FAMILY, SMALL_SIZE)
    c.setFillColor(TEXT_SECONDARY)
    c.drawCentredString(PAGE_WIDTH / 2, y, "Dein kosmisches Profil — astronomisch korrekt.")

    # ═══════════════════════════════════════════
    # FERTIG
    # ═══════════════════════════════════════════
    c.save()
    logger.info("PDF generiert: %s (%d Seiten)", output_path, page_num[0])
    return output_path


# ═══════════════════════════════════════════
# Helper-Funktionen für Content
# ═══════════════════════════════════════════

def _build_analysen(data: dict) -> list[tuple[str, str]]:
    """Baut die Kurzanalysen-Abschnitte aus Content-Dateien."""
    analysen = []

    # 1. Numerologie
    numerologie = data.get("numerologie", {})
    lz = numerologie.get("lebenszahl", 0)
    content = load_content("numerologie", f"lebenszahl_{lz}")
    analysen.append((
        f"Deine Lebenszahl: {lz}",
        content["text"],
    ))

    # 2. Siderisches Sonnenzeichen
    siderisch = data.get("siderisch", {})
    zeichen = siderisch.get("sonne", {}).get("zeichen", "")
    if zeichen:
        zeichen_key = (
            zeichen.lower()
            .replace("ö", "oe")
            .replace("ü", "ue")
            .replace("ä", "ae")
        )
        content = load_content("sternzeichen", zeichen_key)
        analysen.append((
            f"Dein Zeichen: {zeichen}",
            content["text"],
        ))

    # 3. Element
    element_data = data.get("element", {})
    element = element_data.get("element", "")
    if element:
        text = (
            f"Dein Element ist {element}. "
            f"{element_data.get('eigenschaften', '')}. "
            f"Die Schattenseite: {element_data.get('schatten', '')}. "
            f"Wenn du die Stärken deines Elements bewusst lebst und die Schatten erkennst, "
            f"findest du Balance und innere Kraft."
        )
        analysen.append((f"Dein Element: {element}", text))

    # 4. Ägyptischer Wächter
    dekan = data.get("dekan", {})
    gott = dekan.get("gott", "")
    if gott:
        gott_key = (
            gott.lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("ä", "ae")
            .replace("ö", "oe")
            .replace("ü", "ue")
        )
        content = load_content("aegyptische_goetter", gott_key)
        analysen.append((
            f"Dein Ägyptischer Wächter: {gott}",
            content["text"],
        ))

    # 5. Human Design
    hd = data.get("human_design", {})
    hd_typ = hd.get("typ", "")
    if hd_typ:
        hd_key = (
            hd_typ.lower()
            .replace(" ", "_")
            .replace("ö", "oe")
            .replace("ü", "ue")
            .replace("ä", "ae")
        )
        content = load_content("human_design", hd_key)
        analysen.append((
            f"Dein Human Design Typ: {hd_typ}",
            content["text"],
        ))

    return analysen


def _build_synthese(data: dict) -> str:
    """Baut den Synthese-Text aus allen Ergebnissen."""
    numerologie = data.get("numerologie", {})
    siderisch = data.get("siderisch", {})
    element_data = data.get("element", {})
    dekan = data.get("dekan", {})
    hd = data.get("human_design", {})

    lz = numerologie.get("lebenszahl", "?")
    zeichen = siderisch.get("sonne", {}).get("zeichen", "?")
    element = element_data.get("element", "?")
    gott = dekan.get("gott", "?")
    hd_typ = hd.get("typ", "?")
    strategie = hd.get("strategie", "")

    meister = ""
    if numerologie.get("meisterzahl", False):
        meister = f" — eine Meisterzahl, die auf besonderes Potenzial hinweist"

    synthese = (
        f"Mit der Lebenszahl {lz}{meister}, dem siderischen Sonnenzeichen {zeichen} "
        f"im Element {element}, unter dem Schutz von {gott} und als {hd_typ} im Human Design "
        f"trägst du eine einzigartige kosmische Signatur. "
        f"\n\n"
        f"Deine Lebenszahl {lz} gibt dir die Richtung — sie zeigt dein Kernthema und "
        f"deinen tiefsten Antrieb. Als {zeichen} im {element}-Element bringst du die Qualitäten "
        f"mit, die diesen Antrieb in die Welt tragen. Dein ägyptischer Wächter {gott} "
        f"gibt dir ein archetypisches Werkzeug an die Hand — eine Kraft, die dich seit deiner "
        f"Geburt begleitet. "
        f"\n\n"
        f"Und als {hd_typ} im Human Design weißt du nun, WIE du diese Energie am besten "
        f"einsetzt: {strategie}."
        f"\n\n"
        f"Das ist dein kosmischer Bauplan. Nicht als Begrenzung — sondern als Landkarte "
        f"für dein vollstes Potenzial."
    )

    return synthese


# ReportLab braucht diesen Import für HexColor in der Funktion
from reportlab.lib.colors import HexColor
