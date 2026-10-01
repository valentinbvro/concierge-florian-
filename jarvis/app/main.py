"""Aplicația web Jarvis — Faza 2.

Pagini: chat intern (/chat), aprobări (/aprobari), catalog (/catalog),
        oferte (/oferte), cunoștințe (/cunostinte), dispecerat (/dispecerat),
        marketing (/marketing), competitori (/competitori). Bilingv RO/FR.
API: /api/chat, /api/aprobari, /api/pipeline, /api/scoring, /api/jobs/followup,
     /api/curse, /api/soferi, /api/masini, /api/notificari, /api/postari,
     /api/competitori, /sanatate.
Webhooks: /webhooks/whatsapp, /webhooks/messenger (verificare + recepție).
"""
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from . import approvals, audit, catalog, competitori, config, cunostinte, demo, dispecerat, finante, growth, hermes, jobs, \
    marketing, notificari, oferte, pipeline, produs, risc, scoring
from .channels import messenger, whatsapp
from .crm_client import CrmClient, CrmError
from .db import SessionLocal, init_db
from .i18n import LANGS, resolve_lang, t as tr
from .models import AgentTask, Offer, Postare
from .orchestrator import Orchestrator

init_db()
demo.asigura_coloane_demo()
crm = CrmClient()
jarvis = Orchestrator(crm)

app = FastAPI(title="Jarvis — Faza 3")
templates = Jinja2Templates(directory="templates")


def _ctx(request: Request, extra: dict | None = None) -> dict:
    """Context comun pentru template-uri: limbă + funcția de traducere."""
    lang = resolve_lang(request.query_params.get("lang"), request.cookies.get("lang"))
    ctx = {"lang": lang, "t": tr, "demo_activ": demo.demo_activ()}
    if extra:
        ctx.update(extra)
    return ctx


# --- pagini ---
@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse("/chat")


@app.get("/limba/{cod}", include_in_schema=False)
def schimba_limba(cod: str, request: Request):
    lang = cod if cod in LANGS else "ro"
    ref = request.headers.get("referer", "/chat")
    resp = RedirectResponse(ref, status_code=303)
    resp.set_cookie("lang", lang, max_age=31536000)
    return resp


@app.get("/chat", response_class=HTMLResponse)
def pagina_chat(request: Request):
    agenti = [{"key": k, "nume": a.nume, "faza": a.faza, "descriere": a.descriere}
              for k, a in jarvis.agenti.items()]
    return templates.TemplateResponse(request, "chat.html", _ctx(request, {"agenti": agenti}))


@app.get("/aprobari", response_class=HTMLResponse)
def pagina_aprobari(request: Request):
    return templates.TemplateResponse(request, "aprobari.html", _ctx(request, {
        "aprobari": approvals.in_asteptare(), "matrice": approvals.MATRICE}))


@app.get("/catalog", response_class=HTMLResponse)
def pagina_catalog(request: Request):
    return templates.TemplateResponse(request, "catalog.html",
                                      _ctx(request, {"produse": catalog.lista(active_doar=False)}))


@app.get("/oferte", response_class=HTMLResponse)
def pagina_oferte(request: Request):
    return templates.TemplateResponse(request, "oferte.html",
                                      _ctx(request, {"oferte": oferte.lista_oferte()}))


@app.get("/cunostinte", response_class=HTMLResponse)
def pagina_cunostinte(request: Request):
    return templates.TemplateResponse(request, "cunostinte.html",
                                      _ctx(request, {"items": cunostinte.lista()}))


@app.get("/dispecerat", response_class=HTMLResponse)
def pagina_dispecerat(request: Request):
    from datetime import date
    return templates.TemplateResponse(request, "dispecerat.html", _ctx(request, {
        "curse": dispecerat.curse_pe_zi(date.today()),
        "soferi": dispecerat.lista_soferi(),
        "masini": dispecerat.lista_masini(),
        "notifs": notificari.in_asteptare(),
    }))


@app.get("/marketing", response_class=HTMLResponse)
def pagina_marketing(request: Request):
    return templates.TemplateResponse(request, "marketing.html",
                                      _ctx(request, {"postari": marketing.lista_postari()}))


@app.get("/competitori", response_class=HTMLResponse)
def pagina_competitori(request: Request):
    return templates.TemplateResponse(request, "competitori.html",
                                      _ctx(request, {"competitori": competitori.lista()}))


@app.get("/finante", response_class=HTMLResponse)
def pagina_finante(request: Request):
    return templates.TemplateResponse(request, "finante.html",
                                      _ctx(request, {"demo": not config.PENNYLANE_API_TOKEN}))


@app.get("/demo", response_class=HTMLResponse)
def pagina_demo(request: Request):
    try:
        bord = demo.date_bord()
    except Exception:
        bord = {}
    return templates.TemplateResponse(request, "demo.html",
                                      _ctx(request, {"bord": bord}))


@app.get("/hermes", response_class=HTMLResponse)
def pagina_hermes(request: Request):
    return templates.TemplateResponse(request, "hermes.html", _ctx(request))


@app.get("/api/hermes/raport", include_in_schema=False)
def api_hermes_raport():
    return hermes.raport()


@app.get("/api/hermes/sugestii", include_in_schema=False)
def api_hermes_sugestii(status: str | None = None):
    return {"sugestii": [
        {"id": x.id, "tip": x.tip, "titlu": x.titlu, "status": x.status,
         "detalii": x.detalii, "created_at": x.created_at.isoformat() if x.created_at else None}
        for x in hermes.lista_sugestii(status)]}


@app.post("/api/hermes/analizeaza", include_in_schema=False)
def api_hermes_analizeaza():
    return {"ok": True, "rezultat": hermes.analizeaza()}


class _DecizieSugestie(BaseModel):
    decizie: str


class _RaspunsSugestie(BaseModel):
    raspuns: str


class _InstructiuneNoua(BaseModel):
    agent: str
    text: str


@app.post("/api/hermes/sugestie/{sid}/decide", include_in_schema=False)
def api_hermes_decide(sid: int, corp: _DecizieSugestie):
    s = hermes.decide_sugestie(sid, corp.decizie)
    return {"ok": s is not None, "status": s.status if s else None}


@app.post("/api/hermes/sugestie/{sid}/raspuns", include_in_schema=False)
def api_hermes_raspuns(sid: int, corp: _RaspunsSugestie):
    s = hermes.completeaza_raspuns(sid, corp.raspuns)
    return {"ok": s is not None}


@app.post("/api/hermes/sugestie/{sid}/aplica", include_in_schema=False)
def api_hermes_aplica(sid: int):
    ok, cod = hermes.aplica_sugestie(sid)
    return {"ok": ok, "cod": cod}


@app.post("/api/hermes/instructiune", include_in_schema=False)
def api_hermes_instructiune(corp: _InstructiuneNoua):
    inst = hermes.seteaza_instructiune(corp.agent, corp.text)
    return {"ok": True, "agent": inst.agent, "versiune": inst.versiune}


@app.get("/api/hermes/instructiuni", include_in_schema=False)
def api_hermes_instructiuni(agent: str | None = None):
    return {"instructiuni": [
        {"id": x.id, "agent": x.agent, "versiune": x.versiune, "activa": x.activa,
         "text": x.text, "creat_de": x.creat_de,
         "created_at": x.created_at.isoformat() if x.created_at else None}
        for x in hermes.istoric_instructiuni(agent)]}


@app.post("/api/jobs/hermes", include_in_schema=False)
def job_hermes():
    """Job de învățare continuă: analizează semnalele și generează sugestii."""
    try:
        rez = hermes.analizeaza()
        return {"ok": True, **rez}
    except Exception as e:
        return JSONResponse({"ok": False, "eroare": str(e)[:300]}, status_code=500)


@app.post("/api/demo/seed", include_in_schema=False)
def api_demo_seed():
    try:
        rez = demo.seed_demo()
        return {"ok": True, "rezultat": rez}
    except Exception as e:
        return JSONResponse({"ok": False, "eroare": str(e)[:300]}, status_code=500)


@app.post("/api/demo/sterge", include_in_schema=False)
def api_demo_sterge():
    try:
        sterse = demo.sterge_demo()
        return {"ok": True, "sterse": sterse}
    except Exception as e:
        return JSONResponse({"ok": False, "eroare": str(e)[:300]}, status_code=500)


@app.get("/api/demo/status", include_in_schema=False)
def api_demo_status():
    return {"activ": demo.demo_activ()}


@app.get("/bi", response_class=HTMLResponse)
def pagina_bi(request: Request):
    return templates.TemplateResponse(request, "bi.html", _ctx(request))


@app.get("/produs", response_class=HTMLResponse)
def pagina_produs(request: Request):
    return templates.TemplateResponse(request, "produs.html", _ctx(request))


@app.get("/growth", response_class=HTMLResponse)
def pagina_growth(request: Request):
    return templates.TemplateResponse(request, "growth.html", _ctx(request))


@app.get("/risc", response_class=HTMLResponse)
def pagina_risc(request: Request):
    return templates.TemplateResponse(request, "risc.html", _ctx(request))


@app.get("/oferte/{oferta_id}/pdf")
def descarca_pdf(oferta_id: int):
    db = SessionLocal()
    try:
        of = db.query(Offer).get(oferta_id)
        if not of or not of.fisier_pdf:
            return JSONResponse({"eroare": "PDF inexistent. Generează-l aprobând oferta."},
                                status_code=404)
        cale = of.fisier_pdf
    finally:
        db.close()
    return FileResponse(cale, filename=f"{cale.rsplit('/', 1)[-1]}",
                        media_type="application/pdf")


# --- API ---
@app.post("/api/chat")
def api_chat(payload: dict):
    lang = resolve_lang(payload.get("lang"), None)
    raspuns = jarvis.proceseaza(payload.get("text", ""), payload.get("utilizator", "valentin"),
                                lang=lang)
    return {"raspuns": raspuns, "lang": lang}


@app.post("/api/aprobari/{aprobare_id}/decide")
def api_decide(aprobare_id: int, payload: dict):
    ap = approvals.decide(aprobare_id, payload.get("decizie", ""),
                          payload.get("decident", config.APPROVER_NAME))
    if not ap:
        return JSONResponse({"ok": False, "eroare": "Cererea nu există sau e deja decisă."}, status_code=404)
    # La aprobarea unei oferte, generăm automat PDF-ul
    if ap.stare == "aprobat" and ap.tip == "trimitere_oferta":
        db = SessionLocal()
        try:
            of = db.query(Offer).filter_by(approval_id=ap.id).first()
            oid = of.id if of else None
        finally:
            db.close()
        if oid:
            try:
                cale = oferte.genereaza_pdf(oid)
                audit.inregistreaza("jarvis", "oferta_pdf", f"Oferta #{oid}: {cale}")
            except Exception as e:
                audit.inregistreaza("jarvis", "eroare_pdf", str(e)[:200])
    # La aprobarea publicării, postarea devine "aprobata"
    if ap.stare == "aprobat" and ap.tip == "postare_publica":
        db = SessionLocal()
        try:
            post = db.query(Postare).filter_by(approval_id=ap.id).first()
            if post:
                post.status = "aprobata"
                db.commit()
                audit.inregistreaza("jarvis", "postare_aprobata", f"Postarea #{post.id} ({post.canal})")
        finally:
            db.close()
    # La aprobarea anulării, anulăm efectiv cursa (eliberează șofer/mașină)
    if ap.stare == "aprobat" and ap.tip == "anulare_cursa":
        import re as _re
        m = _re.search(r"#(\d+)", ap.titlu or "")
        if m:
            ok, _ = dispecerat.schimba_status(int(m.group(1)), "anulata", crm=crm)
            audit.inregistreaza("jarvis", "cursa_anulata", f"cursa #{m.group(1)}: {ok}")
    # La aprobarea emiterii, finalizăm factura în Pennylane (IREVERSIBIL)
    if ap.stare == "aprobat" and ap.tip == "emitere_factura":
        import re as _re
        m = _re.search(r"JF-\d{4}-\d+", ap.titlu or "")
        if m:
            db = SessionLocal()
            try:
                from .models import Factura as _F
                f = db.query(_F).filter_by(numar=m.group(0)).first()
                fid = f.id if f else None
            finally:
                db.close()
            if fid:
                ok, info = finante.finalizeaza_dupa_aprobare(fid)
                audit.inregistreaza("jarvis", "factura_finalizata",
                                    f"{m.group(0)}: {ok} {info}")
    # La aprobarea trimiterii, trimitem factura pe email via Pennylane
    if ap.stare == "aprobat" and ap.tip == "trimitere_factura":
        import re as _re
        m = _re.search(r"JF-\d{4}-\d+", ap.titlu or "")
        if m:
            db = SessionLocal()
            try:
                from .models import Factura as _F
                f = db.query(_F).filter_by(numar=m.group(0)).first()
                fid = f.id if f else None
            finally:
                db.close()
            if fid:
                ok, info = finante.trimite_dupa_aprobare(fid)
                audit.inregistreaza("jarvis", "factura_trimisa_aprobata",
                                    f"{m.group(0)}: {ok}")
    # La aprobarea investiției, marcăm investiția ca aprobată
    if ap.stare == "aprobat" and ap.tip == "aprobare_investitie":
        db = SessionLocal()
        try:
            from .models import Investitie as _I
            inv = db.query(_I).filter_by(approval_id=ap.id).first()
            iid = inv.id if inv else None
        finally:
            db.close()
        if iid:
            growth.marcheaza_aprobata(iid)
            audit.inregistreaza("jarvis", "investitie_aprobata", f"investiția #{iid}")
    # La aprobarea oportunității, marcăm oportunitatea ca aprobată
    if ap.stare == "aprobat" and ap.tip == "aprobare_oportunitate":
        db = SessionLocal()
        try:
            from .models import Oportunitate as _O
            op = db.query(_O).filter_by(approval_id=ap.id).first()
            oid = op.id if op else None
        finally:
            db.close()
        if oid:
            produs.marcheaza_aprobata(oid)
            audit.inregistreaza("jarvis", "oportunitate_aprobata", f"oportunitatea #{oid}")
    return {"ok": True, "stare": ap.stare}


@app.get("/api/aprobari")
def api_aprobari():
    return [{"id": a.id, "tip": a.tip, "titlu": a.titlu, "detalii": a.detalii,
             "solicitat_de": a.solicitat_de, "stare": a.stare}
            for a in approvals.in_asteptare()]


@app.get("/api/pipeline")
def api_pipeline():
    return pipeline.snapshot(crm)


@app.get("/api/scoring")
def api_scoring():
    try:
        return scoring.leaduri_cu_scor(crm)
    except CrmError as e:
        return JSONResponse({"eroare": str(e)}, status_code=502)


@app.post("/api/jobs/followup")
def api_job_followup():
    return jobs.ruleaza_followup(crm)


@app.get("/api/catalog")
def api_catalog():
    return [{"id": p.id, "nume": p.nume, "sku": p.sku, "pret": p.pret,
             "moneda": p.moneda, "activ": p.activ} for p in catalog.lista(active_doar=False)]


@app.post("/api/catalog")
def api_catalog_adauga(payload: dict):
    p = catalog.adauga(payload.get("nume", ""), float(payload.get("pret", 0) or 0),
                       sku=payload.get("sku", ""), descriere=payload.get("descriere", ""))
    audit.inregistreaza("valentin", "catalog_adauga", f"#{p.id} {p.nume}")
    return {"ok": True, "id": p.id}


@app.get("/api/cunostinte")
def api_cunostinte():
    return [{"id": i.id, "intrebare": i.intrebare, "raspuns": i.raspuns}
            for i in cunostinte.lista()]


@app.post("/api/cunostinte")
def api_cunostinte_adauga(payload: dict):
    it = cunostinte.adauga(payload.get("intrebare", ""), payload.get("raspuns", ""),
                           payload.get("etichete", ""))
    return {"ok": True, "id": it.id}


# --- Faza 2: dispecerat ---
def _cursa_dict(c):
    return {"id": c.id, "client_nume": c.client_nume, "client_telefon": c.client_telefon,
            "preluare": c.preluare, "destinatie": c.destinatie,
            "data_ora": c.data_ora.isoformat() if c.data_ora else None,
            "sofer_id": c.sofer_id, "masina_id": c.masina_id,
            "sofer": c.sofer.nume if c.sofer else None,
            "masina": c.masina.marca_model if c.masina else None,
            "status": c.status, "pret": c.pret, "sursa": c.sursa}


@app.get("/api/curse")
def api_curse(zi: str | None = None):
    from datetime import date as _d
    z = _d.fromisoformat(zi) if zi else _d.today()
    return [_cursa_dict(c) for c in dispecerat.curse_pe_zi(z)]


@app.post("/api/curse")
def api_cursa_noua(payload: dict):
    c = dispecerat.creeaza_cursa(payload.get("client_nume", ""), payload.get("client_telefon", ""),
                                 payload.get("preluare", ""), payload.get("destinatie", ""),
                                 payload.get("cand", ""), pret=float(payload.get("pret", 0) or 0),
                                 sursa=payload.get("sursa", "web"))
    return {"ok": True, "id": c.id}


@app.post("/api/curse/{cursa_id}/atribuie")
def api_cursa_atribuie(cursa_id: int, payload: dict):
    ok, info = dispecerat.atribuie(cursa_id, payload.get("sofer_id"),
                                   payload.get("masina_id"), crm=crm)
    if not ok:
        return JSONResponse({"ok": False, "eroare": info}, status_code=422)
    return {"ok": True, "detaliu": info}


@app.post("/api/curse/{cursa_id}/status")
def api_cursa_status(cursa_id: int, payload: dict):
    status = dispecerat.normalizeaza_status(payload.get("status", ""))
    if not status:
        return JSONResponse({"ok": False, "eroare": "status_invalid"}, status_code=422)
    if status == "anulata":
        ap = approvals.cere_aprobare(tip="anulare_cursa", titlu=f"Anulare cursa #{cursa_id}",
                                     detalii=f"Anulare cursa #{cursa_id} din dispecerat.",
                                     solicitat_de=payload.get("decident", "web"))
        return {"ok": True, "asteapta_aprobare": ap.id}
    ok, info = dispecerat.schimba_status(cursa_id, status, crm=crm)
    if not ok:
        return JSONResponse({"ok": False, "eroare": info}, status_code=422)
    return {"ok": True}


@app.get("/api/soferi")
def api_soferi():
    return [{"id": s.id, "nume": s.nume, "telefon": s.telefon, "status": s.status}
            for s in dispecerat.lista_soferi()]


@app.post("/api/soferi")
def api_sofer_adauga(payload: dict):
    s = dispecerat.adauga_sofer(payload.get("nume", ""), payload.get("telefon", ""))
    return {"ok": True, "id": s.id}


@app.get("/api/masini")
def api_masini():
    return [{"id": m.id, "marca_model": m.marca_model, "numar": m.numar,
             "locuri": m.locuri, "status": m.status} for m in dispecerat.lista_masini()]


@app.post("/api/masini")
def api_masina_adauga(payload: dict):
    m = dispecerat.adauga_masina(payload.get("marca_model", ""), payload.get("numar", ""),
                                 int(payload.get("locuri", 4) or 4))
    return {"ok": True, "id": m.id}


@app.get("/api/notificari")
def api_notificari():
    return [{"id": n.id, "destinatar": n.destinatar, "canal": n.canal,
             "text": n.text, "status": n.status, "cursa_id": n.cursa_id}
            for n in notificari.in_asteptare()]


# --- Faza 2: marketing & competitori ---
@app.get("/api/postari")
def api_postari():
    return [{"id": p.id, "canal": p.canal, "text": p.text,
             "data_programata": p.data_programata.isoformat() if p.data_programata else None,
             "status": p.status} for p in marketing.lista_postari()]


@app.post("/api/postari")
def api_postare_adauga(payload: dict):
    p = marketing.adauga_postare(payload.get("canal", "instagram"), payload.get("text", ""))
    return {"ok": True, "id": p.id}


@app.get("/api/competitori")
def api_competitori():
    return [{"id": c.id, "nume": c.nume, "website": c.website, "servicii": c.servicii,
             "observatii": c.observatii,
             "ultima_verificare": c.ultima_verificare.isoformat() if c.ultima_verificare else None}
            for c in competitori.lista()]


@app.post("/api/competitori")
def api_competitor_adauga(payload: dict):
    c = competitori.adauga(payload.get("nume", ""), payload.get("website", ""),
                           payload.get("servicii", ""))
    return {"ok": True, "id": c.id}


@app.post("/api/competitori/{cid}/observatii")
def api_competitor_observatie(cid: int, payload: dict):
    c = competitori.adauga_observatie(cid, payload.get("text", ""))
    if not c:
        return JSONResponse({"ok": False}, status_code=404)
    return {"ok": True}


# --- Faza 3: finanțe & BI ---
def _factura_dict(f):
    import json as _json
    return {"id": f.id, "numar": f.numar, "numar_pennylane": f.numar_pennylane,
            "cursa_id": f.cursa_id, "client_nume": f.client_nume,
            "linii": _json.loads(f.linii or "[]"),
            "subtotal": f.subtotal, "tva": f.tva, "total": f.total,
            "status": f.status,
            "deadline": f.deadline.strftime("%d.%m.%Y") if f.deadline else None}


@app.get("/api/facturi")
def api_facturi(status: str | None = None):
    return [_factura_dict(f) for f in finante.lista_facturi(status)]


@app.post("/api/facturi")
def api_factura_noua(payload: dict):
    try:
        f = finante.creeaza_factura(cursa_id=payload.get("cursa_id"),
                                    suma=payload.get("suma"),
                                    client_nume=payload.get("client_nume", ""),
                                    client_telefon=payload.get("client_telefon", ""),
                                    solicitat_de=payload.get("solicitat_de", "web"))
    except ValueError:
        return JSONResponse({"ok": False, "eroare": "suma_invalida"}, status_code=422)
    return {"ok": True, "id": f.id, "numar": f.numar}


@app.post("/api/facturi/{factura_id}/emite")
def api_factura_emite(factura_id: int, payload: dict):
    f = next((x for x in finante.lista_facturi() if x.id == factura_id), None)
    if not f or f.status != "ciorna":
        return JSONResponse({"ok": False, "eroare": "nu_exista"}, status_code=404)
    ap = approvals.cere_aprobare(
        tip="emitere_factura",
        titlu=f"Emitere factură {f.numar} ({f.client_nume}, {f.total:.2f} EUR)",
        detalii=f"Finalizare în Pennylane — IREVERSIBILĂ. Cursă #{f.cursa_id or '—'}.",
        solicitat_de=payload.get("solicitat_de", "web"))
    db = SessionLocal()
    try:
        from .models import Factura as _F
        db.query(_F).get(factura_id).approval_id = ap.id
        db.commit()
    finally:
        db.close()
    return {"ok": True, "asteapta_aprobare": ap.id}


@app.post("/api/facturi/{factura_id}/trimite")
def api_factura_trimite(factura_id: int, payload: dict):
    f = next((x for x in finante.lista_facturi() if x.id == factura_id), None)
    if not f or f.status not in ("emisa", "partial"):
        return JSONResponse({"ok": False, "eroare": "nu_exista"}, status_code=404)
    ap = approvals.cere_aprobare(
        tip="trimitere_factura",
        titlu=f"Trimitere factură {f.numar} către {f.client_nume}",
        detalii=f"Trimitere pe email via Pennylane: {f.total:.2f} EUR.",
        solicitat_de=payload.get("solicitat_de", "web"))
    return {"ok": True, "asteapta_aprobare": ap.id}


@app.post("/api/facturi/{factura_id}/platita")
def api_factura_platita(factura_id: int, payload: dict):
    ok, info = finante.marcheaza_platita(factura_id, float(payload.get("suma", 0) or 0),
                                         metoda=payload.get("metoda", ""),
                                         referinta=payload.get("referinta", ""),
                                         solicitat_de=payload.get("solicitat_de", "web"))
    if not ok:
        return JSONResponse({"ok": False, "eroare": info}, status_code=404)
    return {"ok": True, "status": info}


@app.get("/api/finante/restante")
def api_finante_restante():
    return [_factura_dict(f) for f in finante.facturi_restante()]


@app.get("/api/finante/anomalii")
def api_finante_anomalii():
    return finante.detecteaza_anomalii()


@app.get("/api/bi/dashboard")
def api_bi_dashboard():
    return finante.rezumat()


# --- Faza 4: produs / growth / risc ---
@app.get("/api/idei")
def api_idei():
    return [{"id": i.id, "titlu": i.titlu, "descriere": i.descriere,
             "categorie": i.categorie, "scor": i.scor, "status": i.status}
            for i in produs.lista_idei()]


@app.post("/api/idei")
def api_idee_noua(payload: dict):
    i = produs.adauga_idee(payload.get("titlu", ""), payload.get("descriere", ""),
                            payload.get("categorie", "serviciu"))
    return {"id": i.id}


@app.post("/api/idei/{idee_id}/vot")
def api_idee_vot(idee_id: int, payload: dict):
    i = produs.voteaza_idee(idee_id, int(payload.get("scor", 0)))
    return {"ok": i is not None}


@app.get("/api/oportunitati")
def api_oportunitati():
    return [produs.fisa_oportunitate(o) for o in produs.lista_oportunitati()]


@app.post("/api/oportunitati")
def api_oportunitate_noua(payload: dict):
    o = produs.creeaza_oportunitate(payload.get("titlu", ""),
                                    payload.get("descriere", ""),
                                    payload.get("investitie_estimata", 0.0),
                                    payload.get("venit_lunar_estimat", 0.0))
    return {"id": o.id}


@app.get("/api/investitii")
def api_investitii():
    return [growth.analiza_investitie(x) for x in growth.lista_investitii()]


@app.post("/api/investitii")
def api_investitie_noua(payload: dict):
    inv = growth.evalueaza_investitie(payload.get("titlu", ""),
                                      payload.get("tip", "masina"),
                                      payload.get("cost", 0.0),
                                      payload.get("venit_lunar_estimat", 0.0))
    return {"id": inv.id}


@app.get("/api/buget")
def api_buget(luna: str | None = None):
    return growth.buget_luna(luna)


@app.post("/api/buget")
def api_buget_set(payload: dict):
    b = growth.seteaza_buget(payload.get("luna", ""),
                              payload.get("categorie", "altele"),
                              payload.get("planificat", 0.0))
    return {"id": b.id}


@app.get("/api/verificari")
def api_verificari():
    return [{"id": v.id, "tip": v.tip, "referinta": v.referinta,
             "expira_la": v.expira_la.strftime("%Y-%m-%d") if v.expira_la else None,
             "status": v.status, "notite": v.notite}
            for v in risc.lista_verificari()]


@app.post("/api/verificari")
def api_verificare_noua(payload: dict):
    try:
        v = risc.adauga_verificare(payload.get("tip", "alta"),
                                   payload.get("referinta", ""),
                                   payload.get("expira_la", ""),
                                   payload.get("notite", ""))
    except ValueError:
        return JSONResponse({"ok": False, "eroare": "data_invalida"}, status_code=400)
    return {"id": v.id}


@app.get("/api/nereguli")
def api_nereguli():
    return [{"id": n.id, "titlu": n.titlu, "descriere": n.descriere,
             "severitate": n.severitate, "status": n.status}
            for n in risc.lista_nereguli()]


@app.post("/api/nereguli")
def api_neregula_noua(payload: dict):
    n = risc.semnaleaza(payload.get("titlu", ""), payload.get("descriere", ""),
                        payload.get("severitate", "medie"))
    return {"id": n.id}


@app.get("/api/analize-documente")
def api_analize_documente():
    import json as _json
    return [{"id": a.id, "nume": a.nume, "concluzii": _json.loads(a.concluzii)}
            for a in risc.lista_analize()]


@app.post("/api/jobs/conformitate")
def api_job_conformitate():
    return jobs.ruleaza_conformitate()


@app.post("/api/jobs/sync-pennylane")
def api_job_sync():
    rez = finante.sincronizeaza()
    finante.snapshot_kpi()
    return {"ok": True, **rez}
    db = SessionLocal()
    try:
        rows = db.query(AgentTask).order_by(AgentTask.id.desc()).limit(50).all()
        return [{"id": s.id, "agent": s.agent, "titlu": s.titlu, "stare": s.stare}
                for s in rows]
    finally:
        db.close()


@app.get("/api/sarcini")
def api_sarcini():
    db = SessionLocal()
    try:
        rows = db.query(AgentTask).order_by(AgentTask.id.desc()).limit(50).all()
        return [{"id": s.id, "agent": s.agent, "titlu": s.titlu, "stare": s.stare}
                for s in rows]
    finally:
        db.close()


@app.get("/api/audit")
def api_audit():
    return [{"id": e.id, "actor": e.actor, "actiune": e.actiune,
             "detalii": e.detalii, "created_at": str(e.created_at)}
            for e in audit.ultimele(50)]


@app.get("/sanatate")
def sanatate():
    try:
        crm.sumar()
        crm_ok = True
    except CrmError as e:
        crm_ok = str(e)
    return {"status": "ok", "faza": 4, "crm": crm_ok,
            "agenti": list(jarvis.agenti.keys())}


# --- webhooks canale externe (Faza 1: verificare + recepție funcționale) ---
@app.get("/webhooks/whatsapp")
def webhook_whatsapp_verify(request: Request):
    q = request.query_params
    challenge = whatsapp.verifica_webhook(q.get("hub.mode", ""), q.get("hub.verify_token", ""),
                                          q.get("hub.challenge", ""),
                                          config.WHATSAPP_VERIFY_TOKEN)
    if challenge is None:
        return JSONResponse({"eroare": "verify token invalid"}, status_code=403)
    return PlainTextResponse(challenge)


@app.post("/webhooks/whatsapp")
async def webhook_whatsapp(request: Request):
    payload = await request.json()
    return {"ok": True, "raspunsuri": whatsapp.proceseaza_payload(payload, jarvis)}


@app.get("/webhooks/messenger")
def webhook_messenger_verify(request: Request):
    q = request.query_params
    challenge = messenger.verifica_webhook(q.get("hub.mode", ""), q.get("hub.verify_token", ""),
                                           q.get("hub.challenge", ""),
                                           config.MESSENGER_VERIFY_TOKEN)
    if challenge is None:
        return JSONResponse({"eroare": "verify token invalid"}, status_code=403)
    return PlainTextResponse(challenge)


@app.post("/webhooks/messenger")
async def webhook_messenger(request: Request):
    payload = await request.json()
    return {"ok": True, "raspunsuri": messenger.proceseaza_payload(payload, jarvis)}


# --- compatibilitate veche ---
@app.post("/webhooks/{canal}")
async def webhook_generic(canal: str, request: Request):
    corp = (await request.body())[:500]
    audit.inregistreaza("webhook", f"webhook_{canal}", corp.decode("utf-8", "ignore"))
    return {"ok": True, "canal": canal, "nota": "Folosește /webhooks/whatsapp sau /webhooks/messenger."}
