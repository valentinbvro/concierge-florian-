"""Conexiunea la baza de date Jarvis (SQLite)."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from . import config

engine = create_engine(f"sqlite:///{config.DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db():
    from . import models  # noqa: F401  (înregistrează modelele)
    Base.metadata.create_all(engine)
    migreaza()


def migreaza():
    """Migrații ușoare: adaugă coloane noi tabelelor existente (fără pierderi)."""
    from sqlalchemy import text
    with engine.begin() as conn:
        cols = {r[1] for r in conn.execute(text("PRAGMA table_info(offers)"))}
        if "numar" not in cols:
            conn.execute(text("ALTER TABLE offers ADD COLUMN numar VARCHAR(40) DEFAULT ''"))
        if "valabilitate_zile" not in cols:
            conn.execute(text("ALTER TABLE offers ADD COLUMN valabilitate_zile INTEGER DEFAULT 30"))
        if "client_nume" not in cols:
            conn.execute(text("ALTER TABLE offers ADD COLUMN client_nume VARCHAR(200) DEFAULT ''"))
        if "subtotal" not in cols:
            conn.execute(text("ALTER TABLE offers ADD COLUMN subtotal FLOAT DEFAULT 0"))
        if "tva" not in cols:
            conn.execute(text("ALTER TABLE offers ADD COLUMN tva FLOAT DEFAULT 0"))
