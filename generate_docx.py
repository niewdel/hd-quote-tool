"""
generate_docx.py  –  HD Hauling & Grading Word proposal generator
Uses python-docx (pip install python-docx)
"""
import io, os, base64, tempfile
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

RED   = RGBColor(0xCC, 0x00, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK  = RGBColor(0x1A, 0x1A, 0x1A)
LGRAY = RGBColor(0xF5, 0xF5, 0xF5)
MGRAY = RGBColor(0x88, 0x88, 0x88)

LOGO_PATH = os.path.join(os.path.dirname(__file__), 'hd_logo.png')


def _set_cell_bg(cell, hex_color):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  hex_color)
    tcPr.append(shd)


def _para_fmt(para, bold=False, size=11, color=None, align=None):
    run = para.runs[0] if para.runs else para.add_run()
    run.bold = bold
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = color
    if align:
        para.alignment = align
    return run


def _add_red_heading(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run(text.upper())
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = RED
    return p


def _add_kv(doc, label, value, bold_val=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after  = Pt(1)
    r1 = p.add_run(f"{label}: ")
    r1.bold = True
    r1.font.size = Pt(10)
    r2 = p.add_run(str(value or ''))
    r2.bold = bold_val
    r2.font.size = Pt(10)


def build(data):
    doc = Document()

    # ── Page margins ──────────────────────────────────────────────────────────
    for section in doc.sections:
        section.top_margin    = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin   = Inches(1.0)
        section.right_margin  = Inches(1.0)

    # ── Cover / Header ────────────────────────────────────────────────────────
    # Logo
    if os.path.exists(LOGO_PATH):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run()
        run.add_picture(LOGO_PATH, width=Inches(2.0))

    # Title
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    r = p.add_run('PAVING PROPOSAL & CONTRACT')
    r.bold = True
    r.font.size = Pt(18)
    r.font.color.rgb = RED
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()  # spacer

    # ── Project Info ──────────────────────────────────────────────────────────
    _add_red_heading(doc, 'Project Information')

    tbl = doc.add_table(rows=0, cols=2)
    tbl.style = 'Table Grid'
    tbl.autofit = False
    tbl.columns[0].width = Inches(2.8)
    tbl.columns[1].width = Inches(4.6)

    def _tbl_row(label, value):
        row = tbl.add_row()
        row.cells[0].text = label
        row.cells[1].text = str(value or '')
        for i, cell in enumerate(row.cells):
            for para in cell.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(10)
                    if i == 0:
                        run.bold = True
            _set_cell_bg(cell, 'F5F5F5' if i == 0 else 'FFFFFF')

    _tbl_row('Project Name',   data.get('project_name', ''))
    _tbl_row('Client',         data.get('client_name', ''))
    _tbl_row('Address',        data.get('address', ''))
    _tbl_row('City / State',   data.get('city_state', ''))
    _tbl_row('Date',           data.get('date', ''))
    _tbl_row('Prepared By',    data.get('sender_name', 'HD Hauling & Grading'))
    _tbl_row('Phone',          data.get('sender_phone', ''))
    _tbl_row('Email',          data.get('sender_email', ''))

    doc.add_paragraph()

    # Notes
    notes = data.get('notes', '').strip()
    if notes:
        _add_red_heading(doc, 'Project Notes')
        p = doc.add_paragraph(notes)
        p.paragraph_format.space_after = Pt(6)
        for run in p.runs:
            run.font.size = Pt(10)
        doc.add_paragraph()

    # ── Bid Items ─────────────────────────────────────────────────────────────
    _add_red_heading(doc, 'Bid Items')

    headers = ['Item', 'Description', 'Qty', 'Unit', 'Unit Price', 'Subtotal']
    col_w   = [Inches(1.5), Inches(2.5), Inches(0.7), Inches(0.6), Inches(1.0), Inches(1.1)]

    bid_tbl = doc.add_table(rows=1, cols=6)
    bid_tbl.style = 'Table Grid'
    bid_tbl.autofit = False
    for i, w in enumerate(col_w):
        bid_tbl.columns[i].width = w

    # Header row
    hdr_row = bid_tbl.rows[0]
    for i, h in enumerate(headers):
        cell = hdr_row.cells[i]
        cell.text = h
        _set_cell_bg(cell, '1A1A1A')
        for para in cell.paragraphs:
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in para.runs:
                run.bold = True
                run.font.size = Pt(9)
                run.font.color.rgb = WHITE

    # Data rows
    line_items = data.get('line_items', [])
    for item in line_items:
        row = bid_tbl.add_row()
        vals = [
            item.get('name', ''),
            item.get('description', ''),
            f"{item.get('qty', 0):,.2f}".rstrip('0').rstrip('.'),
            item.get('unit', ''),
            f"${item.get('price', 0):,.2f}",
            f"${item.get('subtotal', 0):,.2f}",
        ]
        for i, v in enumerate(vals):
            row.cells[i].text = v
            align = WD_ALIGN_PARAGRAPH.RIGHT if i >= 2 else WD_ALIGN_PARAGRAPH.LEFT
            for para in row.cells[i].paragraphs:
                para.alignment = align
                for run in para.runs:
                    run.font.size = Pt(9)

    doc.add_paragraph()

    # ── Total ─────────────────────────────────────────────────────────────────
    total = data.get('total', 0)
    tot_tbl = doc.add_table(rows=1, cols=2)
    tot_tbl.style = 'Table Grid'
    tot_tbl.autofit = False
    tot_tbl.columns[0].width = Inches(5.9)
    tot_tbl.columns[1].width = Inches(1.5)

    tot_row = tot_tbl.rows[0]
    tot_row.cells[0].text = 'TOTAL BID PRICE:'
    tot_row.cells[1].text = f'${total:,.2f}'
    for i, cell in enumerate(tot_row.cells):
        _set_cell_bg(cell, 'CC0000')
        for para in cell.paragraphs:
            para.alignment = WD_ALIGN_PARAGRAPH.RIGHT if i == 1 else WD_ALIGN_PARAGRAPH.LEFT
            for run in para.runs:
                run.bold = True
                run.font.size = Pt(14)
                run.font.color.rgb = WHITE

    doc.add_paragraph()

    # ── Site Plan ─────────────────────────────────────────────────────────────
    site_plan_b64 = data.get('site_plan_image', '')
    if site_plan_b64 and ',' in site_plan_b64:
        _add_red_heading(doc, 'Site Plan')
        try:
            img_data = base64.b64decode(site_plan_b64.split(',')[1])
            img_ext  = site_plan_b64.split(';')[0].split('/')[1] if ';' in site_plan_b64 else 'png'
            with tempfile.NamedTemporaryFile(suffix=f'.{img_ext}', delete=False) as tmp:
                tmp.write(img_data)
                tmp_path = tmp.name
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run()
            run.add_picture(tmp_path, width=Inches(6.5))
            os.unlink(tmp_path)
        except Exception:
            p = doc.add_paragraph('[Site plan image could not be embedded]')
        doc.add_paragraph()

    # ── Overage Unit Prices ───────────────────────────────────────────────────
    unit_prices = data.get('unit_prices', [])
    if unit_prices:
        _add_red_heading(doc, 'Paving Overage Unit Prices')
        up_tbl = doc.add_table(rows=1, cols=2)
        up_tbl.style = 'Table Grid'
        up_tbl.autofit = False
        up_tbl.columns[0].width = Inches(5.9)
        up_tbl.columns[1].width = Inches(1.5)

        # header
        h_row = up_tbl.rows[0]
        h_row.cells[0].text = 'Description'
        h_row.cells[1].text = 'Rate'
        for cell in h_row.cells:
            _set_cell_bg(cell, 'F5F5F5')
            for para in cell.paragraphs:
                for run in para.runs:
                    run.bold = True
                    run.font.size = Pt(9)

        for up in unit_prices:
            row = up_tbl.add_row()
            row.cells[0].text = up.get('name', '')
            row.cells[1].text = f"${up.get('rate', 0):,.2f}"
            row.cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
            for cell in row.cells:
                for para in cell.paragraphs:
                    for run in para.runs:
                        run.font.size = Pt(9)
        doc.add_paragraph()

    # ── Client Approval ───────────────────────────────────────────────────────
    _add_red_heading(doc, 'Client Approval')

    p = doc.add_paragraph(f'Approved Value:  ${total:,.2f}')
    p.paragraph_format.space_after = Pt(14)
    for run in p.runs:
        run.bold = True
        run.font.size = Pt(11)

    def _sig_line(label, width_in=3.5):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after  = Pt(2)
        r = p.add_run(f'{label}:  {"_" * 45}')
        r.font.size = Pt(10)

    _sig_line('Full Name')
    _sig_line('Date Signed')
    _sig_line('Signature')

    doc.add_paragraph()

    # ── Terms note ────────────────────────────────────────────────────────────
    _add_red_heading(doc, 'Terms & Conditions')
    p = doc.add_paragraph(
        'This Proposal and Contract becomes legally binding upon execution by both the '
        'Customer/Purchaser and HD Hauling & Grading. All work performed per scope outlined '
        'above. One (1) year warranty on materials and workmanship. Full terms available on request.'
    )
    for run in p.runs:
        run.font.size = Pt(9)
        run.font.color.rgb = MGRAY

    # ── Save to buffer ────────────────────────────────────────────────────────
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


if __name__ == '__main__':
    import json, sys
    data = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    buf = build(data)
    out = 'test_proposal.docx'
    with open(out, 'wb') as f:
        f.write(buf.read())
    print(f'Written: {out}')
