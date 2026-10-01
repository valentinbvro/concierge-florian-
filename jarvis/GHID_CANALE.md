# Conectarea canalelor externe — WhatsApp Business & Messenger

Jarvis e pregătit tehnic (webhook-uri funcționale în Faza 1). Pașii de mai jos
necesită conturile tale — nu-i pot face eu în locul tău.

## WhatsApp Business (Cloud API — gratuit, plătești per conversație)

1. Intră pe **Meta for Developers** (developers.facebook.com) → creează o aplicație
   de tip **Business**.
2. Adaugă produsul **WhatsApp** → primești un număr de test gratuit.
3. Pentru producție: conectează-ți **numărul real de business** (nu poate fi
   simultan pe telefonul personal — ai nevoie de un număr dedicat).
4. La **Configuration → Webhook**:
   - Callback URL: `https://domeniul-tau.ro/webhooks/whatsapp`
   - Verify token: alege un text secret și pune-l în `.env` la `WHATSAPP_VERIFY_TOKEN`
5. Abonează-te la câmpul **messages**.
6. Copiază **tokenul de acces** (permanent) — îl vom folosi la trimitere (Faza 1+).

**Important:** serverul Jarvis trebuie accesibil public prin HTTPS pentru webhook.
Opțiuni: domeniu propriu + reverse proxy, sau un tunel (ex. Cloudflare Tunnel).

## Messenger (pagină Facebook)

1. În aceeași aplicație Meta, adaugă produsul **Messenger**.
2. Conectează **pagina de Facebook** a firmei.
3. La webhook: Callback URL `https://domeniul-tau.ro/webhooks/messenger`,
   Verify token → `MESSENGER_VERIFY_TOKEN` în `.env`.
4. Abonează-te la evenimentele **messages** ale paginii.
5. Generează un **Page Access Token**.

## Instagram (DM) — aceeași infrastructură Meta

1. Contul de Instagram trebuie să fie **business/creator** și legat de pagina de Facebook.
2. În aplicația Meta, adaugă produsul **Instagram** (Messenger API for Instagram).
3. Abonează-te la evenimentele **messages** pentru contul de Instagram.
4. Webhook-ul existent de Messenger poate primi și mesajele de Instagram
   (același format de evenimente) — adaptarea e minoră și se face la conectare.

## LinkedIn — limitare cunoscută

LinkedIn **nu oferă API public de mesagerie** pentru automatizări pe pagina
companiei. Ce se poate: postări pe pagina companiei (prin API-ul de shares,
cu aprobare în Jarvis). Mesajele private LinkedIn rămân manuale.

## Cum răspunde Jarvis pe canale (deja implementat)

- **Întrebări cu răspuns în baza de cunoștințe** → răspuns automat instant.
- **Mesaje de tip lead** → lead creat în CRM + mesaj de confirmare.
- **Sesizări/probleme** → tichet deschis în CRM + confirmare.
- **Restul** → mesaj înregistrat, intră în coada agenților; clientul primește
  confirmarea că revine un coleg. Nimic nu se trimite clientului fără acoperire
  în matricea de aprobare.

## Costuri orientative (vezi și `jarvis-costuri.md`)

- WhatsApp: ~0,04–0,06 € / conversație de 24h (primele 1.000/lună gratuite).
- Messenger: gratuit.
