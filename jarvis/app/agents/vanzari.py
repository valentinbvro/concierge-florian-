"""Agentul 1 — Vânzări & Customer Service.

Faza 0: creează leaduri și activități în CRM, cere aprobări pentru oferte.
Faza 1: + catalog produse, oferte cu linii/TVA/PDF, scoring leaduri,
        calificare (status lead), ticketing (cazuri), pipeline.
"""
import json

from .. import approvals, catalog, oferte, scoring
from ..db import SessionLocal
from ..i18n import t
from ..models import Offer
from .base import Agent


class AgentVanzari(Agent):
    key = "vanzari"
    nume = "Vânzări & Customer Service"
    descriere = "Pipeline vânzări în 10 pași, ofertare, follow-up, fidelizare, suport clienți."
    faza = "1"

    def executa(self, actiune: str, payload: dict, solicitat_de: str) -> dict:
        lang = payload.get("lang", "ro")
        if actiune == "creeaza_lead":
            lead = self.crm.creeaza_lead(
                first_name=payload.get("first_name", "?"),
                last_name=payload.get("last_name", ""),
                phone=payload.get("phone", ""),
                email=payload.get("email", ""),
                company=payload.get("company", ""),
                source=payload.get("source", "jarvis"),
                notes=payload.get("notes", ""),
            )
            return {"status": "ok",
                    "mesaj": t("bot_lead_creat", lang).format(
                        nume=f"{lead.get('first_name','')} {lead.get('last_name','')}".strip(),
                        id=lead.get("id")),
                    "crm_refs": {"lead_id": lead.get("id")}}

        if actiune == "creeaza_activitate":
            act = self.crm.creeaza_activitate(
                subject=payload.get("subject", "Activitate din Jarvis"),
                tip=payload.get("tip", "sarcina"),
                description=payload.get("description", ""),
                related_kind=payload.get("related_kind", ""),
                related_id=payload.get("related_id"),
            )
            return {"status": "ok",
                    "mesaj": t("bot_activitate_creata", lang).format(id=act.get("id"),
                                                                      subiect=act.get("subject")),
                    "crm_refs": {"activitate_id": act.get("id")}}

        if actiune == "cere_oferta":
            # linii: [{produs, cantitate, pret?, discount?}] — prețul se ia din catalog dacă lipsește
            linii_in = payload.get("linii", [])
            linii, avertismente = [], []
            for l in linii_in:
                linie = dict(l)
                if not linie.get("pret"):
                    p = catalog.gaseste(str(linie.get("produs", "")))
                    if p:
                        linie["pret"] = p.pret
                    else:
                        avertismente.append(f"«{linie.get('produs')}» nu e în catalog — preț 0.")
                        linie["pret"] = 0
                linii.append(linie)
            client_nume = payload.get("client_nume", "")
            oferta = oferte.creeaza_ciorna(client_nume, linii,
                                           contact_ref=payload.get("contact_ref", ""),
                                           opportunity_id=payload.get("opportunity_id"))
            ap = approvals.cere_aprobare(
                tip="trimitere_oferta",
                titlu=f"Ofertă {oferta.numar} — total {oferta.total:.2f} EUR",
                detalii=f"Client: {client_nume or '—'}\n"
                        f"Linii: {json.dumps(json.loads(oferta.linii), ensure_ascii=False)}\n"
                        f"Subtotal {oferta.subtotal:.2f} + TVA {oferta.tva:.2f} = {oferta.total:.2f} EUR\n"
                        + ("\n".join(avertismente) if avertismente else "") +
                        "\nLa aprobare se generează PDF-ul.",
                solicitat_de=solicitat_de)
            db = SessionLocal()
            try:
                db.query(Offer).get(oferta.id).approval_id = ap.id
                db.commit()
            finally:
                db.close()
            return {"status": "asteapta_aprobare",
                    "mesaj": t("bot_oferta_gata", lang).format(numar=oferta.numar,
                                                               total=oferta.total, ap=ap.id),
                    "crm_refs": {"oferta_id": oferta.id, "aprobare_id": ap.id}}

        if actiune == "califica_lead":
            lid = int(payload.get("lead_id", 0))
            status = payload.get("status", "calificat")
            self.crm.actualizeaza_lead(lid, {"status": status})
            return {"status": "ok",
                    "mesaj": t("bot_lead_calificat", lang).format(id=lid, status=status)}

        if actiune == "creeaza_caz":
            caz = self.crm.creeaza_caz(
                subject=payload.get("subject", "Caz din Jarvis"),
                description=payload.get("description", ""),
                priority=payload.get("priority", "medie"))
            return {"status": "ok",
                    "mesaj": t("bot_caz_creat", lang).format(id=caz.get("id"),
                                                             subiect=caz.get("subject")),
                    "crm_refs": {"caz_id": caz.get("id")}}

        if actiune == "scor_leaduri":
            top = scoring.leaduri_cu_scor(self.crm)[:5]
            if not top:
                return {"status": "ok", "mesaj": t("bot_scor_gol", lang)}
            linii_txt = [f"#{l.get('id')} {l.get('first_name','')} {l.get('last_name','')}: "
                         f"{l['scor']}/100 ({l['clasa']})" for l in top]
            return {"status": "ok",
                    "mesaj": t("bot_scor_top", lang).format(linii="\n".join(linii_txt))}

        return {"status": "esuat", "mesaj": f"Acțiunea '{actiune}' nu e implementată încă la agentul de vânzări."}
