"""
HD Hauling & Grading - Pricing Breakdown PDF Generator

Internal confidential document showing cost breakdown for proposals.
Shows materials, labor, trucking, markup per line item.
"""
import json, sys, os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, KeepTogether)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas as pdfcanvas

RED     = colors.HexColor('#CC0000')
BLACK   = colors.HexColor('#111111')
WHITE   = colors.HexColor('#FFFFFF')
LGRAY   = colors.HexColor('#F4F4F4')
DGRAY   = colors.HexColor('#555555')
TBLBORD = colors.HexColor('#CCCCCC')
ROWALT  = colors.HexColor('#F8F8F8')
COLHDR  = colors.HexColor('#3A3A3A')

W, H    = letter
_DIR    = os.path.dirname(os.path.abspath(__file__))
LOGO    = os.path.join(_DIR, 'hd_logo.png')
if not os.path.exists(LOGO):
    LOGO = os.path.join(_DIR, 'hd_logo_cropped.png')
LM = RM = 0.5 * inch
TM = 1.05 * inch
BM = 0.6  * inch


class PBCanvas(pdfcanvas.Canvas):
    def __init__(self, *args, **kwargs):
        self._date = kwargs.pop('date_str', '')
        super().__init__(*args, **kwargs)
        self._pages = []

    def showPage(self):
        self._pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._pages)
        for i, state in enumerate(self._pages):
            self.__dict__.update(state)
            self._page_index = i + 1
            self._page_total = total
            self._draw_header()
            self._draw_footer()
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)

    def _draw_header(self):
        self.saveState()
        if os.path.exists(LOGO):
            self.drawImage(LOGO, LM, H - 0.82*inch, width=1.25*inch, height=0.52*inch,
                           preserveAspectRatio=True, mask='auto')
        self.setFont('Helvetica-Bold', 17)
        self.setFillColor(BLACK)
        self.drawRightString(W - RM, H - 0.52*inch, 'PRICING BREAKDOWN')
        self.setFont('Helvetica', 9)
        self.setFillColor(DGRAY)
        self.drawRightString(W - RM, H - 0.68*inch, self._date)
        self.setStrokeColor(BLACK)
        self.setLineWidth(1.0)
        self.line(LM, H - 0.88*inch, W - RM, H - 0.88*inch)
        self.restoreState()

    def _draw_footer(self):
        self.saveState()
        self.setFont('Helvetica-Bold', 7)
        self.setFillColor(RED)
        self.drawCentredString(W / 2, BM * 0.65, 'CONFIDENTIAL \u2014 INTERNAL USE ONLY')
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#AAAAAA'))
        self.drawCentredString(W / 2, BM * 0.35, f'Page {self._page_index} of {self._page_total}')
        self.restoreState()


def canvas_maker(date_str):
    class _C(PBCanvas):
        def __init__(self, *a, **kw):
            kw['date_str'] = date_str
            super().__init__(*a, **kw)
    return _C


def _fi(n):
    return '{:,}'.format(round(n))


def build(data, out_path):
    cw = W - LM - RM
    date_str = data.get('date', '')

    doc = SimpleDocTemplate(
        out_path, pagesize=letter,
        title='Pricing Breakdown',
        author='HD Hauling & Grading',
        leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM
    )

    story = []

    # Styles
    lbl_s = ParagraphStyle('lbl', fontName='Helvetica-Bold', fontSize=8, textColor=BLACK)
    val_s = ParagraphStyle('val', fontName='Helvetica', fontSize=8, textColor=DGRAY, leading=11)
    sec_s = ParagraphStyle('sec', fontName='Helvetica-Bold', fontSize=10, textColor=WHITE, alignment=TA_CENTER)
    hdr_s = ParagraphStyle('hdr', fontName='Helvetica-Bold', fontSize=8, textColor=WHITE)
    hdr_r = ParagraphStyle('hdrr', fontName='Helvetica-Bold', fontSize=8, textColor=WHITE, alignment=TA_RIGHT)
    cell_s = ParagraphStyle('cell', fontName='Helvetica', fontSize=8, textColor=BLACK, alignment=TA_RIGHT)
    cell_l = ParagraphStyle('celll', fontName='Helvetica', fontSize=8, textColor=BLACK)
    cell_b = ParagraphStyle('cellb', fontName='Helvetica-Bold', fontSize=8, textColor=BLACK, alignment=TA_RIGHT)
    name_s = ParagraphStyle('name', fontName='Helvetica-Bold', fontSize=9, textColor=BLACK)

    # ── Project Info ──
    proj_name = data.get('project_name', '')
    client = data.get('client_name', '')
    address = data.get('address', '')
    sender = data.get('sender_name', '')

    info_parts = []
    if proj_name: info_parts.append(f'<b>Project:</b> {proj_name}')
    if client: info_parts.append(f'<b>Client:</b> {client}')
    if address: info_parts.append(f'<b>Address:</b> {address}')
    if sender: info_parts.append(f'<b>Prepared by:</b> {sender}')
    if date_str: info_parts.append(f'<b>Date:</b> {date_str}')

    if info_parts:
        info_text = '&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;'.join(info_parts)
        story.append(Paragraph(info_text, ParagraphStyle('info', fontName='Helvetica', fontSize=9,
                                                          textColor=DGRAY, leading=14)))
        story.append(Spacer(1, 0.15*inch))

    # ── Asphalt / Stone Breakdown ──
    items = data.get('asphalt_items', [])
    if items:
        # Banner
        ban = Table([[Paragraph('ASPHALT & STONE', sec_s)]], colWidths=[cw])
        ban.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), RED),
                                  ('TOPPADDING', (0,0), (-1,-1), 5),
                                  ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
        story.append(ban)

        # Header
        cols = [cw*0.22, cw*0.06, cw*0.06, cw*0.08, cw*0.06, cw*0.10, cw*0.10, cw*0.10, cw*0.10, cw*0.06, cw*0.06]
        rows = [[
            Paragraph('ITEM', hdr_s), Paragraph('SY', hdr_r), Paragraph('DEPTH', hdr_r),
            Paragraph('TONS', hdr_r), Paragraph('DAYS', hdr_r),
            Paragraph('MATERIAL', hdr_r), Paragraph('LABOR', hdr_r),
            Paragraph('TRUCKING', hdr_r), Paragraph('BID', hdr_r),
            Paragraph('$/TON', hdr_r), Paragraph('MU%', hdr_r)
        ]]
        for item in items:
            cost = item.get('material', 0) + item.get('labor', 0) + item.get('trucking', 0)
            mu = ((item.get('bid', 0) - cost) / cost * 100) if cost > 0 else 0
            ppt = item.get('bid', 0) / item.get('tons', 1) if item.get('tons', 0) > 0 else 0
            rows.append([
                Paragraph(item.get('name', ''), cell_l),
                Paragraph(_fi(item.get('sy', 0)), cell_s),
                Paragraph(str(item.get('depth', '')) + '"', cell_s),
                Paragraph(_fi(item.get('tons', 0)), cell_s),
                Paragraph(str(item.get('days', 0)), cell_s),
                Paragraph('$' + _fi(item.get('material', 0)), cell_s),
                Paragraph('$' + _fi(item.get('labor', 0)), cell_s),
                Paragraph('$' + _fi(item.get('trucking', 0)), cell_s),
                Paragraph('$' + _fi(item.get('bid', 0)), cell_b),
                Paragraph('$' + f"{ppt:.0f}", cell_s),
                Paragraph(f"{mu:.1f}%", cell_s),
            ])

        tbl = Table(rows, colWidths=cols)
        ts = [
            ('BACKGROUND', (0,0), (-1,0), COLHDR),
            ('TOPPADDING', (0,0), (-1,0), 5), ('BOTTOMPADDING', (0,0), (-1,0), 5),
            ('TOPPADDING', (0,1), (-1,-1), 4), ('BOTTOMPADDING', (0,1), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6), ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('LINEBELOW', (0,1), (-1,-1), 0.3, TBLBORD),
            ('BOX', (0,0), (-1,-1), 0.5, TBLBORD),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]
        for i in range(1, len(rows)):
            if i % 2 == 0:
                ts.append(('BACKGROUND', (0,i), (-1,i), ROWALT))
        tbl.setStyle(TableStyle(ts))
        story.append(tbl)
        story.append(Spacer(1, 0.15*inch))

    # ── Concrete Breakdown ──
    conc_items = data.get('concrete_items', [])
    if conc_items:
        ban = Table([[Paragraph('CONCRETE', sec_s)]], colWidths=[cw])
        ban.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), RED),
                                  ('TOPPADDING', (0,0), (-1,-1), 5),
                                  ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
        story.append(ban)

        cols = [cw*0.28, cw*0.10, cw*0.08, cw*0.10, cw*0.12, cw*0.12, cw*0.12, cw*0.08]
        rows = [[
            Paragraph('ITEM', hdr_s), Paragraph('QTY', hdr_r), Paragraph('UNIT', hdr_r),
            Paragraph('CY', hdr_r), Paragraph('MATERIAL', hdr_r),
            Paragraph('LABOR', hdr_r), Paragraph('BID', hdr_r), Paragraph('MU%', hdr_r)
        ]]
        for item in conc_items:
            cost = item.get('material', 0) + item.get('labor', 0)
            mu = ((item.get('bid', 0) - cost) / cost * 100) if cost > 0 else 0
            rows.append([
                Paragraph(item.get('name', ''), cell_l),
                Paragraph(_fi(item.get('qty', 0)), cell_s),
                Paragraph(item.get('unit', 'LF'), cell_s),
                Paragraph(f"{item.get('cy', 0):.1f}", cell_s),
                Paragraph('$' + _fi(item.get('material', 0)), cell_s),
                Paragraph('$' + _fi(item.get('labor', 0)), cell_s),
                Paragraph('$' + _fi(item.get('bid', 0)), cell_b),
                Paragraph(f"{mu:.1f}%", cell_s),
            ])

        tbl = Table(rows, colWidths=cols)
        ts = [
            ('BACKGROUND', (0,0), (-1,0), COLHDR),
            ('TOPPADDING', (0,0), (-1,0), 5), ('BOTTOMPADDING', (0,0), (-1,0), 5),
            ('TOPPADDING', (0,1), (-1,-1), 4), ('BOTTOMPADDING', (0,1), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6), ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('LINEBELOW', (0,1), (-1,-1), 0.3, TBLBORD),
            ('BOX', (0,0), (-1,-1), 0.5, TBLBORD),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]
        for i in range(1, len(rows)):
            if i % 2 == 0:
                ts.append(('BACKGROUND', (0,i), (-1,i), ROWALT))
        tbl.setStyle(TableStyle(ts))
        story.append(tbl)
        story.append(Spacer(1, 0.15*inch))

    # ── Additional Items ──
    extra_items = data.get('extra_items', [])
    if extra_items:
        ban = Table([[Paragraph('ADDITIONAL ITEMS', sec_s)]], colWidths=[cw])
        ban.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), RED),
                                  ('TOPPADDING', (0,0), (-1,-1), 5),
                                  ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
        story.append(ban)

        cols = [cw*0.40, cw*0.12, cw*0.12, cw*0.18, cw*0.18]
        rows = [[
            Paragraph('ITEM', hdr_s), Paragraph('QTY', hdr_r), Paragraph('UNIT', hdr_r),
            Paragraph('PRICE', hdr_r), Paragraph('SUBTOTAL', hdr_r)
        ]]
        for item in extra_items:
            rows.append([
                Paragraph(item.get('name', ''), cell_l),
                Paragraph(str(item.get('qty', 0)), cell_s),
                Paragraph(item.get('unit', ''), cell_s),
                Paragraph('$' + f"{item.get('price', 0):,.2f}", cell_s),
                Paragraph('$' + _fi(item.get('subtotal', 0)), cell_b),
            ])

        tbl = Table(rows, colWidths=cols)
        ts = [
            ('BACKGROUND', (0,0), (-1,0), COLHDR),
            ('TOPPADDING', (0,0), (-1,0), 5), ('BOTTOMPADDING', (0,0), (-1,0), 5),
            ('TOPPADDING', (0,1), (-1,-1), 4), ('BOTTOMPADDING', (0,1), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6), ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('LINEBELOW', (0,1), (-1,-1), 0.3, TBLBORD),
            ('BOX', (0,0), (-1,-1), 0.5, TBLBORD),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]
        for i in range(1, len(rows)):
            if i % 2 == 0:
                ts.append(('BACKGROUND', (0,i), (-1,i), ROWALT))
        tbl.setStyle(TableStyle(ts))
        story.append(tbl)
        story.append(Spacer(1, 0.15*inch))

    # ── Summary ──
    totals = data.get('totals', {})
    if totals:
        sum_s = ParagraphStyle('sum_l', fontName='Helvetica', fontSize=10, textColor=DGRAY)
        sum_b = ParagraphStyle('sum_r', fontName='Helvetica-Bold', fontSize=10, textColor=BLACK, alignment=TA_RIGHT)
        sum_hdr = ParagraphStyle('sum_h', fontName='Helvetica-Bold', fontSize=11, textColor=BLACK, alignment=TA_RIGHT)

        sum_rows = []
        if totals.get('material'): sum_rows.append([Paragraph('Materials', sum_s), Paragraph('$' + _fi(totals['material']), sum_b)])
        if totals.get('labor'): sum_rows.append([Paragraph('Labor', sum_s), Paragraph('$' + _fi(totals['labor']), sum_b)])
        if totals.get('trucking'): sum_rows.append([Paragraph('Trucking', sum_s), Paragraph('$' + _fi(totals['trucking']), sum_b)])
        cost = totals.get('cost', 0)
        if cost: sum_rows.append([Paragraph('Total Cost', sum_s), Paragraph('$' + _fi(cost), sum_b)])
        if totals.get('mobilization'): sum_rows.append([Paragraph('Mobilization', sum_s), Paragraph('$' + _fi(totals['mobilization']), sum_b)])
        bid = totals.get('bid', 0)
        if bid:
            sum_rows.append([Paragraph('Bid Total', ParagraphStyle('bt', fontName='Helvetica-Bold', fontSize=11, textColor=BLACK)),
                             Paragraph('$' + _fi(bid), sum_hdr)])
        markup = totals.get('markup_pct', 0)
        if markup: sum_rows.append([Paragraph('Markup', sum_s), Paragraph(f"{markup:.1f}%", sum_b)])
        profit = totals.get('profit', 0)
        if profit: sum_rows.append([Paragraph('Gross Profit', sum_s), Paragraph('$' + _fi(profit), sum_b)])

        if sum_rows:
            t = Table(sum_rows, colWidths=[cw*0.60, cw*0.40])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), LGRAY),
                ('BOX', (0,0), (-1,-1), 0.5, TBLBORD),
                ('LINEBELOW', (0,0), (-1,-2), 0.3, TBLBORD),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
                ('RIGHTPADDING', (0,0), (-1,-1), 12),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(t)

    doc.build(story, canvasmaker=canvas_maker(date_str))


if __name__ == '__main__':
    data = json.loads(sys.argv[1])
    out = sys.argv[2] if len(sys.argv) > 2 else 'pricing_breakdown.pdf'
    build(data, out)
