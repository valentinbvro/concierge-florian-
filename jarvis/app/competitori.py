"""Market Research — evidența competitorilor și a observațiilor.

Monitorizarea automată (scraping/API) vine într-o fază ulterioară;
deocamdată: watchlist structurat + jurnal de observații.
"""
from datetime import datetime

from .db import SessionLocal
from .models import Competitor


def adauga(nume: str, website: str = "", servicii: str = "") -> Competitor:
    db = SessionLocal()
    try:
        c = Competitor(nume=nume.strip(), website=website.strip(),
                       servicii=servicii.strip())
        db.add(c)
        db.commit()
        db.refresh(c)
        return c
    finally:
        db.close()


def lista():
    db = SessionLocal()
    try:
        return db.query(Competitor).order_by(Competitor.nume).all()
    finally:
        db.close()


def adauga_observatie(cid: int, text: str) -> Competitor | None:
    db = SessionLocal()
    try:
        c = db.query(Competitor).get(cid)
        if not c:
            return None
        stamp = datetime.now().strftime("%d.%m.%Y")
        prefix = f"[{stamp}] "
        c.observatii = (c.observatii + "\n" + prefix + text.strip()).strip()
        c.ultima_verificare = datetime.now()
        db.commit()
        db.refresh(c)
        return c
    finally:
        db.close()
