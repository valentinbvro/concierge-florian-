"""Conector Messenger (Meta) — aceeași structură ca WhatsApp.

Verificare webhook + recepție mesaje + rutare prin orchestrator.
"""
from .. import audit
from ..db import SessionLocal
from ..models import Conversation, Message


def verifica_webhook(mode: str, token: str, challenge: str, token_asteptat: str):
    if mode == "subscribe" and token == token_asteptat and token_asteptat:
        return challenge
    return None


def proceseaza_payload(payload: dict, orchestrator) -> list[dict]:
    raspunsuri = []
    for entry in payload.get("entry", []):
        for ev in entry.get("messaging", []):
            sender = (ev.get("sender") or {}).get("id", "")
            text = ((ev.get("message") or {}).get("text")) or ""
            if not (sender and text):
                continue
            db = SessionLocal()
            try:
                conv = (db.query(Conversation)
                          .filter_by(canal="messenger", contact_ref=sender, stare="deschisa")
                          .first())
                if not conv:
                    conv = Conversation(canal="messenger", contact_ref=sender,
                                        titlu=f"Messenger — {sender}")
                    db.add(conv)
                    db.commit()
                    db.refresh(conv)
                db.add(Message(conversation_id=conv.id, directie="in",
                               autor=sender, text=text[:4000]))
                db.commit()
            finally:
                db.close()
            audit.inregistreaza("messenger", "mesaj_primit", f"{sender}: {text[:150]}")
            try:
                raspuns = orchestrator.proceseaza_canal(text, utilizator=sender,
                                                         canal="messenger")
            except Exception as e:
                raspuns = "Am primit mesajul tău. Revenim în scurt timp cu un răspuns."
                audit.inregistreaza("messenger", "eroare_procesare", str(e)[:200])
            raspunsuri.append({"către": sender, "text": raspuns,
                               "notă": "trimiterea efectivă necesită pagina conectată"})
    return raspunsuri
