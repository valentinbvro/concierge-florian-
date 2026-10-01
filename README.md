# concierge-florian-

Platforma de operare pentru compania de transport de lux: **Jarvis** (sistem multi-agent) + **CRM**.

## Structură

```
concierge-florian-/
├── jarvis/      # Jarvis — orchestrator + 10 agenți (FastAPI, :8001)
├── crm/         # CRM — contacte, leaduri, activități (FastAPI, :8000)
└── docs/        # blueprint, costuri, ghid de prezentare, manual de utilizare (RO/FR)
```

## Pornire rapidă (local)

```bash
# 1. CRM
cd crm && cp .env.example .env && ./run.sh        # http://127.0.0.1:8000

# 2. Jarvis (în alt terminal)
cd jarvis && cp .env.example .env && ./run.sh     # http://127.0.0.1:8001
```

Completează valorile reale în fiecare `.env` (vezi `.env.example`). Fișierele `.env` nu se comit în git.

## Documentație

- `docs/jarvis-blueprint.md` — arhitectura completă (faze 0–4 + Hermes + mod demo)
- `docs/jarvis-costuri.md` — costuri de construcție și operare
- `docs/ghid-prezentare-jarvis.md` — ghid de prezentare pentru client (RO)
- `docs/manual-utilizare-jarvis.md` — manual de utilizare bilingv (RO/FR)
- `jarvis/GHID_CANALE.md` — conectarea canalelor externe (WhatsApp, Messenger, Meta)

## Principii

- Interfață bilingvă română–franceză.
- Tot ce e ireversibil sau costisitor (oferte, postări, anulări, facturi, investiții) trece prin **aprobare umană**.
- Finanțele se validează cu contabilul; analiza juridică e doar pre-filtru, nu consultanță.
- Hermes (agentul 10) învață continuu din operare — nicio învățare nu se aplică singură.
