"""Agentul 3 — Finanțe & Contabilitate (funcțional din Faza 3).

Ciorne de facturi din curse finalizate, emitere cu aprobare (finalizare
Pennylane = ireversibilă), încasări, sincronizare, anomalii.
"""
from .. import approvals, audit, finante
from ..i18n import t
from .base import Agent


class AgentFinante(Agent):
    key = "finante"
    nume = "Finanțe & Contabilitate"
    descriere = "Facturare Pennylane, încasări, anomalii, rapoarte financiare."
    faza = "3"

    def executa(self, actiune: str, payload: dict, solicitat_de: str) -> dict:
        lang = payload.get("lang", "ro")

        if actiune == "creeaza_factura":
            try:
                f = finante.creeaza_factura(
                    cursa_id=payload.get("cursa_id"),
                    suma=payload.get("suma"),
                    client_nume=payload.get("client_nume", ""),
                    client_telefon=payload.get("client_telefon", ""),
                    solicitat_de=solicitat_de)
            except ValueError:
                return {"status": "esuat", "mesaj": t("bot_factura_suma_invalida", lang)}
            return {"status": "ok",
                    "mesaj": t("bot_factura_creata", lang).format(
                        numar=f.numar, client=f.client_nume, total=f.total),
                    "factura_id": f.id}

        if actiune == "emite_factura":
            fid = int(payload.get("factura_id", 0))
            facturi = [f for f in finante.lista_facturi() if f.id == fid]
            if not facturi or facturi[0].status != "ciorna":
                return {"status": "esuat",
                        "mesaj": t("bot_factura_nu_exista", lang).format(id=fid)}
            f = facturi[0]
            ap = approvals.cere_aprobare(
                tip="emitere_factura",
                titlu=f"Emitere factură {f.numar} ({f.client_nume}, {f.total:.2f} EUR)",
                detalii=f"Finalizare în Pennylane — IREVERSIBILĂ (primește număr legal). "
                        f"Cursă #{f.cursa_id or '—'}, scadență "
                        f"{f.deadline.strftime('%d.%m.%Y') if f.deadline else '—'}.",
                solicitat_de=solicitat_de)
            audit.inregistreaza(solicitat_de, "emitere_ceruta",
                                f"factura {f.numar} → cererea #{ap.id}")
            return {"status": "asteapta_aprobare",
                    "mesaj": t("bot_emitere_ceruta", lang).format(numar=f.numar, ap=ap.id)}

        if actiune == "trimite_factura":
            fid = int(payload.get("factura_id", 0))
            facturi = [f for f in finante.lista_facturi() if f.id == fid]
            if not facturi or facturi[0].status not in ("emisa", "partial"):
                return {"status": "esuat",
                        "mesaj": t("bot_factura_nu_exista", lang).format(id=fid)}
            f = facturi[0]
            ap = approvals.cere_aprobare(
                tip="trimitere_factura",
                titlu=f"Trimitere factură {f.numar} către {f.client_nume}",
                detalii=f"Trimitere pe email via Pennylane: {f.total:.2f} EUR.",
                solicitat_de=solicitat_de)
            return {"status": "asteapta_aprobare",
                    "mesaj": t("bot_trimitere_ceruta", lang).format(numar=f.numar, ap=ap.id)}

        if actiune == "marcheaza_platita":
            ok, info = finante.marcheaza_platita(
                int(payload.get("factura_id", 0)),
                float(payload.get("suma", 0) or 0),
                metoda=payload.get("metoda", ""),
                solicitat_de=solicitat_de)
            if not ok:
                return {"status": "esuat",
                        "mesaj": t("bot_factura_nu_exista", lang).format(
                            id=payload.get("factura_id", 0))}
            return {"status": "ok",
                    "mesaj": t("bot_incasare_ok", lang).format(status=info)}

        if actiune == "facturi_restante":
            restante = finante.facturi_restante()
            if not restante:
                return {"status": "ok", "mesaj": t("bot_restante_zero", lang)}
            linii = [f"• {f.numar} — {f.client_nume}: {f.total:.2f} EUR "
                     f"(scadență {f.deadline.strftime('%d.%m') if f.deadline else '—'})"
                     for f in restante]
            return {"status": "ok",
                    "mesaj": t("bot_restante_lista", lang).format(
                        n=len(restante),
                        total=sum(f.total for f in restante),
                        linii="\n".join(linii))}

        if actiune == "sincronizeaza":
            rez = finante.sincronizeaza()
            return {"status": "ok",
                    "mesaj": t("bot_sync_ok", lang).format(
                        actualizate=rez["actualizate"], erori=rez["erori"])}

        if actiune == "anomalii":
            an = finante.detecteaza_anomalii()
            if not an:
                return {"status": "ok", "mesaj": t("bot_anomalii_zero", lang)}
            linii = [f"• [{a['severitate']}] {a['descriere']}" for a in an]
            return {"status": "ok",
                    "mesaj": t("bot_anomalii_lista", lang).format(n=len(an),
                                                                 linii="\n".join(linii))}

        if actiune == "rezumat":
            r = finante.rezumat()
            return {"status": "ok", "mesaj": self._text_rezumat(r, lang)}

        return {"status": "esuat",
                "mesaj": f"Acțiunea '{actiune}' nu e implementată la finanțe."}

    def _text_rezumat(self, r: dict, lang: str) -> str:
        top = "\n".join(f"• {n}: {v:.2f} EUR" for n, v in r["top_clienti"]) or "—"
        n = r["facturi_emise_luna"]
        fact_txt = f"{n} " + ("factură" if lang == "ro" and n == 1 else
                              "facture" if lang == "fr" and n == 1 else
                              "facturi" if lang == "ro" else "factures")
        return t("bot_rezumat_financiar", lang).format(
            incasari_azi=r["incasari_azi"], facturat_luna=r["facturat_luna"],
            facturi_txt=fact_txt, restante_nr=r["restante_nr"],
            restante_total=r["restante_total"], curse_azi=r["curse_finalizate_azi"],
            tva=r["tva_luna"], anomalii=r["anomalii_nr"], top=top)
