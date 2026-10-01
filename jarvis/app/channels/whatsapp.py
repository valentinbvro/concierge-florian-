"""Conector WhatsApp Business (Cloud API, Meta).

Funcționează structural din Faza 1: verificare webhook + recepție mesaje +
rutare prin orchestrator. Trimiterea efectivă necesită contul conectat
(vezi GHID_CANALE.md) și respectă matricea de aprobare: răspunsurile automate
sunt permise doar pentru Q&A și captare lead; restul intră în coadă.
"""
from .. import audit
from ..db import SessionLocal
from ..models import Conversation, Message


def verifica_webhook(mode: str, token: str, challenge: str, token_asteptat: str):
    """Verificarea Meta la înregistrarea webhook-ului. Întoarce challenge sau None."""
    if mode == "subscribe" and token == token_asteptat and token_asteptat:
        return challenge
    return None


def _conversatie_sau_noua(telefon: str) -> Conversation:
    db = SessionLocal()
    try:
        conv = (db.query(Conversation)
                  .filter_by(canal="whatsapp", contact_ref=telefon, stare="deschisa")
                  .first())
        if not conv:
            conv = Conversation(canal="whatsapp", contact_ref=telefon,
                                titlu=f"WhatsApp — {telefon}")
            db.add(conv)
            db.commit()
            db.refresh(conv)
            cid = conv.id
        else:
            cid = conv.id
        # întoarcem id-ul; obiectul e detașat după close
        return cid
    finally:
        db.close()


def proceseaza_payload(payload: dict, orchestrator) -> list[dict]:
    """Parsează payload-ul Meta, salvează mesajele și le rutează. Întoarce răspunsurile."""
    raspunsuri = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            val = change.get("value", {})
            for msg in val.get("messages", []):
                if msg.get("type") != "text":
                    continue
                telefon = msg.get("from", "")
                text = (msg.get("text") or {}).get("body", "")
                if not (telefon and text):
                    continue
                conv_id = _conversatie_sau_noua(telefon)
                db = SessionLocal()
                try:
                    db.add(Message(conversation_id=conv_id, directie="in",
                                   autor=telefon, text=text[:4000]))
                    db.commit()
                finally:
                    db.close()
                audit.inregistreaza("whatsapp", "mesaj_primit", f"{telefon}: {text[:150]}")
                # Răspunsul automat trece prin orchestrator (Q&A / captare lead)
                try:
                    raspuns = orchestrator.proceseaza_canal(text, utilizator=telefon,
                                                             canal="whatsapp")
                except Exception as e:
                    raspuns = "Am primit mesajul tău. Revenim în scurt timp cu un răspuns."
                    audit.inregistreaza("whatsapp", "eroare_procesare", str(e)[:200])
                raspunsuri.append({"către": telefon, "text": raspuns,
                                   "notă": "trimiterea efectivă necesită contul conectat"})
    return raspunsuri
