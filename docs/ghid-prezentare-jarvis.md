# Ghid de prezentare — Jarvis (platforma de operare pentru taxi de lux)

**Pentru:** Valentin (dezvoltator) → prezentare către șeful companiei cliente.
**Durată recomandată:** 25–35 minute + 10 minute întrebări.
**Mediu:** laptop cu Jarvis pornit local (`http://127.0.0.1:8001`), modul demo încărcat.

---

## 1. Pregătire (cu 15 minute înainte)

- [ ] Pornește CRM-ul (`~/workspace/crm/run.sh`) și Jarvis (`~/workspace/jarvis/run.sh`).
- [ ] Deschide `http://127.0.0.1:8001/demo` și verifică că bannerul auriu **„DATE DEMONSTRATIVE"** apare.
- [ ] Dacă datele demo lipsesc: butonul **„Încarcă datele demo"** de pe pagina `/demo`.
- [ ] Comută limba pe **FR** din header (clientul e francofon) — arată-i și toggle-ul RO/FR.
- [ ] Închide tab-urile inutile; mărește zoom-ul la 110–125%.

## 2. Deschidere (3 min) — problema, nu tehnologia

> „Conduceți ~15 clienți pe zi pe 11 canale — WhatsApp, Instagram, Facebook, LinkedIn, telefon… Jarvis e omul din dispecerat care nu doarme niciodată: răspunde, programează curse, emite facturi și vă învață obiceiurile. Tot ce e ireversibil — oferte, postări, anulări, bani — trece prin aprobarea dumneavoastră."

**Nu începe cu arhitectura.** Începe cu o zi din viața dispeceratului.

## 3. Traseul demo (20 min) — în ordinea asta

### 3.1. `/demo` — tabloul de bord (4 min)
- Arată KPI-urile, campaniile cu ROAS, trendul de 7 zile, cursele zilei.
- Spune clar: **„Toate cifrele de aici sunt fictive, generate pentru demonstrație."**
- Mesaj-cheie: *așa va arăta dimineața dumneavoastră — totul dintr-o privire.*

### 3.2. Chat-ul (5 min) — momentul „wow"
Din `/chat`, tastează live (sau arată comenzi pregătite):
- `curse azi` → lista curselor zilei
- `cursă nouă: Jean Dupont, +33612345678, Paris 8 → Aeroport CDG, azi 18:30` → se creează cursa
- `atribuie cursa 3 lui Mihai` → atribuire
- `facturi restante` → restanțele
- Pune o întrebare fără răspuns în baza de cunoștințe → va fi preluată de **Hermes** (vezi 3.7).

### 3.3. `/dispecerat` (3 min)
- Șoferi, mașini, statusurile curselor. Arată fluxul: rezervată → confirmată → în curs → finalizată.
- „Cursa finalizată cu preț generează automat ciorna de factură."

### 3.4. `/finante` + `/bi` (4 min)
- Facturi, încasări, TVA. **Pennylane:** ciorne automate, emiterea cu număr legal doar cu aprobare.
- `/bi`: încasări azi, facturat luna, top clienți.
- Mesaj-cheie: *contabilul primește totul pregătit, nu mai vânează hârtii.*

### 3.5. `/aprobari` (2 min)
- Arată o cerere în așteptare și explică: **nimic ireversibil nu pleacă fără om.**
- „Dumneavoastră aprobați de pe telefon, cu un click."

### 3.6. `/marketing` + `/produs` + `/growth` + `/risc` (3 min, rapid)
- Marketing: postări cu aprobare înainte de publicare, plan editorial.
- Produs/Growth: bancă de idei → oportunități cu ROI → bugete.
- Risc: verificări cu scadențe (ITP, asigurări), pre-filtru contracte (nu înlocuiește avocatul).

### 3.7. `/hermes` — diferențiatorul (3 min)
- „Aici Jarvis **învață singur**": întrebările fără răspuns devin sugestii; dumneavoastră completați răspunsul corect, aprobați, iar de a doua oară Jarvis știe.
- Arată o sugestie propusă → completează răspunsul → aprobă → aplică.
- Mesaj-cheie: *sistemul devine mai bun în fiecare săptămână, fără programator.*

## 4. Întrebări probabile (și răspunsuri)

| Întrebare | Răspuns |
|---|---|
| „Merge cu WhatsApp-ul nostru?" | Da — webhook-urile sunt gata; conectăm numărul companiei când îmi dați accesul (ghid în `GHID_CANALE.md`). |
| „Cine vede datele?" | Totul rulează pe serverul dumneavoastră. Jurnalele sunt append-only. |
| „Ce se întâmplă dacă greșește?" | Acțiunile ireversibile cer aprobare. Erorile devin semnale pentru Hermes, nu se repetă la nesfârșit. |
| „Cât costă lunar?" | Pilot ~16–40 €/lună; operare normală ~110–275 €/lună (detalii în `jarvis-costuri.md`). |
| „Facturile sunt legale?" | Da — Pennylane emite cu număr legal; validarea finală rămâne la contabil. |
| „Înlocuiește dispecerul?" | Nu — îi ia munca repetitivă; omul decide cursele sensibile și aprobă. |

## 5. Închidere (2 min)

- Rezumă în 3 fraze: **vede tot** (demo), **execută** (dispecerat+finanțe), **învață** (Hermes) — iar omul aprobă.
- Propune pasul următor concret: *„Dacă vă place, săptămâna viitoare conectăm WhatsApp-ul și importăm șoferii și mașinile reale. Datele demo se șterg cu un click."*
- Lasă manualul de utilizare (`manual-utilizare-jarvis.md`) ca document.

## 6. Ce să NU faci

- Nu pretinde că datele demo sunt reale — bannerul e acolo cu un motiv.
- Nu promite termene de conectare fără accesul la conturi (Meta/WhatsApp/Pennylane cer pași din partea clientului).
- Nu intra în detalii de cod/arhitectură decât dacă întreabă.
- Nu arăta tokenuri, chei sau fișierul `.env`.
