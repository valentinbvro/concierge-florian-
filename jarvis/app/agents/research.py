"""Agentul 5 — Market Research & Competitori (funcțional de bază din Faza 2).

Evidența competitorilor + jurnal de observații. Monitorizarea automată
vine într-o fază ulterioară.
"""
from .. import competitori
from ..i18n import t
from .base import Agent


class ResearchAgent(Agent):
    key = "research"
    nume = "Market Research & Competitori"
    descriere = "Evidența competitorilor și observații de piață."
    faza = "2"

    def executa(self, actiune: str, payload: dict, solicitat_de: str) -> dict:
        lang = payload.get("lang", "ro")

        if actiune == "adauga_competitor":
            c = competitori.adauga(payload.get("nume", ""),
                                   payload.get("website", ""),
                                   payload.get("servicii", ""))
            return {"status": "ok",
                    "mesaj": t("bot_competitor_adaugat", lang).format(nume=c.nume)}

        if actiune == "adauga_observatie":
            cid = int(payload.get("competitor_id", 0))
            c = competitori.adauga_observatie(cid, payload.get("text", ""))
            if not c:
                return {"status": "esuat",
                        "mesaj": t("bot_competitor_nu_exista", lang).format(id=cid)}
            return {"status": "ok",
                    "mesaj": t("bot_observatie_salvat", lang).format(nume=c.nume)}

        return {"status": "in_curand",
                "mesaj": "Monitorizarea automată a competitorilor vine într-o fază ulterioară. "
                         "Deocamdată pot ține evidența: «competitor nou: Nume»."}
