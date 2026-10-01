# Manual de utilizare — Jarvis
# Manuel d'utilisation — Jarvis

Platforma de operare pentru compania de transport de lux.
Plateforme d'exploitation pour la société de transport de luxe.

> **RO:** Acest manual descrie utilizarea zilnică a platformei. Interfața este bilingvă română–franceză (comutator în antet).
> **FR :** Ce manuel décrit l'utilisation quotidienne de la plateforme. L'interface est bilingue roumain–français (sélecteur dans l'en-tête).

---

## 1. Acces / Accès

**RO:**
- Deschideți adresa platformei în browser (o primiți de la dezvoltator).
- Navigarea se face din meniul de sus: Demo, Chat, Dispecerat, Finanțe, BI, Marketing, Produs, Growth, Risc, Hermes, Aprobări, Catalog, Oferte, Cunoștințe.
- Limba se schimbă din comutatorul RO/FR din antet — alegerea se păstrează.

**FR :**
- Ouvrez l'adresse de la plateforme dans le navigateur (fournie par le développeur).
- La navigation se fait depuis le menu du haut : Démo, Chat, Dispatch, Finances, BI, Marketing, Produit, Croissance, Risque, Hermès, Approbations, Catalogue, Devis, Connaissances.
- La langue se change avec le sélecteur RO/FR de l'en-tête — le choix est conservé.

---

## 2. Chat-ul cu Jarvis / Le chat avec Jarvis

**RO:** Cel mai rapid mod de lucru. Scrieți comenzi simple, în română sau franceză. Exemple:

| Ce vreți | Comanda (RO / FR) |
|---|---|
| Cursele de azi | `curse azi` / `courses aujourd'hui` |
| Cursă nouă | `cursă nouă: Nume, +33612345678, Plecare → Destinație, azi 18:30` |
| Atribuire șofer | `atribuie cursa 3 lui Mihai` |
| Lead nou | `lead nou: Jean Dupont, +33612345678, jean@mail.fr` |
| Facturi restante | `facturi restante` / `factures en retard` |
| Încasare | `factura 4 plătită: 200` |
| Raport zilnic | `raport zilnic` / `tableau de bord` |
| Sugestii de învățare | `sugestii` / `suggestions` |
| Ajutor | `ajutor` / `aide` |

**FR :** Le moyen le plus rapide de travailler. Écrivez des commandes simples, en roumain ou en français. Exemples :

| Objectif | Commande (RO / FR) |
|---|---|
| Courses du jour | `curse azi` / `courses aujourd'hui` |
| Nouvelle course | `cursă nouă: Nom, +33612345678, Départ → Destination, azi 18:30` |
| Assigner un chauffeur | `atribuie cursa 3 lui Mihai` |
| Nouveau lead | `lead nou: Jean Dupont, +33612345678, jean@mail.fr` |
| Factures en retard | `facturi restante` / `factures en retard` |
| Encaissement | `factura 4 plătită: 200` |
| Rapport quotidien | `raport zilnic` / `tableau de bord` |
| Suggestions d'apprentissage | `sugestii` / `suggestions` |
| Aide | `ajutor` / `aide` |

---

## 3. Dispecerat / Dispatch — `/dispecerat`

**RO:**
- Vedeți șoferii, mașinile și cursele zilei cu statusuri: rezervată → confirmată → în curs → finalizată / anulată.
- Cursa nouă se creează din chat sau din canal extern (WhatsApp/Messenger); atribuirea se face manual sau automat.
- **Anularea unei curse cere aprobare** (pagina Aprobări).
- La finalizarea unei curse cu preț > 0 se generează automat **ciorna de factură**.

**FR :**
- Chauffeurs, voitures et courses du jour avec statuts : réservée → confirmée → en cours → terminée / annulée.
- La course se crée depuis le chat ou un canal externe (WhatsApp/Messenger) ; l'assignation est manuelle ou automatique.
- **L'annulation d'une course exige une approbation** (page Approbations).
- À la fin d'une course au prix > 0, un **brouillon de facture** est généré automatiquement.

---

## 4. Finanțe / Finances — `/finante`

**RO:**
- Facturi: ciorne (locale + Pennylane), emise, plătite/parțiale/restante.
- **Emiterea** (număr legal, ireversibilă) și **trimiterea pe email** cer aprobare umană.
- Încasări: înregistrați plăți parțiale sau totale din chat (`factura 4 plătită: 200`) sau din pagină.
- Sincronizarea cu Pennylane: butonul/comanda `sincronizează pennylane`.
- Anomalii: restanțe după vechime, sume zero, duplicate, curse fără factură.

**FR :**
- Factures : brouillons (local + Pennylane), émises, payées/partielles/en retard.
- **L'émission** (numéro légal, irréversible) et **l'envoi par e-mail** exigent une approbation humaine.
- Encaissements : enregistrez des paiements partiels ou totaux depuis le chat (`factura 4 plătită: 200`) ou la page.
- Synchronisation Pennylane : bouton/commande `sincronizează pennylane`.
- Anomalies : retards par ancienneté, montants zéro, doublons, courses sans facture.

---

## 5. BI — tablou de bord / tableau de bord — `/bi`

**RO:** Încasări azi, facturat luna curentă, restanțe, curse finalizate, TVA estimat, top clienți, trend 7 zile. Datele se actualizează la fiecare rulare a joburilor sau manual.

**FR :** Encaissements du jour, facturé du mois, retards, courses terminées, TVA estimée, top clients, tendance 7 jours. Données actualisées à chaque exécution des tâches ou manuellement.

---

## 6. Marketing — `/marketing`, `/competitori`

**RO:**
- Postări: redactați, programați, iar **publicarea cere aprobare**.
- Plan editorial săptămânal generat automat.
- Competitori: listă de urmărit + observații; comanda `observație: <text>`.

**FR :**
- Publications : rédigez, planifiez ; **la publication exige une approbation**.
- Calendrier éditorial hebdomadaire généré automatiquement.
- Concurrents : liste à surveiller + observations ; commande `observație: <texte>`.

---

## 7. Produs, Growth, Risc / Produit, Croissance, Risque

**RO:**
- **Produs** (`/produs`): bancă de idei (vot 0–10), fișe de oportunitate cu investiție/venit/payback/ROI. Trecerea la oportunitate cere aprobare.
- **Growth** (`/growth`): evaluare investiții (verdict), scenarii de creștere din cifre reale, buget lunar pe categorii. Investițiile cer aprobare.
- **Risc** (`/risc`): verificări cu scadențe (ITP, asigurare, licențe) + alerte; registru nereguli; **pre-filtru contracte** (analiză euristică a clauzelor — nu înlocuiește avocatul).

**FR :**
- **Produit** (`/produs`) : banque d'idées (vote 0–10), fiches d'opportunité avec investissement/revenu/payback/ROI. Le passage en opportunité exige une approbation.
- **Croissance** (`/growth`) : évaluation d'investissements (verdict), scénarios de croissance à partir de chiffres réels, budget mensuel par catégorie. Les investissements exigent une approbation.
- **Risque** (`/risc`) : vérifications avec échéances (contrôle technique, assurance, licences) + alertes ; registre d'irrégularités ; **pré-filtre contrats** (analyse heuristique des clauses — ne remplace pas l'avocat).

---

## 8. Hermes — învățare continuă / apprentissage continu — `/hermes`

**RO:**
- Hermes învață din operare: întrebările fără răspuns, aprobările respinse și erorile devin **semnale**.
- Butonul **„Rulează analiza"** transformă semnalele în **sugestii**.
- Dumneavoastră **completați răspunsul corect, aprobați**, apoi **aplicați** — și Jarvis știe de data următoare.
- Secțiunea „Instrucțiunile agenților" ține versiunile instrucțiunilor fiecărui agent (trasabilitate completă).
- ⚠️ Nicio învățare nu se aplică singură — totul trece prin om.

**FR :**
- Hermès apprend de l'exploitation : questions sans réponse, approbations rejetées et erreurs deviennent des **signaux**.
- Le bouton **« Lancer l'analyse »** transforme les signaux en **suggestions**.
- Vous **complétez la bonne réponse, approuvez**, puis **appliquez** — et Jarvis saura la prochaine fois.
- La section « Instructions des agents » conserve les versions des instructions de chaque agent (traçabilité complète).
- ⚠️ Aucun apprentissage ne s'applique seul — tout passe par l'humain.

---

## 9. Aprobări / Approbations — `/aprobari`

**RO:**
- Tot ce e ireversibil sau costisitor așteaptă aici: oferte trimise, postări publicate, anulări curse, emitere/trimitere facturi, investiții, oportunități.
- Aprobați sau respingeți cu un click (sau din chat). Respingerea devine semnal de învățare pentru Hermes.
- Jurnalul de audit înregistrează fiecare decizie (cine, ce, când).

**FR :**
- Tout ce qui est irréversible ou coûteux attend ici : devis envoyés, publications, annulations de courses, émission/envoi de factures, investissements, opportunités.
- Approuvez ou rejetez en un clic (ou depuis le chat). Le rejet devient un signal d'apprentissage pour Hermès.
- Le journal d'audit enregistre chaque décision (qui, quoi, quand).

---

## 10. Cunoștințe, Catalog, Oferte / Connaissances, Catalogue, Devis

**RO:**
- **Cunoștințe** (`/cunostinte`): baza de întrebări–răspunsuri. Adăugați din pagină sau prin Hermes.
- **Catalog** (`/catalog`): servicii și prețuri — `produs nou: Transfer Aeroport, 90`.
- **Oferte** (`/oferte`): oferte cu linii, TVA și PDF generat automat la aprobare. Trimiterea cere aprobare.

**FR :**
- **Connaissances** (`/cunostinte`) : base de questions–réponses. Ajoutez depuis la page ou via Hermès.
- **Catalogue** (`/catalog`) : services et prix — `produs nou: Transfer Aeroport, 90`.
- **Devis** (`/oferte`) : devis avec lignes, TVA et PDF généré automatiquement à l'approbation. L'envoi exige une approbation.

---

## 11. Siguranță și limite / Sécurité et limites

**RO:**
- Datele rulează pe serverul companiei; jurnalele nu pot fi șterse (audit append-only).
- Jarvis nu trimite nimic extern (email, WhatsApp, postări, bani) fără aprobare umană.
- Documentele fiscale se validează cu contabilul; analiza contractelor nu înlocuiește avocatul.
- În modul demonstrativ, toate paginile poartă bannerul **„DATE DEMONSTRATIVE"** — cifrele sunt fictive.

**FR :**
- Les données tournent sur le serveur de la société ; les journaux ne peuvent pas être effacés (audit append-only).
- Jarvis n'envoie rien à l'externe (e-mail, WhatsApp, publications, argent) sans approbation humaine.
- Les documents fiscaux sont validés avec le comptable ; l'analyse des contrats ne remplace pas l'avocat.
- En mode démonstration, toutes les pages portent le bandeau **« DONNÉES DÉMONSTRATIVES »** — les chiffres sont fictifs.

---

## 12. Probleme frecvente / Problèmes fréquents

**RO:**
- *Nu răspunde la o întrebare* → reformulați; dacă tot nu știe, Hermes o va propune ca sugestie de învățare după analiză.
- *O acțiune pare blocată* → verificați pagina Aprobări — probabil așteaptă aprobarea.
- *Cifrele din BI par vechi* → rulați sincronizarea (`sincronizează pennylane`) sau reîncărcați pagina.

**FR :**
- *Ne répond pas à une question* → reformulez ; s'il ne sait toujours pas, Hermès la proposera comme suggestion après analyse.
- *Une action semble bloquée* → vérifiez la page Approbations — elle attend probablement une approbation.
- *Les chiffres du BI semblent anciens* → lancez la synchronisation (`sincronizează pennylane`) ou rechargez la page.

---

*Document generat pentru platforma Jarvis — modul demonstrativ. / Document généré pour la plateforme Jarvis — mode démonstration.*
