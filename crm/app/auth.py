"""Autentificare: hash parole (PBKDF2), sesiuni, dependențe FastAPI."""
import hashlib
import os

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .db import get_db
from .models import User

SESSION_SECRET = os.environ.get("SESSION_SECRET", "dev-local-schimba-in-productie")


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return f"{salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, dk_hex = stored.split("$", 1)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"),
                                 bytes.fromhex(salt_hex), 200_000)
        return dk.hex() == dk_hex
    except (ValueError, TypeError):
        return False


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    user = db.get(User, user_id) if user_id else None
    if not user or not user.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Neautentificat")
    return user


def require_login(request: Request, db: Session = Depends(get_db)) -> User:
    """Pentru pagini HTML: redirect la /login în loc de 401."""
    user_id = request.session.get("user_id")
    user = db.get(User, user_id) if user_id else None
    if not user or not user.active:
        raise _login_redirect()
    return user


def _login_redirect() -> HTTPException:
    # HTTPException cu 307 nu face redirect automat în browser la GET /login
    # fără JS; folosim excepție custom prinsă de middleware-ul din main.
    return LoginRequired()


class LoginRequired(Exception):
    pass


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Doar administratorii au acces.")
    return user


def login_user(request: Request, user: User):
    request.session["user_id"] = user.id


def logout_user(request: Request):
    request.session.clear()


def login_redirect_response() -> RedirectResponse:
    return RedirectResponse(url="/login", status_code=303)
