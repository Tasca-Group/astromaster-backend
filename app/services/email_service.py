"""AstroMaster Backend — Email-Service via Brevo (SendinBlue)."""

import base64
import logging
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


def send_pdf_email(email: str, name: str, pdf_path: Path) -> bool:
    """
    Sendet die generierte PDF per Email via Brevo API.

    Returns:
        True wenn erfolgreich, False bei Fehler.
    """
    if not settings.BREVO_API_KEY:
        logger.warning("BREVO_API_KEY nicht gesetzt — Email wird übersprungen")
        return False

    try:
        import sib_api_v3_sdk
        from sib_api_v3_sdk.rest import ApiException

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = settings.BREVO_API_KEY
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(configuration)
        )

        # PDF als Base64 Attachment
        with open(pdf_path, "rb") as f:
            pdf_content = base64.b64encode(f.read()).decode("utf-8")

        send_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": email, "name": name}],
            sender={"email": "analyse@astro-masters.com", "name": "AstroMasters"},
            subject="Deine kosmische Analyse ist fertig!",
            html_content=f"""
            <html>
            <body style="font-family: Arial, sans-serif; background: #0A0F14; color: #E8E8E8; padding: 40px;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #C9A961;">Hallo {name},</h1>
                    <p>deine persoenliche kosmische Analyse ist fertig!</p>
                    <p>Im Anhang findest du deine PDF mit allen Ergebnissen:</p>
                    <ul>
                        <li>Siderische Astrologie (Lahiri-Ayanamsa)</li>
                        <li>System-Check: Tropisch vs. Siderisch</li>
                        <li>Numerologie & Lebenszahl</li>
                        <li>Aegyptische Dekane</li>
                        <li>Human Design Typ</li>
                    </ul>
                    <p style="color: #C9A961;">Viel Freude beim Entdecken!</p>
                    <p style="color: #999; font-size: 12px; margin-top: 40px;">
                        AstroMasters | astro-masters.com
                    </p>
                </div>
            </body>
            </html>
            """,
            attachment=[{
                "content": pdf_content,
                "name": pdf_path.name,
            }],
        )

        api_instance.send_transac_email(send_email)
        logger.info("Email gesendet an %s", email)
        return True

    except Exception as e:
        logger.error("Email-Versand fehlgeschlagen: %s", e)
        return False
