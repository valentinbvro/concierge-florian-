"""Agentul 8 — Growth & Capital Allocation (funcțional din Faza 4).

Evaluare investiții (payback, ROI, verdict), scenarii de creștere proiectate din
cifrele reale, buget lunar planificat. Decizia de investiție (bani reali) trece
prin aprobare umană — agentul doar evaluează.
"""
from .. import approvals, audit, growth
from ..i18n import t
from .base import Agent


class AgentGrowth(Agent):
    key = "growth"
    nume = "Growth & Capital Allocation"
    descriere = "Evaluare investiții, scenarii, alocare buget."
    faza = "4"

    def executa(self, actiune: str, payload: dict, solicitat_de: str) -> dict:
        lang = payload.get("lang", "ro")

        if actiune == "evalueaza_investitie":
            inv = growth.evalueaza_investitie(
                payload.get("titlu", ""), payload.get("tip", "masina"),
                payload.get("cost", 0.0), payload.get("venit_lunar_estimat", 0.0),
                solicitat_de=solicitat_de)
            return {"status": "ok", "mesaj": self._analiza_txt(
                growth.analiza_investitie(inv), lang), "investitie_id": inv.id}

        if actiune == "lista_investitii":
            invs = growth.lista_investitii()
            if not invs:
                return {"status": "ok", "mesaj": t("bot_investitii_zero", lang)}
            linii = []
            for inv in invs:
                a = growth.analiza_investitie(inv)
                pb = f"{a['payback_luni']} luni" if a["payback_luni"] else "—"
                linii.append(f"• #{inv.id} {inv.titlu} — {inv.cost:.0f} EUR, "
                             f"payback {pb} [{a['verdict']}] ({inv.status})")
            return {"status": "ok",
                    "mesaj": t("bot_investitii_lista", lang).format(
                        n=len(invs), linii="\n".join(linii))}

        if actiune == "aproba_investitie":
            iid = int(payload.get("investitie_id", 0))
            invs = [x for x in growth.lista_investitii() if x.id == iid]
            if not invs or invs[0].status != "evaluare":
                return {"status": "esuat",
                        "mesaj": t("bot_investitie_inexistenta", lang).format(id=iid)}
            inv = invs[0]
            a = growth.analiza_investitie(inv)
            ap = approvals.cere_aprobare(
                tip="aprobare_investitie",
                titlu=f"Investiție: {inv.titlu} ({inv.cost:.0f} EUR)",
                detalii=f"Tip {inv.tip}, venit lunar estimat "
                        f"{inv.venit_lunar_estimat:.0f} EUR, payback "
                        f"{a['payback_luni'] or '—'} luni, verdict {a['verdict']}. "
                        f"Decizie cu impact financiar — necesită aprobare.",
                solicitat_de=solicitat_de)
            audit.inregistreaza(solicitat_de, "investitie_ceruta",
                                f"#{inv.id} → cererea #{ap.id}")
            growth.leaga_aprobare_investitie(inv.id, ap.id)
            return {"status": "asteapta_aprobare",
                    "mesaj": t("bot_investitie_ceruta", lang).format(
                        titlu=inv.titlu, ap=ap.id)}

        if actiune == "scenariu":
            s = growth.scenariu(float(payload.get("crestere_pct", 10)))
            return {"status": "ok",
                    "mesaj": t("bot_scenariu", lang).format(
                        pct=s["crestere_pct"], actual=s["facturat_luna_actual"],
                        proiectat=s["facturat_luna_proiectat"],
                        suplimentar=s["venit_suplimentar_luna"],
                        anual=s["venit_suplimentar_an"])}

        if actiune == "seteaza_buget":
            b = growth.seteaza_buget(payload.get("luna", ""),
                                     payload.get("categorie", "altele"),
                                     payload.get("planificat", 0.0))
            return {"status": "ok",
                    "mesaj": t("bot_buget_setat", lang).format(
                        luna=b.luna, categorie=b.categorie,
                        suma=b.planificat)}

        if actiune == "buget":
            r = growth.buget_luna(payload.get("luna"))
            linii = [f"• {c}: {v:.0f} EUR" for c, v in r["categorii"].items() if v > 0]
            acoperire = (f"{r['acoperire_pct']}%" if r["acoperire_pct"] is not None
                         else "—")
            return {"status": "ok",
                    "mesaj": t("bot_buget", lang).format(
                        luna=r["luna"], total=r["total_planificat"],
                        venituri=r["venituri_facturate"], acoperire=acoperire,
                        linii="\n".join(linii) or "—")}

        return {"status": "esuat",
                "mesaj": f"Acțiunea '{actiune}' nu e implementată la growth."}

    def _analiza_txt(self, a: dict, lang: str) -> str:
        pb = f"{a['payback_luni']} luni" if a["payback_luni"] else "—"
        roi = f"{a['roi_anual_pct']}%" if a["roi_anual_pct"] else "—"
        return t("bot_investitie_analiza", lang).format(
            titlu=a["titlu"], cost=a["cost"], venit=a["venit_lunar_estimat"],
            payback=pb, roi=roi, verdict=a["verdict"], id=a["id"])
