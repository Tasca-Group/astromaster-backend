"""AstroMaster Backend — PDF-Generierungs-Service."""

import logging
from pathlib import Path

from app.config import settings
from utils import safe_filename
from pdf.pdf_normal import generate as generate_normal_pdf

logger = logging.getLogger(__name__)


def generate_pdf(data: dict, version: str = "normal") -> Path:
    """
    Generiert eine PDF aus den Berechnungsdaten.

    Returns:
        Pfad zur generierten PDF-Datei.
    """
    output_dir = Path(settings.PDF_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    name = data["person"]["name"]
    datum = data["person"]["geburtsdatum"].replace(".", "")
    filename = f"{safe_filename(name)}_{datum}_{version}.pdf"
    output_path = output_dir / filename

    if version == "normal":
        generate_normal_pdf(data, output_path)
    else:
        raise NotImplementedError(f"PDF-Version '{version}' noch nicht implementiert")

    logger.info("PDF generiert: %s", output_path)
    return output_path
