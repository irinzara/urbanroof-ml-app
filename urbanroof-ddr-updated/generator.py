"""
generator.py
------------
Handles AI-powered DDR report generation using Google Gemini.
Prompt engineered to closely match UrbanRoof's official DDR format.
"""

import google.generativeai as genai
import PIL.Image
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import io
import re


def build_prompt(inspection_text: str, thermal_text: str) -> str:
    """
    Build a prompt that mirrors UrbanRoof's real DDR format exactly.
    Based on the official UrbanRoof DDR structure used in the field.
    """
    return f"""
You are an expert property inspection report writer for UrbanRoof Pvt Ltd,
a leading building waterproofing and repair company in India (www.urbanroof.in).

You have been given TWO raw data sources:
1. SITE INSPECTION REPORT — visual observations, checklist inputs, photo references
2. THERMAL IMAGING REPORT — IR camera readings confirming moisture and dampness

YOUR TASK:
Generate a complete Detailed Diagnostic Report (DDR) that EXACTLY follows the
UrbanRoof DDR format used in official field reports. The output must be
professional, structured, and match what a trained UrbanRoof engineer would write.

=== STRICT RULES ===
1. Do NOT invent any facts not present in the source documents
2. If information is missing → write: "Not Available"
3. If documents conflict → write: "Conflicting data — [brief reason]"
4. Use clear, simple language — the client is a property owner, not an engineer
5. Do NOT repeat the same observation in multiple sections
6. Always cross-reference: if thermal data confirms a visual finding, say so explicitly
7. Every area mentioned in the documents MUST appear in Section 3
8. Severity: HIGH = immediate action needed | MEDIUM = within 3 months | LOW = monitor
9. Keep the exact section numbering and headings shown below
10. For the Summary Table in Section 4.3, always pair each negative (damage) side
    finding with its corresponding positive (source) side finding

=== OUTPUT FORMAT — FOLLOW THIS EXACTLY ===

# DETAILED DIAGNOSTIC REPORT (DDR)
**Prepared by:** UrbanRoof AI Diagnostic System
**Company:** UrbanRoof Private Limited | www.urbanroof.in
**Report Type:** Comprehensive Property Health Assessment

---

## SECTION 1 — INTRODUCTION

### 1.1 Background
[2-3 sentences: Who is the client, what property, why was the inspection requested.
Extract from the documents — client name, address, building name, date of inspection.]

### 1.2 Objective of the Health Assessment
- To detect all possible flaws, problems and occurrences that might exist and analyse their cause and effects.
- To prioritise immediate repair and protection measures to be taken.
- To evaluate an accurate scope of work for design estimates and cost analysis.
- To classify recommendations and solutions based on existing flaws and precautionary measures.

### 1.3 Scope of Work
[1-2 sentences: Describe what was inspected and what tools were used — e.g., tapping hammer, crack gauge, IR thermography, moisture and pH meter. Extract from documents if available.]

---

## SECTION 2 — GENERAL INFORMATION

### 2.1 Client & Inspection Details

| Particular | Description |
|------------|-------------|
| Customer Name | [from document or "Not Available"] |
| Property Address | [from document or "Not Available"] |
| Date of Inspection | [from document or "Not Available"] |
| Inspected By | [from document or "Not Available"] |
| Brief of Enquiry | [from document or "Not Available"] |

### 2.2 Description of Site

| Particular | Description |
|------------|-------------|
| Site Address | [from document or "Not Available"] |
| Type of Structure | [e.g., Flat / Row House / Bungalow] |
| Floors | [number] |
| Year of Construction | [from document or "Not Available"] |
| Age of Building | [from document or "Not Available"] |
| Previous Structure Audit | [Yes / No / Not Available] |
| Previous Repairs | [Yes / No / Not Available] |

---

## SECTION 3 — VISUAL OBSERVATION AND READINGS

### 3.1 Sources of Leakage — Summary

[Write a clear paragraph (4-6 sentences) summarising ALL leakage sources found.
Group by area: Bathrooms, Balcony, Terrace, External Wall, etc.
Explain how each source is causing damage to other areas of the property.]

---

### 3.2 Negative Side Inputs (Damage / Impact Observed)

[For EVERY area where damage, dampness, leakage or deterioration is observed,
create one subsection. These are the "effects" — what the client can see and feel.]

#### 📍 [Area Name] — [Floor / Location]

| Input | Finding |
|-------|---------|
| Condition at adjacent walls | [Dampness / Seepage / Live Leakage / No leakage] |
| Leakage timing | [Monsoon / All time / Not sure] |
| Thermal reading | [Temperature value or range if available, else "Not Available"] |
| Thermal confirms issue? | [Yes / No / Partially] |
| Severity | 🔴 HIGH / 🟡 MEDIUM / 🟢 LOW |

**Observation:** [2-3 sentences. Describe what was found. If thermal data is available,
mention the temperature readings and what they indicate about moisture levels.]

---

### 3.3 Positive Side Inputs (Source / Origin of Leakage)

[For EVERY area that is the SOURCE of the leakage — the wet area causing the damage —
create one subsection. These are the "causes" — what needs to be fixed to stop the leakage.]

#### 🔍 [Source Area Name] — [Floor / Location]

| Input | Finding |
|-------|---------|
| Gaps / blackish dirt in tile joints | [Yes / No / Not sure] |
| Gaps around Nahani trap | [Yes / No / Not sure] |
| Tiles broken or loose | [Yes / No / Not sure] |
| Concealed plumbing leakage | [Yes / No / Not sure] |
| Type of waterproofing present | [Brick bat coba / Concrete screed / None / Not Available] |

**Observation:** [2-3 sentences. Describe the source of the problem and explain how it
is causing the damage described in the negative side section above.]

---

## SECTION 4 — ANALYSIS AND SUGGESTIONS

### 4.1 Probable Root Cause

[For each category of problem found, explain WHY it is happening in simple terms.
Use the headings below — add or remove categories as relevant to this property.]

#### 🚿 Bathroom / Wet Area Issues
**Root Cause:** [Explain in 2-3 sentences. E.g., gaps in tile joints allow water to seep
through the floor/walls, causing dampness and paint spalling in rooms below.]

#### 🏗️ Terrace Issues
**Root Cause:** [Explain if terrace issues found — hollow screed, cracks, poor slope, etc.]

#### 🧱 External Wall Issues
**Root Cause:** [Explain if external wall cracks, paint failure, or water ingress found.]

#### 🪟 Balcony Issues
**Root Cause:** [Explain if balcony tile gaps, drainage issues, or dampness found.]

[Add more categories if needed based on what was found in the documents.]

---

### 4.2 Actions Required and Suggested Treatments

[List every repair that needs to be done. Use the headings below as applicable.
Write in clear, actionable language. Include specific products (e.g., Dr. Fixit) if mentioned in documents.]

#### 4.2.1 Bathroom and Balcony Grouting Treatment
[Describe the grouting repair process if tile joint issues were found.]

#### 4.2.2 Plumbing Repairs
[Describe any plumbing work required — fixing outlets, replacing traps, etc.]

#### 4.2.3 Plaster Work
[Describe plaster repair and waterproofing treatment for external/internal walls.]

#### 4.2.4 Terrace Waterproofing Treatment
[Describe terrace repair if terrace issues were found — screed removal, new waterproofing, etc.]

#### 4.2.5 RCC Member Treatment
[Describe crack filling and structural treatment for RCC beams/columns if found.]

---

### 4.3 Summary Table

[This is the most important table. Pair each damage observation (negative/impacted side)
with its corresponding source (positive/exposed side) that caused it.]

| Point No. | Impacted Area (Negative Side — Damage Observed) | Point No. | Exposed Area (Positive Side — Source of Problem) |
|-----------|------------------------------------------------|-----------|--------------------------------------------------|
| N1 | [Damage description — e.g., Dampness at ceiling of Hall] | P1 | [Source — e.g., Gaps in tile joints of Bathroom above] |
| N2 | [Damage description] | P2 | [Source description] |
| N3 | [Continue for all pairs found] | P3 | [Continue] |

---

### 4.4 Severity Assessment

| Area | Issue Found | Severity | Action Required By |
|------|-------------|----------|--------------------|
| [Area] | [Brief issue description] | 🔴 HIGH | Immediately |
| [Area] | [Brief issue description] | 🟡 MEDIUM | Within 3 months |
| [Area] | [Brief issue description] | 🟢 LOW | Within 6 months |

[Include ALL areas from Section 3 in this table]

---

### 4.5 Further Possibilities if Action is Delayed

[2-3 sentences warning the client what will happen if repairs are not done promptly.
E.g., structural damage, increased repair cost, health hazards from mould, etc.]

---

## SECTION 5 — LIMITATION AND PRECAUTION NOTE

This property inspection report provides a general overview of the most obvious repairs required.
It is not an exhaustive inspection. The inspection addresses only those components and conditions
that are present, visible, and accessible at the time of inspection.

Some conditions noted — such as structural cracks and signs of settlement — indicate a potential
problem with the structure of the building. A structure, when stressed beyond its capacity, may
collapse without further warning signs. When such cracks suddenly develop or appear to widen and
spread, the findings must be reported immediately to a Registered Structural Engineer.

This is NOT a code compliance inspection. The inspector does not determine whether the property
complies with any past, present or future building codes or regulatory requirements.

*This report was prepared by UrbanRoof AI Diagnostic System based solely on the provided
inspection and thermal data. For structural concerns, always consult a Registered Structural Engineer.
UrbanRoof Private Limited | www.urbanroof.in | info@urbanroof.in | +91-8925-805-805*

---

=== INSPECTION REPORT DATA ===
{inspection_text}

=== THERMAL IMAGING DATA ===
{thermal_text}

NOW generate the complete DDR report following the format above exactly.
- Be thorough — cover every area, every finding, every source of leakage mentioned
- Match the professional tone of a real UrbanRoof field report
- The Summary Table in Section 4.3 is critical — pair every damage with its source
- Do not skip any section even if data is limited — write "Not Available" where needed
- Thermal readings should include actual temperature values if present in the data
"""


def generate_ddr_text_only(inspection_text: str, thermal_text: str, api_key: str) -> str:
    """Generate DDR using text data only (no images)."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = build_prompt(inspection_text, thermal_text)
    print("🤖 Sending data to AI for DDR generation...")
    response = model.generate_content(prompt)
    return response.text


def generate_ddr_with_vision(inspection_text: str, thermal_text: str,
                              image_paths: list, api_key: str) -> str:
    """Generate DDR using text + actual images (Vision mode)."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    content_parts = []
    content_parts.append(build_prompt(inspection_text, thermal_text))

    images_added = 0
    for img_path in image_paths[:10]:
        try:
            img = PIL.Image.open(img_path)
            content_parts.append(f"\n[Image: {os.path.basename(img_path)}]")
            content_parts.append(img)
            images_added += 1
        except Exception as e:
            print(f"Could not load image {img_path}: {e}")
            continue

    print(f"🤖 Sending text + {images_added} images to AI Vision...")
    response = model.generate_content(content_parts)
    return response.text


def validate_api_key(api_key: str) -> bool:
    """Quick check if the API key works."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        model.generate_content("Say OK")
        return True
    except Exception:
        return False


# ── PDF GENERATION ────────────────────────────────────────────────────────────

def generate_pdf(ddr_text: str) -> bytes:
    """
    Convert the Markdown DDR text to a professional PDF
    that closely mirrors the UrbanRoof official DDR visual style:
    - Dark header band with white text
    - Gold/amber accent colour (#F5A623)
    - Clean table formatting
    - Section headers with underline rules
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=18*mm, leftMargin=18*mm,
        topMargin=18*mm, bottomMargin=18*mm
    )

    GOLD   = colors.HexColor('#F5A623')
    DARK   = colors.HexColor('#1A1A2E')
    WHITE  = colors.white
    GREY   = colors.HexColor('#555555')
    LGREY  = colors.HexColor('#CCCCCC')
    BGCELL = colors.HexColor('#F4F4F4')
    GREEN  = colors.HexColor('#27AE60')
    ORANGE = colors.HexColor('#E67E22')
    RED    = colors.HexColor('#E74C3C')

    title_style = ParagraphStyle('DDRTitle',
        fontName='Helvetica-Bold', fontSize=20,
        textColor=GOLD, alignment=TA_CENTER,
        spaceAfter=4, spaceBefore=0)

    subtitle_style = ParagraphStyle('DDRSubtitle',
        fontName='Helvetica', fontSize=10,
        textColor=WHITE, alignment=TA_CENTER,
        spaceAfter=2)

    h1_style = ParagraphStyle('DDRH1',
        fontName='Helvetica-Bold', fontSize=13,
        textColor=WHITE, alignment=TA_LEFT,
        spaceBefore=14, spaceAfter=2,
        backColor=DARK, borderPad=6,
        leftIndent=-2, rightIndent=-2)

    h2_style = ParagraphStyle('DDRH2',
        fontName='Helvetica-Bold', fontSize=11,
        textColor=DARK, spaceBefore=10, spaceAfter=2)

    h3_style = ParagraphStyle('DDRH3',
        fontName='Helvetica-Bold', fontSize=10,
        textColor=GOLD, spaceBefore=8, spaceAfter=2)

    body_style = ParagraphStyle('DDRBody',
        fontName='Helvetica', fontSize=9,
        textColor=colors.HexColor('#333333'),
        spaceAfter=4, leading=14, alignment=TA_JUSTIFY)

    bullet_style = ParagraphStyle('DDRBullet',
        fontName='Helvetica', fontSize=9,
        textColor=colors.HexColor('#333333'),
        spaceAfter=3, leading=13,
        leftIndent=12, bulletIndent=0)

    footer_style = ParagraphStyle('DDRFooter',
        fontName='Helvetica', fontSize=7.5,
        textColor=GREY, alignment=TA_CENTER,
        spaceBefore=16)

    bold_body = ParagraphStyle('DDRBoldBody',
        fontName='Helvetica-Bold', fontSize=9,
        textColor=DARK, spaceAfter=4, leading=14)

    story = []

    # ── HEADER BANNER ────────────────────────────────────────────────────
    header_data = [[
        Paragraph('<font color="#F5A623"><b>UrbanRoof</b></font><br/>'
                  '<font color="white" size="7">www.urbanroof.in</font>', subtitle_style),
        Paragraph('<font color="white"><b>DETAILED DIAGNOSTIC REPORT (DDR)</b></font><br/>'
                  '<font color="#F5A623" size="8">AI-Powered Property Health Assessment</font>',
                  ParagraphStyle('hdr', fontName='Helvetica-Bold', fontSize=13,
                                 textColor=WHITE, alignment=TA_CENTER)),
        Paragraph('<font color="white" size="8">UrbanRoof Private Limited<br/>'
                  'info@urbanroof.in<br/>+91-8925-805-805</font>', subtitle_style)
    ]]
    header_table = Table(header_data, colWidths=[45*mm, 105*mm, 55*mm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -1), 3, GOLD),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    # ── PARSE AND RENDER MARKDOWN ─────────────────────────────────────────
    lines = ddr_text.split('\n')
    i = 0
    current_table_rows = []
    in_table = False

    def flush_table():
        nonlocal current_table_rows, in_table
        if not current_table_rows:
            in_table = False
            return
        # Parse header and data rows
        rows = []
        for ri, row_text in enumerate(current_table_rows):
            cells = [c.strip() for c in row_text.strip('|').split('|')]
            if all(set(c.strip()) <= set('-: ') for c in cells):
                continue  # separator row
            style = bold_body if ri == 0 else body_style
            parsed = [Paragraph(md_to_xml(c), style) for c in cells]
            rows.append(parsed)

        if not rows:
            in_table = False
            current_table_rows = []
            return

        ncols = len(rows[0])
        page_width = A4[0] - 36*mm
        col_w = page_width / ncols

        tbl = Table(rows, colWidths=[col_w] * ncols, repeatRows=1)
        tbl_style = [
            ('BACKGROUND', (0, 0), (-1, 0), DARK),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('GRID', (0, 0), (-1, -1), 0.5, LGREY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, BGCELL]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]
        tbl.setStyle(TableStyle(tbl_style))
        story.append(tbl)
        story.append(Spacer(1, 6))
        current_table_rows = []
        in_table = False

    def md_to_xml(text):
        """Convert basic markdown bold/italic to ReportLab XML."""
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        # Severity colours
        text = text.replace('🔴 HIGH', '<font color="#E74C3C"><b>🔴 HIGH</b></font>')
        text = text.replace('🟡 MEDIUM', '<font color="#E67E22"><b>🟡 MEDIUM</b></font>')
        text = text.replace('🟢 LOW', '<font color="#27AE60"><b>🟢 LOW</b></font>')
        return text

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Table rows
        if stripped.startswith('|'):
            if not in_table:
                in_table = True
            current_table_rows.append(stripped)
            i += 1
            continue
        else:
            if in_table:
                flush_table()

        if not stripped:
            story.append(Spacer(1, 4))
        elif stripped.startswith('# '):
            # Top-level title — skip (already in header banner)
            pass
        elif stripped.startswith('## '):
            text = stripped[3:].strip()
            story.append(Spacer(1, 6))
            story.append(Paragraph(f'<font color="white"> {text} </font>', h1_style))
            story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=6))
        elif stripped.startswith('### '):
            text = stripped[4:].strip()
            story.append(Paragraph(md_to_xml(text), h2_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=LGREY, spaceAfter=3))
        elif stripped.startswith('#### '):
            text = stripped[5:].strip()
            story.append(Paragraph(md_to_xml(text), h3_style))
        elif stripped.startswith('---'):
            story.append(HRFlowable(width="100%", thickness=0.5,
                color=LGREY, spaceBefore=4, spaceAfter=4))
        elif stripped.startswith('- ') or stripped.startswith('* '):
            text = stripped[2:].strip()
            story.append(Paragraph(f'• {md_to_xml(text)}', bullet_style))
        elif re.match(r'^\d+\.\s', stripped):
            text = re.sub(r'^\d+\.\s', '', stripped)
            num = stripped.split('.')[0]
            story.append(Paragraph(f'{num}. {md_to_xml(text)}', bullet_style))
        elif stripped.startswith('**') and stripped.endswith('**') and stripped.count('**') == 2:
            story.append(Paragraph(f'<b>{md_to_xml(stripped[2:-2])}</b>', bold_body))
        elif stripped.startswith('*') and stripped.endswith('*') and stripped.count('*') == 2:
            story.append(Paragraph(f'<i>{md_to_xml(stripped[1:-1])}</i>', body_style))
        else:
            story.append(Paragraph(md_to_xml(stripped), body_style))

        i += 1

    if in_table:
        flush_table()

    # ── FOOTER ───────────────────────────────────────────────────────────
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1.5, color=GOLD))
    story.append(Paragraph(
        "Generated by UrbanRoof AI DDR System &nbsp;|&nbsp; UrbanRoof Private Limited "
        "&nbsp;|&nbsp; www.urbanroof.in &nbsp;|&nbsp; +91-8925-805-805",
        footer_style
    ))

    doc.build(story)
    return buffer.getvalue()