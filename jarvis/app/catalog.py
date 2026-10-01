"""Catalog de produse/servicii — baza pentru ofertare."""
from .db import SessionLocal
from .models import Produs


def adauga(nume: str, pret: float, sku: str = "", descriere: str = "",
           moneda: str = "EUR") -> Produs:
    db = SessionLocal()
    try:
        p = Produs(nume=nume.strip(), pret=float(pret), sku=sku.strip(),
                   descriere=descriere.strip(), moneda=moneda)
        db.add(p)
        db.commit()
        db.refresh(p)
        return p
    finally:
        db.close()


def lista(active_doar: bool = True):
    db = SessionLocal()
    try:
        q = db.query(Produs)
        if active_doar:
            q = q.filter_by(activ=True)
        return q.order_by(Produs.nume).all()
    finally:
        db.close()


def gaseste(referinta: str) -> Produs | None:
    """Caută produs după nume sau SKU (case-insensitive, parțial)."""
    db = SessionLocal()
    try:
        ref = (referinta or "").strip().lower()
        for p in db.query(Produs).filter_by(activ=True).all():
            if ref in p.nume.lower() or (p.sku and ref == p.sku.lower()):
                return p
        return None
    finally:
        db.close()


def dezactiveaza(pid: int) -> bool:
    db = SessionLocal()
    try:
        p = db.query(Produs).get(pid)
        if not p:
            return False
        p.activ = False
        db.commit()
        return True
    finally:
        db.close()
