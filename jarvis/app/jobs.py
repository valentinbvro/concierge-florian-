"""Job-uri automate Jarvis (se rulează periodic, ex. cron zilnic).

Follow-up: leaduri/oportunități fără activitate recentă primesc automat
o sarcină de follow-up în CRM (nu se trimite nimic clientului fără aprobare).
Sync Pennylane (Faza 3): trage statusurile facturilor, snapshot KPI, raport anomalii.
"""
from datetime import datetime, timedelta

from . import audit, config


def ruleaza_sync_pennylane(solicitant: str = "job-sync-pennylane") -> dict:
    """Sincronizare facturi + snapshot KPI zilnic + raport anomalii."""
    from . import finante
    sync = finante.sincronizeaza()
    kpi = finante.snapshot_kpi()
    anomalii = finante.detecteaza_anomalii()
    ridicate = [a for a in anomalii if a["severitate"] == "ridicata"]
    audit.inregistreaza(solicitant, "job_sync",
                        f"sync: {sync}; anomalii: {len(anomalii)} "
                        f"({len(ridicate)} ridicate)")
    return {"status": "ok", "sincronizare": sync, "kpi": kpi,
            "anomalii": len(anomalii), "anomalii_ridicate": len(ridicate)}


def _zile_vechime(data_str: str | None) -> int | None:
    if not data_str:
        return None
    try:
        dt = datetime.fromisoformat(str(data_str)[:19])
        return (datetime.now() - dt).days
    except ValueError:
        return None


def ruleaza_followup(crm, solicitant: str = "job-followup") -> dict:
    creat = 0
    detalii = []
    try:
        leaduri = crm.cauta_leaduri("") or []
        if isinstance(leaduri, dict):
            leaduri = leaduri.get("items", leaduri.get("leaduri", []))
    except Exception as e:
        return {"status": "esuat", "mesaj": f"Nu am putut citi leadurile: {e}"}

    for l in leaduri:
        status = (l.get("status") or "nou")
        if status not in ("nou", "contactat"):
            continue
        vechime = _zile_vechime(l.get("created_at"))
        if vechime is None or vechime < config.FOLLOWUP_ZILE_LEAD:
            continue
        nume = f"{l.get('first_name', '')} {l.get('last_name', '')}".strip()
        try:
            crm.creeaza_activitate(
                subject=f"Follow-up lead: {nume}",
                tip="apel",
                description=f"Lead de {vechime} zile fără progres (status: {status}). "
                            f"Creat automat de Jarvis.",
                related_kind="lead", related_id=l.get("id"))
            creat += 1
            detalii.append(nume)
        except Exception as e:
            detalii.append(f"{nume}: EROARE {e}")

    audit.inregistreaza(solicitant, "job_followup",
                        f"{creat} sarcini de follow-up create: {', '.join(detalii[:10])}")
    return {"status": "ok",
            "mesaj": f"Am creat {creat} sarcini de follow-up în CRM.",
            "detalii": detalii}


def ruleaza_conformitate(solicitant: str = "job-conformitate") -> dict:
    """Verifică scadențele de conformitate (ITP, asigurări, licențe) și
    înregistrează în audit ce expiră în 30 de zile sau e deja expirat."""
    from . import risc
    urgente = risc.verificari_urgente(30)
    for v in urgente:
        audit.inregistreaza(solicitant, "conformitate_alerta",
                            f"#{v.id} {v.tip} — {v.referinta}: {v.status} "
                            f"(expiră {v.expira_la.strftime('%d.%m.%Y') if v.expira_la else '—'})")
    return {"status": "ok", "urgente": len(urgente),
            "detalii": [f"#{v.id} {v.tip} {v.referinta} [{v.status}]" for v in urgente]}
