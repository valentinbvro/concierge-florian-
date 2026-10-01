"""Jarvis Orchestrator — creierul central.

Faza 2: + dispecerat taxi (curse/șoferi/mașini), marketing & media,
        competitori + interfață bilingvă RO/FR.
"""
import re
from datetime import date

from . import audit, catalog, cunostinte, dispecerat, pipeline
from .agents import construieste_agenti
from .db import SessionLocal
from .i18n import t
from .models import Conversation, Message

# cuvânt-cheie -> agent; prima potrivire câștigă
REGULI_INTENTIE = [
    ("operatiuni", ["curs", "course", "șofer", "sofer", "chauffeur", "mașin",
                    "masin", "voiture", "dispecer", "dispatch", "atribuie", "assigner"]),
    ("marketing", ["postare", "publication", "editorial", "social", "marketing",
                   "campanie", "reclam", "landing"]),
    ("research", ["competitor", "concurrent", "observație", "observation"]),
    ("vanzari", ["lead", "ofert", "devis", "client", "vânzare", "vanzare",
                 "negoci", "follow", "scor", "score"]),
    ("vanzari", ["problemă", "problema", "defecțiune", "defectiune", "nu merge", "eroare",
                 "reclamație", "reclamatie", "tichet", "problème", "panne"]),
    ("finante", ["factur", "bani", "plăt", "plat", "cheltu", "buget", "încas", "incas", "bancar",
                "pennylane", "encaiss", "tva"]),
    ("operatiuni", ["livrare", "lucrare", "interven", "echip", "programare", "termen"]),
    ("bi", ["raport", "statistic", "kpi", "profit", "trend", "pipeline"]),
    ("risc", ["contract", "risc", "conform", "juridic", "avocat", "securitate"]),
    ("hermes", ["hermes", "hermès", "învățare", "invatare", "antrenare",
                "apprentissage", "entraînement", "sugestie învățare",
                "suggestion d'apprentissage"]),
    ("produs", ["idee", "inova", "serviciu nou", "produs nou", "catalog", "catalogue"]),
    ("growth", ["investi", "capital", "creștere", "crestere", "achizi"]),
]

_CUVINTE_PROBLEMA = ["problemă", "problema", "defecțiune", "defectiune", "nu merge",
                     "eroare", "reclamație", "reclamatie", "s-a stricat", "nu funcționează",
                     "nu functioneaza", "problème", "panne"]


class Orchestrator:
    def __init__(self, crm):
        self.crm = crm
        self.agenti = construieste_agenti(crm)

    # --- clasificare ---
    def clasifica(self, text: str) -> str:
        t = text.lower()
        for agent, cuvinte in REGULI_INTENTIE:
            if any(c in t for c in cuvinte):
                return agent
        return "vanzari"

    # --- parsere comenzi (RO + FR) ---
    def _parse_lead(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:lead\s+nou|nouveau\s+lead)\s*:\s*(.+)", text.strip())
        if not m:
            return None
        parti = [p.strip() for p in m.group(1).split(",") if p.strip()]
        if not parti:
            return None
        nume = parti[0].split()
        payload = {"first_name": nume[0], "last_name": " ".join(nume[1:]),
                   "phone": "", "email": "", "company": "", "notes": ""}
        for p in parti[1:]:
            if "@" in p:
                payload["email"] = p
            elif re.search(r"\d{6,}", p):
                payload["phone"] = p
            elif not payload["company"]:
                payload["company"] = p
            else:
                payload["notes"] += p + " "
        payload["notes"] = payload["notes"].strip()
        return payload

    def _parse_activitate(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:activitate|activité)\s*:\s*(.+)", text.strip())
        return {"subject": m.group(1).strip()} if m else None

    def _parse_produs(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:produs\s+nou|nouveau\s+produit)\s*:\s*(.+)", text.strip())
        if not m:
            return None
        parti = [p.strip() for p in m.group(1).split(",")]
        try:
            pret = float(parti[1]) if len(parti) > 1 else 0.0
        except ValueError:
            return None
        return {"nume": parti[0], "pret": pret, "sku": parti[2] if len(parti) > 2 else ""}

    def _parse_oferta(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:ofert[ăa]|devis)\s+(?:pentru\s+([^:]+):\s*|pour\s+([^:]+):\s*)?(.+)",
                     text.strip())
        if not m:
            return None
        client_nume = ((m.group(1) or m.group(2)) or "").strip()
        linii = []
        for buc in m.group(3).split(","):
            buc = buc.strip()
            mm = re.match(r"(.+?)\s*[x×]\s*(\d+)", buc)
            if mm:
                linii.append({"produs": mm.group(1).strip(), "cantitate": int(mm.group(2))})
            elif buc:
                linii.append({"produs": buc, "cantitate": 1})
        return {"client_nume": client_nume, "linii": linii} if linii else None

    def _parse_caz(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:caz\s+nou|nouveau\s+ticket)\s*:\s*(.+)", text.strip())
        if not m:
            return None
        parti = [p.strip() for p in m.group(1).split(",", 1)]
        return {"subject": parti[0], "description": parti[1] if len(parti) > 1 else ""}

    def _parse_qa(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:adaug[ăa]\s+q&a|ajouter\s+q&r)\s*:\s*(.+?)\s*\|\s*(.+)", text.strip())
        return {"intrebare": m.group(1).strip(), "raspuns": m.group(2).strip()} if m else None

    def _parse_califica(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:calific[ăa]\s+lead(?:ul)?|qualifier\s+lead)\s+(\d+)", text.strip())
        return {"lead_id": int(m.group(1)), "status": "calificat"} if m else None

    # --- Faza 2: dispecerat ---
    def _parse_cursa(self, text: str) -> dict | None:
        """'cursă nouă: Nume, 0722..., Preluare, Destinație, azi 14:30'"""
        m = re.match(r"(?i)(?:curs[ăa]\s+nou[ăa]?|nouvelle\s+course)\s*:\s*(.+)", text.strip())
        if not m:
            return None
        parti = [p.strip() for p in m.group(1).split(",")]
        if len(parti) < 3:
            return None
        payload = {"client_nume": parti[0], "client_telefon": "", "preluare": "",
                   "destinatie": "", "cand": ""}
        rest = parti[1:]
        # telefonul: primul câmp cu 6+ cifre
        for i, p in enumerate(rest):
            if re.search(r"\d{6,}", p):
                payload["client_telefon"] = p
                rest = rest[:i] + rest[i + 1:]
                break
        if len(rest) >= 3:
            payload["preluare"], payload["destinatie"], payload["cand"] = rest[0], rest[1], ", ".join(rest[2:])
        elif len(rest) == 2:
            payload["preluare"], payload["destinatie"] = rest
        else:
            return None
        return payload

    def _parse_atribuie(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:atribuie\s+cursa|assigner\s+course)\s+(\d+)"
                     r"(?:\s*:\s*(?:șofer|sofer|chauffeur)\s+(\d+)\s*,?\s*"
                     r"(?:mașin[ăa]|masina|voiture)\s+(\d+))?", text.strip())
        if not m:
            return None
        return {"cursa_id": int(m.group(1)),
                "sofer_id": int(m.group(2)) if m.group(2) else None,
                "masina_id": int(m.group(3)) if m.group(3) else None}

    def _parse_cursa_status(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:cursa|course)\s+(\d+)\s*:\s*(.+)", text.strip())
        if not m:
            return None
        return {"cursa_id": int(m.group(1)), "status": m.group(2).strip()}

    def _parse_sofer(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:șofer|sofer|chauffeur)\s+nou(?:veau)?\s*:\s*(.+)", text.strip())
        if not m:
            return None
        parti = [p.strip() for p in m.group(1).split(",", 1)]
        return {"nume": parti[0], "telefon": parti[1] if len(parti) > 1 else ""}

    def _parse_masina(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:mașin[ăa]|masina|voiture)\s+nou(?:ă|velle)?\s*:\s*(.+)", text.strip())
        if not m:
            return None
        parti = [p.strip() for p in m.group(1).split(",")]
        return {"marca_model": parti[0], "numar": parti[1] if len(parti) > 1 else "",
                "locuri": int(parti[2]) if len(parti) > 2 and parti[2].isdigit() else 4}

    # --- Faza 2: marketing & competitori ---
    def _parse_postare(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:postare\s+nou[ăa]?|nouvelle\s+publication)\s*:\s*(.+)", text.strip())
        if not m:
            return None
        parti = [p.strip() for p in m.group(1).split(",", 1)]
        if len(parti) == 2 and parti[0].lower() in ("instagram", "facebook", "linkedin"):
            return {"canal": parti[0].lower(), "text": parti[1]}
        return {"canal": "instagram", "text": m.group(1).strip()}

    def _parse_publica(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:public[ăa]\s+postarea|publier\s+publication)\s+(\d+)", text.strip())
        return {"postare_id": int(m.group(1))} if m else None

    def _parse_competitor(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:competitor|concurrent)\s+nou(?:veau)?\s*:\s*(.+)", text.strip())
        if not m:
            return None
        parti = [p.strip() for p in m.group(1).split(",", 1)]
        return {"nume": parti[0], "website": parti[1] if len(parti) > 1 else ""}

    def _parse_observatie(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:observa[țt]ie|observation)\s+(?:competitor|concurrent)\s+(\d+)\s*:\s*(.+)",
                     text.strip())
        if not m:
            return None
        return {"competitor_id": int(m.group(1)), "text": m.group(2).strip()}

    # --- Faza 3: finanțe & BI ---
    def _parse_factura(self, text: str) -> dict | None:
        """'factură cursa 5: 120' / 'facture course 5 : 120' / 'factură manuală: 200'"""
        m = re.match(r"(?i)(?:factur[ăa]|facture)\s+(?:(?:pentru\s+|pour\s+)?(?:cursa|course)\s+(\d+)|"
                     r"(?:manual[ăa]|manuelle)\s*(?::\s*(.+))?)\s*(?::\s*(\d+(?:[.,]\d+)?))?\s*$",
                     text.strip())
        if not m:
            return None
        if m.group(1):
            suma = m.group(3)
            return {"cursa_id": int(m.group(1)),
                    "suma": float(suma.replace(",", ".")) if suma else None}
        rest = (m.group(2) or "").strip()
        mm = re.match(r"(.+?)\s*:\s*(\d+(?:[.,]\d+)?)\s*$", rest)
        if mm:
            return {"cursa_id": None, "client_nume": mm.group(1).strip(),
                    "suma": float(mm.group(2).replace(",", "."))}
        return None

    def _parse_emite_factura(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:emite|émettre)\s+(?:factura\s+|la\s+facture\s+)?(\d+)",
                     text.strip())
        return {"factura_id": int(m.group(1))} if m else None

    def _parse_trimite_factura(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:trimite\s+factura|envoyer\s+(?:la\s+)?facture)\s+(\d+)",
                     text.strip())
        return {"factura_id": int(m.group(1))} if m else None

    def _parse_incasare(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:factura\s+(\d+)\s+(?:pl[ăa]tit[ăa]|pay[ée]e?)|"
                     r"facture\s+(\d+)\s+pay[ée]e?)\s*(?::\s*(\d+(?:[.,]\d+)?))?",
                     text.strip())
        if not m:
            return None
        fid = m.group(1) or m.group(2)
        suma = m.group(3)
        return {"factura_id": int(fid),
                "suma": float(suma.replace(",", ".")) if suma else 0}

    # --- Faza 4: produs, growth, risc ---
    def _parse_idee(self, text: str) -> dict | None:
        """'idee nouă: Titlu | descriere' / 'nouvelle idée : Titre'"""
        m = re.match(r"(?i)(?:idee\s+nou[ăa]|nouvelle\s+id[ée]e|id[ée]e\s+nouvelle)\s*:\s*(.+)$",
                     text.strip())
        if not m:
            return None
        parti = re.split(r"\s*\|\s*", m.group(1).strip(), maxsplit=1)
        return {"titlu": parti[0], "descriere": parti[1] if len(parti) > 1 else ""}

    def _parse_vot_idee(self, text: str) -> dict | None:
        """'votează ideea 2: 8' / 'noter l'idée 2 : 8'"""
        m = re.match(r"(?i)(?:voteaz[ăa]\s+(?:ideea\s+)?|noter\s+l['’]id[ée]e\s+)"
                     r"(\d+)\s*:\s*(\d+)", text.strip())
        return ({"idee_id": int(m.group(1)), "scor": int(m.group(2))}
                if m else None)

    def _parse_oportunitate(self, text: str) -> dict | None:
        """'oportunitate nouă: Titlu, investiție 5000, venit 800'"""
        m = re.match(r"(?i)(?:oportunitate\s+nou[ăa]|nouvelle\s+opportunit[ée])\s*:\s*(.+)$",
                     text.strip())
        if not m:
            return None
        rest = m.group(1).strip()
        inv = re.search(r"(?i)(?:investi[țt]ie|investissement)\s+(\d+(?:[.,]\d+)?)", rest)
        ven = re.search(r"(?i)(?:venit(?:\s+lunar)?|revenu(?:\s+mensuel)?)\s+(\d+(?:[.,]\d+)?)", rest)
        titlu = re.split(r",\s*(?:investi[țt]ie|investissement|venit|revenu)",
                         rest, maxsplit=1)[0].strip()
        return {"titlu": titlu,
                "investitie_estimata": float(inv.group(1).replace(",", ".")) if inv else 0.0,
                "venit_lunar_estimat": float(ven.group(1).replace(",", ".")) if ven else 0.0}

    def _parse_promoveaza(self, text: str) -> dict | None:
        """'promovează ideea 1: investiție 5000, venit 800'"""
        m = re.match(r"(?i)(?:promoveaz[ăa]\s+(?:ideea\s+)?|promouvoir\s+l['’]id[ée]e\s+)"
                     r"(\d+)\s*(?::\s*(.+))?$", text.strip())
        if not m:
            return None
        rest = (m.group(2) or "")
        inv = re.search(r"(?i)(?:investi[țt]ie|investissement)\s+(\d+(?:[.,]\d+)?)", rest)
        ven = re.search(r"(?i)(?:venit(?:\s+lunar)?|revenu(?:\s+mensuel)?)\s+(\d+(?:[.,]\d+)?)", rest)
        return {"idee_id": int(m.group(1)),
                "investitie_estimata": float(inv.group(1).replace(",", ".")) if inv else 0.0,
                "venit_lunar_estimat": float(ven.group(1).replace(",", ".")) if ven else 0.0}

    def _parse_aproba_oportunitate(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:aprob[ăa]\s+oportunitatea|approuver\s+l['’]opportunit[ée])\s+(\d+)",
                     text.strip())
        return {"oportunitate_id": int(m.group(1))} if m else None

    def _parse_investitie(self, text: str) -> dict | None:
        """'investiție nouă: Mașină nouă, cost 30000, venit 1500, tip masina'"""
        m = re.match(r"(?i)(?:investi[țt]ie\s+nou[ăa]|nouvel\s+investissement|"
                     r"investissement\s+nouveau)\s*:\s*(.+)$", text.strip())
        if not m:
            return None
        rest = m.group(1).strip()
        cost = re.search(r"(?i)(?:cost|co[ûu]t)\s+(\d+(?:[.,]\d+)?)", rest)
        ven = re.search(r"(?i)(?:venit(?:\s+lunar)?|revenu(?:\s+mensuel)?)\s+(\d+(?:[.,]\d+)?)", rest)
        tipm = re.search(r"(?i)(?:tip|type)\s+([a-zăâîșț]+)", rest)
        titlu = re.split(r",\s*(?:cost|co[ûu]t|venit|revenu|tip|type)",
                         rest, maxsplit=1)[0].strip()
        return {"titlu": titlu,
                "tip": tipm.group(1).lower() if tipm else "masina",
                "cost": float(cost.group(1).replace(",", ".")) if cost else 0.0,
                "venit_lunar_estimat": float(ven.group(1).replace(",", ".")) if ven else 0.0}

    def _parse_aproba_investitie(self, text: str) -> dict | None:
        m = re.match(r"(?i)(?:aprob[ăa]\s+investi[țt]ia|approuver\s+l['’]investissement)\s+(\d+)",
                     text.strip())
        return {"investitie_id": int(m.group(1))} if m else None

    def _parse_scenariu(self, text: str) -> dict | None:
        """'scenariu +20%' / 'scénario +20 %'"""
        m = re.match(r"(?i)(?:scenariu|sc[ée]nario)\s*\+?(\d+(?:[.,]\d+)?)\s*%",
                     text.strip())
        return {"crestere_pct": float(m.group(1).replace(",", "."))} if m else None

    def _parse_buget(self, text: str) -> dict | None:
        """'buget marketing: 500' / 'budget marketing : 500'"""
        m = re.match(r"(?i)(?:buget|budget)\s+([a-zăâîșț\s]+?)\s*:\s*(\d+(?:[.,]\d+)?)\s*$",
                     text.strip())
        if not m:
            return None
        return {"luna": date.today().strftime("%Y-%m"),
                "categorie": m.group(1).strip().lower(),
                "planificat": float(m.group(2).replace(",", "."))}

    def _parse_contract(self, text: str) -> dict | None:
        """'analizează contract: Nume | textul contractului'"""
        m = re.match(r"(?i)(?:analizeaz[ăa]\s+contract(?:ul)?|analyser\s+(?:le\s+)?contrat)"
                     r"\s*:\s*(.+)$", text.strip(), re.DOTALL)
        if not m:
            return None
        parti = re.split(r"\s*\|\s*", m.group(1).strip(), maxsplit=1)
        return {"nume": parti[0][:255],
                "text": parti[1] if len(parti) > 1 else parti[0]}

    def _parse_verificare(self, text: str) -> dict | None:
        """'verificare nouă: itp, B-123-ABC, 2027-01-15'"""
        m = re.match(r"(?i)(?:verificare\s+nou[ăa]|nouvelle\s+v[ée]rification)\s*:\s*(.+)$",
                     text.strip())
        if not m:
            return None
        parti = [p.strip() for p in m.group(1).split(",")]
        if len(parti) < 3:
            return None
        return {"tip": parti[0], "referinta": parti[1], "expira_la": parti[2],
                "notite": parti[3] if len(parti) > 3 else ""}

    def _parse_neregula(self, text: str) -> dict | None:
        """'neregulă: descriere, severitate ridicată'"""
        m = re.match(r"(?i)(?:neregul[ăa]|incident)\s*:\s*(.+)$", text.strip())
        if not m:
            return None
        rest = m.group(1).strip()
        sevm = re.search(r"(?i)severitate\s+(sc[ăa]zut[ăa]|medie|ridicat[ăa])", rest)
        sev = sevm.group(1).lower().replace("ă", "a") if sevm else "medie"
        sev = {"scazuta": "scazuta", "medie": "medie", "ridicata": "ridicata"}.get(sev, "medie")
        titlu = re.split(r",\s*severitate", rest, maxsplit=1)[0].strip()
        return {"titlu": titlu, "severitate": sev}

    # --- persistență conversații ---
    def _conversatie(self, utilizator: str, canal: str = "chat-intern") -> Conversation:
        db = SessionLocal()
        try:
            conv = (db.query(Conversation)
                      .filter_by(canal=canal, contact_ref=utilizator, stare="deschisa")
                      .first())
            if not conv:
                conv = Conversation(canal=canal, contact_ref=utilizator,
                                    titlu=f"{canal} — {utilizator}")
                db.add(conv)
                db.commit()
                db.refresh(conv)
            return conv
        finally:
            db.close()

    def _salveaza_mesaj(self, conv_id: int, directie: str, autor: str, text: str):
        db = SessionLocal()
        try:
            db.add(Message(conversation_id=conv_id, directie=directie, autor=autor, text=text[:4000]))
            db.commit()
        finally:
            db.close()

    # --- intrarea principală ---
    def proceseaza(self, text: str, utilizator: str = "valentin",
                   canal: str = "chat-intern", lang: str = "ro") -> str:
        text = (text or "").strip()
        if not text:
            return t("bot_necesita_text", lang)
        lang = lang if lang in ("ro", "fr") else "ro"

        conv = self._conversatie(utilizator, canal)
        self._salveaza_mesaj(conv.id, "in", utilizator, text)
        audit.inregistreaza(utilizator, "chat_mesaj", text[:200])

        tt = text.lower()
        exe = lambda agent, actiune, payload: self._executa_agent(  # noqa: E731
            agent, actiune, {**payload, "lang": lang}, utilizator)

        if tt in ("ajutor", "help", "aide", "?"):
            raspuns = t("bot_ajutor", lang)
        elif (pl := self._parse_lead(text)):
            raspuns = exe("vanzari", "creeaza_lead", pl)
        elif (pa := self._parse_activitate(text)):
            raspuns = exe("vanzari", "creeaza_activitate", pa)
        elif (pp := self._parse_produs(text)):
            p = catalog.adauga(pp["nume"], pp["pret"], sku=pp["sku"])
            audit.inregistreaza(utilizator, "catalog_adauga", f"#{p.id} {p.nume} — {p.pret} EUR")
            raspuns = t("bot_produs_adaugat", lang).format(nume=p.nume, pret=p.pret)
        elif tt.startswith(("catalog", "catalogue")):
            prods = catalog.lista()
            raspuns = (t("bot_catalog_gol", lang) if not prods else
                       t("bot_catalog_lista", lang).format(
                           linii="\n".join(f"• {p.nume} — {p.pret:.2f} EUR" for p in prods)))
        elif (po := self._parse_oferta(text)):
            po["contact_ref"] = utilizator
            raspuns = exe("vanzari", "cere_oferta", po)
        elif (pc := self._parse_califica(text)):
            raspuns = exe("vanzari", "califica_lead", pc)
        elif tt.startswith(("scor", "score")):
            raspuns = exe("vanzari", "scor_leaduri", {})
        elif (pz := self._parse_caz(text)):
            raspuns = exe("vanzari", "creeaza_caz", pz)
        elif (pq := self._parse_qa(text)):
            it = cunostinte.adauga(pq["intrebare"], pq["raspuns"])
            audit.inregistreaza(utilizator, "qa_adauga", f"#{it.id} {it.intrebare[:80]}")
            raspuns = t("bot_qa_invatat", lang).format(id=it.id)
        elif tt.startswith("pipeline"):
            pasi = pipeline.snapshot(self.crm)
            raspuns = (t("bot_pipeline_titlu", lang) + "\n" +
                       "\n".join(f"{p['pas']}. {p['nume']}: {p['count']}" for p in pasi))
        # --- Faza 2: dispecerat ---
        elif (pcu := self._parse_cursa(text)):
            pcu["sursa"] = canal
            raspuns = exe("operatiuni", "creeaza_cursa", pcu)
        elif (pat := self._parse_atribuie(text)):
            raspuns = exe("operatiuni", "atribuie_cursa", pat)
        elif (pst := self._parse_cursa_status(text)):
            raspuns = exe("operatiuni", "status_cursa", pst)
        elif tt.startswith(("curse azi", "courses aujourd")) or tt in ("dispecerat", "dispatch"):
            raspuns = self._text_curse_azi(lang)
        elif (ps := self._parse_sofer(text)):
            raspuns = exe("operatiuni", "adauga_sofer", ps)
        elif (pm := self._parse_masina(text)):
            raspuns = exe("operatiuni", "adauga_masina", pm)
        # --- Faza 2: marketing & competitori ---
        elif (ppt := self._parse_postare(text)):
            raspuns = exe("marketing", "creeaza_postare", ppt)
        elif (ppu := self._parse_publica(text)):
            ppt = {"canal": "instagram", "text": "", "cere_aprobare": True,
                   "_postare_existenta": ppu["postare_id"]}
            # publicarea unei postări existente: cerem aprobare direct
            from . import approvals, marketing
            from .db import SessionLocal as _S
            from .models import Postare as _P
            db = _S()
            try:
                post = db.query(_P).get(ppu["postare_id"])
                pid, pcanal, ptext = (post.id, post.canal, post.text) if post else (None, None, None)
            finally:
                db.close()
            if pid is None:
                raspuns = t("bot_postare_nu_exista", lang).format(id=ppu["postare_id"])
            else:
                ap = approvals.cere_aprobare(tip="postare_publica",
                    titlu=f"Publicare postare #{pid} ({pcanal})", detalii=ptext[:500],
                    solicitat_de=utilizator)
                db = _S()
                try:
                    db.query(_P).get(pid).approval_id = ap.id
                    db.commit()
                finally:
                    db.close()
                raspuns = t("bot_postare_aprobare", lang).format(id=pid, canal=pcanal, ap=ap.id)
        elif tt.startswith(("plan editorial", "plan éditorial")):
            raspuns = exe("marketing", "plan_editorial", {})
        elif (pco := self._parse_competitor(text)):
            raspuns = exe("research", "adauga_competitor", pco)
        elif (pob := self._parse_observatie(text)):
            raspuns = exe("research", "adauga_observatie", pob)
        # --- Faza 3: finanțe & BI ---
        elif (pfa := self._parse_factura(text)):
            raspuns = exe("finante", "creeaza_factura", pfa)
        elif (pem := self._parse_emite_factura(text)):
            raspuns = exe("finante", "emite_factura", pem)
        elif (ptr := self._parse_trimite_factura(text)):
            raspuns = exe("finante", "trimite_factura", ptr)
        elif (pin := self._parse_incasare(text)):
            raspuns = exe("finante", "marcheaza_platita", pin)
        elif tt.startswith(("facturi restante", "factures en retard", "factures impayées")):
            raspuns = exe("finante", "facturi_restante", {})
        elif tt.startswith(("sincronizeaz", "synchroniser")):
            raspuns = exe("finante", "sincronizeaza", {})
        elif tt.startswith(("incasari", "încasări", "encaissements")):
            raspuns = exe("finante", "rezumat", {})
        elif tt.startswith(("anomalii", "anomalies")):
            raspuns = exe("finante", "anomalii", {})
        # --- mod demonstrativ ---
        elif tt.startswith(("încarcă demo", "incarca demo", "charger la démo",
                             "charge la démo", "charger démo")):
            from . import demo as _demo
            rez = _demo.seed_demo()
            raspuns = (t("demo_bot_deja", lang) if rez.get("deja_activ")
                       else t("demo_bot_ok", lang).format(rez=rez))
        elif tt.startswith(("șterge demo", "sterge demo", "supprimer la démo",
                             "supprime la démo")):
            from . import demo as _demo
            sterse = _demo.sterge_demo()
            raspuns = t("demo_bot_sters", lang).format(n=sum(sterse.values()))
        # --- Faza 4: produs, growth, risc ---
        elif (pide := self._parse_idee(text)):
            raspuns = exe("produs", "idee_noua", pide)
        elif (pvot := self._parse_vot_idee(text)):
            raspuns = exe("produs", "voteaza_idee", pvot)
        elif tt.startswith(("idei", "idées")):
            raspuns = exe("produs", "lista_idei", {})
        elif (popn := self._parse_oportunitate(text)):
            raspuns = exe("produs", "oportunitate_noua", popn)
        elif (ppro := self._parse_promoveaza(text)):
            raspuns = exe("produs", "promoveaza_idee", ppro)
        elif (paop := self._parse_aproba_oportunitate(text)):
            raspuns = exe("produs", "aproba_oportunitate", paop)
        elif tt.startswith(("oportunități", "oportunitati", "opportunités")):
            raspuns = exe("produs", "lista_oportunitati", {})
        elif (pinv := self._parse_investitie(text)):
            raspuns = exe("growth", "evalueaza_investitie", pinv)
        elif (pain := self._parse_aproba_investitie(text)):
            raspuns = exe("growth", "aproba_investitie", pain)
        elif tt.startswith(("investiții", "investitii", "investissements")):
            raspuns = exe("growth", "lista_investitii", {})
        elif (psce := self._parse_scenariu(text)):
            raspuns = exe("growth", "scenariu", psce)
        elif (pbug := self._parse_buget(text)):
            raspuns = exe("growth", "seteaza_buget", pbug)
        elif tt.startswith(("buget", "budget")):
            raspuns = exe("growth", "buget", {})
        elif (pcon := self._parse_contract(text)):
            raspuns = exe("risc", "analizeaza_contract", pcon)
        elif (pver := self._parse_verificare(text)):
            raspuns = exe("risc", "verificare_noua", pver)
        elif tt.startswith(("verificări", "verificari", "vérifications")):
            raspuns = exe("risc", "verificari", {})
        elif (pner := self._parse_neregula(text)):
            raspuns = exe("risc", "semnaleaza_neregula", pner)
        elif tt.startswith(("nereguli",)):
            raspuns = exe("risc", "lista_nereguli", {})
        elif tt.startswith(("raport zilnic", "rapport quotidien", "rapport journalier",
                             "dashboard", "tableau de bord")):
            raspuns = exe("bi", "dashboard", {})
        elif tt.startswith(("analizează semnale", "analizeaza semnale",
                             "analyse les signaux")):
            raspuns = exe("hermes", "analizeaza", {})
        elif tt.startswith(("sugestii", "suggestions")):
            raspuns = exe("hermes", "sugestii", {})
        elif (m := re.match(r"(?:aprobă|aproba) sugestia (\d+)", tt)) or \
                (m := re.match(r"approuver la suggestion (\d+)", tt)):
            raspuns = exe("hermes", "decide_sugestie",
                          {"id": int(m.group(1)), "decizie": "aprobata"})
        elif (m := re.match(r"respinge sugestia (\d+)", tt)) or \
                (m := re.match(r"rejeter la suggestion (\d+)", tt)):
            raspuns = exe("hermes", "decide_sugestie",
                          {"id": int(m.group(1)), "decizie": "respinsa"})
        elif (m := re.match(r"(?:aplică|aplica) sugestia (\d+)", tt)) or \
                (m := re.match(r"appliquer la suggestion (\d+)", tt)):
            raspuns = exe("hermes", "aplica_sugestie", {"id": int(m.group(1))})
        elif tt in ("hermes", "hermès"):
            raspuns = exe("hermes", "raport", {})
        else:
            qa = cunostinte.cauta(text)
            if qa:
                raspuns = qa.raspuns
                audit.inregistreaza("jarvis", "qa_raspuns", qa.intrebare[:120])
            elif any(c in tt for c in _CUVINTE_PROBLEMA):
                raspuns = exe("vanzari", "creeaza_caz",
                              {"subject": text[:120],
                               "description": f"Raportat de {utilizator} ({canal}): {text[:500]}",
                               "priority": "medie"})
            else:
                agent_key = self.clasifica(text)
                raspuns = exe(agent_key, "mesaj_utilizator", {"text": text})

        self._salveaza_mesaj(conv.id, "out", "jarvis", raspuns)
        return raspuns

    def _text_curse_azi(self, lang: str) -> str:
        curse = dispecerat.curse_pe_zi(date.today())
        if not curse:
            return t("bot_curse_azi_gol", lang)
        linii = []
        for c in curse:
            ora = c.data_ora.strftime("%H:%M") if c.data_ora else "—"
            extra = f" · {c.sofer.nume}" if c.sofer_id and c.sofer else ""
            linii.append(f"#{c.id} {ora} {c.client_nume}: {c.preluare} → {c.destinatie} "
                         f"[{t('st_' + c.status, lang)}]{extra}")
        return t("bot_curse_azi_titlu", lang) + "\n" + "\n".join(linii)

    def proceseaza_canal(self, text: str, utilizator: str, canal: str,
                         lang: str = "ro") -> str:
        """Procesare mesaje de pe canale externe — mod conservator."""
        qa = cunostinte.cauta(text)
        if qa:
            audit.inregistreaza(canal, "qa_raspuns", qa.intrebare[:120])
            return qa.raspuns
        pl = self._parse_lead(text)
        if pl:
            try:
                rez = self.agenti["vanzari"].ruleaza("creeaza_lead", {**pl, "lang": lang},
                                                     solicitat_de=canal)
                return rez.get("mesaj", "") + t("bot_canal_lead", lang)
            except Exception:
                pass
        # rezervare cursă de pe canal extern → cursă rezervată, fără atribuire automată
        pcu = self._parse_cursa(text)
        if pcu:
            try:
                pcu["sursa"] = canal
                pcu["lang"] = lang
                rez = self.agenti["operatiuni"].ruleaza("creeaza_cursa", pcu, solicitat_de=canal)
                return rez.get("mesaj", "") + " " + t("bot_canal_confirmare", lang)
            except Exception:
                pass
        if any(c in text.lower() for c in _CUVINTE_PROBLEMA):
            try:
                rez = self.agenti["vanzari"].ruleaza(
                    "creeaza_caz", {**{"subject": text[:120],
                     "description": f"De pe {canal}, de la {utilizator}: {text[:500]}"},
                     "lang": lang}, solicitat_de=canal)
                return "Am înregistrat sesizarea ta " + rez.get("mesaj", "")
            except Exception:
                pass
        self.agenti["vanzari"].ruleaza("mesaj_utilizator",
                                       {"text": text, "canal": canal, "de_la": utilizator},
                                       solicitat_de=canal)
        return t("bot_canal_necunoscut", lang)

    def _executa_agent(self, agent_key: str, actiune: str, payload: dict, utilizator: str) -> str:
        agent = self.agenti.get(agent_key)
        if not agent:
            return f"Nu cunosc agentul «{agent_key}»."
        rezultat = agent.ruleaza(actiune, payload, solicitat_de=utilizator)
        return rezultat.get("mesaj", "Gata.")
