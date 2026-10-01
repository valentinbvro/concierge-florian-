"""API REST v1 al CRM-ului.

Autentificare: header-ul ``Authorization: Bearer <token>``.
Tokenurile se creează din interfața web (/setari/api) și se trimit
doar pe HTTPS în producție.
"""
import hashlib
import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from .db import get_db
from .models import (Account, Activity, ApiToken, Case, Contact, Lead,
                     Opportunity, User)

router = APIRouter(prefix="/api/v1", tags=["API v1"])

TOKEN_PREFIX = "crm_"

# --- liste de valori acceptate ---
STAGE_LIST = ["prospectare", "calificare", "propunere", "negociere",
              "castigat", "pierdut"]
LEAD_STATUS_LIST = ["nou", "contactat", "calificat", "convertit", "pierdut"]
CASE_STATUS_LIST = ["nou", "deschis", "in_asteptare", "rezolvat", "inchis"]
PRIORITY_LIST = ["scazuta", "medie", "ridicata", "urgenta"]
TIPURI_LIST = ["sarcina", "apel", "email", "intalnire"]
ACT_STATUS_LIST = ["deschis", "inchis"]
REL_KIND_LIST = ["lead", "firma", "contact", "oportunitate", "caz"]


# ---------------- tokenuri ----------------
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_token() -> str:
    """Generează un token nou (se afișează o singură dată)."""
    return TOKEN_PREFIX + secrets.token_urlsafe(32)


def get_api_user(request: Request,
                 db: Session = Depends(get_db)) -> User:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Lipsește header-ul Authorization: Bearer <token>.")
    digest = hash_token(auth[7:].strip())
    tok = (db.query(ApiToken)
             .filter(ApiToken.token_hash == digest,
                     ApiToken.active.is_(True)).first())
    if not tok or not tok.user or not tok.user.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token invalid sau revocat.")
    tok.last_used_at = datetime.now()
    db.commit()
    return tok.user


def _check(value: str, allowed: list, field: str):
    if value not in allowed:
        raise HTTPException(status_code=422, detail={
            "field": field,
            "error": f"Valoare invalidă. Acceptate: {', '.join(allowed)}."})


# ---------------- serializare ----------------
def _iso(v):
    return v.isoformat() if v else None


def lead_dict(l: Lead) -> dict:
    return {"id": l.id, "first_name": l.first_name, "last_name": l.last_name,
            "full_name": l.full_name, "company": l.company, "email": l.email,
            "phone": l.phone, "status": l.status, "source": l.source,
            "notes": l.notes, "owner_id": l.owner_id,
            "created_at": _iso(l.created_at)}


def account_dict(a: Account) -> dict:
    return {"id": a.id, "name": a.name, "industry": a.industry,
            "website": a.website, "phone": a.phone, "email": a.email,
            "address": a.address, "owner_id": a.owner_id,
            "created_at": _iso(a.created_at)}


def contact_dict(c: Contact) -> dict:
    return {"id": c.id, "first_name": c.first_name, "last_name": c.last_name,
            "full_name": c.full_name, "account_id": c.account_id,
            "email": c.email, "phone": c.phone, "title": c.title,
            "owner_id": c.owner_id, "created_at": _iso(c.created_at)}


def opp_dict(o: Opportunity) -> dict:
    return {"id": o.id, "name": o.name, "account_id": o.account_id,
            "contact_id": o.contact_id, "amount": o.amount, "stage": o.stage,
            "probability": o.probability, "close_date": _iso(o.close_date),
            "owner_id": o.owner_id, "created_at": _iso(o.created_at)}


def activity_dict(a: Activity) -> dict:
    return {"id": a.id, "tip": a.tip, "subject": a.subject,
            "description": a.description, "due_date": _iso(a.due_date),
            "status": a.status, "related_kind": a.related_kind,
            "related_id": a.related_id, "owner_id": a.owner_id,
            "created_at": _iso(a.created_at)}


def case_dict(c: Case) -> dict:
    return {"id": c.id, "account_id": c.account_id,
            "contact_id": c.contact_id, "subject": c.subject,
            "description": c.description, "status": c.status,
            "priority": c.priority, "owner_id": c.owner_id,
            "created_at": _iso(c.created_at)}


def page(items: list, total: int, limit: int, offset: int) -> dict:
    return {"items": items, "total": total, "limit": limit, "offset": offset}


def _main():
    """Acces leneș la funcțiile din main (automatizări) — evită importul circular."""
    from . import main
    return main


# ---------------- scheme Pydantic ----------------
class _Base(BaseModel):
    model_config = ConfigDict(extra="ignore")


class LeadIn(_Base):
    first_name: str
    last_name: str = ""
    company: str = ""
    email: str = ""
    phone: str = ""
    status: str = "nou"
    source: str = ""
    notes: str = ""
    owner_id: int | None = None


class LeadPatch(_Base):
    first_name: str | None = None
    last_name: str | None = None
    company: str | None = None
    email: str | None = None
    phone: str | None = None
    status: str | None = None
    source: str | None = None
    notes: str | None = None
    owner_id: int | None = None


class AccountIn(_Base):
    name: str
    industry: str = ""
    website: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    owner_id: int | None = None


class AccountPatch(_Base):
    name: str | None = None
    industry: str | None = None
    website: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    owner_id: int | None = None


class ContactIn(_Base):
    first_name: str
    last_name: str = ""
    account_id: int | None = None
    email: str = ""
    phone: str = ""
    title: str = ""
    owner_id: int | None = None


class ContactPatch(_Base):
    first_name: str | None = None
    last_name: str | None = None
    account_id: int | None = None
    email: str | None = None
    phone: str | None = None
    title: str | None = None
    owner_id: int | None = None


class OppIn(_Base):
    name: str
    account_id: int | None = None
    contact_id: int | None = None
    amount: float = 0.0
    stage: str = "prospectare"
    probability: int = 10
    close_date: str | None = None  # YYYY-MM-DD
    owner_id: int | None = None


class OppPatch(_Base):
    name: str | None = None
    account_id: int | None = None
    contact_id: int | None = None
    amount: float | None = None
    stage: str | None = None
    probability: int | None = None
    close_date: str | None = None
    owner_id: int | None = None


class CaseIn(_Base):
    subject: str
    account_id: int | None = None
    contact_id: int | None = None
    description: str = ""
    status: str = "nou"
    priority: str = "medie"
    owner_id: int | None = None


class CasePatch(_Base):
    subject: str | None = None
    account_id: int | None = None
    contact_id: int | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    owner_id: int | None = None


class ActivityIn(_Base):
    subject: str
    tip: str = "sarcina"
    description: str = ""
    due_date: str | None = None  # YYYY-MM-DD
    status: str = "deschis"
    related_kind: str = ""
    related_id: int | None = None
    owner_id: int | None = None


class ActivityPatch(_Base):
    subject: str | None = None
    tip: str | None = None
    description: str | None = None
    due_date: str | None = None
    status: str | None = None
    related_kind: str | None = None
    related_id: int | None = None
    owner_id: int | None = None


# ---------------- helpers endpointuri ----------------
def _get_or_404(db: Session, model, rid: int, name: str):
    obj = db.get(model, rid)
    if not obj:
        raise HTTPException(status_code=404, detail=f"{name} inexistent(ă).")
    return obj


def _owner(data_owner: int | None, user: User) -> int:
    return data_owner or user.id


def _parse_date(s: str | None, field: str):
    if s is None or s == "":
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=422, detail={
            "field": field, "error": "Format dată invalid. Folosește YYYY-MM-DD."})


def _apply_patch(obj, data: BaseModel, allowed: list):
    for f in allowed:
        v = getattr(data, f, None)
        if f in data.model_fields_set and v is not None:
            setattr(obj, f, v)


# ---------------- sumar ----------------
@router.get("/sumar")
def sumar(db: Session = Depends(get_db),
          user: User = Depends(get_api_user)):
    open_stages = ["prospectare", "calificare", "propunere", "negociere"]
    pipeline = (db.query(func.coalesce(func.sum(Opportunity.amount), 0))
                .filter(Opportunity.stage.in_(open_stages)).scalar())
    opp_deschise = (db.query(func.count(Opportunity.id))
                    .filter(Opportunity.stage.in_(open_stages)).scalar())
    luna = datetime.now().strftime("%Y-%m")
    leaduri_noi = (db.query(func.count(Lead.id))
                   .filter(func.strftime("%Y-%m", Lead.created_at) == luna)
                   .scalar())
    cazuri_deschise = (db.query(func.count(Case.id))
                       .filter(Case.status.in_(["nou", "deschis", "in_asteptare"]))
                       .scalar())
    return {"pipeline_deschis": round(float(pipeline), 2),
            "oportunitati_deschise": opp_deschise,
            "leaduri_noi_luna": leaduri_noi,
            "cazuri_deschise": cazuri_deschise}


# ---------------- leaduri ----------------
@router.get("/leaduri")
def api_leaduri(q: str = Query(""), status: str = Query(""),
                limit: int = Query(50, le=200), offset: int = Query(0, ge=0),
                db: Session = Depends(get_db),
                user: User = Depends(get_api_user)):
    query = db.query(Lead)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Lead.first_name.ilike(like),
                                 Lead.last_name.ilike(like),
                                 Lead.company.ilike(like),
                                 Lead.email.ilike(like)))
    if status:
        _check(status, LEAD_STATUS_LIST, "status")
        query = query.filter(Lead.status == status)
    total = query.count()
    items = query.order_by(Lead.id.desc()).limit(limit).offset(offset).all()
    return page([lead_dict(i) for i in items], total, limit, offset)


@router.post("/leaduri", status_code=201)
def api_lead_nou(data: LeadIn, db: Session = Depends(get_db),
                 user: User = Depends(get_api_user)):
    _check(data.status, LEAD_STATUS_LIST, "status")
    lead = Lead(first_name=data.first_name.strip(),
                last_name=data.last_name.strip(),
                company=data.company.strip(), email=data.email.strip(),
                phone=data.phone.strip(), status=data.status,
                source=data.source.strip(), notes=data.notes.strip(),
                owner_id=_owner(data.owner_id, user))
    db.add(lead)
    db.flush()
    _main().automation_lead_nou(db, lead)
    db.commit()
    return lead_dict(lead)


@router.get("/leaduri/{lid}")
def api_lead(lid: int, db: Session = Depends(get_db),
             user: User = Depends(get_api_user)):
    return lead_dict(_get_or_404(db, Lead, lid, "Leadul"))


@router.patch("/leaduri/{lid}")
def api_lead_patch(lid: int, data: LeadPatch,
                   db: Session = Depends(get_db),
                   user: User = Depends(get_api_user)):
    lead = _get_or_404(db, Lead, lid, "Leadul")
    if "status" in data.model_fields_set and data.status is not None:
        _check(data.status, LEAD_STATUS_LIST, "status")
    _apply_patch(lead, data, ["first_name", "last_name", "company", "email",
                              "phone", "status", "source", "notes", "owner_id"])
    db.commit()
    return lead_dict(lead)


@router.post("/leaduri/{lid}/converteste")
def api_lead_convert(lid: int, db: Session = Depends(get_db),
                     user: User = Depends(get_api_user)):
    lead = _get_or_404(db, Lead, lid, "Leadul")
    if lead.status == "convertit":
        raise HTTPException(status_code=400,
                            detail="Leadul e deja convertit.")
    owner_id = lead.owner_id or user.id
    account = Account(name=lead.company or f"Firmă {lead.full_name}",
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
    return {"lead": lead_dict(lead), "firma": account_dict(account),
            "contact": contact_dict(contact),
            "oportunitate": opp_dict(opp)}


@router.delete("/leaduri/{lid}", status_code=204)
def api_lead_delete(lid: int, db: Session = Depends(get_db),
                    user: User = Depends(get_api_user)):
    db.delete(_get_or_404(db, Lead, lid, "Leadul"))
    db.commit()
    return None


# ---------------- firme ----------------
@router.get("/firme")
def api_firme(q: str = Query(""), limit: int = Query(50, le=200),
              offset: int = Query(0, ge=0), db: Session = Depends(get_db),
              user: User = Depends(get_api_user)):
    query = db.query(Account)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Account.name.ilike(like),
                                 Account.email.ilike(like)))
    total = query.count()
    items = query.order_by(Account.id.desc()).limit(limit).offset(offset).all()
    return page([account_dict(i) for i in items], total, limit, offset)


@router.post("/firme", status_code=201)
def api_firma_nou(data: AccountIn, db: Session = Depends(get_db),
                  user: User = Depends(get_api_user)):
    a = Account(name=data.name.strip(), industry=data.industry.strip(),
                website=data.website.strip(), phone=data.phone.strip(),
                email=data.email.strip(), address=data.address.strip(),
                owner_id=_owner(data.owner_id, user))
    db.add(a)
    db.commit()
    return account_dict(a)


@router.get("/firme/{fid}")
def api_firma(fid: int, db: Session = Depends(get_db),
              user: User = Depends(get_api_user)):
    return account_dict(_get_or_404(db, Account, fid, "Firma"))


@router.patch("/firme/{fid}")
def api_firma_patch(fid: int, data: AccountPatch,
                    db: Session = Depends(get_db),
                    user: User = Depends(get_api_user)):
    a = _get_or_404(db, Account, fid, "Firma")
    _apply_patch(a, data, ["name", "industry", "website", "phone", "email",
                           "address", "owner_id"])
    db.commit()
    return account_dict(a)


@router.delete("/firme/{fid}", status_code=204)
def api_firma_delete(fid: int, db: Session = Depends(get_db),
                     user: User = Depends(get_api_user)):
    db.delete(_get_or_404(db, Account, fid, "Firma"))
    db.commit()
    return None


# ---------------- contacte ----------------
@router.get("/contacte")
def api_contacte(q: str = Query(""), limit: int = Query(50, le=200),
                 offset: int = Query(0, ge=0), db: Session = Depends(get_db),
                 user: User = Depends(get_api_user)):
    query = db.query(Contact)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Contact.first_name.ilike(like),
                                 Contact.last_name.ilike(like),
                                 Contact.email.ilike(like)))
    total = query.count()
    items = query.order_by(Contact.id.desc()).limit(limit).offset(offset).all()
    return page([contact_dict(i) for i in items], total, limit, offset)


@router.post("/contacte", status_code=201)
def api_contact_nou(data: ContactIn, db: Session = Depends(get_db),
                    user: User = Depends(get_api_user)):
    c = Contact(first_name=data.first_name.strip(),
                last_name=data.last_name.strip(),
                account_id=data.account_id, email=data.email.strip(),
                phone=data.phone.strip(), title=data.title.strip(),
                owner_id=_owner(data.owner_id, user))
    db.add(c)
    db.commit()
    return contact_dict(c)


@router.get("/contacte/{cid}")
def api_contact(cid: int, db: Session = Depends(get_db),
                user: User = Depends(get_api_user)):
    return contact_dict(_get_or_404(db, Contact, cid, "Contactul"))


@router.patch("/contacte/{cid}")
def api_contact_patch(cid: int, data: ContactPatch,
                      db: Session = Depends(get_db),
                      user: User = Depends(get_api_user)):
    c = _get_or_404(db, Contact, cid, "Contactul")
    _apply_patch(c, data, ["first_name", "last_name", "account_id", "email",
                           "phone", "title", "owner_id"])
    db.commit()
    return contact_dict(c)


@router.delete("/contacte/{cid}", status_code=204)
def api_contact_delete(cid: int, db: Session = Depends(get_db),
                       user: User = Depends(get_api_user)):
    db.delete(_get_or_404(db, Contact, cid, "Contactul"))
    db.commit()
    return None


# ---------------- oportunitati ----------------
@router.get("/oportunitati")
def api_oportunitati(q: str = Query(""), stage: str = Query(""),
                     limit: int = Query(50, le=200),
                     offset: int = Query(0, ge=0),
                     db: Session = Depends(get_db),
                     user: User = Depends(get_api_user)):
    query = db.query(Opportunity)
    if q:
        query = query.filter(Opportunity.name.ilike(f"%{q}%"))
    if stage:
        _check(stage, STAGE_LIST, "stage")
        query = query.filter(Opportunity.stage == stage)
    total = query.count()
    items = (query.order_by(Opportunity.id.desc())
             .limit(limit).offset(offset).all())
    return page([opp_dict(i) for i in items], total, limit, offset)


@router.post("/oportunitati", status_code=201)
def api_opp_nou(data: OppIn, db: Session = Depends(get_db),
                user: User = Depends(get_api_user)):
    _check(data.stage, STAGE_LIST, "stage")
    o = Opportunity(name=data.name.strip(), account_id=data.account_id,
                    contact_id=data.contact_id, amount=data.amount,
                    stage=data.stage, probability=data.probability,
                    close_date=_parse_date(data.close_date, "close_date"),
                    owner_id=_owner(data.owner_id, user))
    db.add(o)
    db.commit()
    return opp_dict(o)


@router.get("/oportunitati/{oid}")
def api_opp(oid: int, db: Session = Depends(get_db),
            user: User = Depends(get_api_user)):
    return opp_dict(_get_or_404(db, Opportunity, oid, "Oportunitatea"))


@router.patch("/oportunitati/{oid}")
def api_opp_patch(oid: int, data: OppPatch, db: Session = Depends(get_db),
                  user: User = Depends(get_api_user)):
    o = _get_or_404(db, Opportunity, oid, "Oportunitatea")
    fields = data.model_fields_set
    if "stage" in fields and data.stage is not None:
        _check(data.stage, STAGE_LIST, "stage")
        _main().set_opp_stage(db, o, data.stage)  # + automatizare la câștig
    if "close_date" in fields:
        o.close_date = _parse_date(data.close_date, "close_date")
    _apply_patch(o, data, ["name", "account_id", "contact_id", "amount",
                           "probability", "owner_id"])
    db.commit()
    return opp_dict(o)


@router.delete("/oportunitati/{oid}", status_code=204)
def api_opp_delete(oid: int, db: Session = Depends(get_db),
                   user: User = Depends(get_api_user)):
    db.delete(_get_or_404(db, Opportunity, oid, "Oportunitatea"))
    db.commit()
    return None


# ---------------- cazuri ----------------
@router.get("/cazuri")
def api_cazuri(q: str = Query(""), status: str = Query(""),
               priority: str = Query(""), limit: int = Query(50, le=200),
               offset: int = Query(0, ge=0), db: Session = Depends(get_db),
               user: User = Depends(get_api_user)):
    query = db.query(Case)
    if q:
        query = query.filter(Case.subject.ilike(f"%{q}%"))
    if status:
        _check(status, CASE_STATUS_LIST, "status")
        query = query.filter(Case.status == status)
    if priority:
        _check(priority, PRIORITY_LIST, "priority")
        query = query.filter(Case.priority == priority)
    total = query.count()
    items = query.order_by(Case.id.desc()).limit(limit).offset(offset).all()
    return page([case_dict(i) for i in items], total, limit, offset)


@router.post("/cazuri", status_code=201)
def api_caz_nou(data: CaseIn, db: Session = Depends(get_db),
                user: User = Depends(get_api_user)):
    _check(data.status, CASE_STATUS_LIST, "status")
    _check(data.priority, PRIORITY_LIST, "priority")
    c = Case(subject=data.subject.strip(), account_id=data.account_id,
             contact_id=data.contact_id, description=data.description.strip(),
             status=data.status, priority=data.priority,
             owner_id=_owner(data.owner_id, user))
    db.add(c)
    db.flush()
    _main().automation_caz_urgent(db, c)
    db.commit()
    return case_dict(c)


@router.get("/cazuri/{cid}")
def api_caz(cid: int, db: Session = Depends(get_db),
            user: User = Depends(get_api_user)):
    return case_dict(_get_or_404(db, Case, cid, "Cazul"))


@router.patch("/cazuri/{cid}")
def api_caz_patch(cid: int, data: CasePatch, db: Session = Depends(get_db),
                  user: User = Depends(get_api_user)):
    c = _get_or_404(db, Case, cid, "Cazul")
    if "status" in data.model_fields_set and data.status is not None:
        _check(data.status, CASE_STATUS_LIST, "status")
    if "priority" in data.model_fields_set and data.priority is not None:
        _check(data.priority, PRIORITY_LIST, "priority")
    _apply_patch(c, data, ["subject", "account_id", "contact_id",
                           "description", "status", "priority", "owner_id"])
    db.commit()
    return case_dict(c)


@router.delete("/cazuri/{cid}", status_code=204)
def api_caz_delete(cid: int, db: Session = Depends(get_db),
                   user: User = Depends(get_api_user)):
    db.delete(_get_or_404(db, Case, cid, "Cazul"))
    db.commit()
    return None


# ---------------- activitati ----------------
@router.get("/activitati")
def api_activitati(q: str = Query(""), status: str = Query(""),
                   limit: int = Query(50, le=200),
                   offset: int = Query(0, ge=0),
                   db: Session = Depends(get_db),
                   user: User = Depends(get_api_user)):
    query = db.query(Activity)
    if q:
        query = query.filter(Activity.subject.ilike(f"%{q}%"))
    if status:
        _check(status, ACT_STATUS_LIST, "status")
        query = query.filter(Activity.status == status)
    total = query.count()
    items = (query.order_by(Activity.id.desc())
             .limit(limit).offset(offset).all())
    return page([activity_dict(i) for i in items], total, limit, offset)


@router.post("/activitati", status_code=201)
def api_activitate_nou(data: ActivityIn, db: Session = Depends(get_db),
                       user: User = Depends(get_api_user)):
    _check(data.tip, TIPURI_LIST, "tip")
    _check(data.status, ACT_STATUS_LIST, "status")
    if data.related_kind:
        _check(data.related_kind, REL_KIND_LIST, "related_kind")
    a = Activity(tip=data.tip, subject=data.subject.strip(),
                 description=data.description.strip(),
                 due_date=_parse_date(data.due_date, "due_date"),
                 status=data.status, related_kind=data.related_kind,
                 related_id=data.related_id,
                 owner_id=_owner(data.owner_id, user))
    db.add(a)
    db.commit()
    return activity_dict(a)


@router.get("/activitati/{aid}")
def api_activitate(aid: int, db: Session = Depends(get_db),
                   user: User = Depends(get_api_user)):
    return activity_dict(_get_or_404(db, Activity, aid, "Activitatea"))


@router.patch("/activitati/{aid}")
def api_activitate_patch(aid: int, data: ActivityPatch,
                         db: Session = Depends(get_db),
                         user: User = Depends(get_api_user)):
    a = _get_or_404(db, Activity, aid, "Activitatea")
    fields = data.model_fields_set
    if "tip" in fields and data.tip is not None:
        _check(data.tip, TIPURI_LIST, "tip")
    if "status" in fields and data.status is not None:
        _check(data.status, ACT_STATUS_LIST, "status")
    if "related_kind" in fields and data.related_kind:
        _check(data.related_kind, REL_KIND_LIST, "related_kind")
    if "due_date" in fields:
        a.due_date = _parse_date(data.due_date, "due_date")
    _apply_patch(a, data, ["subject", "tip", "description", "status",
                           "related_kind", "related_id", "owner_id"])
    db.commit()
    return activity_dict(a)


@router.delete("/activitati/{aid}", status_code=204)
def api_activitate_delete(aid: int, db: Session = Depends(get_db),
                          user: User = Depends(get_api_user)):
    db.delete(_get_or_404(db, Activity, aid, "Activitatea"))
    db.commit()
    return None
