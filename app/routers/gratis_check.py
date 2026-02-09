"""AstroMaster Backend — Gratis-Check Endpoint."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import hash_ip, limiter
from app.models import GratisCheck
from app.schemas import GratisCheckRequest, GratisCheckResponse
from app.services.calculation import gratis_check

router = APIRouter()


@router.post("/api/gratis-check", response_model=GratisCheckResponse)
@limiter.limit("30/minute")
def do_gratis_check(
    request: Request,
    data: GratisCheckRequest,
    db: Session = Depends(get_db),
):
    """
    Schneller Vergleich: Tropisch vs. Siderisch Sonnenzeichen.
    Keine Auth, Rate-Limit 30/min/IP.
    """
    try:
        result = gratis_check(data.geburtsdatum, data.geburtszeit, data.geburtsort)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Berechnung fehlgeschlagen: {e}")

    # In DB speichern (DSGVO: IP nur als Hash)
    check = GratisCheck(
        geburtsdatum=data.geburtsdatum,
        tropisch_sonne=result["tropisch"],
        siderisch_sonne=result["siderisch"],
        abweichung=result["abweichung"],
        ip_hash=hash_ip(request),
    )
    db.add(check)
    db.commit()

    return GratisCheckResponse(**result)
