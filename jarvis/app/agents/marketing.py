"""Agentul 4 — Marketing & Media (funcțional din Faza 2).

Creează postări (ciornă), cere aprobare pentru publicare, generează plan editorial.
Publicarea efectivă pe canale necesită tokenii conturilor (ca la WhatsApp).
"""
from .. import approvals, marketing
from ..i18n import t
from .base import Agent


class MarketingAgent(Agent):
    key = "marketing"
    nume = "Marketing & Media"
    descriere = "Postări social media cu aprobare, plan editorial, KPI."
    faza = "2"

    def executa(self, actiune: str, payload: dict, solicitat_de: str) -> dict:
        lang = payload.get("lang", "ro")

        if actiune == "creeaza_postare":
            from datetime import datetime
            dp = payload.get("data_programata")
            data = None
            if dp:
                try:
                    data = datetime.fromisoformat(str(dp)[:16])
                except ValueError:
                    data = None
            p = marketing.adauga_postare(payload.get("canal", "instagram"),
                                         payload.get("text", ""), data)
            if payload.get("cere_aprobare"):
                ap = approvals.cere_aprobare(
                    tip="postare_publica",
                    titlu=f"Publicare postare #{p.id} ({p.canal})",
                    detalii=p.text[:500],
                    solicitat_de=solicitat_de)
                # legăm cererea de postare; la aprobare, main.py o marchează "aprobata"
                from ..db import SessionLocal
                from ..models import Postare
                db = SessionLocal()
                try:
                    db.query(Postare).get(p.id).approval_id = ap.id
                    db.commit()
                finally:
                    db.close()
                return {"status": "asteapta_aprobare",
                        "mesaj": t("bot_postare_aprobare", lang).format(id=p.id,
                                                                        canal=p.canal, ap=ap.id)}
            return {"status": "ok",
                    "mesaj": t("bot_postare_creata", lang).format(id=p.id, canal=p.canal)}

        if actiune == "plan_editorial":
            plan = marketing.plan_editorial(lang)
            linii = [f"• {z['zi']} ({z['canal']}): {z['text']}" for z in plan]
            return {"status": "ok",
                    "mesaj": t("bot_plan_editorial", lang).format(linii="\n".join(linii))}

        return {"status": "esuat",
                "mesaj": f"Acțiunea '{actiune}' nu e implementată la marketing."}
