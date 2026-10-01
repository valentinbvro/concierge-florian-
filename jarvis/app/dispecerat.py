"""Dispecerat taxi de lux — curse, șoferi, mașini, atribuire.

Tranziții de status: rezervata → confirmata → in_curs → finalizata
                     (anulare posibilă din rezervata/confirmata).
La atribuire/finalizare se pun notificări în coadă și se creează
activități în CRM (dacă se primește clientul CRM).
"""
import re
from datetime import datetime, date, time, timedelta

from . import audit, notificari
from .db import SessionLocal
from .models import Cursa, Masina, Sofer

TRANZITII = {
    "rezervata": ("confirmata", "anulata"),
    "confirmata": ("in_curs", "anulata"),
    "in_curs": ("finalizata",),
    "finalizata": (),
    "anulata": (),
}

_ALIAS_STATUS = {
    "rezervata": "rezervata", "réservée": "rezervata", "rezervată": "rezervata",
    "confirmata": "confirmata", "confirmée": "confirmata", "confirmată": "confirmata",
    "in_curs": "in_curs", "en cours": "in_curs", "în curs": "in_curs",
    "finalizata": "finalizata", "terminée": "finalizata", "finalizată": "finalizata",
    "anulata": "anulata", "annulée": "anulata", "anulată": "anulata",
}


def normalizeaza_status(text: str) -> str | None:
    return _ALIAS_STATUS.get((text or "").strip().lower())


def parse_cand(text: str) -> datetime | None:
    """'azi 14:30', 'mâine 09:00', '2026-10-02 09:00', '02.10 14:30',
    "aujourd'hui 14:30", 'demain 09:00'."""
    t = (text or "").strip().lower()
    if not t:
        return None
    m_ora = re.search(r"(\d{1,2})[:h](\d{2})", t)
    ora = (int(m_ora.group(1)), int(m_ora.group(2))) if m_ora else (9, 0)
    ziua = date.today()
    if any(c in t for c in ("mâine", "maine", "demain")):
        ziua = ziua + timedelta(days=1)
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", t)
    if m:
        ziua = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    else:
        m2 = re.search(r"(\d{1,2})\.(\d{1,2})(?:\.(\d{4}))?", t)
        if m2:
            an = int(m2.group(3)) if m2.group(3) else ziua.year
            ziua = date(an, int(m2.group(2)), int(m2.group(1)))
    return datetime.combine(ziua, time(ora[0], ora[1]))


# --- șoferi / mașini ---

def adauga_sofer(nume: str, telefon: str = "") -> Sofer:
    db = SessionLocal()
    try:
        s = Sofer(nume=nume.strip(), telefon=telefon.strip())
        db.add(s)
        db.commit()
        db.refresh(s)
        return s
    finally:
        db.close()


def adauga_masina(marca_model: str, numar: str = "", locuri: int = 4) -> Masina:
    db = SessionLocal()
    try:
        m = Masina(marca_model=marca_model.strip(), numar=numar.strip(), locuri=locuri)
        db.add(m)
        db.commit()
        db.refresh(m)
        return m
    finally:
        db.close()


def lista_soferi(active_doar=True):
    db = SessionLocal()
    try:
        q = db.query(Sofer)
        if active_doar:
            q = q.filter_by(activ=True)
        return q.order_by(Sofer.nume).all()
    finally:
        db.close()


def lista_masini(active_doar=True):
    db = SessionLocal()
    try:
        q = db.query(Masina)
        if active_doar:
            q = q.filter_by(activa=True)
        return q.order_by(Masina.marca_model).all()
    finally:
        db.close()


# --- curse ---

def creeaza_cursa(client_nume: str, client_telefon: str, preluare: str,
                  destinatie: str, cand: str, pret: float = 0.0,
                  sursa: str = "chat-intern", notite: str = "") -> Cursa:
    db = SessionLocal()
    try:
        c = Cursa(client_nume=client_nume.strip(), client_telefon=client_telefon.strip(),
                  preluare=preluare.strip(), destinatie=destinatie.strip(),
                  data_ora=parse_cand(cand), pret=float(pret or 0),
                  sursa=sursa, notite=notite.strip())
        db.add(c)
        db.commit()
        db.refresh(c)
        return c
    finally:
        db.close()


def _liber(db, model, camp_status, val_libera):
    return (db.query(model)
              .filter(getattr(model, "activ" if model is Sofer else "activa") == True)  # noqa: E712
              .filter(camp_status == val_libera)
              .order_by(model.id)
              .first())


def atribuie(cursa_id: int, sofer_id: int | None = None,
             masina_id: int | None = None, crm=None) -> tuple[bool, str]:
    """Atribuie șofer+mașină (automat dacă nu sunt precizate). Întoarce (ok, mesaj)."""
    db = SessionLocal()
    try:
        c = db.query(Cursa).get(cursa_id)
        if not c:
            return False, "nu_exista"
        if c.status not in ("rezervata", "confirmata"):
            return False, "status_nepotrivit"
        sofer = db.query(Sofer).get(sofer_id) if sofer_id else _liber(db, Sofer, Sofer.status, "liber")
        masina = db.query(Masina).get(masina_id) if masina_id else _liber(db, Masina, Masina.status, "libera")
        if not sofer or not masina:
            return False, "nimic_liber"
        if sofer.status != "liber" or masina.status != "libera":
            return False, "ocupat"
        c.sofer_id, c.masina_id = sofer.id, masina.id
        c.status = "confirmata"
        sofer.status, masina.status = "ocupat", "ocupata"
        db.commit()
        nume_sofer, marca = sofer.nume, masina.marca_model
        tel_client, tel_sofer = c.client_telefon, sofer.telefon
        preluare, destinatie = c.preluare, c.destinatie
        cid = c.id
    finally:
        db.close()
    notificari.pune_in_coada(tel_client, "whatsapp",
        f"Cursa #{cid} confirmată. Șoferul {nume_sofer} vă preia cu {marca}.", cid)
    if tel_sofer:
        notificari.pune_in_coada(tel_sofer, "whatsapp",
            f"Cursă nouă #{cid}: {preluare} → {destinatie}.", cid)
    if crm:
        try:
            crm.creeaza_activitate(subject=f"Cursă #{cid} atribuită: {nume_sofer}",
                                   tip="sarcina", description=f"Mașina: {marca}")
        except Exception:
            pass
    return True, f"{nume_sofer}|{marca}"


def schimba_status(cursa_id: int, status_nou: str, crm=None) -> tuple[bool, str]:
    db = SessionLocal()
    try:
        c = db.query(Cursa).get(cursa_id)
        if not c:
            return False, "nu_exista"
        if status_nou not in TRANZITII.get(c.status, ()):
            return False, "tranzitie_invalida"
        c.status = status_nou
        if status_nou in ("finalizata", "anulata"):
            if c.sofer_id:
                db.query(Sofer).get(c.sofer_id).status = "liber"
            if c.masina_id:
                db.query(Masina).get(c.masina_id).status = "libera"
        db.commit()
        tel, cid, vechi = c.client_telefon, c.id, c.status
        pret_final = float(c.pret or 0)
    finally:
        db.close()
    if status_nou == "in_curs" and tel:
        notificari.pune_in_coada(tel, "whatsapp",
            f"Șoferul a pornit spre dumneavoastră (cursa #{cid}).", cid)
    if status_nou == "finalizata" and pret_final > 0:
        # Faza 3: ciornă automată de factură (doar ciornă — emiterea cere aprobare)
        try:
            from . import finante
            f = finante.creeaza_factura(cursa_id=cid, solicitat_de="dispecerat")
            audit.inregistreaza("dispecerat", "factura_auto",
                                f"cursa #{cid} → ciorna {f.numar}")
        except Exception as e:
            audit.inregistreaza("dispecerat", "eroare_factura_auto", str(e)[:200])
    if crm:
        try:
            crm.creeaza_activitate(subject=f"Cursă #{cid}: {status_nou}", tip="sarcina")
        except Exception:
            pass
    return True, "ok"


def curse_pe_zi(zi: date | None = None):
    from sqlalchemy.orm import joinedload
    zi = zi or date.today()
    db = SessionLocal()
    try:
        start = datetime.combine(zi, time.min)
        end = datetime.combine(zi, time.max)
        return (db.query(Cursa)
                  .options(joinedload(Cursa.sofer), joinedload(Cursa.masina))
                  .filter(Cursa.data_ora >= start, Cursa.data_ora <= end)
                  .order_by(Cursa.data_ora).all())
    finally:
        db.close()


def rezumat_azi() -> dict:
    curse = curse_pe_zi()
    db = SessionLocal()
    try:
        liberi = db.query(Sofer).filter_by(activ=True, status="liber").count()
        masini = db.query(Masina).filter_by(activa=True, status="libera").count()
    finally:
        db.close()
    return {"curse": len(curse), "liberi": liberi, "masini": masini, "detalii": curse}
