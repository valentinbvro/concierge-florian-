"""Agentul 10 — Hermes: antrenare & învățare continuă.

Transformă semnalele din operare (întrebări fără răspuns, aprobări respinse)
în sugestii de îmbunătățire, aplicate doar cu aprobare umană. Ține și versiunile
instrucțiunilor agenților.
"""
from .. import hermes
from ..i18n import t
from .base import Agent


class AgentHermes(Agent):
    key = "hermes"
    nume = "Hermes — Antrenare continuă"
    descriere = "Învață din operare: semnale, sugestii, instrucțiuni versionate."
    faza = "5"

    def executa(self, actiune: str, payload: dict, solicitat_de: str) -> dict:
        lang = payload.get("lang", "ro")

        if actiune == "semnaleaza":
            s = hermes.semnal(payload.get("tip", "corectie_utilizator"),
                              payload.get("continut", ""),
                              payload.get("meta"), creat_de=solicitat_de)
            return {"status": "ok",
                    "mesaj": t("hermes_semnal", lang).format(id=s.id, tip=s.tip)}

        if actiune == "analizeaza":
            st = hermes.analizeaza()
            return {"status": "ok",
                    "mesaj": t("hermes_analiza", lang).format(
                        semnale=st["semnale_procesate"], sugestii=st["sugestii_create"])}

        if actiune == "sugestii":
            status = payload.get("status")
            ss = hermes.lista_sugestii(status)
            if not ss:
                return {"status": "ok", "mesaj": t("hermes_sugestii_zero", lang)}
            linii = [f"#{s.id} [{s.tip}] {s.titlu[:80]} — {s.status}" for s in ss[:15]]
            return {"status": "ok",
                    "mesaj": t("hermes_sugestii_lista", lang).format(
                        n=len(ss), linii="\n".join(linii))}

        if actiune == "decide_sugestie":
            s = hermes.decide_sugestie(int(payload.get("id", 0)),
                                       payload.get("decizie", ""),
                                       decident=solicitat_de)
            if not s:
                return {"status": "esuat", "mesaj": t("hermes_sugestie_lipsa", lang)}
            return {"status": "ok",
                    "mesaj": t("hermes_sugestie_decisa", lang).format(id=s.id, status=s.status)}

        if actiune == "completeaza_raspuns":
            s = hermes.completeaza_raspuns(int(payload.get("id", 0)),
                                           payload.get("raspuns", ""))
            if not s:
                return {"status": "esuat", "mesaj": t("hermes_sugestie_lipsa", lang)}
            return {"status": "ok", "mesaj": t("hermes_raspuns_salvat", lang).format(id=s.id)}

        if actiune == "aplica_sugestie":
            ok, cod = hermes.aplica_sugestie(int(payload.get("id", 0)))
            if not ok:
                return {"status": "esuat",
                        "mesaj": t("hermes_aplicare_esuata", lang).format(cod=cod)}
            return {"status": "ok", "mesaj": t("hermes_aplicata", lang).format(
                id=payload.get("id"))}

        if actiune == "seteaza_instructiune":
            inst = hermes.seteaza_instructiune(payload.get("agent", ""),
                                               payload.get("text", ""),
                                               creat_de=solicitat_de)
            return {"status": "ok",
                    "mesaj": t("hermes_instructiune", lang).format(
                        agent=inst.agent, v=inst.versiune)}

        if actiune == "raport":
            r = hermes.raport()
            return {"status": "ok", "mesaj": t("hermes_raport", lang).format(
                neprocesate=r["semnale_neprocesate"],
                invatate=r["cunostinte_invatate"],
                propuse=r["sugestii_pe_status"].get("propusa", 0))}

        return {"status": "esuat",
                "mesaj": f"Acțiunea '{actiune}' nu e implementată încă la Hermes."}
