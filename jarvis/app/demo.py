"""Mod demonstrativ — date fictive, clar marcate, pentru prezentări către client.

Valentin (dezvoltatorul) nu are acces la datele reale ale firmei, așa că Jarvis
poate fi populat cu un set de date demonstrative realiste (Paris, EUR), vizibile
în toate paginile și într-un bord dedicat `/demo` în stilul planșelor LUNA.

Toate rândurile create de seed poartă `demo=1` și pot fi șterse integral cu
`sterge_demo()`, fără a afecta datele reale (demo=0).
"""
from datetime import datetime, timedelta

from sqlalchemy import text

from .db import SessionLocal, engine
from .models import (Sofer, Masina, Cursa, Notificare, Postare, Competitor,
                     Factura, Plata, Idee, Oportunitate, Investitie, Buget,
                     Verificare, Neregula, AnalizaDocument, Campanie, KpiSnapshot)
from . import audit

TABELE_DEMO = [
    ("soferi", Sofer), ("masini", Masina), ("curse", Cursa),
    ("notificari", Notificare), ("postari", Postare), ("competitori", Competitor),
    ("facturi", Factura), ("plati", Plata), ("idei", Idee),
    ("oportunitati", Oportunitate), ("investitii", Investitie), ("bugete", Buget),
    ("verificari", Verificare), ("nereguli", Neregula),
    ("analize_documente", AnalizaDocument), ("campanii", Campanie),
    ("kpi_snapshots", KpiSnapshot),
]


def asigura_coloane_demo():
    """Migrare ușoară: adaugă coloana `demo` tabelelor existente (dacă lipsește)."""
    with engine.begin() as conn:
        for nume, _ in TABELE_DEMO:
            try:
                conn.execute(text(f"ALTER TABLE {nume} ADD COLUMN demo INTEGER DEFAULT 0"))
            except Exception as e:
                if "duplicate column" not in str(e).lower():
                    raise


def _repere_id(db) -> dict:
    """Max(id) per tabelă înainte de seed — tot ce apare peste e creat de seed."""
    from sqlalchemy import func
    rep = {}
    for nume, model in TABELE_DEMO:
        try:
            rep[nume] = db.query(func.max(model.id)).scalar() or 0
        except Exception:
            db.rollback()
            rep[nume] = 0
    return rep


def _marcheaza_noi_ca_demo(db, repere: dict):
    """Marchează demo=1 exact rândurile create după repere."""
    for nume, model in TABELE_DEMO:
        try:
            db.query(model).filter(model.id > repere.get(nume, 0)).update(
                {"demo": 1}, synchronize_session=False)
        except Exception:
            db.rollback()


def demo_activ() -> bool:
    db = SessionLocal()
    try:
        for _, model in TABELE_DEMO:
            try:
                if db.query(model).filter(model.demo == 1).count():
                    return True
            except Exception:
                continue
        return False
    finally:
        db.close()


def sterge_demo() -> dict:
    """Șterge integral rândurile demonstrative. Întoarce numărul de rânduri șterse."""
    db = SessionLocal()
    sterse = {}
    try:
        # întâi copiii (FK), apoi părinții
        ordine = ["plati", "notificari", "analize_documente", "facturi", "curse",
                  "soferi", "masini", "postari", "competitori", "idei",
                  "oportunitati", "investitii", "bugete", "verificari",
                  "nereguli", "campanii", "kpi_snapshots"]
        modele = {n: m for n, m in TABELE_DEMO}
        for nume in ordine:
            model = modele[nume]
            n = db.query(model).filter(model.demo == 1).delete(
                synchronize_session=False)
            sterse[nume] = n
        db.commit()
    finally:
        db.close()
    audit.inregistreaza("demo", "sterge_demo",
                        f"șterse {sum(sterse.values())} rânduri demonstrative")
    return sterse


def seed_demo() -> dict:
    """Populează Jarvis cu date demonstrative (Paris, EUR). Idempotent."""
    if demo_activ():
        return {"deja_activ": True}
    from . import dispecerat, finante, marketing, competitori, produs, growth, risc

    db0 = SessionLocal()
    try:
        repere = _repere_id(db0)
    finally:
        db0.close()

    acum = datetime.now()
    rez = {}

    # --- șoferi & mașini ---
    soferi = {}
    for nume, tel in [("Thomas", "+33611223344"), ("Alexandre", "+33622334455"),
                      ("Mihai", "+33633445566"), ("Karim", "+33644556677"),
                      ("Sophie", "+33655667788")]:
        s = dispecerat.adauga_sofer(nume, tel)
        soferi[nume] = s.id
    masini = {}
    for marca, numar, locuri in [("Mercedes E-Class", "AB-123-CD", 4),
                                 ("Mercedes S-Class", "EF-456-GH", 4),
                                 ("Mercedes V-Class", "IJ-789-KL", 7),
                                 ("Mercedes Sprinter", "MN-012-OP", 8)]:
        m = dispecerat.adauga_masina(marca, numar, locuri)
        masini[marca] = m.id
    rez["soferi"], rez["masini"] = len(soferi), len(masini)

    # --- curse ---
    curse = [
        # client, telefon, preluare, destinatie, data, pret, sofer, masina, status final
        ("Mr. Dupont", "+33711111111", "CDG Terminal 2E", "Paris 8e", "2026-09-28 08:00",
         145, "Thomas", "Mercedes E-Class", "finalizata"),
        ("Travel Agency", "+33122223333", "Paris 1er", "Versailles", "2026-09-28 10:30",
         180, "Karim", "Mercedes S-Class", "finalizata"),
        ("Mrs. Green", "+447111222333", "ORY Terminal 4", "Paris 7e", "2026-09-29 12:00",
         120, "Sophie", "Mercedes V-Class", "finalizata"),
        ("Société Lumière", "+33133334444", "Paris 9e", "La Défense", "2026-09-29 14:00",
         95, "Alexandre", "Mercedes Sprinter", "finalizata"),
        ("VIP Client", "+33699998888", "CDG Terminal 2E", "Hôtel Ritz, Paris",
         "2026-09-30 09:00", 220, "Thomas", "Mercedes S-Class", "finalizata"),
        ("Mr. Smith", "+12125550123", "Paris 6e", "Disneyland Paris", "2026-09-30 18:00",
         160, "Mihai", "Mercedes E-Class", "finalizata"),
        ("Ms. Laurent", "+33677776666", "CDG Terminal 2E", "Paris 16e", "2026-10-01 09:30",
         150, "Karim", "Mercedes S-Class", "in_curs"),
        ("Société Lumière", "+33133334444", "Paris 9e", "CDG Terminal 2E",
         "2026-10-01 15:30", 145, "Alexandre", "Mercedes V-Class", "confirmata"),
        ("Mr. Bernard", "+33655554444", "ORY Terminal 4", "Paris 15e",
         "2026-10-01 18:00", 120, None, None, "rezervata"),
        ("Travel Agency", "+33122223333", "Paris 1er", "CDG Terminal 2E",
         "2026-10-02 07:00", 145, None, None, "rezervata"),
    ]
    curse_ids = []
    for (client, tel, prel, dest, cand, pret, sof, mas, status) in curse:
        c = dispecerat.creeaza_cursa(client, tel, prel, dest, cand, pret,
                                     sursa="demo", notite="Cursă demonstrativă")
        if sof:
            ok, _ = dispecerat.atribuie(c.id, soferi[sof], masini[mas])
            if not ok:
                continue
            if status in ("in_curs", "finalizata"):
                dispecerat.schimba_status(c.id, "in_curs")
            if status == "finalizata":
                dispecerat.schimba_status(c.id, "finalizata")
        curse_ids.append(c.id)
    rez["curse"] = len(curse_ids)

    # --- facturi: emisă/plătită/parțială/restantă din ciornele auto ---
    db = SessionLocal()
    try:
        facturi = (db.query(Factura).filter(Factura.id > repere.get("facturi", 0))
                    .order_by(Factura.id).all())
        plan = ["platita", "platita", "partial", "restanta", "ciorna", "platita"]
        for f, stare in zip(facturi, plan):
            f.data_emitere = acum  # luna curentă, ca să apară în BI
            if stare == "ciorna":
                f.status = "ciorna"
            elif stare == "restanta":
                f.status = "emisa"
                f.data_emitere = acum - timedelta(days=40)
                f.deadline = acum - timedelta(days=10)
            else:
                f.status = "emisa"
                db.flush()
                platit = f.total if stare == "platita" else round(f.total / 2, 2)
                db.add(Plata(factura_id=f.id, suma=platit, metoda="card",
                             referinta="DEMO-PLATA", data=acum - timedelta(days=1)))
                f.status = stare
        db.commit()
    finally:
        db.close()
    rez["facturi"] = len(facturi)

    # --- marketing: postări + campanii ---
    for canal, txt, status in [
        ("instagram", "✨ Paris by night, în confort absolut. Transferurile noastre premium vă așteaptă. #LuxuryTransfer #Paris",
         "publicata"),
        ("facebook", "🚗 Service chauffeur privé à Paris — ponctualité et élégance, 24/7.",
         "publicata"),
        ("linkedin", "Corporate mobility in Paris: reliable executive transfers for your teams.",
         "programata"),
        ("instagram", "🍂 Automne à Paris — réservez votre transfert aéroport en toute sérénité.",
         "ciorna"),
    ]:
        p = marketing.adauga_postare(canal, txt)
        if status != "ciorna":
            db2 = SessionLocal()
            try:
                pp = db2.query(Postare).get(p.id)
                pp.status = status
                pp.data_programata = acum + timedelta(days=2) if status == "programata" else acum - timedelta(days=3)
                db2.commit()
            finally:
                db2.close()
    campanii = [
        ("Transferts Aéroport — Automne", "instagram", "2026-09-01", "2026-10-31",
         2400, 48200, 312, 18400, 2400, "activa"),
        ("Corporate & MICE", "linkedin", "2026-09-15", "2026-11-15",
         1800, 12600, 96, 22100, 1800, "activa"),
        ("Fêtes de fin d'année", "facebook", "2026-11-20", "2026-12-31",
         1500, 31500, 188, 9800, 1500, "planificata"),
    ]
    db = SessionLocal()
    try:
        for (nume, canal, di, ds, buget, reach, leaduri, venit, cost, status) in campanii:
            db.add(Campanie(nume=nume, canal=canal,
                            data_inceput=datetime.fromisoformat(di),
                            data_sfarsit=datetime.fromisoformat(ds),
                            buget=buget, reach=reach, leaduri=leaduri,
                            venit=venit, cost=cost, status=status))
        db.commit()
    finally:
        db.close()
    rez["campanii"] = len(campanii)

    # --- competitori ---
    for nume, site, serv in [
        ("Elite Cars Paris", "elitecars-paris.fr", "transferuri aeroport, chauffeur"),
        ("Prestige Drive", "prestigedrive.fr", "corporate, evenimente"),
        ("Royal Transfer 75", "royaltransfer75.fr", "VIP, nunți"),
    ]:
        c = competitori.adauga(nume, site, serv)
        competitori.adauga_observatie(c.id, "Tarife cu ~10% peste media pieței; prezență activă pe Instagram.")

    # --- produs / growth / risc ---
    i1 = produs.adauga_idee("Abonament corporate lunar", "Pachet 20 curse/lună pentru firme", "serviciu")
    i2 = produs.adauga_idee("Concierge la bord", "Șampanie și Wi-Fi premium în S-Class", "serviciu")
    i3 = produs.adauga_idee("Tururi Paris by night", "Circuit turistic de 2h cu șofer-ghid", "serviciu")
    produs.voteaza_idee(i1.id, 9)
    produs.voteaza_idee(i2.id, 7)
    produs.voteaza_idee(i3.id, 8)
    o1 = produs.creeaza_oportunitate("Abonament corporate", "Contracte lunare cu 5 firme",
                                    investitie_estimata=2000, venit_lunar_estimat=3500)
    produs.marcheaza_aprobata(o1.id)
    o2 = produs.creeaza_oportunitate("Flotă +2 mașini", "Două V-Class pentru segmentul grupuri",
                                    investitie_estimata=90000, venit_lunar_estimat=6000)
    inv1 = growth.evalueaza_investitie("Mercedes V-Class suplimentar", "masina",
                                      cost=65000, venit_lunar_estimat=4200)
    growth.marcheaza_aprobata(inv1.id)
    inv2 = growth.evalueaza_investitie("Campanie Google Ads Q4", "marketing",
                                      cost=3000, venit_lunar_estimat=1800)
    luna = acum.strftime("%Y-%m")
    for cat, val in [("marketing", 2500), ("salarii", 9000),
                     ("combustibil", 1200), ("mentenanta", 800)]:
        growth.seteaza_buget(luna, cat, val)
    risc.adauga_verificare("ITP", "AB-123-CD", "2026-10-20")
    risc.adauga_verificare("asigurare", "EF-456-GH", "2027-03-01")
    risc.adauga_verificare("licență transport", "TLP-2026", "2026-11-15")
    nr1 = risc.semnaleaza("Zgârieturi caroserie S-Class", "constatate la spălătorie", "scazuta")
    risc.rezolva_neregula(nr1.id)
    risc.semnaleaza("Anvelopă uzată V-Class", "de înlocuit înainte de sezonul rece", "medie")
    risc.analizeaza_contract(
        "Contract-cadru demo",
        "Prestatorul se obligă să asigure transferuri. Penalități de 50% în caz de "
        "întârziere. Contractul se prelungește automat pe 5 ani fără notificare. "
        "Forța majoră exonerează ambele părți.")

    # --- snapshoturi KPI ultimele 7 zile ---
    db = SessionLocal()
    try:
        for i in range(6, 0, -1):
            zi = acum - timedelta(days=i)
            db.add(KpiSnapshot(cheie="incasari_azi", valoare=900 + i * 120,
                               created_at=zi))
            db.add(KpiSnapshot(cheie="curse_finalizate_azi", valoare=6 + (i % 3),
                               created_at=zi))
        db.commit()
    finally:
        db.close()
    finante.snapshot_kpi()

    # --- marchează tot ce a creat seed-ul ca demo=1 ---
    db = SessionLocal()
    try:
        _marcheaza_noi_ca_demo(db, repere)
        db.commit()
    finally:
        db.close()

    audit.inregistreaza("demo", "seed_demo",
                        f"încărcate date demonstrative: {rez}")
    return rez


def date_bord() -> dict:
    """Datele pentru pagina /demo: marketing + analitică + statistică."""
    from . import dispecerat, finante
    fin = finante.rezumat()
    db = SessionLocal()
    try:
        campanii = db.query(Campanie).order_by(Campanie.id).all()
        camp = []
        for c in campanii:
            roas = round(c.venit / c.cost, 1) if c.cost else 0
            camp.append({"nume": c.nume, "canal": c.canal, "status": c.status,
                         "reach": c.reach, "leaduri": c.leaduri,
                         "venit": round(c.venit, 2), "cost": round(c.cost, 2),
                         "roas": roas})
        snap = (db.query(KpiSnapshot)
                  .filter(KpiSnapshot.cheie.in_(["venituri_zi", "incasari_azi"]))
                  .order_by(KpiSnapshot.created_at).all())
        trend = [{"zi": (s.created_at or datetime.now()).strftime("%d.%m"),
                  "val": round(s.valoare or 0)} for s in snap[-7:]]
        max_trend = max([t["val"] for t in trend] or [1])
        from sqlalchemy import func
        statusuri = {}
        for st, nr in db.query(Cursa.status, func.count(Cursa.id)).group_by(Cursa.status).all():
            statusuri[st or "—"] = nr
        curse_azi = dispecerat.curse_pe_zi()
        soferi = db.query(Sofer).order_by(Sofer.id).all()
        leaduri_tot = sum(c["leaduri"] for c in camp)
        roas_mediu = (round(sum(c["roas"] for c in camp) / len(camp), 1)
                      if camp else 0)
        return {
            "fin": fin, "campanii": camp, "trend": trend,
            "max_trend": max_trend, "statusuri": statusuri,
            "curse_azi": [{"id": c.id, "client": c.client_nume,
                           "ruta": f"{c.preluare} → {c.destinatie}",
                           "ora": c.data_ora.strftime("%H:%M") if c.data_ora else "—",
                           "status": c.status, "pret": c.pret,
                           "sofer": c.sofer.nume if c.sofer else "—"}
                          for c in curse_azi],
            "soferi": [{"nume": s.nume, "status": s.status} for s in soferi],
            "leaduri_tot": leaduri_tot, "roas_mediu": roas_mediu,
            "curse_luna": sum(1 for _ in db.query(Cursa.id).all()),
        }
    finally:
        db.close()
