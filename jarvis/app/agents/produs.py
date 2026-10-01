"""Agentul 7 — Produs & Inovație (funcțional din Faza 4).

Bancă de idei, voturi, fișe de oportunitate cu estimări (investiție, venit lunar,
payback, ROI). Promovarea ideilor mature la oportunități.
"""
import re

from .. import approvals, produs
from ..i18n import t
from .base import Agent


class AgentProdus(Agent):
    key = "produs"
    nume = "Produs & Inovație"
    descriere = "Bancă de idei, oportunități servicii noi, dosare decizionale."
    faza = "4"

    def executa(self, actiune: str, payload: dict, solicitat_de: str) -> dict:
        lang = payload.get("lang", "ro")

        if actiune == "idee_noua":
            i = produs.adauga_idee(payload.get("titlu", ""), payload.get("descriere", ""),
                                   payload.get("categorie", "serviciu"),
                                   solicitat_de=solicitat_de)
            return {"status": "ok",
                    "mesaj": t("bot_idee_noua", lang).format(id=i.id, titlu=i.titlu),
                    "idee_id": i.id}

        if actiune == "lista_idei":
            idei = produs.lista_idei()
            if not idei:
                return {"status": "ok", "mesaj": t("bot_idei_zero", lang)}
            linii = [f"• #{i.id} [{i.scor}/10] {i.titlu} ({i.status})" for i in idei]
            return {"status": "ok",
                    "mesaj": t("bot_idei_lista", lang).format(n=len(idei),
                                                             linii="\n".join(linii))}

        if actiune == "voteaza_idee":
            i = produs.voteaza_idee(int(payload.get("idee_id", 0)),
                                    int(payload.get("scor", 0)))
            if not i:
                return {"status": "esuat",
                        "mesaj": t("bot_idee_inexistenta", lang).format(
                            id=payload.get("idee_id", 0))}
            return {"status": "ok",
                    "mesaj": t("bot_idee_vot", lang).format(titlu=i.titlu, scor=i.scor)}

        if actiune == "oportunitate_noua":
            o = produs.creeaza_oportunitate(
                payload.get("titlu", ""), payload.get("descriere", ""),
                payload.get("investitie_estimata", 0.0),
                payload.get("venit_lunar_estimat", 0.0),
                solicitat_de=solicitat_de)
            f = produs.fisa_oportunitate(o)
            return {"status": "ok", "mesaj": self._fisa_txt(f, lang),
                    "oportunitate_id": o.id}

        if actiune == "promoveaza_idee":
            o = produs.promoveaza_idee(int(payload.get("idee_id", 0)),
                                       float(payload.get("investitie_estimata", 0) or 0),
                                       float(payload.get("venit_lunar_estimat", 0) or 0),
                                       solicitat_de=solicitat_de)
            if not o:
                return {"status": "esuat",
                        "mesaj": t("bot_idee_inexistenta", lang).format(
                            id=payload.get("idee_id", 0))}
            return {"status": "ok", "mesaj": self._fisa_txt(produs.fisa_oportunitate(o), lang),
                    "oportunitate_id": o.id}

        if actiune == "lista_oportunitati":
            ops = produs.lista_oportunitati()
            if not ops:
                return {"status": "ok", "mesaj": t("bot_oportunitati_zero", lang)}
            linii = []
            for o in ops:
                f = produs.fisa_oportunitate(o)
                pb = f"{f['payback_luni']} luni" if f["payback_luni"] else "—"
                linii.append(f"• #{o.id} {o.titlu} — inv. {o.investitie_estimata:.0f} EUR, "
                             f"payback {pb} ({o.status})")
            return {"status": "ok",
                    "mesaj": t("bot_oportunitati_lista", lang).format(
                        n=len(ops), linii="\n".join(linii))}

        if actiune == "aproba_oportunitate":
            oid = int(payload.get("oportunitate_id", 0))
            ops = [x for x in produs.lista_oportunitati() if x.id == oid]
            if not ops or ops[0].status != "evaluare":
                return {"status": "esuat",
                        "mesaj": t("bot_oportunitate_inexistenta", lang).format(id=oid)}
            o = ops[0]
            f = produs.fisa_oportunitate(o)
            ap = approvals.cere_aprobare(
                tip="aprobare_oportunitate",
                titlu=f"Oportunitate: {o.titlu} (investiție estimată {o.investitie_estimata:.0f} EUR)",
                detalii=f"Venit lunar estimat {o.venit_lunar_estimat:.0f} EUR, payback "
                        f"{f['payback_luni'] or '—'} luni, ROI anual "
                        f"{f['roi_anual_pct'] or '—'}%. Decizie cu impact financiar.",
                solicitat_de=solicitat_de)
            produs.leaga_aprobare_oportunitate(o.id, ap.id)
            return {"status": "asteapta_aprobare",
                    "mesaj": t("bot_oportunitate_ceruta", lang).format(
                        titlu=o.titlu, ap=ap.id)}

        return {"status": "esuat",
                "mesaj": f"Acțiunea '{actiune}' nu e implementată la produs."}

    def _fisa_txt(self, f: dict, lang: str) -> str:
        pb = f"{f['payback_luni']} luni" if f["payback_luni"] else "—"
        roi = f"{f['roi_anual_pct']}%" if f["roi_anual_pct"] else "—"
        return t("bot_oportunitate_fisa", lang).format(
            titlu=f["titlu"], investitie=f["investitie_estimata"],
            venit=f["venit_lunar_estimat"], payback=pb, roi=roi, status=f["status"])
