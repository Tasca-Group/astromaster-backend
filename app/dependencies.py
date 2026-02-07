"""AstroMaster Backend — FastAPI Dependencies."""

import hashlib

from fastapi import Depends, Header, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)


def verify_admin_key(x_admin_key: str = Header(...)) -> str:
    """Prüft den Admin-API-Key aus dem X-Admin-Key Header."""
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Ungültiger Admin-Key")
    return x_admin_key


def hash_ip(request: Request) -> str:
    """Hasht die Client-IP mit SHA256 (DSGVO-konform)."""
    client_ip = request.client.host if request.client else "unknown"
    return hashlib.sha256(client_ip.encode()).hexdigest()
