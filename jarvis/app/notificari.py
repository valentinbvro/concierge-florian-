"""Coada de notificări — ce ar trebui trimis clienților/șoferilor.

Trimiterea efectivă se face la conectarea canalelor (Faza 1: GHID_CANALE.md).
Până atunci, notificările stau în coadă și sunt vizibile în Dispecerat.
"""
from .db import SessionLocal
from .models import Notificare


def pune_in_coada(destinatar: str, canal: str, text: str,
                  cursa_id: int | None = None) -> Notificare | None:
    if not destinatar:
        return None
    db = SessionLocal()
    try:
        n = Notificare(destinatar=destinatar.strip(), canal=canal,
                       text=text.strip(), cursa_id=cursa_id)
        db.add(n)
        db.commit()
        db.refresh(n)
        return n
    finally:
        db.close()


def in_asteptare():
    db = SessionLocal()
    try:
        return (db.query(Notificare).filter_by(status="in_asteptare")
                  .order_by(Notificare.id.desc()).limit(100).all())
    finally:
        db.close()


def marcheaza_trimisa(nid: int) -> bool:
    db = SessionLocal()
    try:
        n = db.query(Notificare).get(nid)
        if not n:
            return False
        n.status = "trimisa"
        db.commit()
        return True
    finally:
        db.close()
