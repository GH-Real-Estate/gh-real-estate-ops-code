#!/usr/bin/env python3
"""Build a verified cache of current federal housing-law source PDFs.

Official PDFs are preserved byte-for-byte.  eCFR materials are fetched as
official versioned XML and rendered into searchable PDFs with the XML retained
beside the render.  The FTC landlord guide is treated the same way: the
official HTML is retained and its substantive body is rendered to PDF.
"""

from __future__ import annotations

import hashlib
import html as html_lib
import json
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

from lxml import html as lxml_html
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
RETRIEVED = "2026-07-12"
ECFR_DATE = "2026-07-09"
UA = "GH-Legal-Source-Pack/1.0 (authoritative-source archiving)"


@dataclass(frozen=True)
class DirectPDF:
    filename: str
    title: str
    citation: str
    authority_tier: str
    applicability: str
    url: str
    currentness: str
    notes: str = ""
    download_url: str | None = None


@dataclass(frozen=True)
class ECFRSpec:
    filename: str
    title: str
    citation: str
    authority_tier: str
    applicability: str
    title_no: int
    part: int
    subpart: str | None = None
    notes: str = ""


DIRECT_PDFS = [
    DirectPDF(
        "01_Fair_Housing_Act_42_USC_3601-3631_USCode_2024.pdf",
        "Fair Housing Act — Title VIII, Civil Rights Act of 1968",
        "42 U.S.C. §§ 3601–3631 (2024 U.S. Code edition)",
        "Tier 1 — binding federal statute",
        "Directly applies to most residential rentals; statutory exemptions must be analyzed narrowly and do not all extend to advertising or 42 U.S.C. § 1982.",
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title42/pdf/USCODE-2024-title42-chap45.pdf",
        "Official 2024 U.S. Code edition; verify later amendments before reliance.",
    ),
    DirectPDF(
        "02_Civil_Rights_Act_42_USC_1981-2000h_USCode_2024.pdf",
        "Civil Rights statutes, including 42 U.S.C. §§ 1981 and 1982",
        "42 U.S.C. chapter 21, subchapter I (2024 U.S. Code edition)",
        "Tier 1 — binding federal statute",
        "42 U.S.C. § 1982 independently prohibits racial discrimination in property transactions; other included provisions have narrower triggers.",
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title42/pdf/USCODE-2024-title42-chap21-subchapI.pdf",
        "Official 2024 U.S. Code edition; verify later amendments before reliance.",
    ),
    DirectPDF(
        "12_HUD_2025_Withdrawal_of_FHEO_Guidance.pdf",
        "Notice of the Withdrawal of FHEO Guidance Documents",
        "HUD memorandum, Sept. 17, 2025",
        "Tier 2 — official agency withdrawal/enforcement policy; nonbinding as substantive law",
        "Always relevant when consulting legacy HUD guidance; listed documents are withdrawn and should not be treated as current authority.",
        "https://www.hud.gov/sites/dfiles/Main/documents/Notice-of-Withdrawal-of-Guidance-Documents.pdf",
        "Effective Sept. 17, 2025; HUD states it remains effective until amended, superseded, or rescinded.",
    ),
    DirectPDF(
        "13_Federal_Register_2026_HUD_Guidance_Withdrawal_91_FR_17291.pdf",
        "Notification of Withdrawal of Fair Housing and Equal Opportunity Guidance Documents",
        "91 Fed. Reg. 17291–17292 (Apr. 6, 2026)",
        "Tier 2 — official Federal Register notice of agency action",
        "Always relevant when evaluating whether old HUD fair-housing guidance remains in active use.",
        "https://www.govinfo.gov/content/pkg/FR-2026-04-06/pdf/2026-06624.pdf",
        "Published Apr. 6, 2026; withdrawal effective Sept. 17, 2025.",
    ),
    DirectPDF(
        "14_HUD_2026_Assistance_Animal_Enforcement_Guidance.pdf",
        "Enforcement Guidance — Assessing Requests for the Use of an Animal as a Reasonable Accommodation Under the Fair Housing Act",
        "HUD FHEO memorandum, May 22, 2026",
        "Tier 2 — official agency enforcement policy; expressly nonbinding",
        "Relevant to assistance-animal accommodation requests; must be read with 42 U.S.C. § 3604(f)(3)(B), 24 C.F.R. § 100.204, controlling case law, and applicable state/local law.",
        "https://www.hud.gov/sites/default/files/hudclips/documents/AS-Trainor-Enforcement-Guidance-Assessing-Requests-for-the-use-of-an-animal-as-a-reasonable-accommodation-under-the-fair-housing-act.pdf",
        "Dated May 22, 2026. It describes FHEO enforcement priorities and does not itself alter statutes or regulations.",
        "The HUD CDN blocked automated retrieval; cached from a public mirror of the signed 26-page memorandum. Re-verify against the official HUD URL before legal reliance.",
        "https://grandriversolutions.com/wp-content/uploads/2026/05/ESA-Enforcement-Memorandum-w-Appendix-05.22.2026-SIGNED-Incomplete-Access-Pass.pdf",
    ),
    DirectPDF(
        "15_HUD_Keating_Occupancy_Standards_Memorandum.pdf",
        "Fair Housing Enforcement Policy: Occupancy Cases (Keating Memorandum)",
        "63 Fed. Reg. 70256, 70256–70257 (Dec. 18, 1998), reproducing Mar. 20, 1991 memorandum",
        "Tier 2 — statutorily preserved HUD enforcement policy; rebuttable, not a hard occupancy limit",
        "Relevant when adopting or enforcing occupancy standards; two persons per bedroom is only a starting point, subject to unit size/configuration, ages, local code, and other factors.",
        "https://www.govinfo.gov/content/pkg/FR-1998-12-18/pdf/98-33568.pdf",
        "Published under Pub. L. 105-276 § 589. Read as enforcement policy, not as a safe harbor that overrides the Fair Housing Act.",
    ),
    DirectPDF(
        "16_HUD_Fair_Housing_Poster_Form_928.1.pdf",
        "Equal Housing Opportunity Poster",
        "Form HUD-928.1 (8/2011); 24 C.F.R. part 110",
        "Tier 3 — official compliance form implementing a binding posting regulation",
        "Posting duty depends on 24 C.F.R. part 110; especially relevant to leasing or brokerage offices open to the public.",
        "https://www.hud.gov/sites/documents/928.1.pdf",
        "Official HUD form currently posted by HUD; the form itself is an aid, while part 110 supplies the legal requirement.",
    ),
    DirectPDF(
        "17_HUD_DOJ_Reasonable_Accommodations_Joint_Statement_2004.pdf",
        "Joint Statement of HUD and DOJ: Reasonable Accommodations Under the Fair Housing Act",
        "HUD/DOJ Joint Statement (May 17, 2004)",
        "Tier 2 — official interpretive guidance; nonbinding",
        "Relevant to disability-related requests to change rules, policies, practices, or services. Do not substitute it for the statute, regulation, or controlling precedent.",
        "https://www.justice.gov/sites/default/files/crt/legacy/2010/12/14/joint_statement_ra.pdf",
        "Not identified in HUD's Sept. 17, 2025 withdrawal table; verify status at time of use.",
    ),
    DirectPDF(
        "18_HUD_DOJ_Reasonable_Modifications_Joint_Statement_2008.pdf",
        "Joint Statement of HUD and DOJ: Reasonable Modifications Under the Fair Housing Act",
        "HUD/DOJ Joint Statement (Mar. 5, 2008)",
        "Tier 2 — official interpretive guidance; nonbinding",
        "Relevant to disability-related structural-change requests and allocation of costs; federally assisted housing may have additional Section 504 duties.",
        "https://www.justice.gov/sites/default/files/crt/legacy/2010/12/15/reasonable_modifications_mar08.pdf",
        "Not identified in HUD's Sept. 17, 2025 withdrawal table; verify status at time of use.",
    ),
    DirectPDF(
        "19_EPA_Protect_Your_Family_From_Lead_2026.pdf",
        "Protect Your Family From Lead in Your Home",
        "EPA-747-K-12-001, revised 2026",
        "Tier 3 — official mandatory-disclosure pamphlet/compliance aid",
        "Directly relevant to most leases of pre-1978 housing; provide the current pamphlet before the tenant is obligated under the lease, together with required disclosures.",
        "https://www.epa.gov/system/files/documents/2026-02/protectyourfamily_pamphlet_2026_3.pdf",
        "2026 edition reflects dust-lead levels effective Jan. 12, 2026.",
    ),
    DirectPDF(
        "20_EPA_Renovate_Right_Guide_2026_Posted.pdf",
        "The Lead-Safe Certified Guide to Renovate Right",
        "EPA-740-K-10-001 (rev. Sept. 2011; official EPA file reposted Feb. 2026)",
        "Tier 3 — official pre-renovation education pamphlet/compliance aid",
        "Relevant before covered renovation, repair, or painting work in pre-1978 housing or child-occupied facilities.",
        "https://www.epa.gov/system/files/documents/2026-02/renovateright_sept2011_b-w_booklet_0.pdf",
        "The substantive pamphlet is revised Sept. 2011; EPA's official file was posted in its 2026 document collection.",
    ),
    DirectPDF(
        "21_EPA_RRP_Small_Entity_Compliance_Guide_2026.pdf",
        "Small Entity Compliance Guide to Renovate Right",
        "EPA compliance guide (2026)",
        "Tier 3 — official compliance guidance; nonbinding explanation of binding RRP rules",
        "Relevant when an owner, manager, maintenance worker, or contractor disturbs painted surfaces in covered pre-1978 housing.",
        "https://www.epa.gov/system/files/documents/2026-05/508-small-entity-guide-2026.pdf",
        "Current EPA guide retrieved July 12, 2026.",
    ),
    DirectPDF(
        "22_EPA_Steps_to_Lead_Safe_RRP_2026.pdf",
        "Steps to Lead Safe Renovation, Repair and Painting",
        "EPA-740-K-11-007, revised May 2026",
        "Tier 3 — official compliance aid; nonbinding explanation of binding RRP rules",
        "Relevant to covered renovation/maintenance work and useful as a field checklist; regulations control if the guide differs.",
        "https://www.epa.gov/system/files/documents/2026-05/508-stepsbooklet_2026.pdf",
        "Revised May 2026.",
    ),
    DirectPDF(
        "23_EPA_HUD_Lead_Disclosure_Rule_Fact_Sheet_2025.pdf",
        "Lead-Based Paint Disclosure Rule Fact Sheet",
        "EPA/HUD fact sheet (Jan. 2025)",
        "Tier 3 — official compliance aid; nonbinding",
        "Relevant to sales and leases of most pre-1978 housing; use with 42 U.S.C. § 4852d, 24 C.F.R. part 35 subpart A, and 40 C.F.R. part 745 subpart F.",
        "https://www.epa.gov/system/files/documents/2024-09/lead-disclosure-rule-fact-sheet.pdf",
        "Document states January 2025; official EPA URL retained.",
    ),
    DirectPDF(
        "24_EPA_Sample_Lessor_Lead_Disclosure_Form.pdf",
        "Lessor's Disclosure of Information on Lead-Based Paint and/or Lead-Based Paint Hazards",
        "EPA sample lessor disclosure form",
        "Tier 3 — official model form; not itself a substitute for compliance analysis",
        "Relevant to most pre-1978 leases. Complete accurately, attach records/reports, provide pamphlet, and retain signed acknowledgments as required.",
        "https://www.epa.gov/sites/default/files/documents/lesr_eng.pdf",
        "Official sample form; verify EPA's current form page at time of transaction.",
    ),
    DirectPDF(
        "26_FCRA_15_USC_1681-1681x_USCode_2024.pdf",
        "Fair Credit Reporting Act",
        "15 U.S.C. §§ 1681–1681x (2024 U.S. Code edition)",
        "Tier 1 — binding federal statute",
        "Directly relevant when obtaining or using tenant-screening consumer reports, taking adverse action, furnishing information, or disposing of report data.",
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title15/pdf/USCODE-2024-title15-chap41-subchapIII.pdf",
        "Official 2024 U.S. Code edition; verify later amendments before reliance.",
    ),
    DirectPDF(
        "27_ESIGN_Act_15_USC_7001-7031_USCode_2024.pdf",
        "Electronic Signatures in Global and National Commerce Act (E-SIGN)",
        "15 U.S.C. chapter 96 (2024 U.S. Code edition)",
        "Tier 1 — binding federal statute",
        "Relevant to electronic leases and records. Section 7003 excludes certain notices involving default, acceleration, repossession, foreclosure, eviction, or the right to cure under a primary-residence lease.",
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title15/pdf/USCODE-2024-title15-chap96.pdf",
        "Official 2024 U.S. Code edition; verify later amendments before reliance.",
    ),
    DirectPDF(
        "28_Servicemembers_Civil_Relief_Act_50_USC_3901-4043_USCode_2024.pdf",
        "Servicemembers Civil Relief Act",
        "50 U.S.C. chapter 50 (2024 U.S. Code edition)",
        "Tier 1 — binding federal statute",
        "Conditional: eviction protection, lease termination, default-judgment affidavits, and related duties trigger with qualifying military service/dependents. Dollar caps are adjusted periodically.",
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title50/pdf/USCODE-2024-title50-chap50.pdf",
        "Official 2024 U.S. Code edition; confirm the current annual rent cap and later amendments.",
    ),
    DirectPDF(
        "29_CARES_Act_15_USC_9001-9141_Including_9058_USCode_2024.pdf",
        "Coronavirus Aid, Relief, and Economic Security Act codification, including 15 U.S.C. § 9058",
        "15 U.S.C. chapter 116 (2024 U.S. Code edition)",
        "Tier 1 — binding federal statute; coverage-dependent",
        "Conditional: 15 U.S.C. § 9058(c) notice-to-vacate provision applies only to a covered dwelling in a covered property; coverage depends on federal program or federally backed mortgage facts.",
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title15/pdf/USCODE-2024-title15-chap116.pdf",
        "Official 2024 U.S. Code edition. The chapter is included because GovInfo does not publish the requested section as a standalone PDF.",
    ),
    DirectPDF(
        "30_PTFA_12_USC_5201-5261_With_5220_Note_USCode_2024.pdf",
        "Emergency Economic Stabilization Act codification and Protecting Tenants at Foreclosure Act note",
        "12 U.S.C. chapter 52, including note to § 5220 (2024 U.S. Code edition)",
        "Tier 1 — binding federal statute; foreclosure-triggered",
        "Conditional: successor-in-interest obligations arise after foreclosure of federally related mortgage loans or on residential real property, subject to bona fide tenancy and purchaser-occupancy provisions.",
        "https://www.govinfo.gov/content/pkg/USCODE-2024-title12/pdf/USCODE-2024-title12-chap52.pdf",
        "Official 2024 U.S. Code edition; the PTFA text appears in the statutory note to 12 U.S.C. § 5220.",
    ),
]


ECFR_SPECS = [
    ECFRSpec(
        "03_24_CFR_Part_100_Fair_Housing_Regulations_2026-07-09.pdf",
        "Discriminatory Conduct Under the Fair Housing Act",
        "24 C.F.R. part 100",
        "Tier 1 — binding federal regulation",
        "Directly applies to Fair Housing Act conduct; provisions cover sales/rentals, advertising, disability accommodations/modifications, familial status, interference, and disparate impact.",
        24,
        100,
    ),
    ECFRSpec(
        "04_24_CFR_Part_103_Fair_Housing_Complaints_2026-07-09.pdf",
        "Fair Housing — Complaint Processing",
        "24 C.F.R. part 103",
        "Tier 1 — binding federal regulation",
        "Triggered by a HUD Fair Housing Act complaint or investigation; useful for preservation, response, conciliation, and timing.",
        24,
        103,
    ),
    ECFRSpec(
        "05_24_CFR_Part_110_Fair_Housing_Poster_2026-07-09.pdf",
        "Fair Housing Poster",
        "24 C.F.R. part 110",
        "Tier 1 — binding federal regulation",
        "Posting obligations depend on the regulated person's real-estate business and premises; pair with current Form HUD-928.1.",
        24,
        110,
    ),
    ECFRSpec(
        "06_24_CFR_Part_35_Subpart_A_Lead_Disclosure_2026-07-09.pdf",
        "Disclosure of Known Lead-Based Paint and/or Lead-Based Paint Hazards Upon Sale or Lease of Residential Property",
        "24 C.F.R. part 35, subpart A",
        "Tier 1 — binding federal regulation",
        "Directly relevant to most leases of housing constructed before 1978, subject to stated exemptions.",
        24,
        35,
        "A",
    ),
    ECFRSpec(
        "07_40_CFR_Part_745_Subpart_D_Lead_Hazard_Standards_2026-07-09.pdf",
        "Lead-Based Paint Hazards",
        "40 C.F.R. part 745, subpart D",
        "Tier 1 — binding federal regulation",
        "Relevant when evaluating lead-based paint hazards and dust-lead reportable/action levels, including levels effective in 2026.",
        40,
        745,
        "D",
    ),
    ECFRSpec(
        "08_40_CFR_Part_745_Subpart_E_RRP_2026-07-09.pdf",
        "Residential Property Renovation",
        "40 C.F.R. part 745, subpart E",
        "Tier 1 — binding federal regulation",
        "Triggered by compensated renovation, repair, or painting that disturbs painted surfaces in covered pre-1978 housing or child-occupied facilities, subject to exemptions and thresholds.",
        40,
        745,
        "E",
    ),
    ECFRSpec(
        "09_40_CFR_Part_745_Subpart_F_Lead_Disclosure_2026-07-09.pdf",
        "Disclosure of Known Lead-Based Paint and/or Lead-Based Paint Hazards Upon Sale or Lease of Residential Property",
        "40 C.F.R. part 745, subpart F",
        "Tier 1 — binding federal regulation",
        "Directly relevant to most leases of pre-1978 housing; EPA's parallel disclosure rule complements 24 C.F.R. part 35 subpart A.",
        40,
        745,
        "F",
    ),
    ECFRSpec(
        "10_16_CFR_Part_682_Consumer_Information_Disposal_2026-07-09.pdf",
        "Disposal of Consumer Report Information and Records",
        "16 C.F.R. part 682",
        "Tier 1 — binding federal regulation",
        "Triggered when disposing of tenant-screening consumer report information; requires reasonable disposal measures.",
        16,
        682,
    ),
    ECFRSpec(
        "11_24_CFR_Part_5_Subpart_A_HUD_General_Requirements_2026-07-09.pdf",
        "General HUD Program Requirements; Waivers",
        "24 C.F.R. part 5, subpart A",
        "Tier 1 — binding federal regulation; program/mortgage-status dependent",
        "Conditional: applies where a listed HUD program, HUD assistance, or HUD-insured mortgage triggers a provision; includes 24 C.F.R. § 5.105.",
        24,
        5,
        "A",
    ),
    ECFRSpec(
        "11A_24_CFR_Part_5_Subpart_L_VAWA_2026-07-09.pdf",
        "Protection for Victims of Domestic Violence, Dating Violence, Sexual Assault, or Stalking",
        "24 C.F.R. part 5, subpart L",
        "Tier 1 — binding federal regulation; covered-housing-program dependent",
        "Conditional: applies to covered housing programs, not automatically to every private rental. Kansas law may independently protect tenants.",
        24,
        5,
        "L",
    ),
    ECFRSpec(
        "11B_24_CFR_Part_8_Section_504_HUD_Programs_2026-07-09.pdf",
        "Nondiscrimination Based on Handicap in Federally Assisted Programs and Activities of HUD",
        "24 C.F.R. part 8",
        "Tier 1 — binding federal regulation; federal-financial-assistance dependent",
        "Conditional: applies to recipients of federal financial assistance from HUD; obligations can exceed Fair Housing Act duties.",
        24,
        8,
    ),
]


FTC_META = {
    "filename": "25_FTC_Using_Consumer_Reports_What_Landlords_Need_to_Know_2023.pdf",
    "title": "Using Consumer Reports: What Landlords Need to Know",
    "citation": "Federal Trade Commission business guidance (July 20, 2023)",
    "authority_tier": "Tier 3 — official agency compliance guidance; nonbinding",
    "applicability": "Directly relevant when a landlord or property manager obtains a tenant-screening report or takes adverse action based wholly or partly on it.",
    "url": "https://www.ftc.gov/business-guidance/resources/using-consumer-reports-what-landlords-need-know",
    "currentness": "Official FTC page retrieved July 12, 2026; statutes and regulations control.",
}


def request_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        # HUD's CDN intermittently rejects urllib while serving the same public
        # file to curl.  Preserve a strict --fail result and never accept an
        # HTML error page as a PDF.
        if exc.code not in {403, 429}:
            raise
        proc = subprocess.run(
            ["curl", "-L", "--fail", "--silent", "--show-error", "--max-time", "120", url],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if proc.returncode:
            raise RuntimeError(proc.stderr.decode("utf-8", "replace").strip()) from exc
        return proc.stdout


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".part")
    tmp.write_bytes(data)
    tmp.replace(path)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def page_count(path: Path) -> int:
    return len(PdfReader(str(path), strict=False).pages)


def validate_pdf(path: Path) -> int:
    if path.read_bytes()[:5] != b"%PDF-":
        raise ValueError(f"download did not return a PDF: {path.name}")
    pages = page_count(path)
    if pages < 1:
        raise ValueError(f"PDF has no pages: {path.name}")
    return pages


def clean_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    return re.sub(r"\s+", " ", text).strip()


def pdf_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="SourceTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#17365D"),
            alignment=TA_CENTER,
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SourceMeta",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#333333"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="PartHead",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=17,
            textColor=colors.HexColor("#17365D"),
            spaceBefore=9,
            spaceAfter=8,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubpartHead",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#7A4F00"),
            spaceBefore=10,
            spaceAfter=6,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHead",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=12,
            textColor=colors.HexColor("#17365D"),
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="RegBody",
            parent=styles["BodyText"],
            fontName="Times-Roman",
            fontSize=8.7,
            leading=11.2,
            spaceAfter=4,
            allowWidows=1,
            allowOrphans=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="RegNote",
            parent=styles["RegBody"],
            fontName="Times-Italic",
            textColor=colors.HexColor("#444444"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="FTCBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12.5,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="FTCBullet",
            parent=styles["FTCBody"],
            leftIndent=16,
            firstLineIndent=-8,
            bulletIndent=7,
        )
    )
    return styles


STYLES = pdf_styles()


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D5DCE5"))
    canvas.line(0.65 * inch, 0.48 * inch, 7.85 * inch, 0.48 * inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#56616F"))
    canvas.drawString(0.65 * inch, 0.29 * inch, f"GH Federal Legal Source Cache • retrieved {RETRIEVED}")
    canvas.drawRightString(7.85 * inch, 0.29 * inch, f"Page {doc.page}")
    canvas.restoreState()


def meta_cover(title: str, citation: str, authority: str, applicability: str, url: str, currentness: str):
    story = [Spacer(1, 0.55 * inch)]
    story.append(Paragraph(html_lib.escape(title), STYLES["SourceTitle"]))
    for label, value in [
        ("Citation", citation),
        ("Authority", authority),
        ("Applicability / trigger", applicability),
        ("Source", url),
        ("Currentness", currentness),
        ("Retrieved", RETRIEVED),
    ]:
        story.append(
            Paragraph(
                f"<b>{html_lib.escape(label)}:</b> {html_lib.escape(value)}",
                STYLES["SourceMeta"],
            )
        )
    story.append(Spacer(1, 0.15 * inch))
    story.append(
        Paragraph(
            "This is a searchable rendering of an official source. It is not legal advice. The official source controls, and current law must be rechecked before action.",
            STYLES["SourceMeta"],
        )
    )
    story.append(PageBreak())
    return story


def find_subpart(root: ET.Element, subpart: str) -> ET.Element:
    for node in root.iter():
        if node.tag == "DIV6" and node.attrib.get("TYPE") == "SUBPART" and node.attrib.get("N", "").upper() == subpart.upper():
            return node
    raise ValueError(f"subpart {subpart} not found")


def ecfr_blocks(node: ET.Element, depth: int = 0) -> Iterable[tuple[str, str]]:
    """Yield nonduplicated semantic blocks from eCFR XML."""
    terminal = {"P", "FP", "PSPACE", "AUTH", "SOURCE", "CITA"}
    for child in list(node):
        tag = child.tag
        text = clean_text(" ".join(child.itertext()))
        if tag == "HEAD":
            if text:
                if node.tag == "DIV5":
                    yield ("part", text)
                elif node.tag == "DIV6":
                    yield ("subpart", text)
                else:
                    yield ("section", text)
            continue
        if tag in {"HED", "APPRO"}:
            if text:
                yield ("section", text)
            continue
        if tag in terminal:
            if text:
                yield ("note" if tag in {"AUTH", "SOURCE", "CITA"} else "body", text)
            continue
        if tag in {"TABLE", "GPOTABLE"}:
            for row in child.iter():
                if row.tag in {"ROW", "TR"}:
                    cells = [clean_text(" ".join(c.itertext())) for c in list(row)]
                    cells = [c for c in cells if c]
                    if cells:
                        yield ("body", " | ".join(cells))
            continue
        yield from ecfr_blocks(child, depth + 1)


def render_ecfr(spec: ECFRSpec, xml_path: Path, pdf_path: Path) -> None:
    root = ET.parse(xml_path).getroot()
    content = find_subpart(root, spec.subpart) if spec.subpart else root
    url = f"https://www.ecfr.gov/api/versioner/v1/full/{ECFR_DATE}/title-{spec.title_no}.xml?part={spec.part}"
    if spec.subpart:
        url += f" (render limited to subpart {spec.subpart})"
    story = meta_cover(
        spec.title,
        spec.citation,
        spec.authority_tier,
        spec.applicability,
        url,
        f"Official eCFR versioned XML as of {ECFR_DATE}; retrieved {RETRIEVED}.",
    )
    count = 0
    for kind, text in ecfr_blocks(content):
        count += 1
        escaped = html_lib.escape(text)
        if kind == "part":
            style = STYLES["PartHead"]
        elif kind == "subpart":
            style = STYLES["SubpartHead"]
        elif kind == "section":
            style = STYLES["SectionHead"]
        elif kind == "note":
            style = STYLES["RegNote"]
        else:
            style = STYLES["RegBody"]
        story.append(Paragraph(escaped, style))
    if count < 3:
        raise ValueError(f"too few text blocks rendered from {xml_path.name}: {count}")
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.62 * inch,
        bottomMargin=0.62 * inch,
        title=spec.title,
        author="Official eCFR XML; local searchable rendering for GH Real Estate",
        subject=spec.citation,
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def render_ftc(html_path: Path, pdf_path: Path) -> None:
    tree = lxml_html.parse(str(html_path))
    bodies = tree.xpath('//*[contains(concat(" ", normalize-space(@class), " "), " field--name-body ")]')
    if not bodies:
        bodies = tree.xpath("//main")
    if not bodies:
        raise ValueError("FTC substantive body not found")
    body = bodies[0]
    story = meta_cover(
        FTC_META["title"],
        FTC_META["citation"],
        FTC_META["authority_tier"],
        FTC_META["applicability"],
        FTC_META["url"],
        FTC_META["currentness"],
    )
    blocks = body.xpath(".//h2 | .//h3 | .//h4 | .//p | .//li")
    used = 0
    for el in blocks:
        if el.tag == "p" and el.xpath("ancestor::li"):
            continue
        text = clean_text(el.text_content())
        if not text:
            continue
        used += 1
        if el.tag == "h2":
            style, prefix = STYLES["PartHead"], ""
        elif el.tag in {"h3", "h4"}:
            style, prefix = STYLES["SectionHead"], ""
        elif el.tag == "li":
            style, prefix = STYLES["FTCBullet"], "• "
        else:
            style, prefix = STYLES["FTCBody"], ""
        story.append(Paragraph(html_lib.escape(prefix + text), style))
    if used < 8:
        raise ValueError(f"FTC render found too little body content: {used}")
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.62 * inch,
        bottomMargin=0.62 * inch,
        title=FTC_META["title"],
        author="Federal Trade Commission official HTML; local searchable rendering for GH Real Estate",
        subject=FTC_META["citation"],
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def manifest_entry(path: Path, *, title: str, citation: str, authority: str, applicability: str, url: str, currentness: str, notes: str = "", source_archive: Path | None = None, render_note: str = "") -> dict:
    entry = {
        "title": title,
        "citation": citation,
        "authority_tier": authority,
        "applicability_trigger": applicability,
        "official_url": url,
        "retrieved_date": RETRIEVED,
        "currentness": currentness,
        "sha256": sha256(path),
        "local_path": str(path.relative_to(ROOT.parent.parent.parent.parent)),
        "page_count": validate_pdf(path),
        "download_status": "downloaded_and_verified",
    }
    if notes:
        entry["notes"] = notes
    if source_archive:
        entry["source_archive_path"] = str(source_archive.relative_to(ROOT.parent.parent.parent.parent))
        entry["source_archive_sha256"] = sha256(source_archive)
    if render_note:
        entry["render_note"] = render_note
    return entry


def main() -> int:
    ROOT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    documents: list[dict] = []
    failures: list[dict] = []

    for item in DIRECT_PDFS:
        path = ROOT / item.filename
        if item.filename in {
            "12_HUD_2025_Withdrawal_of_FHEO_Guidance.pdf",
            "16_HUD_Fair_Housing_Poster_Form_928.1.pdf",
        } and not path.exists():
            failures.append(
                {
                    "title": item.title,
                    "official_url": item.url,
                    "error": "HUD CDN returned HTTP 403 to automated retrieval; equivalent controlling source is present (91 FR 17291 or 24 CFR part 110).",
                }
            )
            print(f"LINK ONLY {item.filename}: HUD CDN blocked automated retrieval", file=sys.stderr)
            continue
        try:
            if not path.exists():
                data = request_bytes(item.download_url or item.url)
                atomic_write(path, data)
            validate_pdf(path)
            documents.append(
                manifest_entry(
                    path,
                    title=item.title,
                    citation=item.citation,
                    authority=item.authority_tier,
                    applicability=item.applicability,
                    url=item.url,
                    currentness=item.currentness,
                    notes=item.notes,
                )
            )
            if item.download_url:
                documents[-1]["retrieval_mirror_url"] = item.download_url
                documents[-1]["download_status"] = "downloaded_from_public_mirror_official_url_blocked"
            print(f"OK direct {item.filename}")
        except Exception as exc:
            path.unlink(missing_ok=True)
            failures.append({"title": item.title, "official_url": item.url, "error": repr(exc)})
            print(f"FAIL direct {item.filename}: {exc}", file=sys.stderr)

    for spec in ECFR_SPECS:
        xml_url = f"https://www.ecfr.gov/api/versioner/v1/full/{ECFR_DATE}/title-{spec.title_no}.xml?part={spec.part}"
        xml_name = f"title-{spec.title_no}_part-{spec.part}_{ECFR_DATE}.xml"
        xml_path = RAW / xml_name
        pdf_path = ROOT / spec.filename
        try:
            if not xml_path.exists():
                atomic_write(xml_path, request_bytes(xml_url))
            render_ecfr(spec, xml_path, pdf_path)
            validate_pdf(pdf_path)
            documents.append(
                manifest_entry(
                    pdf_path,
                    title=spec.title,
                    citation=spec.citation,
                    authority=spec.authority_tier,
                    applicability=spec.applicability,
                    url=xml_url,
                    currentness=f"Official eCFR XML as of {ECFR_DATE}.",
                    notes=spec.notes,
                    source_archive=xml_path,
                    render_note="Searchable PDF rendered locally from the versioned official eCFR XML; the archived XML is the exact official source payload.",
                )
            )
            print(f"OK eCFR {spec.filename}")
        except Exception as exc:
            pdf_path.unlink(missing_ok=True)
            failures.append({"title": spec.title, "official_url": xml_url, "error": repr(exc)})
            print(f"FAIL eCFR {spec.filename}: {exc}", file=sys.stderr)

    html_path = RAW / "FTC_Using_Consumer_Reports_Landlords_2026-07-12.html"
    ftc_pdf = ROOT / FTC_META["filename"]
    try:
        atomic_write(html_path, request_bytes(FTC_META["url"]))
        render_ftc(html_path, ftc_pdf)
        documents.append(
            manifest_entry(
                ftc_pdf,
                title=FTC_META["title"],
                citation=FTC_META["citation"],
                authority=FTC_META["authority_tier"],
                applicability=FTC_META["applicability"],
                url=FTC_META["url"],
                currentness=FTC_META["currentness"],
                source_archive=html_path,
                render_note="Searchable PDF rendered locally from the official FTC page; the archived HTML is retained for provenance.",
            )
        )
        print(f"OK FTC {ftc_pdf.name}")
    except Exception as exc:
        ftc_pdf.unlink(missing_ok=True)
        failures.append({"title": FTC_META["title"], "official_url": FTC_META["url"], "error": repr(exc)})
        print(f"FAIL FTC: {exc}", file=sys.stderr)

    documents.sort(key=lambda d: Path(d["local_path"]).name)
    linked_conditional_sources = [
        {
            "title": "Notice of the Withdrawal of FHEO Guidance Documents",
            "citation": "HUD memorandum, Sept. 17, 2025",
            "authority_tier": "Tier 2 — official agency withdrawal notice; nonbinding as substantive law",
            "applicability_trigger": "Consult whenever legacy HUD guidance is cited. The official Federal Register notice at 91 FR 17291 is downloaded in this cache.",
            "official_url": "https://www.hud.gov/sites/dfiles/Main/documents/Notice-of-Withdrawal-of-Guidance-Documents.pdf",
            "retrieved_date": RETRIEVED,
            "sha256": None,
            "local_path": None,
            "page_count": None,
            "download_status": "link_only_hud_cdn_http_403",
        },
        {
            "title": "Equal Housing Opportunity Poster",
            "citation": "Form HUD-928.1 (8/2011)",
            "authority_tier": "Tier 3 — official compliance form; 24 CFR part 110 is binding",
            "applicability_trigger": "Posting requirement depends on 24 CFR part 110; the current regulation is downloaded in this cache.",
            "official_url": "https://www.hud.gov/sites/documents/928.1.pdf",
            "retrieved_date": RETRIEVED,
            "sha256": None,
            "local_path": None,
            "page_count": None,
            "download_status": "link_only_hud_cdn_http_403",
        },
        {
            "title": "HUD Basic Laws — June 2025 compilation",
            "citation": "HUD Office of General Counsel compilation (June 2025)",
            "authority_tier": "Tier 4 — agency compilation/backstop; not the official U.S. Code and not current enough to control",
            "applicability_trigger": "Research backstop only. Do not upload as a primary active source because it is very large and can conflict with later law and 2025–2026 policy changes.",
            "official_url": "https://www.hud.gov/sites/dfiles/GC/documents/HUDBasicLawsJune2025.pdf",
            "retrieved_date": RETRIEVED,
            "sha256": None,
            "local_path": None,
            "page_count": None,
            "download_status": "link_only_intentionally_excluded",
        },
        {
            "title": "HUD Equal Access Rule — proposed 2026 revision",
            "citation": "Proposed rule; not final law as of July 12, 2026",
            "authority_tier": "Proposal — not binding current law",
            "applicability_trigger": "Track only if GH property is subject to HUD-assisted or HUD-insured program rules; do not use as current law unless finalized.",
            "official_url": "https://www.federalregister.gov/documents/2026/04/28/2026-08355/revising-the-equal-access-rule",
            "retrieved_date": RETRIEVED,
            "sha256": None,
            "local_path": None,
            "page_count": None,
            "download_status": "link_only_proposed_rule",
        },
    ]
    payload = {
        "manifest_title": "GH Real Estate — Federal, HUD, EPA, and FTC Authoritative Source Cache",
        "generated_date": RETRIEVED,
        "ecfr_as_of": ECFR_DATE,
        "scope_note": "Official current primary law and selected current compliance guidance for a Kansas private residential landlord. Authority tiers and factual triggers must be honored; presence in this cache does not mean every source applies to every property or event.",
        "documents": documents,
        "linked_conditional_sources": linked_conditional_sources,
        "failures": failures,
        "document_count": len(documents),
        "failure_count": len(failures),
    }
    manifest = ROOT / "federal_source_manifest.json"
    manifest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"WROTE {manifest.name}: {len(documents)} documents, {len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
