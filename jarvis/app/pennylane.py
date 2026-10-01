"""Adaptor Pennylane API v2 — facturare clienți.

Documentație (verificat 01.10.2026):
- bază: https://app.pennylane.com/api/external/v2
- auth: header Authorization: Bearer <TOKEN> (token per companie)
- POST /customer_invoices {customer_id, date, deadline, draft, external_reference,
    invoice_lines: [{label, quantity (număr), unit, raw_currency_unit_price (șir),
    vat_rate: "FR_200"}]} → ciornă (draft)
- PUT /customer_invoices/{id}/finalize → ireversibil, primește număr legal
- POST /customer_invoices/{id}/send_by_email
- PUT /customer_invoices/{id}/mark_as_paid
- GET /customer_invoices/{id} → status: draft/paid/partially_paid/late/upcoming…
- POST /individual_customers / POST /company_customers (billing_address obligatoriu)

Fără PENNYLANE_API_TOKEN rulează în MOD DEMO: nicio rețea, ID-uri simulate
(prefix DEMO-). Tot fluxul local (ciorne, aprobări, BI) funcționează identic.
"""
import json
import os
from datetime import date

import httpx

from . import audit, config


class PennylaneError(Exception):
    pass


class PennylaneClient:
    def __init__(self, token: str | None = None, base_url: str | None = None):
        self.token = token if token is not None else config.PENNYLANE_API_TOKEN
        self.base = (base_url or config.PENNYLANE_BASE_URL
                     or "https://app.pennylane.com/api/external/v2").rstrip("/")
        self.demo = not bool(self.token)
        self._demo_seq = 1000

    # --- infrastructură ---
    def _client(self) -> httpx.Client:
        # trust_env=False: ocolim intrările malformate din no_proxy (vezi AGENTS.md);
        # proxy-ul explicit din mediu rămâne valabil pentru apelurile externe.
        proxy = os.environ.get("https_proxy") or os.environ.get("HTTPS_PROXY") \
            or os.environ.get("http_proxy") or os.environ.get("HTTP_PROXY")
        return httpx.Client(base_url=self.base, timeout=30.0, trust_env=False,
                            proxy=proxy or None)

    def _request(self, metoda: str, cale: str, payload: dict | None = None) -> dict:
        with self._client() as c:
            r = c.request(metoda, cale,
                          headers={"Authorization": f"Bearer {self.token}",
                                   "Content-Type": "application/json"},
                          json=payload or {})
        if r.status_code >= 400:
            raise PennylaneError(f"Pennylane {r.status_code}: {r.text[:300]}")
        try:
            return r.json()
        except ValueError:
            return {}

    # --- conexiune ---
    def verifica(self) -> dict:
        """GET /me — validarea tokenului."""
        if self.demo:
            return {"demo": True, "mesaj": "Mod demo: fără token Pennylane."}
        return self._request("GET", "/me")

    # --- clienți ---
    def creeaza_client(self, nume: str, telefon: str = "", tip: str = "individual") -> dict:
        """Creează clientul în Pennylane. În demo, întoarce un ID simulat."""
        if self.demo:
            self._demo_seq += 1
            return {"id": f"DEMO-C{self._demo_seq}", "name": nume}
        parti = (nume or "").split()
        if tip == "company":
            payload = {"name": nume,
                       "billing_address": {"address": "-", "postal_code": "-",
                                           "city": "-", "country_alpha2": "FR"}}
            return self._request("POST", "/company_customers", payload)
        payload = {"first_name": parti[0] if parti else "-",
                   "last_name": " ".join(parti[1:]) or "-",
                   "billing_address": {"address": "-", "postal_code": "-",
                                       "city": "-", "country_alpha2": "FR"}}
        if telefon:
            payload["phone"] = telefon
        return self._request("POST", "/individual_customers", payload)

    # --- facturi ---
    def creeaza_ciorna(self, customer_id, linii: list[dict],
                       data: str | None = None, deadline: str | None = None,
                       referinta_externa: str = "") -> dict:
        """POST /customer_invoices cu draft=true."""
        data = data or date.today().isoformat()
        payload = {"customer_id": customer_id, "date": data,
                   "deadline": deadline or data, "draft": True,
                   "invoice_lines": linii}
        if referinta_externa:
            payload["external_reference"] = referinta_externa
        if self.demo:
            self._demo_seq += 1
            total = sum(float(l.get("raw_currency_unit_price", 0)) * l.get("quantity", 1)
                        for l in linii)
            return {"id": f"DEMO-F{self._demo_seq}", "status": "draft",
                    "external_reference": referinta_externa,
                    "total_with_tax": f"{total:.2f}", "demo": True}
        return self._request("POST", "/customer_invoices", payload)

    def finalizeaza(self, invoice_id) -> dict:
        """PUT /customer_invoices/{id}/finalize — IREVERSIBIL."""
        if self.demo:
            return {"id": invoice_id, "status": "upcoming",
                    "invoice_number": f"DEMO-2026-{invoice_id}", "demo": True}
        return self._request("PUT", f"/customer_invoices/{invoice_id}/finalize")

    def trimite_email(self, invoice_id, destinatari: list[str] | None = None) -> dict:
        if self.demo:
            return {"id": invoice_id, "trimis": True, "demo": True}
        payload = {"recipients": destinatari} if destinatari else {}
        return self._request("POST", f"/customer_invoices/{invoice_id}/send_by_email", payload)

    def marcheaza_platita(self, invoice_id) -> dict:
        if self.demo:
            return {"id": invoice_id, "status": "paid", "demo": True}
        return self._request("PUT", f"/customer_invoices/{invoice_id}/mark_as_paid")

    def detalii(self, invoice_id) -> dict:
        if self.demo:
            return {"id": invoice_id, "status": "draft", "demo": True}
        return self._request("GET", f"/customer_invoices/{invoice_id}")

    def sterge_ciorna(self, invoice_id) -> dict:
        """DELETE — doar ciorne."""
        if self.demo:
            return {"id": invoice_id, "sters": True, "demo": True}
        with self._client() as c:
            r = c.delete(f"/customer_invoices/{invoice_id}",
                         headers={"Authorization": f"Bearer {self.token}"})
        if r.status_code >= 400:
            raise PennylaneError(f"Pennylane {r.status_code}: {r.text[:300]}")
        return {"id": invoice_id, "sters": True}
