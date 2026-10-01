"""Agentul 2 — Operațiuni & Dispecerat (funcțional din Faza 2).

Gestionează șoferi, mașini, curse, atribuire și statusuri.
Acțiunile ireversibile (anulare cursă) cer aprobare conform matricei.
"""
from .. import approvals, audit, dispecerat
from ..i18n import t
from .base import Agent


class OperatiuniAgent(Agent):
    key = "operatiuni"
    nume = "Operațiuni & Dispecerat"
    descriere = "Dispecerat curse taxi de lux: șoferi, mașini, atribuire, monitorizare."
    faza = "2"

    def executa(self, actiune: str, payload: dict, solicitat_de: str) -> dict:
        lang = payload.get("lang", "ro")

        if actiune == "creeaza_cursa":
            c = dispecerat.creeaza_cursa(
                payload.get("client_nume", ""), payload.get("client_telefon", ""),
                payload.get("preluare", ""), payload.get("destinatie", ""),
                payload.get("cand", ""), pret=payload.get("pret", 0),
                sursa=payload.get("sursa", "chat-intern"))
            cand = c.data_ora.strftime("%d.%m %H:%M") if c.data_ora else "—"
            return {"status": "ok",
                    "mesaj": t("bot_cursa_creata", lang).format(
                        id=c.id, nume=c.client_nume or "—",
                        preluare=c.preluare or "—", destinatie=c.destinatie or "—", cand=cand),
                    "cursa_id": c.id}

        if actiune == "atribuie_cursa":
            cid = int(payload.get("cursa_id", 0))
            ok, info = dispecerat.atribuie(cid, payload.get("sofer_id"),
                                           payload.get("masina_id"), crm=self.crm)
            if not ok:
                cheie = {"nu_exista": "bot_cursa_nu_exista",
                         "nimic_liber": "bot_atribuire_imposibila",
                         "ocupat": "bot_atribuire_imposibila"}.get(info, "bot_cursa_nu_exista")
                return {"status": "esuat", "mesaj": t(cheie, lang).format(id=cid)}
            sofer, masina = info.split("|")
            return {"status": "ok",
                    "mesaj": t("bot_atribuita", lang).format(id=cid, sofer=sofer, masina=masina)}

        if actiune == "status_cursa":
            cid = int(payload.get("cursa_id", 0))
            status = dispecerat.normalizeaza_status(payload.get("status", ""))
            if not status:
                return {"status": "esuat", "mesaj": t("bot_status_invalid", lang)}
            if status == "anulata":
                ap = approvals.cere_aprobare(
                    tip="anulare_cursa",
                    titlu=f"Anulare cursa #{cid}",
                    detalii=f"Se cere anularea cursei #{cid}. Șoferul/mașina se eliberează.",
                    solicitat_de=solicitat_de)
                audit.inregistreaza(solicitat_de, "anulare_ceruta", f"cursa #{cid} → cererea #{ap.id}")
                return {"status": "asteapta_aprobare",
                        "mesaj": t("bot_anulare_ceruta", lang).format(id=cid, ap=ap.id)}
            ok, info = dispecerat.schimba_status(cid, status, crm=self.crm)
            if not ok:
                return {"status": "esuat",
                        "mesaj": t("bot_cursa_nu_exista", lang).format(id=cid)
                        if info == "nu_exista" else t("bot_tranzitie_invalida", lang).format(id=cid)}
            return {"status": "ok",
                    "mesaj": t("bot_status_schimbat", lang).format(
                        id=cid, status=t("st_" + status, lang))}

        if actiune == "adauga_sofer":
            s = dispecerat.adauga_sofer(payload.get("nume", ""), payload.get("telefon", ""))
            return {"status": "ok",
                    "mesaj": t("bot_sofer_adaugat", lang).format(nume=s.nume, telefon=s.telefon or "—")}

        if actiune == "adauga_masina":
            m = dispecerat.adauga_masina(payload.get("marca_model", ""),
                                         payload.get("numar", ""),
                                         int(payload.get("locuri", 4) or 4))
            return {"status": "ok",
                    "mesaj": t("bot_masina_adaugata", lang).format(marca=m.marca_model,
                                                                   numar=m.numar or "—")}

        if actiune == "rezumat_dispecerat":
            r = dispecerat.rezumat_azi()
            return {"status": "ok",
                    "mesaj": t("bot_dispecerat_rezumat", lang).format(
                        curse=r["curse"], liberi=r["liberi"], masini=r["masini"])}

        return {"status": "esuat",
                "mesaj": f"Acțiunea '{actiune}' nu e implementată la dispecerat."}
