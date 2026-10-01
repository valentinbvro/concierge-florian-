"""Registrul agenților Jarvis."""
from .bi import AgentBI
from .finante import AgentFinante
from .growth import AgentGrowth
from .hermes import AgentHermes
from .marketing import MarketingAgent
from .operatiuni import OperatiuniAgent
from .produs import AgentProdus
from .research import ResearchAgent
from .rest import AgentOperatiuni
from .risc import AgentRisc
from .vanzari import AgentVanzari

CLASE_AGENTI = [
    AgentVanzari,
    OperatiuniAgent,
    AgentFinante,
    MarketingAgent,
    ResearchAgent,
    AgentBI,
    AgentProdus,
    AgentGrowth,
    AgentHermes,
    AgentRisc,
]


def construieste_agenti(crm: object) -> dict:
    return {cls.key: cls(crm) for cls in CLASE_AGENTI}
