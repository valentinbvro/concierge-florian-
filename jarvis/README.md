# JARVIS — Faza 2: Operațiuni & Dispecerat

## Ce e nou în Faza 2

- **Dispecerat taxi de lux** (`/dispecerat`) — curse, șoferi, mașini, atribuire
  automată, tranziții de status (rezervată → confirmată → în curs → finalizată),
  coadă de notificări client/șofer, activități oglindă în CRM
- **Bilingv RO/FR** — toată interfața + comenzile de chat în română și franceză
  (toggle RO/FR în header; `?lang=fr` sau cookie)
- **Marketing & Media** (`/marketing`) — postări cu aprobare înainte de publicare,
  plan editorial săptămânal generat automat
- **Competitori** (`/competitori`) — watchlist + jurnal de observații datate
- Aprobatorul e configurabil (`APPROVER_NAME` în `.env`)

## Comenzi noi în chat (RO + FR)

- `cursă nouă: Nume, telefon, preluare, destinație, când` / `nouvelle course: ...`
- `curse azi` / `courses aujourd'hui` · `atribuie cursa 3` · `cursa 3: confirmată`
- `șofer nou: Nume, telefon` · `mașină nouă: Marcă Model, număr`
- `postare nouă: canal, text` · `publică postarea 1` · `plan editorial`
- `competitor nou: Nume` · `observație competitor 1: text`

## Faza 1 (inclusă)

- **Catalog produse/servicii** (`/catalog`) — baza pentru ofertare
- **Oferte cu linii, TVA și PDF** (`/oferte`) — la aprobarea cererii se generează automat PDF-ul
- **Scoring leaduri** (0–100, reguli transparente) — comanda `scor leaduri`
- **Calificare leaduri** — `califică leadul 12` → status în CRM
- **Pipeline vânzări în 10 pași** — comanda `pipeline` sau `/api/pipeline`
- **Bază de cunoștințe Q&A** (`/cunostinte`) — răspunsuri automate
- **Ticketing** — sesizările devin cazuri în CRM (`caz nou: ...`)
- **Follow-up automat** — job care creează sarcini pentru leaduri uitate (`POST /api/jobs/followup`)
- **Webhooks WhatsApp/Messenger** funcționale (verificare + recepție) — vezi `GHID_CANALE.md`

## Comenzi de chat din Faza 1

- `produs nou: Nume, preț` · `catalog` · `oferta pentru Client: produs x 2, altul x 1`
- `scor leaduri` · `califică leadul 12` · `caz nou: subiect, descriere`
- `adaugă q&a: întrebarea | răspunsul` · `pipeline`

## Job-ul de follow-up (recomandat: zilnic, dimineața)

```bash
curl -X POST http://127.0.0.1:8001/api/jobs/followup
```

Creează în CRM sarcini de tip apel pentru leadurile (nou/contactat) mai vechi de
`FOLLOWUP_ZILE_LEAD` zile. Nu trimite nimic clientului — doar îți pune ție
sarcini în listă.

## Instalare

```bash
./setup.sh        # creează venv, instalează dependențe, copiază .env.example → .env
```

Completează în `.env`:
- `CRM_API_TOKEN` — token generat din CRM (Setări → Tokenuri API)
- `CRM_API_URL` — implicit `http://127.0.0.1:8000/api/v1`

## Rulare

```bash
./run.sh          # pornește pe http://127.0.0.1:8001
```

Pagini:
- `/chat` — chat intern cu Jarvis
- `/aprobari` — cereri de aprobare în așteptare + matricea de aprobare
- `/catalog` — produse/servicii
- `/oferte` — oferte + descărcare PDF
- `/cunostinte` — baza de cunoștințe Q&A
- `/sanatate` — stare sistem + conexiune CRM

```bash
./setup.sh        # creează venv, instalează dependențe, copiază .env.example → .env
```

Completează în `.env`:
- `CRM_API_TOKEN` — token generat din CRM (Setări → Tokenuri API)
- `CRM_API_URL` — implicit `http://127.0.0.1:8000/api/v1`

## Rulare

```bash
./run.sh          # pornește pe http://127.0.0.1:8001
```

Pagini:
- `/chat` — chat intern cu Jarvis
- `/aprobari` — cereri de aprobare în așteptare + matricea de aprobare
- `/sanatate` — stare sistem + conexiune CRM

## Comenzi în chat

- `ajutor` — ce știe să facă
- `lead nou: Nume Prenume, telefon, email, firmă` — creează lead în CRM
- `activitate: text` — creează activitate în CRM
- `ofertă` — pregătește ciorna și cere aprobare (PDF-ul vine în Faza 1)

Orice altceva e clasificat pe reguli și rutat la agentul potrivit; agenții
nefuncționali încă își înregistrează sarcina în coadă (`agent_tasks`).

## Structură

```
jarvis/
  app/
    config.py        setări din .env
    db.py            SQLite (jarvis.db)
    models.py        conversations, messages, agent_runs, agent_tasks,
                     approvals, offers, documents, knowledge_base,
                     audit_log, kpi_snapshots
    audit.py         jurnal append-only
    approvals.py     matricea de aprobare + cereri
    crm_client.py    client REST v1 pentru CRM (Bearer token)
    orchestrator.py  clasificare intenție + rutare
    agents/          base.py + vanzari.py + rest.py (8 stub-uri)
    main.py          FastAPI: /chat, /aprobari, /api/*, /webhooks/{canal}
  templates/         chat.html, aprobari.html
```

## Note

- CRM-ul rămâne sursa de adevăr pentru clienți, leaduri, oportunități.
- Tabelele Jarvis sunt extensii; nimic din CRM nu e modificat.
- Webhook-urile (`/webhooks/whatsapp`, `/webhooks/messenger`, …) doar înregistrează
  apelul — procesarea pe canale externe se activează în fazele următoare.
