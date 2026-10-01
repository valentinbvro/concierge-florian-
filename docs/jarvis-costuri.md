# JARVIS — Breakdown costuri de construcție

**Buget estimativ pentru ecosistemul multi-agent**
Versiune 1.0 — 30 septembrie 2026 — document financiar-tehnic

> Toate sumele sunt estimări orientative, în EUR, fără TVA. Tarifele
> providerilor externi se pot schimba — verifică-le înainte de angajamente.

---

## 1. Imaginea de ansamblu

| Categorie | Estimare | Note |
|---|---|---|
| Dezvoltare software (construit cu mine, în sesiuni) | **0 €** suplimentar | inclus în abonamentul tău; plătești cu timp de lucru împreună |
| Dezvoltare software (echipă externă, alternativă) | **13.500 – 18.000 €** | ~45–60 zile lucrătoare × ~300 €/zi (tarif freelance senior RO) |
| Setup conturi & infrastructură (one-time) | **50 – 300 €** | vezi secțiunea 3 |
| Operare lunară — pilot (Faza 0–1) | **20 – 60 €/lună** | |
| Operare lunară — regim normal (toate fazele) | **80 – 250 €/lună** | la volum mic–mediu (vezi ipotezele §4) |

**Concluzia pe scurt:** dacă îl construim împreună aici, costul de construcție
propriu-zis e aproape zero în bani — cheltuielile reale sunt conturile externe
(WhatsApp, telefonie, API LLM) și operarea lunară, care pornește de la ~20 €/lună
și crește odată cu volumul.

---

## 2. Costuri de dezvoltare, pe faze

### Opțiunea A — construit cu mine (recomandat la start)

| Fazele (din blueprint) | Efort estimat în sesiuni | Cost bani |
|---|---|---|
| Faza 0 — Fundație (orchestrator, tabele noi, chat intern, aprobări) | 3–5 sesiuni de lucru | 0 € |
| Faza 1 — Vânzări & Customer Service (pipeline, oferte PDF, Q&A, WhatsApp) | 5–8 sesiuni | 0 € |
| Faza 2 — Operațiuni + Marketing & Media (dispecerat, editorial, landing pages, competitori) | 5–8 sesiuni | 0 € |
| Faza 3 — Finanțe + BI (import extrase, anomalii, facturare ciornă, dashboard executiv) | 4–6 sesiuni | 0 € |
| Faza 4 — Produs, Growth, Risc (idei, scenarii investiții, analiză contracte) | 3–5 sesiuni | 0 € |
| Testare, reglaje, documentație finală | 2–3 sesiuni | 0 € |
| **Total** | **22–35 sesiuni** | **0 €** |

Ce "plătești" de fapt: timpul tău de decizie (aprobări, răspunsuri la
întrebările din §10 al blueprint-ului, testare) și eventualele conturi externe.

### Opțiunea B — echipă externă de dezvoltare (dacă vrei viteză sau predare la cheie)

| Fazele | Zile lucrătoare estimate | La 300 €/zi |
|---|---|---|
| Faza 0 — Fundație | 5–8 | 1.500 – 2.400 € |
| Faza 1 — Vânzări & Customer Service | 10–15 | 3.000 – 4.500 € |
| Faza 2 — Operațiuni + Marketing | 10–15 | 3.000 – 4.500 € |
| Faza 3 — Finanțe + BI | 10–12 | 3.000 – 3.600 € |
| Faza 4 — Produs, Growth, Risc | 8–10 | 2.400 – 3.000 € |
| Testare & lansare | 4–6 | 1.200 – 1.800 € |
| **Total** | **~47–66 zile** | **~14.000 – 20.000 €** |

Notă: o echipă externă va avea nevoie oricum de tine pentru decizii de business
(catalog prețuri, texte, aprobări) — nu elimină complet timpul tău.

---

## 3. Setup one-time: conturi, infrastructură, licențe

| Element | Cost one-time | Detalii |
|---|---|---|
| Server / hosting | 0 € | rulează pe aceeași mașină ca CRM-ul la început |
| Domeniu + certificat SSL | 10 – 15 €/an | doar dacă vrei acces webhooks pe domeniu propriu (recomandat pentru WhatsApp/Messenger) |
| Număr de telefon dedicat (WhatsApp Business) | 0 – 30 € | un SIM/număr separat de cel personal, ca să nu amesteci canalele |
| WhatsApp Business API (provider: 360dialog / Twilio) | 0 – 50 € | înscriere și verificare business; unii provideri au taxă de activare |
| Twilio (voce/SMS) | 0 € | plata e la utilizare |
| Aplicație Meta (Messenger + postări FB/Instagram) | 0 € | doar timp de configurare + verificare business (gratuită) |
| Stripe | 0 € | verificare cont gratuită |
| Cheie API LLM (provider la alegere) | 0 € | plata e la utilizare; unele oferă credit inițial gratuit |
| **Total setup** | **~10 – 95 €** | |

---

## 4. Costuri de operare lunare (recurente)

### Ipoteze de volum

| Scenariu | Conversații client/lună | Oferte generate | Postări social | Documente analizate |
|---|---|---|---|---|
| **Pilot** (Faza 0–1) | ~200 | ~20 | 0 | ~5 |
| **Normal** (toate fazele) | ~2.000 | ~150 | ~20 | ~30 |
| **Intensiv** | ~10.000+ | ~800 | ~60 | ~150 |

### 4.1 API LLM (creierul agenților)

Costul depinde de modelul ales. Estimări per unitate de lucru:

| Operație | Cost estimat |
|---|---|
| O conversație simplă client (5–10 mesaje) | 0,01 – 0,05 € |
| Calificare lead + notițe extrase | 0,02 – 0,06 € |
| Generare ofertă (calcul + text) | 0,05 – 0,15 € |
| Analiză contract / document (10–20 pagini) | 0,20 – 0,80 € |
| Raport BI săptămânal | 0,10 – 0,30 € |

| Scenariu | Estimare lunară LLM |
|---|---|
| Pilot | **5 – 15 €** |
| Normal | **40 – 120 €** |
| Intensiv | **200 – 600 €** |

*Pârghii de control al costului:* alegerea unui model mai ieftin pentru
sarcini simple (răspunsuri Q&A), cache pentru întrebări repetate, limite
lunare per agent cu alertă (deja prevăzute în blueprint §2, principiul 6).

### 4.2 Canale de comunicare

| Canal | Model de tarifare | Pilot | Normal |
|---|---|---|---|
| WhatsApp Business API | ~0,04 – 0,06 € / conversație de 24h | 5 – 10 € | 40 – 80 € |
| Telefonie (Twilio voce) | ~0,02 – 0,05 € / minut + ~1–2 € nr./lună | 3 – 8 € | 15 – 40 € |
| SMS (notificări) | ~0,05 – 0,09 € / SMS | 1 – 3 € | 5 – 15 € |
| Messenger / Social organic | gratuit | 0 € | 0 € |
| Email | gratuit (cont existent) | 0 € | 0 € |

### 4.3 Infrastructură

| Element | Pilot | Normal |
|---|---|---|
| Hosting (aceeași mașină ca CRM) | 0 € | 0 € |
| VPS dedicat (dacă e nevoie ulterior, ex. Hetzner) | — | 6 – 12 € |
| Backup automat (stocare) | 1 – 3 € | 2 – 5 € |
| Domeniu (amortizat lunar) | ~1 € | ~1 € |

### 4.4 Total operare lunară

| Scenariu | LLM | Canale | Infrastructură | **Total/lună** |
|---|---|---|---|---|
| **Pilot** (Faza 0–1) | 5 – 15 € | 9 – 21 € | 2 – 4 € | **~16 – 40 €** |
| **Normal** (toate fazele) | 40 – 120 € | 60 – 135 € | 9 – 18 € | **~110 – 275 €** |
| **Intensiv** | 200 – 600 € | 300 – 700 € | 15 – 30 € | **~515 – 1.330 €** |

> Observație importantă: la scenariul "Normal", dacă fiecare client câștigat
> aduce de ordinul sutelor/miilor de euro, 110–275 €/lună operare se amortizează
> din prima vânzare asistată de sistem.

---

## 5. Costuri pe faze — rezumat construcție + operare

| Faza | Build (cu mine) | Setup extern nou în fază | Operare lunară adăugată |
|---|---|---|---|
| Faza 0 — Fundație | 0 € | 0 € (doar cheie LLM) | +5 – 15 € (LLM) |
| Faza 1 — Vânzări | 0 € | 0 – 80 € (WhatsApp Business, număr) | +10 – 25 € (WhatsApp + LLM) |
| Faza 2 — Operațiuni + Marketing | 0 € | 0 € (Meta app gratuită) | +5 – 15 € (LLM postări/analize) |
| Faza 3 — Finanțe + BI | 0 € | 0 € (Stripe gratuit) | +5 – 10 € (LLM rapoarte) |
| Faza 4 — Produs, Growth, Risc | 0 € | 0 – 30 € (Twilio număr, dacă vrei voce) | +10 – 40 € (voce + analize) |

Fiecare fază își "plătește" singură operarea din luna în care e livrată —
nu ai un salt brusc de cost la final.

---

## 6. Costuri ascunse / riscuri bugetare (onest)

1. **Timpul tău de aprobare** — sistemul e proiectat cu omul în buclă; dacă
   aprobările întârzie zile întregi, valoarea scade. Nu costă bani, costă
   disciplină.
2. **Mentenanță anuală** — regulă generală în software: ~10–20% din costul de
   dezvoltare pe an (update-uri, adaptări la API-uri schimbate de Meta/Twilio).
   Cu mine: câteva sesiuni pe an. Extern: 1.500 – 3.500 €/an.
3. **Schimbări de tarife la provideri** — Meta, Twilio, providerii LLM își
   modifică prețurile; alertele de buget din sistem te prind din timp.
4. **Calitatea datelor de intrare** — dacă catalogul de prețuri sau baza Q&A
   sunt incomplete, agentul cere multe aprobări la început. E normal în primele
   2–4 săptămâni (perioadă de "antrenare").
5. **Telefonie automată** — apelurile AI sunt utile, dar reglementate diferit
   de la țară la țară; verifică regulile locale înainte de campanii outbound.

---

## 7. Recomandare de buget de pornire

Pentru **Faza 0 + Faza 1** (primele 3–4 săptămâni, construit cu mine):

| Element | Suma |
|---|---|
| Dezvoltare | 0 € |
| Setup (domeniu dacă lipsește + număr WhatsApp) | 10 – 95 € |
| Operare 2 luni pilot | 30 – 80 € |
| **Buget de pornire recomandat** | **~50 – 175 €** |

Cu acest buget ai, la finalul Fazei 1: Jarvis funcțional în chatul intern,
leaduri care intră din WhatsApp, calificare automată, oferte PDF cu aprobarea
ta și follow-up automat — adică nucleul care produce valoare.

---

*Document de lucru — se actualizează cu tarife reale pe măsură ce alegem
providerii concreți (întrebările din §10 ale blueprint-ului).*
