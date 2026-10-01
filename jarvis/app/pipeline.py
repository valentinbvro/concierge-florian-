"""Pipeline de vânzări în 10 pași — mapat pe datele din CRM + ofertele Jarvis.

Pașii 1–3: leaduri CRM · 4–8: oportunități CRM · 6: oferte Jarvis · 9–10: activități.
"""
from . import oferte


def snapshot(crm) -> list[dict]:
    pasi = [
        {"pas": 1, "nume": "Lead nou", "sursa": "crm", "filtru": ("lead", "nou")},
        {"pas": 2, "nume": "Contactare inițială", "sursa": "crm", "filtru": ("lead", "contactat")},
        {"pas": 3, "nume": "Calificare", "sursa": "crm", "filtru": ("lead", "calificat")},
        {"pas": 4, "nume": "Oportunitate: prospectare", "sursa": "crm", "filtru": ("oportunitate", "prospectare")},
        {"pas": 5, "nume": "Oportunitate: calificare nevoi", "sursa": "crm", "filtru": ("oportunitate", "calificare")},
        {"pas": 6, "nume": "Ofertă trimisă", "sursa": "jarvis", "filtru": ("oferta", "trimisa")},
        {"pas": 7, "nume": "Negociere", "sursa": "crm", "filtru": ("oportunitate", "negociere")},
        {"pas": 8, "nume": "Câștigat", "sursa": "crm", "filtru": ("oportunitate", "castigat")},
        {"pas": 9, "nume": "Oferte în lucru (ciornă/aprobată)", "sursa": "jarvis", "filtru": ("oferta", "deschisa")},
        {"pas": 10, "nume": "Leaduri pierdute (învățare)", "sursa": "crm", "filtru": ("lead", "pierdut")},
    ]
    try:
        leaduri = crm.cauta_leaduri("") or []
        if isinstance(leaduri, dict):
            leaduri = leaduri.get("items", leaduri.get("leaduri", []))
        oportunitati = crm.lista_oportunitati() or []
        if isinstance(oportunitati, dict):
            oportunitati = oportunitati.get("items", oportunitati.get("oportunitati", []))
    except Exception:
        leaduri, oportunitati = [], []
    oferte_toate = oferte.lista_oferte()

    for p in pasi:
        tip, val = p["filtru"]
        if tip == "lead":
            p["count"] = sum(1 for l in leaduri if (l.get("status") or "") == val)
        elif tip == "oportunitate":
            p["count"] = sum(1 for o in oportunitati if (o.get("stage") or "") == val)
        elif tip == "oferta" and val == "trimisa":
            p["count"] = sum(1 for o in oferte_toate if o.stare == "trimisa")
        elif tip == "oferta":
            p["count"] = sum(1 for o in oferte_toate if o.stare in ("ciorna", "aprobata"))
        del p["filtru"], p["sursa"]
    return pasi
