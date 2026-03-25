"""
HD Hauling & Grading - Report PDF Generator
Generates one-page executive summary style PDFs from report data.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether, PageBreak
)
import os, json, re
from html.parser import HTMLParser

W, H = letter
LM = RM = 0.6*inch
TM = BM = 0.65*inch

RED    = colors.HexColor('#CC0000')
BLACK  = colors.HexColor('#111111')
DGRAY  = colors.HexColor('#555555')
LGRAY  = colors.HexColor('#F5F5F5')
TBLBRD = colors.HexColor('#D0D0D0')
GREEN  = colors.HexColor('#27500A')
WHITE  = colors.white

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hd_logo.png')


class HTMLTextExtractor(HTMLParser):
    """Simple HTML to text converter for report content."""
    def __init__(self):
        super().__init__()
        self.result = []
        self.tables = []
        self._in_table = False
        self._current_table = []
        self._current_row = []
        self._current_cell = ''
        self._in_th = False
        self._in_td = False

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self._in_table = True
            self._current_table = []
        elif tag == 'tr':
            self._current_row = []
        elif tag == 'th':
            self._in_th = True
            self._current_cell = ''
        elif tag == 'td':
            self._in_td = True
            self._current_cell = ''
        elif tag == 'br':
            if not self._in_table:
                self.result.append('\n')

    def handle_endtag(self, tag):
        if tag == 'table':
            self._in_table = False
            if self._current_table:
                self.tables.append(self._current_table)
        elif tag == 'tr':
            if self._current_row:
                self._current_table.append(self._current_row)
        elif tag in ('th', 'td'):
            self._current_row.append(self._current_cell.strip())
            self._in_th = False
            self._in_td = False
        elif tag in ('div', 'p') and not self._in_table:
            self.result.append('\n')

    def handle_data(self, data):
        if self._in_th or self._in_td:
            self._current_cell += data
        else:
            self.result.append(data)

    def get_text(self):
        return ''.join(self.result).strip()


def extract_report_data(html):
    """Extract text sections and tables from report HTML."""
    parser = HTMLTextExtractor()
    parser.feed(html)
    return parser.get_text(), parser.tables


def build(data, out_path):
    report_name = data.get('report_name', 'Report')
    date_range = data.get('date_range', '')
    generated_date = data.get('generated_date', '')
    html = data.get('html', '')

    cw = W - LM - RM
    doc = SimpleDocTemplate(out_path, pagesize=letter,
        title=f'HD Report - {report_name}',
        author='HD Hauling & Grading',
        leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM)

    # Styles
    title_style = ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=16, textColor=RED,
                                  spaceAfter=4)
    subtitle = ParagraphStyle('sub', fontName='Helvetica', fontSize=10, textColor=DGRAY,
                               spaceAfter=12)
    body = ParagraphStyle('body', fontName='Helvetica', fontSize=9, textColor=BLACK, leading=13)
    bold = ParagraphStyle('bold', fontName='Helvetica-Bold', fontSize=9, textColor=BLACK, leading=13)
    small = ParagraphStyle('small', fontName='Helvetica', fontSize=8, textColor=DGRAY, leading=11)
    th_style = ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=WHITE, leading=11)
    td_style = ParagraphStyle('td', fontName='Helvetica', fontSize=8, textColor=BLACK, leading=11)
    td_right = ParagraphStyle('tdr', fontName='Helvetica', fontSize=8, textColor=BLACK, leading=11,
                               alignment=TA_RIGHT)
    section_hdr = ParagraphStyle('sh', fontName='Helvetica-Bold', fontSize=11, textColor=BLACK,
                                  spaceBefore=12, spaceAfter=6)

    elements = []

    # Header with logo
    header_data = []
    if os.path.exists(LOGO_PATH):
        from reportlab.platypus import Image
        logo = Image(LOGO_PATH, width=1.2*inch, height=0.5*inch)
        header_data.append([logo, ''])
    header_data.append([
        Paragraph('HD HAULING &amp; GRADING', title_style),
        Paragraph(f'Generated {generated_date}', ParagraphStyle('r', fontName='Helvetica',
                  fontSize=8, textColor=DGRAY, alignment=TA_RIGHT))
    ])
    header_data.append([
        Paragraph(f'{report_name} &mdash; {date_range}', subtitle),
        ''
    ])
    ht = Table(header_data, colWidths=[cw*0.7, cw*0.3])
    ht.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
    ]))
    elements.append(ht)
    elements.append(HRFlowable(width='100%', thickness=2, color=RED, spaceAfter=12))

    # Extract content from HTML
    text_content, tables = extract_report_data(html)

    # Render text sections
    lines = text_content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Skip lines that are just styling artifacts
        if line in ('·',) or len(line) < 2:
            continue
        # Detect stat-like lines (number + label)
        elements.append(Paragraph(line.replace('&', '&amp;'), body))

    # Render tables
    for tbl_data in tables:
        if not tbl_data:
            continue
        elements.append(Spacer(1, 8))

        # Determine column widths
        n_cols = max(len(row) for row in tbl_data)
        col_w = cw / max(n_cols, 1)
        col_widths = [col_w] * n_cols

        # Build table rows
        rows = []
        for i, row in enumerate(tbl_data):
            styled_row = []
            for j, cell in enumerate(row):
                cell_text = cell.replace('&', '&amp;')
                if i == 0:
                    styled_row.append(Paragraph(cell_text, th_style))
                else:
                    # Right-align cells that look like numbers/money
                    if cell.startswith('$') or cell.endswith('%') or cell.replace(',','').replace('.','').replace('-','').replace('+','').isdigit():
                        styled_row.append(Paragraph(cell_text, td_right))
                    else:
                        styled_row.append(Paragraph(cell_text, td_style))
            # Pad to n_cols
            while len(styled_row) < n_cols:
                styled_row.append('')
            rows.append(styled_row)

        if not rows:
            continue

        t = Table(rows, colWidths=col_widths, repeatRows=1)
        style_cmds = [
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('GRID', (0,0), (-1,-1), 0.5, TBLBRD),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]
        # Header row styling
        if len(rows) > 0:
            style_cmds.append(('BACKGROUND', (0,0), (-1,0), RED))
            style_cmds.append(('TEXTCOLOR', (0,0), (-1,0), WHITE))
        # Alternating row colors
        for r_idx in range(1, len(rows)):
            if r_idx % 2 == 0:
                style_cmds.append(('BACKGROUND', (0,r_idx), (-1,r_idx), LGRAY))

        t.setStyle(TableStyle(style_cmds))
        elements.append(t)

    # Footer
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width='100%', thickness=1, color=TBLBRD, spaceAfter=6))
    elements.append(Paragraph('CONFIDENTIAL — HD Hauling &amp; Grading Internal Report',
                              ParagraphStyle('foot', fontName='Helvetica', fontSize=7,
                                            textColor=DGRAY, alignment=TA_CENTER)))

    doc.build(elements)
    return out_path
