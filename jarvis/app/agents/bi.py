"""Agentul BI — Business Intelligence (funcțional din Faza 3).

Dashboard executiv, raport zilnic, snapshot-uri KPI pentru trenduri.
"""
from .. import audit, finante
from ..i18n import t
from .base import Agent


class AgentBI(Agent):
    key = "bi"
    nume = "Business Intelligence"
    descriere = "Dashboard executiv, starea companiei în timp real, trenduri."
    faza = "3"

    def executa(self, actiune: str, payload: dict, solicitat_de: str) -> dict:
        lang = payload.get("lang", "ro")

        if actiune in ("dashboard", "raport_zilnic"):
            r = finante.rezumat()
            audit.inregistreaza(solicitat_de, f"bi_{actiune}", "dashboard generat")
            return {"status": "ok", "mesaj": self._text_dashboard(r, lang), "kpi": r}

        if actiune == "snapshot":
            r = finante.snapshot_kpi()
            return {"status": "ok",
                    "mesaj": t("bot_snapshot_ok", lang),
                    "kpi": r}

        return {"status": "esuat",
                "mesaj": f"Acțiunea '{actiune}' nu e implementată la BI."}

    def _text_dashboard(self, r: dict, lang: str) -> str:
        top = "\n".join(f"• {n}: {v:.2f} EUR" for n, v in r["top_clienti"]) or "—"
        n = r["facturi_emise_luna"]
        fact_txt = f"{n} " + ("factură" if lang == "ro" and n == 1 else
                              "facture" if lang == "fr" and n == 1 else
                              "facturi" if lang == "ro" else "factures")
        return t("bot_dashboard", lang).format(
            incasari_azi=r["incasari_azi"], facturat_luna=r["facturat_luna"],
            facturi_txt=fact_txt, restante_nr=r["restante_nr"],
            restante_total=r["restante_total"], curse_azi=r["curse_finalizate_azi"],
            tva=r["tva_luna"], anomalii=r["anomalii_nr"], top=top)
