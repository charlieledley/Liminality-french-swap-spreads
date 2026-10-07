# -*- coding: utf-8 -*-
"""Design system for the Liminality decks: palette, type scale, and slide primitives.

Palette is Midnight Executive -- navy dominant, ice-blue support, gold accent, with a
green/red pair reserved strictly for gains and losses so colour never carries two meanings.
Fonts are Cambria (headers) / Calibri (body): both ship with Office AND render true-to-width
in LibreOffice, so the visual QA pass can be trusted on text fit.
"""
import os

from PIL import ImageFont
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

NAVY = RGBColor.from_string("011C40")      # Jeff's band and text navy (template of 2026-10-07); was 1E2761
INK = RGBColor.from_string("11142E")
ICE = RGBColor.from_string("CADCFC")
ICE_BG = RGBColor.from_string("EEF4FD")
GOLD = RGBColor.from_string("C9922E")
WHITE = RGBColor.from_string("FFFFFF")
GREY = RGBColor.from_string("5A6172")
LGREY = RGBColor.from_string("9AA1B2")
RULE = RGBColor.from_string("DCE3EF")
POS = RGBColor.from_string("2C7A5A")
NEG = RGBColor.from_string("B3332E")

HFONT, BFONT = "Garamond", "Garamond"     # Jeff's serif throughout (Charlie, 2026-10-07); was Cambria / Calibri
W, H = 13.333, 7.5
M = 0.62
CW = W - 2 * M
TITLE_Y = 0.42
# Jeff's master: an empty copy of his file scaled to 13.33 x 7.5in through PowerPoint. Each body page is his "Title and
# Content" layout: the navy band (0 to BAND_H) with the title placeholder, his logo bottom left. Content drawn by the
# primitives below is shifted down by SHIFT so the pages written for the old title zone clear the band.
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template-liminality-2026-10-07.pptx")
BAND_H = 1.68
SHIFT = 0.40
DARK_GREY = RGBColor.from_string("262626")


def Y(y):
    """Physical y for a content coordinate: the old pages' y plus the band shift."""
    return Inches(y + SHIFT)


_FONTS = {("Calibri", 0, 0): "calibri.ttf", ("Calibri", 1, 0): "calibrib.ttf",
          ("Calibri", 0, 1): "calibrii.ttf", ("Calibri", 1, 1): "calibriz.ttf",
          ("Cambria", 0, 0): "cambria.ttc", ("Cambria", 1, 0): "cambriab.ttf",
          ("Cambria", 0, 1): "cambriai.ttf", ("Cambria", 1, 1): "cambriaz.ttf",
          ("Garamond", 0, 0): "GARA.TTF", ("Garamond", 1, 0): "GARABD.TTF",
          ("Garamond", 0, 1): "GARAIT.TTF", ("Garamond", 1, 1): "GARABD.TTF"}
_FDIR = r"C:\Windows\Fonts"
_fc = {}
LINE_BOX = 1.22          # PowerPoint line box as a multiple of the point size, these faces
WIDTH_SAFETY = 0.965     # PowerPoint sets Garamond a little wider than the TrueType metrics predict; wrap a touch early


def _font(name, bold, italic, pt):
    k = (name, int(bool(bold)), int(bool(italic)), round(pt, 1))
    if k not in _fc:
        fn = _FONTS.get(k[:3], "calibri.ttf")
        path = os.path.join(_FDIR, fn)
        if not os.path.exists(path):
            path = os.path.join(_FDIR, "calibri.ttf")
        _fc[k] = ImageFont.truetype(path, max(1, int(round(pt * 96.0 / 72.0))))
    return _fc[k]


def nlines(text, w_in, pt, name=None, bold=False, italic=False):
    """Lines this string wraps to in a box w_in wide -- measured with the real glyphs."""
    f = _font(name or BFONT, bold, italic, pt)
    wpx = w_in * 96.0 * WIDTH_SAFETY
    n = 0
    for para in str(text).split("\n"):
        cur, k = "", 1
        for word in para.split(" "):
            cand = (cur + " " + word).strip()
            if f.getlength(cand) <= wpx or not cur:
                cur = cand
            else:
                k += 1
                cur = word
        n += k
    return n


def theight(text, w_in, pt, name=None, bold=False, italic=False, line=0.95, space_after=0):
    """Height in inches that `text` needs at this width. The inverse of nlines."""
    return (nlines(text, w_in, pt, name, bold, italic) * pt * LINE_BOX * line
            + space_after) / 72.0


def blank(prs, keep_title=True):
    """A page on Jeff's "Title and Content" layout. python-pptx clones the title and body placeholders; the body one is
    removed (it would show "Click to add text"), the title one kept for title() unless keep_title is False."""
    lay = prs.slide_layouts.get_by_name("Title and Content") or prs.slide_layouts[0]
    sl = prs.slides.add_slide(lay)
    for ph in list(sl.placeholders):
        if ph.placeholder_format.idx != 0 or not keep_title:
            ph._element.getparent().remove(ph._element)
    return sl


def bg(slide, colour):
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(W), Inches(H))
    r.fill.solid()
    r.fill.fore_color.rgb = colour
    r.line.fill.background()
    r.shadow.inherit = False
    slide.shapes._spTree.remove(r._element)
    slide.shapes._spTree.insert(2, r._element)
    return r


def tbox(slide, x, y, w, h, text, size=14, bold=False, colour=NAVY, font=None,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, space_after=6, line=0.95,
         italic=False, raw=False, underline=False):
    """A text box. `text` is a string, or a list of (string, {overrides}) tuples. raw=True places it at y exactly
    (title zone, footnotes, page number); otherwise y is a content coordinate and is shifted below the band."""
    items0 = text if isinstance(text, list) else [(text, {})]
    need = 0.0
    for it in items0:
        s0, o0 = it if isinstance(it, tuple) else (it, {})
        need += theight(s0, w, o0.get("size", size), o0.get("font", font or BFONT),
                        o0.get("bold", bold), o0.get("italic", italic),
                        o0.get("line", line), o0.get("space_after", space_after))
    tb = slide.shapes.add_textbox(Inches(x), Inches(y) if raw else Y(y), Inches(w), Inches(max(h, need)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    items = text if isinstance(text, list) else [(text, {})]
    for i, it in enumerate(items):
        s, o = it if isinstance(it, tuple) else (it, {})
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = o.get("align", align)
        p.space_after = Pt(o.get("space_after", space_after))
        p.line_spacing = o.get("line", line)
        r = p.add_run()
        r.text = s
        f = r.font
        f.name = o.get("font", font or BFONT)
        f.size = Pt(o.get("size", size))
        f.bold = o.get("bold", bold)
        f.italic = o.get("italic", italic)
        f.underline = o.get("underline", underline)
        f.color.rgb = o.get("colour", colour)
    return tb


def title(slide, text, sub=None, dark=False):
    """Title in the band's placeholder (white Garamond, as Jeff's), the subtitle beneath it inside the band."""
    ph = slide.shapes.title
    if ph is None:
        tbox(slide, M, 0.34, CW, 0.70, text, size=28, colour=WHITE, font=HFONT, raw=True)
    else:
        ph.left, ph.top, ph.width, ph.height = Inches(M), Inches(0.30 if sub else 0.0), Inches(CW), Inches(0.78 if sub else BAND_H)
        tf = ph.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        para = tf.paragraphs[0]
        para.alignment = PP_ALIGN.LEFT
        r = para.add_run()
        r.text = text
        r.font.name, r.font.size, r.font.bold = HFONT, Pt(28), False
        r.font.color.rgb = WHITE
    if sub:
        tbox(slide, M, 1.10, CW, 0.50, sub, size=13.5, italic=True, colour=ICE, raw=True, line=1.0, space_after=0)


def card(slide, x, y, w, h, fill=ICE_BG, radius=0.04, line=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Y(y),
                                Inches(w), Inches(h))
    sh.adjustments[0] = radius
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(0.75)
    sh.shadow.inherit = False
    return sh


def stat(slide, x, y, w, value, label, vcolour=NAVY, h=1.16, fill=ICE_BG, vsize=31,
         lsize=10.5):
    """Big number over a caption, both measured and stacked so the card always contains them."""
    iw = w - 0.20
    vh = theight(value, iw, vsize, HFONT, True, False, 0.95)
    lh = theight(label, iw, lsize, BFONT, False, False, 0.95)
    h = max(h, vh + lh + 0.34)
    card(slide, x, y, w, h, fill)
    top = y + (h - vh - lh - 0.10) / 2.0
    tbox(slide, x + 0.10, top, iw, vh, value, size=vsize, bold=True, colour=vcolour,
         font=HFONT, align=PP_ALIGN.CENTER, space_after=0)
    tbox(slide, x + 0.10, top + vh + 0.10, iw, lh, label, size=lsize, colour=GREY,
         align=PP_ALIGN.CENTER, line=0.95, space_after=0)
    return h


def note(slide, x, y, w, lead, body, fill=ICE_BG, line_=None, size=12.2, pad=0.20,
         lead_colour=NAVY, body_colour=GREY, minh=0.0):
    """A tinted callout whose card is sized to its text. Returns the card's bottom y.

    Lead and body run as two paragraphs in one box, so the card can never be shorter than
    what it holds -- the failure this replaces was a hand-guessed card height.
    """
    iw = w - 2 * pad
    hh = (theight(lead, iw, size, BFONT, True, False, 1.14, 2)
          + theight(body, iw, size, BFONT, False, False, 1.14))
    ch = max(minh, hh + 2 * pad)
    card(slide, x, y, w, ch, fill=fill, line=line_)
    tbox(slide, x + pad, y + (ch - hh) / 2.0, iw, hh,
         [(lead, {"bold": True, "colour": lead_colour, "space_after": 2}),
          (body, {"colour": body_colour, "space_after": 0})],
         size=size, line=1.14)
    return y + ch


def bullets(slide, x, y, w, items, size=13.5, colour=NAVY, gap=10, dot=GOLD, line=1.03):
    """Bulleted list drawn with real dots so the spacing is ours, not the layout's.

    Each bullet advances by its MEASURED wrapped height, so the next one always clears it
    however the text wraps. Returns the y just below the last bullet.
    """
    cy = y
    for it in items:
        s, o = it if isinstance(it, tuple) else (it, {})
        sz, bd = o.get("size", size), o.get("bold", False)
        d = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Y(cy + 0.072),
                                   Inches(0.072), Inches(0.072))
        d.fill.solid()
        d.fill.fore_color.rgb = o.get("dot", dot)
        d.line.fill.background()
        d.shadow.inherit = False
        hgt = theight(s, w - 0.20, sz, BFONT, bd, False, line)
        tbox(slide, x + 0.20, cy, w - 0.20, hgt, s, size=sz, space_after=0, line=line,
             colour=o.get("colour", colour), bold=bd)
        cy += hgt + gap / 72.0
    return cy


FOOT_X = 2.72             # clears Jeff's logo, bottom left (0.36 to 2.42in on his layout)
FOOT_W = 8.55              # ends before the page number, bottom right


def footnote(slide, text, y=None, colour=LGREY, size=9, w=None):
    """Sits in the lane between the page number (bottom left) and the logo (bottom right)."""
    ww = w if w is not None else FOOT_W
    hgt = theight(text, ww, size, BFONT, False, False, 1.08)
    tbox(slide, FOOT_X, y if y is not None else H - 0.26 - hgt, ww, hgt, text, size=size,
         colour=colour, line=1.08, space_after=0, raw=True)


def table(slide, x, y, w, rows, colw=None, head=True, size=11.5, rowh=0.285, headh=0.34,
          zebra=True, aligns=None, headfill=NAVY, boldcol0=False, neutral=(), rowhs=None,
          anchor=MSO_ANCHOR.MIDDLE, colours=None):
    """Plain table; rows is a list of lists of strings. Returns the bottom y.

    rowhs: one height per body row, when the rows must land at given positions (the scenario
    table's rows sit level with the chart's lines). anchor TOP then keeps the text at the top
    of a tall row. colours: optional text colour per body row (index 0 = first body row).
    """
    n, m = len(rows), len(rows[0])
    colw = colw or [w / m] * m
    body_h = sum(rowhs) if rowhs else rowh * (n - 1)
    gf = slide.shapes.add_table(n, m, Inches(x), Y(y), Inches(w),
                                Inches((headh if head else 0) + body_h))
    t = gf.table
    t.first_row = head
    t.horz_banding = False
    for j, cwj in enumerate(colw):
        t.columns[j].width = Inches(cwj)
    for i, row in enumerate(rows):
        k = i - 1 if head else i
        t.rows[i].height = Inches(headh if (head and i == 0) else (rowhs[k] if rowhs else rowh))
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.margin_left = c.margin_right = Inches(0.07)
            c.margin_top = c.margin_bottom = Inches(0.01 if anchor == MSO_ANCHOR.MIDDLE else 0.035)
            c.vertical_anchor = anchor
            c.fill.solid()
            if head and i == 0:
                c.fill.fore_color.rgb = headfill
            elif zebra and i % 2 == 0:
                c.fill.fore_color.rgb = ICE_BG
            else:
                c.fill.fore_color.rgb = WHITE
            p = c.text_frame.paragraphs[0]
            p.alignment = (PP_ALIGN.LEFT if j == 0
                           else (aligns[j] if aligns else PP_ALIGN.RIGHT))
            s = str(val)
            # one minus glyph throughout: a mix of "-" and U+2212 in one table looks broken
            if s[:1] == "-":
                s = "−" + s[1:]
            r = p.add_run()
            r.text = s
            f = r.font
            f.name = BFONT
            f.size = Pt(size)
            f.bold = bool((head and i == 0) or (boldcol0 and j == 0))
            if head and i == 0:
                f.color.rgb = WHITE
            elif colours and colours[k] is not None:
                f.color.rgb = colours[k]
            elif i in neutral or j == 0:
                # a row whose sign is not a gain or a loss -- skew, kurtosis, a ratio
                f.color.rgb = NAVY
            elif s.startswith("−"):
                f.color.rgb = NEG
            elif s.startswith("+"):
                f.color.rgb = POS
            else:
                f.color.rgb = NAVY
    return y + headh + rowh * (n - 1)


LOGO_AR = 1976.0 / 560.0          # measured from the cropped asset


def logo(slide, x, y, w, dark_bg=False, _dir=None):
    """Place the Liminality Capital mark, lifted from the prior deck's layout art.

    Two variants exist: logo_dark.png (the original wordmark, for light slides) and
    logo_light.png (the same file with the near-black glyphs recoloured for dark slides,
    brand blues untouched). White pixels were made transparent in both, so the mark sits
    on any background without a white box behind it.
    """
    d = _dir or os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(d, "logo_light.png" if dark_bg else "logo_dark.png")
    if not os.path.exists(p):
        return None
    return slide.shapes.add_picture(p, Inches(x), Inches(y), Inches(w),
                                    Inches(w / LOGO_AR))


def pagenum(slide, n):
    """Bottom right, as on Jeff's layout (his slide-number placeholder is not cloned onto new slides)."""
    tbox(slide, W - M - 1.0, H - 0.48, 1.0, 0.26, str(n), size=10.5, colour=GREY, space_after=0, align=PP_ALIGN.RIGHT, raw=True)


def logscale(chart):
    """python-pptx exposes no log axis; write c:logBase into the value axis scaling."""
    from pptx.oxml.ns import qn
    sc = chart.value_axis._element.find(qn("c:scaling"))
    lb = sc.makeelement(qn("c:logBase"), {"val": "10"})
    sc.insert(0, lb)


def style_chart(chart, colours, legend=True, vfmt='0%', catsize=9, valsize=9,
                gridlines=True):
    from pptx.enum.chart import XL_LEGEND_POSITION
    from pptx.oxml.ns import qn
    chart.has_title = False
    chart.font.name = BFONT
    chart.font.size = Pt(catsize)
    chart.has_legend = legend
    if legend:
        chart.legend.position = XL_LEGEND_POSITION.TOP
        chart.legend.include_in_layout = False
        chart.legend.font.size = Pt(10.5)
        chart.legend.font.color.rgb = GREY
    for s, col in zip(chart.plots[0].series, colours):
        s.format.fill.solid()
        s.format.fill.fore_color.rgb = col
        s.format.line.fill.background()
    va, ca = chart.value_axis, chart.category_axis
    va.has_major_gridlines = gridlines
    if gridlines:
        gl = va.major_gridlines.format.line
        gl.color.rgb = RULE
        gl.width = Pt(0.6)
    ca.has_major_gridlines = False
    for ax, sz in ((va, valsize), (ca, catsize)):
        ax.tick_labels.font.size = Pt(sz)
        ax.tick_labels.font.color.rgb = GREY
        ax.tick_labels.font.name = BFONT
        ax.format.line.color.rgb = RULE
    va.tick_labels.number_format = vfmt
    va.tick_labels.number_format_is_linked = False
    return chart
