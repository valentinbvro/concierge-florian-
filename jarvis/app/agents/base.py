"""Clasa de bază pentru toți agenții Jarvis."""
import json

from .. import audit
from ..db import SessionLocal
from ..models import AgentRun


class Agent:
    key = "baza"
    nume = "Agent"
    descriere = ""
    faza = "0"  # faza din blueprint în care devine complet funcțional

    def __init__(self, crm):
        self.crm = crm

    def ruleaza(self, actiune: str, payload: dict, solicitat_de: str = "jarvis") -> dict:
        """Execută o acțiune și înregistrează rularea (trasabilitate + cost)."""
        try:
            rezultat = self.executa(actiune, payload, solicitat_de)
            stare = rezultat.get("status", "ok")
        except Exception as e:  # noqa: BLE001 — erorile agenților nu opresc orchestratorul
            rezultat = {"status": "esuat", "mesaj": str(e)[:300]}
            stare = "esuat"
        db = SessionLocal()
        try:
            db.add(AgentRun(agent=self.key, actiune=actiune,
                            intrari=json.dumps(payload, ensure_ascii=False)[:2000],
                            iesiri=json.dumps(rezultat, ensure_ascii=False)[:2000],
                            stare=stare))
            db.commit()
        finally:
            db.close()
        audit.inregistreaza(self.key, f"ruleaza:{actiune}", rezultat.get("mesaj", "")[:200])
        # Hermes: întrebare fără răspuns → semnal de antrenare
        if actiune == "mesaj_utilizator" and stare == "esuat":
            try:
                from .. import hermes as _hermes
                _hermes.semnal("intrebare_fara_raspuns",
                               str(payload.get("text", ""))[:500],
                               {"agent": self.key}, creat_de=solicitat_de)
            except Exception:
                pass
        return rezultat

    def executa(self, actiune: str, payload: dict, solicitat_de: str) -> dict:
        raise NotImplementedError
