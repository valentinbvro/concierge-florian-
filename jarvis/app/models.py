"""Modelele SQLAlchemy ale Jarvis — extensii peste CRM (care rămâne sursa de adevăr)."""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .db import Base


def _now():
    return datetime.now()


class Conversation(Base):
    """Fir de discuție per client/canal."""
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    canal = Column(String(40), default="chat-intern")  # chat-intern/whatsapp/messenger/telefon/email
    contact_ref = Column(String(160), default="")  # telefon, id extern sau utilizator
    titlu = Column(String(200), default="")
    stare = Column(String(20), default="deschisa")  # deschisa/inchisa
    created_at = Column(DateTime, default=_now)
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Un mesaj dintr-o conversație (intrare sau ieșire)."""
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    directie = Column(String(10), default="in")  # in / out
    autor = Column(String(80), default="")  # utilizator sau numele agentului
    text = Column(Text, default="")
    created_at = Column(DateTime, default=_now)
    conversation = relationship("Conversation", back_populates="messages")


class AgentRun(Base):
    """O execuție a unui agent (pentru trasabilitate și costuri)."""
    __tablename__ = "agent_runs"
    id = Column(Integer, primary_key=True)
    agent = Column(String(40), nullable=False)
    actiune = Column(String(80), default="")
    intrari = Column(Text, default="{}")
    iesiri = Column(Text, default="{}")
    stare = Column(String(20), default="ok")  # ok / partial / esuat / asteapta_aprobare
    cost_estimat = Column(Float, default=0.0)
    created_at = Column(DateTime, default=_now)


class AgentTask(Base):
    """Sarcină în coada unui agent."""
    __tablename__ = "agent_tasks"
    id = Column(Integer, primary_key=True)
    agent = Column(String(40), nullable=False)
    titlu = Column(String(200), nullable=False)
    detalii = Column(Text, default="")
    prioritate = Column(String(20), default="normala")  # scazuta / normala / ridicata
    stare = Column(String(20), default="noua")  # noua / in_lucru / gata / esuata
    termen = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_now)


class Approval(Base):
    """Cerere de aprobare umană pentru acțiuni ireversibile/costisitoare."""
    __tablename__ = "approvals"
    id = Column(Integer, primary_key=True)
    tip = Column(String(80), nullable=False)  # ex: trimitere_oferta
    titlu = Column(String(200), nullable=False)
    detalii = Column(Text, default="")
    solicitat_de = Column(String(80), default="")
    stare = Column(String(20), default="asteptare")  # asteptare / aprobat / respins
    decident = Column(String(80), default="")
    created_at = Column(DateTime, default=_now)
    decis_at = Column(DateTime, nullable=True)


class Offer(Base):
    """Ofertă generată (Faza 1: calcul + PDF; trimiterea pe canal după aprobare)."""
    __tablename__ = "offers"
    id = Column(Integer, primary_key=True)
    numar = Column(String(40), default="")  # ex: OF-2026-0001
    opportunity_id = Column(Integer, nullable=True)
    contact_ref = Column(String(160), default="")
    client_nume = Column(String(200), default="")
    linii = Column(Text, default="[]")  # JSON: [{produs, cantitate, pret, discount}]
    subtotal = Column(Float, default=0.0)
    tva = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    valabilitate_zile = Column(Integer, default=30)
    stare = Column(String(20), default="ciorna")  # ciorna / aprobata / trimisa / acceptata / respinsa
    fisier_pdf = Column(String(255), default="")
    approval_id = Column(Integer, ForeignKey("approvals.id"), nullable=True)
    created_at = Column(DateTime, default=_now)


class Produs(Base):
    """Catalog de produse/servicii pentru ofertare."""
    __tablename__ = "produse"
    id = Column(Integer, primary_key=True)
    nume = Column(String(200), nullable=False)
    sku = Column(String(60), default="")
    descriere = Column(Text, default="")
    pret = Column(Float, default=0.0)
    moneda = Column(String(10), default="EUR")
    activ = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_now)


# ---------- Faza 2: Dispecerat taxi de lux ----------

class Sofer(Base):
    """Șoferi ai companiei."""
    __tablename__ = "soferi"
    demo = Column(Integer, default=0)  # 1 = rând demonstrativ (mod demo)
    id = Column(Integer, primary_key=True)
    nume = Column(String(120), nullable=False)
    telefon = Column(String(40), default="")
    status = Column(String(20), default="liber")  # liber / ocupat / indisponibil
    activ = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_now)


class Masina(Base):
    """Mașinile flotei."""
    __tablename__ = "masini"
    demo = Column(Integer, default=0)  # 1 = rând demonstrativ (mod demo)
    id = Column(Integer, primary_key=True)
    marca_model = Column(String(120), nullable=False)
    numar = Column(String(20), default="")  # număr înmatriculare
    locuri = Column(Integer, default=4)
    clasa = Column(String(40), default="lux")
    status = Column(String(20), default="libera")  # libera / ocupata / service
    activa = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_now)


class Cursa(Base):
    """Cursă / rezervare de transport."""
    __tablename__ = "curse"
    demo = Column(Integer, default=0)  # 1 = rând demonstrativ (mod demo)
    id = Column(Integer, primary_key=True)
    client_nume = Column(String(160), default="")
    client_telefon = Column(String(40), default="")
    preluare = Column(String(255), default="")
    destinatie = Column(String(255), default="")
    data_ora = Column(DateTime, nullable=True)
    sofer_id = Column(Integer, ForeignKey("soferi.id"), nullable=True)
    masina_id = Column(Integer, ForeignKey("masini.id"), nullable=True)
    status = Column(String(20), default="rezervata")
    # rezervata / confirmata / in_curs / finalizata / anulata
    pret = Column(Float, default=0.0)
    sursa = Column(String(40), default="chat-intern")
    notite = Column(Text, default="")
    created_at = Column(DateTime, default=_now)
    sofer = relationship("Sofer")
    masina = relationship("Masina")


class Notificare(Base):
    """Notificări de trimis clienților/șoferilor (coadă; trimiterea la conectarea canalelor)."""
    __tablename__ = "notificari"
    demo = Column(Integer, default=0)  # 1 = rând demonstrativ (mod demo)
    id = Column(Integer, primary_key=True)
    destinatar = Column(String(80), default="")  # telefon sau identificator
    canal = Column(String(20), default="whatsapp")
    text = Column(Text, default="")
    status = Column(String(20), default="in_asteptare")  # in_asteptare / trimisa / esuata
    cursa_id = Column(Integer, ForeignKey("curse.id"), nullable=True)
    created_at = Column(DateTime, default=_now)


# ---------- Faza 2: Marketing & competitori ----------

class Postare(Base):
    """Postări social media (cu aprobare înainte de publicare)."""
    __tablename__ = "postari"
    demo = Column(Integer, default=0)  # 1 = rând demonstrativ (mod demo)
    id = Column(Integer, primary_key=True)
    canal = Column(String(40), default="instagram")  # instagram / facebook / linkedin
    text = Column(Text, default="")
    data_programata = Column(DateTime, nullable=True)
    status = Column(String(20), default="ciorna")  # ciorna / aprobata / programata / publicata
    approval_id = Column(Integer, ForeignKey("approvals.id"), nullable=True)
    created_at = Column(DateTime, default=_now)


class Competitor(Base):
    """Firmă concurentă monitorizată."""
    __tablename__ = "competitori"
    demo = Column(Integer, default=0)  # 1 = rând demonstrativ (mod demo)
    id = Column(Integer, primary_key=True)
    nume = Column(String(160), nullable=False)
    website = Column(String(255), default="")
    servicii = Column(Text, default="")
    observatii = Column(Text, default="")
    ultima_verificare = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_now)


class Document(Base):
    """Documente analizate (contracte etc.) — Agentul 9, Faza 4."""
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    nume = Column(String(255), nullable=False)
    cale = Column(String(255), default="")
    tip = Column(String(40), default="")  # contract / oferta / altele
    rezumat = Column(Text, default="")
    created_at = Column(DateTime, default=_now)


class KnowledgeItem(Base):
    """Baza de cunoștințe Q&A pentru customer service (Faza 1)."""
    __tablename__ = "knowledge_base"
    id = Column(Integer, primary_key=True)
    intrebare = Column(String(300), nullable=False)
    raspuns = Column(Text, nullable=False)
    etichete = Column(String(200), default="")
    activa = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_now)


class AuditLog(Base):
    """Jurnal de audit append-only. Agenții nu au drept de ștergere."""
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True)
    actor = Column(String(80), nullable=False)  # utilizator sau agent
    actiune = Column(String(120), nullable=False)
    detalii = Column(Text, default="")
    created_at = Column(DateTime, default=_now)


# ---------- Faza 3: Finanțe (Pennylane) & BI ----------

class MapareClient(Base):
    """Mapare nume client local → ID client Pennylane (evită căutări fragile în API)."""
    __tablename__ = "mapari_clienti"
    id = Column(Integer, primary_key=True)
    nume = Column(String(200), nullable=False, unique=True)
    telefon = Column(String(40), default="")
    pennylane_id = Column(String(80), default="")
    tip = Column(String(20), default="individual")  # individual / company
    created_at = Column(DateTime, default=_now)


class Factura(Base):
    """Factură client: ciornă locală → ciornă Pennylane → emisă (finalizată) → plătită.

    Numerotarea legală aparține Pennylane (la finalizare); `numar` e referința
    internă Jarvis (JF-AAAA-NNNN). Emiterea (finalizarea) e ireversibilă și cere
    aprobare umană (matricea de aprobare: emitere_factura).
    """
    __tablename__ = "facturi"
    demo = Column(Integer, default=0)  # 1 = rând demonstrativ (mod demo)
    id = Column(Integer, primary_key=True)
    numar = Column(String(40), default="")  # ex: JF-2026-0001 (referință internă)
    numar_pennylane = Column(String(40), default="")  # ex: F-2026-0042 (la finalizare)
    pennylane_id = Column(String(80), default="")
    external_reference = Column(String(80), default="")  # idempotență (jarvis-cursa-N)
    cursa_id = Column(Integer, ForeignKey("curse.id"), nullable=True)
    client_nume = Column(String(200), default="")
    client_telefon = Column(String(40), default="")
    linii = Column(Text, default="[]")  # JSON: [{eticheta, cantitate, pret_unitar}]
    subtotal = Column(Float, default=0.0)
    tva = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    moneda = Column(String(10), default="EUR")
    status = Column(String(20), default="ciorna")  # ciorna / emisa / partial / platita / anulata
    data_emitere = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    approval_id = Column(Integer, ForeignKey("approvals.id"), nullable=True)
    created_at = Column(DateTime, default=_now)


class Plata(Base):
    """Încasare înregistrată pentru o factură."""
    __tablename__ = "plati"
    demo = Column(Integer, default=0)  # 1 = rând demonstrativ (mod demo)
    id = Column(Integer, primary_key=True)
    factura_id = Column(Integer, ForeignKey("facturi.id"), nullable=False)
    suma = Column(Float, default=0.0)
    metoda = Column(String(40), default="")  # numerar / card / transfer
    referinta = Column(String(120), default="")
    data = Column(DateTime, default=_now)
    created_at = Column(DateTime, default=_now)


# ---------- Faza 4: Produs, Growth, Risc ----------

class Idee(Base):
    """Bancă de idei — Agentul 7 (Produs & Inovație)."""
    __tablename__ = "idei"
    demo = Column(Integer, default=0)  # 1 = rând demonstrativ (mod demo)
    id = Column(Integer, primary_key=True)
    titlu = Column(String(200), nullable=False)
    descriere = Column(Text, default="")
    categorie = Column(String(60), default="serviciu")  # serviciu / proces / marketing / altul
    scor = Column(Integer, default=0)  # voturi / evaluare 0-10
    status = Column(String(20), default="noua")  # noua / in_evaluare / oportunitate / respinsa
    created_at = Column(DateTime, default=_now)


class Oportunitate(Base):
    """Fișă de oportunitate — idee maturizată cu cifre estimate."""
    __tablename__ = "oportunitati"
    demo = Column(Integer, default=0)  # 1 = rând demonstrativ (mod demo)
    id = Column(Integer, primary_key=True)
    titlu = Column(String(200), nullable=False)
    descriere = Column(Text, default="")
    investitie_estimata = Column(Float, default=0.0)
    venit_lunar_estimat = Column(Float, default=0.0)
    status = Column(String(20), default="evaluare")  # evaluare / aprobata / respinsa / lansata
    idee_id = Column(Integer, ForeignKey("idei.id"), nullable=True)
    approval_id = Column(Integer, ForeignKey("approvals.id"), nullable=True)
    created_at = Column(DateTime, default=_now)


class Investitie(Base):
    """Evaluare investiție — Agentul 8 (Growth & Capital Allocation)."""
    __tablename__ = "investitii"
    demo = Column(Integer, default=0)  # 1 = rând demonstrativ (mod demo)
    id = Column(Integer, primary_key=True)
    titlu = Column(String(200), nullable=False)
    tip = Column(String(40), default="masina")  # masina / echipament / marketing / altul
    cost = Column(Float, default=0.0)
    venit_lunar_estimat = Column(Float, default=0.0)
    status = Column(String(20), default="evaluare")  # evaluare / aprobata / respinsa / realizata
    approval_id = Column(Integer, ForeignKey("approvals.id"), nullable=True)
    created_at = Column(DateTime, default=_now)


class Buget(Base):
    """Buget lunar planificat pe categorii."""
    __tablename__ = "bugete"
    demo = Column(Integer, default=0)  # 1 = rând demonstrativ (mod demo)
    id = Column(Integer, primary_key=True)
    luna = Column(String(7), nullable=False)  # YYYY-MM
    categorie = Column(String(60), nullable=False)
    planificat = Column(Float, default=0.0)
    created_at = Column(DateTime, default=_now)


class Verificare(Base):
    """Verificare de conformitate cu scadență (ITP, asigurare, licențe…)."""
    __tablename__ = "verificari"
    demo = Column(Integer, default=0)  # 1 = rând demonstrativ (mod demo)
    id = Column(Integer, primary_key=True)
    tip = Column(String(60), nullable=False)  # itp / asigurare / licenta_sofer / vtc / alta
    referinta = Column(String(160), default="")  # ex: "B-123-ABC" sau numele șoferului
    expira_la = Column(DateTime, nullable=True)
    status = Column(String(20), default="valida")  # valida / expira_curand / expirata
    notite = Column(Text, default="")
    created_at = Column(DateTime, default=_now)


class Neregula(Base):
    """Neregulă / incident semnalat — Agentul 9."""
    __tablename__ = "nereguli"
    demo = Column(Integer, default=0)  # 1 = rând demonstrativ (mod demo)
    id = Column(Integer, primary_key=True)
    titlu = Column(String(200), nullable=False)
    descriere = Column(Text, default="")
    severitate = Column(String(20), default="medie")  # scazuta / medie / ridicata
    status = Column(String(20), default="noua")  # noua / in_investigare / rezolvata
    created_at = Column(DateTime, default=_now)


class AnalizaDocument(Base):
    """Rezultatul pre-filtrului de analiză contracte (NU consultanță juridică)."""
    __tablename__ = "analize_documente"
    demo = Column(Integer, default=0)  # 1 = rând demonstrativ (mod demo)
    id = Column(Integer, primary_key=True)
    nume = Column(String(255), default="")
    concluzii = Column(Text, default="")  # JSON: {clauze_gasite, clauze_lipsa, scor_risc, disclaimer}
    created_at = Column(DateTime, default=_now)


class KpiSnapshot(Base):
    """Valori KPI zilnice, pentru trenduri BI (Faza 3)."""
    __tablename__ = "kpi_snapshots"
    demo = Column(Integer, default=0)  # 1 = rând demonstrativ (mod demo)
    id = Column(Integer, primary_key=True)
    cheie = Column(String(80), nullable=False)
    valoare = Column(Float, default=0.0)
    created_at = Column(DateTime, default=_now)


class Campanie(Base):
    """Campanie de marketing cu statistici (pentru previzualizare demo / raportare)."""
    __tablename__ = "campanii"
    demo = Column(Integer, default=0)  # 1 = rând demonstrativ (mod demo)
    id = Column(Integer, primary_key=True)
    nume = Column(String(200), nullable=False)
    canal = Column(String(60), default="instagram")  # instagram / facebook / linkedin / google / tiktok
    data_inceput = Column(DateTime, nullable=True)
    data_sfarsit = Column(DateTime, nullable=True)
    buget = Column(Float, default=0.0)
    reach = Column(Integer, default=0)
    leaduri = Column(Integer, default=0)
    venit = Column(Float, default=0.0)
    cost = Column(Float, default=0.0)
    status = Column(String(20), default="activa")  # activa / incheiata / planificata
    created_at = Column(DateTime, default=_now)


# ---------- Hermes: antrenare & învățare continuă ----------

class SemnalAntrenare(Base):
    """Semnal brut pentru învățare: întrebare fără răspuns, aprobare respinsă etc."""
    __tablename__ = "semnale_antrenare"
    id = Column(Integer, primary_key=True)
    tip = Column(String(40), default="intrebare_fara_raspuns")
    # intrebare_fara_raspuns / aprobare_respinsa / eroare_agent / corectie_utilizator
    continut = Column(Text, default="")
    meta = Column(Text, default="{}")  # JSON: agent, canal, etc.
    creat_de = Column(String(80), default="sistem")
    procesat = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_now)


class SugestieInvatare(Base):
    """Sugestie de îmbunătățire generată de Hermes — se aplică doar cu aprobare umană."""
    __tablename__ = "sugestii_invatare"
    id = Column(Integer, primary_key=True)
    tip = Column(String(40), default="cunostinta_noua")
    # cunostinta_noua / ajustare_prag / imbunatatire_raspuns
    titlu = Column(String(300), default="")
    detalii = Column(Text, default="{}")  # JSON: intrebare, raspuns_propus, ...
    status = Column(String(20), default="propusa")  # propusa / aprobata / respinsa / aplicata
    semnal_id = Column(Integer, ForeignKey("semnale_antrenare.id"), nullable=True)
    decis_de = Column(String(80), default="")
    created_at = Column(DateTime, default=_now)


class InstructiuneAgent(Base):
    """Versiuni ale instrucțiunilor unui agent — antrenare continuă cu trasabilitate."""
    __tablename__ = "instructiuni_agenti"
    id = Column(Integer, primary_key=True)
    agent = Column(String(40), nullable=False)
    versiune = Column(Integer, default=1)
    text = Column(Text, default="")
    activa = Column(Boolean, default=True)
    creat_de = Column(String(80), default="valentin")
    created_at = Column(DateTime, default=_now)
