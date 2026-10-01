"""Oferte: calcul linii + TVA, numerotare, generare PDF."""
import json
import os
from datetime import datetime, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors

from . import catalog, config
from .db import SessionLocal
from .models import Offer

_FONT = "DejaVuSans"
_FONT_BOLD = "DejaVuSans-Bold"
try:
    pdfmetrics.registerFont(TTFont(_FONT, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont(_FONT_BOLD, "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
except Exception:
    _FONT, _FONT_BOLD = "Helvetica", "Helvetica-Bold"


def calculeaza(linii: list[dict], tva_procent: float | None = None) -> dict:
    """linii: [{produs, cantitate, pret, discount(%)}]. Întoarce subtotal/tva/total."""
    tva_rata = config.TVA_DEFAULT if tva_procent is None else tva_procent
    randuri, subtotal = [], 0.0
    for l in linii:
        cant = float(l.get("cantitate", 1) or 1)
        pret = float(l.get("pret", 0) or 0)
        disc = float(l.get("discount", 0) or 0)
        net = cant * pret * (1 - disc / 100)
        subtotal += net
        randuri.append({**l, "cantitate": cant, "pret": pret,
                        "discount": disc, "valoare": round(net, 2)})
    tva = subtotal * tva_rata
    return {"linii": randuri, "subtotal": round(subtotal, 2),
            "tva": round(tva, 2), "total": round(subtotal + tva, 2),
            "tva_procent": round(tva_rata * 100, 1)}


def numar_nou() -> str:
    an = datetime.now().year
    db = SessionLocal()
    try:
        n = db.query(Offer).filter(Offer.numar.like(f"OF-{an}-%")).count() + 1
        return f"OF-{an}-{n:04d}"
    finally:
        db.close()


def creeaza_ciorna(client_nume: str, linii: list[dict], contact_ref: str = "",
                   valabilitate_zile: int = 30, opportunity_id: int | None = None) -> Offer:
    calc = calculeaza(linii)
    db = SessionLocal()
    try:
        of = Offer(numar=numar_nou(), client_nume=client_nume.strip(),
                   contact_ref=contact_ref, opportunity_id=opportunity_id,
                   linii=json.dumps(calc["linii"], ensure_ascii=False),
                   subtotal=calc["subtotal"], tva=calc["tva"], total=calc["total"],
                   valabilitate_zile=valabilitate_zile)
        db.add(of)
        db.commit()
        db.refresh(of)
        return of
    finally:
        db.close()


def genereaza_pdf(oferta_id: int) -> str:
    """Generează PDF-ul ofertei și actualizează înregistrarea. Întoarce calea."""
    db = SessionLocal()
    try:
        of = db.query(Offer).get(oferta_id)
        if not of:
            raise ValueError("Oferta nu există.")
        linii = json.loads(of.linii or "[]")
        os.makedirs(config.OFERTE_DIR, exist_ok=True)
        cale = os.path.join(config.OFERTE_DIR, f"{of.numar}.pdf")

        stil = ParagraphStyle("n", fontName=_FONT, fontSize=10, leading=14)
        stil_b = ParagraphStyle("b", fontName=_FONT_BOLD, fontSize=10, leading=14)
        stil_h = ParagraphStyle("h", fontName=_FONT_BOLD, fontSize=16, leading=20)

        el = [Paragraph(f"Ofertă {of.numar}", stil_h), Spacer(1, 6 * mm),
              Paragraph(f"Client: {of.client_nume or '—'}", stil),
              Paragraph(f"Data: {of.created_at.strftime('%d.%m.%Y')}", stil),
              Paragraph(f"Valabilitate: {of.valabilitate_zile} zile "
                        f"(până la {(of.created_at + timedelta(days=of.valabilitate_zile)).strftime('%d.%m.%Y')})", stil),
              Spacer(1, 6 * mm)]

        tabel = [[Paragraph("<b>Produs / Serviciu</b>", stil_b), Paragraph("<b>Cant.</b>", stil_b),
                  Paragraph("<b>Preț</b>", stil_b), Paragraph("<b>Disc. %</b>", stil_b),
                  Paragraph("<b>Valoare</b>", stil_b)]]
        for l in linii:
            tabel.append([Paragraph(str(l.get("produs", "")), stil),
                          str(l.get("cantitate", "")), f"{l.get('pret', 0):.2f}",
                          str(l.get("discount", 0)), f"{l.get('valoare', 0):.2f}"])
        t = Table(tabel, colWidths=[80 * mm, 18 * mm, 25 * mm, 20 * mm, 30 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        el += [t, Spacer(1, 6 * mm),
               Paragraph(f"Subtotal: {of.subtotal:.2f} EUR", stil),
               Paragraph(f"TVA: {of.tva:.2f} EUR", stil),
               Paragraph(f"<b>Total: {of.total:.2f} EUR</b>", stil_b),
               Spacer(1, 10 * mm),
               Paragraph("Document generat de Jarvis. Oferta e valabilă în perioada menționată.", stil)]

        SimpleDocTemplate(cale, pagesize=A4,
                          leftMargin=20 * mm, rightMargin=20 * mm).build(el)
        of.fisier_pdf = cale
        of.stare = "aprobata" if of.stare == "ciorna" else of.stare
        db.commit()
        return cale
    finally:
        db.close()


def marcheaza_trimisa(oferta_id: int, canal: str = "") -> bool:
    db = SessionLocal()
    try:
        of = db.query(Offer).get(oferta_id)
        if not of:
            return False
        of.stare = "trimisa"
        db.commit()
        return True
    finally:
        db.close()


def lista_oferte():
    db = SessionLocal()
    try:
        return db.query(Offer).order_by(Offer.id.desc()).limit(100).all()
    finally:
        db.close()
