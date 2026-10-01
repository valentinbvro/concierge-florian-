"""Matricea de aprobare + gestionarea cererilor de aprobare.

Principiu (blueprint §7): omul aprobă tot ce e ireversibil sau costisitor.
"""
from datetime import datetime

from . import audit
from .db import SessionLocal
from .models import Approval

# acțiune -> politică: "singur" | "aprobare" | "interzis"
MATRICE = {
    "raspuns_intrebare_frecventa": "singur",
    "creare_lead": "singur",
    "creare_activitate": "singur",
    "creare_caz": "singur",
    "trimitere_oferta": "aprobare",
    "discount_peste_10": "aprobare",
    "postare_publica": "aprobare",
    "anulare_cursa": "aprobare",
    "emitere_factura": "aprobare",
    "trimitere_factura": "aprobare",
    "aprobare_investitie": "aprobare",
    "aprobare_oportunitate": "aprobare",
    "initiere_plata": "aprobare",
    "stergere_date": "interzis",
}


def politica(actiune: str) -> str:
    """Returnează politica pentru o acțiune; necunoscutele cer aprobare."""
    return MATRICE.get(actiune, "aprobare")


def cere_aprobare(tip: str, titlu: str, detalii: str, solicitat_de: str) -> Approval:
    db = SessionLocal()
    try:
        ap = Approval(tip=tip, titlu=titlu, detalii=detalii[:2000], solicitat_de=solicitat_de)
        db.add(ap)
        db.commit()
        db.refresh(ap)
        audit.inregistreaza(solicitat_de, "cerere_aprobare",
                            f"#{ap.id} {tip}: {titlu}")
        return ap
    finally:
        db.close()


def decide(aprobare_id: int, decizie: str, decident: str) -> Approval | None:
    """decizie: 'aprobat' sau 'respins'."""
    if decizie not in ("aprobat", "respins"):
        raise ValueError("decizie invalidă")
    db = SessionLocal()
    try:
        ap = db.query(Approval).get(aprobare_id)
        if not ap or ap.stare != "asteptare":
            return None
        ap.stare = decizie
        ap.decident = decident
        ap.decis_at = datetime.now()
        db.commit()
        db.refresh(ap)
        audit.inregistreaza(decident, f"aprobare_{decizie}", f"#{ap.id} {ap.tip}: {ap.titlu}")
        # Hermes: aprobare respinsă → semnal de antrenare
        if decizie == "respins":
            try:
                from . import hermes as _hermes
                _hermes.semnal("aprobare_respinsa", f"#{ap.id} {ap.tip}: {ap.titlu}"[:500],
                               {"tip": ap.tip, "aprobare_id": ap.id}, creat_de=decident)
            except Exception:
                pass
        return ap
    finally:
        db.close()


def in_asteptare():
    db = SessionLocal()
    try:
        return db.query(Approval).filter_by(stare="asteptare").order_by(Approval.id.desc()).all()
    finally:
        db.close()
