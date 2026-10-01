"""Client Python pentru API-ul REST v1 al CRM-ului (autentificare Bearer token)."""
import httpx

from . import config


class CrmError(Exception):
    pass


class CrmClient:
    def __init__(self, base_url: str | None = None, token: str | None = None, timeout: float = 10.0):
        self.base_url = (base_url or config.CRM_API_URL).rstrip("/")
        self.token = token if token is not None else config.CRM_API_TOKEN
        self.timeout = timeout

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def _get(self, path: str, params: dict | None = None):
        try:
            # trust_env=False: ignoră proxy-urile din mediu (apeluri locale)
            r = httpx.get(self.base_url + path, headers=self._headers(),
                          params=params, timeout=self.timeout, trust_env=False)
        except httpx.ConnectError as e:
            raise CrmError(f"CRM inaccesibil la {self.base_url}: {e}")
        if r.status_code == 401:
            raise CrmError("Token CRM invalid sau lipsă (verifică CRM_API_TOKEN în .env).")
        if r.status_code >= 400:
            raise CrmError(f"CRM a răspuns {r.status_code}: {r.text[:200]}")
        return r.json()

    def _post(self, path: str, payload: dict):
        try:
            r = httpx.post(self.base_url + path, headers=self._headers(),
                           json=payload, timeout=self.timeout, trust_env=False)
        except httpx.ConnectError as e:
            raise CrmError(f"CRM inaccesibil la {self.base_url}: {e}")
        if r.status_code == 401:
            raise CrmError("Token CRM invalid sau lipsă (verifică CRM_API_TOKEN în .env).")
        if r.status_code >= 400:
            raise CrmError(f"CRM a răspuns {r.status_code}: {r.text[:200]}")
        return r.json()

    def _patch(self, path: str, payload: dict):
        try:
            r = httpx.patch(self.base_url + path, headers=self._headers(),
                            json=payload, timeout=self.timeout, trust_env=False)
        except httpx.ConnectError as e:
            raise CrmError(f"CRM inaccesibil la {self.base_url}: {e}")
        if r.status_code == 401:
            raise CrmError("Token CRM invalid sau lipsă (verifică CRM_API_TOKEN în .env).")
        if r.status_code >= 400:
            raise CrmError(f"CRM a răspuns {r.status_code}: {r.text[:200]}")
        return r.json() if r.text else {}

    # --- operațiuni folosite de agenți ---
    def sumar(self):
        """Verifică și conexiunea; întoarce KPI-urile din dashboard."""
        return self._get("/sumar")

    def creeaza_lead(self, first_name: str, last_name: str = "", phone: str = "",
                     email: str = "", company: str = "", source: str = "jarvis",
                     notes: str = "") -> dict:
        return self._post("/leaduri", {
            "first_name": first_name, "last_name": last_name, "phone": phone,
            "email": email, "company": company, "source": source, "notes": notes,
        })

    def cauta_leaduri(self, q: str = ""):
        return self._get("/leaduri", params={"q": q, "limit": 20})

    def creeaza_activitate(self, subject: str, tip: str = "sarcina", description: str = "",
                           related_kind: str = "", related_id: int | None = None) -> dict:
        return self._post("/activitati", {
            "subject": subject, "tip": tip, "description": description,
            "related_kind": related_kind, "related_id": related_id,
        })

    def creeaza_caz(self, subject: str, description: str = "", priority: str = "medie") -> dict:
        return self._post("/cazuri", {
            "subject": subject, "description": description, "priority": priority,
        })

    def actualizeaza_lead(self, lid: int, payload: dict) -> dict:
        """payload ex: {"status": "calificat"}"""
        return self._patch(f"/leaduri/{lid}", payload)

    def lista_oportunitati(self):
        return self._get("/oportunitati", params={"limit": 100})
