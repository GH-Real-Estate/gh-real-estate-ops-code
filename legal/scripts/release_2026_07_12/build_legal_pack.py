#!/usr/bin/env python3
"""Build searchable, bookmarked GH Real Estate legal-source PDFs.

Official source PDFs are concatenated without editing their legal text.  Each
bundle receives a dated cover, use instructions, a source inventory, exact page
ranges, authority labels, and bookmarks.
"""

from __future__ import annotations

import hashlib
import html as html_lib
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    LongTable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "tmp/pdfs/source_downloads"
OUT = ROOT / "output/pdf"
AS_OF = "July 12, 2026"
AS_OF_ISO = "2026-07-12"
PROPERTY = "9401 Nieman Road, Overland Park, Kansas 66214"

NAVY = colors.HexColor("#15263C")
BLUE = colors.HexColor("#285778")
GOLD = colors.HexColor("#C9A657")
PALE = colors.HexColor("#EDF2F5")
PALE_GOLD = colors.HexColor("#F6F0E1")
INK = colors.HexColor("#17212B")
GRAY = colors.HexColor("#66737F")
RED = colors.HexColor("#A43C3C")
GREEN = colors.HexColor("#2D6A4F")


def register_fonts() -> None:
    regular = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    pdfmetrics.registerFont(TTFont("GH", regular))
    pdfmetrics.registerFont(TTFont("GH-Bold", bold))


register_fonts()


def esc(value: object) -> str:
    return html_lib.escape(str(value), quote=True)


def styles():
    s = getSampleStyleSheet()
    s.add(
        ParagraphStyle(
            "CoverEyebrow",
            fontName="GH-Bold",
            fontSize=10,
            leading=13,
            textColor=GOLD,
            alignment=TA_CENTER,
            spaceAfter=14,
            tracking=1.3,
        )
    )
    s.add(
        ParagraphStyle(
            "CoverTitle",
            fontName="GH-Bold",
            fontSize=25,
            leading=30,
            textColor=colors.white,
            alignment=TA_CENTER,
            spaceAfter=16,
        )
    )
    s.add(
        ParagraphStyle(
            "CoverSub",
            fontName="GH",
            fontSize=10.5,
            leading=15,
            textColor=colors.white,
            alignment=TA_CENTER,
        )
    )
    s.add(
        ParagraphStyle(
            "H1x",
            fontName="GH-Bold",
            fontSize=18,
            leading=23,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=10,
        )
    )
    s.add(
        ParagraphStyle(
            "H2x",
            fontName="GH-Bold",
            fontSize=12.5,
            leading=16,
            textColor=BLUE,
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    s.add(
        ParagraphStyle(
            "H3x",
            fontName="GH-Bold",
            fontSize=9.5,
            leading=12,
            textColor=NAVY,
            spaceBefore=7,
            spaceAfter=3,
        )
    )
    s.add(
        ParagraphStyle(
            "Bodyx",
            fontName="GH",
            fontSize=8.7,
            leading=12.4,
            textColor=INK,
            spaceAfter=6,
        )
    )
    s.add(
        ParagraphStyle(
            "Smallx",
            fontName="GH",
            fontSize=7.2,
            leading=9.4,
            textColor=INK,
        )
    )
    s.add(
        ParagraphStyle(
            "Tinyx",
            fontName="GH",
            fontSize=6.2,
            leading=7.8,
            textColor=INK,
            wordWrap="CJK",
        )
    )
    s.add(
        ParagraphStyle(
            "Notex",
            fontName="GH",
            fontSize=8.2,
            leading=11.5,
            textColor=NAVY,
            leftIndent=9,
            rightIndent=9,
            borderColor=GOLD,
            borderWidth=0.8,
            borderPadding=7,
            backColor=PALE_GOLD,
            spaceBefore=5,
            spaceAfter=8,
        )
    )
    s.add(
        ParagraphStyle(
            "Warningx",
            fontName="GH-Bold",
            fontSize=8.2,
            leading=11.5,
            textColor=RED,
            leftIndent=9,
            rightIndent=9,
            borderColor=RED,
            borderWidth=0.8,
            borderPadding=7,
            backColor=colors.HexColor("#FBECEC"),
            spaceBefore=5,
            spaceAfter=8,
        )
    )
    return s


S = styles()


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.6)
    canvas.line(0.65 * inch, 0.48 * inch, 7.85 * inch, 0.48 * inch)
    canvas.setFont("GH", 6.8)
    canvas.setFillColor(GRAY)
    canvas.drawString(0.65 * inch, 0.29 * inch, f"GH Legal Source Pack • Current through {AS_OF}")
    canvas.drawRightString(7.85 * inch, 0.29 * inch, f"Front matter page {doc.page}")
    canvas.restoreState()


def p(text: str, style="Bodyx") -> Paragraph:
    return Paragraph(text, S[style])


def bullet(text: str, style="Bodyx") -> Paragraph:
    return Paragraph(f"• {text}", S[style])


def section_heading(text: str) -> list:
    return [p(esc(text), "H1x"), HRFlowable(width="100%", thickness=1.2, color=GOLD, spaceAfter=8)]


def doc(path: Path, title: str) -> SimpleDocTemplate:
    return SimpleDocTemplate(
        str(path),
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.62 * inch,
        bottomMargin=0.62 * inch,
        title=title,
        author="GH Real Estate LLC",
        subject=f"Legal source compilation current through {AS_OF}",
    )


def cover_flow(title: str, subtitle: str, scope: str) -> list:
    banner = Table(
        [[p("GH REAL ESTATE • LEGAL SOURCE PACK", "CoverEyebrow")],
         [p(esc(title), "CoverTitle")],
         [p(esc(subtitle), "CoverSub")]],
        colWidths=[7.2 * inch],
        rowHeights=[0.8 * inch, 2.15 * inch, 1.0 * inch],
    )
    banner.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), NAVY),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 0.8, GOLD),
                ("LEFTPADDING", (0, 0), (-1, -1), 24),
                ("RIGHTPADDING", (0, 0), (-1, -1), 24),
            ]
        )
    )
    status = Table(
        [
            [p("PROPERTY", "Tinyx"), p(esc(PROPERTY), "Smallx")],
            [p("CURRENT THROUGH", "Tinyx"), p(AS_OF, "Smallx")],
            [p("ACTIVE-SET STATUS", "Tinyx"), p("Current-law set; enacted addenda included; withdrawn sources excluded", "Smallx")],
            [p("SCOPE", "Tinyx"), p(esc(scope), "Smallx")],
        ],
        colWidths=[1.35 * inch, 5.75 * inch],
    )
    status.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), PALE),
                ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#BCC8CF")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return [
        Spacer(1, 0.42 * inch),
        banner,
        Spacer(1, 0.36 * inch),
        status,
        Spacer(1, 0.28 * inch),
        p(
            "<b>Use rule:</b> Retrieve the controlling text, confirm the trigger and currentness, then obtain Kansas counsel review before enforcement, filing, denial, accommodation decisions, or material lease changes.",
            "Notex",
        ),
        p(
            "This compilation is a research and retrieval aid, not legal advice, a title opinion, or a substitute for official current law. Summaries and applicability labels are navigation aids; the appended official text controls.",
            "Smallx",
        ),
        PageBreak(),
    ]


def authority_legend() -> Table:
    rows = [
        [p("LABEL", "Tinyx"), p("HOW TO USE IT", "Tinyx")],
        [p("BINDING", "Smallx"), p("Statute, regulation, ordinance, or controlling court decision. Confirm effective date and later history.", "Smallx")],
        [p("CONDITIONAL", "Smallx"), p("Binding only when a stated trigger exists—such as HUD assistance, a federally backed mortgage, or third-party management.", "Smallx")],
        [p("GUIDANCE", "Smallx"), p("Agency or court-administration material. Useful operationally but not itself controlling law unless incorporated.", "Smallx")],
        [p("PROPOSED", "Smallx"), p("Monitoring only. Do not apply as current law.", "Smallx")],
        [p("WITHDRAWN", "Smallx"), p("Excluded from this active set. Keep only in a separately labeled historical archive.", "Smallx")],
    ]
    t = Table(rows, colWidths=[1.15 * inch, 5.95 * inch], repeatRows=1)
    t.setStyle(table_style())
    return t


def table_style() -> TableStyle:
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "GH-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#BCC8CF")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
    )


def natural_key(value: str):
    return [int(x) if x.isdigit() else x.lower() for x in re.split(r"(\d+)", value)]


def enrich_record(record: dict) -> dict:
    rec = dict(record)
    path = ROOT / rec["local_path"]
    if not path.exists():
        raise FileNotFoundError(path)
    data = path.read_bytes()
    rec.setdefault("sha256", hashlib.sha256(data).hexdigest())
    rec.setdefault("bytes", len(data))
    rec.setdefault("pages", len(PdfReader(path).pages))
    rec.setdefault("authority", "Official source")
    rec.setdefault("applicability", "See master applicability index")
    rec.setdefault("citation", rec.get("tocid") or path.stem)
    rec.setdefault("title", path.stem.replace("_", " "))
    rec.setdefault("official_url", rec.get("source_url", ""))
    rec.setdefault("group", "official_sources")
    return rec


def make_front_matter(
    path: Path,
    title: str,
    subtitle: str,
    scope: str,
    notes: list[str],
    records: list[dict],
    start_page: int | None,
) -> int:
    story = cover_flow(title, subtitle, scope)
    story += section_heading("How this bundle should be used")
    story.append(authority_legend())
    story.append(Spacer(1, 0.12 * inch))
    for note in notes:
        story.append(bullet(esc(note)))
    story.append(
        p(
            "<b>Text-integrity rule:</b> appended official PDFs are preserved as retrieved. The front matter adds navigation only and does not alter statutory, regulatory, judicial, or municipal wording.",
            "Notex",
        )
    )
    story.append(PageBreak())
    story += section_heading("Source inventory and page map")
    story.append(
        p(
            f"{len(records)} official source documents are included. Page numbers below refer to the finished merged PDF. Use the PDF bookmarks or search the exact citation.",
            "Bodyx",
        )
    )
    rows = [[p("#", "Tinyx"), p("CITATION / SOURCE", "Tinyx"), p("TITLE", "Tinyx"), p("PAGES", "Tinyx")]]
    cursor = start_page
    for i, rec in enumerate(records, 1):
        if cursor is None:
            page_text = "pending"
        else:
            last = cursor + rec["pages"] - 1
            page_text = str(cursor) if last == cursor else f"{cursor}–{last}"
            cursor = last + 1
        rows.append(
            [
                p(str(i), "Tinyx"),
                p(esc(rec["citation"]), "Tinyx"),
                p(esc(rec["title"]), "Tinyx"),
                p(page_text, "Tinyx"),
            ]
        )
    inventory = LongTable(rows, colWidths=[0.28 * inch, 1.7 * inch, 4.55 * inch, 0.57 * inch], repeatRows=1)
    inventory.setStyle(table_style())
    story.append(inventory)
    story.append(Spacer(1, 0.15 * inch))
    story.append(
        p(
            "Source URLs, retrieval date, authority/applicability labels, and SHA-256 fingerprints are recorded in the companion Markdown manifest.",
            "Smallx",
        )
    )
    d = doc(path, title)
    d.build(story, onFirstPage=footer, onLaterPages=footer)
    return len(PdfReader(path).pages)


def merge_bundle(
    output: Path,
    title: str,
    subtitle: str,
    scope: str,
    notes: list[str],
    records: Iterable[dict],
) -> dict:
    recs = [enrich_record(r) for r in records]
    if recs and all("/federal/" in r["local_path"] for r in recs):
        recs.sort(key=lambda r: natural_key(Path(r["local_path"]).name))
    else:
        recs.sort(
            key=lambda r: (
                natural_key(r.get("group", "")),
                natural_key(r["citation"].replace(",", "999")),
            )
        )
    temp = OUT / f".{output.stem}_front.pdf"
    front_pages = make_front_matter(temp, title, subtitle, scope, notes, recs, None)
    for _ in range(3):
        new_pages = make_front_matter(temp, title, subtitle, scope, notes, recs, front_pages + 1)
        if new_pages == front_pages:
            break
        front_pages = new_pages

    writer = PdfWriter()
    front = PdfReader(temp)
    for page in front.pages:
        writer.add_page(page)
    writer.add_outline_item("Front matter and source index", 0)

    parents = {}
    source_ranges = []
    for rec in recs:
        start = len(writer.pages)
        reader = PdfReader(ROOT / rec["local_path"])
        for page in reader.pages:
            # The 2026 HUD assistance-animal memo's public-mirror PDF contains
            # broken hyperlink annotation references.  Strip only those
            # non-substantive annotations so the merged active source remains
            # structurally clean; text and page images are unchanged.
            if rec["local_path"].endswith(
                "14_HUD_2026_Assistance_Animal_Enforcement_Guidance.pdf"
            ):
                page.pop(NameObject("/Annots"), None)
            writer.add_page(page)
        group = rec.get("group", "official_sources")
        if group not in parents:
            parents[group] = writer.add_outline_item(group.replace("_", " ").title(), start)
        writer.add_outline_item(
            f"{rec['citation']} — {rec['title']}", start, parent=parents[group]
        )
        source_ranges.append({**rec, "bundle_start_page": start + 1, "bundle_end_page": len(writer.pages)})

    writer.add_metadata(
        {
            "/Title": title,
            "/Author": "GH Real Estate LLC",
            "/Subject": f"Official legal source compilation current through {AS_OF}",
            "/Keywords": "Kansas landlord tenant fair housing HUD Overland Park real estate",
            "/GHAsOf": AS_OF_ISO,
        }
    )
    writer.page_mode = "/UseOutlines"
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as fh:
        writer.write(fh)
    temp.unlink(missing_ok=True)
    data = output.read_bytes()
    return {
        "filename": output.name,
        "title": title,
        "pages": len(PdfReader(output).pages),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "sources": source_ranges,
    }


def issue_map_table() -> Table:
    data = [
        ("Lease terms, deposits, duties, entry, remedies", "GH-KS-01", "K.S.A. 58-2540–2573; Article 25 source text"),
        ("Notice, eviction, court process", "GH-KS-02", "K.S.A. 61 procedure + 2026 HB 2357 + current cases"),
        ("State protected classes / local civil rights", "GH-KS-02 + GH-OP-01", "K.S.A. 44-1015–1029; OPMC 8.10"),
        ("Federal fair housing / advertising", "GH-FED-01", "42 U.S.C. ch. 45; 24 CFR Parts 100, 103, 110"),
        ("Assistance animals / accommodations", "GH-FED-01", "42 U.S.C. 3604(f); 24 CFR 100.204; 2026 HUD memo is guidance"),
        ("Lead disclosure / renovation", "GH-FED-02 + GH-KS-02", "Pre-1978 trigger; EPA/HUD/KDHE sources"),
        ("Screening / adverse action / tenant data", "GH-FED-02 + GH-KS-02", "FCRA, Disposal Rule, Kansas credit/data law"),
        ("Military, bankruptcy, foreclosure, CARES", "GH-FED-02", "Trigger-specific federal overlays"),
        ("Voucher / HUD-assisted / VAWA / Section 504", "GH-FED-03", "Conditional on verified program/mortgage/assistance facts"),
        ("Rental license / inspection / property upkeep", "GH-OP-01", "OPMC 5.75 and Title 7 chapters"),
        ("Fire, building systems, zoning, parking", "GH-OP-02", "OPMC Titles 16 and 18; base ICC text incorporated separately"),
    ]
    rows = [[p("ISSUE", "Tinyx"), p("START WITH", "Tinyx"), p("PRIMARY AUTHORITY", "Tinyx")]]
    for a, b, c in data:
        rows.append([p(esc(a), "Smallx"), p(esc(b), "Smallx"), p(esc(c), "Smallx")])
    t = LongTable(rows, colWidths=[2.55 * inch, 1.35 * inch, 3.2 * inch], repeatRows=1)
    t.setStyle(table_style())
    return t


def property_trigger_table() -> Table:
    data = [
        ("Four dwelling units", "Verified in project profile", "Apply FHA/Kansas fair housing conservatively; do not assume owner-occupied small-property exemption."),
        ("LLC ownership", "Verified", "Owner-occupancy exemption analysis is not established; counsel should confirm."),
        ("Construction year", "Public sources report 1963; official county record not yet verified", "Treat federal/Kansas lead disclosure and renovation rules as active until official verification."),
        ("Rental license", "Direct city requirement", "Confirm current Overland Park license and inspection status."),
        ("Federally backed mortgage", "Unknown", "Controls CARES Act covered-property analysis and may affect HUD equal-access rules."),
        ("Voucher / HUD assistance", "Unknown", "Controls HCV addendum, VAWA, Section 504, Title VI, HUD lead-safe rules and other program duties."),
        ("Owner versus third-party manager", "GH manages its property; future third-party services unknown", "Kansas broker/property-management licensing can become active for compensated third-party management."),
        ("Property zoning / lawful occupancy", "R-3 appears plausible but not verified to parcel", "Verify official parcel zoning and any lawful nonconforming status before relying on zoning excerpts."),
    ]
    rows = [[p("TRIGGER", "Tinyx"), p("STATUS", "Tinyx"), p("LEGAL EFFECT", "Tinyx")]]
    for a, b, c in data:
        rows.append([p(esc(a), "Smallx"), p(esc(b), "Smallx"), p(esc(c), "Smallx")])
    t = LongTable(rows, colWidths=[1.55 * inch, 2.05 * inch, 3.5 * inch], repeatRows=1)
    t.setStyle(table_style())
    return t


def master_pdf(path: Path, bundle_summaries: list[dict]) -> None:
    story = cover_flow(
        "MASTER AUTHORITY INDEX",
        "Applicability map • currentness register • update protocol",
        "Kansas residential operations, federal/HUD overlays, and Overland Park municipal law relevant to GH’s fourplex",
    )
    story += section_heading("Executive use instructions")
    story.append(
        p(
            "This is the controlling navigation document for the active project-source set. Begin here, identify the issue and trigger, then open the cited source bundle. A source’s presence does not mean every provision applies to every event.",
            "Bodyx",
        )
    )
    for text in [
        "Prefer current binding statutes, regulations, ordinances and controlling decisions over summaries or agency guidance.",
        "Treat proposed rules as monitoring only and withdrawn guidance as historical only.",
        "For notices, evictions, denials, adverse action, accommodation decisions, deposit deductions, fee enforcement or filings, verify the exact current text and obtain Kansas counsel review.",
        "Never blend a superseded version with current wording. Effective-but-not-yet-codified session laws travel as explicit addenda.",
    ]:
        story.append(bullet(esc(text)))
    story.append(authority_legend())
    story.append(PageBreak())

    story += section_heading("Property applicability and unresolved triggers")
    story.append(property_trigger_table())
    story.append(
        p(
            "<b>Conservative default:</b> unless counsel verifies an exemption, act as though federal and Kansas fair-housing duties apply fully. Do not rely on a four-unit exemption without proof of the required owner occupancy and entity analysis.",
            "Warningx",
        )
    )
    story.append(PageBreak())

    story += section_heading("Issue-to-source map")
    story.append(issue_map_table())
    story.append(Spacer(1, 0.16 * inch))
    story.append(
        p(
            "Search tip: query an exact citation first (for example, “58-2550,” “24 CFR 100.204,” or “OPMC 5.75”), then search the operational concept.",
            "Notex",
        )
    )

    story += section_heading("Currentness register — material 2026 changes")
    current_rows = [
        [p("SOURCE", "Tinyx"), p("CURRENTNESS / CHANGE", "Tinyx"), p("ACTIVE-SET TREATMENT", "Tinyx")],
        [p("Kansas statutes", "Smallx"), p("Official 2026 pages retrieved July 12, 2026; some displayed eviction sections still require session-law overlays.", "Smallx"), p("Current consolidated PDFs + HB 2357 and SB 391 enrolled PDFs.", "Smallx")],
        [p("HB 2357", "Smallx"), p("Effective July 1, 2026: eviction-record expungement and mediation provisions.", "Smallx"), p("Binding enacted addendum; do not use earlier bill versions.", "Smallx")],
        [p("SB 391", "Smallx"), p("Effective July 1, 2026 after veto override: specified local voucher/screening/deposit/right-of-first-refusal preemption.", "Smallx"), p("Binding state-local overlay; federal/state fair housing and FCRA still control.", "Smallx")],
        [p("eCFR", "Smallx"), p("Federal regulation snapshot dated July 9, 2026.", "Smallx"), p("Binding current regulation text in federal bundles.", "Smallx")],
        [p("HUD guidance withdrawals", "Smallx"), p("91 FR 17291 (Apr. 6, 2026) records withdrawal of listed FHEO guidance effective Sept. 17, 2025.", "Smallx"), p("Withdrawn items excluded from active authority; withdrawal notice retained.", "Smallx")],
        [p("Assistance animals", "Smallx"), p("HUD memo dated May 22, 2026 is enforcement guidance, not a rule.", "Smallx"), p("Label GUIDANCE. Statute, 24 CFR 100.204, precedent and private rights remain controlling.", "Smallx")],
        [p("Disparate impact", "Smallx"), p("24 CFR 100.500 remains in force; Jan. 2026 removal is proposed only.", "Smallx"), p("Current regulation retained; proposal excluded from operative authority.", "Smallx")],
        [p("HUD equal access", "Smallx"), p("24 CFR 5.105(a)(2) remains current; 2026 revisions are proposed only.", "Smallx"), p("Conditional on HUD-assisted or HUD-insured housing trigger.", "Smallx")],
        [p("Overland Park codes", "Smallx"), p("Official city exports retrieved July 12, 2026; city adopted the 2024 International Code package in 2026.", "Smallx"), p("Local amendments included. Copyrighted ICC base texts are incorporated but not reproduced.", "Smallx")],
    ]
    ct = LongTable(current_rows, colWidths=[1.25 * inch, 3.25 * inch, 2.6 * inch], repeatRows=1)
    ct.setStyle(table_style())
    story.append(ct)
    story.append(PageBreak())

    story += section_heading("GH-specific high-priority legal review queue")
    risks = [
        ("Fee policy and lease mismatch", "The project policy can total 25% of monthly rent in staged late fees plus 12% simple annual interest, while current signed leases may contain an older schedule. No source in this pack validates that structure. Review under K.S.A. 58-2544, 58-2547 and applicable consumer/unconscionability law before enforcement; Schutt v. Foster is not blanket approval."),
        ("Default / cure / eviction notices", "Kansas timing, content, service and court-process rules are exacting. McConnell requires a 14/30 notice to identify curable acts or omissions with sufficient specificity. Do not use self-help or rely only on email/e-sign delivery."),
        ("Lead", "Public sources report a 1963 build, making federal disclosure and renovation rules likely direct. Verify official year, keep signed disclosures/pamphlet acknowledgments, and use certified firms/renovators where required."),
        ("Fair housing poster", "24 CFR Part 110 generally requires display at covered property and places of business. Verify and post the current HUD-928.1 poster."),
        ("Assistance animals", "The May 2026 HUD memo changes enforcement posture but does not rewrite the FHA or 24 CFR 100.204. Use an individualized accommodation process; obtain counsel for denials or disputed documentation."),
        ("Federal-program status", "Determine mortgage backing and whether any unit participates in HCV or another HUD program. This changes CARES, VAWA, Section 504, Title VI, lead-safe housing and form/addendum duties."),
        ("Fire / grill policy", "Overland Park’s adopted fire-code package and amendments may constrain open-flame cooking at a fourplex. Compare the lease policy with the current code and obtain fire-official/counsel confirmation; the proprietary ICC base text is not reproduced here."),
        ("Sensitive application data", "Use federal and Kansas screening/adverse-action rules; retain only what is needed and securely destroy consumer-report and personal-information records."),
    ]
    risk_rows = [[p("PRIORITY", "Tinyx"), p("REVIEW POINT", "Tinyx")]]
    for a, b in risks:
        risk_rows.append([p(esc(a), "Smallx"), p(esc(b), "Smallx")])
    rt = LongTable(risk_rows, colWidths=[1.65 * inch, 5.45 * inch], repeatRows=1)
    rt.setStyle(table_style())
    story.append(rt)
    story.append(PageBreak())

    story += section_heading("Withdrawn, proposed and historical material")
    story.append(
        p(
            "The following are intentionally not treated as current operative authority: HUD’s 2013/2020 assistance-animal notices; 2007 LEP guidance; 2016 criminal-record and LEP guidance; the 2022 criminal-record implementation memo; the 2021 sexual-orientation/gender-identity enforcement memo; the 2016 HUD/DOJ land-use statement; 2024 digital-advertising guidance; and 2024 source-of-income testing memorandum. The April 2026 Federal Register withdrawal notice is included to document status.",
            "Bodyx",
        )
    )
    for x in [
        "HUD’s January 2026 disparate-impact proposal is not current law; 24 CFR 100.500 remains operative as of this snapshot.",
        "HUD’s April 2026 equal-access revisions are proposed, not final; current 24 CFR 5.105(a)(2) remains in the conditional federal set.",
        "Kansas introduced bills and ‘Measures Affecting This Section’ cards are not law unless final enactment and effective date are verified.",
        "Historical session laws belong in a dated archive with valid-from/valid-to metadata. They should not be uploaded into the active ChatGPT source set unless a past-period question requires them.",
    ]:
        story.append(bullet(esc(x)))
    story.append(
        p(
            "<b>Why no synthetic ‘patched law book’:</b> combining historical wording and addenda into a rewritten rule creates a serious retrieval risk. A law-firm-style system keeps current consolidated text active, attaches enacted-but-not-integrated session laws, and preserves prior versions separately.",
            "Warningx",
        )
    )

    story += section_heading("Update and replacement protocol")
    protocol = [
        ("Monthly", "Check Kansas Legislature/Revisor alerts, eCFR changes, HUD/EPA notices, Overland Park ordinances and material appellate decisions."),
        ("Quarterly", "Re-retrieve all active sources, compare SHA-256 fingerprints, review proposals/withdrawals and issue a dated change log."),
        ("Kansas session close / July 1", "Check enrolled bills, vetoes/overrides, Session Laws, statute-book effective dates and delayed codification."),
        ("Before any high-risk action", "Live-check the exact statute/regulation/city section and local court rules; do not rely only on this snapshot."),
        ("When replacing project sources", "Replace the full active set and master manifest together. Remove superseded active PDFs so ChatGPT cannot retrieve conflicting versions."),
        ("Historical research", "Load only the dated archive needed for the event period, then remove it from the active workspace when the task is complete."),
    ]
    rows = [[p("CADENCE", "Tinyx"), p("ACTION", "Tinyx")]]
    for a, b in protocol:
        rows.append([p(esc(a), "Smallx"), p(esc(b), "Smallx")])
    pt = LongTable(rows, colWidths=[1.55 * inch, 5.55 * inch], repeatRows=1)
    pt.setStyle(table_style())
    story.append(pt)
    story.append(PageBreak())

    story += section_heading("Active bundle register")
    rows = [[p("FILE", "Tinyx"), p("PAGES", "Tinyx"), p("ROLE", "Tinyx")]]
    roles = {
        "GH-KS-01": "Kansas Article 25 / KRLTA primary text",
        "GH-KS-02": "Kansas eviction, fair housing, screening, safety, 2026 addenda and cases",
        "GH-FED-01": "Federal fair housing and current HUD regulations/guidance status",
        "GH-FED-02": "Federal lead, screening, service, foreclosure, military and communications overlays",
        "GH-FED-03": "Conditional HUD-assisted / federally backed program rules",
        "GH-OP-01": "Overland Park rental operations, property maintenance and civil rights",
        "GH-OP-02": "Overland Park building, fire, systems and zoning amendments",
    }
    for b in bundle_summaries:
        role = next((v for k, v in roles.items() if b["filename"].startswith(k)), "Legal source bundle")
        rows.append([p(esc(b["filename"]), "Tinyx"), p(str(b["pages"]), "Smallx"), p(esc(role), "Smallx")])
    bt = LongTable(rows, colWidths=[3.75 * inch, 0.65 * inch, 2.7 * inch], repeatRows=1)
    bt.setStyle(table_style())
    story.append(bt)

    story += section_heading("Official portals for live verification")
    links = [
        ("Kansas Legislature — 2026 statutes", "https://www.kslegislature.gov/b2025_26/laws/"),
        ("Kansas Secretary of State — Session Laws", "https://sos.ks.gov/publications/session-laws.html"),
        ("Kansas Judicial Council — landlord/tenant forms", "https://www.kjc.ks.gov/legal-forms/evictions-landlord-tenant"),
        ("eCFR", "https://www.ecfr.gov/"),
        ("U.S. Code", "https://uscode.house.gov/"),
        ("HUD fair housing", "https://www.hud.gov/fairhousing"),
        ("EPA lead", "https://www.epa.gov/lead"),
        ("Overland Park municipal code", "https://online.encodeplus.com/regs/overlandpark-ks/"),
        ("Overland Park rental licensing", "https://www.opkansas.gov/rental-licensing-and-inspection"),
        ("Overland Park building codes", "https://www.opkansas.gov/building-codes"),
    ]
    for label, url in links:
        story.append(p(f'<link href="{esc(url)}" color="#285778"><u>{esc(label)}</u></link><br/><font size="6.5">{esc(url)}</font>', "Smallx"))
    story.append(
        p(
            "Prepared for internal research and source retrieval. Not legal advice. Confirm official current law and engage licensed Kansas counsel for legal conclusions or action.",
            "Warningx",
        )
    )
    d = doc(path, "GH Master Authority Index")
    d.build(story, onFirstPage=footer, onLaterPages=footer)
    # The master is short but still receives a useful navigation outline.
    reader = PdfReader(path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    for label, page_no in [
        ("Cover and use rule", 0),
        ("Executive instructions", 1),
        ("Property triggers", 2),
        ("Issue map and currentness register", 3),
        ("GH legal review queue", 4),
        ("Historical status and update protocol", 5),
        ("Bundle register and official portals", 6),
    ]:
        if page_no < len(writer.pages):
            writer.add_outline_item(label, page_no)
    writer.add_metadata(dict(reader.metadata or {}))
    temp = path.with_suffix(".outlined.pdf")
    with temp.open("wb") as fh:
        writer.write(fh)
    temp.replace(path)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def op_records() -> list[dict]:
    data = load_json(SOURCE_ROOT / "overland_park/encodeplus_manifest.json")
    records = []
    for x in data:
        path = SOURCE_ROOT / "overland_park" / x["filename"]
        records.append(
            {
                "group": "overland_park_code",
                "citation": f"OPMC toc {x['tocid']}",
                "title": x["filename"].removesuffix(".pdf").replace("_", " "),
                "authority": "Binding municipal code / local amendment (official export)",
                "applicability": "Direct unless section-specific trigger or zoning status differs",
                "official_url": x["source_url"],
                "retrieved": AS_OF_ISO,
                "local_path": str(path.relative_to(ROOT)),
            }
        )
    return records


def federal_records() -> list[dict]:
    preferred = SOURCE_ROOT / "federal/federal_manifest.json"
    path = preferred if preferred.exists() else SOURCE_ROOT / "federal/federal_source_manifest.json"
    if not path.exists():
        raise FileNotFoundError(f"Federal manifest is not ready: {path}")
    data = load_json(path)
    raw = data.get("records") or data.get("documents") or (data if isinstance(data, list) else [])
    records = []
    for item in raw:
        if not item.get("local_path"):
            continue
        rec = dict(item)
        rec["group"] = rec.get("group", "federal_official")
        rec["authority"] = rec.get("authority", rec.get("authority_tier", "Official federal source"))
        rec["applicability"] = rec.get(
            "applicability", rec.get("applicability_trigger", "See master applicability index")
        )
        rec["pages"] = rec.get("pages", rec.get("page_count"))
        records.append(rec)
    extension = SOURCE_ROOT / "federal/federal_extension_manifest.json"
    if extension.exists():
        extra = load_json(extension)
        for item in extra.get("records", extra if isinstance(extra, list) else []):
            records.append(item)
    return records


def fed_bucket(rec: dict) -> str:
    text = " ".join(
        str(rec.get(k, "")) for k in ("group", "citation", "title", "local_path")
    ).lower()
    conditional_terms = [
        "conditional_hud", "housing choice", "part 982", "hcv", "vawa", "section 504",
        "title vi of", "2000d", "part 8", "part 5 subpart l", "part 5, subpart l",
        "part 5 subpart a", "part 5, subpart a", "hud-assisted", "hud assisted",
        "52641", "5380", "5381", "5382", "5383", "part 146", "subpart m",
        "29 u.s.c. § 794", "34 u.s.c. chapter 121",
    ]
    if any(x in text for x in conditional_terms):
        return "conditional"
    fair_terms = [
        "fair housing", "part 100", "part_100", "part 103", "part_103", "part 110",
        "part_110", "poster", "keating", "occupancy", "assistance animal", "reasonable accommodation",
        "reasonable modification", "withdrawal", "enforcement-prioritization", "3601", "chapter 45",
        "civil rights statutes", "42 u.s.c. chapter 21",
    ]
    if any(x in text for x in fair_terms):
        return "fair"
    return "other"


def write_manifest(path: Path, bundles: list[dict]) -> None:
    def mb(n):
        return f"{n / (1024 * 1024):.2f} MB"

    lines = [
        "# GH Legal Source Pack — upload manifest",
        "",
        f"**Current through:** {AS_OF}",
        f"**Property:** {PROPERTY}",
        "",
        "> Internal research and retrieval aid; not legal advice. Verify live official law and use Kansas counsel before enforcement, filing, denial, accommodation decisions, deposit deductions, or material lease changes.",
        "",
        "## Upload order",
        "",
        "Upload the master index first, then every active bundle below. Replace the entire set together when updated; remove superseded active files.",
        "",
        "| Order | File | Pages | Size | SHA-256 |",
        "|---:|---|---:|---:|---|",
    ]
    master = OUT / "GH-00_MASTER-Authority-Index_2026-07-12.pdf"
    all_files = []
    if master.exists():
        data = master.read_bytes()
        all_files.append(
            {
                "filename": master.name,
                "pages": len(PdfReader(master).pages),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    all_files += bundles
    for i, f in enumerate(all_files, 1):
        lines.append(f"| {i} | `{f['filename']}` | {f['pages']} | {mb(f['bytes'])} | `{f['sha256']}` |")
    lines += [
        "",
        "## Authority and retrieval rules",
        "",
        "- `BINDING`: current statute, regulation, ordinance, or controlling decision; confirm effective date and later history.",
        "- `CONDITIONAL`: operative only if the stated program, mortgage, management, construction, activity, or fact trigger exists.",
        "- `GUIDANCE`: operational material, not itself controlling law unless incorporated.",
        "- `PROPOSED`: monitoring only; do not apply as current law.",
        "- `WITHDRAWN`: keep outside the active project-source set.",
        "- Official appended text controls over every summary or applicability note.",
        "",
        "## Critical unresolved facts",
        "",
        "- Verify Johnson County official construction year; public sources report 1963.",
        "- Verify whether any mortgage is Fannie/Freddie/FHA/VA/USDA or otherwise federally backed.",
        "- Verify whether any unit participates in HCV or another HUD/federal assistance program.",
        "- Verify current Overland Park rental license, parcel zoning, occupancy classification, and any lawful nonconforming status.",
        "- Confirm whether an owner actually occupies a unit before even considering a four-unit fair-housing exemption; LLC ownership also requires counsel analysis.",
        "",
        "## 2026 status rules",
        "",
        "- Kansas Sub. HB 2357 and SB 391 are effective July 1, 2026 and remain explicit addenda where live section text is not integrated.",
        "- 24 CFR 100.500 remains current; the January 2026 disparate-impact proposal is not final.",
        "- 24 CFR 5.105(a)(2) remains current for covered HUD-assisted/HUD-insured housing; 2026 revisions are proposed only.",
        "- HUD's May 22, 2026 assistance-animal memo is nonbinding enforcement guidance; it does not amend the FHA or 24 CFR 100.204.",
        "- HUD guidance listed in 91 FR 17291 as withdrawn is excluded from the active set.",
        "",
        "## Bundle source ledgers",
        "",
    ]
    for bundle in bundles:
        lines += [f"### {bundle['filename']}", ""]
        for src in bundle["sources"]:
            auth = src.get("authority", "Official source")
            trigger = src.get("applicability", "See master")
            url = src.get("official_url", "")
            citation = src.get("citation", "Source")
            title = src.get("title", "")
            page = f"pp. {src['bundle_start_page']}–{src['bundle_end_page']}"
            lines.append(f"- **{citation} — {title}** ({page}); {auth}; {trigger}; [official source]({url}); SHA-256 `{src['sha256']}`")
        lines.append("")
    lines += [
        "## Maintenance protocol",
        "",
        "1. Recheck live law before every high-risk action.",
        "2. Rebuild quarterly and after the Kansas session/statute-book publication, significant federal rulemaking, city code changes, or controlling decisions.",
        "3. Compare source hashes and record changed sources in a dated change log.",
        "4. Keep prior versions in a separate historical archive with valid-from/valid-to metadata; do not upload them into the active source set unless researching a past event.",
        "5. Never patch historical and current wording into a synthetic statute.",
        "",
        "## Official live portals",
        "",
        "- [Kansas statutes](https://www.kslegislature.gov/b2025_26/laws/)",
        "- [Kansas Session Laws](https://sos.ks.gov/publications/session-laws.html)",
        "- [eCFR](https://www.ecfr.gov/)",
        "- [U.S. Code](https://uscode.house.gov/)",
        "- [HUD fair housing](https://www.hud.gov/fairhousing)",
        "- [EPA lead](https://www.epa.gov/lead)",
        "- [Overland Park code](https://online.encodeplus.com/regs/overlandpark-ks/)",
        "- [Overland Park rental licensing](https://www.opkansas.gov/rental-licensing-and-inspection)",
        "",
        "## Official items retained as links or provenance references",
        "",
        "These items could not be retrieved directly from the issuing CDN in this environment, or are program forms that should always be fetched fresh when their trigger becomes active:",
        "",
        "- [HUD Form 928.1 — Fair Housing Poster](https://www.hud.gov/sites/documents/928.1.pdf) — download and post the current form; binding 24 CFR Part 110 is included.",
        "- [HUD May 22, 2026 assistance-animal enforcement memo](https://www.hud.gov/sites/default/files/hudclips/documents/AS-Trainor-Enforcement-Guidance-Assessing-Requests-for-the-use-of-an-animal-as-a-reasonable-accommodation-under-the-fair-housing-act.pdf) — a mirror copy is bundled and clearly labeled; compare it with HUD before reliance.",
        "- [Kansas K.A.R. 28-72 lead regulations](https://www.kdhe.ks.gov/DocumentCenter/View/2586/Kansas-Administrative-Regulations---Lead-PDF) — retrieve live before covered lead work; current statutory text and federal rules are included.",
        "- [HUD-52641-A HCV tenancy addendum](https://www.hud.gov/sites/dfiles/OCHCO/documents/52641A.pdf) and [HUD-52641 HAP contract](https://www.hud.gov/sites/dfiles/OCHCO/documents/52641ENG.pdf) — activate only for HCV participation.",
        "- VAWA forms [HUD-5380](https://www.hud.gov/sites/dfiles/OCHCO/documents/5380.pdf), [5381](https://www.hud.gov/sites/dfiles/OCHCO/documents/5381.pdf), [5382](https://www.hud.gov/sites/dfiles/OCHCO/documents/5382.pdf), and [5383](https://www.hud.gov/sites/dfiles/OCHCO/documents/5383.pdf) — fetch current forms if a covered-housing-program trigger is verified.",
        "- [Johnson County Local Civil Rule 3](https://courts.jocogov.org/local_civ3.aspx) — recheck before filing; Rule 3.7 contains generative-AI certification requirements.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ks = load_json(SOURCE_ROOT / "kansas/kansas_manifest.json")
    if ks.get("errors"):
        raise RuntimeError(f"Kansas source manifest contains errors: {ks['errors']}")
    ks_records = ks["records"]
    op = op_records()
    fed = federal_records()

    bundles: list[dict] = []
    bundles.append(
        merge_bundle(
            OUT / "GH-KS-01_Kansas-Residential-Landlord-Tenant-Primary-Law_CURRENT.pdf",
            "KANSAS RESIDENTIAL LANDLORD–TENANT PRIMARY LAW",
            "K.S.A. Chapter 58, Article 25 • complete official article text",
            "All official sections in Article 25, including the operative KRLTA at 58-2540–2573 and protected-survivor section 58-25,137",
            [
                "For GH’s fourplex, K.S.A. 58-2540–2573 is the primary residential act.",
                "Older general tenancy, agricultural and mobile-home sections are preserved because this is the complete Article 25 source; do not apply them without confirming scope.",
                "Use the Kansas compliance bundle for eviction procedure, fair housing, data, smoke/fire rules, 2026 addenda and current cases.",
            ],
            [r for r in ks_records if r["group"] == "core_article25"],
        )
    )
    bundles.append(
        merge_bundle(
            OUT / "GH-KS-02_Kansas-Eviction-Fair-Housing-Screening-Safety-Addenda_CURRENT.pdf",
            "KANSAS EVICTION, FAIR HOUSING & COMPLIANCE",
            "Procedure • civil rights • screening/data • safety • 2026 addenda • current cases",
            "Kansas sources that supplement Article 25 and materially affect fourplex leasing, operations, notices, evictions, safety and applicant/tenant data",
            [
                "HB 2357 and SB 391 are binding 2026 addenda effective July 1, 2026; earlier bill drafts are not included.",
                "The eviction-procedure corpus includes Chapter 61 Articles 28–41 for procedural completeness; money-collection provisions are not routine eviction authority.",
                "Cases are preserved as published official opinions; verify later history before relying on a holding.",
                "Agency checklists/guidance are labeled nonbinding and do not replace adopted codes or regulations.",
            ],
            [r for r in ks_records if r["group"] != "core_article25"],
        )
    )

    fair = [r for r in fed if fed_bucket(r) == "fair"]
    conditional = [r for r in fed if fed_bucket(r) == "conditional"]
    other = [r for r in fed if fed_bucket(r) == "other"]
    bundles.append(
        merge_bundle(
            OUT / "GH-FED-01_Federal-Fair-Housing-HUD-Regulations_CURRENT.pdf",
            "FEDERAL FAIR HOUSING & HUD REGULATIONS",
            "Binding law • occupancy • accommodations • current guidance status",
            "Federal Fair Housing Act, implementing regulations, poster/occupancy materials, and dated 2025–2026 HUD guidance-status documents",
            [
                "Apply the full FHA conservatively unless Kansas counsel confirms a specific exemption on verified facts.",
                "A two-person-per-bedroom occupancy standard is a rebuttable starting point, not a hard federal maximum.",
                "The May 22, 2026 assistance-animal memo is guidance; statute, regulation, precedent and private-action rights remain controlling.",
                "Withdrawn HUD guidance is not reproduced as current authority; the official withdrawal/status document is retained.",
            ],
            fair,
        )
    )
    bundles.append(
        merge_bundle(
            OUT / "GH-FED-02_Lead-Screening-Military-Foreclosure-Electronic-Overlays_CURRENT.pdf",
            "FEDERAL LEAD, SCREENING & ENFORCEMENT OVERLAYS",
            "Lead disclosure/RRP • FCRA • military • foreclosure • bankruptcy • electronic notices",
            "Direct and event-triggered federal rules outside the core fair-housing packet",
            [
                "Public sources report a 1963 build; treat pre-1978 lead rules as active until the official county record is verified.",
                "Consumer-report adverse-action duties can apply to denial, a higher deposit, cosigner requirement, higher rent or other less favorable terms.",
                "E-SIGN does not make electronic-only service sufficient for every default, cure, eviction or foreclosure notice.",
                "CARES, SCRA, bankruptcy and foreclosure provisions are event- or financing-triggered; confirm facts before use.",
            ],
            other,
        )
    )
    bundles.append(
        merge_bundle(
            OUT / "GH-FED-03_CONDITIONAL-HUD-HCV-VAWA-Section504-Programs.pdf",
            "CONDITIONAL FEDERAL HOUSING PROGRAM RULES",
            "HCV • VAWA • Section 504 • Title VI • HUD-assisted / HUD-insured triggers",
            "Federal sources that become operative only after confirming program participation, federal financial assistance or covered mortgage/insurance status",
            [
                "Do not apply this packet merely because HUD administers housing law; first verify the stated program, assistance or mortgage trigger.",
                "If a tenant uses HCV, the HUD tenancy addendum/HAP contract and PHA requirements can override inconsistent lease language.",
                "VAWA, Section 504, Title VI, HUD lead-safe housing and related forms are program-specific; federal FHA duties remain separate.",
            ],
            conditional,
        )
    )

    tenant_codes = [r for r in op if not (r["citation"].startswith("OPMC toc 016") or r["citation"].startswith("OPMC toc 018"))]
    building_codes = [r for r in op if r not in tenant_codes]
    bundles.append(
        merge_bundle(
            OUT / "GH-OP-01_Overland-Park-Rental-Property-Civil-Rights-Code_CURRENT.pdf",
            "OVERLAND PARK RENTAL & PROPERTY CODE",
            "Licensing • property maintenance • nuisances • animals • civil rights • towing",
            "Official municipal-code chapters most directly affecting ongoing rental operations at the GH fourplex",
            [
                "Overland Park requires a rental license; confirm current license, renewal and inspection status.",
                "OPMC 8.10 supplies local civil-rights protections in addition to federal and Kansas law.",
                "State 2026 SB 391 preempts specified local housing policies but does not erase otherwise valid city health, safety, licensing or civil-rights rules.",
            ],
            tenant_codes,
        )
    )
    bundles.append(
        merge_bundle(
            OUT / "GH-OP-02_Overland-Park-Building-Fire-Systems-Zoning-Code_CURRENT.pdf",
            "OVERLAND PARK BUILDING, FIRE & ZONING CODE",
            "2024 code amendments adopted in 2026 • zoning excerpts • parking",
            "Official local amendments and selected development-code chapters relevant to a fourplex",
            [
                "These city PDFs contain local amendments. The incorporated copyrighted ICC base codes are not reproduced; consult the officially adopted base text when an amendment depends on it.",
                "R-3 zoning appears plausible but is not verified to the parcel. Confirm official zoning and lawful nonconforming status before applying district excerpts.",
                "Fire/open-flame, building, electrical, mechanical, plumbing, fuel-gas and energy rules can depend on occupancy classification and the scope/date of work.",
            ],
            building_codes,
        )
    )

    master = OUT / "GH-00_MASTER-Authority-Index_2026-07-12.pdf"
    master_pdf(master, bundles)
    write_manifest(OUT / "GH_LEGAL_SOURCE_PACK_UPLOAD_MANIFEST.md", bundles)
    build_record = {
        "as_of": AS_OF_ISO,
        "property": PROPERTY,
        "bundles": bundles,
        "master": {
            "filename": master.name,
            "pages": len(PdfReader(master).pages),
            "bytes": master.stat().st_size,
            "sha256": hashlib.sha256(master.read_bytes()).hexdigest(),
        },
    }
    (OUT / "GH_LEGAL_SOURCE_PACK_BUILD.json").write_text(json.dumps(build_record, indent=2), encoding="utf-8")
    for item in [build_record["master"], *bundles]:
        print(f"{item['filename']}: {item['pages']} pages, {item['bytes']} bytes")


if __name__ == "__main__":
    main()
