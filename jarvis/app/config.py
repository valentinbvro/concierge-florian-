"""Configurare Jarvis din variabile de mediu (opțional fișier .env)."""
import os

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_dotenv():
    path = os.path.join(_BASE, ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


_load_dotenv()


def _get(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


CRM_API_URL = _get("CRM_API_URL", "http://127.0.0.1:8000/api/v1")
CRM_API_TOKEN = _get("CRM_API_TOKEN", "")
JARVIS_SECRET = _get("JARVIS_SECRET", "schimba-ma")
JARVIS_PORT = int(_get("JARVIS_PORT", "8001") or 8001)
DB_PATH = _get("JARVIS_DB", os.path.join(_BASE, "jarvis.db"))
LLM_API_KEY = _get("LLM_API_KEY", "")
LLM_MODEL = _get("LLM_MODEL", "")

# Faza 1
TVA_DEFAULT = float(_get("TVA_DEFAULT", "0.19") or 0.19)
OFERTE_DIR = _get("OFERTE_DIR", os.path.join(_BASE, "oferte_pdf"))
WHATSAPP_VERIFY_TOKEN = _get("WHATSAPP_VERIFY_TOKEN", "")
MESSENGER_VERIFY_TOKEN = _get("MESSENGER_VERIFY_TOKEN", "")
META_APP_SECRET = _get("META_APP_SECRET", "")
FOLLOWUP_ZILE_LEAD = int(_get("FOLLOWUP_ZILE_LEAD", "3") or 3)
FOLLOWUP_ZILE_OPORTUNITATE = int(_get("FOLLOWUP_ZILE_OPORTUNITATE", "7") or 7)
APPROVER_NAME = _get("APPROVER_NAME", "șeful companiei")

# Faza 3 — Pennylane (fără token → mod demo, fără apeluri de rețea)
PENNYLANE_API_TOKEN = _get("PENNYLANE_API_TOKEN", "")
PENNYLANE_BASE_URL = _get("PENNYLANE_BASE_URL", "https://app.pennylane.com/api/external/v2")
PENNYLANE_VAT_RATE = _get("PENNYLANE_VAT_RATE", "FR_200")
PENNYLANE_SCADENTA_ZILE = int(_get("PENNYLANE_SCADENTA_ZILE", "30") or 30)
