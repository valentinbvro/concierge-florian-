"""Finanțe & contabilitate (Faza 3) — facturi clienți via Pennylane.

Flux: cursă finalizată → ciornă automată (local + draft Pennylane)
      → emitere (finalizare Pennylane) DOAR cu aprobare umană
      → trimitere email (cu aprobare) → încasare → sincronizare statusuri.
Anomalii: restanțe, sume 0, duplicate, curse finalizate fără factură, sume aberante.
"""
import json
from datetime import date, datetime, timedelta

from . import audit, config
from .db import SessionLocal
from .models import Cursa, Factura, KpiSnapshot, MapareClient, Plata
from .pennylane import PennylaneClient, PennylaneError

SCADENTA_ZILE = int(getattr(config, "PENNYLANE_SCADENTA_ZILE", 0) or 30)
TVA_COTA = float(getattr(config, "TVA_DEFAULT", 0.19) or 0.19)


def _client_pennylane() -> PennylaneClient:
    return PennylaneClient()


# --- numerotare internă ---
def _numar_nou(db) -> str:
    an = date.today().year
    n = db.query(Factura).filter(Factura.numar.like(f"JF-{an}-%")).count() + 1
    return f"JF-{an}-{n:04d}"


# --- mapare clienți ---
def _mapare_client(db, nume: str, telefon: str = "") -> MapareClient:
    mp = db.query(MapareClient).filter_by(nume=nume).first()
    if mp:
        return mp
    mp = MapareClient(nume=nume, telefon=telefon)
    db.add(mp)
    db.flush()
    try:
        pl = _client_pennylane()
        rez = pl.creeaza_client(nume or "Client", telefon)
        mp.pennylane_id = str(rez.get("id", ""))
    except PennylaneError as e:
        audit.inregistreaza("finante", "eroare_client_pennylane", str(e)[:200])
    db.commit()
    db.refresh(mp)
    return mp


# --- creare factură ---
def creeaza_factura(cursa_id: int | None = None, suma: float | None = None,
                    client_nume: str = "", client_telefon: str = "",
                    eticheta: str = "", solicitat_de: str = "sistem") -> Factura:
    """Creează ciorna de factură (local + draft în Pennylane). Nu emite nimic."""
    db = SessionLocal()
    try:
        cursa = db.query(Cursa).get(cursa_id) if cursa_id else None
        if cursa:
            client_nume = client_nume or cursa.client_nume or "Client"
            client_telefon = client_telefon or cursa.client_telefon or ""
            suma = float(suma) if suma else float(cursa.pret or 0)
            eticheta = eticheta or (
                f"Cursă taxi de lux #{cursa.id}: {cursa.preluare or '—'} → "
                f"{cursa.destinatie or '—'}")
        suma = float(suma or 0)
        if suma <= 0:
            raise ValueError("suma_invalida")

        mp = _mapare_client(db, client_nume.strip() or "Client", client_telefon)
        subtotal = round(suma, 2)
        tva = round(subtotal * TVA_COTA, 2)
        total = round(subtotal + tva, 2)
        linii = [{"eticheta": eticheta or "Prestare transport taxi de lux",
                  "cantitate": 1, "pret_unitar": subtotal}]

        f = Factura(
            numar=_numar_nou(db),
            external_reference=f"jarvis-cursa-{cursa_id}" if cursa_id else f"jarvis-manual-{int(datetime.now().timestamp())}",
            cursa_id=cursa_id, client_nume=client_nume, client_telefon=client_telefon,
            linii=json.dumps(linii, ensure_ascii=False),
            subtotal=subtotal, tva=tva, total=total, status="ciorna",
            deadline=datetime.now() + timedelta(days=SCADENTA_ZILE))
        db.add(f)
        db.flush()

        try:
            pl = _client_pennylane()
            linii_pl = [{"label": l["eticheta"], "quantity": l["cantitate"], "unit": "piece",
                         "raw_currency_unit_price": f"{l['pret_unitar']:.2f}",
                         "vat_rate": config.PENNYLANE_VAT_RATE}
                        for l in linii]
            rez = pl.creeaza_ciorna(mp.pennylane_id or "0", linii_pl,
                                    referinta_externa=f.external_reference)
            f.pennylane_id = str(rez.get("id", ""))
        except PennylaneError as e:
            audit.inregistreaza("finante", "eroare_ciorna_pennylane", str(e)[:200])
        db.commit()
        db.refresh(f)
        audit.inregistreaza(solicitat_de, "factura_ciorna",
                            f"{f.numar} — {client_nume} — {total:.2f} EUR"
                            + (f" (Pennylane {f.pennylane_id})" if f.pennylane_id else " (doar local)"))
        return f
    finally:
        db.close()


# --- emitere (finalizare) ---
def finalizeaza_dupa_aprobare(factura_id: int) -> tuple[bool, str]:
    """Cheamă Pennylane finalize — doar după aprobare umană (ireversibil)."""
    db = SessionLocal()
    try:
        f = db.query(Factura).get(factura_id)
        if not f or f.status != "ciorna":
            return False, "nu_exista"
        try:
            rez = _client_pennylane().finalizeaza(f.pennylane_id or "0")
        except PennylaneError as e:
            audit.inregistreaza("finante", "eroare_finalizare", str(e)[:200])
            return False, "pennylane_eroare"
        f.status = "emisa"
        f.numar_pennylane = str(rez.get("invoice_number", ""))
        f.data_emitere = datetime.now()
        db.commit()
        audit.inregistreaza("finante", "factura_emisa",
                            f"{f.numar} → {f.numar_pennylane or '—'} ({f.total:.2f} EUR)")
        return True, f.numar_pennylane or "ok"
    finally:
        db.close()


def trimite_dupa_aprobare(factura_id: int) -> tuple[bool, str]:
    db = SessionLocal()
    try:
        f = db.query(Factura).get(factura_id)
        if not f or f.status not in ("emisa", "partial"):
            return False, "nu_exista"
        try:
            _client_pennylane().trimite_email(f.pennylane_id or "0")
        except PennylaneError as e:
            audit.inregistreaza("finante", "eroare_trimitere", str(e)[:200])
            return False, "pennylane_eroare"
        audit.inregistreaza("finante", "factura_trimisa", f"{f.numar} → {f.client_nume}")
        return True, "ok"
    finally:
        db.close()


# --- încasări ---
def marcheaza_platita(factura_id: int, suma: float, metoda: str = "",
                      referinta: str = "", solicitat_de: str = "valentin") -> tuple[bool, str]:
    db = SessionLocal()
    try:
        f = db.query(Factura).get(factura_id)
        if not f or f.status not in ("emisa", "partial"):
            return False, "nu_exista"
        platit_deja = sum(p.suma for p in db.query(Plata).filter_by(factura_id=f.id).all())
        p = Plata(factura_id=f.id, suma=round(float(suma or 0), 2),
                  metoda=metoda, referinta=referinta)
        db.add(p)
        total_platit = round(platit_deja + p.suma, 2)
        if total_platit >= f.total - 0.01:
            f.status = "platita"
            try:
                _client_pennylane().marcheaza_platita(f.pennylane_id or "0")
            except PennylaneError:
                pass
        else:
            f.status = "partial"
        db.commit()
        audit.inregistreaza(solicitat_de, "incasare",
                            f"{f.numar}: +{p.suma:.2f} EUR ({metoda or '—'}) → {f.status}")
        return True, f.status
    finally:
        db.close()


# --- interogări ---
def lista_facturi(status: str | None = None):
    db = SessionLocal()
    try:
        q = db.query(Factura).order_by(Factura.id.desc())
        if status:
            q = q.filter_by(status=status)
        return q.limit(200).all()
    finally:
        db.close()


def incasari_pe_zi(zi: date | None = None) -> float:
    zi = zi or date.today()
    db = SessionLocal()
    try:
        start = datetime.combine(zi, datetime.min.time())
        end = datetime.combine(zi, datetime.max.time())
        return sum(p.suma for p in db.query(Plata).filter(
            Plata.data >= start, Plata.data <= end).all())
    finally:
        db.close()


def facturi_restante():
    """Facturi emise/parțiale cu deadline depășit."""
    db = SessionLocal()
    try:
        acum = datetime.now()
        return (db.query(Factura)
                  .filter(Factura.status.in_(("emisa", "partial")),
                          Factura.deadline < acum)
                  .order_by(Factura.deadline).all())
    finally:
        db.close()


def detecteaza_anomalii() -> list[dict]:
    """Returnează anomalii financiare detectate (nu le persistă)."""
    anomalii = []
    db = SessionLocal()
    try:
        azi = datetime.now()
        facturi = db.query(Factura).all()
        # 1. restanțe
        for f in facturi_restante():
            zile = (azi - f.deadline).days if f.deadline else 0
            anomalii.append({
                "tip": "restanta", "severitate": "ridicata" if zile > 30 else "medie",
                "factura_id": f.id,
                "descriere": f"Factura {f.numar} ({f.client_nume}, {f.total:.2f} EUR) "
                             f"restantă de {zile} zile."})
        # 2. sume 0 / negative emise
        for f in facturi:
            if f.status in ("emisa", "partial", "platita") and f.total <= 0:
                anomalii.append({"tip": "suma_zero", "severitate": "medie",
                                 "factura_id": f.id,
                                 "descriere": f"Factura {f.numar} emisă cu total {f.total:.2f} EUR."})
        # 3. duplicate: același client + același total în 24h
        vazute = {}
        for f in sorted(facturi, key=lambda x: x.created_at or azi):
            cheie = (f.client_nume, round(f.total, 2))
            if cheie in vazute and abs(((f.created_at or azi) - vazute[cheie]).total_seconds()) < 86400:
                anomalii.append({"tip": "duplicat", "severitate": "medie",
                                 "factura_id": f.id,
                                 "descriere": f"Posibil duplicat: {f.numar} — {f.client_nume}, "
                                              f"{f.total:.2f} EUR (două facturi în 24h)."})
            else:
                vazute[cheie] = f.created_at or azi
        # 4. curse finalizate fără factură
        fara = (db.query(Cursa).outerjoin(Factura, Factura.cursa_id == Cursa.id)
                  .filter(Cursa.status == "finalizata", Cursa.pret > 0,
                          Factura.id.is_(None)).all())
        for c in fara:
            anomalii.append({"tip": "fara_factura", "severitate": "scazuta",
                             "factura_id": None,
                             "descriere": f"Cursa #{c.id} ({c.client_nume}, {c.pret:.2f} EUR) "
                                          "finalizată fără factură."})
        # 5. sume aberante (>3x media facturilor emise)
        totale = [f.total for f in facturi if f.total > 0]
        if len(totale) >= 3:
            media = sum(totale) / len(totale)
            for f in facturi:
                if f.total > 3 * media:
                    anomalii.append({"tip": "suma_aberanta", "severitate": "medie",
                                     "factura_id": f.id,
                                     "descriere": f"Factura {f.numar}: {f.total:.2f} EUR — "
                                                  f"peste 3x media ({media:.2f} EUR)."})
    finally:
        db.close()
    return anomalii


# --- BI ---
def rezumat() -> dict:
    """KPI-urile companiei — baza dashboard-ului BI."""
    db = SessionLocal()
    try:
        azi = date.today()
        prima_luna = azi.replace(day=1)
        start_luna = datetime.combine(prima_luna, datetime.min.time())
        facturi = db.query(Factura).all()
        emise_luna = [f for f in facturi
                      if f.status in ("emisa", "partial", "platita")
                      and (f.data_emitere or f.created_at) and
                      (f.data_emitere or f.created_at) >= start_luna]
        restante = facturi_restante()
        curse_fin_azi = db.query(Cursa).filter(
            Cursa.status == "finalizata",
            Cursa.data_ora >= datetime.combine(azi, datetime.min.time()),
            Cursa.data_ora <= datetime.combine(azi, datetime.max.time())).count()
        # top clienți (luna curentă)
        top: dict[str, float] = {}
        for f in emise_luna:
            top[f.client_nume or "—"] = top.get(f.client_nume or "—", 0) + f.total
        return {
            "incasari_azi": round(incasari_pe_zi(azi), 2),
            "facturat_luna": round(sum(f.total for f in emise_luna), 2),
            "facturi_emise_luna": len(emise_luna),
            "restante_nr": len(restante),
            "restante_total": round(sum(f.total for f in restante), 2),
            "curse_finalizate_azi": curse_fin_azi,
            "tva_luna": round(sum(f.tva for f in emise_luna), 2),
            "top_clienti": sorted(top.items(), key=lambda x: -x[1])[:5],
            "anomalii_nr": len(detecteaza_anomalii()),
        }
    finally:
        db.close()


def snapshot_kpi() -> dict:
    """Scrie snapshot-ul zilnic de KPI (pentru trenduri)."""
    r = rezumat()
    db = SessionLocal()
    try:
        for cheie, val in r.items():
            if isinstance(val, (int, float)):
                db.add(KpiSnapshot(cheie=cheie, valoare=float(val)))
        db.commit()
    finally:
        db.close()
    return r


def sincronizeaza() -> dict:
    """Trage statusurile facturilor din Pennylane și actualizează local."""
    db = SessionLocal()
    actualizate = 0
    erori = 0
    try:
        pl = _client_pennylane()
        facturi = (db.query(Factura)
                     .filter(Factura.status.in_(("emisa", "partial")),
                             Factura.pennylane_id != "")
                     .all())
        for f in facturi:
            try:
                d = pl.detalii(f.pennylane_id)
                status = (d.get("status") or "").lower()
                if status == "paid" and f.status != "platita":
                    f.status = "platita"
                    actualizate += 1
                elif status == "partially_paid" and f.status != "partial":
                    f.status = "partial"
                    actualizate += 1
            except PennylaneError:
                erori += 1
        db.commit()
    finally:
        db.close()
    audit.inregistreaza("finante", "sincronizare_pennylane",
                        f"{actualizate} actualizate, {erori} erori")
    return {"actualizate": actualizate, "erori": erori}
