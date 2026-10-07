# -*- coding: utf-8 -*-
"""French swap spreads investor deck (first build 2026-10-05; round-1 edits held for rebuild).

Running order follows docs/deck-plan-2026-10-04.md. Every figure on a slide is read from
deck/data/*.json, written by analysis/spread_history.py and analysis/scenario_returns.py;
nothing numeric is typed here. Text that Charlie left in brackets in his draft of 2026-10-04 is
carried as he wrote it and flagged with an internal note.

Conventions on every slide that shows a spread: 1y and 5y France swap spreads versus the 6m
Euribor swap, swap minus bond, so a cheap OAT reads negative (decisions 0002, 0003); Bloomberg
generic benchmark yields throughout (0004, reversed 2026-10-05); percentiles since 2010-01-01 (0005). IRR and MOIC are Charlie's, gross of fees.

INTERNAL_NOTES = False strips every internal note for the external build.
Output: exports/Liminality_French_Swap_Spreads_<date>.pptx (gitignored; rebuild with this file).
"""
import datetime as dt
import json
import os
import sys

from pptx import Presentation
from pptx.chart.data import XyChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_TICK_LABEL_POSITION
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dsl import (NAVY, INK, ICE, ICE_BG, GOLD, WHITE, GREY, LGREY, RULE, POS, NEG,     # noqa: E402
                 HFONT, BFONT, W, H, M, CW, blank, bg, tbox, title, card, stat, note,
                 bullets, footnote, table, pagenum, logo, theight, TEMPLATE, SHIFT, Y)

ASOF = "2026-10-05"
INTERNAL_NOTES = True
DATA = os.path.join(HERE, "data")
SH = json.load(open(os.path.join(DATA, f"spread_history_{ASOF}.json"), encoding="utf-8"))
SC = json.load(open(os.path.join(DATA, f"scenario_irr_moic_{ASOF}.json"), encoding="utf-8"))
OUT = os.environ.get("DECK_OUT") or os.path.join(HERE, "..", "exports", f"Liminality_French_Swap_Spreads_{ASOF}.pptx")
POLYMARKET = os.path.join(HERE, "..", "docs", "drafts", "draft-images", "slide10_Picture_5.png")

B = SH["primary_basis"]                       # "eur6m"
E = SH["by_basis"][B]
CUR = E["current"]
L1 = E["ladder_1y"][SH["pct_start"][:4]]
L5 = E["ladder_5y"][SH["pct_start"][:4]]
IT = E["italy"]
WK = SH["weekly"]
BASIS = SH["basis_eur6m_minus_ois_bp"]
INP = SC["model_inputs"]
NAMED = {n["id"]: n for n in SC["named"]}
TP = json.load(open(os.path.join(DATA, "third_party_facts_2026-10-06.json"), encoding="utf-8"))
PA, PC, PB = TP["political_alpha"], TP["pragmata_calendar"], TP["pragmata_budget_note"]
# The bond's spread, one number throughout: the model's entry spread on the trade date (-82.9bp). The Bloomberg
# 5y benchmark yield gives -83.1 and the bond's own mid -82.5 the same day; the bond IS the 5y benchmark, so the
# deck does not show two figures for it (Charlie, round 2).
BOND_BP = float(SC["model_inputs"]["Entry spread"])
DATA_DATE = dt.date.fromisoformat(SH["asof_data"])
PCT_YEAR = SH["pct_start"][:4]
NOTE_FILL, NOTE_INK = RGBColor.from_string("FFF4C2"), RGBColor.from_string("7A5A00")
VIOLET = RGBColor.from_string("6A4C93")
SKY = RGBColor.from_string("3C8DBC")      # second-series colour on charts; gold stays for the title rule and bullets
T_BODY, T_CARD, T_CAP = 14.0, 12.8, 11.0
MINUS = "−"


def bp(x, sign=False, dp=0):
    s = (("%+." if sign else "%.") + str(dp) + "f") % x
    return s.replace("-", MINUS) + "bp"


def pc(x, dp=1):
    return (("%." + str(dp) + "f") % x).replace("-", MINUS) + "%"


def rarer(pct, since=None):
    """'lower than 99.8% of days since 2010' reads better than '0.2th percentile'; at the low itself, say so."""
    if pct <= 0.0:
        return "the cheapest since %s" % (since or PCT_YEAR)
    return "lower than %s%% of days since %s" % (("%.1f" % (100 - pct)).rstrip("0").rstrip("."), since or PCT_YEAR)


def low_clause(ladder):
    """'; the low was -91bp (11/16/2011)' unless the low is today's observation."""
    if dt.date.fromisoformat(ladder["min_date"]) == DATA_DATE:
        return ""
    return "; the low was %s (%s)" % (bp(ladder["min"]), longdate(ladder["min_date"]))


def days_phrase(n):
    return "%d day%s" % (n, "" if n == 1 else "s") if n else "no day"


def rarity_5y():
    """How rare the bond's spread is for the 5-year point since the window start, phrased from the count."""
    n = CUR["days_5y_below_frtr32"]
    if n == 0:
        return "the cheapest since %s" % PCT_YEAR
    return ("a level seen on only %s since %s, %s"
            % (days_phrase(n), PCT_YEAR, span_phrase(CUR["days_5y_below_frtr32_span"])))


def span_phrase(span):
    """'all in November 2011' when the days fall in one month, else 'between <d1> and <d2>'."""
    if not span:
        return "never"
    a, b = (dt.date.fromisoformat(x) for x in span)
    if (a.year, a.month) == (b.year, b.month):
        return "all in %s" % a.strftime("%B %Y")
    return "between %s and %s" % (longdate(a), longdate(b))


def longdate(d):
    d = dt.date.fromisoformat(d) if isinstance(d, str) else d
    # US style, month/day/year, for the whole deck (Charlie, 2026-10-07); was "10/2/2026"
    return d.strftime("%#m/%#d/%Y") if os.name == "nt" else d.strftime("%-m/%-d/%Y")


def serial(d):
    """Excel serial day number, so an XY chart gets a true date axis."""
    d = dt.date.fromisoformat(d) if isinstance(d, str) else d
    return (d - dt.date(1899, 12, 30)).days


prs = Presentation(TEMPLATE)                 # Jeff's master, scaled (Charlie, 2026-10-07: "Jeff's band and serif")
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
N = [0]


def sl(dark=False):
    """A body page on Jeff's layout (band, logo); the title page (dark=True) is drawn over a white background."""
    s = blank(prs, keep_title=not dark)
    N[0] += 1
    if dark:
        bg(s, WHITE)
    else:
        pagenum(s, N[0])
    return s


def internal_note(slide, x, y, w, text, size=10.5):
    if not INTERNAL_NOTES:
        return
    note(slide, x, y, w, "INTERNAL NOTE - delete before circulation", text, size=size,
         fill=NOTE_FILL, line_=NOTE_INK, minh=0.70)


def xy_chart(slide, x, y, w, h, series, yfmt='0"bp"', legend=True, ymin=None, ymax=None,
             xmin=None, xmax=None, lab=9.5, major_years=2, xfmt="yyyy", xunit=None, markers=False, plot_layout=None):
    """Lines against a date axis (x as ISO strings) or a numeric axis (x as numbers; pass xfmt and xunit).
    series: list of dicts name, x, y, colour, width, dash."""
    cd = XyChartData()
    for sr in series:
        ser = cd.add_series(sr["name"])
        for a, b in zip(sr["x"], sr["y"]):
            if b is not None:
                ser.add_data_point(serial(a) if isinstance(a, str) else a, b)
    gf = slide.shapes.add_chart(XL_CHART_TYPE.XY_SCATTER_LINES if markers else XL_CHART_TYPE.XY_SCATTER_LINES_NO_MARKERS,
                                Inches(x), Y(y), Inches(w), Inches(h), cd)
    c = gf.chart
    # python-pptx writes no c:date1904 element; PowerPoint then reads the serial dates on the 1904 system and labels the
    # axis four years late (LibreOffice assumes 1900). Say 1900 explicitly. (Charlie saw "2014" at the left of a 2010 axis.)
    from pptx.oxml import parse_xml
    from pptx.oxml.ns import qn
    cs = c._chartSpace
    if cs.find(qn("c:date1904")) is None:
        cs.insert(0, parse_xml('<c:date1904 xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" val="0"/>'))
    c.has_title = False
    c.font.name = BFONT
    c.font.size = Pt(lab)
    c.has_legend = legend
    if legend:
        c.legend.position = XL_LEGEND_POSITION.TOP
        c.legend.include_in_layout = False
        c.legend.font.size = Pt(10.5)
        c.legend.font.color.rgb = GREY
    for pl, sr in zip(c.plots[0].series, series):
        pl.format.line.color.rgb = sr["colour"]
        pl.format.line.width = Pt(sr.get("width", 1.75))
        if sr.get("dash"):
            pl.format.line.dash_style = MSO_LINE.DASH
        pl.smooth = False
        if markers:
            from pptx.enum.chart import XL_MARKER_STYLE
            pl.marker.style = XL_MARKER_STYLE.CIRCLE
            pl.marker.size = 6
            pl.marker.format.fill.solid()
            pl.marker.format.fill.fore_color.rgb = sr["colour"]
            pl.marker.format.line.fill.background()
        if sr.get("label"):
            # a label on the series' last point, in the series colour, so a flat scenario line names itself
            from pptx.enum.chart import XL_LABEL_POSITION
            n_pts = sum(1 for v in sr["y"] if v is not None)
            dl = pl.points[n_pts - 1].data_label
            dl.has_text_frame = True
            dl.text_frame.text = sr["label"]
            dl.position = {"right": XL_LABEL_POSITION.RIGHT, "above": XL_LABEL_POSITION.ABOVE,
                           "below": XL_LABEL_POSITION.BELOW}[sr.get("label_pos", "right")]
            f = dl.text_frame.paragraphs[0].runs[0].font
            f.size = Pt(sr.get("label_size", 9))
            f.bold = True
            f.color.rgb = sr["colour"]
            f.name = BFONT
    va, ca = c.value_axis, c.category_axis
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = RULE
    va.major_gridlines.format.line.width = Pt(0.6)
    va.format.line.fill.background()
    ca.has_major_gridlines = False
    ca.format.line.color.rgb = RULE
    for ax, fmt in ((va, yfmt), (ca, xfmt)):
        ax.tick_label_position = XL_TICK_LABEL_POSITION.LOW
        ax.tick_labels.font.size = Pt(lab)
        ax.tick_labels.font.color.rgb = GREY
        ax.tick_labels.number_format = fmt
        ax.tick_labels.number_format_is_linked = False
    if ymin is not None:
        va.minimum_scale = ymin
    if ymax is not None:
        va.maximum_scale = ymax
    if xmin is not None:
        ca.minimum_scale = serial(xmin) if isinstance(xmin, str) else xmin
    if xmax is not None:
        ca.maximum_scale = serial(xmax) if isinstance(xmax, str) else xmax
    if xunit is not None:
        ca.major_unit = xunit
    else:
        # 366 for yearly ticks: 365 drifts a day a year and labels a leap year twice ("2012 2012")
        ca.major_unit = 366 if major_years == 1 else int(365.25 * major_years)
    if plot_layout:
        # pin the inner plot area at fixed fractions of the chart frame (x, y, w, h), so that a level on the value
        # axis maps to a known position on the slide and labels can be drawn outside the chart
        from pptx.oxml.ns import qn
        from pptx.oxml import parse_xml
        px, py, pw, ph = plot_layout
        pa = c._chartSpace.chart.plotArea
        old = pa.find(qn("c:layout"))
        if old is not None:
            pa.remove(old)
        lay = parse_xml('<c:layout xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart"><c:manualLayout>'
                        '<c:layoutTarget val="inner"/><c:xMode val="edge"/><c:yMode val="edge"/>'
                        '<c:x val="%f"/><c:y val="%f"/><c:w val="%f"/><c:h val="%f"/></c:manualLayout></c:layout>' % (px, py, pw, ph))
        pa.insert(0, lay)
    return c


def col_chart(slide, x, y, w, h, cats, series, yfmt='0.00"%"', lab=9.5, ymin=None, ymax=None, gap=60):
    """Clustered columns; series: list of (name, values, colour)."""
    from pptx.chart.data import CategoryChartData
    cd = CategoryChartData()
    cd.categories = cats
    for nm, vals, _c in series:
        cd.add_series(nm, vals)
    gf = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(x), Y(y), Inches(w), Inches(h), cd)
    c = gf.chart
    c.has_title = False
    c.font.name = BFONT
    c.font.size = Pt(lab)
    c.has_legend = True
    c.legend.position = XL_LEGEND_POSITION.TOP
    c.legend.include_in_layout = False
    c.legend.font.size = Pt(10.5)
    c.legend.font.color.rgb = GREY
    pl = c.plots[0]
    pl.gap_width = gap
    pl.has_data_labels = True
    pl.data_labels.number_format = yfmt
    pl.data_labels.number_format_is_linked = False
    pl.data_labels.font.size = Pt(lab)
    pl.data_labels.font.color.rgb = GREY
    for sr, (_n, _v, col) in zip(pl.series, series):
        sr.format.fill.solid()
        sr.format.fill.fore_color.rgb = col
        sr.format.line.fill.background()
    va, ca = c.value_axis, c.category_axis
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = RULE
    va.major_gridlines.format.line.width = Pt(0.6)
    va.format.line.fill.background()
    ca.format.line.color.rgb = RULE
    for ax in (va, ca):
        ax.tick_labels.font.size = Pt(lab)
        ax.tick_labels.font.color.rgb = GREY
    va.tick_labels.number_format = yfmt
    va.tick_labels.number_format_is_linked = False
    if ymin is not None:
        va.minimum_scale = ymin
    if ymax is not None:
        va.maximum_scale = ymax
    return c


def arrow(slide, x, y, w, h, colour, left=False):
    a = slide.shapes.add_shape(MSO_SHAPE.LEFT_ARROW if left else MSO_SHAPE.RIGHT_ARROW, Inches(x), Y(y), Inches(w), Inches(h))
    a.fill.solid(); a.fill.fore_color.rgb = colour; a.line.fill.background(); a.shadow.inherit = False
    return a


def box(slide, x, y, w, h, head, body, fill=NAVY, ink=WHITE, sub_ink=None, hsize=14, bsize=10.5):
    card(slide, x, y, w, h, fill=fill, line=None if fill != WHITE else RULE)
    tbox(slide, x + 0.15, y + 0.12, w - 0.30, h - 0.24, [(head, {"bold": True, "size": hsize, "font": HFONT}),
         (body, {"size": bsize, "colour": sub_ink or ink})], colour=ink, align=PP_ALIGN.CENTER, space_after=3,
         anchor=MSO_ANCHOR.MIDDLE)


def weekly(col, start=None, end=None):
    xs, ys = [], []
    for d, v in zip(WK["date"], WK[col]):
        if (start and d < start) or (end and d > end):
            continue
        xs.append(d)
        ys.append(v)
    return xs, ys


def flat(name, level, colour, start, end, width=1.25, label=None, label_pos="right"):
    return {"name": name, "x": [start, end], "y": [level, level], "colour": colour, "width": width, "dash": True,
            "label": label, "label_pos": label_pos}


FOOT_SIGN = "Spreads are the swap rate less the bond yield, so more negative is cheaper."      # Charlie, 2026-10-07
FOOT_CONSTRUCTION = ("Spreads are the swap rate less the bond yield, so a cheap OAT reads negative: versus the 6m Euribor swap "
                     "(Bloomberg EUSA), France and Italy yields are Bloomberg generic benchmark bonds at each tenor; the financing "
                     "leg of the trade is €STR, which sat %s below the 1y Euribor swap and %s below the 5y on %s. "
                     "Source: Bloomberg, Liminality calculations."
                     % (bp(BASIS["1y"]["current"]), bp(BASIS["5y"]["current"]), longdate(DATA_DATE)))

# Charlie, 2026-10-07: on every page that mentions hypothetical performance, in his words
HYPO = "Please see the disclosures page regarding the hypothetical performance results listed above."
BOND_NAME = INP["Bond Underlier"].replace("3 1/4", "3¼")
import csv                                                                                   # noqa: E402
with open(os.path.join(HERE, "..", "analysis", "data", "frtr32_price_yield_bbg_2026-10-07.csv"), encoding="utf-8") as _f:
    PX = {r["date"]: r for r in csv.DictReader(_f)}
PX_TRADE = PX[INP["Trade Date"]]          # the bond's clean price and mid yield on the trade date, Bloomberg Desktop API
TERMS = json.load(open(os.path.join(DATA, "structure_terms_2026-10-07.json"), encoding="utf-8"))   # the floor's cost and the collateral, Charlie 2026-10-07


def lead_bullets(slide, x, y, w, items, size=13.0, gap=12, line=1.14, colour=NAVY):
    """Numbered paragraphs with a bold lead ("Dislocation: ..."), as on Jeff's executive summary. Returns the y below."""
    cy = y
    for i, (lead, rest) in enumerate(items):
        full = lead + ": " + rest
        hgt = theight(full, w - 0.38, size, BFONT, True, False, line)      # bold metrics: the lead is bold, so never short
        tbox(slide, x, cy, 0.30, hgt, "%d." % (i + 1), size=size, bold=True, colour=colour, space_after=0, line=line)
        tb = tbox(slide, x + 0.38, cy, w - 0.38, hgt, full, size=size, colour=colour, space_after=0, line=line)
        para = tb.text_frame.paragraphs[0]
        r0 = para.runs[0]
        r0.text, r0.font.bold = lead + ": ", True
        r1 = para.add_run()
        r1.text = rest
        r1.font.name, r1.font.size, r1.font.bold = BFONT, Pt(size), False
        r1.font.color.rgb = colour
        cy += hgt + gap / 72.0
    return cy


# ---- data shared by several slides (hoisted when the slides became functions, 2026-10-07)
S3, S4, BE = NAMED["S3"], NAMED["S4"], NAMED["BE"]
BR = SC["breakeven_breaches_1y"]
LV = SH["levels_pct"]
MV = SH["moves"]
CV = json.load(open(os.path.join(DATA, "curve_2026-10-02.json"), encoding="utf-8"))
FI = json.load(open(os.path.join(DATA, "fiscal_2026-10-05.json"), encoding="utf-8"))
FY, FS, FL = FI["years"], FI["series"], FI["latest"]
LATEST_YEAR = FI["latest_year"]
RT = FI["ratings_frtr"]
HP = json.load(open(os.path.join(DATA, "hedge_pair_2026-10-02.json"), encoding="utf-8"))
HL, HH = HP["low"], HP["high"]



def slide_title():
    # 1. title, drawn to Jeff's title slide (received 2026-10-07): the logo on white above, a navy block below with the title
    # underlined, the subtitle in Charlie's words, the date and the confidential line. Layout placeholders are not used.
    s = sl(dark=True)
    logo(s, (W - 4.9) / 2, 1.85, 4.9)
    blk = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(5.0), Inches(W), Inches(H - 5.0))
    blk.fill.solid(); blk.fill.fore_color.rgb = NAVY; blk.line.fill.background(); blk.shadow.inherit = False
    tbox(s, M, 5.22, CW, 0.62, "French swap spreads", size=36, colour=WHITE, font=HFONT, align=PP_ALIGN.CENTER, raw=True,
         underline=True, space_after=0)
    tbox(s, M, 5.86, CW, 0.40, "5-year OAT swap spread with non-recourse financing", size=18, colour=WHITE, font=HFONT,
         align=PP_ALIGN.CENTER, raw=True, space_after=0)
    tbox(s, M, 6.30, CW, 0.40, "October 2026", size=20, colour=WHITE, font=HFONT, align=PP_ALIGN.CENTER, raw=True, underline=True,
         space_after=0)
    tbox(s, M, 6.78, CW, 0.62,
         [("CONFIDENTIAL AND PROPRIETARY — FOR DISCUSSION ONLY", {"size": 11}),
          ("This presentation contains confidential information and is intended solely for the use of the named recipient(s). "
           "Returns shown are scenario illustrations, gross of fees. Please read the important information.", {"size": 11})],
         colour=WHITE, align=PP_ALIGN.CENTER, raw=True, line=1.0, space_after=0)


def slide_disclaimer():
    # 2. disclaimer
    # The closing disclaimer of the US swap-spread deck (July 2025, slide 36), reproduced verbatim at Charlie's
    # request (round 6) in place of the put-writing deck's "Important information" page. Legal text is his and
    # his counsel's; nothing is paraphrased except the missing "be" in "were to be made", inserted at his request.
    s = sl()
    title(s, "Disclaimer")
    _DISC = [
        ("No offer or solicitation",
         "Nothing herein constitutes or should be construed as an offering of securities or a recommendation to purchase or "
         "sell securities or commodity interests. If an offer of securities were to be made in the future, it must be made only "
         "through a confidential private placement memorandum (“PPM”) and related subscription documents."),
        ("Eligibility requirements",
         "Potential investors must meet the eligibility requirements set forth in the PPM. The information contained herein "
         "is for informational and discussion purposes only, reflects the opinions of the author and no other person, and to "
         "the extent factual is accurate only as the date hereof. Liminality Capital does not undertake to update any "
         "information that subsequently becomes inaccurate. Past performance is no guarantee of future results."),
        ("Not advice",
         "This material is intended for informational purposes only and should not be construed as legal or tax advice, nor "
         "is it intended to replace the advice of a qualified attorney or tax advisor. The recipient should conduct his or "
         "her own analysis and consult with professional advisors prior to making any investment decisions."),
        # added by Charlie on 2026-10-07, verbatim
        ("Hypothetical Performance Results",
         "Hypothetical performance results in this presentation have certain inherent limitations. Unlike the results shown in "
         "an actual performance record, these results do not represent the weighting of the portfolio as actually traded. No "
         "representation is being made that any future investment will or is likely to achieve outcomes or profits or losses "
         "similar to these being shown. The hypothetical performance results are gross and do not factor in any expenses (fund "
         "or otherwise), investment management fees or performance allocations – net performance results will be lower."),
    ]
    # one text box, so the gaps between the blocks are uniform whatever line PowerPoint wraps on
    _items = []
    for _hd, _bd in _DISC:
        _items.append((_hd, {"bold": True, "font": HFONT, "size": 13.5, "colour": NAVY, "space_after": 3, "line": 1.0}))
        _items.append((_bd, {"size": 12.0, "colour": GREY, "space_after": 11, "line": 1.20}))
    tbox(s, M, 1.42, CW, 4.6, _items, size=12.0)


def slide_firm():
    # 3. the firm
    # The Relative Value Fund deck's own words, as re-set in the put-writing deck.
    s = sl()
    title(s, "Liminality Capital")
    FIRM = ["Established in 2018, Liminality Capital LP is a private investment firm based in Boston, MA. The firm is "
            "registered as a Commodity Pool Operator and Commodity Trading Advisor with the Commodity Futures Trading "
            "Commission and is a National Futures Association member.",
            "The firm’s primary investment vehicle, Liminality Partners LP, launched on June 1, 2019. Potential "
            "opportunities are drawn from a wide variety of asset classes, geographies, financial instruments and "
            "securities types, but with a particular focus on identifying price dislocations within derivatives markets "
            "to deliver asymmetric returns."]
    _ty = 1.52
    for _q in FIRM:
        _hh = theight(_q, 7.30 - 0.22, 14.5, BFONT, False, False, 1.32)
        tbox(s, M, _ty, 7.30, _hh, _q, size=14.5, colour=GREY, line=1.32, space_after=0)
        _ty += _hh + 0.26
    for _i, (_v, _l) in enumerate([("2018", "Firm established"), ("Boston, MA", "Headquarters"),
                                   ("CPO / CTA", "Registered with the CFTC; NFA member"),
                                   ("June 2019", "First fund launched")]):
        stat(s, 8.20, 1.52 + _i * 1.24, 4.51, _v, _l, vcolour=NAVY, h=1.10, vsize=26, lsize=T_CAP)



def slide_exec_summary():
    # 4. executive summary. Jeff's cut of 6-10/7/2026: three numbered bullets with bold leads, his wording verbatim with
    # the figures computed; the trade box on the right in his words, the price and yield filled from Bloomberg, the premium
    # and collateral split still his to supply ([EUR x], [EUR y]).
    s = sl()
    title(s, "Executive summary: the French swap spread opportunity",
          "Trade recommendation: buy the spread between a French government bond and the euro swap curve, financed for %.1f years "
          "with a floor making the leverage non-recourse" % INP["Yrs Time to Expiry"])
    _items = [
        ("Dislocation",
         "French government bonds (“OATs”) have dislocated against swaps in recent weeks as the market has grown nervous about "
         "French public finances amid increasing political uncertainty around budget negotiations and the increased probability "
         "of a populist government, left or right, in the upcoming April 2027 Presidential elections."),
        ("Non-recourse structuring",
         "The attractiveness of the opportunity is heavily dependent on a proprietary financing structure: our position is "
         "financed for %.1f years – within a year of maturity – with non-recourse leverage at €STR + %dbp, and a floor only "
         "%dbp out of the money." % (INP["Yrs Time to Expiry"], INP["Funding E+ (bps)"], -INP["Floor strike (from ATMF)"])),
        ("Asymmetry and pull to par",
         "Over the life of investment, the bond rolls from the %.1f-year point of the curve to the 1-year point, where a "
         "“pull to par” dynamic generally keeps spreads well anchored – in the case of France even through the euro sovereign "
         "crisis. If nothing changes, the roll alone returns %s a year (%.1fx). To break even, the 1-year spread at expiry just "
         "needs to be at %s or higher, a level even Spain never breached, and Italy breached only briefly, in November 2011."
         % (INP["Starting Bond Expiry"], pc(S3["irr"] * 100, 0), S3["moic"], bp(BE["spread_bp"]))),
    ]
    lead_bullets(s, M, 1.62, 7.40, _items, size=13.0, gap=12, line=1.14)
    _x, _w = 8.40, 4.31
    card(s, _x, 1.62, _w, 3.85, fill=ICE_BG)
    _lines = [
        ("The trade", {"bold": True, "font": HFONT, "size": 13.5, "space_after": 6}),
        ("Buy a %.1f-year France versus Euribor swap spread, financed for %.1f years with a floor making the leverage non-recourse."
         % (INP["Starting Bond Expiry"], INP["Yrs Time to Expiry"]), {"bold": True, "space_after": 10}),
        ("Buy %s at %.2f, i.e. a %.2f%% yield: %s over the matched swap, %s."
         % (BOND_NAME, float(PX_TRADE["frtr32_px_last"]), float(PX_TRADE["frtr32_yld_ytm_mid"]), bp(-BOND_BP), rarity_5y()), {}),
        # Charlie's wording of 2026-10-07; the three percentages are his, of bond notional, from deck/data/structure_terms_2026-10-07.json
        ("Pay fixed on a %.1f-year 6m Euribor swap, DV01-neutral." % INP["Starting Bond Expiry"], {}),
        ("Buy floor struck ATMF – %dbp for %.2f%%." % (-INP["Floor strike (from ATMF)"], TERMS["floor_cost_pct_notional"]), {}),
        ("Present value of our maximum loss, %.3f%%." % TERMS["pv_max_loss_pct_notional"], {}),
        ("Total capital at risk, %.2f%%." % TERMS["total_capital_pct_notional"], {"space_after": 10}),
        ("Spend 1.1m for 100m of swap spread exposure.", {"bold": True}),
    ]
    tbox(s, _x + 0.22, 1.80, _w - 0.44, 3.50, _lines, size=11.2, colour=NAVY, line=1.14, space_after=4)
    # Spain's low and the price/yield line cut from this footnote (Charlie, 2026-10-07); Spain's low stays in the data and on page 11's chart
    # the model sentence and the "constructed as on page 6" clause cut as redundant (Charlie, 2026-10-07)
    footnote(s, HYPO + " Italy's 1-year spread was below %s on %d trading days, %s to %s. Spreads are the swap rate less the bond yield "
                "versus the 6m Euribor swap. Source: Bloomberg, Liminality calculations."
                % (bp(BE["spread_bp"]), BR["ita"]["days_below_breakeven"], longdate(BR["ita"]["span"][0]), longdate(BR["ita"]["span"][1])))



def slide_what_is_swap_spread():
    # 5. what is a swap spread. Jeff's layout of 6-7 October: the definition and the sign convention as two statements across
    # the top, the yield curves and the spread curve side by side beneath. Text is Charlie's bullets of round 2, merged by Jeff.
    s = sl()
    title(s, "What is a swap spread?")
    _cw = (CW - 0.40) / 2
    tbox(s, M, 1.42, _cw, 1.0, "A swap spread is the difference between a government bond yield and the swap rate of the same "
         "maturity. To be “long” the swap spread, buy the OAT and pay fixed on the swap, fully hedging the duration.",
         size=13.0, colour=NAVY, line=1.14)
    tbox(s, M + _cw + 0.40, 1.42, _cw, 1.0, "In this deck the spread is the swap rate less the bond yield, so a bond that is cheap "
         "to swaps reads as a negative number.", size=13.0, bold=True, colour=NAVY, line=1.14)
    _cy = 2.62
    tbox(s, M, _cy, _cw, 0.28, "French yield curves, %s" % longdate(CV["asof"]), size=11, bold=True, colour=NAVY, font=HFONT)
    xy_chart(s, M, _cy + 0.30, _cw, 3.20, [
        {"name": "OAT yield", "x": CV["years"], "y": CV["oat_yield_pct"], "colour": NAVY, "width": 2.0},
        {"name": "6m Euribor swap rate", "x": CV["years"], "y": CV["swap_rate_pct"], "colour": SKY, "width": 2.0},
    ], yfmt='0.0"%"', xfmt='0"y"', xunit=5, xmin=0, xmax=30, markers=True, lab=9,
        ymin=0.5 * int(min(CV["swap_rate_pct"]) * 2), ymax=0.5 * (int(max(CV["oat_yield_pct"]) * 2) + 1))
    tbox(s, M + _cw + 0.40, _cy, _cw, 0.28, "Swap spread at each point of the curve (swap less OAT)", size=11, bold=True, colour=NAVY, font=HFONT)
    xy_chart(s, M + _cw + 0.40, _cy + 0.30, _cw, 3.20, [
        {"name": "Swap spread", "x": CV["years"], "y": CV["spread_bp"], "colour": NEG, "width": 2.0},
    ], yfmt='0"bp"', xfmt='0"y"', xunit=5, xmin=0, xmax=30, markers=True, legend=False, lab=9)
    # as-of date and source only (Charlie, 2026-10-07)
    footnote(s, "As of %s. Source: Bloomberg, Liminality calculations." % longdate(CV["asof"]))



def slide_dislocation():
    # 6. the dislocation. Jeff dropped the three cards (6-7 October); the chart runs full width and today's readings sit on the
    # lines as labels, so the page still states where the spread is.
    s = sl()
    title(s, "The current dislocation",
          "France swap spreads versus the 6m Euribor swap, weekly, since %s" % PCT_YEAR)
    _x1, _y1 = weekly("fra_1y_%s" % B, SH["pct_start"])
    _x5, _y5 = weekly("fra_5y_%s" % B, SH["pct_start"])
    xy_chart(s, M, 1.55, CW, 4.60, [
        {"name": "5-year", "x": _x5, "y": _y5, "colour": NAVY, "width": 2.0,
         "label": "5-year %s, %s" % (bp(CUR["fra_5y"]), rarer(CUR[f"fra_5y_pct_since_{PCT_YEAR}"])), "label_pos": "right", "label_size": 9.5},
        {"name": "1-year", "x": _x1, "y": _y1, "colour": SKY, "width": 2.0,
         "label": "1-year %s" % bp(CUR["fra_1y"]), "label_pos": "right", "label_size": 9.5},
    ], xmin=SH["pct_start"], xmax=str(DATA_DATE.replace(year=DATA_DATE.year + 3)))
    # Charlie's wording, 2026-10-07; the full construction stays in FOOT_CONSTRUCTION for the cut pages and the record
    footnote(s, FOOT_SIGN + " As of %s. Source: Bloomberg, Liminality calculations." % longdate(DATA_DATE))


def slide_why_dislocation():
    # 7. why the dislocation (drafted by Claude on Charlie's brackets, round 8)
    _fl, _fs, _fy = FI["latest"], FI["series"], FI["years"]
    s = sl()
    title(s, "Why is there a dislocation?")          # subheading removed (Charlie, 2026-10-07)
    _cw = (CW - 0.40) / 2
    card(s, M, 1.55, _cw, 4.75, fill=ICE_BG)
    card(s, M + _cw + 0.40, 1.55, _cw, 4.75, fill=WHITE, line=RULE)
    tbox(s, M + 0.28, 1.74, _cw - 0.56, 0.40, "Long-term factors", size=17, bold=True, font=HFONT)
    tbox(s, M + _cw + 0.68, 1.74, _cw - 0.56, 0.40, "Short-term factors", size=17, bold=True, font=HFONT)
    bullets(s, M + 0.28, 2.30, _cw - 0.56, [
        "Budget and fiscal: a deficit of %.1f%% of GDP in %d and debt of %.0f%% of GDP, the widest and the fastest-rising of "
        "the euro area's four large economies." % (-_fl["FR_balance_pct_gdp"], FI["latest_year"], _fl["FR_debt_pct_gdp"]),
        "Political dysfunction: no majority since June 2024, governments falling on the budget, and no visible will to fix "
        "the arithmetic before the 2027 election.",
        "A negative feedback loop: net interest has risen from %.1f%% of GDP in 2020 to %.1f%% in %d as the debt reprices, so "
        "higher yields push the deficit further." % (_fs["FR_net_interest_pct_gdp"][_fy.index(2020)], _fl["FR_net_interest_pct_gdp"], FI["latest_year"]),
    ], size=12.4, gap=9, line=1.12)
    bullets(s, M + _cw + 0.68, 2.30, _cw - 0.56, [
        # "ratings downgrade", with Scope's move spelled out (Charlie, 2026-10-07); the from/to checked against Bloomberg, 18 Sept 2026
        # "the kind of move that comes from forced sellers rather than new information" cut (Charlie, 2026-10-07)
        "Levered unwinds: the 5-year spread fell %.0fbp in ten trading days to %s. The triggers: the 2026 deficit target missed "
        "(%.1f%% against 5%%), a ratings "
        "downgrade (Scope, %s to %s), and Lagarde calling debt near 120%% of GDP a serious problem."
        % (-MV["fra_5y_change_10d_bp"], bp(CUR["fra_5y"]), PA["deficit_2026_pct"], PA["scope_downgrade"]["from"].replace("-", "−"),
           PA["scope_downgrade"]["to"]),
        # second clause in Charlie's words, 2026-10-07
        "Rates globally moving higher and more volatile: the 5-year euro swap rate is %.2f%% against %.2f%% a year ago, with "
        "the possibility that a global tightening cycle could still be in its early innings." % (MV["swap_5y_pct"], MV["swap_5y_1y_ago_pct"]),
        "Polls showing the far right and far left leading into the presidential election of April and May 2027.",
        # Charlie's wording, 2026-10-07 (spelling checked: Jean-Luc Mélenchon)
        "The far left-wing candidate for President, Mélenchon, recently proposed cancelling the French debt held by the "
        "central bank.",
    ], size=12.4, gap=9, line=1.12)
    internal_note(s, M + _cw + 0.68, 5.45, _cw - 0.56, "Short-term factors still need to be tweaked (Charlie, %s)." % longdate(dt.date(2026, 10, 7)), size=10)
    footnote(s, "Fiscal figures: Eurostat and OECD via Bloomberg, latest full year %d. Spread and swap moves: Bloomberg, to %s. Triggers: Political "
                "Alpha Research, 10/5/2026; Scope's downgrade of 9/18/2026 per Bloomberg. The attribution of the recent move to "
                "levered unwinds is Liminality's judgement. Source: Eurostat, OECD, Bloomberg, Political Alpha, Liminality calculations." % (FI["latest_year"], longdate(MV["asof"])))


def slide_trade():
    # 8. what is the trade: the TRS, as on slide 24 of the US deck
    BOND = INP["Bond Underlier"].replace("3 1/4", "3¼")
    s = sl()
    title(s, "What is the trade?", "Long the OAT, pay fixed on the swap, financed through a total return swap with a floor")
    # Bank top-left, Liminality top-right, the underlying bottom-left, as the US page lays it out
    _bx, _by, _bw, _bh = 1.40, 1.75, 3.00, 1.15
    _lx = 8.95
    box(s, _bx, _by, _bw, _bh, "Bank", "total return payer")
    box(s, _lx, _by, _bw, _bh, "Liminality", "total return receiver", fill=ICE_BG, ink=NAVY, sub_ink=GREY)
    box(s, _bx, 4.05, _bw, _bh, "Underlying asset", "%s and a matched 6m Euribor swap, pay fixed" % BOND, fill=WHITE, ink=NAVY, sub_ink=GREY, hsize=13)
    _ln = s.shapes.add_connector(1, Inches(_bx + _bw / 2), Y(_by + _bh), Inches(_bx + _bw / 2), Y(4.05))
    _ln.line.color.rgb = GREY; _ln.line.width = Pt(1.5)
    tbox(s, _bx + _bw / 2 + 0.12, 3.20, 2.4, 0.5, "underlying cash flows", size=10.5, colour=GREY)
    _ax, _aw = _bx + _bw + 0.20, _lx - (_bx + _bw) - 0.40
    arrow(s, _ax, 1.95, _aw, 0.34, POS)
    tbox(s, _ax, 1.50, _aw, 0.40, "total return on the package: carry plus price change", size=11, bold=True, colour=POS, align=PP_ALIGN.CENTER)
    arrow(s, _ax, 2.48, _aw, 0.34, GOLD, left=True)
    tbox(s, _ax, 2.86, _aw, 0.40, "€STR + %dbp, %.1f years of funding locked in" % (INP["Funding E+ (bps)"], INP["Yrs Time to Expiry"]),
         size=11, bold=True, colour=GOLD, align=PP_ALIGN.CENTER)
    note(s, 5.30, 4.05, 6.65, "Unique feature: limited downside",
         "The total return swap carries a floor struck %dbp out of the money. The most that can be lost is the capital posted, %sm per 100m "
         "of bond notional with the floor's cost included, and there is no margin call or refinancing before %s."
         % (-INP["Floor strike (from ATMF)"], "1.1", longdate(INP["Opt Expiry"])), size=11.5, line_=RULE, fill=WHITE)
    _terms = [["Bond", "Swap", "Financing", "Expiry", "Floor", "Capital"],
              [BOND, "6m Euribor, pay fixed, matched maturity", "TRS at €STR + %dbp" % INP["Funding E+ (bps)"],
               "%s (%.1f years)" % (longdate(INP["Opt Expiry"]), INP["Yrs Time to Expiry"]),
               "%dbp below the forward spread" % -INP["Floor strike (from ATMF)"], "%sm per 100m notional" % "1.1"]]
    table(s, M, 5.62, CW, _terms, size=10.0, rowh=0.42, headh=0.32, aligns=[PP_ALIGN.LEFT] * 6, neutral=(1,))
    footnote(s, "Terms as modelled on %s; entry spread %s versus the 6m Euribor swap, swap minus bond. Final terms are subject to "
                "documentation with the counterparty." % (longdate(INP["Trade Date"]), bp(INP["Entry spread"], dp=1)))


def slide_return_sources():
    # 9. the arithmetic: carry and roll-down
    s = sl()
    title(s, "Where the return comes from", "Carry on the package, the floating-rate basis, and roll-down; all per 100m of bond notional")
    _swap_matched = LV["frtr32_yield"] + INP["Entry spread"] / 100.0        # the matched-maturity swap, from the model's entry spread
    _cw3 = (CW - 0.60) / 3
    _y0 = 1.62
    _cards = [
        ("1  Carry on the spread", bp(-INP["Entry spread"], dp=1) + " a year", POS,
         "Receive the bond yield, %.2f%%. Pay the fixed swap rate of the same maturity, %.2f%%. The difference is the swap "
         "spread, earned for as long as the position is held." % (LV["frtr32_yield"], _swap_matched)),
        ("2  The floating legs", "basis less %dbp" % INP["Funding E+ (bps)"], GOLD,
         "The swap pays us 6m Euribor; the financing charges us €STR + %dbp. In the US version the two floating rates are "
         "both SOFR and cancel. Here the residual is the 6m Euribor / €STR basis, %s on the 5-year curve today, which widens "
         "when funding markets are stressed." % (INP["Funding E+ (bps)"], bp(BASIS["5y"]["current"]))),
        ("3  Roll-down", bp(S3["spread_bp"] - BOND_BP, sign=True) + " over the life", NAVY,
         "The bond is a %.1f-year bond at %s. At expiry it is a 1-year bond, and the 1-year point sits at %s today. If the "
         "curve does not move, the spread tightens by that difference as the bond rolls, taken as a price gain (the gain is the "
         "spread change times the DV01: about one cent per basis point for a one-year bond, more for a longer one)."
         % (INP["Starting Bond Expiry"], bp(BOND_BP), bp(S3["spread_bp"], dp=1))),
    ]
    for _i, (_hd, _big, _col, _bd) in enumerate(_cards):
        _cx = M + _i * (_cw3 + 0.30)
        card(s, _cx, _y0, _cw3, 2.95, fill=ICE_BG if _i != 1 else WHITE, line=None if _i != 1 else RULE)
        tbox(s, _cx + 0.22, _y0 + 0.20, _cw3 - 0.44, 0.34, _hd, size=14, bold=True, font=HFONT)
        tbox(s, _cx + 0.22, _y0 + 0.62, _cw3 - 0.44, 0.50, _big, size=24, bold=True, font=HFONT, colour=_col)
        tbox(s, _cx + 0.22, _y0 + 1.22, _cw3 - 0.44, 1.60, _bd, size=10.8, colour=GREY, line=1.12)
    # the chain on the capital, approximate and for intuition (Charlie, round 7): carry per year on capital, over the life,
    # plus the roll-down once; the model's multiple nets the basis and the option premium
    _CAP_M = 1.1
    _carry_yr = -INP["Entry spread"] * 1e-4 * 100 / _CAP_M * 100           # % of capital a year from the spread carry on 100m
    _carry_life = _carry_yr * INP["Yrs Time to Expiry"]
    _roll_once = (S3["spread_bp"] - BOND_BP) * 1e-4 * 100 / _CAP_M * 100  # % of capital, 1bp = 1 cent per 100 at a one-year duration
    note(s, M, 4.80, CW, "On the capital, approximately, for intuition",
         "The position is 100m of bond notional against %sm of capital. Carry of %.0fbp a year on 100m is about %.0f%% of the "
         "capital a year, or about %.0f%% over the %.1f years. The roll-down, about %.0fbp realised once at a one-year duration, "
         "adds about %.0f%%. That is roughly %.0f%% before the floating-leg basis and the cost of the floor; the model's %.2fx, "
         "which nets both, is on the scenario page."
         % (_CAP_M, -INP["Entry spread"], _carry_yr, _carry_life, INP["Yrs Time to Expiry"], S3["spread_bp"] - BOND_BP, _roll_once,
            _carry_life + _roll_once, S3["moic"]), size=11.5, line_=RULE, fill=WHITE)
    footnote(s, HYPO + " The same page on the €STR basis is in the appendix (page %d). Levels on %s: bond yield from Bloomberg; matched-maturity swap implied by the model's entry spread of %s; basis from "
                "the 5-year 6m Euribor swap less the 5-year €STR OIS. Roll-down ignores convexity and any change in the curve. "
                "Source: Bloomberg, Liminality calculations." % (page_of("app_return_estr"), longdate(DATA_DATE), bp(INP["Entry spread"], dp=1)), w=7.40)


def slide_not_credit():
    # 10. what a swap spread is, and is not
    # Charlie's argument, from his edit of 2026-10-05, set as prose; wording for his review
    s = sl()
    title(s, "A swap spread is not, in the usual case, a credit spread", "Why the gap exists, and what moves it")
    _y = bullets(s, M, 1.62, CW, [
        ("Sovereigns that borrow in a currency they print rarely default on that debt; the exceptions are few and mostly in "
         "emerging markets. A swap spread on such a bond is therefore not generally read as a measure of credit risk.", {"size": 14.0}),
        ("We would argue it is instead the product of three things:", {"size": 14.0}),
    ], gap=12, line=1.14)
    # Charlie's wording, round 4 (2026-10-05); one change of his: "increased the cost and capacity" read as a slip and is
    # set as "increased the cost, and reduced the capacity" -- revert if the original was intended
    _items = [("Plumbing", "An externality of problems in global funding markets that were created by new regulatory regimes "
                           "introduced after the global financial crisis: capital charges and leverage rules that significantly "
                           "increased the cost, and reduced the capacity, of banks to hold and finance government bonds."),
              ("Financing and mark-to-market risk", "Holding a highly leveraged bond position typically entails rolling your funding "
                                 "daily, with the risk that you won't be able to or the cost may spike – more of a risk than it used to "
                                 "be because of the plumbing. It also entails wearing the mark-to-market risk that can lead to collateral "
                                 "calls and drawdowns – which can be self-reinforcing."),
              ("Supply", "Made more acute by the growth in government bond issuance since the crisis, which has to be absorbed by "
                         "balance sheets that are now more constrained.")]
    _cw3 = (CW - 0.60) / 3
    for _i, (_hd, _bd) in enumerate(_items):
        _cx = M + _i * (_cw3 + 0.30)
        card(s, _cx, _y + 0.10, _cw3, 3.05, fill=ICE_BG if _i % 2 == 0 else WHITE, line=None if _i % 2 == 0 else RULE)
        _n = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(_cx + 0.22), Y(_y + 0.32), Inches(0.46), Inches(0.46))
        _n.fill.solid(); _n.fill.fore_color.rgb = NAVY; _n.line.fill.background(); _n.shadow.inherit = False
        _tf = _n.text_frame; _tf.margin_left = _tf.margin_right = 0
        _p = _tf.paragraphs[0]; _p.alignment = PP_ALIGN.CENTER
        _r = _p.add_run(); _r.text = "i" * (_i + 1) if _i < 2 else "iii"; _r.font.size, _r.font.bold, _r.font.name = Pt(14), True, HFONT
        _r.font.color.rgb = WHITE
        tbox(s, _cx + 0.82, _y + 0.30, _cw3 - 1.04, 0.56, _hd, size=13, bold=True, font=HFONT, line=1.0)
        tbox(s, _cx + 0.22, _y + 1.02, _cw3 - 0.44, 1.90, _bd, size=11.2, colour=GREY, line=1.14)
    footnote(s, "Local-currency defaults have occurred: Russia on its rouble GKO bills, August 1998, is the best-known; others (Reinhart and "
                "Rogoff) were mostly in emerging markets. The usual route for a currency-issuing sovereign under strain is inflation.")


def slide_france_different():
    # 11. France is different
    s = sl()
    title(s, "France is different: it does not print the currency it borrows in",
          "So a French swap spread can carry sovereign risk in a way a US or UK spread, in practice, does not")
    _y = bullets(s, M, 1.62, 7.55, [
        ("The United States and the United Kingdom issue debt in a currency their own central bank creates. France issues in "
         "euros, which the ECB controls on behalf of twenty members.", {"size": 13.5}),
        ("A French swap spread can therefore price some probability of a sovereign credit event, which is what it did for a "
         "variety of European government bonds including Italy and Spain in 2011 and 2012.", {"size": 13.5}),
        ("That sets the bar for this investment much higher than for a US swap spread investment. Our structure meets it "
         "several ways:", {"size": 13.5}),
    ], gap=11, line=1.14)
    # sub-bullets (Charlie, round 4); every figure computed
    _SP1 = E["spain"]["1y"]
    _y = bullets(s, M + 0.35, _y - 0.02, 7.20, [
        "Locked-up financing almost to maturity \u2013 just one year short.",
        "The floor caps the loss at the capital posted.",
        "Very attractive returns if \u201cnothing happens\u201d: %s a year (%.1fx) with the curve unchanged." % (pc(S3["irr"] * 100, 0), S3["moic"]),
        "The structure is robust: break-even for the 1-year spread at expiry is %s and full impairment %s, against an Italian "
        "1-year low of %s in 2011 and a Spanish low of %s. Italy's 1-year spread traded below %s for only %d days, and below %s "
        "for only %d days." % (bp(NAMED["BE"]["spread_bp"]), bp(NAMED["IMP"]["spread_bp"]), bp(IT["1y"]["min"]), bp(_SP1["min"]),
                              bp(IT["1y"]["stress_level_bp"]), IT["1y"]["days_below_stress"], bp(NAMED["BE"]["spread_bp"]),
                              BR["ita"]["days_below_breakeven"]),
    ], size=12.2, gap=7, line=1.12, dot=GREY)
    _x, _w = 8.55, 4.16
    stat(s, _x, 1.62, _w, bp(NAMED["BE"]["spread_bp"]), "1-year France spread at expiry for break-even", vcolour=NAVY, h=1.22)
    stat(s, _x, 2.98, _w, bp(IT["1y"]["min"]), "Italy's 1-year spread at its worst, %s" % longdate(IT["1y"]["min_date"]), vcolour=NEG, h=1.22)
    stat(s, _x, 4.34, _w, "%d days" % IT["1y"]["days_below_stress"], "trading days Italy's 1-year spread spent below %s, all in late 2011"
         % bp(IT["1y"]["stress_level_bp"]), vcolour=VIOLET, h=1.22)
    footnote(s, FOOT_CONSTRUCTION, w=7.30)


def slide_fiscal():
    # 12. the French fiscal situation (drafted by Claude, round 6)
    s = sl()
    title(s, "The French fiscal situation",
          "General government debt, %% of GDP, %d to %d: France against Italy, Spain and Germany" % (FY[0], LATEST_YEAR))
    _fy = [float(y) for y in FY]
    xy_chart(s, M, 1.55, 7.30, 3.55, [
        {"name": "France", "x": _fy, "y": FS["FR_debt_pct_gdp"], "colour": NAVY, "width": 2.5},
        {"name": "Italy", "x": _fy, "y": FS["IT_debt_pct_gdp"], "colour": NEG, "width": 1.5},
        {"name": "Spain", "x": _fy, "y": FS["ES_debt_pct_gdp"], "colour": RGBColor.from_string("2A9D8F"), "width": 1.5},
        {"name": "Germany", "x": _fy, "y": FS["DE_debt_pct_gdp"], "colour": GREY, "width": 1.5},
    ], yfmt='0"%"', xfmt="0", xunit=5, xmin=_fy[0], xmax=_fy[-1], lab=9, ymin=40)
    _rows = [["%d" % LATEST_YEAR, "France", "Italy", "Spain", "Germany"],
             ["Budget balance, % of GDP"] + [("%+.1f%%" % FL[f"{c}_balance_pct_gdp"]).replace("-", MINUS) for c in ("FR", "IT", "ES", "DE")],
             ["Gross debt, % of GDP"] + ["%.0f%%" % FL[f"{c}_debt_pct_gdp"] for c in ("FR", "IT", "ES", "DE")],
             ["Net interest, % of GDP"] + ["%.1f%%" % FL[f"{c}_net_interest_pct_gdp"] for c in ("FR", "IT", "ES", "DE")]]
    table(s, M, 5.22, 7.30, _rows, colw=[2.50, 1.20, 1.20, 1.20, 1.20], size=10.0, rowh=0.30, headh=0.32, neutral=range(1, 4))
    _x, _w = 8.25, 4.46
    _i20 = FY.index(2020)
    stat(s, _x, 1.55, _w, ("%+.1f%%" % FL["FR_balance_pct_gdp"]).replace("-", MINUS), "budget balance in %d, the widest in the euro area's big four; "
         "%s in %d" % (LATEST_YEAR, ("%+.1f%%" % FS["FR_balance_pct_gdp"][FY.index(2019)]).replace("-", MINUS), 2019), vcolour=NEG, h=1.18)
    stat(s, _x, 2.88, _w, "%.0f%%" % FL["FR_debt_pct_gdp"], "gross debt to GDP in %d, from %.0f%% in %d; Germany %.0f%%"
         % (LATEST_YEAR, FS["FR_debt_pct_gdp"][FY.index(2019)], 2019, FL["DE_debt_pct_gdp"]), vcolour=NAVY, h=1.18)
    stat(s, _x, 4.21, _w, "%.1f%%" % FL["FR_net_interest_pct_gdp"], "of GDP in net interest in %d, up from %.1f%% in 2020 as the debt reprices: "
         "the feedback loop in which higher yields widen the deficit" % (LATEST_YEAR, FS["FR_net_interest_pct_gdp"][_i20]), vcolour=NEG, h=1.18)
    tbox(s, _x, 5.50, _w, 1.05, "Ratings: S&P %s (%s, review 27 Nov), Moody's %s (negative, review 23 Oct), Fitch %s (%s). Fitch and S&P cut France "
         "to A+ in autumn 2025. The government's own draft budget takes debt from %.1f%% of GDP in 2026 to %.1f%% in 2027 and the interest "
         "bill from \u20ac%dbn to \u20ac%dbn."
         % (RT.get("RTG_SP_LT_LC_ISSUER_CREDIT", "").rstrip("u"), RT.get("RTG_SP_OUTLOOK", "").lower(), RT.get("RTG_MOODY_LONG_TERM", ""),
            RT.get("RTG_FITCH_LT_ISSUER_DEFAULT", "").rstrip("u"), RT.get("RTG_FITCH_OUTLOOK", "").lower(),
            PA["debt_2026_pct_gdp"], PA["debt_2027_pct_gdp"], PA["interest_2026_bn"], PA["interest_2027_bn"]), size=10.0, colour=GREY, line=1.12)
    footnote(s, "Eurostat general government gross debt and balance, OECD Economic Outlook net interest payments, annual, latest full year %d, "
                "via Bloomberg (%s). Ratings and review dates: Bloomberg and Pragmata Partners' calendar, October 2026. Draft-budget debt and "
                "interest path: Political Alpha Research, 10/5/2026. Source: Eurostat, OECD, Bloomberg, Pragmata, Political Alpha, Liminality."
                % (LATEST_YEAR, longdate(FI["asof"])), w=7.00)


def slide_politics():
    # 13. French politics (drafted by Claude, round 6; verify)
    s = sl()
    title(s, "French politics: the parties and the election", "A presidential election in the spring of 2027, with no bloc holding a majority")
    _y = bullets(s, M, 1.62, 7.55, [
        ("Since the dissolution of June 2024 the National Assembly has been split three ways, between the Rassemblement "
         "National, the left and the centre-right, with no bloc near a majority. Prime Minister Lecornu presented the 2027 "
         "budget on 10/1/2026: \u20ac%dbn of consolidation, a pay freeze, pensions indexed below inflation, a deficit of %.1f%% "
         "of GDP against %.1f%% this year. The Socialists say they will censure; the budget passes only if the RN abstains, "
         "and Le Pen has said she prefers an imperfect budget she can rewrite in office to a special law."
         % (PA["budget_total_effort_bn"], PA["deficit_2027_target_pct"], PA["deficit_2026_pct"]), {"size": 12.2}),
        ("The presidential election of 4/18/2027 and 5/2/2027 is the event the market is pricing. Marine Le Pen is the "
         "RN's candidate since the Paris Court of Appeal's ruling of 7/7/2026 cut her ineligibility to end before the vote; "
         "Jordan Bardella stood aside. She polls 33 to 35% in the first round and beats Philippe 57 to 43 and M\u00e9lenchon 69 to 31 "
         "in run-off tests. The Cour de cassation is expected to rule on her case by early April 2027, late in the campaign.", {"size": 12.2}),
        ("Rassemblement National: higher spending financed by growth and cuts elsewhere, including a return to retirement at 62. "
         "The party abandoned euro exit after the 2017 debate and proposes no referendum on EU membership.", {"size": 12.4}),
        ("La France Insoumise: higher taxes and spending. In August 2026 M\u00e9lenchon revived his proposal to cancel the roughly "
         "18% of French debt held by the Banque de France; the ECB's president called it a clear treaty violation on 10 "
         "September. It is the one proposal that speaks directly to the swap spread.", {"size": 12.4}),
        ("The centre and centre-right, the government's base, stand for consolidation but cannot pass it alone. Our advisers put "
         "the chance of the government falling this autumn at %s and of a dissolution at %s." % (PB["censure_probability"], PB["dissolution_probability"]), {"size": 12.2}),
    ], gap=7, line=1.10)
    _x, _w = 8.55, 4.16
    _pm = [("Le Pen", "44%"), ("Philippe", "20%"), ("M\u00e9lenchon", "13%"), ("Lisnard", "8%")]
    tbox(s, _x, 1.62, _w, 0.30, "Next president: Polymarket odds, 10/4/2026", size=11, bold=True, colour=NAVY, font=HFONT)
    _rows = [["Candidate", "Odds"]] + [[n, o] for n, o in _pm]
    table(s, _x, 1.96, _w, _rows, colw=[2.96, 1.20], size=10.5, rowh=0.30, headh=0.30, neutral=range(1, 5))
    tbox(s, _x, 3.62, _w, 0.30, "Polls, September 2026", size=11, bold=True, colour=NAVY, font=HFONT)
    _rows = [["First round (OpinionWay)", "Share"], ["Le Pen", "33 to 35%"], ["Mélenchon", "16 to 17%"],
             ["Run-off (Harris, 28 Sep)", "Result"], ["Le Pen v Philippe", "57 to 43"], ["Le Pen v Mélenchon", "69 to 31"]]
    table(s, _x, 3.96, _w, _rows, colw=[2.76, 1.40], size=10.5, rowh=0.30, headh=0.30, neutral=range(1, 6))
    tbox(s, _x, 5.84, _w, 0.72, "What matters for the trade is not who wins but whether the next government can pass a budget that "
         "stops the debt ratio rising, and whether any candidate questions the debt itself: the first drives the spread, the "
         "second is what the floor is for.", size=9.5, colour=GREY, line=1.08)
    footnote(s, "Odds: Polymarket, 10/4/2026. Polls: OpinionWay, September 2026, and Harris Interactive, 9/28/2026. Budget, RN "
                "position and polls via Political Alpha Research, 10/5/2026; probabilities via Pragmata Partners, 9/30/2026. "
                "Le Pen: Court of Appeal, 7/7/2026. Mélenchon: Reuters, 8/26/2026; Lagarde, 9/10/2026.")



def slide_no_default():
    # 13. why we don't think France will exit the EUR or default. Charlie's text of 10/7/2026, verbatim; the retirement-age
    # bracket filled from the Cour des comptes' February 2025 report (the pension system's own deficit, not the general deficit;
    # see the footnote); the output share computed from Eurostat. One typo corrected ("agrees to makes").
    s = sl()
    title(s, "Why we don't think France will exit the EUR or default")
    _lw = 5.75
    _y = bullets(s, M, 1.55, _lw, [
        # the retirement-age sentence removed (Charlie, 2026-10-07); the Cour des comptes figures stay in the facts file
        "France’s fiscal problems, while ugly and likely to get uglier in the near term, are not unsolvable. They are due only to a "
        "failure of political will thus far.",
        "When the consequences of their reckless fiscal policy become acute – and sufficiently onerous – the politics will change. "
        "When faced with the choice of “death or disease”, they will choose disease.",
        "What are the consequences they will be faced with?",
    ], size=13.0, gap=11, line=1.16)
    bullets(s, M + 0.35, _y - 0.02, _lw - 0.35, [
        "A spike in interest rates beyond some threshold – the “Liz Truss moment”.",
        "The potential collapse of their banks.",
    ], size=13.0, gap=7, line=1.14, dot=GREY)
    _x2 = M + _lw + 0.45
    _w2 = CW - _lw - 0.45
    _y2 = bullets(s, _x2, 1.55, _w2, [
        "In an acute crisis, and particularly if France agrees to make the necessary changes, we believe the ECB will step in to "
        "stabilize their debt markets.",
    ], size=13.0, gap=11, line=1.16)
    bullets(s, _x2 + 0.35, _y2 - 0.02, _w2 - 0.35, [
        "Political integration in Europe fundamentally changed in 2012, when they effectively socialized their collective debt. "
        "And we believe trade and national security issues are dramatically more significant today.",
        "France is too big to fail, with %.0f%% of euro-area output. A French default would be the end of the EUR."
        % dict(FI["share_rank_latest"])["FR"],
        "They already have the available tools, built and designed precisely for this purpose: the ESM, the ECB’s OMT and since "
        "2022 the Transmission Protection Instrument.",
        "Leaving the euro has no legal route short of leaving the EU, and no major party proposes it; the far right dropped the "
        "idea after 2017 because it lost votes.",
    ], size=12.6, gap=10, line=1.14, dot=GREY)
    footnote(s, "Output share: Eurostat nominal GDP %d via Bloomberg. ESM treaty in force %s; OMT announced %s; TPI %s. "
                "Source: Eurostat, ECB, ESM, Liminality." % (LATEST_YEAR, longdate("2012-09-27"), longdate("2012-09-06"), longdate("2022-07-21")))


def slide_ecb_eu():
    # 15. the ECB and EU as stabilisers (drafted by Claude, round 6)
    s = sl()
    title(s, "The ECB and the EU as stabilisers of bond prices",
          "Italy and Spain 1-year swap spreads versus 6m Euribor, weekly, 2010 to 2013, with the interventions marked")
    _EV = [("2010-05-10", "SMP"), ("2011-12-08", "3-year LTRO"), ("2012-07-26", "\u201cwhatever it takes\u201d"), ("2012-09-06", "OMT")]
    _xa, _ya = weekly("ita_1y_%s" % B, "2010-01-01", "2013-12-31")
    _xs, _ys = weekly("esp_1y_%s" % B, "2010-01-01", "2013-12-31")
    _ser = [{"name": "Italy", "x": _xa, "y": _ya, "colour": NEG, "width": 2.0},
            {"name": "Spain", "x": _xs, "y": _ys, "colour": RGBColor.from_string("2A9D8F"), "width": 2.0}]
    for _d, _nm in _EV:
        _ser.append({"name": _nm, "x": [_d, _d], "y": [-650, 150], "colour": GREY, "width": 1.0, "dash": True})
    _cx, _cy, _cw, _ch = M, 1.55, 7.55, 4.35
    _pl = (0.10, 0.10, 0.88, 0.80)
    xy_chart(s, _cx, _cy, _cw, _ch, _ser, legend=False, ymin=-650, ymax=150, xmin="2010-01-01", xmax="2013-12-31", major_years=1,
             plot_layout=_pl)
    _px0 = _cx + _pl[0] * _cw
    _pw = _pl[2] * _cw
    _s0, _s1 = serial("2010-01-01"), serial("2013-12-31")
    for _k, (_d, _nm) in enumerate(_EV):
        _xx = _px0 + (serial(_d) - _s0) / (_s1 - _s0) * _pw
        _row = 0.02 if _k % 2 == 0 else 0.24           # alternate two rows so the 2012 labels do not collide
        tbox(s, _xx - 0.55, _cy + _row, 1.10, 0.22, _nm, size=8.5, bold=True, colour=GREY, align=PP_ALIGN.CENTER, space_after=0)
    tbox(s, M, _cy + _ch + 0.05, 7.55, 0.30, "Italy in red, Spain in teal; dashed lines mark the announcements", size=9.5, colour=GREY)
    _x, _w = 8.55, 4.16
    _rows = [["When", "What", "Effect"],
             ["May 2010", "SMP: ECB buys peripheral bonds", "bought time, not trust"],
             ["Dec 2011", "3-year LTROs, \u20ac1tn to banks", "banks bought their sovereigns"],
             ["Jul 2012", "\u201cWhatever it takes\u201d", "the turn"],
             ["Sep 2012", "OMT: unlimited, conditional", "never used, never needed"],
             ["Mar 2015", "APP: QE across the area", "ECB the largest holder"],
             ["Mar 2020", "PEPP; then NGEU joint debt", "pandemic spreads capped"],
             ["Jul 2022", "TPI: buy on unwarranted widening", "announced before use"]]
    table(s, _x, 1.55, _w, _rows, colw=[0.80, 1.86, 1.50], size=9.0, rowh=0.40, headh=0.32, neutral=range(1, 8),
          aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.LEFT])
    tbox(s, _x, 4.95, _w, 1.2, "Each time the periphery's 1-year spreads blew out, the ECB or the EU added a tool, and each tool was "
         "larger and earlier than the last. The 2011 lows were made before the tools existed; a French episode would meet "
         "all of them on day one.", size=11.0, colour=GREY, line=1.16)
    footnote(s, "Spreads: swap rate less bond yield versus the 6m Euribor swap, Bloomberg generic 1-year benchmarks (Spain from October 2011). "
                "Announcement dates from the ECB. Source: Bloomberg, ECB, Liminality calculations.", w=7.30)


def slide_base_case():
    # 12. base case: the roll
    s = sl()
    title(s, "Base case: the bond rolls to the anchored 1-year point",
          "In %.1f years the %.1f-year bond becomes a 1-year bond. France swap spreads versus 6m Euribor, weekly, since 2021"
          % (INP["Yrs Time to Expiry"], INP["Starting Bond Expiry"]))
    _start5 = "%d-01-01" % (DATA_DATE.year - 5)
    _x1, _y1 = weekly("fra_1y_%s" % B, _start5)
    _x5, _y5 = weekly("fra_5y_%s" % B, _start5)
    _xb, _yb = weekly("frtr32_%s" % B, _start5)
    xy_chart(s, M, 1.62, 8.30, 4.85, [
        {"name": "5-year point", "x": _x5, "y": _y5, "colour": NAVY, "width": 2.0},
        {"name": "1-year point", "x": _x1, "y": _y1, "colour": SKY, "width": 2.0},
        {"name": "FRTR 3¼ 02/25/32", "x": _xb, "y": _yb, "colour": NEG, "width": 2.5},
    ], xmin=_start5, xmax=str(DATA_DATE), major_years=1)
    _x, _w = 9.25, 3.46
    stat(s, _x, 1.62, _w, bp(BOND_BP), "the bond today, %.1f years to maturity" % INP["Starting Bond Expiry"], vcolour=NEG, h=1.18)
    stat(s, _x, 2.95, _w, bp(S3["spread_bp"], dp=1), "the 1-year point today, interpolated to the bond's maturity at expiry", vcolour=SKY, h=1.18)
    stat(s, _x, 4.28, _w, bp(S3["spread_bp"] - BOND_BP, sign=True), "spread tightening from the roll alone if the curve is unchanged, "
         "worth %s a year" % pc(S3["irr"] * 100, 0), vcolour=POS, h=1.18)
    _five = ("The 5-year point is at its cheapest since %s today." % PCT_YEAR
             if dt.date.fromisoformat(L5["min_date"]) == DATA_DATE else
             "The 5-year point reached %s in the euro crisis (%s)." % (bp(L5["min"]), longdate(L5["min_date"])))
    tbox(s, _x, 5.62, _w, 0.80, "The 1-year point has never closed below %s since %s (%s). %s"
         % (bp(L1["min"]), PCT_YEAR, longdate(L1["min_date"]), _five), size=10.5, colour=GREY, line=1.12)
    footnote(s, FOOT_CONSTRUCTION)



def slide_scenario():
    # 10. scenario analysis. Jeff's layout of 6-7 October: each table row sits level with its dashed line (Charlie: "he lined up
    # the bullets to the lines"), the MOIC column dropped because the multiple labels the line, and the 10th-percentile row cut.
    # Here the row positions come from the axis scale, so they stay level if the data or the scale moves.
    s = sl()
    title(s, "Scenario analysis: %.1f-year IRR and multiple of capital at expiry" % INP["Yrs Time to Expiry"],
          "Returns depend on where the 1-year France swap spread is when the structure expires. The history since %s is on the left; "
          "the scenario levels are the dashed lines, each labelled with its multiple" % PCT_YEAR)
    _x1, _y1 = weekly("fra_1y_%s" % B, SH["pct_start"])
    _cols = {"S1": POS, "S2": POS, "S3": SKY, "S4": NAVY, "S5": VIOLET, "BE": GREY, "S6": NEG, "IMP": NEG}
    _order = [n["id"] for n in SC["named"] if n["id"] != "S2"]       # richest first; S2 (10th percentile) cut by Jeff
    _series = [{"name": "1-year France spread", "x": _x1, "y": _y1, "colour": NAVY, "width": 1.75}]
    _x_end = str(DATA_DATE)
    for _id in _order:
        _series.append(flat(_id, NAMED[_id]["spread_bp"], _cols[_id], SH["pct_start"], _x_end, width=1.5))
    _cx, _cy, _cw, _ch = M, 1.62, 5.55, 4.55
    _pl = (0.12, 0.03, 0.70, 0.87)          # inner plot area as fractions of the chart frame
    _ymin, _ymax = -650, 150
    xy_chart(s, _cx, _cy, _cw, _ch, _series, legend=False, ymin=_ymin, ymax=_ymax, xmin=SH["pct_start"], xmax=_x_end,
             major_years=4, plot_layout=_pl)
    _plot_right = _cx + (_pl[0] + _pl[2]) * _cw
    _plot_top, _plot_h = _cy + _pl[1] * _ch, _pl[3] * _ch

    def _ypos(level):
        return _plot_top + (_ymax - level) / (_ymax - _ymin) * _plot_h

    # the multiple at each line's right-hand end, stacked where lines are too close for separate labels
    _lab_h, _gap = 0.17, 0.02
    _labels = []
    for _id in _order:
        _ly = _ypos(NAMED[_id]["spread_bp"])
        _ty = _ly - _lab_h / 2
        if _labels and _ty < _labels[-1][2] + _lab_h + _gap:
            _ty = _labels[-1][2] + _lab_h + _gap
        _labels.append((_id, _ly, _ty))
    for _id, _ly, _ty in _labels:
        _n = NAMED[_id]
        _txt = "%.1fx" % _n["moic"] if _n["moic"] > 0 else "0x"
        _ln = s.shapes.add_connector(1, Inches(_plot_right), Y(_ly), Inches(_plot_right + 0.20), Y(_ty + _lab_h / 2))
        _ln.line.color.rgb = _cols[_id]; _ln.line.width = Pt(0.75)
        tbox(s, _plot_right + 0.24, _ty, 0.60, _lab_h, _txt, size=9, bold=True, colour=_cols[_id], space_after=0, line=1.0)
    # the table: one row per scenario, its top set so the text sits level with the line; rows pushed down where lines bunch
    _gap1 = NAMED["S3"]["spread_bp"] - L1["min"]
    _s3 = "Roll to spot: curve unchanged (%s above the 1-year low since %s)" % (bp(_gap1), PCT_YEAR) if _gap1 > 1.5 \
        else "Roll to spot: curve unchanged (within 1bp of the 1-year low since %s)" % PCT_YEAR
    _s4 = ("No roll: the bond's spread unchanged (the 5-year point's cheapest since %s)" % PCT_YEAR
           if CUR["days_5y_below_frtr32"] == 0 else
           "No roll: the bond's spread unchanged (within %s of the 5-year low since %s)" % (bp(abs(L5["min"] - BOND_BP)), PCT_YEAR))
    _short = {"S1": "Median since %s" % PCT_YEAR, "S2": "10th percentile since %s" % PCT_YEAR, "S3": _s3, "S4": _s4,
              "S5": "Italy's 2011 crisis level: below this for only %d trading days" % IT["1y"]["days_below_stress"],
              "BE": "Investment break-even",
              "S6": "Italy's 1-year point at its euro-crisis low, %s" % dt.date.fromisoformat(IT["1y"]["min_date"]).strftime("%#m/%#d/%Y" if os.name == "nt" else "%-m/%-d/%Y"),
              "IMP": "Full impairment at expiry"}
    # rows as positioned text, not a table: PowerPoint enforces a minimum row height that pushed table rows off the lines
    _hmin, _lift = 0.27, 0.12
    _tops = []
    for _id in _order:
        _want = _ypos(NAMED[_id]["spread_bp"]) - _lift
        _tops.append(max(_want, _tops[-1] + _hmin) if _tops else _want)
    _tx, _tw = 6.72, 5.99
    _cx1, _cx2, _cx3 = _tx + 0.30, _tx + 1.08, _tx + 1.82          # dot | spread | IRR | scenario
    _hy = _tops[0] - 0.36
    for _xx, _ww, _lab, _al in ((_cx1, 0.72, "Spread", PP_ALIGN.RIGHT), (_cx2, 0.68, "IRR", PP_ALIGN.RIGHT),
                                (_cx3, _tw - 1.82, "Scenario: 1-year spread at expiry", PP_ALIGN.LEFT)):
        tbox(s, _xx, _hy, _ww, 0.22, _lab, size=9.5, bold=True, colour=NAVY, align=_al, space_after=0, line=1.0)
    _rule = s.shapes.add_connector(1, Inches(_tx), Y(_hy + 0.26), Inches(_tx + _tw), Y(_hy + 0.26))
    _rule.line.color.rgb = NAVY; _rule.line.width = Pt(1.0)
    for _i, _id in enumerate(_order):
        _n = NAMED[_id]
        _ty = _tops[_i]
        _d = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(_tx + 0.08), Y(_ty + 0.04), Inches(0.13), Inches(0.13))
        _d.fill.solid(); _d.fill.fore_color.rgb = _cols[_id]; _d.line.fill.background(); _d.shadow.inherit = False
        tbox(s, _cx1, _ty, 0.72, 0.20, bp(_n["spread_bp"], dp=1 if _n["spread_bp"] != round(_n["spread_bp"]) else 0), size=9.5,
             colour=NAVY, align=PP_ALIGN.RIGHT, space_after=0, line=1.0)
        tbox(s, _cx2, _ty, 0.68, 0.20, pc(_n["irr"] * 100, 1) if _n["moic"] > 0 else "total loss", size=9.5, colour=NAVY,
             align=PP_ALIGN.RIGHT, space_after=0, line=1.0)
        tbox(s, _cx3, _ty, _tw - 1.82, 0.20, _short[_id], size=9.5, colour=NAVY, space_after=0, line=1.0)
    # cut to the disclosure sentence, the entry spread and the source (Charlie, 2026-10-07)
    footnote(s, HYPO + " Entry spread %s. Source: Bloomberg, Liminality calculations." % bp(INP["Entry spread"], dp=1))



def slide_stress():
    # 11. the stress analogue. Jeff's title and subtitle (6-7 October); the three cards dropped, the chart centred with its own
    # caption. 1-year only (Charlie, round 2). The card figures moved to the footnote and the risks page.
    s = sl()
    title(s, "Risk: Italy and Spain during the euro crisis", "Our structure rolls into a 1-year swap spread at expiry")
    tbox(s, M, 1.52, CW, 0.30, "1-year swap spreads versus 6m Euribor, weekly, 2010 to 2013", size=12, bold=True, colour=NAVY,
         font=HFONT, align=PP_ALIGN.CENTER)
    _xa, _ya = weekly("ita_1y_%s" % B, "2010-01-01", "2013-12-31")
    _xs, _ys = weekly("esp_1y_%s" % B, "2010-01-01", "2013-12-31")
    _xf, _yf = weekly("fra_1y_%s" % B, "2010-01-01", "2013-12-31")
    xy_chart(s, M + 0.90, 1.84, CW - 1.80, 4.40, [
        {"name": "Italy", "x": _xa, "y": _ya, "colour": NEG, "width": 2.25},
        {"name": "Spain", "x": _xs, "y": _ys, "colour": RGBColor.from_string("2A9D8F"), "width": 2.0},
        {"name": "France", "x": _xf, "y": _yf, "colour": NAVY, "width": 2.0},
        flat("Break-even", NAMED["BE"]["spread_bp"], GREY, "2010-01-01", "2013-12-31", width=1.5,
             label="break-even %s" % bp(NAMED["BE"]["spread_bp"])),
    ], xmin="2010-01-01", xmax="2014-06-30", major_years=1)
    _sp = IT["1y"]["days_below_stress_span"]
    FC = E["france_crisis"]["1y"]
    SP = E["spain"]["1y"]
    # cut to one fact and the source (Charlie, 2026-10-07)
    footnote(s, "Italy's 1-year spread bottomed at %s on %s. Source: Bloomberg, Liminality calculations."
                % (bp(IT["1y"]["min"]), longdate(IT["1y"]["min_date"])))



def slide_risks():
    # 12. risks. Charlie, 2026-10-07: the drafted text and the subheader taken out; Jeff's three headings of 6-7 October stay as the
    # skeleton with an internal note that the text is to be added. The earlier draft is in git history (commit after 0f7bf0f).
    s = sl()
    title(s, "Risks")
    _y = bullets(s, M, 1.62, CW, [
        ("Near-term mark to market", {"size": 14.0, "bold": True}),
        ("At expiry: a dislocation to Italy's 2011 levels on %s" % longdate(INP["Opt Expiry"]), {"size": 14.0, "bold": True}),
        ("Before expiry: a crisis that leads to exit from the euro, or default", {"size": 14.0, "bold": True}),
    ], gap=14, line=1.1)
    internal_note(s, M, _y + 0.30, CW, "Text to add (Charlie, %s)." % longdate(dt.date(2026, 10, 7)))



def slide_app_calendar():
    # 20. appendix: the calendar and the election odds
    s = sl()
    title(s, "Appendix: the political and fiscal calendar", "From the RN counter-budget to the second round of the presidential election")
    _rows = [["When", "What"]] + [[d, w] for d, w in PC["events"]]
    table(s, M, 1.55, CW, _rows, colw=[1.90, CW - 1.90], size=10.0, rowh=0.26, headh=0.30, neutral=range(1, len(_rows)),
          aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT])
    footnote(s, "Calendar: Pragmata Partners, French Political and Fiscal Risk Calendar prepared for Liminality, October 2026; ratings as stated "
                "there. Source: Pragmata.")


def slide_app_hedge():
    # appendix: hedges, the low-coupon / high-coupon pair (moved to the appendix, round 4) (Charlie, 2026-10-05)
    s = sl()
    title(s, "Appendix: a low-coupon / high-coupon OAT pair as a hedge",
          "Whether a hedge is needed, and one that would pay if the market started to price an actual default")
    _y = bullets(s, M, 1.55, 7.30, [
        ("It is not clear that we need or want a hedge: in one sense the floor already provides it. There may nonetheless be "
         "cheap and effective hedges available, including EURUSD downside, CDS on French banks and SX7E implied volatility.", {"size": 12.0}),
        ("In particular: buy %s, sell %s. Roughly the same yield (%s apart) and z-spread, but the low-coupon bond trades at %.0f%% of "
         "the price of the high-coupon one. If the market starts to price actual sovereign default risk, bonds trade on price "
         "points rather than yield: the low coupon could trade up while the high coupon is crushed."
         % (HL["name"].replace("0.5", "0½").replace(" 144A", ""), HH["name"].replace("4.5", "4½"), bp(HP["yield_gap_bp"], dp=1),
            HP["price_ratio"] * 100), {"size": 12.0}),
    ], gap=9, line=1.12)
    _rows = [["", "Buy: FRTR 0½ 2040", "Sell: FRTR 4½ 2041"],
             ["Price", "%.2f" % HL["price"], "%.2f" % HH["price"]],
             ["Mid yield", "%.3f%%" % HL["ytm"], "%.3f%%" % HH["ytm"]],
             ["Years to maturity", "%.1f" % HL["years_to_maturity"], "%.1f" % HH["years_to_maturity"]],
             ["Modified duration", "%.1f" % HL["modified_duration"], "%.1f" % HH["modified_duration"]]]
    _bot = table(s, M, _y + 0.10, 3.55, _rows, colw=[1.35, 1.10, 1.10], size=10.0, rowh=0.30, headh=0.32, neutral=range(1, 5),
                 aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT])
    DN = HP["sizings"]["dv01_neutral"]
    _crows = [["Both bonds at", "Long leg", "Short leg", "Net, per 100 face sold"]]
    for r in DN["convergence"]:
        _lab = "%d (recovery)" % r["common_price"] if r["common_price"] == DN["recovery"] else "%d" % r["common_price"]
        _crows.append([_lab, "%+.1f" % r["long_leg"], "%+.1f" % r["short_leg"], "%+.1f" % r["net"]])
    _bot2 = table(s, M + 3.75, _y + 0.10, 3.55, _crows, colw=[1.15, 0.75, 0.75, 0.90], size=10.0, rowh=0.30, headh=0.32)
    tbox(s, M, max(_bot, _bot2) + 0.16, 7.30, 0.9,
         "DV01-neutral: buy %.0f face of the low coupon per 100 of the high coupon sold, so the pair has no duration. At a %d%% "
         "recovery, both bonds at %d, it earns %+.0f per 100 sold (%+.0f long, %+.0f short), and it is positive at any common price "
         "down to %d. Carry: the long leg earns %.2f%% on %.0f of market value (%.1f a year) against %.2f%% paid on %.0f (%.1f); the "
         "%.0f of cash released earns about %.1f%%, %.2f; about 10 through the middle costs %.2f a year; all-in about %.2f a year."
         % (DN["face_low_per_100_high"] * 100, DN["recovery"], DN["recovery"], DN["at_recovery"]["net"], DN["at_recovery"]["long_leg"],
            DN["at_recovery"]["short_leg"], DN["convergence"][-1]["common_price"], HL["ytm"], DN["market_value_low"],
            HL["ytm"] / 100 * DN["market_value_low"], HH["ytm"], DN["market_value_high"], HH["ytm"] / 100 * DN["market_value_high"],
            DN["excess_cash"], DN["cash_rate"] * 100, DN["cash_income_per_year"], DN["bid_offer_per_year"], -DN["net_carry_all_in_per_year"]),
         size=9.5, colour=GREY, line=1.10)
    HW = HP["weekly"]
    tbox(s, 8.30, 1.50, 4.41, 0.26, "Mid yield to maturity, weekly since %s" % HP["history"]["first"][:4], size=10.5, bold=True, colour=NAVY, font=HFONT)
    xy_chart(s, 8.30, 1.74, 4.41, 2.05, [
        {"name": "FRTR 4½ 2041", "x": HW["date"], "y": HW["high_ytm"], "colour": NEG, "width": 1.75},
        {"name": "FRTR 0½ 2040", "x": HW["date"], "y": HW["low_ytm"], "colour": NAVY, "width": 1.75},
    ], yfmt='0.0"%"', xmin=HW["date"][0], xmax=HW["date"][-1], major_years=2, lab=8.5)
    tbox(s, 8.30, 3.84, 4.41, 0.26, "Price, same two bonds", size=10.5, bold=True, colour=NAVY, font=HFONT)
    xy_chart(s, 8.30, 4.08, 4.41, 2.05, [
        {"name": "FRTR 4½ 2041", "x": HW["date"], "y": HW["high_price"], "colour": NEG, "width": 1.75},
        {"name": "FRTR 0½ 2040", "x": HW["date"], "y": HW["low_price"], "colour": NAVY, "width": 1.75},
    ], yfmt='0', xmin=HW["date"][0], xmax=HW["date"][-1], major_years=2, lab=8.5, legend=False)
    tbox(s, 8.30, 6.16, 4.41, 0.40, "Yields within %s to %s of each other over the whole period; the price ratio moved from %.2f to %.2f."
         % (bp(HP["history"]["yield_gap_bp_min"]), bp(HP["history"]["yield_gap_bp_max"]), HP["history"]["price_ratio_first"], HP["history"]["price_ratio_last"]),
         size=9.5, colour=GREY, line=1.1)
    footnote(s, "Prices and yields as of %s; history daily from Bloomberg. Durations computed from the quoted yields (annual coupons, "
                "ACT/ACT; computed clean prices %.2f and %.2f). Convergence payoffs ignore carry; cash rate and bid-offer are assumptions. "
                "Source: Bloomberg, Liminality calculations." % (longdate(HP["asof"]), HL["computed_clean"], HH["computed_clean"]), w=7.30)


def slide_app_estr():
    # appendix: ESTR vs Euribor (moved from the body, Charlie 2026-10-05)
    s = sl()
    title(s, "Appendix: €STR and Euribor, the two floating rates in the trade",
          "6m Euribor swap rate less €STR OIS rate, 1-year and 5-year, weekly since 2007")
    _xb1, _yb1 = weekly("basis_1y", "2007-01-01")
    _xb5, _yb5 = weekly("basis_5y", "2007-01-01")
    xy_chart(s, M, 1.55, 7.60, 4.30, [
        {"name": "1-year", "x": _xb1, "y": _yb1, "colour": SKY, "width": 1.75},
        {"name": "5-year", "x": _xb5, "y": _yb5, "colour": NAVY, "width": 2.0},
    ], xmin="2007-01-01", xmax=str(DATA_DATE), ymin=0)
    _x, _w = 8.55, 4.16
    note(s, _x, 1.55, _w, "€STR",
         "The euro short-term rate: the overnight rate at which euro-area banks borrow unsecured in the wholesale market, "
         "published by the ECB since October 2019 as the successor to EONIA. It is unsecured, where SOFR is a secured repo rate, "
         "but both are overnight and near risk-free; it is the rate our financing is set over.", size=10.2, line_=RULE, fill=WHITE)
    note(s, _x, 3.22, _w, "6m Euribor",
         "The rate at which euro-area banks lend to each other unsecured for six months. It carries a term and bank-credit "
         "premium over €STR, so it sits above it, by more in a funding stress. It is the floating leg of the standard euro "
         "swap, and so of ours.", size=10.2, line_=RULE, fill=WHITE)
    note(s, _x, 4.89, _w, "Why it helps the trade",
         "We receive 6m Euribor on the swap and pay €STR + %dbp on the financing, so we are long the basis. It averaged %s at "
         "1 year in 2008 to 2012 and is %s today." % (INP["Funding E+ (bps)"], bp(BASIS["1y"]["mean_2008_2012"]), bp(BASIS["1y"]["current"])),
         size=10.2, fill=ICE_BG)
    tbox(s, M, 5.95, 7.60, 0.70, "The spread history in this deck is measured against the 6m Euribor swap, the curve the trade pays fixed on. "
         "Measured against €STR every spread would sit lower by the basis shown here; the appendix shows both.", size=10.5, colour=GREY, line=1.14)
    footnote(s, "Source: Bloomberg EUSA (6m Euribor swaps) and EESWE (€STR OIS; EONIA less 8.5bp before October 2019, the ECB's recalibration). "
                "Liminality calculations.")


def slide_app_bases():
    # 18. appendix: both bases
    s = sl()
    title(s, "Appendix: the swap curve the spread is measured against",
          "France 5-year swap spread versus the 6m Euribor swap and versus €STR OIS, weekly since 2007")
    _xe, _ye = weekly("fra_5y_eur6m", "2007-01-01")
    _xo, _yo = weekly("fra_5y_ois", "2007-01-01")
    xy_chart(s, M, 1.55, 8.30, 4.95, [
        {"name": "vs 6m Euribor swap (used in this deck)", "x": _xe, "y": _ye, "colour": NAVY, "width": 2.0},
        {"name": "vs €STR OIS (the financing leg)", "x": _xo, "y": _yo, "colour": SKY, "width": 1.75},
    ], xmin="2007-01-01", xmax=str(DATA_DATE))
    _yrs = sorted(BASIS["5y"]["yearly_mean"])
    _brows = [["Period", "1y basis", "5y basis"],
              ["2008 to 2012 average", bp(BASIS["1y"]["mean_2008_2012"]), bp(BASIS["5y"]["mean_2008_2012"])],
              ["%s to date average" % PCT_YEAR, bp(BASIS["1y"][f"mean_since_{PCT_YEAR}"]), bp(BASIS["5y"][f"mean_since_{PCT_YEAR}"])],
              [longdate(DATA_DATE), bp(BASIS["1y"]["current"]), bp(BASIS["5y"]["current"])]]
    _bot = table(s, 9.25, 1.55, 3.46, _brows, colw=[1.66, 0.90, 0.90], size=10.0, rowh=0.36, headh=0.36, neutral=range(1, 4))
    tbox(s, 9.25, _bot + 0.20, 3.46, 2.60,
         "The trade pays fixed on a 6m Euribor swap, so that is the spread the scenario returns are built on. The financing "
         "leg is €STR. The gap between the two curves, the Euribor / €STR basis, is what separates the lines: "
         "it widens in a funding stress, which helps the trade. The €STR series is Bloomberg's, with EONIA less 8.5bp before "
         "October 2019, the ECB's own recalibration.", size=10.5, colour=GREY, line=1.14)
    footnote(s, FOOT_CONSTRUCTION)


def slide_app_return_estr():
    # appendix: slide 9 with the spread measured against €STR OIS, the financing rate, so the floating legs cancel (Charlie,
    # 2026-10-07: "a version of this slide with €STR, out in the appendix"). Figures from the model inputs, the trade-date levels
    # and the OIS-basis history; the bond's €STR spread is the model's entry spread less the 5-year basis (one number, decision 0007).
    s = sl()
    title(s, "Appendix: the return as if the swap were on €STR",
          "The same three sources with the spread measured against €STR OIS, the financing rate; all per 100m of bond notional")
    _b5, _b1 = BASIS["5y"]["current"], BASIS["1y"]["current"]
    _swap_eur = LV["frtr32_yield"] + INP["Entry spread"] / 100.0
    _swap_estr = _swap_eur - _b5 / 100.0
    _fund = INP["Funding E+ (bps)"]
    _bond_estr = BOND_BP - _b5                       # the bond's spread versus €STR
    _s3_estr = S3["spread_bp"] - _b1                 # the 1-year point it rolls to, on the €STR basis
    _roll_estr, _roll_eur = _s3_estr - _bond_estr, S3["spread_bp"] - BOND_BP
    _cards = [
        ("1  Carry on the spread", bp(-_bond_estr) + " a year", POS,
         "Receive the bond yield, %.2f%%. Pay the €STR swap rate of the same maturity, %.2f%%. The spread versus €STR is %s: the "
         "Euribor spread of %s plus the %s Euribor / €STR basis." % (LV["frtr32_yield"], _swap_estr, bp(_bond_estr), bp(BOND_BP), bp(_b5))),
        ("2  The floating legs", "cancel, less %dbp" % _fund, GOLD,
         "The €STR swap pays us €STR; the financing charges us €STR + %dbp. The two floating rates cancel, as SOFR does in the US "
         "version, and the funding spread is all that is left: %s − %dbp = %s a year of net carry."
         % (_fund, bp(-_bond_estr), _fund, bp(-_bond_estr - _fund))),
        ("3  Roll-down", bp(_roll_estr, sign=True) + " over the life", NAVY,
         "On the €STR basis the 1-year point sits at %s today, so the roll from %s is %s, against %s on the Euribor basis. The "
         "%s gap is the slope of the basis curve, %s at 1 year against %s at 5 years, which the Euribor spread carries and the €STR "
         "spread does not. The model works on the Euribor spread." % (bp(_s3_estr), bp(_bond_estr), bp(_roll_estr), bp(_roll_eur),
                                                                      bp(_roll_eur - _roll_estr), bp(_b1), bp(_b5))),
    ]
    _cw3 = (CW - 0.60) / 3
    _y0, _h = 1.55, 2.45
    for _i, (_hd, _big, _col, _bd) in enumerate(_cards):
        _cx = M + _i * (_cw3 + 0.30)
        card(s, _cx, _y0, _cw3, _h, fill=ICE_BG if _i != 1 else WHITE, line=None if _i != 1 else RULE)
        tbox(s, _cx + 0.22, _y0 + 0.16, _cw3 - 0.44, 0.32, _hd, size=13, bold=True, font=HFONT)
        tbox(s, _cx + 0.22, _y0 + 0.50, _cw3 - 0.44, 0.44, _big, size=20, bold=True, font=HFONT, colour=_col)
        tbox(s, _cx + 0.22, _y0 + 0.98, _cw3 - 0.44, _h - 1.10, _bd, size=10.4, colour=GREY, line=1.12)
    _cy = _y0 + _h + 0.18
    tbox(s, M, _cy, CW, 0.26, "France 5-year swap spread on both bases, weekly since %s" % PCT_YEAR, size=11, bold=True, colour=NAVY, font=HFONT)
    _xe, _ye = weekly("fra_5y_eur6m", SH["pct_start"])
    _xo, _yo = weekly("fra_5y_ois", SH["pct_start"])
    xy_chart(s, M, _cy + 0.28, CW, 1.80, [
        {"name": "versus the 6m Euribor swap (the deck's basis)", "x": _xe, "y": _ye, "colour": NAVY, "width": 1.75},
        {"name": "versus €STR OIS (the financing rate)", "x": _xo, "y": _yo, "colour": SKY, "width": 1.75},
    ], xmin=SH["pct_start"], xmax=str(DATA_DATE), lab=8.5)
    footnote(s, HYPO + " €STR OIS from Bloomberg EESWE, with EONIA less 8.5bp before October 2019, the ECB's recalibration. As of %s. "
                "Source: Bloomberg, Liminality calculations." % longdate(DATA_DATE))


def page_of(name):
    """Page number of a slide in the running order, for cross-references in footnotes."""
    return ORDER.index(name) + 1


def foot_short():
    """The closing line of the spread pages: the sign rule in Charlie's words (2026-10-07) and the source."""
    return FOOT_SIGN + " Source: Bloomberg, Liminality calculations."


# ================================================================ running order
# The deck as cut down by Jeff and added to by Charlie, 10/7/2026 (docs/drafts/deck-jeff-turn-charlie-edits-received-2026-10-07.pptx).
# Pages not in ORDER are kept here as raw material (CUT) and are not built.
ORDER = ["title", "disclaimer", "firm", "exec_summary", "what_is_swap_spread", "dislocation", "why_dislocation",
         "return_sources", "scenario", "stress", "risks", "no_default", "app_return_estr"]
CUT = ["trade",            # "What is the trade?" (the TRS diagram and terms table), taken out by Charlie 2026-10-07
       "not_credit", "france_different", "fiscal", "politics", "ecb_eu", "base_case", "app_calendar", "app_hedge", "app_estr",
       "app_bases"]
if os.environ.get("DECK_ALL"):          # every page, in the old 23-slide order, for comparison builds
    ORDER = keys_all = ["title", "disclaimer", "firm", "exec_summary", "what_is_swap_spread", "dislocation", "why_dislocation", "trade",
                        "return_sources", "not_credit", "france_different", "fiscal", "politics", "no_default", "ecb_eu", "base_case",
                        "scenario", "stress", "risks", "app_calendar", "app_hedge", "app_estr", "app_bases"]
for _k in ORDER:
    globals()["slide_" + _k]()
prs.save(OUT)
print("wrote", os.path.relpath(OUT, os.path.join(HERE, "..")), "with", N[0], "slides")
