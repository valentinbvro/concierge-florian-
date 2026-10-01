"""Hermes — agentul de antrenare și învățare continuă al lui Jarvis.

Rol: transformă ce se întâmplă în operarea zilnică (întrebări fără răspuns,
aprobări respinse, erori) în îmbunătățiri concrete, propuse omului spre aprobare.

Bucla de învățare:
  1. semnale — evenimente brute culese automat (hook-uri în orchestrator/aprobări);
  2. analiză — `analizeaza()` grupează semnalele și generează sugestii;
  3. omul aprobă/respinge sugestia și completează răspunsul propus;
  4. aplicare — sugestia aprobată intră în baza de cunoștințe / instrucțiuni.

Nicio învățare nu se aplică singură: sugestiile trec prin om (buton sau chat).
"""
import json
from datetime import datetime

from . import audit
from .db import SessionLocal
from .models import SemnalAntrenare, SugestieInvatare, InstructiuneAgent

TIPURI_SEMNAL = ("intrebare_fara_raspuns", "aprobare_respinsa", "eroare_agent",
                 "corectie_utilizator")
TIPURI_SUGESTIE = ("cunostinta_noua", "ajustare_prag", "imbunatatire_raspuns")


def semnal(tip: str, continut: str, meta: dict | None = None,
           creat_de: str = "sistem") -> SemnalAntrenare:
    """Înregistrează un semnal brut de antrenare."""
    if tip not in TIPURI_SEMNAL:
        tip = "corectie_utilizator"
    db = SessionLocal()
    try:
        s = SemnalAntrenare(tip=tip, continut=(continut or "")[:2000],
                            meta=json.dumps(meta or {}, ensure_ascii=False),
                            creat_de=creat_de)
        db.add(s)
        db.commit()
        db.refresh(s)
        db.expunge(s)
        return s
    finally:
        db.close()


def _detalii(sug: SugestieInvatare) -> dict:
    try:
        return json.loads(sug.detalii or "{}")
    except Exception:
        return {}


def analizeaza() -> dict:
    """Procesează semnalele neprocesate și generează sugestii. Idempotent."""
    from . import cunostinte
    db = SessionLocal()
    stats = {"semnale_procesate": 0, "sugestii_create": 0}
    try:
        semnale = (db.query(SemnalAntrenare)
                     .filter(SemnalAntrenare.procesat == False)  # noqa: E712
                     .order_by(SemnalAntrenare.id).all())
        for s in semnale:
            creat = 0
            if s.tip == "intrebare_fara_raspuns":
                intreb = s.continut.strip()
                if intreb and not cunostinte.cauta(intreb):
                    # evită duplicatele
                    exista = (db.query(SugestieInvatare)
                                .filter(SugestieInvatare.tip == "cunostinta_noua",
                                        SugestieInvatare.titlu == intreb[:280],
                                        SugestieInvatare.status.in_(["propusa", "aprobata"]))
                                .count())
                    if not exista:
                        db.add(SugestieInvatare(
                            tip="cunostinta_noua", titlu=intreb[:280],
                            detalii=json.dumps({"intrebare": intreb,
                                                "raspuns_propus": ""},
                                               ensure_ascii=False),
                            semnal_id=s.id))
                        creat = 1
            elif s.tip == "aprobare_respinsa":
                try:
                    meta = json.loads(s.meta or "{}")
                except Exception:
                    meta = {}
                tip_ap = meta.get("tip", "necunoscut")
                exista = (db.query(SugestieInvatare)
                            .filter(SugestieInvatare.tip == "ajustare_prag",
                                    SugestieInvatare.status.in_(["propusa", "aprobata"]))
                            .count())
                if not exista:
                    db.add(SugestieInvatare(
                        tip="ajustare_prag",
                        titlu=f"Revizuiește criteriile pentru «{tip_ap}»",
                        detalii=json.dumps(
                            {"observatie": f"O cerere de tip «{tip_ap}» a fost respinsă: {s.continut[:200]}. "
                                          "Verifică dacă pragurile sau descrierea din matricea de aprobare "
                                          "trebuie ajustate.",
                             "tip_aprobare": tip_ap}, ensure_ascii=False),
                        semnal_id=s.id))
                    creat = 1
            s.procesat = True
            stats["semnale_procesate"] += 1
            stats["sugestii_create"] += creat
        db.commit()
    finally:
        db.close()
    if stats["semnale_procesate"]:
        audit.inregistreaza("hermes", "analiza",
                            f"{stats['semnale_procesate']} semnale → "
                            f"{stats['sugestii_create']} sugestii")
    return stats


def lista_sugestii(status: str | None = None):
    db = SessionLocal()
    try:
        q = db.query(SugestieInvatare).order_by(SugestieInvatare.id.desc())
        if status:
            q = q.filter(SugestieInvatare.status == status)
        return q.all()
    finally:
        db.close()


def decide_sugestie(sugestie_id: int, decizie: str,
                    decident: str = "valentin") -> SugestieInvatare | None:
    """Aprobă sau respinge o sugestie (omul decide)."""
    if decizie not in ("aprobata", "respinsa"):
        raise ValueError("decizie invalida")
    db = SessionLocal()
    try:
        s = db.query(SugestieInvatare).get(sugestie_id)
        if not s or s.status != "propusa":
            return None
        s.status = decizie
        s.decis_de = decident
        db.commit()
        db.refresh(s)
        db.expunge(s)
        audit.inregistreaza(decident, f"sugestie_{decizie}", f"#{s.id} {s.titlu[:120]}")
        return s
    finally:
        db.close()


def completeaza_raspuns(sugestie_id: int, raspuns: str) -> SugestieInvatare | None:
    """Omul completează/ajustează răspunsul propus de Hermes."""
    db = SessionLocal()
    try:
        s = db.query(SugestieInvatare).get(sugestie_id)
        if not s or s.tip != "cunostinta_noua":
            return None
        d = _detalii(s)
        d["raspuns_propus"] = raspuns
        s.detalii = json.dumps(d, ensure_ascii=False)
        db.commit()
        db.refresh(s)
        db.expunge(s)
        return s
    finally:
        db.close()


def aplica_sugestie(sugestie_id: int) -> tuple[bool, str]:
    """Aplică o sugestie aprobată (doar omul o declanșează)."""
    from . import cunostinte
    db = SessionLocal()
    try:
        s = db.query(SugestieInvatare).get(sugestie_id)
        if not s:
            return False, "nu_exista"
        if s.status != "aprobata":
            return False, "neaprobata"
        d = _detalii(s)
        if s.tip == "cunostinta_noua":
            intrebare = d.get("intrebare", "").strip()
            raspuns = d.get("raspuns_propus", "").strip()
            if not intrebare or not raspuns:
                return False, "raspuns_lipsa"
            cunostinte.adauga(intrebare, raspuns, etichete="hermes")
        s.status = "aplicata"
        db.commit()
        audit.inregistreaza("hermes", "sugestie_aplicata", f"#{s.id} {s.titlu[:120]}")
        return True, "aplicata"
    finally:
        db.close()


def seteaza_instructiune(agent: str, text: str,
                         creat_de: str = "valentin") -> InstructiuneAgent:
    """Salvează o nouă versiune a instrucțiunilor unui agent (antrenare continuă)."""
    db = SessionLocal()
    try:
        ultima = (db.query(InstructiuneAgent)
                    .filter(InstructiuneAgent.agent == agent)
                    .order_by(InstructiuneAgent.versiune.desc()).first())
        v = (ultima.versiune + 1) if ultima else 1
        db.query(InstructiuneAgent).filter(
            InstructiuneAgent.agent == agent).update({"activa": False})
        inst = InstructiuneAgent(agent=agent, versiune=v, text=text,
                                activa=True, creat_de=creat_de)
        db.add(inst)
        db.commit()
        db.refresh(inst)
        db.expunge(inst)
        audit.inregistreaza(creat_de, "instructiune_noua", f"{agent} v{v}")
        return inst
    finally:
        db.close()


def instructiune_curenta(agent: str) -> InstructiuneAgent | None:
    db = SessionLocal()
    try:
        return (db.query(InstructiuneAgent)
                  .filter(InstructiuneAgent.agent == agent,
                          InstructiuneAgent.activa == True)  # noqa: E712
                  .order_by(InstructiuneAgent.versiune.desc()).first())
    finally:
        db.close()


def istoric_instructiuni(agent: str | None = None):
    db = SessionLocal()
    try:
        q = db.query(InstructiuneAgent).order_by(InstructiuneAgent.id.desc())
        if agent:
            q = q.filter(InstructiuneAgent.agent == agent)
        return q.limit(20).all()
    finally:
        db.close()


def raport() -> dict:
    """Starea învățării continue — pentru pagină și BI."""
    db = SessionLocal()
    try:
        from sqlalchemy import func
        semnale = dict(db.query(SemnalAntrenare.tip, func.count(SemnalAntrenare.id))
                         .group_by(SemnalAntrenare.tip).all())
        neprocesate = (db.query(SemnalAntrenare)
                         .filter(SemnalAntrenare.procesat == False)  # noqa: E712
                         .count())
        sugestii = dict(db.query(SugestieInvatare.status, func.count(SugestieInvatare.id))
                          .group_by(SugestieInvatare.status).all())
        invatate = (db.query(SugestieInvatare)
                      .filter(SugestieInvatare.status == "aplicata").count())
        return {"semnale_pe_tip": semnale, "semnale_neprocesate": neprocesate,
                "sugestii_pe_status": sugestii, "cunostinte_invatate": invatate,
                "instructiuni_active": db.query(InstructiuneAgent)
                                         .filter(InstructiuneAgent.activa == True)  # noqa: E712
                                         .count()}
    finally:
        db.close()
