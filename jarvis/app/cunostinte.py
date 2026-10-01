"""Baza de cunoștințe Q&A pentru customer service.

Căutare pe potrivire de cuvinte-cheie (fără LLM în Faza 1); când vine LLM-ul,
acest modul devine retriever-ul pentru RAG.
"""
import re

from .db import SessionLocal
from .models import KnowledgeItem

_STOP = {"ce", "care", "cum", "cat", "cât", "sunt", "este", "e", "si", "și", "sau",
         "pentru", "din", "cu", "un", "o", "la", "de", "in", "în", "a", "se", "va",
         "mai", "foarte", "imi", "îmi", "ma", "mă", "te", "ne", "va rog", "vă rog"}


def _cuvinte(text: str) -> set[str]:
    return {c for c in re.findall(r"[a-zăâîșț]{3,}", text.lower()) if c not in _STOP}


def adauga(intrebare: str, raspuns: str, etichete: str = "") -> KnowledgeItem:
    db = SessionLocal()
    try:
        it = KnowledgeItem(intrebare=intrebare.strip(), raspuns=raspuns.strip(),
                           etichete=etichete.strip())
        db.add(it)
        db.commit()
        db.refresh(it)
        return it
    finally:
        db.close()


def lista():
    db = SessionLocal()
    try:
        return db.query(KnowledgeItem).filter_by(activa=True).order_by(KnowledgeItem.id.desc()).all()
    finally:
        db.close()


def cauta(intrebare: str, prag: int = 2) -> KnowledgeItem | None:
    """Întoarce cel mai bun răspuns dacă scorul trece pragul, altfel None."""
    q = _cuvinte(intrebare)
    if not q:
        return None
    db = SessionLocal()
    try:
        items = db.query(KnowledgeItem).filter_by(activa=True).all()
        cel_mai_bun, scor_max = None, 0
        for it in items:
            scor = len(q & _cuvinte(it.intrebare + " " + it.etichete))
            # bonus dacă întrebarea conține cuvinte din răspuns
            if scor > scor_max:
                scor_max, cel_mai_bun = scor, it
        if cel_mai_bun and scor_max >= prag:
            # atașăm scorul fără a-l persista
            cel_mai_bun._scor = scor_max
            db.expunge(cel_mai_bun)
            return cel_mai_bun
        return None
    finally:
        db.close()
