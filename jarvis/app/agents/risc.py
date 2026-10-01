"""Agentul 9 — Risc, Conformitate & Securitate (funcțional din Faza 4).

- Analiză contracte = pre-filtru euristic (clauze prezente/lipsă, scor de risc).
  NU e consultanță juridică; fiecare rezultat poartă disclaimerul.
- Verificări de conformitate cu scadență (ITP, asigurări, licențe…).
- Registru nereguli.
"""
import json

from .. import risc
from ..i18n import t
from .base import Agent


class AgentRisc(Agent):
    key = "risc"
    nume = "Risc, Conformitate & Securitate"
    descriere = ("Analiză contracte (pre-filtru, nu consultanță juridică), "
                 "nereguli, conformitate.")
    faza = "4"

    def executa(self, actiune: str, payload: dict, solicitat_de: str) -> dict:
        lang = payload.get("lang", "ro")

        if actiune == "analizeaza_contract":
            a = risc.analizeaza_contract(payload.get("nume", "contract"),
                                         payload.get("text", ""), lang,
                                         solicitat_de=solicitat_de)
            c = json.loads(a.concluzii)
            gasite = ", ".join(c["clauze_gasite"]) or "—"
            lipsa = ", ".join(c["clauze_lipsa"]) or "—"
            return {"status": "ok",
                    "mesaj": t("bot_contract_analizat", lang).format(
                        nume=a.nume, risc=c["scor_risc"], gasite=gasite,
                        lipsa=lipsa, disclaimer=c["disclaimer"]),
                    "analiza_id": a.id}

        if actiune == "verificare_noua":
            try:
                v = risc.adauga_verificare(payload.get("tip", "alta"),
                                           payload.get("referinta", ""),
                                           payload.get("expira_la", ""),
                                           payload.get("notite", ""),
                                           solicitat_de=solicitat_de)
            except ValueError:
                return {"status": "esuat", "mesaj": t("bot_data_invalida", lang)}
            return {"status": "ok",
                    "mesaj": t("bot_verificare_noua", lang).format(
                        id=v.id, tip=v.tip, referinta=v.referinta,
                        data=v.expira_la.strftime("%d.%m.%Y"))}

        if actiune == "verificari":
            vs = risc.lista_verificari()
            if not vs:
                return {"status": "ok", "mesaj": t("bot_verificari_zero", lang)}
            linii = [f"• #{v.id} {v.tip} — {v.referinta}: "
                     f"{v.expira_la.strftime('%d.%m.%Y') if v.expira_la else '—'} "
                     f"[{v.status}]" for v in vs]
            return {"status": "ok",
                    "mesaj": t("bot_verificari_lista", lang).format(
                        n=len(vs), linii="\n".join(linii))}

        if actiune == "semnaleaza_neregula":
            n = risc.semnaleaza(payload.get("titlu", ""),
                                payload.get("descriere", ""),
                                payload.get("severitate", "medie"),
                                solicitat_de=solicitat_de)
            return {"status": "ok",
                    "mesaj": t("bot_neregula_noua", lang).format(
                        id=n.id, titlu=n.titlu, severitate=n.severitate)}

        if actiune == "lista_nereguli":
            ns = risc.lista_nereguli()
            if not ns:
                return {"status": "ok", "mesaj": t("bot_nereguli_zero", lang)}
            linii = [f"• #{n.id} [{n.severitate}] {n.titlu} ({n.status})" for n in ns]
            return {"status": "ok",
                    "mesaj": t("bot_nereguli_lista", lang).format(
                        n=len(ns), linii="\n".join(linii))}

        if actiune == "rezolva_neregula":
            n = risc.rezolva_neregula(int(payload.get("neregula_id", 0)))
            if not n:
                return {"status": "esuat",
                        "mesaj": t("bot_neregula_inexistenta", lang).format(
                            id=payload.get("neregula_id", 0))}
            return {"status": "ok",
                    "mesaj": t("bot_neregula_rezolvata", lang).format(
                        id=n.id, titlu=n.titlu)}

        return {"status": "esuat",
                "mesaj": f"Acțiunea '{actiune}' nu e implementată la risc."}
