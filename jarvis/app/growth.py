"""Growth & Capital Allocation (Faza 4) — Agentul 8.

Evaluare investiții (payback, ROI), scenarii de creștere proiectate din KPI-urile
reale (BI), buget lunar planificat pe categorii.
Decizia de investiție (bani reali) cere aprobare umană.
"""
from datetime import date

from . import audit, finante
from .db import SessionLocal
from .models import Buget, Investitie

CATEGORII_BUGET = ["marketing", "salarii", "combustibil", "intretinere",
                   "asigurari", "altele"]


def evalueaza_investitie(titlu: str, tip: str = "masina", cost: float = 0.0,
                         venit_lunar_estimat: float = 0.0,
                         solicitat_de: str = "valentin") -> Investitie:
    db = SessionLocal()
    try:
        inv = Investitie(titlu=titlu.strip(), tip=tip.strip() or "masina",
                         cost=float(cost or 0),
                         venit_lunar_estimat=float(venit_lunar_estimat or 0))
        db.add(inv)
        db.commit()
        db.refresh(inv)
        audit.inregistreaza(solicitat_de, "investitie_evaluata",
                            f"#{inv.id} {inv.titlu} — cost {inv.cost:.0f} EUR")
        return inv
    finally:
        db.close()


def lista_investitii(status: str | None = None):
    db = SessionLocal()
    try:
        q = db.query(Investitie).order_by(Investitie.id.desc())
        if status:
            q = q.filter_by(status=status)
        return q.limit(200).all()
    finally:
        db.close()


def analiza_investitie(inv: Investitie) -> dict:
    pb = round(inv.cost / inv.venit_lunar_estimat, 1) if inv.venit_lunar_estimat > 0 else None
    roi = (round(inv.venit_lunar_estimat * 12 / inv.cost * 100, 1)
           if inv.cost > 0 and inv.venit_lunar_estimat > 0 else None)
    verdict = "neutru"
    if pb is not None:
        verdict = "excelent" if pb <= 12 else "bun" if pb <= 24 else "slab"
    return {"id": inv.id, "titlu": inv.titlu, "tip": inv.tip, "cost": inv.cost,
            "venit_lunar_estimat": inv.venit_lunar_estimat,
            "payback_luni": pb, "roi_anual_pct": roi, "verdict": verdict,
            "status": inv.status}


def scenariu(crestere_pct: float) -> dict:
    """Proiecție: ce s-ar întâmpla cu +X% curse, pe baza cifrelor reale (BI)."""
    r = finante.rezumat()
    baza = r["facturat_luna"]
    suplimentar = round(baza * crestere_pct / 100, 2)
    return {"crestere_pct": crestere_pct,
            "facturat_luna_actual": baza,
            "facturat_luna_proiectat": round(baza + suplimentar, 2),
            "venit_suplimentar_luna": suplimentar,
            "venit_suplimentar_an": round(suplimentar * 12, 2),
            "curse_azi": r["curse_finalizate_azi"]}


def seteaza_buget(luna: str, categorie: str, planificat: float) -> Buget:
    db = SessionLocal()
    try:
        b = (db.query(Buget).filter_by(luna=luna, categorie=categorie).first()
             or Buget(luna=luna, categorie=categorie))
        b.planificat = float(planificat or 0)
        db.add(b)
        db.commit()
        db.refresh(b)
        audit.inregistreaza("valentin", "buget_setat", f"{luna} {categorie}: {b.planificat:.0f} EUR")
        return b
    finally:
        db.close()


def buget_luna(luna: str | None = None) -> dict:
    luna = luna or date.today().strftime("%Y-%m")
    db = SessionLocal()
    try:
        rows = db.query(Buget).filter_by(luna=luna).all()
        plan = {c: 0.0 for c in CATEGORII_BUGET}
        for b in rows:
            plan[b.categorie] = b.planificat
        total = round(sum(plan.values()), 2)
        venituri = finante.rezumat()["facturat_luna"]
        return {"luna": luna, "categorii": plan, "total_planificat": total,
                "venituri_facturate": venituri,
                "acoperire_pct": round(venituri / total * 100, 1) if total > 0 else None}
    finally:
        db.close()


def leaga_aprobare_investitie(investitie_id: int, approval_id: int) -> None:
    db = SessionLocal()
    try:
        inv = db.query(Investitie).get(investitie_id)
        if inv:
            inv.approval_id = approval_id
            db.commit()
    finally:
        db.close()


def marcheaza_aprobata(investitie_id: int) -> None:
    db = SessionLocal()
    try:
        inv = db.query(Investitie).get(investitie_id)
        if inv:
            inv.status = "aprobata"
            db.commit()
    finally:
        db.close()
