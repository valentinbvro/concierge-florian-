"""Ceilalți 8 agenți — stub-uri pentru Faza 0.

Fiecare știe cine e și în ce fază devine funcțional; până atunci înregistrează
sarcina primită în coadă (agent_tasks) ca să nu se piardă nimic.
"""
from ..db import SessionLocal
from ..models import AgentTask
from .base import Agent


class _Stub(Agent):
    def executa(self, actiune: str, payload: dict, solicitat_de: str) -> dict:
        db = SessionLocal()
        try:
            db.add(AgentTask(agent=self.key,
                             titlu=f"[{actiune}] {str(payload)[:120]}",
                             detalii=f"Solicitat de {solicitat_de}. Va fi procesat în Faza {self.faza}."))
            db.commit()
        finally:
            db.close()
        return {"status": "partial",
                "mesaj": f"Sunt {self.nume} (Faza {self.faza}). Am înregistrat sarcina "
                         f"«{actiune}» în coadă; o voi procesa când modulul devine activ."}


class AgentOperatiuni(_Stub):
    """Înlocuit de OperatiuniAgent (agents/operatiuni.py) în Faza 2 — păstrat pentru compatibilitate."""
    key = "operatiuni"; nume = "Operațiuni & Dispecerat"; faza = "2"
    descriere = "Atribuire lucrări, monitorizare timp real, anticipare blocaje, livrare."
