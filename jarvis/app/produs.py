"""Produs & Inovație (Faza 4) — Agentul 7.

Bancă de idei + fișe de oportunitate cu estimări (investiție, venit lunar,
payback). Ideile mature pot fi promovate la oportunități.
"""
from datetime import datetime

from . import audit
from .db import SessionLocal
from .models import Idee, Oportunitate


def adauga_idee(titlu: str, descriere: str = "", categorie: str = "serviciu",
                solicitat_de: str = "valentin") -> Idee:
    db = SessionLocal()
    try:
        i = Idee(titlu=titlu.strip(), descriere=descriere.strip(),
                 categorie=categorie.strip() or "serviciu")
        db.add(i)
        db.commit()
        db.refresh(i)
        audit.inregistreaza(solicitat_de, "idee_noua", f"#{i.id} {i.titlu}")
        return i
    finally:
        db.close()


def lista_idei(status: str | None = None):
    db = SessionLocal()
    try:
        q = db.query(Idee).order_by(Idee.scor.desc(), Idee.id.desc())
        if status:
            q = q.filter_by(status=status)
        return q.limit(200).all()
    finally:
        db.close()


def voteaza_idee(idee_id: int, scor: int) -> Idee | None:
    db = SessionLocal()
    try:
        i = db.query(Idee).get(idee_id)
        if not i:
            return None
        i.scor = max(0, min(10, int(scor)))
        db.commit()
        db.refresh(i)
        return i
    finally:
        db.close()


def _payback_luni(investitie: float, venit_lunar: float) -> float | None:
    if venit_lunar and venit_lunar > 0:
        return round(investitie / venit_lunar, 1)
    return None


def creeaza_oportunitate(titlu: str, descriere: str = "",
                         investitie_estimata: float = 0.0,
                         venit_lunar_estimat: float = 0.0,
                         idee_id: int | None = None,
                         solicitat_de: str = "valentin") -> Oportunitate:
    db = SessionLocal()
    try:
        o = Oportunitate(titlu=titlu.strip(), descriere=descriere.strip(),
                         investitie_estimata=float(investitie_estimata or 0),
                         venit_lunar_estimat=float(venit_lunar_estimat or 0),
                         idee_id=idee_id)
        db.add(o)
        db.flush()
        if idee_id:
            idee = db.query(Idee).get(idee_id)
            if idee:
                idee.status = "oportunitate"
        db.commit()
        db.refresh(o)
        audit.inregistreaza(solicitat_de, "oportunitate_noua",
                            f"#{o.id} {o.titlu} — inv. {o.investitie_estimata:.0f} EUR")
        return o
    finally:
        db.close()


def promoveaza_idee(idee_id: int, investitie: float = 0.0, venit_lunar: float = 0.0,
                    solicitat_de: str = "valentin") -> Oportunitate | None:
    db = SessionLocal()
    try:
        i = db.query(Idee).get(idee_id)
        titlu, descriere = (i.titlu, i.descriere) if i else ("", "")
    finally:
        db.close()
    if not titlu:
        return None
    return creeaza_oportunitate(titlu, descriere, investitie, venit_lunar,
                                idee_id=idee_id, solicitat_de=solicitat_de)


def lista_oportunitati(status: str | None = None):
    db = SessionLocal()
    try:
        q = db.query(Oportunitate).order_by(Oportunitate.id.desc())
        if status:
            q = q.filter_by(status=status)
        return q.limit(200).all()
    finally:
        db.close()


def fisa_oportunitate(o: Oportunitate) -> dict:
    pb = _payback_luni(o.investitie_estimata, o.venit_lunar_estimat)
    roi_anual = (round(o.venit_lunar_estimat * 12 / o.investitie_estimata * 100, 1)
                 if o.investitie_estimata > 0 and o.venit_lunar_estimat > 0 else None)
    return {"id": o.id, "titlu": o.titlu, "descriere": o.descriere,
            "investitie_estimata": o.investitie_estimata,
            "venit_lunar_estimat": o.venit_lunar_estimat,
            "payback_luni": pb, "roi_anual_pct": roi_anual, "status": o.status}


def leaga_aprobare_oportunitate(oportunitate_id: int, approval_id: int) -> None:
    db = SessionLocal()
    try:
        o = db.query(Oportunitate).get(oportunitate_id)
        if o:
            o.approval_id = approval_id
            db.commit()
    finally:
        db.close()


def marcheaza_aprobata(oportunitate_id: int) -> None:
    db = SessionLocal()
    try:
        o = db.query(Oportunitate).get(oportunitate_id)
        if o:
            o.status = "aprobata"
            db.commit()
    finally:
        db.close()
