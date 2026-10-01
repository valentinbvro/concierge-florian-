"""Date inițiale: utilizatori demo, firme, contacte, leaduri, oportunități,
cazuri, activități, automatizări și setări. Rulează la prima pornire."""
from datetime import date, datetime, timedelta

from .auth import hash_password
from .db import SessionLocal
from .models import (Account, Activity, Automation, Case, Contact, Lead,
                     Opportunity, Setting, User)


def seed():
    db = SessionLocal()
    try:
        if db.query(User).first():
            return  # deja populat
        now = datetime.now()

        admin = User(name="Administrator", email="admin@demo.ro",
                     pw_hash=hash_password("admin123"), role="admin")
        maria = User(name="Maria Popescu", email="maria@demo.ro",
                     pw_hash=hash_password("maria123"), role="vanzari")
        ion = User(name="Ion Ionescu", email="ion@demo.ro",
                   pw_hash=hash_password("ion123"), role="suport")
        db.add_all([admin, maria, ion])
        db.flush()

        # --- automatizări predefinite ---
        db.add_all([
            Automation(key="lead_nou", name="Sarcină la lead nou",
                       description="Creează sarcina „Contactează leadul” "
                                   "cu scadență mâine, pentru responsabil.",
                       enabled=True),
            Automation(key="oportunitate_castigata",
                       name="Follow-up la oportunitate câștigată",
                       description="La trecerea în „câștigat”, creează "
                                   "sarcina „Follow-up client nou” la +7 zile.",
                       enabled=True),
            Automation(key="caz_urgent", name="Sarcină la caz urgent",
                       description="La caz nou cu prioritate „urgentă”, "
                                   "creează sarcină cu scadență azi.",
                       enabled=True),
        ])
        db.add(Setting(key="nume_firma", value="Firma Demo SRL"))

        # --- firme ---
        firme = [
            Account(name="SC Alfa SRL", industry="IT & Software",
                    website="www.alfa-it.ro", phone="021 310 4455",
                    email="contact@alfa-it.ro",
                    address="Bd. Pipera 42, București", owner_id=maria.id),
            Account(name="SC Beta Construct SRL", industry="Construcții",
                    website="www.betaconstruct.ro", phone="0264 598 201",
                    email="office@betaconstruct.ro",
                    address="Str. Fabricii 18, Cluj-Napoca", owner_id=maria.id),
            Account(name="Gamma Retail SA", industry="Retail",
                    website="www.gamma-retail.ro", phone="021 444 8899",
                    email="info@gamma-retail.ro",
                    address="Calea Floreasca 169, București", owner_id=maria.id),
            Account(name="Delta Pharma SRL", industry="Farmaceutice",
                    website="www.deltapharma.ro", phone="0232 271 330",
                    email="contact@deltapharma.ro",
                    address="Bd. Carol I 12, Iași", owner_id=ion.id),
            Account(name="Epsilon Logistic SRL", industry="Logistică",
                    website="www.epsilon-logistic.ro", phone="0248 210 765",
                    email="dispecerat@epsilon-logistic.ro",
                    address="Str. Depozitelor 5, Pitești", owner_id=maria.id),
        ]
        db.add_all(firme)
        db.flush()

        # --- contacte ---
        contacte = [
            Contact(account_id=firme[0].id, first_name="Andrei", last_name="Vasilescu",
                    email="andrei.vasilescu@alfa-it.ro", phone="0722 111 234",
                    title="Director General", owner_id=maria.id),
            Contact(account_id=firme[0].id, first_name="Elena", last_name="Dumitru",
                    email="elena.dumitru@alfa-it.ro", phone="0722 111 235",
                    title="Manager Achiziții", owner_id=maria.id),
            Contact(account_id=firme[1].id, first_name="Radu", last_name="Mihăilescu",
                    email="radu.mihailescu@betaconstruct.ro", phone="0744 222 345",
                    title="Director Tehnic", owner_id=maria.id),
            Contact(account_id=firme[2].id, first_name="Ioana", last_name="Stanciu",
                    email="ioana.stanciu@gamma-retail.ro", phone="0755 333 456",
                    title="Director Marketing", owner_id=maria.id),
            Contact(account_id=firme[2].id, first_name="Vlad", last_name="Georgescu",
                    email="vlad.georgescu@gamma-retail.ro", phone="0755 333 457",
                    title="Responsabil IT", owner_id=maria.id),
            Contact(account_id=firme[3].id, first_name="Cristina", last_name="Popa",
                    email="cristina.popa@deltapharma.ro", phone="0766 444 567",
                    title="Farmacist-șef", owner_id=ion.id),
            Contact(account_id=firme[4].id, first_name="Mihai", last_name="Tudor",
                    email="mihai.tudor@epsilon-logistic.ro", phone="0777 555 678",
                    title="Director Operațiuni", owner_id=maria.id),
            Contact(account_id=None, first_name="Simona", last_name="Rădulescu",
                    email="simona.radulescu@gmail.com", phone="0788 666 789",
                    title="Consultant independent", owner_id=maria.id),
        ]
        db.add_all(contacte)
        db.flush()

        # --- leaduri ---
        leaduri = [
            Lead(first_name="Alexandru", last_name="Neagu", company="Neagu Consulting",
                 email="alex@neagu-consulting.ro", phone="0721 100 200", status="nou",
                 source="Website", notes="Interesat de modulul de vânzări.",
                 owner_id=maria.id, created_at=now - timedelta(days=2)),
            Lead(first_name="Diana", last_name="Florescu", company="Florescu Design",
                 email="diana@florescu-design.ro", phone="0721 100 201", status="nou",
                 source="Recomandare", notes="", owner_id=maria.id,
                 created_at=now - timedelta(days=1)),
            Lead(first_name="Bogdan", last_name="Ilie", company="Ilie & Asociații",
                 email="bogdan@ilie-asociatii.ro", phone="0721 100 202",
                 status="contactat", source="Târg", notes="Discuție inițială purtată.",
                 owner_id=maria.id, created_at=now - timedelta(days=9)),
            Lead(first_name="Carmen", last_name="Voicu", company="Voicu Imobiliare",
                 email="carmen@voicu-imobiliare.ro", phone="0721 100 203",
                 status="contactat", source="LinkedIn", notes="", owner_id=maria.id,
                 created_at=now - timedelta(days=12)),
            Lead(first_name="Dan", last_name="Petrescu", company="Petrescu Auto",
                 email="dan@petrescu-auto.ro", phone="0721 100 204", status="calificat",
                 source="Website", notes="Buget confirmat, decizie în 30 zile.",
                 owner_id=maria.id, created_at=now - timedelta(days=20)),
            Lead(first_name="Monica", last_name="Dobre", company="Dobre Fashion",
                 email="monica@dobre-fashion.ro", phone="0721 100 205",
                 status="calificat", source="Recomandare", notes="", owner_id=maria.id,
                 created_at=now - timedelta(days=25)),
            Lead(first_name="Paul", last_name="Stoica", company="Stoica Media",
                 email="paul@stoica-media.ro", phone="0721 100 206", status="convertit",
                 source="Website", notes="Convertit în client.",
                 owner_id=maria.id, created_at=now - timedelta(days=40)),
            Lead(first_name="Laura", last_name="Munteanu", company="Munteanu Food",
                 email="laura@munteanu-food.ro", phone="0721 100 207", status="pierdut",
                 source="Târg", notes="A ales un competitor.",
                 owner_id=maria.id, created_at=now - timedelta(days=45)),
        ]
        db.add_all(leaduri)
        db.flush()

        # --- oportunități (toate stagiile) ---
        azi = date.today()
        oportunitati = [
            Opportunity(name="Licențe CRM — Alfa", account_id=firme[0].id,
                        contact_id=contacte[0].id, amount=25000, stage="prospectare",
                        probability=10, close_date=azi + timedelta(days=60),
                        owner_id=maria.id),
            Opportunity(name="Echipamente șantier — Beta", account_id=firme[1].id,
                        contact_id=contacte[2].id, amount=48000, stage="calificare",
                        probability=25, close_date=azi + timedelta(days=45),
                        owner_id=maria.id),
            Opportunity(name="Platformă e-commerce — Gamma", account_id=firme[2].id,
                        contact_id=contacte[3].id, amount=75000, stage="propunere",
                        probability=50, close_date=azi + timedelta(days=30),
                        owner_id=maria.id),
            Opportunity(name="Sistem gestiune stocuri — Delta", account_id=firme[3].id,
                        contact_id=contacte[5].id, amount=32000, stage="negociere",
                        probability=75, close_date=azi + timedelta(days=15),
                        owner_id=maria.id),
            Opportunity(name="Contract mentenanță — Alfa", account_id=firme[0].id,
                        contact_id=contacte[1].id, amount=18000, stage="castigat",
                        probability=100, close_date=azi - timedelta(days=5),
                        owner_id=maria.id),
            Opportunity(name="Flotă GPS — Epsilon", account_id=firme[4].id,
                        contact_id=contacte[6].id, amount=41000, stage="negociere",
                        probability=70, close_date=azi + timedelta(days=20),
                        owner_id=maria.id),
            Opportunity(name="Digitalizare magazine — Gamma", account_id=firme[2].id,
                        contact_id=contacte[4].id, amount=60000, stage="propunere",
                        probability=45, close_date=azi + timedelta(days=40),
                        owner_id=maria.id),
            Opportunity(name="Licențe vechi — Beta", account_id=firme[1].id,
                        contact_id=contacte[2].id, amount=12000, stage="pierdut",
                        probability=0, close_date=azi - timedelta(days=10),
                        owner_id=maria.id),
        ]
        db.add_all(oportunitati)
        db.flush()

        # --- cazuri ---
        cazuri = [
            Case(account_id=firme[0].id, contact_id=contacte[0].id,
                 subject="Eroare la sincronizarea datelor",
                 description="Sincronizarea zilnică eșuează cu eroare de timeout.",
                 status="deschis", priority="ridicata", owner_id=ion.id,
                 created_at=now - timedelta(days=1)),
            Case(account_id=firme[2].id, contact_id=contacte[4].id,
                 subject="Pagină de plată indisponibilă",
                 description="Clienții nu pot finaliza comenzile online.",
                 status="nou", priority="urgenta", owner_id=ion.id,
                 created_at=now - timedelta(hours=5)),
            Case(account_id=firme[3].id, contact_id=contacte[5].id,
                 subject="Solicitare raport lunar",
                 description="Doresc un raport automat pe email la început de lună.",
                 status="in_asteptare", priority="medie", owner_id=ion.id,
                 created_at=now - timedelta(days=4)),
            Case(account_id=firme[1].id, contact_id=contacte[2].id,
                 subject="Actualizare date de facturare",
                 description="Schimbare sediu social pe facturi.",
                 status="rezolvat", priority="scazuta", owner_id=ion.id,
                 created_at=now - timedelta(days=8)),
            Case(account_id=firme[4].id, contact_id=contacte[6].id,
                 subject="GPS arată poziții eronate",
                 description="3 vehicule apar pe hartă în locații greșite.",
                 status="deschis", priority="ridicata", owner_id=ion.id,
                 created_at=now - timedelta(days=2)),
            Case(account_id=firme[0].id, contact_id=contacte[1].id,
                 subject="Întrebare licențiere",
                 description="Câte conturi de utilizator include pachetul?",
                 status="inchis", priority="scazuta", owner_id=ion.id,
                 created_at=now - timedelta(days=15)),
        ]
        db.add_all(cazuri)
        db.flush()

        # --- activități ---
        activitati = [
            Activity(tip="sarcina", subject="Sună leadul Alexandru Neagu",
                     description="", due_date=azi + timedelta(days=1),
                     status="deschis", related_kind="lead",
                     related_id=leaduri[0].id, owner_id=maria.id,
                     created_at=now - timedelta(days=1)),
            Activity(tip="apel", subject="Apel de descoperire — Beta Construct",
                     description="Discutat nevoile pentru echipamente.",
                     due_date=azi - timedelta(days=1), status="inchis",
                     related_kind="firma", related_id=firme[1].id,
                     owner_id=maria.id, created_at=now - timedelta(days=3)),
            Activity(tip="intalnire", subject="Demo platformă — Gamma Retail",
                     description="Prezentare modul e-commerce.", due_date=azi + timedelta(days=3),
                     status="deschis", related_kind="oportunitate",
                     related_id=oportunitati[2].id, owner_id=maria.id,
                     created_at=now - timedelta(days=1)),
            Activity(tip="email", subject="Trimite oferta — Delta Pharma",
                     description="", due_date=azi, status="deschis",
                     related_kind="oportunitate", related_id=oportunitati[3].id,
                     owner_id=maria.id, created_at=now - timedelta(hours=6)),
            Activity(tip="sarcina", subject="Verifică log-urile de sincronizare",
                     description="", due_date=azi, status="deschis",
                     related_kind="caz", related_id=cazuri[0].id, owner_id=ion.id,
                     created_at=now - timedelta(days=1)),
            Activity(tip="apel", subject="Escaladare plată Gamma",
                     description="Echipa tehnică notificată.",
                     due_date=azi - timedelta(days=0), status="inchis",
                     related_kind="caz", related_id=cazuri[1].id, owner_id=ion.id,
                     created_at=now - timedelta(hours=4)),
            Activity(tip="sarcina", subject="Pregătește contractul — Alfa",
                     description="", due_date=azi + timedelta(days=2),
                     status="deschis", related_kind="oportunitate",
                     related_id=oportunitati[4].id, owner_id=maria.id,
                     created_at=now - timedelta(days=2)),
            Activity(tip="intalnire", subject="Ședință kick-off — Epsilon",
                     description="", due_date=azi + timedelta(days=5),
                     status="deschis", related_kind="firma",
                     related_id=firme[4].id, owner_id=maria.id,
                     created_at=now - timedelta(days=1)),
            Activity(tip="email", subject="Follow-up Monica Dobre",
                     description="", due_date=azi - timedelta(days=2),
                     status="inchis", related_kind="lead",
                     related_id=leaduri[5].id, owner_id=maria.id,
                     created_at=now - timedelta(days=5)),
            Activity(tip="sarcina", subject="Actualizează datele de facturare Beta",
                     description="", due_date=azi + timedelta(days=1),
                     status="deschis", related_kind="caz",
                     related_id=cazuri[3].id, owner_id=ion.id,
                     created_at=now - timedelta(days=2)),
        ]
        db.add_all(activitati)

        db.commit()
        print("Seed: baza de date a fost populată cu date demo.")
    finally:
        db.close()
