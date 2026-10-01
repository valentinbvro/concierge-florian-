"""Risc, Conformitate & Securitate (Faza 4) — Agentul 9.

- Analiză contracte = PRE-FILTRU euristic (clauze prezente/lipsă). Nu e consultanță
  juridică și nu înlocuiește avocatul — fiecare analiză poartă disclaimerul.
- Verificări de conformitate cu scadență (ITP, asigurări, licențe șoferi…).
- Registru nereguli / incidente.

Bilingv RO/FR: clauzele se caută în ambele limbi.
"""
import json
from datetime import datetime, timedelta

from . import audit
from .db import SessionLocal
from .models import AnalizaDocument, Neregula, Verificare

DISCLAIMER = {
    "ro": ("Analiză preliminară automată — NU e consultanță juridică și NU înlocuiește "
           "avocatul. Verificați cu un jurist înainte de semnare."),
    "fr": ("Analyse préliminaire automatisée — ce N'EST PAS un conseil juridique et ne "
           "remplace PAS un avocat. Faites vérifier par un juriste avant signature."),
}

# clauză -> cuvinte-cheie (ro/fr)
CLAUZE = [
    ("obiect_contract", ["obiectul contractului", "objet du contrat"]),
    ("durata", ["durata contractului", "durée du contrat", "durata:", "durée:"]),
    ("pret_plata", ["preț", "prix", "tarif", "plata", "paiement", "facturare"]),
    ("reziliere", ["reziliere", "résiliation", "denunțare unilaterală"]),
    ("penalitati", ["penalități", "penalitate", "pénalités", "daune-interese",
                    "dommages-intérêts"]),
    ("raspundere", ["răspundere", "responsabilité", "răspunde pentru"]),
    ("forta_majora", ["forță majoră", "force majeure"]),
    ("confidentialitate", ["confidențialitate", "confidentialité"]),
    ("date_personale", ["date cu caracter personal", "données personnelles", "GDPR", "RGPD"]),
    ("litigii", ["litigii", "litiges", "instanța competentă", "tribunal compétent",
                 "arbitraj", "arbitrage"]),
]

ETICHETE_CLAUZE = {
    "obiect_contract": ("Obiectul contractului", "Objet du contrat"),
    "durata": ("Durata", "Durée"),
    "pret_plata": ("Preț / plată", "Prix / paiement"),
    "reziliere": ("Reziliere", "Résiliation"),
    "penalitati": ("Penalități", "Pénalités"),
    "raspundere": ("Răspundere", "Responsabilité"),
    "forta_majora": ("Forță majoră", "Force majeure"),
    "confidentialitate": ("Confidențialitate", "Confidentialité"),
    "date_personale": ("Date personale / GDPR", "Données personnelles / RGPD"),
    "litigii": ("Litigii / instanță", "Litiges / tribunal"),
}


def analizeaza_contract(nume: str, text: str, lang: str = "ro",
                        solicitat_de: str = "valentin") -> AnalizaDocument:
    t = (text or "").lower()
    gasite, lipsa = [], []
    for cheie, cuvinte in CLAUZE:
        et = ETICHETE_CLAUZE[cheie][0 if lang == "ro" else 1]
        (gasite if any(c in t for c in cuvinte) else lipsa).append(et)
    scor_risc = round(len(lipsa) / len(CLAUZE) * 10, 1)  # 0-10, mai mare = mai riscant
    concluzii = {"clauze_gasite": gasite, "clauze_lipsa": lipsa,
                 "scor_risc": scor_risc,
                 "disclaimer": DISCLAIMER.get(lang, DISCLAIMER["ro"])}
    db = SessionLocal()
    try:
        a = AnalizaDocument(nume=nume[:255], concluzii=json.dumps(concluzii, ensure_ascii=False))
        db.add(a)
        db.commit()
        db.refresh(a)
        audit.inregistreaza(solicitat_de, "contract_analizat",
                            f"#{a.id} {nume[:60]} — risc {scor_risc}/10")
        return a
    finally:
        db.close()


def lista_analize():
    db = SessionLocal()
    try:
        return db.query(AnalizaDocument).order_by(AnalizaDocument.id.desc()).limit(50).all()
    finally:
        db.close()


# --- conformitate ---
def adauga_verificare(tip: str, referinta: str, expira_la: str,
                      notite: str = "", solicitat_de: str = "valentin") -> Verificare:
    try:
        dt = datetime.fromisoformat(expira_la)
    except (ValueError, TypeError):
        raise ValueError("data_invalida")
    db = SessionLocal()
    try:
        v = Verificare(tip=tip.strip(), referinta=referinta.strip(),
                       expira_la=dt, notite=notite.strip())
        v.status = _status_verificare(v)
        db.add(v)
        db.commit()
        db.refresh(v)
        audit.inregistreaza(solicitat_de, "verificare_noua",
                            f"#{v.id} {v.tip} {v.referinta} → {expira_la}")
        return v
    finally:
        db.close()


def _status_verificare(v: Verificare) -> str:
    if not v.expira_la:
        return "valida"
    zile = (v.expira_la - datetime.now()).days
    if zile < 0:
        return "expirata"
    return "expira_curand" if zile <= 30 else "valida"


def lista_verificari():
    db = SessionLocal()
    try:
        vs = db.query(Verificare).order_by(Verificare.expira_la).all()
        for v in vs:
            nou = _status_verificare(v)
            if nou != v.status:
                v.status = nou
        db.commit()
        # reîncarcă atributele înainte de detach, altfel DetachedInstanceError
        for v in vs:
            db.refresh(v)
        db.expunge_all()
        return vs
    finally:
        db.close()


def verificari_urgente(zile: int = 30):
    return [v for v in lista_verificari() if v.status in ("expirata", "expira_curand")]


# --- nereguli ---
def semnaleaza(titlu: str, descriere: str = "", severitate: str = "medie",
               solicitat_de: str = "valentin") -> Neregula:
    db = SessionLocal()
    try:
        n = Neregula(titlu=titlu.strip(), descriere=descriere.strip(),
                     severitate=severitate if severitate in ("scazuta", "medie", "ridicata")
                     else "medie")
        db.add(n)
        db.commit()
        db.refresh(n)
        audit.inregistreaza(solicitat_de, "neregula_semnalata",
                            f"#{n.id} [{n.severitate}] {n.titlu[:80]}")
        return n
    finally:
        db.close()


def lista_nereguli(status: str | None = None):
    db = SessionLocal()
    try:
        q = db.query(Neregula).order_by(Neregula.id.desc())
        if status:
            q = q.filter_by(status=status)
        return q.limit(200).all()
    finally:
        db.close()


def rezolva_neregula(neregula_id: int) -> Neregula | None:
    db = SessionLocal()
    try:
        n = db.query(Neregula).get(neregula_id)
        if n:
            n.status = "rezolvata"
            db.commit()
            db.refresh(n)
        return n
    finally:
        db.close()
