"""Aplicația CRM — FastAPI + Jinja2 + SQLite."""
import os
from datetime import date, datetime, timedelta

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from .auth import (LoginRequired, get_current_user, hash_password,
                   login_redirect_response, login_user, logout_user,
                   require_admin, require_login, verify_password,
                   SESSION_SECRET)
from .db import Base, engine, get_db
from .models import (Account, Activity, ApiToken, Automation, Case, Contact,
                     Lead, Opportunity, Setting, User)
from .seed import seed
from .api_v1 import generate_token, hash_token, router as api_v1_router

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app = FastAPI(title="CRM")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)
app.include_router(api_v1_router)


@app.exception_handler(LoginRequired)
def _login_required(request: Request, exc: LoginRequired):
    return login_redirect_response()


@app.on_event("startup")
def _startup():
    Base.metadata.create_all(bind=engine)
    seed()


# ---------------- constante ----------------
STAGES = [("prospectare", "Prospectare"), ("calificare", "Calificare"),
          ("propunere", "Propunere"), ("negociere", "Negociere"),
          ("castigat", "Câștigat"), ("pierdut", "Pierdut")]
LEAD_STATUS = [("nou", "Nou"), ("contactat", "Contactat"),
               ("calificat", "Calificat"), ("convertit", "Convertit"),
               ("pierdut", "Pierdut")]
CASE_STATUS = [("nou", "Nou"), ("deschis", "Deschis"),
               ("in_asteptare", "În așteptare"), ("rezolvat", "Rezolvat"),
               ("inchis", "Închis")]
PRIORITIES = [("scazuta", "Scăzută"), ("medie", "Medie"),
              ("ridicata", "Ridicată"), ("urgenta", "Urgentă")]
TIPURI_ACT = [("sarcina", "Sarcină"), ("apel", "Apel"),
              ("email", "Email"), ("intalnire", "Întâlnire")]
ROLURI = [("admin", "Administrator"), ("vanzari", "Vânzări"),
          ("suport", "Suport")]
TIPURI_REL = [("lead", "Lead"), ("firma", "Firmă"), ("contact", "Contact"),
              ("oportunitate", "Oportunitate"), ("caz", "Caz")]
OPEN_STAGES = ["prospectare", "calificare", "propunere", "negociere"]


# ---------------- helpers ----------------
def ctx(request: Request, db: Session, user: User, **kw):
    s = db.get(Setting, "nume_firma")
    d = {"request": request, "user": user,
         "company": s.value if s else "CRM",
         "stages": STAGES, "lead_status": LEAD_STATUS,
         "case_status": CASE_STATUS, "priorities": PRIORITIES,
         "tipuri_act": TIPURI_ACT, "roluri": ROLURI, "tipuri_rel": TIPURI_REL}
    d.update(kw)
    return d


def automation_enabled(db: Session, key: str) -> bool:
    a = db.query(Automation).filter_by(key=key).first()
    return bool(a and a.enabled)


def add_activity(db: Session, *, tip, subject, owner_id, description="",
                 due_date=None, related_kind="", related_id=None):
    a = Activity(tip=tip, subject=subject, description=description,
                 due_date=due_date, status="deschis",
                 related_kind=related_kind, related_id=related_id,
                 owner_id=owner_id)
    db.add(a)
    return a


# --- automatizări (comutabile din /setari) ---
def automation_lead_nou(db: Session, lead: Lead):
    if not automation_enabled(db, "lead_nou"):
        return
    add_activity(db, tip="sarcina",
                 subject=f"Contactează leadul: {lead.full_name}",
                 due_date=date.today() + timedelta(days=1),
                 related_kind="lead", related_id=lead.id,
                 owner_id=lead.owner_id)


def automation_oportunitate_castigata(db: Session, opp: Opportunity):
    if not automation_enabled(db, "oportunitate_castigata"):
        return
    add_activity(db, tip="sarcina", subject=f"Follow-up client nou: {opp.name}",
                 description="Verifică satisfacția clientului după închidere.",
                 due_date=date.today() + timedelta(days=7),
                 related_kind="oportunitate", related_id=opp.id,
                 owner_id=opp.owner_id)


def automation_caz_urgent(db: Session, caz: Case):
    if not automation_enabled(db, "caz_urgent"):
        return
    add_activity(db, tip="sarcina",
                 subject=f"URGENT: rezolvă cazul „{caz.subject}”",
                 due_date=date.today(), related_kind="caz",
                 related_id=caz.id, owner_id=caz.owner_id)


def set_opp_stage(db: Session, opp: Opportunity, new_stage: str):
    old = opp.stage
    opp.stage = new_stage
    if new_stage == "castigat":
        opp.probability = 100
    elif new_stage == "pierdut":
        opp.probability = 0
    db.flush()
    if old != "castigat" and new_stage == "castigat":
        automation_oportunitate_castigata(db, opp)


def related_activities(db: Session, kind: str, rid: int):
    return (db.query(Activity)
            .filter(Activity.related_kind == kind, Activity.related_id == rid)
            .order_by(Activity.created_at.desc()).all())


def related_label(db: Session, kind: str, rid: int) -> str:
    try:
        if kind == "lead":
            o = db.get(Lead, rid)
            return f"Lead: {o.full_name}" if o else ""
        if kind == "firma":
            o = db.get(Account, rid)
            return f"Firmă: {o.name}" if o else ""
        if kind == "contact":
            o = db.get(Contact, rid)
            return f"Contact: {o.full_name}" if o else ""
        if kind == "oportunitate":
            o = db.get(Opportunity, rid)
            return f"Oportunitate: {o.name}" if o else ""
        if kind == "caz":
            o = db.get(Case, rid)
            return f"Caz: {o.subject}" if o else ""
    except Exception:
        pass
    return ""


def parse_date(s: str):
    s = (s or "").strip()
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


# ---------------- auth ----------------
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(request, "login.html", {"request": request})


@app.post("/login")
def login_post(request: Request, email: str = Form(""),
               password: str = Form(""), db: Session = Depends(get_db)):
    user = db.query(User).filter(func.lower(User.email) == email.strip().lower()).first()
    if not user or not user.active or not verify_password(password, user.pw_hash):
        return templates.TemplateResponse(
            request, "login.html", {"request": request,
                                    "error": "Email sau parolă incorectă."},
            status_code=401)
    login_user(request, user)
    return RedirectResponse("/", status_code=303)


@app.get("/logout")
def logout(request: Request):
    logout_user(request)
    return RedirectResponse("/login", status_code=303)


# ---------------- dashboard ----------------
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db),
              user: User = Depends(require_login)):
    open_q = db.query(Opportunity).filter(Opportunity.stage.in_(OPEN_STAGES))
    pipeline_val = open_q.with_entities(func.coalesce(func.sum(Opportunity.amount), 0)).scalar()
    opps_open = open_q.count()
    first = date.today().replace(day=1)
    leads_month = db.query(Lead).filter(Lead.created_at >= datetime(first.year, first.month, 1)).count()
    cases_open = db.query(Case).filter(Case.status.in_(["nou", "deschis", "in_asteptare"])).count()

    stage_labels, stage_vals = [], []
    for key, label in STAGES:
        stage_labels.append(label)
        v = db.query(func.coalesce(func.sum(Opportunity.amount), 0)).filter(
            Opportunity.stage == key).scalar()
        stage_vals.append(round(float(v or 0), 2))

    ls_labels = [l for _, l in LEAD_STATUS]
    ls_vals = [db.query(Lead).filter(Lead.status == k).count() for k, _ in LEAD_STATUS]

    pr_labels = [l for _, l in PRIORITIES]
    pr_vals = [db.query(Case).filter(Case.priority == k).count() for k, _ in PRIORITIES]

    recent = db.query(Activity).order_by(Activity.created_at.desc()).limit(8).all()
    my_tasks = (db.query(Activity)
                .filter(Activity.owner_id == user.id, Activity.tip == "sarcina",
                        Activity.status == "deschis")
                .order_by(Activity.due_date.is_(None), Activity.due_date).limit(10).all())
    for t in my_tasks + recent:
        t.related_label = related_label(db, t.related_kind, t.related_id)

    return templates.TemplateResponse(request, "dashboard.html", ctx(
        request, db, user, pipeline_val=pipeline_val, opps_open=opps_open,
        leads_month=leads_month, cases_open=cases_open,
        stage_labels=stage_labels, stage_vals=stage_vals,
        ls_labels=ls_labels, ls_vals=ls_vals,
        pr_labels=pr_labels, pr_vals=pr_vals,
        recent=recent, my_tasks=my_tasks, today=date.today(),
        active="dashboard"))


# ---------------- leaduri ----------------
@app.get("/leaduri", response_class=HTMLResponse)
def leaduri_list(request: Request, q: str = "", status: str = "",
                 db: Session = Depends(get_db), user: User = Depends(require_login)):
    query = db.query(Lead)
    if status:
        query = query.filter(Lead.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter((Lead.first_name.ilike(like)) |
                             (Lead.last_name.ilike(like)) |
                             (Lead.company.ilike(like)) |
                             (Lead.email.ilike(like)))
    leaduri = query.order_by(Lead.created_at.desc()).all()
    return templates.TemplateResponse(request, "leaduri_list.html",
                                      ctx(request, db, user, leaduri=leaduri,
                                          q=q, status=status, active="leaduri"))


@app.get("/leaduri/nou", response_class=HTMLResponse)
def lead_nou_form(request: Request, db: Session = Depends(get_db),
                  user: User = Depends(require_login)):
    users = db.query(User).filter_by(active=True).all()
    return templates.TemplateResponse(request, "lead_form.html",
                                      ctx(request, db, user, users=users,
                                          active="leaduri"))


@app.post("/leaduri/nou")
def lead_nou_post(request: Request, first_name: str = Form(""),
                  last_name: str = Form(""), company: str = Form(""),
                  email: str = Form(""), phone: str = Form(""),
                  status: str = Form("nou"), source: str = Form(""),
                  notes: str = Form(""), owner_id: int = Form(None),
                  db: Session = Depends(get_db), user: User = Depends(require_login)):
    lead = Lead(first_name=first_name.strip(), last_name=last_name.strip(),
                company=company.strip(), email=email.strip(), phone=phone.strip(),
                status=status, source=source.strip(), notes=notes.strip(),
                owner_id=owner_id or user.id)
    db.add(lead)
    db.flush()
    automation_lead_nou(db, lead)
    db.commit()
    return RedirectResponse(f"/leaduri/{lead.id}", status_code=303)


@app.get("/leaduri/{lid}", response_class=HTMLResponse)
def lead_detail(lid: int, request: Request, db: Session = Depends(get_db),
                user: User = Depends(require_login)):
    lead = db.get(Lead, lid)
    if not lead:
        return RedirectResponse("/leaduri", status_code=303)
    acts = related_activities(db, "lead", lid)
    for a in acts:
        a.related_label = ""
    return templates.TemplateResponse(request, "lead_detail.html",
                                      ctx(request, db, user, lead=lead,
                                          activitati=acts, active="leaduri"))


@app.get("/leaduri/{lid}/editeaza", response_class=HTMLResponse)
def lead_edit_form(lid: int, request: Request, db: Session = Depends(get_db),
                   user: User = Depends(require_login)):
    lead = db.get(Lead, lid)
    if not lead:
        return RedirectResponse("/leaduri", status_code=303)
    users = db.query(User).filter_by(active=True).all()
    return templates.TemplateResponse(request, "lead_form.html",
                                      ctx(request, db, user, lead=lead,
                                          users=users, active="leaduri"))


@app.post("/leaduri/{lid}/editeaza")
def lead_edit_post(lid: int, request: Request, first_name: str = Form(""),
                   last_name: str = Form(""), company: str = Form(""),
                   email: str = Form(""), phone: str = Form(""),
                   status: str = Form("nou"), source: str = Form(""),
                   notes: str = Form(""), owner_id: int = Form(None),
                   db: Session = Depends(get_db),
                   user: User = Depends(require_login)):
    lead = db.get(Lead, lid)
    if not lead:
        return RedirectResponse("/leaduri", status_code=303)
    lead.first_name = first_name.strip()
    lead.last_name = last_name.strip()
    lead.company = company.strip()
    lead.email = email.strip()
    lead.phone = phone.strip()
    lead.status = status
    lead.source = source.strip()
    lead.notes = notes.strip()
    if owner_id:
        lead.owner_id = owner_id
    db.commit()
    return RedirectResponse(f"/leaduri/{lid}", status_code=303)


@app.post("/leaduri/{lid}/sterge")
def lead_delete(lid: int, db: Session = Depends(get_db),
                user: User = Depends(require_login)):
    lead = db.get(Lead, lid)
    if lead:
        db.delete(lead)
        db.commit()
    return RedirectResponse("/leaduri", status_code=303)


@app.post("/leaduri/{lid}/converteste")
def lead_convert(lid: int, db: Session = Depends(get_db),
                 user: User = Depends(require_login)):
    lead = db.get(Lead, lid)
    if not lead:
        return RedirectResponse("/leaduri", status_code=303)
    owner_id = lead.owner_id or user.id
    account = Account(name=lead.company or f"Firma {lead.full_name}",
                      email=lead.email, phone=lead.phone, owner_id=owner_id)
    db.add(account)
    db.flush()
    contact = Contact(account_id=account.id, first_name=lead.first_name,
                      last_name=lead.last_name, email=lead.email,
                      phone=lead.phone, owner_id=owner_id)
    db.add(contact)
    db.flush()
    opp = Opportunity(name=f"Oportunitate — {account.name}",
                      account_id=account.id, contact_id=contact.id,
                      amount=0.0, stage="prospectare", probability=10,
                      owner_id=owner_id)
    db.add(opp)
    lead.status = "convertit"
    db.commit()
    return RedirectResponse(f"/oportunitati/{opp.id}", status_code=303)


# ---------------- firme ----------------
@app.get("/firme", response_class=HTMLResponse)
def firme_list(request: Request, q: str = "", db: Session = Depends(get_db),
               user: User = Depends(require_login)):
    query = db.query(Account)
    if q:
        like = f"%{q}%"
        query = query.filter((Account.name.ilike(like)) |
                             (Account.industry.ilike(like)) |
                             (Account.email.ilike(like)))
    firme = query.order_by(Account.name).all()
    return templates.TemplateResponse(request, "firme_list.html",
                                      ctx(request, db, user, firme=firme,
                                          q=q, active="firme"))


@app.get("/firme/nou", response_class=HTMLResponse)
def firma_nou_form(request: Request, db: Session = Depends(get_db),
                   user: User = Depends(require_login)):
    users = db.query(User).filter_by(active=True).all()
    return templates.TemplateResponse(request, "firma_form.html",
                                      ctx(request, db, user, users=users,
                                          active="firme"))


@app.post("/firme/nou")
def firma_nou_post(request: Request, name: str = Form(""),
                   industry: str = Form(""), website: str = Form(""),
                   phone: str = Form(""), email: str = Form(""),
                   address: str = Form(""), owner_id: int = Form(None),
                   db: Session = Depends(get_db),
                   user: User = Depends(require_login)):
    f = Account(name=name.strip(), industry=industry.strip(),
                website=website.strip(), phone=phone.strip(),
                email=email.strip(), address=address.strip(),
                owner_id=owner_id or user.id)
    db.add(f)
    db.commit()
    return RedirectResponse(f"/firme/{f.id}", status_code=303)


@app.get("/firme/{fid}", response_class=HTMLResponse)
def firma_detail(fid: int, request: Request, db: Session = Depends(get_db),
                 user: User = Depends(require_login)):
    f = db.get(Account, fid)
    if not f:
        return RedirectResponse("/firme", status_code=303)
    acts = related_activities(db, "firma", fid)
    return templates.TemplateResponse(request, "firma_detail.html",
                                      ctx(request, db, user, firma=f,
                                          activitati=acts, active="firme"))


@app.get("/firme/{fid}/editeaza", response_class=HTMLResponse)
def firma_edit_form(fid: int, request: Request, db: Session = Depends(get_db),
                    user: User = Depends(require_login)):
    f = db.get(Account, fid)
    if not f:
        return RedirectResponse("/firme", status_code=303)
    users = db.query(User).filter_by(active=True).all()
    return templates.TemplateResponse(request, "firma_form.html",
                                      ctx(request, db, user, firma=f,
                                          users=users, active="firme"))


@app.post("/firme/{fid}/editeaza")
def firma_edit_post(fid: int, request: Request, name: str = Form(""),
                    industry: str = Form(""), website: str = Form(""),
                    phone: str = Form(""), email: str = Form(""),
                    address: str = Form(""), owner_id: int = Form(None),
                    db: Session = Depends(get_db),
                    user: User = Depends(require_login)):
    f = db.get(Account, fid)
    if not f:
        return RedirectResponse("/firme", status_code=303)
    f.name = name.strip()
    f.industry = industry.strip()
    f.website = website.strip()
    f.phone = phone.strip()
    f.email = email.strip()
    f.address = address.strip()
    if owner_id:
        f.owner_id = owner_id
    db.commit()
    return RedirectResponse(f"/firme/{fid}", status_code=303)


@app.post("/firme/{fid}/sterge")
def firma_delete(fid: int, db: Session = Depends(get_db),
                 user: User = Depends(require_login)):
    f = db.get(Account, fid)
    if f:
        for c in f.contacts:
            c.account_id = None
        for o in f.opportunities:
            o.account_id = None
        for c in f.cases:
            c.account_id = None
        db.delete(f)
        db.commit()
    return RedirectResponse("/firme", status_code=303)


# ---------------- contacte ----------------
@app.get("/contacte", response_class=HTMLResponse)
def contacte_list(request: Request, q: str = "", db: Session = Depends(get_db),
                   user: User = Depends(require_login)):
    query = db.query(Contact)
    if q:
        like = f"%{q}%"
        query = query.filter((Contact.first_name.ilike(like)) |
                             (Contact.last_name.ilike(like)) |
                             (Contact.email.ilike(like)))
    contacte = query.order_by(Contact.last_name, Contact.first_name).all()
    return templates.TemplateResponse(request, "contacte_list.html",
                                      ctx(request, db, user, contacte=contacte,
                                          q=q, active="contacte"))


@app.get("/contacte/nou", response_class=HTMLResponse)
def contact_nou_form(request: Request, db: Session = Depends(get_db),
                     user: User = Depends(require_login)):
    firme = db.query(Account).order_by(Account.name).all()
    users = db.query(User).filter_by(active=True).all()
    return templates.TemplateResponse(request, "contact_form.html",
                                      ctx(request, db, user, firme=firme,
                                          users=users, active="contacte"))


@app.post("/contacte/nou")
def contact_nou_post(request: Request, first_name: str = Form(""),
                     last_name: str = Form(""), email: str = Form(""),
                     phone: str = Form(""), title: str = Form(""),
                     account_id: str = Form(""), owner_id: int = Form(None),
                     db: Session = Depends(get_db),
                     user: User = Depends(require_login)):
    c = Contact(first_name=first_name.strip(), last_name=last_name.strip(),
                email=email.strip(), phone=phone.strip(), title=title.strip(),
                account_id=int(account_id) if account_id else None,
                owner_id=owner_id or user.id)
    db.add(c)
    db.commit()
    return RedirectResponse(f"/contacte/{c.id}", status_code=303)


@app.get("/contacte/{cid}", response_class=HTMLResponse)
def contact_detail(cid: int, request: Request, db: Session = Depends(get_db),
                   user: User = Depends(require_login)):
    c = db.get(Contact, cid)
    if not c:
        return RedirectResponse("/contacte", status_code=303)
    acts = related_activities(db, "contact", cid)
    return templates.TemplateResponse(request, "contact_detail.html",
                                      ctx(request, db, user, contact=c,
                                          activitati=acts, active="contacte"))


@app.get("/contacte/{cid}/editeaza", response_class=HTMLResponse)
def contact_edit_form(cid: int, request: Request, db: Session = Depends(get_db),
                      user: User = Depends(require_login)):
    c = db.get(Contact, cid)
    if not c:
        return RedirectResponse("/contacte", status_code=303)
    firme = db.query(Account).order_by(Account.name).all()
    users = db.query(User).filter_by(active=True).all()
    return templates.TemplateResponse(request, "contact_form.html",
                                      ctx(request, db, user, contact=c,
                                          firme=firme, users=users,
                                          active="contacte"))


@app.post("/contacte/{cid}/editeaza")
def contact_edit_post(cid: int, request: Request, first_name: str = Form(""),
                      last_name: str = Form(""), email: str = Form(""),
                      phone: str = Form(""), title: str = Form(""),
                      account_id: str = Form(""), owner_id: int = Form(None),
                      db: Session = Depends(get_db),
                      user: User = Depends(require_login)):
    c = db.get(Contact, cid)
    if not c:
        return RedirectResponse("/contacte", status_code=303)
    c.first_name = first_name.strip()
    c.last_name = last_name.strip()
    c.email = email.strip()
    c.phone = phone.strip()
    c.title = title.strip()
    c.account_id = int(account_id) if account_id else None
    if owner_id:
        c.owner_id = owner_id
    db.commit()
    return RedirectResponse(f"/contacte/{cid}", status_code=303)


@app.post("/contacte/{cid}/sterge")
def contact_delete(cid: int, db: Session = Depends(get_db),
                   user: User = Depends(require_login)):
    c = db.get(Contact, cid)
    if c:
        for o in db.query(Opportunity).filter_by(contact_id=cid):
            o.contact_id = None
        for cs in db.query(Case).filter_by(contact_id=cid):
            cs.contact_id = None
        db.delete(c)
        db.commit()
    return RedirectResponse("/contacte", status_code=303)


# ---------------- oportunități ----------------
@app.get("/oportunitati", response_class=HTMLResponse)
def oportunitati_kanban(request: Request, db: Session = Depends(get_db),
                        user: User = Depends(require_login)):
    opps = db.query(Opportunity).order_by(Opportunity.amount.desc()).all()
    by_stage = {k: [] for k, _ in STAGES}
    for o in opps:
        by_stage.setdefault(o.stage, []).append(o)
    firme = db.query(Account).order_by(Account.name).all()
    contacte = db.query(Contact).order_by(Contact.last_name).all()
    users = db.query(User).filter_by(active=True).all()
    return templates.TemplateResponse(request, "oportunitati.html",
                                      ctx(request, db, user, by_stage=by_stage,
                                          firme=firme, contacte=contacte,
                                          users=users, today=date.today(),
                                          active="oportunitati"))


@app.post("/oportunitati/nou")
def oportunitate_nou_post(request: Request, name: str = Form(""),
                          account_id: str = Form(""),
                          contact_id: str = Form(""),
                          amount: float = Form(0.0), stage: str = Form("prospectare"),
                          probability: int = Form(10), close_date: str = Form(""),
                          owner_id: int = Form(None),
                          db: Session = Depends(get_db),
                          user: User = Depends(require_login)):
    o = Opportunity(name=name.strip(),
                    account_id=int(account_id) if account_id else None,
                    contact_id=int(contact_id) if contact_id else None,
                    amount=amount or 0.0, stage=stage,
                    probability=probability, close_date=parse_date(close_date),
                    owner_id=owner_id or user.id)
    db.add(o)
    db.flush()
    if o.stage == "castigat":
        automation_oportunitate_castigata(db, o)
    db.commit()
    return RedirectResponse("/oportunitati", status_code=303)


@app.get("/oportunitati/{oid}", response_class=HTMLResponse)
def oportunitate_detail(oid: int, request: Request,
                        db: Session = Depends(get_db),
                        user: User = Depends(require_login)):
    o = db.get(Opportunity, oid)
    if not o:
        return RedirectResponse("/oportunitati", status_code=303)
    acts = related_activities(db, "oportunitate", oid)
    return templates.TemplateResponse(request, "oportunitate_detail.html",
                                      ctx(request, db, user, opp=o,
                                          activitati=acts,
                                          active="oportunitati"))


@app.get("/oportunitati/{oid}/editeaza", response_class=HTMLResponse)
def oportunitate_edit_form(oid: int, request: Request,
                           db: Session = Depends(get_db),
                           user: User = Depends(require_login)):
    o = db.get(Opportunity, oid)
    if not o:
        return RedirectResponse("/oportunitati", status_code=303)
    firme = db.query(Account).order_by(Account.name).all()
    contacte = db.query(Contact).order_by(Contact.last_name).all()
    users = db.query(User).filter_by(active=True).all()
    return templates.TemplateResponse(request, "oportunitate_form.html",
                                      ctx(request, db, user, opp=o, firme=firme,
                                          contacte=contacte, users=users,
                                          active="oportunitati"))


@app.post("/oportunitati/{oid}/editeaza")
def oportunitate_edit_post(oid: int, request: Request, name: str = Form(""),
                           account_id: str = Form(""),
                           contact_id: str = Form(""),
                           amount: float = Form(0.0),
                           stage: str = Form("prospectare"),
                           probability: int = Form(10),
                           close_date: str = Form(""),
                           owner_id: int = Form(None),
                           db: Session = Depends(get_db),
                           user: User = Depends(require_login)):
    o = db.get(Opportunity, oid)
    if not o:
        return RedirectResponse("/oportunitati", status_code=303)
    o.name = name.strip()
    o.account_id = int(account_id) if account_id else None
    o.contact_id = int(contact_id) if contact_id else None
    o.amount = amount or 0.0
    set_opp_stage(db, o, stage)
    o.probability = probability
    o.close_date = parse_date(close_date)
    if owner_id:
        o.owner_id = owner_id
    db.commit()
    return RedirectResponse(f"/oportunitati/{oid}", status_code=303)


@app.post("/oportunitati/{oid}/sterge")
def oportunitate_delete(oid: int, db: Session = Depends(get_db),
                        user: User = Depends(require_login)):
    o = db.get(Opportunity, oid)
    if o:
        db.delete(o)
        db.commit()
    return RedirectResponse("/oportunitati", status_code=303)


@app.patch("/api/oportunitati/{oid}/stage")
async def oportunitate_stage_api(oid: int, request: Request,
                                 db: Session = Depends(get_db),
                                 user: User = Depends(get_current_user)):
    o = db.get(Opportunity, oid)
    if not o:
        return JSONResponse({"ok": False, "error": "Nu există."}, status_code=404)
    data = await request.json()
    new_stage = data.get("stage", "")
    if new_stage not in [k for k, _ in STAGES]:
        return JSONResponse({"ok": False, "error": "Stagiu invalid."}, status_code=400)
    set_opp_stage(db, o, new_stage)
    db.commit()
    return {"ok": True, "stage": o.stage, "probability": o.probability}


# ---------------- cazuri ----------------
@app.get("/cazuri", response_class=HTMLResponse)
def cazuri_list(request: Request, q: str = "", status: str = "",
                priority: str = "", db: Session = Depends(get_db),
                user: User = Depends(require_login)):
    query = db.query(Case)
    if status:
        query = query.filter(Case.status == status)
    if priority:
        query = query.filter(Case.priority == priority)
    if q:
        like = f"%{q}%"
        query = query.filter(Case.subject.ilike(like))
    cazuri = query.order_by(Case.created_at.desc()).all()
    return templates.TemplateResponse(request, "cazuri_list.html",
                                      ctx(request, db, user, cazuri=cazuri,
                                          q=q, status=status, priority=priority,
                                          active="cazuri"))


@app.get("/cazuri/nou", response_class=HTMLResponse)
def caz_nou_form(request: Request, db: Session = Depends(get_db),
                 user: User = Depends(require_login)):
    firme = db.query(Account).order_by(Account.name).all()
    contacte = db.query(Contact).order_by(Contact.last_name).all()
    users = db.query(User).filter_by(active=True).all()
    return templates.TemplateResponse(request, "caz_form.html",
                                      ctx(request, db, user, firme=firme,
                                          contacte=contacte, users=users,
                                          active="cazuri"))


@app.post("/cazuri/nou")
def caz_nou_post(request: Request, subject: str = Form(""),
                 description: str = Form(""), status: str = Form("nou"),
                 priority: str = Form("medie"), account_id: str = Form(""),
                 contact_id: str = Form(""), owner_id: int = Form(None),
                 db: Session = Depends(get_db),
                 user: User = Depends(require_login)):
    c = Case(subject=subject.strip(), description=description.strip(),
             status=status, priority=priority,
             account_id=int(account_id) if account_id else None,
             contact_id=int(contact_id) if contact_id else None,
             owner_id=owner_id or user.id)
    db.add(c)
    db.flush()
    if c.priority == "urgenta":
        automation_caz_urgent(db, c)
    db.commit()
    return RedirectResponse(f"/cazuri/{c.id}", status_code=303)


@app.get("/cazuri/{cid}", response_class=HTMLResponse)
def caz_detail(cid: int, request: Request, db: Session = Depends(get_db),
               user: User = Depends(require_login)):
    c = db.get(Case, cid)
    if not c:
        return RedirectResponse("/cazuri", status_code=303)
    acts = related_activities(db, "caz", cid)
    return templates.TemplateResponse(request, "caz_detail.html",
                                      ctx(request, db, user, caz=c,
                                          activitati=acts, active="cazuri"))


@app.post("/cazuri/{cid}/editeaza")
def caz_edit_post(cid: int, request: Request, subject: str = Form(""),
                  description: str = Form(""), status: str = Form("nou"),
                  priority: str = Form("medie"), account_id: str = Form(""),
                  contact_id: str = Form(""), owner_id: int = Form(None),
                  db: Session = Depends(get_db),
                  user: User = Depends(require_login)):
    c = db.get(Case, cid)
    if not c:
        return RedirectResponse("/cazuri", status_code=303)
    old_priority = c.priority
    c.subject = subject.strip()
    c.description = description.strip()
    c.status = status
    c.priority = priority
    c.account_id = int(account_id) if account_id else None
    c.contact_id = int(contact_id) if contact_id else None
    if owner_id:
        c.owner_id = owner_id
    db.flush()
    if old_priority != "urgenta" and priority == "urgenta":
        automation_caz_urgent(db, c)
    db.commit()
    return RedirectResponse(f"/cazuri/{cid}", status_code=303)


@app.post("/cazuri/{cid}/sterge")
def caz_delete(cid: int, db: Session = Depends(get_db),
               user: User = Depends(require_login)):
    c = db.get(Case, cid)
    if c:
        db.delete(c)
        db.commit()
    return RedirectResponse("/cazuri", status_code=303)


# ---------------- activități ----------------
@app.get("/activitati", response_class=HTMLResponse)
def activitati_list(request: Request, filtru: str = "mele",
                    status: str = "", db: Session = Depends(get_db),
                    user: User = Depends(require_login)):
    query = db.query(Activity)
    if filtru == "mele":
        query = query.filter(Activity.owner_id == user.id)
    if status:
        query = query.filter(Activity.status == status)
    acts = query.order_by(Activity.due_date.is_(None),
                          Activity.due_date).all()
    for a in acts:
        a.related_label = related_label(db, a.related_kind, a.related_id)
    return templates.TemplateResponse(request, "activitati.html",
                                      ctx(request, db, user, activitati=acts,
                                          filtru=filtru, status=status,
                                          today=date.today(),
                                          active="activitati"))


@app.get("/activitati/nou", response_class=HTMLResponse)
def activitate_nou_form(request: Request, related_kind: str = "",
                        related_id: str = "", db: Session = Depends(get_db),
                        user: User = Depends(require_login)):
    users = db.query(User).filter_by(active=True).all()
    entitati = {
        "lead": [(l.id, f"{l.full_name} ({l.company})") for l in
                 db.query(Lead).order_by(Lead.last_name).all()],
        "firma": [(f.id, f.name) for f in
                  db.query(Account).order_by(Account.name).all()],
        "contact": [(c.id, c.full_name) for c in
                    db.query(Contact).order_by(Contact.last_name).all()],
        "oportunitate": [(o.id, o.name) for o in
                         db.query(Opportunity).order_by(Opportunity.name).all()],
        "caz": [(c.id, c.subject) for c in
                db.query(Case).order_by(Case.created_at.desc()).all()],
    }
    return templates.TemplateResponse(request, "activitate_form.html",
                                      ctx(request, db, user, users=users,
                                          entitati=entitati,
                                          related_kind=related_kind,
                                          related_id=related_id,
                                          today=date.today(),
                                          active="activitati"))


@app.post("/activitati/nou")
def activitate_nou_post(request: Request, tip: str = Form("sarcina"),
                        subject: str = Form(""), description: str = Form(""),
                        due_date: str = Form(""),
                        related_kind: str = Form(""),
                        related_id: str = Form(""),
                        owner_id: int = Form(None),
                        back: str = Form("/activitati"),
                        db: Session = Depends(get_db),
                        user: User = Depends(require_login)):
    a = Activity(tip=tip, subject=subject.strip(),
                 description=description.strip(),
                 due_date=parse_date(due_date), status="deschis",
                 related_kind=related_kind,
                 related_id=int(related_id) if related_id else None,
                 owner_id=owner_id or user.id)
    db.add(a)
    db.commit()
    return RedirectResponse(back if back.startswith("/") else "/activitati",
                            status_code=303)


@app.post("/activitati/{aid}/comuta")
def activitate_toggle(aid: int, request: Request,
                      db: Session = Depends(get_db),
                      user: User = Depends(require_login)):
    a = db.get(Activity, aid)
    back = request.headers.get("referer", "/activitati")
    if a:
        a.status = "inchis" if a.status == "deschis" else "deschis"
        db.commit()
    return RedirectResponse(back, status_code=303)


@app.post("/activitati/{aid}/sterge")
def activitate_delete(aid: int, request: Request,
                      db: Session = Depends(get_db),
                      user: User = Depends(require_login)):
    a = db.get(Activity, aid)
    back = request.headers.get("referer", "/activitati")
    if a:
        db.delete(a)
        db.commit()
    return RedirectResponse(back, status_code=303)


# ---------------- utilizatori (admin) ----------------
@app.get("/utilizatori", response_class=HTMLResponse)
def utilizatori_list(request: Request, db: Session = Depends(get_db),
                     user: User = Depends(require_login),
                     admin: User = Depends(require_admin)):
    users = db.query(User).order_by(User.name).all()
    return templates.TemplateResponse(request, "utilizatori.html",
                                      ctx(request, db, user, users=users,
                                          active="utilizatori"))


@app.post("/utilizatori/nou")
def utilizator_nou(request: Request, name: str = Form(""),
                   email: str = Form(""), password: str = Form(""),
                   role: str = Form("vanzari"),
                   db: Session = Depends(get_db),
                   user: User = Depends(require_login),
                   admin: User = Depends(require_admin)):
    if not name.strip() or not email.strip() or not password:
        return RedirectResponse("/utilizatori", status_code=303)
    exists = db.query(User).filter(func.lower(User.email) == email.strip().lower()).first()
    if exists:
        return RedirectResponse("/utilizatori", status_code=303)
    u = User(name=name.strip(), email=email.strip(),
             pw_hash=hash_password(password), role=role, active=True)
    db.add(u)
    db.commit()
    return RedirectResponse("/utilizatori", status_code=303)


@app.post("/utilizatori/{uid}/comuta")
def utilizator_toggle(uid: int, db: Session = Depends(get_db),
                      user: User = Depends(require_login),
                      admin: User = Depends(require_admin)):
    u = db.get(User, uid)
    if u and u.id != user.id:  # nu te poți dezactiva singur
        u.active = not u.active
        db.commit()
    return RedirectResponse("/utilizatori", status_code=303)


# ---------------- setări ----------------
@app.get("/setari", response_class=HTMLResponse)
def setari_page(request: Request, db: Session = Depends(get_db),
                user: User = Depends(require_login)):
    automations = db.query(Automation).order_by(Automation.id).all()
    s = db.get(Setting, "nume_firma")
    return templates.TemplateResponse(request, "setari.html",
                                      ctx(request, db, user,
                                          automations=automations,
                                          nume_firma=s.value if s else "",
                                          active="setari"))


@app.post("/setari")
async def setari_post(request: Request, db: Session = Depends(get_db),
                      user: User = Depends(require_login)):
    form = await request.form()
    for a in db.query(Automation).all():
        a.enabled = f"auto_{a.key}" in form
    s = db.get(Setting, "nume_firma")
    if not s:
        s = Setting(key="nume_firma", value="")
        db.add(s)
    s.value = (form.get("nume_firma") or "").strip() or "CRM"
    db.commit()
    return RedirectResponse("/setari", status_code=303)


# ---------------- tokenuri API ----------------
@app.get("/setari/api", response_class=HTMLResponse)
def api_tokens_page(request: Request, db: Session = Depends(get_db),
                    user: User = Depends(require_login)):
    q = db.query(ApiToken).order_by(ApiToken.id.desc())
    tokens = q.all() if user.role == "admin" else q.filter(
        ApiToken.user_id == user.id).all()
    users = {u.id: u.name for u in db.query(User).all()}
    return templates.TemplateResponse(request, "api_tokens.html",
                                      ctx(request, db, user, tokens=tokens,
                                          users=users, new_token=None,
                                          active="setari"))


@app.post("/setari/api/nou")
def api_token_nou(request: Request, name: str = Form(""),
                  db: Session = Depends(get_db),
                  user: User = Depends(require_login)):
    plain = generate_token()
    tok = ApiToken(user_id=user.id, name=name.strip() or "Token API",
                   token_hash=hash_token(plain), prefix=plain[:12])
    db.add(tok)
    db.commit()
    q = db.query(ApiToken).order_by(ApiToken.id.desc())
    tokens = q.all() if user.role == "admin" else q.filter(
        ApiToken.user_id == user.id).all()
    users = {u.id: u.name for u in db.query(User).all()}
    return templates.TemplateResponse(request, "api_tokens.html",
                                      ctx(request, db, user, tokens=tokens,
                                          users=users, new_token=plain,
                                          active="setari"))


@app.post("/setari/api/{tid}/revoca")
def api_token_revoca(tid: int, db: Session = Depends(get_db),
                     user: User = Depends(require_login)):
    tok = db.get(ApiToken, tid)
    if tok and (tok.user_id == user.id or user.role == "admin"):
        tok.active = False
        db.commit()
    return RedirectResponse("/setari/api", status_code=303)
