"""Marketing & Media — postări cu aprobare + plan editorial simplu."""
from datetime import datetime, timedelta

from .db import SessionLocal
from .models import Postare

CANAle_VALIDE = ("instagram", "facebook", "linkedin")

# idei de postări pe 7 zile (bilingve)
_IDEI = [
    ("ro", "Prezentare serviciu: transfer aeroport premium — punctualitate și confort."),
    ("fr", "Présentation : transfert aéroport premium — ponctualité et confort."),
    ("ro", "Testimonial client: «Cea mai elegantă cursă din oraș.»"),
    ("fr", "Témoignage client : « La course la plus élégante de la ville. »"),
    ("ro", "În culise: pregătim mașinile în fiecare dimineață."),
    ("fr", "En coulisses : nous préparons les voitures chaque matin."),
    ("ro", "Ofertă corporate: transport executiv pentru echipe."),
    ("fr", "Offre corporate : transport exécutif pour vos équipes."),
    ("ro", "Destinație de weekend: evadare cu șofer privat."),
    ("fr", "Destination week-end : escapade avec chauffeur privé."),
    ("ro", "Siguranță mai întâi: șoferi verificați, mașini impecabile."),
    ("fr", "La sécurité d'abord : chauffeurs vérifiés, voitures impeccables."),
    ("ro", "Rezervă în 2 minute pe WhatsApp — răspundem imediat."),
    ("fr", "Réservez en 2 minutes sur WhatsApp — réponse immédiate."),
]


def adauga_postare(canal: str, text: str, data_programata=None) -> Postare:
    canal = (canal or "instagram").strip().lower()
    if canal not in CANAle_VALIDE:
        canal = "instagram"
    db = SessionLocal()
    try:
        p = Postare(canal=canal, text=text.strip(), data_programata=data_programata)
        db.add(p)
        db.commit()
        db.refresh(p)
        return p
    finally:
        db.close()


def lista_postari():
    db = SessionLocal()
    try:
        return db.query(Postare).order_by(Postare.id.desc()).limit(100).all()
    finally:
        db.close()


def marcheaza_aprobata(pid: int, approval_id: int) -> bool:
    db = SessionLocal()
    try:
        p = db.query(Postare).get(pid)
        if not p:
            return False
        p.status = "aprobata"
        p.approval_id = approval_id
        db.commit()
        return True
    finally:
        db.close()


def plan_editorial(lang: str = "ro", zile: int = 7) -> list[dict]:
    """Generează idei de postări pentru următoarele zile (nu le salvează)."""
    idei = [t for (l, t) in _IDEI if l == (lang if lang in ("ro", "fr") else "ro")]
    canale = ["instagram", "facebook", "linkedin"]
    plan = []
    azi = datetime.now().date()
    for i in range(min(zile, len(idei))):
        plan.append({"zi": (azi + timedelta(days=i)).strftime("%d.%m"),
                     "canal": canale[i % len(canale)],
                     "text": idei[i]})
    return plan
