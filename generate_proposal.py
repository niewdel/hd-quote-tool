import json, sys, os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, PageBreak, KeepTogether)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus.flowables import Flowable

RED     = colors.HexColor('#CC0000')
BLACK   = colors.HexColor('#000000')
WHITE   = colors.HexColor('#FFFFFF')
LGRAY   = colors.HexColor('#F4F4F4')
MGRAY   = colors.HexColor('#CCCCCC')
COLHDR  = colors.HexColor('#3A3A3A')
SECHDR  = colors.HexColor('#222222')
DGRAY   = colors.HexColor('#555555')
TBLBORD = colors.HexColor('#CCCCCC')
ROWALT  = colors.HexColor('#EEEEEE')

W, H    = letter
LOGO    = os.path.join(os.path.dirname(__file__), "hd_logo.png")
LM = RM = 0.5 * inch
TM = 1.05 * inch
BM = 0.6  * inch

def S():
    return {
        'info_hdr':    ParagraphStyle('ih',  fontName='Helvetica-Bold', fontSize=8,   textColor=BLACK, alignment=TA_CENTER),
        'info_lbl':    ParagraphStyle('il',  fontName='Helvetica-Bold', fontSize=8,   textColor=BLACK),
        'info_val':    ParagraphStyle('iv',  fontName='Helvetica',      fontSize=8,   textColor=DGRAY, leading=11),
        'info_val_sm': ParagraphStyle('ivs', fontName='Helvetica',      fontSize=7,   textColor=DGRAY, leading=10),
        'notes_hdr':   ParagraphStyle('nh',  fontName='Helvetica-Bold', fontSize=10,  textColor=WHITE, alignment=TA_CENTER),
        'notes_body':  ParagraphStyle('nb',  fontName='Helvetica',      fontSize=9,   textColor=DGRAY, leading=13),
        'bid_title':   ParagraphStyle('bt',  fontName='Helvetica-Bold', fontSize=11,  textColor=WHITE, alignment=TA_CENTER),
        'item_name':   ParagraphStyle('in2', fontName='Helvetica-Bold', fontSize=9,   textColor=BLACK, leading=12),
        'cell':        ParagraphStyle('c',   fontName='Helvetica',      fontSize=9,   textColor=BLACK, alignment=TA_RIGHT),
        'cell_b':      ParagraphStyle('cb',  fontName='Helvetica-Bold', fontSize=9,   textColor=BLACK, alignment=TA_RIGHT),
        'appr_hdr':    ParagraphStyle('ah',  fontName='Helvetica-Bold', fontSize=10,  textColor=WHITE),
        'appr_lbl':    ParagraphStyle('al',  fontName='Helvetica-Bold', fontSize=10,  textColor=BLACK),
        'appr_val':    ParagraphStyle('av',  fontName='Helvetica',      fontSize=9,   textColor=DGRAY),
        'tc_section':  ParagraphStyle('ts',  fontName='Helvetica-Bold', fontSize=9,   textColor=colors.HexColor('#CC0000')),
        'tc_body':     ParagraphStyle('tb',  fontName='Helvetica',      fontSize=8,   textColor=DGRAY, leading=14, spaceBefore=1, spaceAfter=5),
        'tc_bullet':   ParagraphStyle('tbul',fontName='Helvetica',      fontSize=8,   textColor=DGRAY, leading=14, leftIndent=16, bulletIndent=2, spaceBefore=1, spaceAfter=4),
    }

class HDCanvas(pdfcanvas.Canvas):
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
            self._page_total  = total
            if i > 0:
                self._draw_header()
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)
    def _draw_header(self):
        self.saveState()
        if os.path.exists(LOGO):
            self.drawImage(LOGO, LM, H - 0.82*inch, width=1.25*inch, height=0.52*inch,
                           preserveAspectRatio=True, mask='auto')
        self.setFont('Helvetica-Bold', 19)
        self.setFillColor(BLACK)
        self.drawRightString(W - RM, H - 0.52*inch, 'PROPOSAL & CONTRACT')
        self.setFont('Helvetica', 9)
        self.setFillColor(DGRAY)
        self.drawRightString(W - RM, H - 0.70*inch, self._date)
        self.setStrokeColor(BLACK)
        self.setLineWidth(1.0)
        self.line(LM, H - 0.88*inch, W - RM, H - 0.88*inch)
        # Page number bottom center
        total = len(self._pages)
        page_num = self._pages.index({k:v for k,v in self.__dict__.items()
                                       if k in self._pages[0]}) + 1 if False else None
        # simpler: derive from save order
        self.setFont('Helvetica', 8)
        self.setFillColor(colors.HexColor('#AAAAAA'))
        self.drawCentredString(W / 2, BM * 0.45, f'Page {self._page_index} of {self._page_total}')
        self.restoreState()


def canvas_maker(date_str):
    class _C(HDCanvas):
        def __init__(self, *a, **kw):
            kw['date_str'] = date_str
            super().__init__(*a, **kw)
    return _C

class CoverPage(Flowable):
    def __init__(self, data):
        super().__init__()
        self.data = data
    def wrap(self, aw, ah):
        self._aw, self._ah = aw, ah
        return aw, ah
    def draw(self):
        c  = self.canv
        d  = self.data
        aw = self._aw
        ah = self._ah
        mid = (W / 2) - LM

        if os.path.exists(LOGO):
            lw = 5.04 * inch
            lh = 2.1  * inch
            c.drawImage(LOGO, mid - lw/2, ah * 0.50, width=lw, height=lh,
                        preserveAspectRatio=True, mask='auto')

        c.setFont('Helvetica-Bold', 26)
        c.setFillColor(BLACK)
        c.drawCentredString(mid, ah * 0.454, d.get('project_name', 'Proposal'))

        c.setStrokeColor(MGRAY)
        c.setLineWidth(0.75)
        c.line(mid - 2.6*inch, ah * 0.437, mid + 2.6*inch, ah * 0.437)

        # ~15% more spacing below divider before subtitle
        c.setFont('Helvetica', 18)
        c.setFillColor(DGRAY)
        c.drawCentredString(mid, ah * 0.408, 'Proposal & Contract')

        date_str = d.get('date', '')
        if date_str:
            c.setFont('Helvetica', 13)
            c.setFillColor(colors.HexColor('#999999'))
            # ~15% more spacing between subtitle and date
            c.drawCentredString(mid, ah * 0.384, date_str)

        fy = 0.55 * inch
        c.setFont('Helvetica-Bold', 10)
        c.setFillColor(BLACK)
        c.drawString(LM, fy + 0.58*inch, 'Created by:')
        c.setFont('Helvetica', 10)
        c.setFillColor(DGRAY)
        c.drawString(LM, fy + 0.36*inch, d.get('sender_name', ''))
        c.drawString(LM, fy + 0.16*inch, d.get('company', 'HD Hauling & Grading'))

        rx = aw * 0.55
        c.setFont('Helvetica-Bold', 10)
        c.setFillColor(BLACK)
        c.drawString(rx, fy + 0.58*inch, 'Prepared for:')
        c.setFont('Helvetica', 10)
        c.setFillColor(DGRAY)
        c.drawString(rx, fy + 0.36*inch, d.get('client_name', ''))
        c.drawString(rx, fy + 0.16*inch, d.get('client_company', ''))

def info_block(data, st):
    """Three-column stacked layout. Each column has a header row then
    label-above-value pairs ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¢ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ no side-by-side label/value split, so
    long emails and addresses never wrap awkwardly."""

    lbl_s  = ParagraphStyle('ibl', fontName='Helvetica-Bold', fontSize=7,
                             textColor=DGRAY, leading=10, spaceBefore=4)
    val_s  = ParagraphStyle('iva', fontName='Helvetica',      fontSize=8,
                             textColor=BLACK, leading=11, spaceAfter=2)
    hdr_s  = ParagraphStyle('ihd', fontName='Helvetica-Bold', fontSize=8,
                             textColor=BLACK, alignment=TA_CENTER)

    def make_col(title, pairs):
        parts = [Paragraph(title, hdr_s)]
        for lbl, val in pairs:
            parts.append(Paragraph(lbl, lbl_s))
            parts.append(Paragraph(val or 'ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¢ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ', val_s))
        return parts

    from reportlab.platypus import Frame
    cw = (W - inch) / 3 - 2  # slight gap between cols

    def col_table(title, pairs):
        """Each column is its own single-cell table containing stacked paragraphs."""
        content = make_col(title, pairs)
        # Wrap in a single-cell table
        # Split into header row + content row so we can draw a rule between them
        hdr_para = content[0]   # Paragraph('Project/Sender/Client Information')
        body_content = content[1:]  # Spacer + label/value pairs

        inner = Table([
            [hdr_para],
            [body_content],
        ], colWidths=[cw - 2])
        inner.setStyle(TableStyle([
            ('LINEBELOW',    (0,0), (-1,0),  0.75, colors.HexColor('#CCCCCC')),
            ('BACKGROUND',   (0,0), (-1,0),  colors.HexColor('#F7F7F7')),
            ('TOPPADDING',   (0,0), (-1,0),  6),
            ('BOTTOMPADDING',(0,0), (-1,0),  5),
            ('LEFTPADDING',  (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING',   (0,1), (-1,1),  5),
            ('BOTTOMPADDING',(0,1), (-1,1),  6),
            ('VALIGN',       (0,0), (-1,-1), 'TOP'),
        ]))
        t = Table([[inner]], colWidths=[cw])
        t.setStyle(TableStyle([
            ('BOX',         (0,0),(-1,-1), 0.5, TBLBORD),
            ('TOPPADDING',  (0,0),(-1,-1), 0),
            ('BOTTOMPADDING',(0,0),(-1,-1),0),
            ('LEFTPADDING', (0,0),(-1,-1), 0),
            ('RIGHTPADDING',(0,0),(-1,-1), 0),
        ]))
        return t

    proj_t = col_table('Project Information', [
        ('Project Name', data.get('project_name','')),
        ('Street Address', data.get('address','')),
        ('City, State', data.get('city_state','')),
    ])
    send_t = col_table('Sender Information', [
        ('Name', data.get('sender_name','')),
        ('Email', data.get('sender_email','')),
        ('Phone', data.get('sender_phone','')),
    ])
    cli_t  = col_table('Client Information', [
        ('Name', data.get('client_name','')),
        ('Email', data.get('client_email','')),
        ('Phone', data.get('client_phone','')),
    ])

    # Lay all three side by side in a wrapper table
    gap = 4
    wrapper = Table([[proj_t, send_t, cli_t]],
                    colWidths=[cw, cw, cw],
                    hAlign='LEFT')
    wrapper.setStyle(TableStyle([
        ('LEFTPADDING',  (0,0),(-1,-1), 2),
        ('RIGHTPADDING', (0,0),(-1,-1), 2),
        ('TOPPADDING',   (0,0),(-1,-1), 0),
        ('BOTTOMPADDING',(0,0),(-1,-1), 0),
        ('VALIGN',       (0,0),(-1,-1), 'TOP'),
    ]))
    return wrapper

def notes_block(text, st):
    body_text = (text or '').strip()
    if not body_text:
        return []
    hdr = Table([[Paragraph('Project Notes', st['notes_hdr'])]], colWidths=[W-inch])
    hdr.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),BLACK),
        ('TOPPADDING',(0,0),(-1,-1),6), ('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),8),
    ]))
    body = Table([[Paragraph(body_text, st['notes_body'])]], colWidths=[W-inch])
    body.setStyle(TableStyle([
        ('BOX',(0,0),(-1,-1),0.5,TBLBORD),
        ('TOPPADDING',(0,0),(-1,-1),6), ('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),8), ('RIGHTPADDING',(0,0),(-1,-1),8),
    ]))
    return [hdr, body]

def bid_table(items, st):
    cw = W - inch
    ch_l = ParagraphStyle('chl', fontName='Helvetica-Bold', fontSize=8, textColor=WHITE)
    ch_r = ParagraphStyle('chr', fontName='Helvetica-Bold', fontSize=8, textColor=WHITE, alignment=TA_RIGHT)

    rows = [
        [Paragraph('Bid Items', st['bid_title']), '', '', '', ''],
        [Paragraph('Item &amp; Design', ch_l), Paragraph('Qty',ch_r),
         Paragraph('Unit',ch_r), Paragraph('Price',ch_r), Paragraph('Subtotal',ch_r)],
    ]
    for item in items:
        name  = item.get('name','')
        desc  = item.get('description','')
        qty   = item.get('qty','')
        unit  = item.get('unit','SY')
        price = item.get('price',0)
        sub   = item.get('subtotal',0)
        qty_s = f'{int(qty):,}' if isinstance(qty,(int,float)) and qty==int(qty) else str(qty)
        rows.append([
            Paragraph(f'<b>{name}</b><br/><font size="8" color="#777777">{desc}</font>', st['item_name']),
            Paragraph(qty_s, st['cell']),
            Paragraph(unit,  st['cell']),
            Paragraph(f'${price:,.2f}', st['cell']),
            Paragraph(f'${sub:,.2f}',   st['cell_b']),
        ])

    # Build explicit row heights: both header rows forced short
    banner_h  = 0.26 * inch   # red Bid Items banner
    col_hdr_h = 0.20 * inch   # col-label row
    row_heights = [banner_h, col_hdr_h] + [None] * (len(rows) - 2)
    t = Table(rows, colWidths=[cw*0.50, cw*0.10, cw*0.10, cw*0.15, cw*0.15],
              rowHeights=row_heights)
    ts = [
        ('SPAN',(0,0),(-1,0)), ('BACKGROUND',(0,0),(-1,0),RED), ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('TOPPADDING',(0,0),(-1,0),3), ('BOTTOMPADDING',(0,0),(-1,0),3),
        ('BACKGROUND',(0,1),(-1,1),COLHDR),
        ('TOPPADDING',(0,1),(-1,1),2), ('BOTTOMPADDING',(0,1),(-1,1),2),
        ('LEFTPADDING',(0,1),(0,1),8), ('RIGHTPADDING',(-1,1),(-1,1),8),
        ('TOPPADDING',(0,2),(-1,-1),4), ('BOTTOMPADDING',(0,2),(-1,-1),4),
        ('LEFTPADDING',(0,2),(0,-1),8), ('RIGHTPADDING',(-1,2),(-1,-1),8),
        ('LINEBELOW',(0,2),(-1,-1),0.3,TBLBORD),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('ALIGN',(1,0),(-1,-1),'RIGHT'),
        ('BOX',(0,0),(-1,-1),0.5,TBLBORD),
    ]
    for i in range(2, len(rows)):
        if i % 2 == 0:
            ts.append(('BACKGROUND',(0,i),(-1,i),ROWALT))
    t.setStyle(TableStyle(ts))
    return t

def total_line(total):
    """Clean right-aligned total ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ¢ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂ label in regular weight, amount in bold black.
    No box, no background. Just a subtle top rule and generous spacing so it
    reads as a natural footer to the table above it."""
    cw  = W - inch
    lbl = ParagraphStyle('tl', fontName='Helvetica',      fontSize=10,
                          textColor=DGRAY, alignment=TA_RIGHT)
    val = ParagraphStyle('tv', fontName='Helvetica-Bold', fontSize=13,
                          textColor=BLACK, alignment=TA_RIGHT)
    t = Table([[Paragraph('TOTAL BID PRICE:', lbl),
                Paragraph(f'${total:,.2f}', val)]],
              colWidths=[cw * 0.68, cw * 0.32])
    t.setStyle(TableStyle([
        ('LINEABOVE',     (0,0),(-1,0),  0.5, TBLBORD),
        ('TOPPADDING',    (0,0),(-1,-1), 10),
        ('BOTTOMPADDING', (0,0),(-1,-1), 6),
        ('LEFTPADDING',   (0,0),(-1,-1), 0),
        ('RIGHTPADDING',  (-1,0),(-1,-1),0),
        ('VALIGN',        (0,0),(-1,-1), 'MIDDLE'),
    ]))
    return t

class SitePlanPage(Flowable):
    def wrap(self, aw, ah):
        self._aw, self._ah = aw, ah
        return aw, ah
    def draw(self):
        c = self.canv
        c.setStrokeColor(MGRAY)
        c.setLineWidth(1)
        c.setDash(6,4)
        c.rect(0, 0, self._aw, self._ah, stroke=1, fill=0)
        c.setDash()
        cx, cy = self._aw/2, self._ah/2
        c.setFont('Helvetica-Bold', 14)
        c.setFillColor(MGRAY)
        c.drawCentredString(cx, cy + 0.2*inch, 'Site Plan / Drawing')
        c.setFont('Helvetica', 10)
        c.drawCentredString(cx, cy - 0.1*inch, 'Replace this page with site plan image')
        c.drawCentredString(cx, cy - 0.32*inch, 'or attach separately before sending to client')

def red_hdr(text, st, cw):
    t = Table([[Paragraph(text, st['appr_hdr'])]], colWidths=[cw])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),RED),
        ('TOPPADDING',(0,0),(-1,-1),7), ('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LEFTPADDING',(0,0),(-1,-1),8),
    ]))
    return t

def approval_page(data, st):
    elems = []
    cw = W - inch
    elems.append(red_hdr('Client Approval', st, cw))
    total = data.get('total',0)
    val_lbl = ParagraphStyle('vl', fontName='Helvetica-Bold', fontSize=9, textColor=DGRAY)
    val_amt = ParagraphStyle('va', fontName='Helvetica-Bold', fontSize=11, textColor=BLACK, alignment=TA_RIGHT)
    sig_rows = [
        # Approved value: label left, amount right, same row
        [Paragraph('<b>Approved Value:</b>', st['appr_lbl']),
         Paragraph(f'${total:,.2f}', val_amt)],
        [Paragraph('<b>Full Name:</b>',   st['appr_lbl']), ''],
        [Paragraph('<b>Date Signed:</b>', st['appr_lbl']), ''],
        [Paragraph('<b>Signature:</b>',   st['appr_lbl']), ''],
    ]
    sig_t = Table(sig_rows, colWidths=[cw*0.40, cw*0.60])
    sig_t.setStyle(TableStyle([
        ('BOX',           (0,0),(-1,-1), 0.5, TBLBORD),
        ('LINEBELOW',     (0,0),(-1,-2), 0.3, TBLBORD),
        ('TOPPADDING',    (0,0),(-1,-1), 8),
        ('BOTTOMPADDING', (0,0),(-1,-2), 8),
        ('BOTTOMPADDING', (0,-1),(-1,-1), 36),
        ('LEFTPADDING',   (0,0),(-1,-1), 8),
        ('RIGHTPADDING',  (-1,0),(-1,-1), 8),
        ('ALIGN',         (1,0),(1,0),   'RIGHT'),
        ('VALIGN',        (0,0),(-1,-1), 'MIDDLE'),
        ('SPAN',          (0,-1),(-1,-1)),
        ('BACKGROUND',    (0,0),(-1,0),  colors.HexColor('#FAFAFA')),
    ]))
    elems.append(sig_t)
    elems.append(Spacer(1, 0.18*inch))

    unit_items = data.get('unit_prices',[])
    if unit_items:
        elems.append(red_hdr('Paving Overage Unit Prices', st, cw))
        up_rows = []
        for item in unit_items:
            up_rows.append([
                Paragraph(item['name'], st['appr_val']),
                Paragraph(f'${item["rate"]:,.2f}', st['cell']),
            ])
        up_t = Table(up_rows, colWidths=[cw*0.78, cw*0.22])
        up_ts = [
            ('BOX',(0,0),(-1,-1),0.5,TBLBORD),
            ('LINEBELOW',(0,0),(-1,-2),0.3,TBLBORD),
            ('TOPPADDING',(0,0),(-1,-1),6), ('BOTTOMPADDING',(0,0),(-1,-1),6),
            ('LEFTPADDING',(0,0),(-1,-1),8), ('RIGHTPADDING',(-1,0),(-1,-1),8),
            ('ALIGN',(1,0),(1,-1),'RIGHT'), ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ]
        for i in range(len(up_rows)):
            if i % 2 == 0:
                up_ts.append(('BACKGROUND',(0,i),(-1,i),LGRAY))
        up_t.setStyle(TableStyle(up_ts))
        elems.append(up_t)
    return elems

def tc_block(title, body_items, st, cw):
    """Returns a KeepTogether block for one T&C section."""
    hdr = Table([[Paragraph(title, st['tc_section'])]], colWidths=[cw])
    hdr.setStyle(TableStyle([
        ('BACKGROUND',   (0,0),(-1,-1), colors.HexColor('#F6F6F6')),
        ('LINEBEFORE',   (0,0),(0,-1),  4, RED),
        ('LINEBELOW',    (0,0),(-1,-1), 0.5, TBLBORD),
        ('TOPPADDING',   (0,0),(-1,-1), 6),
        ('BOTTOMPADDING',(0,0),(-1,-1), 6),
        ('LEFTPADDING',  (0,0),(-1,-1), 10),
    ]))
    items = [hdr, Spacer(1, 0.04*inch)]
    for item in body_items:
        items.append(Paragraph(item, st['tc_body']))
    items.append(Spacer(1, 0.06*inch))
    return KeepTogether(items)


def tc_pages(st):
    cw = W - inch
    elems = []
    elems.append(Paragraph('Terms &amp; Conditions',
        ParagraphStyle('tch', fontName='Helvetica-Bold', fontSize=14,
                       alignment=TA_CENTER, spaceAfter=6)))
    elems.append(HRFlowable(width='100%', thickness=1, color=BLACK, spaceAfter=10))
    sections = [["1. CONTRACT FORMATION AND BINDING AGREEMENT",["This Proposal and Contract (\"Agreement\") is legally binding upon execution by both the Customer/Purchaser (\"Customer\") and HD Hauling & Grading (\"Contractor\"). No representation, warranty, or understanding not expressly set forth herein shall be enforceable against Contractor. No verbal agreement, course of dealing, or prior understanding shall modify or supersede this Agreement unless reduced to writing and executed by authorized representatives of both parties."]],["2. PROPOSAL VALIDITY",["Pricing set forth herein is valid for thirty (30) calendar days from the date of issuance. Contractor reserves the right to withdraw or reprice this Proposal prior to execution if Customer fails to execute within said period, including adjustments for material cost changes, fuel surcharges, or labor rate fluctuations. If work has not commenced within sixty (60) calendar days of execution, Contractor reserves the right to reprice the Agreement to reflect prevailing costs at the time of mobilization, with advance written notice to Customer."]],["3. SCOPE OF WORK",["Contractor's obligations are strictly limited to the work explicitly described in the Bid Items section of this Agreement. No work, materials, labor, or services beyond those expressly enumerated shall be construed as included within Contractor's scope. All additional, modified, or substituted work shall be performed solely pursuant to a written Change Order executed by both parties prior to commencement, as set forth in Section 5 herein."]],["4. CHANGED CONDITIONS",["Should Contractor encounter subsurface, concealed, or latent conditions at the project site that differ materially from those indicated in the Agreement -- or that could not reasonably have been anticipated through a standard pre-bid site walkthrough -- including but not limited to rock, unsuitable or unstable soils, organic material, underground obstructions, undisclosed utilities, excessive groundwater, or contaminated material, Contractor shall provide prompt written notice to Customer prior to disturbing the affected area.","(a) All work arising from or related to such changed conditions shall be governed by a written Change Order executed by both parties prior to the performance of any additional work. Customer shall not direct Contractor to proceed in any area of changed conditions without a fully executed Change Order.","(b) Upon receipt of written notice of changed conditions, Customer shall respond in writing within forty-eight (48) hours authorizing a Change Order, directing Contractor to stop work in the affected area, or providing alternative written direction. Failure to respond within forty-eight (48) hours shall entitle Contractor to suspend work in the affected area and to bill standby time and re-mobilization costs at applicable unit rates, without liability to Customer.","(c) Contractor shall bear no liability for schedule delays, cost overruns, property damage, or consequential losses attributable to changed conditions that were not disclosed by Customer, were not reasonably ascertainable during a standard pre-bid walkthrough, or were caused by third parties.","(d) Customer bears sole responsibility for ensuring all underground utilities within and adjacent to the project site are identified, located, and marked pursuant to the requirements of the North Carolina One-Call Center (NC 811) prior to commencement of any excavation or grading work. Contractor shall bear no liability for damage to any utility infrastructure not properly located and marked prior to the start of work."]],["5. CHANGE ORDERS",["Any addition, deletion, substitution, or modification of the scope of work set forth in this Agreement shall require a written Change Order fully executed by authorized representatives of both parties prior to commencement of such work. Contractor shall have no obligation to perform out-of-scope work absent an executed Change Order, and shall bear no liability for any delay, damage, or cost arising from changes not memorialized in a fully executed Change Order. Unit prices for Change Order work of similar type and scope shall be those set forth in the Paving Overage Unit Prices section of this Agreement."]],["6. SITE ACCESS AND STAGING",["Customer shall provide Contractor with continuous, unobstructed vehicular and equipment access to all areas of the project site necessary for the performance of the work, an adequate staging area for equipment, materials, and supplies, and a safe haul route capable of accommodating fully loaded delivery vehicles throughout the duration of the project.","(a) Delays, standby time, or re-mobilization costs incurred by Contractor due to restricted or denied site access, interference by other trades, or unavailability of the designated work area shall be billed at applicable unit rates set forth in the Paving Overage Unit Prices section.","(b) Customer bears sole responsibility for ensuring all underground utilities within and adjacent to the project site are identified and marked by NC 811 or a licensed private utility locating service prior to the commencement of any subsurface work. Contractor shall bear no liability for damage to any utility, conduit, or infrastructure not properly marked prior to the start of work."]],["7. SUBGRADE ACCEPTANCE AND PAVEMENT PERFORMANCE",["Contractor shall bear no responsibility for pavement failure, cracking, rutting, settlement, or premature deterioration attributable to inadequate subgrade preparation, insufficient base course compaction, inadequate drainage, or unsuitable sub-base materials outside the scope of work expressly undertaken by Contractor under this Agreement.","(a) Commencement of paving operations by Contractor shall constitute Customer's express acceptance of the existing subgrade and base course conditions. Prior to paving, Customer bears sole responsibility for ensuring the subgrade has been properly graded, compacted in accordance with applicable NCDOT specifications, proof-rolled where required, and inspected by a qualified party.","(b) In the event Contractor identifies conditions that may adversely affect pavement performance, Contractor shall provide written notice to Customer prior to proceeding. Customer's direction to proceed, whether written or verbal, shall constitute a full and complete release of Contractor from all performance liability attributable to those identified conditions.","(c) Proof rolling, compaction testing, moisture content testing, and geotechnical evaluation shall be Customer's sole responsibility unless expressly included within Contractor's scope in the Bid Items section."]],["8. MATERIALS AND NCDOT SPECIFICATIONS",["All asphalt materials furnished by Contractor shall conform to the applicable requirements of the current edition of the North Carolina Department of Transportation Standard Specifications for Roads and Structures (NCDOT Specifications), unless alternative specifications are expressly identified in the Bid Items. In the event a specified material or mix type becomes unavailable due to plant operations, material shortages, or supply chain disruptions, Contractor shall promptly notify Customer and may substitute a functionally equivalent material meeting applicable NCDOT Specifications at no additional cost to Customer."]],["9. WEATHER AND TEMPERATURE CONDITIONS",["Paving operations shall be performed in strict accordance with the ambient temperature, surface temperature, and weather placement requirements established by the NCDOT Specifications for the designated mix type. Contractor shall not be obligated to perform paving operations during precipitation of any kind, when standing water or frost is present on the base course, when temperatures fail to satisfy NCDOT minimums, or when forecast conditions within four (4) hours are reasonably anticipated to compromise compaction, bonding, or curing of the pavement.","(a) Schedule adjustments or delays arising from weather conditions shall not constitute grounds for price renegotiation, assessment of liquidated damages, or any other claim against Contractor.","(b) Concrete placement shall be performed in compliance with ACI 305R (Hot Weather Concreting) and ACI 306R (Cold Weather Concreting), as applicable to prevailing field conditions."]],["10. COMPACTION AND QUALITY",["Compaction shall be performed to achieve density requirements in accordance with applicable NCDOT Specifications for the designated mix type. Where the Owner or Engineer of Record requires independent compaction or quality assurance testing, Customer shall engage and compensate a qualified independent testing agency at Customer's sole expense. Contractor shall bear no liability for compaction deficiencies attributable to: (i) mix temperature loss during transport resulting from causes beyond Contractor's reasonable control; (ii) laydown delays caused by Customer, other contractors, or third parties; or (iii) subgrade instability or inadequate base course support."]],["11. WARRANTY",["Contractor warrants all materials and workmanship performed under this Agreement against defects for a period of one (1) year from the date of substantial completion (Warranty Period), limited to defects directly and solely attributable to Contractor's performance hereunder. For purposes of this Agreement, substantial completion shall be defined as the date on which paving operations are complete and the improved surface is open to vehicular or pedestrian traffic, as applicable.","This warranty expressly excludes:","(a) Damage or deterioration resulting from the application of petroleum products, chemical spills, solvents, or de-icing agents, including without limitation sodium chloride, calcium chloride, or magnesium chloride;","(b) Pavement failure, rutting, cracking, or settlement attributable to subgrade, sub-base, or base course conditions not prepared by Contractor under this Agreement;","(c) Damage caused by vehicular or axle loads exceeding the design capacity of the pavement section specified in the Bid Items;","(d) Reflective cracking, delamination, or surface distress resulting from conditions in the underlying existing pavement on mill-and-pave, overlay, or patching projects;","(e) Normal surface oxidation, weathering, aggregate polishing, raveling, or other age-related pavement distress consistent with expected material performance over time;","(f) Damage or deterioration caused by third parties, acts of God, flooding, subsidence, tree root intrusion, freeze-thaw cycling, or events beyond Contractor's reasonable control;","(g) Pavement markings, thermoplastic striping, signage, or appurtenances not installed by Contractor under this Agreement.","All warranty claims must be submitted to Contractor in writing prior to expiration of the Warranty Period. Contractor's sole and exclusive obligation under this warranty shall be, at Contractor's election, repair or replacement of the defective work. This warranty is expressly in lieu of all other warranties, express or implied, including without limitation any implied warranty of merchantability or fitness for a particular purpose."]],["12. TRAFFIC CONTROL AND PERMITS",["To the extent traffic control is expressly included within Contractor's scope in the Bid Items, Contractor shall provide traffic control devices in general conformance with the Manual on Uniform Traffic Control Devices (MUTCD) during periods of active paving operations only. Traffic control shall not extend beyond active operations or between work shifts.","(a) Customer bears sole responsibility for obtaining and maintaining, at Customer's expense, all permits, licenses, right-of-way authorizations, NCDOT encroachment agreements, and governmental approvals required for the performance of the work prior to the scheduled commencement date. Permit-related delays shall not constitute grounds for price renegotiation or claims against Contractor.","(b) All determinations regarding ADA compliance for pavement markings, curb ramps, detectable warning surfaces, and accessible routes are the sole responsibility of the Owner and Engineer of Record. Contractor assumes no ADA compliance design or certification responsibility."]],["13. LIMITATION OF LIABILITY",["Contractor's aggregate liability for any and all claims arising out of or related to this Agreement, whether in contract, tort, or otherwise, shall not exceed the total contract price paid by Customer to Contractor hereunder. Under no circumstances shall Contractor be liable for consequential, incidental, indirect, special, exemplary, or punitive damages of any nature, including without limitation loss of use, loss of revenue, lost profits, loss of business opportunity, business interruption, or third-party claims, regardless of the theory of liability asserted."]],["14. PAYMENT TERMS",["All invoices are due and payable in full within thirty (30) calendar days of the invoice date. Invoices shall be submitted upon substantial completion of the work or upon completion of each defined phase, whichever occurs first.","(a) Any unpaid balance remaining after the due date shall accrue interest at the rate of one and one-half percent (1.5%) per month -- eighteen percent (18%) per annum -- calculated on the outstanding principal balance from the invoice date until paid in full.","(b) Should any invoice remain unpaid beyond thirty (30) days, Contractor may, upon written notice to Customer, suspend all work under this Agreement until the full outstanding balance, together with all accrued interest, has been satisfied. All schedule delays, re-mobilization costs, and project cost increases resulting from a payment-related suspension shall be the sole responsibility of Customer.","(c) The individual executing this Agreement, whether in their individual capacity or as an authorized representative of a business entity, hereby unconditionally and personally guarantees full and prompt payment of all amounts due hereunder, including principal, accrued interest, attorneys' fees, and collection costs. By signing in the designated Personal Guarantee field, the signatory acknowledges this guarantee is made in their individual capacity and is enforceable independently of any corporate or entity signature on this Agreement.","(d) Any good-faith dispute regarding a specific invoice amount must be submitted to Contractor in writing within ten (10) calendar days of the invoice date, stating with specificity the basis for the dispute. All undisputed invoice amounts shall remain due and payable per the terms hereof, notwithstanding any pending dispute."]],["15. LIEN RIGHTS AND COLLECTIONS",["NOTICE TO OWNER: HD Hauling & Grading is a licensed contractor in the State of North Carolina. Contractor expressly reserves, and does not waive, its right to file and enforce a Claim of Lien upon the real property on which the work is performed and a Bond Claim against any applicable payment bond, pursuant to N.C.G.S. Chapter 44A, in the event of non-payment of any amounts due under this Agreement.","Nothing contained in this Agreement, in any purchase order, in any joint check agreement, or in any payment direction letter shall be construed as a waiver of Contractor's lien or bond rights under N.C.G.S. Chapter 44A, absent a separate written waiver executed by an authorized representative of Contractor.","Should Contractor be required to institute legal or collection proceedings to recover amounts due hereunder, Customer shall be liable for and shall pay all reasonable attorneys' fees, court costs, and collection expenses incurred by Contractor, as authorized by N.C.G.S. § 44A-35."]],["16. RETAINAGE",["Where this Agreement is performed as a subcontract and retainage is withheld by the prime contractor or Owner, Contractor's retainage shall be released no later than thirty (30) calendar days following final completion and acceptance of Contractor's scope of work, regardless of the status of any other work on the project. Pursuant to N.C.G.S. § 22C-2, any retainage not released within said thirty (30) day period shall accrue interest at the legal rate from the date on which it was due until the date of full payment. Contractor expressly does not waive its right to interest on any retainage held beyond the statutory release date."]],["17. MATERIAL PRICING AND MARKET ADJUSTMENTS",["Customer acknowledges that asphalt material costs are subject to market volatility arising from fluctuations in the Liquid Asphalt Index (LAI), crude oil pricing, aggregate costs, and transportation and fuel surcharges. Should Contractor's actual material costs at the time of purchase exceed those assumed in this Proposal by more than ten percent (10%), Contractor reserves the right to adjust the contract price accordingly, with advance written notice to Customer prior to any such adjustment. Contractor shall bear no liability for project delays arising from plant closures, material shortages, or supply chain disruptions beyond Contractor's control."]],["18. FORCE MAJEURE",["Contractor shall not be liable for any delay in, or failure of, performance under this Agreement caused by circumstances beyond Contractor's reasonable control, including without limitation acts of God, severe weather events, flooding, fire, public health emergencies, labor disputes or strikes, governmental actions or restrictions, fuel shortages, or supply chain disruptions. In the event of a qualifying force majeure condition, the project schedule shall be extended for a period equal to the duration of the delay, and the contract price shall be subject to good-faith renegotiation in the event market conditions change materially during the period of force majeure."]],["19. GOVERNING LAW AND DISPUTE RESOLUTION",["This Agreement shall be governed by and construed in accordance with the laws of the State of North Carolina, without regard to its conflict of laws principles. In the event of any dispute arising out of or relating to this Agreement, the parties shall first attempt resolution through good-faith negotiation prior to initiating formal legal proceedings. If negotiation fails to resolve the matter, venue and exclusive jurisdiction for any legal action shall lie in the Superior Court of the county in which the project is located, or in the appropriate federal district court where federal jurisdiction exists."]],["20. ENTIRE AGREEMENT AND INTEGRATION",["This Agreement, together with the Bid Items, Paving Overage Unit Prices, and any fully executed Change Orders, constitutes the entire agreement between the parties with respect to the subject matter hereof and supersedes all prior and contemporaneous proposals, negotiations, representations, and understandings, whether written or oral. No terms or conditions contained in any Customer purchase order or other document shall be incorporated into or deemed part of this Agreement unless expressly identified in a written amendment executed by authorized representatives of both parties. No amendment, modification, or waiver of any provision hereof shall be valid or binding unless made in writing and executed by authorized representatives of both parties."]]]
    for title, body in sections:
        elems.append(tc_block(title, body, st, cw))
    elems.append(Spacer(1, 0.25*inch))
    sig_data = [
        [Paragraph('<b>HD Hauling &amp; Grading</b>', st['tc_body']),
         Paragraph('<b>Customer / Purchaser</b>', st['tc_body'])],
        [Paragraph('Authorized Signature: ___________________________', st['tc_body']),
         Paragraph('Authorized Signature: ___________________________', st['tc_body'])],
        [Paragraph('Printed Name: _________________________________', st['tc_body']),
         Paragraph('Printed Name: _________________________________', st['tc_body'])],
        [Paragraph('Title: _________________________________________', st['tc_body']),
         Paragraph('Title: _________________________________________', st['tc_body'])],
        [Paragraph('Date: __________________________________________', st['tc_body']),
         Paragraph('Date: __________________________________________', st['tc_body'])],
    ]
    sig_tbl = Table(sig_data, colWidths=[(W-inch)/2, (W-inch)/2])
    sig_tbl.setStyle(TableStyle([
        ('VALIGN',        (0,0),(-1,-1), 'TOP'),
        ('TOPPADDING',    (0,0),(-1,-1), 6),
        ('BOTTOMPADDING',(0,0),(-1,-1), 6),
        ('LINEABOVE',     (0,0),(-1,0),  1, TBLBORD),
        ('LINEBELOW',     (0,-1),(-1,-1),1, TBLBORD),
    ]))
    pg_data = [
        [Paragraph('<b>PERSONAL GUARANTEE -- See Section 14(c)</b>', st['tc_section']),
         Paragraph('', st['tc_body'])],
        [Paragraph('Personal Guarantee Signature: __________________', st['tc_body']),
         Paragraph('Printed Name &amp; Title: ________________________', st['tc_body'])],
        [Paragraph('Date: __________________________________________', st['tc_body']),
         Paragraph('', st['tc_body'])],
    ]
    pg_tbl = Table(pg_data, colWidths=[(W-inch)/2, (W-inch)/2])
    pg_tbl.setStyle(TableStyle([
        ('VALIGN',        (0,0),(-1,-1), 'TOP'),
        ('TOPPADDING',    (0,0),(-1,-1), 6),
        ('BOTTOMPADDING',(0,0),(-1,-1), 6),
        ('LINEABOVE',     (0,0),(-1,0),  2, RED),
        ('LINEBELOW',     (0,-1),(-1,-1),1, TBLBORD),
        ('BACKGROUND',    (0,0),(-1,-1), colors.HexColor('#FFF5F5')),
    ]))
    elems.append(KeepTogether([
        Paragraph('CONTRACT EXECUTION',
            ParagraphStyle('cex', fontName='Helvetica-Bold', fontSize=10,
                alignment=TA_CENTER, spaceBefore=10, spaceAfter=8)),
        sig_tbl,
        Spacer(1, 0.18*inch),
        pg_tbl,
    ]))
    return elems


def build(data, out_path):
    st = S()
    doc = SimpleDocTemplate(out_path, pagesize=letter,
                             title=data.get('project_name','Proposal'),
                             author='HD Hauling & Grading',
                             creator='HD Hauling & Grading',
                             subject=data.get('project_name','Proposal'),
                             leftMargin=LM, rightMargin=RM,
                             topMargin=TM, bottomMargin=BM)
    story = []
    story.append(CoverPage(data))
    story.append(PageBreak())
    story.append(info_block(data, st))
    story.append(Spacer(1, 0.12*inch))
    story += notes_block(data.get('notes',''), st)
    story.append(Spacer(1, 0.12*inch))
    story.append(bid_table(data.get('line_items',[]), st))
    story.append(Spacer(1, 0.1*inch))
    story.append(total_line(data.get('total',0)))
    story.append(PageBreak())
    story.append(SitePlanPage())
    story.append(PageBreak())
    story += approval_page(data, st)
    story.append(PageBreak())
    story += tc_pages(st)
    doc.build(story, canvasmaker=canvas_maker(data.get('date','')))


if __name__ == '__main__':
    import json, sys
    data = json.loads(sys.argv[1])
    out  = sys.argv[2] if len(sys.argv) > 2 else '/tmp/proposal.pdf'
    build(data, out)
    print('OK:', out)
