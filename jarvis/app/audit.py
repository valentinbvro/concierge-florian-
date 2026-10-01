"""Jurnal de audit append-only: orice acțiune externă a unui agent e înregistrată."""
from .db import SessionLocal
from .models import AuditLog


def inregistreaza(actor: str, actiune: str, detalii: str = "") -> int:
    db = SessionLocal()
    try:
        entry = AuditLog(actor=actor, actiune=actiune, detalii=(detalii or "")[:2000])
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry.id
    finally:
        db.close()


def ultimele(n: int = 50):
    db = SessionLocal()
    try:
        return db.query(AuditLog).order_by(AuditLog.id.desc()).limit(n).all()
    finally:
        db.close()
