# JARVIS — Blueprint arhitectură

**Sistem multi-agent pentru operarea companiei**
Versiune 1.0 — 30 septembrie 2026 — document tehnic

---

## 1. Rezumat executiv

JARVIS este un sistem software compus dintr-un **agent orchestrator central** (Jarvis) și **9 agenți specializați**, conectați la CRM-ul existent al companiei și la canalele de comunicare (WhatsApp, Facebook Messenger, telefon, social media, email).

Scopul: automatizarea și asistarea operațiunilor companiei pe tot ciclul — de la primul contact cu un lead, până la ofertare, vânzare, livrare, follow-up, marketing, finanțe și conformitate — cu **omul în buclă** acolo unde deciziile sunt ireversibile sau costisitoare.

Sistemul se construiește **peste CRM-ul existent** (`~/workspace/crm` — FastAPI + SQLAlchemy + SQLite), pe care îl extinde, nu îl înlocuiește. CRM-ul rămâne sursa de adevăr pentru clienți, leaduri, oportunități, activități și cazuri.

---

## 2. Principii de proiectare

1. **Un creier, multe mâini.** Jarvis decide *ce* trebuie făcut și *cine* o face; agenții specializați execută. Nicio logică de business critică nu trăiește în afara agenților versionați.
2. **CRM-ul e sursa de adevăr.** Toate datele despre clienți/leaduri/oportunități trec prin API-ul REST existent al CRM-ului. Agenții nu țin evidențe paralele.
3. **Omul aprobă ce e ireversibil.** Trimiterea unei oferte peste un prag, o plată, o postare publică, ștergerea de date — toate cer aprobare umană explicită (buton în interfață sau mesaj de confirmare).
4. **Totul e auditabil.** Fiecare acțiune a unui agent e înregistrată: cine, ce, când, cu ce date, cu ce rezultat. Jurnalul de audit nu poate fi șters de agenți.
5. **Degradare elegantă.** Dacă un canal extern pică (ex. WhatsApp API), sistemul continuă pe celelalte și marchează sarcinile restante — nu pierde mesaje.
6. **Costuri sub control.** Fiecare agent are buget de operare (apeluri LLM, mesaje) și alerte la depășire.

---

## 3. Arhitectura generală

```
                    ┌─────────────────────────────────┐
                    │        CANALE DE INTRARE         │
                    │  WhatsApp │ Messenger │ Telefon  │
                    │  Social   │  Email    │ Web chat │
                    └────────┬────────────────────────┘
                             │ evenimente (webhook)
                    ┌────────▼────────────────────────┐
                    │      JARVIS ORCHESTRATOR         │
                    │  rutare intenții │ planificare  │
                    │  memorie │ politici & aprobări   │
                    └────────┬────────────────────────┘
                             │ sarcini
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
 ┌─────────────┐    ┌──────────────┐    ┌──────────────┐
 │ 1. VÂNZĂRI  │    │ 2. OPERAȚIUNI│    │ 3. FINANȚE   │  ... (9 agenți)
 │ & CUSTOMER  │    │ & DISPECERAT │    │ & CONTABIL.  │
 │   SERVICE   │    │              │    │              │
 └──────┬──────┘    └──────┬───────┘    └──────┬───────┘
        └────────────────┼───────────────────┘
                         │ API REST (token)
              ┌──────────▼──────────┐
              │   CRM EXISTENT      │◄──── interfața web actuală
              │ Lead│Firmă│Contact  │
              │ Oportunitate│Caz    │
              │ Activitate│Utilizator
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │  EXTENSII DE DATE   │
              │ conversații, mesaje │
              │ oferte, documente,  │
              │ knowledge base,     │
              │ jurnal audit,       │
              │ sarcini agenți      │
              └─────────────────────┘
```

Fluxul tipic: un mesaj sosește pe un canal → Jarvis înțelege intenția → creează un plan → delegă agentului potrivit → agentul lucrează prin unelte (tools: API CRM, trimitere mesaje, generare documente) → rezultatul e salvat în CRM + jurnal de audit → omul e notificat sau i se cere aprobare.

---

## 4. Componente

### 4.1 Jarvis Orchestrator (master agent)

Rol: poarta de intrare și coordonatorul. Nu face muncă de specialitate, ci:

- **Înțelegerea intenției** — clasifică fiecare cerere/mesaj: vânzare, suport, reclamație, întrebare financiară, cerere de raport etc.
- **Planificare** — descompune cererile complexe în pași și îi atribuie agenților (ex. "pregătește oferta pentru X" → agent vânzări: adună date → calculează preț → generează PDF → cere aprobare).
- **Memorie** — (a) memoria conversației curente, (b) memorie pe termen lung: preferințele clientului, istoricul interacțiunilor, decizii anterioare.
- **Politici și aprobări** — aplică matricea de aprobare (secțiunea 8): decide ce poate face singur un agent și ce trebuie să aștepte OK-ul uman.
- **Rezolvarea conflictelor** — dacă doi agenți au nevoie de aceeași resursă sau dau răspunsuri contradictorii, Jarvis arbitrează.

Interfața umană a lui Jarvis: un chat intern (web) unde Valentin sau echipa pot cere orice ("fă-mi un rezumat al vânzărilor de săptămâna asta", "pregătește oferta pentru firma X") și pot aproba/respinge acțiuni propuse.

### 4.2 Agenții specializați

Fiecare agent = un modul cu: responsabilități clare, set de unelte (tools), declanșatoare (ce îl pornește) și limite de autonomie.

#### Agentul 1 — Vânzări & Customer Service
*Mapare notițe: pipeline-ul în 10 pași + citire social media/WhatsApp/Facebook/telefon + CRM clienți.*

- Pașii pipeline-ului implementați ca mașină de stări, aliniată la stagiile din CRM (`prospectare → calificare → propunere → negociere → castigat/pierdut`):
  1. **Inițiere contact** — răspunde automat la mesaje noi (WhatsApp/Messenger/telefon/email), prezintă firma, colectează date → creează Lead în CRM.
  2. **Administrare** — menține fișa leadului la zi (sursă, notițe, scor).
  3. **Extragere și catalogare** — extrage date structurate din conversații (nevoi, buget, termen) și le atașează leadului.
  4. **Calificarea leadurilor** — scoring automat (potențial, potrivire, urgență); leadurile slabe sunt marcate `pierdut` cu motiv.
  5. **Calcul și întocmire ofertă** — pe baza catalogului de prețuri/servicii → generează ofertă PDF → **cere aprobare umană** înainte de trimitere.
  6. **Negociere** — gestionează obiecții standard în limite de discount pre-aprobate; peste limită → escaladează la om.
  7. **Închidere vânzare** — mută oportunitatea pe `castigat`, creează activități de onboarding.
  8. **Raport și livrare** — confirmă livrarea/prestarea, colectează dovada.
  9. **Calcul preț serviciu** — motor de pricing: tarifare pe serviciu, pachete, discounturi, TVA.
  10. **Follow-up** — mementouri automate la 3/7/30 zile pentru oferte fără răspuns.
  11. **Fidelizare** — campanii de reactivare pentru clienți inactivi, cerere de recenzii/testimoniale.
- **Customer service**: răspunde la întrebări frecvente din baza de cunoștințe; creează Cazuri în CRM pentru probleme reale și le urmărește până la rezolvare.

#### Agentul 2 — Operațiuni & Dispecerat
*Mapare notițe: analizează intervenții, livrare/confirmare/atribuire, monitor timp real, anticipează, rezolvă, actualizare financiară.*

- Primește comenzi/lucrări de la agentul de vânzări → le transformă în sarcini de execuție cu responsabili și termene.
- **Atribuire inteligentă**: propune cine execută (după competențe, disponibilitate, zonă).
- **Monitorizare în timp real**: tablou de bord cu stadiul lucrărilor; alerte la întârzieri.
- **Anticipare**: detectează blocaje (ex. material lipsă, suprapuneri de program) înainte să devină probleme.
- **Rezoluție incidente**: pași standard de remediere + escaladare.
- La final: marchează livrarea, atașează dovada și notifică agentul financiar pentru facturare.

#### Agentul 3 — Finanțe & Contabilitate
*Mapare notițe: admin cont bancar, Stripe/payment, booking engine, extrage & clasifică, detect anomalii, categ cheltuieli, rapoarte & insight.*

- **NU** înlocuiește contabilul. Rolul lui: pregătire, clasificare, semnalare.
- Import și clasificare automată a tranzacțiilor (extras bancar CSV, Stripe) pe categorii de venituri/cheltuieli.
- **Detectare anomalii**: cheltuieli neobișnuite, duplicate, abateri de la buget → alertă.
- Facturare: generează facturi/proforme din oportunitățile câștigate (integrare viitoare cu e-factura, cu validare umană obligatorie).
- Încasări: urmărește facturi neplătite → mementouri automate politicoase.
- Rapoarte: cash-flow, profit/pierdere pe perioadă, top cheltuieli — la cerere sau recurent.
- **Limite stricte**: nu inițiază plăți singur; nu modifică înregistrări contabile fără aprobare.

#### Agentul 4 — Marketing & Media
*Mapare notițe: roadmap evenimente, Google Trends, analiză competitori, știri, feedback, comportament client, oportunități noi, postări social media, plan editorial, landing pages, KPI, studiere piață.*

- **Plan editorial**: generează calendar de conținut (teme, canale, frecvență) → omul aprobă → agentul pregătește textele/vizualele.
- **Publicare**: postează pe canalele conectate (cu aprobare pentru fiecare postare, cel puțin la început).
- **Ascultare socială**: monitorizează mențiuni despre firmă și subiecte relevante; rezumate zilnice.
- **Landing pages**: generează pagini de captare pentru campanii (template + conținut), conectate la formularul care creează Lead în CRM.
- **Tendințe**: interoghează Google Trends / știri pe teme relevante → idei de conținut și alerte de piață.
- **KPI**: urmărește reach, engagement, leaduri din marketing; raport săptămânal.

#### Agentul 5 — Marketing Research & Competitor Monitoring
*Mapare notițe: monitor competitori, elemente media.*

- Urmărește 1–2 competitori definiți: oferte, prețuri publice, campanii, recenzii.
- Fișă de competitor actualizată periodic: puncte tari/slabe, mișcări recente.
- Alerte la schimbări importante (ex. competitorul a lansat un serviciu nou / a schimbat prețurile).
- Culege "elemente media": ce formate și mesaje funcționează în nișă → le pasează agentului de marketing.

#### Agentul 6 — Business Intelligence
*Mapare notițe: venit & profit analiză, surse leaduri, marjă profit marketing, revenue/leads, satisfacție clienți, stare companie în timp real, idei KPI.*

- Tablou de bord executiv: venituri, profit, pipeline, conversii — actualizat automat.
- **Atribuire**: de unde vin leadurile care se convertesc (canal, campanie) → marjă de profit per canal de marketing.
- **Satisfacție clienți**: scoruri din follow-up-uri și cazuri de suport; trenduri.
- "Starea companiei în timp real": un ecran unic cu sănătatea afacerii + abateri de la obiective.
- Sugerează KPI-uri noi când vede tipare (ex. "rata de răspuns la oferte a scăzut 3 săptămâni la rând").

#### Agentul 7 — Produs & Inovație
*Mapare notițe: idei, venit, servicii noi, experiențe noi.*

- Bancă de idei: colectează idei din echipă, clienți, piață; le structurează (problemă, soluție, efort, impact).
- Analizează ce servicii se vând cel mai bine și propune pachete noi sau îmbunătățiri.
- Urmărește "experiențe noi": ce fac alții în industrie → fișe de oportunitate.
- Nu decide singur lansări — pregătește dosarul decizional pentru Valentin.

#### Agentul 8 — Growth & Capital Allocation
*Mapare notițe: investiții inteligente, maxim impact, creștere sustenabilă.*

- Evaluează propunerile de investiții (marketing, echipamente, angajări) după criterii: cost, randament estimat, risc, timp de recuperare.
- Recomandă alocarea bugetului între canale/inițiative pentru impact maxim.
- Modelează scenarii simple ("dacă dublăm bugetul de reclame pe canalul X cu conversia actuală…").
- Principiu: creștere sustenabilă — semnalează când creșterea ar suprasolicita operațiunile.

#### Agentul 9 — Risc, Conformitate & Securitate
*Mapare notițe: avocat/contract, semnalizare nereguli, analiză contract.*

- **Analiză contracte**: citește contracte (PDF), extrage clauze-cheie, termene, penalități → rezumat + puncte de atenție. **Nu e consultanță juridică** — e un pre-filtru pentru avocat.
- **Semnalare nereguli**: tipare suspecte (acces neobișnuit la date, discrepanțe financiare, conflicte de interese) → alertă confidențială către Valentin.
- Verifică conformitatea acțiunilor celorlalți agenți cu politicile interne (ex. "oferta respectă marja minimă?").
- Gestionează secretele (chei API, tokeni): stocare securizată, rotație, acces pe principiul minimului necesar.

#### Agentul 10 — Hermes: antrenare & învățare continuă ✅ LIVRAT 01.10.2026
*Antrenare continuă a sistemului din operare, cu omul în buclă.*

- **Semnale**: întrebări fără răspuns (hook în `Agent.ruleaza`), aprobări respinse (hook în `approvals.decide`), erori de agent — culese automat în `semnale_antrenare`.
- **Analiză**: job `POST /api/jobs/hermes` grupează semnalele și generează sugestii (`cunostinta_noua` / `ajustare_prag`) în `sugestii_invatare`. Idempotent, fără duplicate.
- **Omul decide**: completează răspunsul propus, aprobă/respinge (pagină `/hermes` sau chat: `aprobă/respinge/aplică sugestia N`).
- **Aplicare**: sugestia aprobată intră în baza de cunoștințe (`cunostinte.adauga`, etichetă `hermes`); status `aplicata`.
- **Instrucțiuni versionate**: `InstructiuneAgent` — fiecare agent are instrucțiuni cu versiuni și trasabilitate.
- **Principiu**: nicio învățare nu se aplică singură. Totul trece prin aprobare umană.
- Pagina `/hermes`: raport (semnale neprocesate, cunoștințe învățate, sugestii propuse), listă sugestii cu acțiuni, istoric instrucțiuni.

### 4.3 Stratul de canale (intrări/ieșiri)

| Canal | Intrare | Ieșire | Necesită | Stadiu |
|---|---|---|---|---|
| WhatsApp | webhook mesaje | răspunsuri, oferte, mementouri | cont WhatsApp Business API + HTTPS public | ✅ webhook funcțional (Faza 1); conectarea contului → `GHID_CANALE.md` |
| Facebook Messenger | webhook | răspunsuri | pagină Facebook + aplicație Meta | ✅ webhook funcțional (Faza 1) |
| Instagram | webhook (același Meta) | răspunsuri DM | cont business Instagram legat de pagina FB | 🔜 infrastructura e aceeași ca Messenger |
| LinkedIn | — | postări companie | token companie | ⚠️ fără API public de mesagerie pentru automatizare |
| Alte ~7 canale | de identificat | — | — | ❓ de clarificat cu Valentin |
| Telefon | apeluri (transcriere) | apeluri automate simple | cont Twilio (voce) | 🔜 fază ulterioară |
| Email | IMAP/webhook | emailuri | cont SMTP/IMAP sau Gmail API | 🔜 fază ulterioară |
| Chat web intern | mesaje echipă | răspunsuri Jarvis | inclus (modul nou în CRM) | ✅ funcțional |

Toate canalele normalizează mesajele într-un format intern comun (`canal, expeditor, text, atașamente, timestamp`) și le trimit orchestratorului.

### 4.4 Stratul de date

**CRM-ul existent rămâne neschimbat** ca sursă de adevăr. Se adaugă tabele noi (în aceeași bază sau una dedicată `jarvis.db`):

- `conversations` — fir de discuție per client/canal (id, canal, contact_id, stare, scor).
- `messages` — fiecare mesaj in/out (id, conversation_id, direcție, text, atașamente, timestamp).
- `agent_runs` — fiecare execuție a unui agent (agent, sarcină, intrări, ieșiri, durată, cost, stare).
- `agent_tasks` — sarcini în coadă (agent destinatar, prioritate, termen, stare).
- `offers` — oferte generate (oportunity_id, linii, total, PDF, stare aprobare).
- `documents` — contracte și documente analizate (fișier, rezumat, clauze extrase).
- `knowledge_base` — articole Q&A pentru customer service (titlu, conținut, etichete, valabilitate).
- `audit_log` — append-only: cine/ce/când (nu poate fi modificat de agenți).
- `approvals` — cereri de aprobare (tip, detalii, solicitant, decident, decizie, timestamp).
- `kpi_snapshots` — valori KPI zilnice pentru trenduri BI.

### 4.5 Stratul de integrări

- **Conector CRM**: client Python peste API-ul REST v1 existent (token Bearer) — operațiuni CRUD pe leaduri, firme, contacte, oportunități, activități, cazuri.
- **Bus de evenimente**: coadă internă (inițial simplă, în proces; ulterior Redis) — evenimente de tipul `lead.nou`, `ofertă.aprobată`, `plată.primită`, `caz.urgent`.
- **Webhooks inbound**: endpointuri FastAPI per canal (`/webhooks/whatsapp`, `/webhooks/messenger`...), cu verificare de semnătură.
- **LLM provider**: interfață abstractă (inițial un singur provider configurabil) — agenții nu depind de un model anume.
- **Stocare fișiere**: PDF-uri oferte, contracte, atașamente — director dedicat + referințe în DB.

---

## 5. Fluxuri end-to-end (exemple)

### Fluxul A — Lead nou din WhatsApp până la vânzare închisă

1. Clientul scrie pe WhatsApp: *"Bună, mă interesează serviciul X pentru firma mea."*
2. Webhook → Jarvis clasifică: intenție vânzare → creează `conversation`, delegă **Agentului 1**.
3. Agentul 1 răspunde, pune 3–4 întrebări de calificare → creează **Lead** în CRM (sursă: WhatsApp), atașează notițele extrase.
4. Scoring: lead calificat → creează **Oportunitate** (stadiu `prospectare`) + **Activitate** de tip apel pentru om.
5. La cerere ("trimite-mi o ofertă"): agentul calculează prețul din catalog → generează PDF → creează cerere de **aprobare** → Valentin aprobă din chat → oferta e trimisă pe WhatsApp + email.
6. Clientul negociază: agentul poate oferi până la 10% discount (limită pre-aprobată); peste → escaladează.
7. Clientul acceptă → oportunitatea trece pe `castigat` → sarcină către **Agentul 2** (livrare) și către **Agentul 3** (facturare).
8. Follow-up automat la 7 zile după livrare: *"Cum a fost experiența?"* → scor satisfacție → **Agentul 6** (BI).

### Fluxul B — Postare social media

1. **Agentul 4** propune săptămânal 3 idei de postări (pe baza trendurilor de la **Agentul 5**).
2. Valentin aprobă 2 → agentul redactează textele și pregătește vizualele.
3. Aprobare finală per postare → programare și publicare → link-urile din postări duc la landing page cu formular → leaduri noi în CRM.

### Fluxul C — Alertă financiară

1. **Agentul 3** importă extrasul bancar → clasifică tranzacțiile → detectează o cheltuială dublată la un furnizor.
2. Creează alertă + activitate în CRM pentru Valentin, cu dovada (liniile duplicat).
3. Nu face nimic ireversibil — doar semnalează și propune corecția.

---

## 6. Contracte între agenți (API intern)

Agenții comunică prin sarcini structurate, nu prin text liber:

```json
{
  "task_id": "t-20260930-0042",
  "from": "jarvis",
  "to": "agent_vanzari",
  "action": "genereaza_oferta",
  "payload": {
    "oportunity_id": 17,
    "linii": [{"serviciu": "X", "cantitate": 2}],
    "discount_max_pct": 10
  },
  "needs_approval": true,
  "deadline": "2026-10-01T12:00:00"
}
```

Răspunsul conține: `status` (ok / parțial / eșuat / așteaptă_aprobare), `result` (date structurate), `crm_refs` (ce s-a creat/modificat în CRM), `cost` (consum de resurse), `audit_id`.

---

## 7. Securitate, conformitate, audit

- **Autentificare**: agenții folosesc tokenuri API dedicate (ca cele existente în CRM), cu permisiuni minime per agent (ex. agentul de marketing nu vede date bancare).
- **Secrete**: chei API externe în variabile de mediu / seif, niciodată în cod sau în mesaje.
- **Matricea de aprobare** (exemple):

| Acțiune | Poate singur | Cu aprobare |
|---|---|---|
| Răspuns la întrebare frecventă | da | — |
| Creare lead / activitate / caz | da | — |
| Trimitere ofertă sub 5.000 € | — | da |
| Discount peste 10% | — | da |
| Postare publică | — | da |
| Inițiere plată | — | da (mereu) |
| Ștergere date | niciodată (doar omul) | — |

- **Jurnal de audit** append-only: fiecare acțiune externă (mesaj trimis, ofertă generată, fișier creat) e înregistrată cu timestamp și nu poate fi ștearsă de agenți.
- **GDPR**: datele clienților stau în CRM; agenții procesează minimul necesar; la cerere de ștergere, omul execută, sistemul confirmă propagarea.
- **Financiar/fiscal**: documentele cu valoare fiscală (facturi) sunt generate ca *ciorne* și validate uman înainte de emitere; integrarea e-factura se face doar cu dublă verificare.
- **Juridic**: Agentul 9 oferă *analiză preliminară*, marcată vizibil "nu constituie consultanță juridică".

---

## 8. Infrastructură și costuri

### 8.1 Stack propus

- **Backend**: Python + FastAPI (același ca CRM-ul) — un serviciu nou `jarvis/` lângă `crm/`, care vorbește cu CRM-ul prin API-ul REST.
- **Bază de date**: SQLite la început (ca CRM-ul), migrare la PostgreSQL când volumul crește.
- **Lucrători de fundal**: procese dedicate pentru sarcini lungi (monitorizare, importuri) — `systemd` / cron la început, coadă (Redis + worker) ulterior.
- **LLM**: provider extern configurabil (cheie API a firmei); interfață abstractă ca să poți schimba modelul fără să rescrii agenții.
- **Canale**: webhooks FastAPI + provideri externi (vezi tabelul din 4.3).

### 8.2 Costuri recurente estimate (orientativ)

- API LLM: în funcție de volum — de la câțiva €/lună (sute de conversații) la zeci/sute € (mii de conversații + analize documente). Fiecare agent raportează consumul; alerte la praguri.
- WhatsApp Business API: ~0,03–0,06 € / conversație (tarife provider).
- Telefonie (Twilio): ~0,02–0,05 € / minut + număr lunar (~1–2 €).
- Hosting: poate rula pe același server ca CRM-ul la început (cost 0 suplimentar).

### 8.3 Ce NU e nevoie să cumperi din prima

Servere noi, licențe scumpe, platforme "AI enterprise". Totul pornește pe infrastructura existentă și crește odată cu utilizarea.

---

## 9. Plan de implementare pe faze

### Faza 0 — Fundație (săptămâna 1) ✅ LIVRAT 2026-10-01

Proiectul e construit în `~/workspace/jarvis/` și testat end-to-end:

- Repo `jarvis/` + structură de proiect; client Python pentru API-ul CRM (Bearer token, testat real).
- Tabelele noi de date (secțiunea 4.4); jurnalul de audit append-only.
- Jarvis Orchestrator minimal: chat intern + clasificare intenție pe reguli + rutare către agenți.
- Agentul 1 (Vânzări) parțial funcțional: creează leaduri/activități în CRM, cere aprobare pentru oferte.
- Ceilalți 8 agenți ca stub-uri (își înregistrează sarcinile în coadă, nu se pierde nimic).
- Matricea de aprobare + interfața de aprobare (pagina Aprobări).
- Webhook-uri stub pentru canalele viitoare.
- Testat: lead + activitate create în CRM prin chat, ofertă → aprobare → decizie, audit, coadă sarcini; datele de test șterse.
- **Livrabil**: poți vorbi cu Jarvis în chatul intern, iar el știe să creeze leaduri/activități în CRM.

### Faza 1 — Vânzări & Customer Service (săptămânile 2–3) ✅ LIVRAT 2026-10-01

Construit în `~/workspace/jarvis/` peste Faza 0 și testat end-to-end (datele de test șterse după):

- **Catalog produse/servicii** (tabel nou `produse`) — pagină `/catalog` + comenzi chat
  `produs nou: Nume, preț` / `catalog`.
- **Motor de oferte complet**: linii cu cantitate/preț/discount, TVA 19% configurabil,
  numerotare automată (OF-2026-0001), calcul subtotal/total.
- **Generare PDF oferte** (reportlab, font DejaVu — diacritice românești corecte);
  PDF-ul se generează automat la aprobarea cererii, se descarcă din `/oferte`.
- **Scoring leaduri** 0–100 pe reguli transparente (date contact, firmă, sursă, status)
  — comanda `scor leaduri`; **calificare** — `califică leadul 12` scrie statusul în CRM.
- **Pipeline vânzări în 10 pași** — comanda `pipeline` sau `/api/pipeline`, calculat live
  din leadurile/oportunitățile CRM + ofertele Jarvis.
- **Baza de cunoștințe Q&A** (tabel existent, acum cu pagină `/cunostinte` + API);
  întrebările cu răspuns cunoscut primesc răspuns automat pe chat intern și pe canalele externe.
- **Ticketing**: sesizările devin cazuri în CRM (`caz nou: ...` sau detectare automată
  pe cuvinte-cheie ca „nu merge", „defecțiune", „reclamație").
- **Follow-up automat**: job (`POST /api/jobs/followup`, recomandat zilnic prin cron)
  care creează în CRM sarcini de apel pentru leadurile uitate — nu trimite nimic clientului.
- **Webhooks WhatsApp/Messenger funcționale** (verificare token + recepție mesaje +
  rutare prin orchestrator, mod conservator pe canal extern). Ghidul de conectare
  pas-cu-pas: `~/workspace/jarvis/GHID_CANALE.md` — necesită conturile lui Valentin
  (aplicație Meta, număr business, server accesibil public prin HTTPS).
- Pagini noi: `/catalog`, `/oferte`, `/cunostinte`.
- **Livrabil**: poți construi catalogul, genera oferte PDF cu aprobare, urmări scorul
  leadurilor și pipeline-ul, iar Jarvis răspunde automat la întrebări frecvente.

> Următorul pas (Faza 2 — Operațiuni & Dispecerat): programare intervenții,
> optimizare rute, alocare echipe din datele CRM.

### Faza 2 — Operațiuni + Marketing & Media ✅ LIVRAT 01.10.2026
- Agentul 2 (Dispecerat taxi de lux): preluare curse din vânzări, atribuire șofer/mașină
  (automat sau manual), monitorizare curse în timp real, tablou de bord dispecer,
  notificări clienți/șoferi (coadă WhatsApp), activități oglindă în CRM.
- Agentul 4: postări cu aprobare, plan editorial săptămânal generat, pagină Marketing.
- Agentul 5: watchlist competitori + jurnal de observații datate.
- Bilingv RO/FR pe toată interfața și comenzile de chat (119 șiruri, toggle în header).
- Aprobator configurabil (`APPROVER_NAME`).
- **Livrabil**: de la cursă vândută, ajunge automat în dispecerat; marketingul produce
  conținut aprobat constant. Testat end-to-end; date de test curățate.

### Faza 3 — Finanțe + BI (săptămânile 7–9) ✅ LIVRATĂ 01.10.2026
- Agentul 3 (funcțional): integrare **Pennylane API v2** — adaptor cu mod demo
  (fără token = nicio rețea; totul funcționează local + simulat).
- Ciorne automate de facturi la finalizarea curselor (local + draft Pennylane);
  emiterea (finalizarea — ireversibilă) și trimiterea pe email cer aprobare umană.
- Urmărire încasări (plăți parțiale/totale), sincronizare statusuri din Pennylane.
- Detecție anomalii: restanțe (severitate după zile), sume 0, duplicate, curse
  finalizate fără factură, sume aberante (>3x media).
- Agentul 6 (funcțional): dashboard BI — încasări azi, facturat lună, restanțe,
  curse finalizate, TVA, top clienți; snapshot-uri KPI zilnice pentru trenduri.
- Pagini noi bilingve: `/finante`, `/bi`; ~40 șiruri RO/FR adăugate (total ~160).
- Comenzi chat RO/FR: «factură cursa 5: 120», «emite factura 1», «trimite factura 2»,
  «factura 1 plătită: 238», «facturi restante», «sincronizează pennylane»,
  «anomalii», «dashboard» / «tableau de bord».
- **Livrabil**: "starea companiei în timp real" + închidere de lună asistată.
  Testat end-to-end; date de test curățate din Jarvis și CRM.
- Pentru conectarea reală: token API Pennylane per companie → `PENNYLANE_API_TOKEN` în `.env`.

### Faza 4 — Produs, Growth, Risc (săptămânile 10–12) ✅ LIVRATĂ 01.10.2026
- Agentul 7 (Produs & Inovație, funcțional): bancă de idei cu voturi 0–10,
  fișe de oportunitate (investiție estimată, venit lunar, payback, ROI anual),
  promovare idee → oportunitate; aprobarea oportunității trece prin om
  (`aprobare_oportunitate` în matrice).
- Agentul 8 (Growth & Capital Allocation, funcțional): evaluare investiții
  (cost, venit lunar estimat, payback, ROI, verdict), scenarii de creștere
  proiectate din cifrele reale BI («scenariu +20%»), buget lunar planificat
  pe categorii cu grad de acoperire din veniturile facturate; decizia de
  investiție cere aprobare umană (`aprobare_investitie`).
- Agentul 9 (Risc, Conformitate & Securitate, funcțional): analiză contracte
  ca **pre-filtru euristic** (10 clauze RO/FR, scor de risc 0–10) — fiecare
  rezultat poartă disclaimerul că NU e consultanță juridică; verificări de
  conformitate cu scadență (ITP, asigurări, licențe) + job de alertare
  (`POST /api/jobs/conformitate`); registru nereguli cu severitate.
- Pagini noi bilingve: `/produs`, `/growth`, `/risc`; ~40 șiruri RO/FR adăugate
  (total ~200).
- Comenzi chat RO/FR: «idee nouă: …», «votează ideea 1: 9», «idei»,
  «oportunitate nouă: …», «promovează ideea 1: investiție 5000, venit 800»,
  «aprobă oportunitatea 1», «investiție nouă: …», «aprobă investiția 1»,
  «scenariu +20%», «buget marketing: 500», «analizează contract: …»,
  «verificare nouă: itp, B-123-ABC, 2027-01-15», «neregulă: …» + echivalentele FR.
- **Livrabil**: sistemul complet din notițe, operațional.
  Testat end-to-end (35 verificări, inclusiv fluxul aprobare → execuție pentru
  investiții/oportunități și comenzi în franceză); date de test curățate din
  Jarvis și CRM (verificat: CRM-ul are doar cele 10 activități seed).

> Cerință transversală (din 01.10.2026): interfața **bilingvă română + franceză** —
> se introduce începând cu Faza 2 (șabloane și mesaje în ambele limbi).

> Estimările sunt pentru dezvoltare asistată de mine, cu decizii prompte din partea ta la punctele de aprobare. Fiecare fază e utilizabilă independent — nu trebuie să aștepți finalul ca să vezi valoare.

---

## 10. Decizii — răspunsuri primite 01.10.2026 ✅

1. **Ce vinde compania?** Servicii de **taxi de lux** (transport premium de persoane).
   → Catalogul Jarvis = servicii: curse, transferuri aeroport, închiriere cu șofer etc.
2. **Ce canale?** WhatsApp, Instagram, Facebook, LinkedIn + alte ~7 (de identificat).
   → WhatsApp/Messenger au webhook-uri funcționale (Faza 1); Instagram poate folosi
   aceeași infrastructură Meta; LinkedIn nu oferă API public de mesagerie pentru
   automatizare — de evaluat separat; restul de ~7 canale rămân de identificat.
3. **Cine aprobă?** Șeful companiei (configurabil în Jarvis: `APPROVER_NAME` în `.env`).
4. **Volum**: ~15+ clienți/zi → costuri WhatsApp estimabile (~20–25 €/lună la volum constant).
5. **Facturare**: **Pennylane** → integrare API în Faza 3 (Agentul 3).
6. **Limba**: **română + franceză** → cerință bilingvă transversală, din Faza 2.

---

## Anexă — maparea notițelor tale la arhitectură

| Notița ta | Unde trăiește în blueprint |
|---|---|
| Jarvis, master agent (agent swarm) | §4.1 Orchestrator |
| Sales & customer service + cei 10 pași | §4.2 Agentul 1 |
| Citire social media, WhatsApp, Facebook, telefon | §4.3 Canale |
| CRM clienți, date avansate | §4.4 (CRM existent + extensii) |
| Operation and dispatch | §4.2 Agentul 2 |
| Finanțe și contabilitate (+ Stripe, booking) | §4.2 Agentul 3 |
| Marketing și media | §4.2 Agentul 4 |
| Marketing research & comp, monitor competitori | §4.2 Agentul 5 |
| Business intelligence | §4.2 Agentul 6 |
| Product and innovation | §4.2 Agentul 7 |
| Growth and capital allocation | §4.2 Agentul 8 |
| Risk, compliance and security | §4.2 Agentul 9 + §7 |

---

---

## Mod demonstrativ (date fictive pentru prezentări) ✅ LIVRAT 01.10.2026

Deoarece dezvoltatorul nu are acces la datele reale ale companiei cliente, Jarvis include un **mod demo**:
- `app/demo.py` — `seed_demo()` populează ~95 rânduri fictive (Paris, EUR), toate marcate `demo=1`;
  `sterge_demo()` le șterge integral fără a atinge datele reale (`demo=0`).
- Pagina **`/demo`** — bord în stilul planșelor LUNA (navy/auriu): KPI-uri, campanii de marketing cu
  reach/leaduri/venit/ROAS, trend venituri 7 zile, cursele de azi, șoferi, top clienți.
- Banner „DATE DEMONSTRATIVE” pe toate paginile cât modul e activ; butoane Încarcă/Șterge pe pagină;
  comenzi chat RO/FR: „încarcă demo”, „șterge demo”.
- Tabel nou `campanii` (statistici marketing). Migrare automată: coloana `demo` adăugată la pornire.

*Document generat ca bază de lucru. Se versionează odată cu implementarea — fiecare fază încheiată marchează secțiunea corespunzătoare ca "livrat".*

## Documente operaționale ✅ LIVRAT 01.10.2026

- **Ghid de prezentare** (`~/workspace/your_files/ghid-prezentare-jarvis.md`, RO): traseu demo de 25–35 min pentru Valentin → șeful companiei cliente — pregătire, deschidere, ordinea paginilor (`/demo` → chat → `/dispecerat` → `/finante`+`/bi` → `/aprobari` → `/marketing`+`/produs`+`/growth`+`/risc` → `/hermes`), întrebări probabile cu răspunsuri, închidere, ce să nu facă.
- **Manual de utilizare** (`~/workspace/your_files/manual-utilizare-jarvis.md`, bilingv RO/FR): pentru clientul final — acces, chat cu comenzi, dispecerat, finanțe, BI, marketing, produs/growth/risc, Hermes, aprobări, cunoștințe/catalog/oferte, siguranță și limite, probleme frecvente.
