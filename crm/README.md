# CRM — aplicație de management al relațiilor cu clienții

Aplicație web CRM completă, în limba română, construită cu **FastAPI**,
**SQLAlchemy** (SQLite), **Jinja2**, **Tailwind CSS** și **Chart.js**.

## Instalare

```bash
cd ~/workspace/crm
./venv/bin/pip install -r requirements.txt   # opțional, pachetele sunt deja instalate
```

Pachete necesare: `fastapi`, `uvicorn`, `sqlalchemy`, `jinja2`,
`python-multipart`, `itsdangerous`.

## Pornire

```bash
./run.sh
```

Apoi deschide în browser: **http://127.0.0.1:8000**

La prima pornire baza de date (`crm.db`) este creată și populată automat
cu date demo.

Variabilă de mediu opțională:

```bash
CRM_SECRET="un-secret-puternic" ./run.sh   # secret pentru sesiuni (implicit: valoare dev)
```

## Conturi demo

| Email            | Parolă   | Rol           |
|------------------|----------|---------------|
| admin@demo.ro    | admin123 | Administrator |
| maria@demo.ro    | maria123 | Vânzări       |
| ion@demo.ro      | ion123   | Suport        |

## Funcționalități

- **Panou principal** — KPI-uri (valoare pipeline, oportunități deschise,
  leaduri noi, cazuri deschise), grafice (pipeline pe stagii, leaduri pe
  status, cazuri pe prioritate), sarcinile mele, ultimele activități.
- **Leaduri** — listă cu căutare/filtru, adăugare, editare, ștergere,
  conversie în firmă + contact + oportunitate.
- **Firme** — listă, detalii cu contacte/oportunități/cazuri/activități asociate.
- **Contacte** — listă, detalii, activități asociate.
- **Oportunități** — kanban cu drag & drop între cele 6 stagii,
  adăugare, editare, ștergere, pagină de detaliu.
- **Cazuri** — tichete de suport cu status și prioritate, filtre,
  activități asociate.
- **Activități** — sarcini/apeluri/emailuri/întâlniri, filtru „ale mele”,
  bifare deschis/închis, legare de orice entitate.
- **Utilizatori** (doar admin) — adăugare, activare/dezactivare, roluri.
- **Setări** — numele firmei + comutatoare pentru automatizări.

### Automatizări (comutabile din Setări)

1. **Sarcină la lead nou** — creează sarcina „Contactează leadul" cu
   scadență mâine.
2. **Follow-up la oportunitate câștigată** — la trecerea în „câștigat",
   creează sarcină la +7 zile.
3. **Sarcină la caz urgent** — la caz nou cu prioritate „urgentă",
   creează sarcină cu scadență azi.

## Structură

```
~/workspace/crm/
├── app/
│   ├── __init__.py
│   ├── main.py        # aplicația FastAPI: rute, automatizări, dashboard
│   ├── models.py      # modelele SQLAlchemy
│   ├── db.py          # engine SQLite + sesiune
│   ├── auth.py        # hash parole PBKDF2, sesiuni, dependențe
│   └── seed.py        # date demo (rulează la prima pornire)
├── templates/         # template-uri Jinja2 (Tailwind + Chart.js via CDN)
├── crm.db             # baza de date SQLite (creată la prima pornire)
├── venv/              # mediu virtual Python
├── run.sh             # script de pornire
└── README.md
```

## Note

- Parolele sunt hash-uite cu PBKDF2-HMAC-SHA256 (200.000 iterații).
- Sesiunile sunt cookie-uri semnate (`SessionMiddleware`).
- Pagina `/utilizatori` este accesibilă doar rolului `admin`.
