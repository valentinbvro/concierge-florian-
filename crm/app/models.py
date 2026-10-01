"""Modelele SQLAlchemy ale CRM-ului."""
from datetime import datetime
from sqlalchemy import (Boolean, Column, Date, DateTime, Float, ForeignKey,
                        Integer, String, Text)
from sqlalchemy.orm import relationship

from .db import Base


def _now():
    return datetime.now()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(160), unique=True, nullable=False, index=True)
    pw_hash = Column(String(256), nullable=False)
    role = Column(String(20), nullable=False, default="vanzari")  # admin/vanzari/suport
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=_now)


class Setting(Base):
    __tablename__ = "settings"
    key = Column(String(80), primary_key=True)
    value = Column(String(255), nullable=False, default="")


class Automation(Base):
    __tablename__ = "automations"
    id = Column(Integer, primary_key=True)
    key = Column(String(80), unique=True, nullable=False)
    name = Column(String(160), nullable=False)
    description = Column(Text, default="")
    enabled = Column(Boolean, default=True, nullable=False)


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    name = Column(String(160), nullable=False)
    industry = Column(String(80), default="")
    website = Column(String(160), default="")
    phone = Column(String(40), default="")
    email = Column(String(160), default="")
    address = Column(String(255), default="")
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=_now)
    owner = relationship("User")
    contacts = relationship("Contact", back_populates="account")
    opportunities = relationship("Opportunity", back_populates="account")
    cases = relationship("Case", back_populates="account")


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    email = Column(String(160), default="")
    phone = Column(String(40), default="")
    title = Column(String(80), default="")  # funcție
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=_now)
    account = relationship("Account", back_populates="contacts")
    owner = relationship("User")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    company = Column(String(160), default="")
    email = Column(String(160), default="")
    phone = Column(String(40), default="")
    status = Column(String(20), default="nou")  # nou/contactat/calificat/convertit/pierdut
    source = Column(String(80), default="")
    notes = Column(Text, default="")
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=_now)
    owner = relationship("User")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Opportunity(Base):
    __tablename__ = "opportunities"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    amount = Column(Float, default=0.0)
    stage = Column(String(20), default="prospectare")
    # prospectare/calificare/propunere/negociere/castigat/pierdut
    probability = Column(Integer, default=10)
    close_date = Column(Date, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=_now)
    account = relationship("Account", back_populates="opportunities")
    contact = relationship("Contact")
    owner = relationship("User")


class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True)
    tip = Column(String(20), default="sarcina")  # sarcina/apel/email/intalnire
    subject = Column(String(200), nullable=False)
    description = Column(Text, default="")
    due_date = Column(Date, nullable=True)
    status = Column(String(10), default="deschis")  # deschis/inchis
    related_kind = Column(String(20), default="")  # lead/firma/contact/oportunitate/caz
    related_id = Column(Integer, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=_now)
    owner = relationship("User")


class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    subject = Column(String(200), nullable=False)
    description = Column(Text, default="")
    status = Column(String(20), default="nou")  # nou/deschis/in_asteptare/rezolvat/inchis
    priority = Column(String(20), default="medie")  # scazuta/medie/ridicata/urgenta
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=_now)
    account = relationship("Account", back_populates="cases")
    contact = relationship("Contact")
    owner = relationship("User")


class ApiToken(Base):
    """Tokenuri de acces pentru API-ul REST (Authorization: Bearer)."""
    __tablename__ = "api_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(80), nullable=False, default="")  # etichetă, ex: "Site web"
    token_hash = Column(String(64), unique=True, nullable=False, index=True)  # sha256
    prefix = Column(String(12), default="")  # primele caractere, pentru identificare
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=_now)
    last_used_at = Column(DateTime, nullable=True)
    user = relationship("User")
