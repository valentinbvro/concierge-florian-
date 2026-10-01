"""Scoring leaduri — reguli transparente, fără LLM.

Scor 0–100 din completitudinea datelor, sursă și vechime.
"""
SURSE_BUNE = {"recomandare": 15, "website": 10, "whatsapp": 8, "facebook": 6,
              "jarvis": 5, "manual": 5}


def scor(lead: dict) -> tuple[int, list[str]]:
    puncte, motive = 0, []
    if lead.get("phone"):
        puncte += 15
        motive.append("are telefon (+15)")
    if lead.get("email"):
        puncte += 15
        motive.append("are email (+15)")
    if lead.get("company"):
        puncte += 20
        motive.append("are firmă (+20)")
    sursa = (lead.get("source") or "").lower()
    bonus = SURSE_BUNE.get(sursa, 3)
    puncte += bonus
    motive.append(f"sursă «{sursa or 'necunoscută'}» (+{bonus})")
    if len(lead.get("notes") or "") > 30:
        puncte += 10
        motive.append("notițe detaliate (+10)")
    status = (lead.get("status") or "nou")
    bonus_status = {"contactat": 10, "calificat": 25, "convertit": 40}.get(status, 0)
    puncte += bonus_status
    if bonus_status:
        motive.append(f"status «{status}» (+{bonus_status})")
    return min(puncte, 100), motive


def clasifica(puncte: int) -> str:
    if puncte >= 70:
        return "fierbinte"
    if puncte >= 40:
        return "cald"
    return "rece"


def leaduri_cu_scor(crm) -> list[dict]:
    """Toate leadurile din CRM, ordonate după scor descrescător."""
    leaduri = crm.cauta_leaduri("") or []
    if isinstance(leaduri, dict):  # unele API-uri întorc {"items": [...]}
        leaduri = leaduri.get("items", leaduri.get("leaduri", []))
    rez = []
    for l in leaduri:
        p, motive = scor(l)
        rez.append({**l, "scor": p, "clasa": clasifica(p), "motive": motive})
    return sorted(rez, key=lambda x: x["scor"], reverse=True)
