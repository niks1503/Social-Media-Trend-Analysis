"""
Script to convert the Interview Q&A Markdown file to a Word document.
Run: pip install python-docx && python convert_to_docx.py
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
import re
import os

MD_FILE = os.path.join(os.path.dirname(__file__),
                       "Social_Media_Trend_Analysis_NLP_Enhanced_Interview_QA.md")
DOCX_FILE = os.path.join(os.path.dirname(__file__),
                         "Social_Media_Trend_Analysis_NLP_Enhanced_Interview_QA.docx")


def set_cell_shading(cell, color_hex):
    """Set cell background color."""
    from docx.oxml.ns import qn
    from lxml import etree
    shading = etree.SubElement(cell._element.get_or_add_tcPr(), qn('w:shd'))
    shading.set(qn('w:fill'), color_hex)
    shading.set(qn('w:val'), 'clear')


def add_formatted_text(paragraph, text, bold=False, italic=False, code=False, color=None, size=None):
    """Add a run with formatting to a paragraph."""
    run = paragraph.add_run(text)
    run.bold = bold
    run.italic = italic
    if code:
        run.font.name = 'Consolas'
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)
    if color:
        run.font.color.rgb = color
    if size:
        run.font.size = size
    return run


def parse_inline_formatting(paragraph, text):
    """Parse inline markdown: **bold**, *italic*, `code`."""
    # Pattern: **bold**, *italic*, `code`, or plain text
    pattern = r'(\*\*.*?\*\*|\*.*?\*|`[^`]+`|[^*`]+)'
    parts = re.findall(pattern, text)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            add_formatted_text(paragraph, part[2:-2], bold=True)
        elif part.startswith('*') and part.endswith('*'):
            add_formatted_text(paragraph, part[1:-1], italic=True)
        elif part.startswith('`') and part.endswith('`'):
            add_formatted_text(paragraph, part[1:-1], code=True)
        else:
            paragraph.add_run(part)


def add_table_from_lines(doc, table_lines):
    """Parse markdown table lines and add a formatted table to the document."""
    rows_data = []
    for line in table_lines:
        line = line.strip().strip('|')
        cells = [c.strip() for c in line.split('|')]
        # Skip separator lines (e.g., |---|---|)
        if all(re.match(r'^[-:]+$', c) for c in cells):
            continue
        rows_data.append(cells)

    if not rows_data:
        return

    num_cols = max(len(r) for r in rows_data)
    table = doc.add_table(rows=len(rows_data), cols=num_cols)
    table.style = 'Light Grid Accent 1'

    for i, row_data in enumerate(rows_data):
        for j, cell_text in enumerate(row_data):
            if j < num_cols:
                cell = table.cell(i, j)
                cell.text = ''
                p = cell.paragraphs[0]
                parse_inline_formatting(p, cell_text)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.space_before = Pt(2)
                # Bold header row
                if i == 0:
                    for run in p.runs:
                        run.bold = True

    doc.add_paragraph()  # spacing


def build_docx():
    with open(MD_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    doc = Document()

    # ── Custom styles ──────────────────────────────────────────
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    style.paragraph_format.space_after = Pt(4)

    for level in range(1, 4):
        h_style = doc.styles[f'Heading {level}']
        h_style.font.name = 'Calibri'
        h_style.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)

    # ── Parse lines ────────────────────────────────────────────
    i = 0
    in_code_block = False
    code_lines = []
    table_lines = []
    in_table = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # ── Code blocks ───────────────────────────────────────
        if stripped.startswith('```'):
            if in_code_block:
                # End code block
                code_text = '\n'.join(code_lines)
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.3)
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(4)
                run = p.add_run(code_text)
                run.font.name = 'Consolas'
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)
                code_lines = []
                in_code_block = False
            else:
                # Flush any pending table
                if in_table and table_lines:
                    add_table_from_lines(doc, table_lines)
                    table_lines = []
                    in_table = False
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_lines.append(line.rstrip())
            i += 1
            continue

        # ── Tables ─────────────────────────────────────────────
        if stripped.startswith('|'):
            in_table = True
            table_lines.append(stripped)
            i += 1
            continue
        elif in_table:
            add_table_from_lines(doc, table_lines)
            table_lines = []
            in_table = False
            # Don't increment i — process current line normally

        # ── Blank / horizontal rule lines ──────────────────────
        if stripped == '' or stripped == '---':
            i += 1
            continue

        # ── Remove emojis (keep text clean in Word) ────────────
        clean_line = stripped

        # ── Headings ───────────────────────────────────────────
        if clean_line.startswith('# '):
            doc.add_heading(clean_line[2:], level=0)
            i += 1
            continue
        if clean_line.startswith('## '):
            doc.add_heading(clean_line[3:], level=1)
            i += 1
            continue
        if clean_line.startswith('### '):
            text = clean_line[4:]
            # Detect Q&A question lines
            if re.match(r'^Q\d+\.', text):
                p = doc.add_heading(text, level=2)
                p.runs[0].font.color.rgb = RGBColor(0x00, 0x47, 0x95)
            else:
                doc.add_heading(text, level=2)
            i += 1
            continue

        # ── Answer label ───────────────────────────────────────
        if clean_line.startswith('**Answer:**'):
            p = doc.add_paragraph()
            add_formatted_text(p, 'Answer:', bold=True,
                               color=RGBColor(0x00, 0x80, 0x00), size=Pt(11))
            i += 1
            continue

        # ── Bullet / list items ────────────────────────────────
        if clean_line.startswith('- ') or clean_line.startswith('* '):
            content = clean_line[2:]
            p = doc.add_paragraph(style='List Bullet')
            parse_inline_formatting(p, content)
            i += 1
            continue
        if re.match(r'^\d+\.\s', clean_line):
            content = re.sub(r'^\d+\.\s', '', clean_line)
            p = doc.add_paragraph(style='List Number')
            parse_inline_formatting(p, content)
            i += 1
            continue

        # ── Regular paragraphs ─────────────────────────────────
        p = doc.add_paragraph()
        parse_inline_formatting(p, clean_line)
        i += 1

    # Flush remaining table
    if in_table and table_lines:
        add_table_from_lines(doc, table_lines)

    # ── Save ───────────────────────────────────────────────────
    doc.save(DOCX_FILE)
    print(f"✅ Word document saved to:\n   {DOCX_FILE}")


if __name__ == '__main__':
    build_docx()
