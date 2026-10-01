"""Internaționalizare RO/FR pentru interfața Jarvis (cerință Faza 2).

Utilizare: t('cheie', lang) — lang ∈ {'ro', 'fr'}. Șirurile cu {placeholder}
se formatează cu .format().
"""
LANGS = ("ro", "fr")
DEFAULT = "ro"

STRINGS = {
    # --- navigare ---
    "nav_chat": {"ro": "Chat intern", "fr": "Chat interne"},
    "nav_aprobari": {"ro": "Aprobări", "fr": "Approbations"},
    "nav_catalog": {"ro": "Catalog", "fr": "Catalogue"},
    "nav_oferte": {"ro": "Oferte", "fr": "Devis"},
    "nav_cunostinte": {"ro": "Cunoștințe", "fr": "Connaissances"},
    "nav_dispecerat": {"ro": "Dispecerat", "fr": "Dispatch"},
    "nav_marketing": {"ro": "Marketing", "fr": "Marketing"},
    "nav_competitori": {"ro": "Competitori", "fr": "Concurrents"},
    "lang_label": {"ro": "Limbă", "fr": "Langue"},

    # --- comun ---
    "c_adauga": {"ro": "Adaugă", "fr": "Ajouter"},
    "c_salveaza": {"ro": "Salvează", "fr": "Enregistrer"},
    "c_inactiv": {"ro": "inactiv", "fr": "inactif"},

    # --- chat ---
    "chat_placeholder": {"ro": "Scrie o comandă sau o întrebare…",
                         "fr": "Écrivez une commande ou une question…"},
    "chat_trimite": {"ro": "Trimite", "fr": "Envoyer"},

    # --- aprobări ---
    "ap_titlu": {"ro": "Cereri de aprobare în așteptare",
                 "fr": "Demandes d'approbation en attente"},
    "ap_nicio": {"ro": "Nicio cerere în așteptare. 🎉",
                 "fr": "Aucune demande en attente. 🎉"},
    "ap_matrice": {"ro": "Matricea de aprobare", "fr": "Matrice d'approbation"},
    "ap_aproba": {"ro": "Aprobă", "fr": "Approuver"},
    "ap_respinge": {"ro": "Respinge", "fr": "Rejeter"},
    "ap_singur": {"ro": "agentul decide singur", "fr": "l'agent décide seul"},
    "ap_necesita": {"ro": "necesită aprobare", "fr": "approbation requise"},
    "ap_interzis": {"ro": "interzis", "fr": "interdit"},

    # --- catalog ---
    "cat_titlu": {"ro": "Catalog produse / servicii", "fr": "Catalogue produits / services"},
    "cat_adauga_titlu": {"ro": "Adaugă produs", "fr": "Ajouter un produit"},
    "cat_nume_ph": {"ro": "Nume produs/serviciu", "fr": "Nom du produit/service"},
    "cat_pret_ph": {"ro": "Preț EUR", "fr": "Prix EUR"},
    "cat_sku_ph": {"ro": "SKU (opțional)", "fr": "SKU (optionnel)"},
    "cat_hint": {"ro": "Sau din chat: «produs nou: Nume, preț»",
                 "fr": "Ou via chat : «nouveau produit : Nom, prix»"},
    "cat_gol": {"ro": "Catalogul e gol.", "fr": "Le catalogue est vide."},

    # --- oferte ---
    "of_titlu": {"ro": "Oferte", "fr": "Devis"},
    "of_hint": {"ro": "Creezi oferte din chat: «oferta pentru Client: produs x 2, altul x 1». "
                      "Prețurile se iau automat din catalog. La aprobare se generează PDF-ul.",
                "fr": "Créez des devis via chat : «devis pour Client : produit x 2, autre x 1». "
                      "Les prix viennent du catalogue. Le PDF est généré à l'approbation."},
    "of_descarca": {"ro": "Descarcă PDF", "fr": "Télécharger le PDF"},
    "of_fara_pdf": {"ro": "PDF-ul se generează la aprobare.",
                    "fr": "Le PDF est généré à l'approbation."},
    "of_nicio": {"ro": "Nicio ofertă încă.", "fr": "Aucun devis pour l'instant."},

    # --- cunoștințe ---
    "cu_titlu": {"ro": "Baza de cunoștințe Q&A", "fr": "Base de connaissances Q&R"},
    "cu_hint": {"ro": "Răspunsurile de aici sunt date automat clienților (chat intern, WhatsApp, Messenger).",
                "fr": "Les réponses ici sont envoyées automatiquement aux clients (chat interne, WhatsApp, Messenger)."},
    "cu_adauga_titlu": {"ro": "Adaugă pereche întrebare–răspuns",
                        "fr": "Ajouter une paire question–réponse"},
    "cu_intrebare_ph": {"ro": "Întrebarea clientului", "fr": "Question du client"},
    "cu_raspuns_ph": {"ro": "Răspunsul", "fr": "La réponse"},
    "cu_nicio": {"ro": "Nicio întrebare salvată încă.",
                 "fr": "Aucune question enregistrée pour l'instant."},
    "cu_chat_hint": {"ro": "Sau din chat: «adaugă q&a: întrebarea | răspunsul»",
                     "fr": "Ou via chat : «ajouter q&r : la question | la réponse»"},

    # --- dispecerat ---
    "di_titlu": {"ro": "Dispecerat — cursele de azi", "fr": "Dispatch — courses du jour"},
    "di_curse": {"ro": "Curse", "fr": "Courses"},
    "di_soferi": {"ro": "Șoferi", "fr": "Chauffeurs"},
    "di_masini": {"ro": "Mașini", "fr": "Voitures"},
    "di_notificari": {"ro": "Notificări în așteptare", "fr": "Notifications en attente"},
    "di_nicio_cursa": {"ro": "Nicio cursă programată azi.",
                       "fr": "Aucune course programmée aujourd'hui."},
    "di_niciun_sofer": {"ro": "Niciun șofer introdus.", "fr": "Aucun chauffeur enregistré."},
    "di_nicio_masina": {"ro": "Nicio mașină introdusă.", "fr": "Aucune voiture enregistrée."},
    "di_nicio_notif": {"ro": "Nicio notificare în așteptare.",
                       "fr": "Aucune notification en attente."},
    "di_adauga_cursa": {"ro": "Cursă nouă", "fr": "Nouvelle course"},
    "di_client_ph": {"ro": "Nume client", "fr": "Nom du client"},
    "di_tel_ph": {"ro": "Telefon", "fr": "Téléphone"},
    "di_preluare_ph": {"ro": "Adresă preluare", "fr": "Adresse de prise en charge"},
    "di_destinatie_ph": {"ro": "Destinație", "fr": "Destination"},
    "di_cand_ph": {"ro": "Când (ex: azi 14:30 sau 2026-10-02 09:00)",
                   "fr": "Quand (ex : aujourd'hui 14:30 ou 2026-10-02 09:00)"},
    "di_nume_ph": {"ro": "Nume șofer", "fr": "Nom du chauffeur"},
    "di_marca_ph": {"ro": "Marcă și model", "fr": "Marque et modèle"},
    "di_numar_ph": {"ro": "Nr. înmatriculare", "fr": "Immatriculation"},
    "di_atribuie_auto": {"ro": "Atribuie automat", "fr": "Assigner automatiquement"},
    "di_status": {"ro": "Status", "fr": "Statut"},
    "st_rezervata": {"ro": "rezervată", "fr": "réservée"},
    "st_confirmata": {"ro": "confirmată", "fr": "confirmée"},
    "st_in_curs": {"ro": "în curs", "fr": "en cours"},
    "st_finalizata": {"ro": "finalizată", "fr": "terminée"},
    "st_anulata": {"ro": "anulată", "fr": "annulée"},
    "st_liber": {"ro": "liber", "fr": "libre"},
    "st_ocupat": {"ro": "ocupat", "fr": "occupé"},

    # --- marketing ---
    "ma_titlu": {"ro": "Marketing & Media", "fr": "Marketing & Médias"},
    "ma_adauga_titlu": {"ro": "Postare nouă", "fr": "Nouvelle publication"},
    "ma_text_ph": {"ro": "Textul postării…", "fr": "Texte de la publication…"},
    "ma_data_ph": {"ro": "Data programată (opțional, ex: 2026-10-05 10:00)",
                   "fr": "Date programmée (optionnel, ex : 2026-10-05 10:00)"},
    "ma_hint": {"ro": "Publicarea efectivă necesită aprobare și conturile conectate.",
                "fr": "La publication effective nécessite une approbation et les comptes connectés."},
    "ma_plan_btn": {"ro": "Generează plan editorial (7 zile)",
                    "fr": "Générer un plan éditorial (7 jours)"},

    # --- competitori ---
    "co_titlu": {"ro": "Competitori monitorizați", "fr": "Concurrents suivis"},
    "co_adauga_titlu": {"ro": "Competitor nou", "fr": "Nouveau concurrent"},
    "co_nume_ph": {"ro": "Nume firmă", "fr": "Nom de l'entreprise"},
    "co_web_ph": {"ro": "Website", "fr": "Site web"},
    "co_niciun": {"ro": "Niciun competitor introdus.",
                  "fr": "Aucun concurrent enregistré."},
    "co_obs_ph": {"ro": "Adaugă o observație…", "fr": "Ajouter une observation…"},

    # --- mesaje bot: ajutor ---
    "bot_ajutor": {
        "ro": ("Sunt Jarvis (Faza 2). Comenzi:\n"
               "• «lead nou: Nume Prenume, telefon, email, firmă» — creez lead în CRM\n"
               "• «activitate: text» — creez o activitate în CRM\n"
               "• «califică leadul 12» · «scor leaduri» · «pipeline»\n"
               "• «produs nou: Nume, preț» · «catalog»\n"
               "• «oferta pentru Client: produs x 2, altul x 1»\n"
               "• «caz nou: subiect, descriere»\n"
               "• «adaugă q&a: întrebarea | răspunsul»\n"
               "— Dispecerat —\n"
               "• «cursă nouă: Nume, telefon, preluare, destinație, când»\n"
               "• «curse azi» · «atribuie cursa 3» · «cursa 3: confirmată»\n"
               "• «șofer nou: Nume, telefon» · «mașină nouă: Marcă Model, număr»\n"
               "— Marketing —\n"
               "• «postare nouă: canal, text» · «plan editorial»\n"
               "• «competitor nou: Nume» · «observație competitor 1: text»"),
        "fr": ("Je suis Jarvis (Phase 2). Commandes :\n"
               "• «nouveau lead : Nom Prénom, téléphone, email, entreprise»\n"
               "• «activité : texte» · «qualifier lead 12» · «score leads» · «pipeline»\n"
               "• «nouveau produit : Nom, prix» · «catalogue»\n"
               "• «devis pour Client : produit x 2, autre x 1»\n"
               "• «nouveau ticket : sujet, description»\n"
               "• «ajouter q&r : la question | la réponse»\n"
               "— Dispatch —\n"
               "• «nouvelle course : Nom, téléphone, départ, destination, quand»\n"
               "• «courses aujourd'hui» · «assigner course 3» · «course 3 : confirmée»\n"
               "• «nouveau chauffeur : Nom, téléphone» · «nouvelle voiture : Marque Modèle, immat.»\n"
               "— Marketing —\n"
               "• «nouvelle publication : canal, texte» · «plan éditorial»\n"
               "• «nouveau concurrent : Nom» · «observation concurrent 1 : texte»")},

    # --- mesaje bot: vânzări (Faza 1, bilingve) ---
    "bot_lead_creat": {"ro": "Lead creat în CRM: {nume} (id {id}).",
                       "fr": "Lead créé dans le CRM : {nume} (id {id})."},
    "bot_activitate_creata": {"ro": "Activitate creată în CRM (id {id}): {subiect}.",
                              "fr": "Activité créée dans le CRM (id {id}) : {subiect}."},
    "bot_produs_adaugat": {"ro": "Am adăugat în catalog: {nume} — {pret:.2f} EUR.",
                           "fr": "Ajouté au catalogue : {nume} — {pret:.2f} EUR."},
    "bot_catalog_gol": {"ro": "Catalogul e gol. Adaugă produse cu «produs nou: Nume, preț».",
                        "fr": "Le catalogue est vide. Ajoutez avec «nouveau produit : Nom, prix»."},
    "bot_catalog_lista": {"ro": "Catalog:\n{linii}", "fr": "Catalogue :\n{linii}"},
    "bot_oferta_gata": {"ro": ("Am pregătit oferta {numar} ({total:.2f} EUR) și am cerut aprobare "
                               "(cererea #{ap}). O poți aproba din pagina Aprobări — "
                               "la aprobare generez PDF-ul."),
                        "fr": ("J'ai préparé le devis {numar} ({total:.2f} EUR) et demandé "
                               "une approbation (demande n°{ap}). Approuvez depuis la page "
                               "Approbations — le PDF sera généré.")},
    "bot_lead_calificat": {"ro": "Leadul #{id} a trecut în status «{status}» în CRM.",
                           "fr": "Le lead n°{id} est passé au statut «{status}» dans le CRM."},
    "bot_scor_gol": {"ro": "Nu există leaduri în CRM.", "fr": "Aucun lead dans le CRM."},
    "bot_scor_top": {"ro": "Top leaduri după scor:\n{linii}",
                     "fr": "Top des leads par score :\n{linii}"},
    "bot_caz_creat": {"ro": "Am deschis tichetul #{id} în CRM: {subiect}. Un coleg preia cazul.",
                      "fr": "Ticket n°{id} ouvert dans le CRM : {subiect}. Un collègue prend le relais."},
    "bot_qa_invatat": {"ro": "Am învățat răspunsul #{id}. De acum răspund automat la întrebări similare.",
                       "fr": "Réponse n°{id} apprise. Je répondrai automatiquement aux questions similaires."},
    "bot_pipeline_titlu": {"ro": "Pipeline vânzări (10 pași):",
                           "fr": "Pipeline des ventes (10 étapes) :"},

    # --- mesaje bot: dispecerat ---
    "bot_cursa_creata": {"ro": "Cursa #{id} creată pentru {nume}: {preluare} → {destinatie}, {cand}.",
                         "fr": "Course n°{id} créée pour {nume} : {preluare} → {destinatie}, {cand}."},
    "bot_cursa_nu_exista": {"ro": "Cursa #{id} nu există.", "fr": "La course n°{id} n'existe pas."},
    "bot_atribuita": {"ro": "Cursa #{id} atribuită: {sofer} cu {masina}. Clientul și șoferul vor fi notificați.",
                      "fr": "Course n°{id} assignée : {sofer} avec {masina}. Le client et le chauffeur seront notifiés."},
    "bot_atribuire_imposibila": {"ro": "Nu am găsit șofer și mașină libere pentru cursa #{id}.",
                                 "fr": "Aucun chauffeur ni voiture libre pour la course n°{id}."},
    "bot_status_schimbat": {"ro": "Cursa #{id} a trecut în status «{status}».",
                            "fr": "La course n°{id} est passée au statut «{status}»."},
    "bot_status_invalid": {"ro": "Status invalid. Folosește: rezervată, confirmată, în curs, finalizată, anulată.",
                           "fr": "Statut invalide. Utilisez : réservée, confirmée, en cours, terminée, annulée."},
    "bot_sofer_adaugat": {"ro": "Am adăugat șoferul: {nume} ({telefon}).",
                          "fr": "Chauffeur ajouté : {nume} ({telefon})."},
    "bot_masina_adaugata": {"ro": "Am adăugat mașina: {marca} ({numar}).",
                            "fr": "Voiture ajoutée : {marca} ({numar})."},
    "bot_curse_azi_gol": {"ro": "Nicio cursă programată azi.",
                          "fr": "Aucune course programmée aujourd'hui."},
    "bot_curse_azi_titlu": {"ro": "Cursele de azi:", "fr": "Courses du jour :"},
    "bot_dispecerat_rezumat": {"ro": "Dispecerat — azi: {curse} curse, {liberi} șoferi liberi, {masini} mașini libere.",
                               "fr": "Dispatch — aujourd'hui : {curse} courses, {liberi} chauffeurs libres, {masini} voitures libres."},
    "bot_anulare_ceruta": {"ro": "Am cerut aprobare pentru anularea cursei #{id} (cererea #{ap}).",
                           "fr": "Approbation demandée pour annuler la course n°{id} (demande n°{ap})."},
    "bot_tranzitie_invalida": {"ro": "Tranziție de status invalidă pentru cursa #{id}.",
                               "fr": "Transition de statut invalide pour la course n°{id}."},

    # --- mesaje bot: marketing & competitori ---
    "bot_postare_creata": {"ro": "Am salvat postarea #{id} pentru {canal} ca ciornă.",
                           "fr": "Publication n°{id} enregistrée pour {canal} comme brouillon."},
    "bot_postare_aprobare": {"ro": ("Am creat postarea #{id} și am cerut aprobare (cererea #{ap}). "
                                    "Publicarea efectivă necesită conturile conectate."),
                             "fr": ("Publication n°{id} créée, approbation demandée (n°{ap}). "
                                     "La publication effective nécessite les comptes connectés.")},
    "bot_plan_editorial": {"ro": "Plan editorial (7 zile):\n{linii}",
                           "fr": "Plan éditorial (7 jours) :\n{linii}"},
    "bot_competitor_adaugat": {"ro": "Am adăugat competitorul: {nume}.",
                               "fr": "Concurrent ajouté : {nume}."},
    "bot_observatie_salvat": {"ro": "Observație salvată pentru {nume}.",
                              "fr": "Observation enregistrée pour {nume}."},
    "bot_competitor_nu_exista": {"ro": "Competitorul #{id} nu există.",
                                 "fr": "Le concurrent n°{id} n'existe pas."},

    # --- canal extern ---
    "bot_canal_necunoscut": {"ro": ("Mulțumim pentru mesaj! Un coleg îți răspunde în scurt timp. "
                                    "Pentru urgențe, ne poți suna direct."),
                             "fr": ("Merci pour votre message ! Un collègue vous répondra bientôt. "
                                     "Pour les urgences, appelez-nous directement.")},
    "bot_canal_lead": {"ro": " Te sunăm în scurt timp pentru detalii.",
                       "fr": " Nous vous appellerons bientôt pour les détails."},
    "bot_canal_confirmare": {"ro": "Vă confirmăm rezervarea în scurt timp.",
                             "fr": "Nous confirmerons votre réservation sous peu."},
    "bot_necesita_text": {"ro": "Spune-mi cu ce te ajut.",
                          "fr": "Dites-moi comment je peux vous aider."},
    "bot_postare_nu_exista": {"ro": "Postarea #{id} nu există.",
                              "fr": "La publication n°{id} n'existe pas."},
    "chat_bunvenit": {"ro": "Salut! Sunt Jarvis. Scrie «ajutor» ca să vezi ce știu să fac.",
                      "fr": "Salut ! Je suis Jarvis. Écrivez « aide » pour voir ce que je sais faire."},
    "chat_agenti": {"ro": "Agenții mei", "fr": "Mes agents"},
    "nav_finante": {"ro": "Finanțe", "fr": "Finances"},
    "nav_bi": {"ro": "BI", "fr": "BI"},

    # --- finanțe (Faza 3) ---
    "fin_titlu": {"ro": "Finanțe — facturi clienți",
                "fr": "Finances — factures clients"},
    "fin_hint": {"ro": ("Ciornele se creează automat la finalizarea curselor. "
                      "Emiterea (finalizarea în Pennylane) e ireversibilă și cere aprobare. "
                      "Din chat: «factură cursa 5: 120», «emite factura 1», «facturi restante»."),
               "fr": ("Les brouillons sont créés automatiquement à la fin des courses. "
                      "L'émission (finalisation dans Pennylane) est irréversible et requiert "
                      "une approbation. Via chat : « facture course 5 : 120 », "
                      "« émettre facture 1 », « factures en retard ».")},
    "fin_demo": {"ro": "Mod DEMO Pennylane (fără token API — nicio rețea).",
               "fr": "Mode DÉMO Pennylane (sans token API — aucun réseau)."},
    "fin_live": {"ro": "Conectat la Pennylane (API).",
               "fr": "Connecté à Pennylane (API)."},
    "fin_col_numar": {"ro": "Număr", "fr": "Numéro"},
    "fin_col_client": {"ro": "Client", "fr": "Client"},
    "fin_col_total": {"ro": "Total", "fr": "Total"},
    "fin_col_status": {"ro": "Status", "fr": "Statut"},
    "fin_col_scadenta": {"ro": "Scadență", "fr": "Échéance"},
    "fin_col_actiuni": {"ro": "Acțiuni", "fr": "Actions"},
    "fin_emite": {"ro": "Emite", "fr": "Émettre"},
    "fin_trimite": {"ro": "Trimite", "fr": "Envoyer"},
    "fin_platita": {"ro": "Marchează plătită", "fr": "Marquer payée"},
    "fin_sincronizeaza": {"ro": "Sincronizează Pennylane", "fr": "Synchroniser Pennylane"},
    "fin_anomalii_titlu": {"ro": "Anomalii detectate", "fr": "Anomalies détectées"},
    "fin_anomalii_zero": {"ro": "Nicio anomalie. 🎉", "fr": "Aucune anomalie. 🎉"},
    "fin_restante_titlu": {"ro": "Facturi restante", "fr": "Factures en retard"},
    "st_ciorna": {"ro": "ciornă", "fr": "brouillon"},
    "st_emisa": {"ro": "emisă", "fr": "émise"},
    "st_partial": {"ro": "parțial plătită", "fr": "partiellement payée"},
    "st_platita": {"ro": "plătită", "fr": "payée"},
    "st_anulata_fact": {"ro": "anulată", "fr": "annulée"},

    # --- BI (Faza 3) ---
    "bi_titlu": {"ro": "Business Intelligence — starea companiei",
               "fr": "Business Intelligence — état de l'entreprise"},
    "bi_incasari_azi": {"ro": "Încasări azi", "fr": "Encaissements aujourd'hui"},
    "bi_facturat_luna": {"ro": "Facturat luna aceasta", "fr": "Facturé ce mois-ci"},
    "bi_facturi_luna": {"ro": "Facturi emise (lună)", "fr": "Factures émises (mois)"},
    "bi_restante": {"ro": "Restanțe", "fr": "En retard"},
    "bi_curse_azi": {"ro": "Curse finalizate azi", "fr": "Courses terminées aujourd'hui"},
    "bi_tva": {"ro": "TVA colectat (lună)", "fr": "TVA collectée (mois)"},
    "bi_anomalii": {"ro": "Anomalii", "fr": "Anomalies"},
    "bi_top": {"ro": "Top clienți (lună)", "fr": "Top clients (mois)"},

    # --- mesaje bot finanțe/BI ---
    "bot_factura_creata": {"ro": "Ciornă factură {numar}: {client} — {total:.2f} EUR. "
                                "Emiterea cere aprobare.",
                          "fr": "Brouillon de facture {numar} : {client} — {total:.2f} EUR. "
                                "L'émission requiert une approbation."},
    "bot_factura_suma_invalida": {"ro": "Nu pot factura suma 0. Specifică suma: «factură cursa 5: 120».",
                                "fr": "Impossible de facturer 0. Précisez le montant : « facture course 5 : 120 »."},
    "bot_factura_nu_exista": {"ro": "Factura #{id} nu există sau nu e în starea potrivită.",
                             "fr": "La facture n°{id} n'existe pas ou n'est pas dans le bon état."},
    "bot_emitere_ceruta": {"ro": ("Am cerut aprobarea pentru emiterea facturii {numar} "
                                 "(cererea #{ap}). Finalizarea în Pennylane e ireversibilă."),
                          "fr": ("Approbation demandée pour l'émission de la facture {numar} "
                                 "(demande n°{ap}). La finalisation dans Pennylane est irréversible.")},
    "bot_trimitere_ceruta": {"ro": "Am cerut aprobarea pentru trimiterea facturii {numar} (cererea #{ap}).",
                            "fr": "Approbation demandée pour l'envoi de la facture {numar} (demande n°{ap})."},
    "bot_incasare_ok": {"ro": "Încasare înregistrată. Status factură: {status}.",
                       "fr": "Encaissement enregistré. Statut de la facture : {status}."},
    "bot_restante_zero": {"ro": "Nicio factură restantă. 🎉",
                         "fr": "Aucune facture en retard. 🎉"},
    "bot_restante_lista": {"ro": "{n} facturi restante ({total:.2f} EUR):\n{linii}",
                          "fr": "{n} factures en retard ({total:.2f} EUR) :\n{linii}"},
    "bot_sync_ok": {"ro": "Sincronizare Pennylane: {actualizate} actualizate, {erori} erori.",
                   "fr": "Synchronisation Pennylane : {actualizate} mises à jour, {erori} erreurs."},
    "bot_anomalii_zero": {"ro": "Nicio anomalie financiară detectată.",
                         "fr": "Aucune anomalie financière détectée."},
    "bot_anomalii_lista": {"ro": "{n} anomalii:\n{linii}",
                          "fr": "{n} anomalies :\n{linii}"},
    "bot_rezumat_financiar": {"ro": ("💰 Financiar:\n• Încasări azi: {incasari_azi:.2f} EUR\n"
                                     "• Facturat luna aceasta: {facturat_luna:.2f} EUR ({facturi_txt})\n"
                                     "• Restanțe: {restante_nr} ({restante_total:.2f} EUR)\n"
                                     "• Curse finalizate azi: {curse_azi}\n• TVA (lună): {tva:.2f} EUR\n"
                                     "• Anomalii: {anomalii}"),
                             "fr": ("💰 Finances :\n• Encaissements aujourd'hui : {incasari_azi:.2f} EUR\n"
                                     "• Facturé ce mois-ci : {facturat_luna:.2f} EUR ({facturi_txt})\n"
                                     "• En retard : {restante_nr} ({restante_total:.2f} EUR)\n"
                                     "• Courses terminées aujourd'hui : {curse_azi}\n• TVA (mois) : {tva:.2f} EUR\n"
                                     "• Anomalies : {anomalii}")},
    "bot_dashboard": {"ro": ("📊 Starea companiei:\n• Încasări azi: {incasari_azi:.2f} EUR\n"
                              "• Facturat luna aceasta: {facturat_luna:.2f} EUR ({facturi_txt})\n"
                              "• Restanțe: {restante_nr} ({restante_total:.2f} EUR)\n"
                              "• Curse finalizate azi: {curse_azi}\n• TVA (lună): {tva:.2f} EUR\n"
                              "• Anomalii: {anomalii}\nTop clienți:\n{top}"),
                      "fr": ("📊 État de l'entreprise :\n• Encaissements aujourd'hui : {incasari_azi:.2f} EUR\n"
                              "• Facturé ce mois-ci : {facturat_luna:.2f} EUR ({facturi_txt})\n"
                              "• En retard : {restante_nr} ({restante_total:.2f} EUR)\n"
                              "• Courses terminées aujourd'hui : {curse_azi}\n• TVA (mois) : {tva:.2f} EUR\n"
                              "• Anomalies : {anomalii}\nTop clients :\n{top}")},
    "bot_snapshot_ok": {"ro": "Snapshot KPI salvat.",
                       "fr": "Instantané KPI enregistré."},
    "bot_pennylane_demo": {"ro": "Pennylane e în mod demo (fără token). Ciornele sunt locale + simulate.",
                          "fr": "Pennylane est en mode démo (sans token). Brouillons locaux + simulés."},

    # --- navigare Faza 4 ---
    "nav_produs": {"ro": "Produs", "fr": "Produit"},
    "nav_growth": {"ro": "Growth", "fr": "Croissance"},
    "nav_risc": {"ro": "Risc", "fr": "Risques"},

    # --- pagini Faza 4 ---
    "pg_produs_idei": {"ro": "Bancă de idei", "fr": "Banque d'idées"},
    "pg_produs_oport": {"ro": "Oportunități", "fr": "Opportunités"},
    "pg_growth_inv": {"ro": "Investiții", "fr": "Investissements"},
    "pg_growth_buget": {"ro": "Buget lunar", "fr": "Budget mensuel"},
    "pg_growth_scenariu": {"ro": "Scenarii de creștere", "fr": "Scénarios de croissance"},
    "pg_risc_verif": {"ro": "Verificări conformitate", "fr": "Vérifications de conformité"},
    "pg_risc_nereguli": {"ro": "Nereguli semnalate", "fr": "Incidents signalés"},
    "pg_risc_contracte": {"ro": "Analize contracte (pre-filtru)", "fr": "Analyses de contrats (pré-filtre)"},

    # --- bot: produs ---
    "bot_idee_noua": {"ro": "💡 Ideea #{id} înregistrată: {titlu}",
                      "fr": "💡 Idée #{id} enregistrée : {titlu}"},
    "bot_idei_zero": {"ro": "Nicio idee în bancă încă. Adaugă una cu «idee nouă: …».",
                      "fr": "Aucune idée pour l'instant. Ajoutez-en une avec « nouvelle idée : … »."},
    "bot_idei_lista": {"ro": "💡 Idei ({n}):\n{linii}",
                       "fr": "💡 Idées ({n}) :\n{linii}"},
    "bot_idee_inexistenta": {"ro": "Ideea #{id} nu există.",
                             "fr": "L'idée #{id} n'existe pas."},
    "bot_idee_vot": {"ro": "Ideea «{titlu}» are acum scorul {scor}/10.",
                     "fr": "L'idée « {titlu} » a maintenant la note {scor}/10."},
    "bot_oportunitati_zero": {"ro": "Nicio oportunitate încă.",
                              "fr": "Aucune opportunité pour l'instant."},
    "bot_oportunitati_lista": {"ro": "📋 Oportunități ({n}):\n{linii}",
                               "fr": "📋 Opportunités ({n}) :\n{linii}"},
    "bot_oportunitate_fisa": {"ro": ("📋 {titlu}\n• Investiție estimată: {investitie:.0f} EUR\n"
                                     "• Venit lunar estimat: {venit:.0f} EUR\n• Payback: {payback}\n"
                                     "• ROI anual: {roi}\n• Status: {status}"),
                              "fr": ("📋 {titlu}\n• Investissement estimé : {investitie:.0f} EUR\n"
                                     "• Revenu mensuel estimé : {venit:.0f} EUR\n• Retour : {payback}\n"
                                     "• ROI annuel : {roi}\n• Statut : {status}")},
    "bot_oportunitate_inexistenta": {"ro": "Oportunitatea #{id} nu există sau nu mai e în evaluare.",
                                     "fr": "L'opportunité #{id} n'existe pas ou n'est plus en évaluation."},
    "bot_oportunitate_ceruta": {"ro": "Cerere de aprobare trimisă pentru oportunitatea «{titlu}» (cererea #{ap}).",
                                "fr": "Demande d'approbation envoyée pour l'opportunité « {titlu} » (demande #{ap})."},

    # --- bot: growth ---
    "bot_investitie_analiza": {"ro": ("💰 {titlu}\n• Cost: {cost:.0f} EUR\n• Venit lunar estimat: {venit:.0f} EUR\n"
                                      "• Payback: {payback}\n• ROI anual: {roi}\n• Verdict: {verdict}\n"
                                      "(evaluare #{id} — cere aprobarea cu «aprobă investiția {id}»)"),
                               "fr": ("💰 {titlu}\n• Coût : {cost:.0f} EUR\n• Revenu mensuel estimé : {venit:.0f} EUR\n"
                                      "• Retour : {payback}\n• ROI annuel : {roi}\n• Verdict : {verdict}\n"
                                      "(évaluation #{id} — demandez l'approbation avec « approuver l'investissement {id} »)")},
    "bot_investitii_zero": {"ro": "Nicio investiție evaluată încă.",
                            "fr": "Aucun investissement évalué pour l'instant."},
    "bot_investitii_lista": {"ro": "💰 Investiții ({n}):\n{linii}",
                             "fr": "💰 Investissements ({n}) :\n{linii}"},
    "bot_investitie_inexistenta": {"ro": "Investiția #{id} nu există sau nu mai e în evaluare.",
                                   "fr": "L'investissement #{id} n'existe pas ou n'est plus en évaluation."},
    "bot_investitie_ceruta": {"ro": "Cerere de aprobare trimisă pentru investiția «{titlu}» (cererea #{ap}).",
                              "fr": "Demande d'approbation envoyée pour l'investissement « {titlu} » (demande #{ap})."},
    "bot_scenariu": {"ro": ("📈 Scenariu +{pct:g}% curse:\n• Facturat luna aceasta: {actual:.2f} EUR\n"
                            "• Proiectat: {proiectat:.2f} EUR\n• Venit suplimentar/lună: {suplimentar:.2f} EUR "
                            "({anual:.2f} EUR/an)"),
                     "fr": ("📈 Scénario +{pct:g} % de courses :\n• Facturé ce mois-ci : {actual:.2f} EUR\n"
                            "• Projeté : {proiectat:.2f} EUR\n• Revenu supplémentaire/mois : {suplimentar:.2f} EUR "
                            "({anual:.2f} EUR/an)")},
    "bot_buget_setat": {"ro": "Buget {luna} — {categorie}: {suma:.0f} EUR.",
                        "fr": "Budget {luna} — {categorie} : {suma:.0f} EUR."},
    "bot_buget": {"ro": ("💶 Buget {luna}:\n{linii}\n• Total planificat: {total:.0f} EUR\n"
                         "• Venituri facturate: {venituri:.2f} EUR\n• Acoperire: {acoperire}"),
                  "fr": ("💶 Budget {luna} :\n{linii}\n• Total planifié : {total:.0f} EUR\n"
                         "• Revenus facturés : {venituri:.2f} EUR\n• Couverture : {acoperire}")},

    # --- bot: risc ---
    "bot_contract_analizat": {"ro": ("📄 {nume} — scor de risc {risc}/10\n✅ Clauze găsite: {gasite}\n"
                                     "⚠️ Clauze lipsă: {lipsa}\n\n{disclaimer}"),
                              "fr": ("📄 {nume} — score de risque {risc}/10\n✅ Clauses trouvées : {gasite}\n"
                                     "⚠️ Clauses manquantes : {lipsa}\n\n{disclaimer}")},
    "bot_data_invalida": {"ro": "Data e invalidă. Folosește formatul AAAA-LL-ZZ (ex: 2027-01-15).",
                          "fr": "Date invalide. Utilisez le format AAAA-MM-JJ (ex : 2027-01-15)."},
    "bot_verificare_noua": {"ro": "✅ Verificarea #{id} înregistrată: {tip} — {referinta}, expiră la {data}.",
                            "fr": "✅ Vérification #{id} enregistrée : {tip} — {referinta}, expire le {data}."},
    "bot_verificari_zero": {"ro": "Nicio verificare de conformitate înregistrată.",
                            "fr": "Aucune vérification de conformité enregistrée."},
    "bot_verificari_lista": {"ro": "🛡️ Verificări ({n}):\n{linii}",
                             "fr": "🛡️ Vérifications ({n}) :\n{linii}"},
    "bot_neregula_noua": {"ro": "🚨 Neregula #{id} semnalată: {titlu} (severitate {severitate}).",
                          "fr": "🚨 Incident #{id} signalé : {titlu} (gravité {severitate})."},
    "bot_nereguli_zero": {"ro": "Nicio neregulă semnalată. 🎉",
                          "fr": "Aucun incident signalé. 🎉"},
    "bot_nereguli_lista": {"ro": "🚨 Nereguli ({n}):\n{linii}",
                           "fr": "🚨 Incidents ({n}) :\n{linii}"},
    "bot_neregula_inexistenta": {"ro": "Neregula #{id} nu există.",
                                 "fr": "L'incident #{id} n'existe pas."},
    "bot_neregula_rezolvata": {"ro": "Neregula #{id} «{titlu}» a fost marcată ca rezolvată.",
                               "fr": "L'incident #{id} « {titlu} » a été marqué comme résolu."},
    # --- mod demonstrativ ---
    "nav_demo": {"ro": "Demo", "fr": "Démo"},
    "demo_titlu": {"ro": "Bord demonstrativ", "fr": "Tableau de démonstration"},
    "demo_sub": {"ro": "Previzualizare marketing · analitică · statistică",
                 "fr": "Aperçu marketing · analytique · statistiques"},
    "demo_banner": {"ro": "DATE DEMONSTRATIVE — 100% fictive, generate pentru prezentare",
                    "fr": "DONNÉES DE DÉMONSTRATION — 100 % fictives, générées pour la présentation"},
    "demo_incarca": {"ro": "Încarcă datele demo", "fr": "Charger les données démo"},
    "demo_sterge": {"ro": "Șterge datele demo", "fr": "Supprimer les données démo"},
    "demo_gol": {"ro": "Nu există încă date demonstrative. Încarcă setul demo pentru a previzualiza bordul.",
                 "fr": "Aucune donnée de démonstration. Chargez le jeu démo pour prévisualiser le tableau."},
    "demo_kpi_venit": {"ro": "Facturat luna aceasta", "fr": "Facturé ce mois-ci"},
    "demo_kpi_curse": {"ro": "Curse înregistrate", "fr": "Courses enregistrées"},
    "demo_kpi_leaduri": {"ro": "Leaduri din campanii", "fr": "Leads des campagnes"},
    "demo_kpi_roas": {"ro": "ROAS mediu campanii", "fr": "ROAS moyen des campagnes"},
    "demo_kpi_restante": {"ro": "Facturi restante", "fr": "Factures impayées"},
    "demo_marketing": {"ro": "Marketing — campanii", "fr": "Marketing — campagnes"},
    "demo_analitica": {"ro": "Analitică — venituri, ultimele 7 zile",
                       "fr": "Analytique — revenus, 7 derniers jours"},
    "demo_operatiuni": {"ro": "Operațiuni — cursele de azi",
                        "fr": "Opérations — courses du jour"},
    "demo_soferi": {"ro": "Șoferi", "fr": "Chauffeurs"},
    "demo_top": {"ro": "Top clienți (luna)", "fr": "Top clients (mois)"},
    "demo_confirm_sterge": {"ro": "Sigur ștergi toate datele demonstrative? Datele reale nu sunt afectate.",
                            "fr": "Supprimer toutes les données de démonstration ? Les données réelles ne sont pas affectées."},
    "demo_nota": {"ro": "Datele din acest bord sunt fictive și servesc doar pentru prezentare. Le poți șterge oricând fără a afecta datele reale.",
                  "fr": "Les données de ce tableau sont fictives et servent uniquement à la présentation. Vous pouvez les supprimer à tout moment sans affecter les données réelles."},
    "demo_bot_deja": {"ro": "📊 Datele demonstrative sunt deja încărcate. Vezi pagina /demo.",
                        "fr": "📊 Les données de démonstration sont déjà chargées. Voir la page /demo."},
    "demo_bot_ok": {"ro": "📊 Date demonstrative încărcate: {rez}. Vezi pagina /demo.",
                    "fr": "📊 Données de démonstration chargées : {rez}. Voir la page /demo."},
    "demo_bot_sters": {"ro": "🧹 Date demonstrative șterse: {n} rânduri. Datele reale nu au fost afectate.",
                       "fr": "🧹 Données de démonstration supprimées : {n} lignes. Les données réelles n'ont pas été affectées."},


    # --- Hermes: antrenare & învățare continuă ---
    "nav_hermes": {"ro": "Hermes", "fr": "Hermès"},
    "hermes_titlu": {"ro": "Hermes — antrenare & învățare continuă",
                     "fr": "Hermès — entraînement & apprentissage continu"},
    "hermes_sub": {"ro": "Din operare în îmbunătățire: semnale → analiză → omul decide → aplicare",
                   "fr": "De l'opération à l'amélioration : signaux → analyse → l'humain décide → application"},
    "hermes_bucla": {"ro": "1️⃣ Semnale: întrebări fără răspuns, aprobări respinse, erori — culese automat. 2️⃣ Analiză: Hermes grupează semnalele și propune sugestii. 3️⃣ Omul decide: aprobi/respingi și completezi răspunsul. 4️⃣ Aplicare: sugestia aprobată intră în baza de cunoștințe. Nicio învățare nu se aplică singură.",
                     "fr": "1️⃣ Signaux : questions sans réponse, approbations rejetées, erreurs — collectés automatiquement. 2️⃣ Analyse : Hermès regroupe les signaux et propose des suggestions. 3️⃣ L'humain décide : vous approuvez/rejetez et complétez la réponse. 4️⃣ Application : la suggestion approuvée entre dans la base de connaissances. Aucun apprentissage ne s'applique seul."},
    "hermes_analizeaza": {"ro": "Rulează analiza", "fr": "Lancer l'analyse"},
    "hermes_semnale": {"ro": "semnale neprocesate", "fr": "signaux non traités"},
    "hermes_invatate": {"ro": "cunoștințe învățate", "fr": "connaissances apprises"},
    "hermes_propuse": {"ro": "sugestii propuse", "fr": "suggestions proposées"},
    "hermes_sugestii": {"ro": "Sugestii de învățare", "fr": "Suggestions d'apprentissage"},
    "hermes_nicio": {"ro": "Nicio sugestie. Rulează analiza după ce apar semnale noi.",
                     "fr": "Aucune suggestion. Lancez l'analyse après l'apparition de nouveaux signaux."},
    "hermes_aproba": {"ro": "Aprobă", "fr": "Approuver"},
    "hermes_respinge": {"ro": "Respinge", "fr": "Rejeter"},
    "hermes_aplica": {"ro": "Aplică", "fr": "Appliquer"},
    "hermes_raspuns_ph": {"ro": "Scrie răspunsul corect, cum ar trebui să răspundă Jarvis…",
                          "fr": "Écrivez la bonne réponse, comme Jarvis devrait répondre…"},
    "hermes_salveaza": {"ro": "Salvează răspunsul", "fr": "Enregistrer la réponse"},
    "hermes_instructiuni": {"ro": "Instrucțiunile agenților (versionate)",
                            "fr": "Instructions des agents (versionnées)"},
    "hermes_instr_ph": {"ro": "Scrie instrucțiunea pentru agent…",
                        "fr": "Écrivez l'instruction pour l'agent…"},
    "hermes_salveaza_instr": {"ro": "Salvează instrucțiunea", "fr": "Enregistrer l'instruction"},
    "hermes_semnal": {"ro": "📡 Semnal #{id} înregistrat ({tip}). Hermes îl va analiza.",
                      "fr": "📡 Signal #{id} enregistré ({tip}). Hermès l'analysera."},
    "hermes_analiza": {"ro": "🔍 Analiză completă: {semnale} semnale procesate → {sugestii} sugestii noi.",
                       "fr": "🔍 Analyse terminée : {semnale} signaux traités → {sugestii} nouvelles suggestions."},
    "hermes_sugestii_zero": {"ro": "Nicio sugestie de învățare. 🎉",
                             "fr": "Aucune suggestion d'apprentissage. 🎉"},
    "hermes_sugestii_lista": {"ro": "📚 Sugestii ({n}):\n{linii}",
                              "fr": "📚 Suggestions ({n}) :\n{linii}"},
    "hermes_sugestie_lipsa": {"ro": "Sugestia nu există sau nu mai e în stadiul „propusă”.",
                              "fr": "La suggestion n'existe pas ou n'est plus « proposée »."},
    "hermes_sugestie_decisa": {"ro": "Sugestia #{id} a fost marcată: {status}.",
                               "fr": "Suggestion #{id} marquée : {status}."},
    "hermes_raspuns_salvat": {"ro": "Răspunsul pentru sugestia #{id} a fost salvat. O poți aproba și aplica.",
                              "fr": "Réponse pour la suggestion #{id} enregistrée. Vous pouvez l'approuver et l'appliquer."},
    "hermes_aplicare_esuata": {"ro": "Aplicarea a eșuat: {cod}.",
                               "fr": "Échec de l'application : {cod}."},
    "hermes_aplicata": {"ro": "✅ Sugestia #{id} a fost aplicată — Jarvis a învățat ceva nou.",
                        "fr": "✅ Suggestion #{id} appliquée — Jarvis a appris quelque chose."},
    "hermes_instructiune": {"ro": "📜 Instrucțiunea agentului {agent} a ajuns la versiunea {v}.",
                            "fr": "📜 Instruction de l'agent {agent} passée à la version {v}."},
    "hermes_raport": {"ro": "📡 Hermes: {neprocesate} semnale neprocesate · {invatate} cunoștințe învățate · {propuse} sugestii propuse.",
                      "fr": "📡 Hermès : {neprocesate} signaux non traités · {invatate} connaissances apprises · {propuse} suggestions proposées."},

}


def t(key: str, lang: str = DEFAULT) -> str:
    lang = lang if lang in LANGS else DEFAULT
    return STRINGS.get(key, {}).get(lang, STRINGS.get(key, {}).get(DEFAULT, key))


def resolve_lang(cerut: str | None, cookie: str | None = None) -> str:
    for v in (cerut, cookie):
        if v in LANGS:
            return v
    return DEFAULT
