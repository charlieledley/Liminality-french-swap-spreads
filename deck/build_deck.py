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
                 bullets, footnote, table, pagenum, logo, theight)

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
# The bond's spread, one number throughout: the model's entry spread on the trade date (-82.9bp). The Bloomberg
# 5y benchmark yield gives -83.1 and the bond's own mid -82.5 the same day; the bond IS the 5y benchmark, so the
# deck does not show two figures for it (Charlie, round 2).
BOND_BP = float(SC["model_inputs"]["Entry spread"])
DATA_DATE = dt.date.fromisoformat(SH["asof_data"])
PCT_YEAR = SH["pct_start"][:4]
NOTE_FILL, NOTE_INK = RGBColor.from_string("FFF4C2"), RGBColor.from_string("7A5A00")
VIOLET = RGBColor.from_string("6A4C93")
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
    """'; the low was -91bp (16 November 2011)' unless the low is today's observation."""
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
    return d.strftime("%#d %B %Y") if os.name == "nt" else d.strftime("%-d %B %Y")


def serial(d):
    """Excel serial day number, so an XY chart gets a true date axis."""
    d = dt.date.fromisoformat(d) if isinstance(d, str) else d
    return (d - dt.date(1899, 12, 30)).days


prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
N = [0]


def sl(dark=False):
    s = blank(prs)
    bg(s, INK if dark else WHITE)
    N[0] += 1
    if N[0] > 1:
        logo(s, W - M - 1.26, H - 0.56, 1.26, dark_bg=dark)
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
                                Inches(x), Inches(y), Inches(w), Inches(h), cd)
    c = gf.chart
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
    gf = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd)
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
    a = slide.shapes.add_shape(MSO_SHAPE.LEFT_ARROW if left else MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(w), Inches(h))
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


FOOT_CONSTRUCTION = ("Spreads are the swap rate less the bond yield, so a cheap OAT reads negative: versus the 6m Euribor swap "
                     "(Bloomberg EUSA), France and Italy yields are Bloomberg generic benchmark bonds at each tenor; the financing "
                     "leg of the trade is €STR, which sat %s below the 1y Euribor swap and %s below the 5y on %s. "
                     "Source: Bloomberg, Liminality calculations."
                     % (bp(BASIS["1y"]["current"]), bp(BASIS["5y"]["current"]), longdate(DATA_DATE)))

# ================================================================ 1. title
s = sl(dark=True)
logo(s, M, 1.30, 3.85, dark_bg=True)
tbox(s, M, 2.72, CW, 0.92, "French swap spreads", size=52, bold=True, colour=WHITE, font=HFONT)
tbox(s, M, 3.70, 11.0, 0.5, "A four-year option on the OAT swap spread, with non-recourse financing",
     size=21, colour=ICE)
card(s, M, 4.54, 4.3, 0.062, fill=GOLD)
tbox(s, M, 4.88, 10.5, 0.4, "October 2026", size=14, colour=LGREY)
tbox(s, M, H - 1.02, CW, 0.62,
     [("Confidential and proprietary — for discussion only.", {"bold": True, "size": 11}),
      ("This presentation contains confidential information and is intended solely for the use of the named "
       "recipient(s). Returns shown are scenario illustrations, gross of fees. Please read the important information.",
       {"size": 11})], colour=LGREY, line=1.16)

# ================================================================ 2. important information
# Charlie's own language (put-writing deck, 24 September 2026), reproduced verbatim.
s = sl()
title(s, "Important information", "Confidential — for the use of the recipient only")
DISC = (
    "The contents of this document are confidential and proprietary, are furnished exclusively "
    "for the use of the person to whom it is provided, and may not be copied, disclosed, "
    "distributed or used in any way by the person to whom it was provided or by any other party "
    "without the express prior written permission of Liminality Capital. The information "
    "contained herein should only be read in conjunction with, and is subject in all respects "
    "to, the notes set forth throughout this document in the footers. Nothing herein "
    "constitutes or should be construed as an offering of securities or a recommendation to "
    "purchase or sell securities or commodity interests. If an offer of securities were to be "
    "made in the future, it must be made only through, and subject to the disclosures in, a "
    "confidential private placement memorandum (“PPM”) and related subscription "
    "documents. Potential investors must meet the eligibility requirements set forth in the "
    "PPM. The information contained herein is for informational and discussion purposes only, "
    "reflects the opinions of the author and no other person, and to the extent factual is "
    "accurate only as the date hereof. Liminality Capital does not undertake to update any "
    "information that subsequently becomes inaccurate. Past performance is no guarantee of "
    "future results.")
tbox(s, M, 1.66, CW, theight(DISC, CW, 13.0, BFONT, False, False, 1.34), DISC,
     size=13.0, colour=GREY, line=1.34, space_after=0)

# ================================================================ 3. the firm
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

# ================================================================ 4. executive summary
s = sl()
title(s, "Executive summary: the French opportunity",
      "A %.1f-year option on the spread between a French government bond and the euro swap curve"
      % INP["Yrs Time to Expiry"])
S3, S4, BE = NAMED["S3"], NAMED["S4"], NAMED["BE"]
_items = [
    ("Buy a %.0f-year-expiry option on a %.0f-year France versus Euribor swap spread." % (round(INP["Yrs Time to Expiry"]), round(INP["Starting Bond Expiry"])), {"bold": True}),
    # Charlie's wording, 2026-10-05 (round-1 edit); the figure and the rarity clause are computed
    "French government bonds (“OATs”) have dislocated against swaps in recent weeks as the market has grown "
    "nervous about slipping French public finances amid increasing political uncertainty around budget negotiations. "
    "Spring presidential elections loom, with an increased probability of a populist government on the left or right.",
    # the closing sentence of the bullet above, moved to its own bullet (Charlie, 2026-10-05)
    "5-year OATs now yield %s more than swaps, %s." % (bp(-BOND_BP), rarity_5y()),
    # Charlie's wording, 2026-10-05 (round-1 edit); the three terms are computed from the model inputs
    "The attractiveness of the opportunity is heavily dependent on a proprietary financing structure: our position is "
    "financed for %.1f years – within a year of maturity – with non-recourse leverage at €STR + %dbp, and a floor "
    "only %dbp out of the money." % (INP["Yrs Time to Expiry"], INP["Funding E+ (bps)"], -INP["Floor strike (from ATMF)"]),
    # Charlie's wording, 2026-10-05 (round-2 edit); figures computed. The Spain clause is his and is not yet
    # checked against data (no Spanish series in the repo); see the internal note.
    "Over the life of the option the bond rolls from the %.1f-year point of the curve to the 1-year point, where a "
    "“pull to par” dynamic generally keeps spreads well anchored – in the case of France even through the euro "
    "sovereign crisis. If nothing changes, the roll alone returns %s a year (%.1fx). To break even, the 1-year spread at "
    "expiry just needs to be at %s or higher, a level even Spain never breached, and Italy breached only briefly, in "
    "November 2011." % (INP["Starting Bond Expiry"], pc(S3["irr"] * 100, 0), S3["moic"], bp(BE["spread_bp"])),
]
bullets(s, M, 1.62, 7.55, _items, size=13.2, gap=9, line=1.12)
_x, _w = 8.55, 4.16
stat(s, _x, 1.62, _w, bp(BOND_BP), "%.1f-year OAT swap spread, %s; %s"
     % (INP["Starting Bond Expiry"], longdate(DATA_DATE), rarity_5y()), vcolour=NEG, h=1.30)
stat(s, _x, 3.07, _w, "%s | %.1fx" % (pc(S3["irr"] * 100, 0), S3["moic"]),
     "4-year IRR and multiple if the spread curve is unchanged at expiry (roll to spot)", vcolour=POS, h=1.30)
stat(s, _x, 4.52, _w, bp(BE["spread_bp"]), "1-year spread at expiry for break-even; %s for full impairment"
     % bp(NAMED["IMP"]["spread_bp"]), vcolour=NAVY, h=1.30)
BR = SC["breakeven_breaches_1y"]
footnote(s, "Returns gross of fees, from Liminality's scenario model with %sm of capital including the option premium per 100m of "
            "bond notional; see the scenario page for the construction. Spain's 1-year spread (data from %s) reached %s on %s; "
            "Italy's was below %s on %d trading days, %s to %s. %s"
            % ("1.1", longdate(BR["esp"]["first"]), bp(BR["esp"]["min"]), longdate(BR["esp"]["min_date"]), bp(BE["spread_bp"]),
               BR["ita"]["days_below_breakeven"], longdate(BR["ita"]["span"][0]), longdate(BR["ita"]["span"][1]), FOOT_CONSTRUCTION))

# ================================================================ 5. what is a swap spread
# Modelled on slide 19 of the US deck (Charlie, round-1 edit): definition on the left, the curves on the right.
# Only the 1y and 5y points are on hand for France, so the chart shows those two tenors until the full OAT and
# 6m Euribor swap curves are pulled.
LV = SH["levels_pct"]
s = sl()
title(s, "What is a swap spread?", "The gap between a government bond yield and the swap rate of the same maturity")
bullets(s, M, 1.62, 5.60, [
    ("A swap spread is the difference between the yield on a government bond, here a French OAT, and the fixed "
     "rate on an interest rate swap of the same maturity.", {}),
    ("To be “long” the swap spread, buy the OAT and pay fixed on the swap, fully hedging the duration.", {}),
    ("In this deck the spread is the swap rate less the bond yield, so a bond that is cheap to swaps reads as a "
     "negative number.", {}),
], size=12.8, gap=9, line=1.12)
# the two-panel curve picture of the US deck's slide 19, for France: yields above, spread beneath
CV = json.load(open(os.path.join(DATA, "curve_2026-10-02.json"), encoding="utf-8"))
tbox(s, 6.60, 1.50, 6.11, 0.30, "French yield curves, %s" % longdate(CV["asof"]), size=11, bold=True, colour=NAVY, font=HFONT)
xy_chart(s, 6.60, 1.78, 6.11, 2.55, [
    {"name": "OAT yield", "x": CV["years"], "y": CV["oat_yield_pct"], "colour": NAVY, "width": 2.0},
    {"name": "6m Euribor swap rate", "x": CV["years"], "y": CV["swap_rate_pct"], "colour": GOLD, "width": 2.0},
], yfmt='0.0"%"', xfmt='0"y"', xunit=5, xmin=0, xmax=30, markers=True, lab=9,
    ymin=0.5 * int(min(CV["swap_rate_pct"]) * 2), ymax=0.5 * (int(max(CV["oat_yield_pct"]) * 2) + 1))
tbox(s, 6.60, 4.36, 6.11, 0.26, "Swap spread at each point of the curve (swap less OAT)", size=11, bold=True, colour=NAVY, font=HFONT)
xy_chart(s, 6.60, 4.70, 6.11, 1.80, [
    {"name": "Swap spread", "x": CV["years"], "y": CV["spread_bp"], "colour": NEG, "width": 2.0},
], yfmt='0"bp"', xfmt='0"y"', xunit=5, xmin=0, xmax=30, markers=True, legend=False, lab=9)
footnote(s, "Bloomberg I14 France sovereign curve and S45 EUR swap curve versus 6m Euribor, mid, as of %s; the 5-year sovereign "
            "point is the FRTR 3¼ 02/25/2032 yield. Spread is the swap rate less the bond yield. Source: Bloomberg, Liminality "
            "calculations." % longdate(CV["asof"]))

# ================================================================ 6. the dislocation
s = sl()
title(s, "The current dislocation",
      "France swap spreads versus the 6m Euribor swap, weekly, since %s" % PCT_YEAR)
_x1, _y1 = weekly("fra_1y_%s" % B, SH["pct_start"])
_x5, _y5 = weekly("fra_5y_%s" % B, SH["pct_start"])
xy_chart(s, M, 1.55, 8.30, 4.95, [
    {"name": "5-year", "x": _x5, "y": _y5, "colour": NAVY, "width": 2.0},
    {"name": "1-year", "x": _x1, "y": _y1, "colour": GOLD, "width": 2.0},
], xmin=SH["pct_start"], xmax=str(DATA_DATE))
_x, _w = 9.25, 3.46
stat(s, _x, 1.55, _w, bp(BOND_BP), "5-year today, %s%s. The OAT in the trade, FRTR 3¼ 02/25/2032, is the 5-year benchmark"
     % (rarer(CUR[f"fra_5y_pct_since_{PCT_YEAR}"]), low_clause(L5)), vcolour=NEG, h=1.50)
stat(s, _x, 3.20, _w, bp(CUR["fra_1y"]), "1-year today, %s; it has never closed below %s"
     % (rarer(CUR[f"fra_1y_pct_since_{PCT_YEAR}"]), bp(L1["min"])), vcolour=NAVY, h=1.50)
stat(s, _x, 4.85, _w, bp(CUR["fra_1y"] - BOND_BP), "gap between the 1-year and 5-year points today: the roll-down available if the "
     "curve does not move", vcolour=POS, h=1.50)
footnote(s, FOOT_CONSTRUCTION)

# ================================================================ 7. why the dislocation
s = sl()
title(s, "Why is there a dislocation?")
_cw = (CW - 0.40) / 2
card(s, M, 1.62, _cw, 3.80, fill=ICE_BG)
card(s, M + _cw + 0.40, 1.62, _cw, 3.80, fill=WHITE, line=RULE)
tbox(s, M + 0.28, 1.84, _cw - 0.56, 0.40, "Long-term factors", size=17, bold=True, font=HFONT)
tbox(s, M + _cw + 0.68, 1.84, _cw - 0.56, 0.40, "Short-term factors", size=17, bold=True, font=HFONT)
# placeholders in Charlie's brackets: the first two in each column from the 2026-10-04 draft, the rest added 2026-10-05
bullets(s, M + 0.28, 2.42, _cw - 0.56, ["[Budget, fiscal]", "[Political dysfunction, lack of will to fix the situation]",
        "[Negative feedback loop, with rising yields pushing the budget deficit further]"],
        size=13.5, gap=10, line=1.12)
bullets(s, M + _cw + 0.68, 2.42, _cw - 0.56, ["[Levered unwinds]",
        "[Rates globally moving higher, higher volatility in rates complex with global tightening cycle back in early innings]",
        "[Polls showing popularity of far-left and far-right parties; upcoming presidential election]",
        "[Left-wing leader floats the idea of cancelling French debt held by the central bank]"],
        size=13.5, gap=10, line=1.12)
internal_note(s, M, 5.62, CW, "Bullets are Charlie's placeholders from the 2026-10-04 draft, in his brackets. The US deck's version of "
                              "this page (QT, dealer balance sheets, Treasury supply; year-end dealer inventories, Q1 crowding, "
                              "Liberation Day unwind) is the model for the final wording.", size=10)

# ================================================================ 8. what is the trade: the TRS, as on slide 24 of the US deck
BOND = INP["Bond Underlier"].replace("3 1/4", "3¼")
s = sl()
title(s, "What is the trade?", "Long the OAT, pay fixed on the swap, financed through a total return swap with a floor")
# Bank top-left, Liminality top-right, the underlying bottom-left, as the US page lays it out
_bx, _by, _bw, _bh = 1.40, 1.75, 3.00, 1.15
_lx = 8.95
box(s, _bx, _by, _bw, _bh, "Bank", "total return payer")
box(s, _lx, _by, _bw, _bh, "Liminality", "total return receiver", fill=ICE_BG, ink=NAVY, sub_ink=GREY)
box(s, _bx, 4.05, _bw, _bh, "Underlying asset", "%s and a matched 6m Euribor swap, pay fixed" % BOND, fill=WHITE, ink=NAVY, sub_ink=GREY, hsize=13)
_ln = s.shapes.add_connector(1, Inches(_bx + _bw / 2), Inches(_by + _bh), Inches(_bx + _bw / 2), Inches(4.05))
_ln.line.color.rgb = GREY; _ln.line.width = Pt(1.5)
tbox(s, _bx + _bw / 2 + 0.12, 3.20, 2.4, 0.5, "underlying cash flows", size=10.5, colour=GREY)
_ax, _aw = _bx + _bw + 0.20, _lx - (_bx + _bw) - 0.40
arrow(s, _ax, 1.95, _aw, 0.34, POS)
tbox(s, _ax, 1.50, _aw, 0.40, "total return on the package: carry plus price change", size=11, bold=True, colour=POS, align=PP_ALIGN.CENTER)
arrow(s, _ax, 2.48, _aw, 0.34, GOLD, left=True)
tbox(s, _ax, 2.86, _aw, 0.40, "€STR + %dbp, %.1f years of funding locked in" % (INP["Funding E+ (bps)"], INP["Yrs Time to Expiry"]),
     size=11, bold=True, colour=GOLD, align=PP_ALIGN.CENTER)
note(s, 5.30, 4.05, 6.65, "Unique feature: limited downside",
     "Liminality buys an option struck %dbp out of the money. The most that can be lost is the capital posted, %sm per 100m "
     "of bond notional including the option premium, and there is no margin call or refinancing before %s."
     % (-INP["Floor strike (from ATMF)"], "1.1", longdate(INP["Opt Expiry"])), size=11.5, line_=RULE, fill=WHITE)
_terms = [["Bond", "Swap", "Financing", "Option expiry", "Floor", "Capital"],
          [BOND, "6m Euribor, pay fixed, matched maturity", "TRS at €STR + %dbp" % INP["Funding E+ (bps)"],
           "%s (%.1f years)" % (longdate(INP["Opt Expiry"]), INP["Yrs Time to Expiry"]),
           "%dbp below the forward spread" % -INP["Floor strike (from ATMF)"], "%sm per 100m notional" % "1.1"]]
table(s, M, 5.62, CW, _terms, size=10.0, rowh=0.42, headh=0.32, aligns=[PP_ALIGN.LEFT] * 6, neutral=(1,))
footnote(s, "Terms as modelled on %s; entry spread %s versus the 6m Euribor swap, swap minus bond. Final terms are subject to "
            "documentation with the counterparty." % (longdate(INP["Trade Date"]), bp(INP["Entry spread"], dp=1)))

# ================================================================ 9. the arithmetic: carry and roll-down
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
     "curve does not move, the spread tightens by that difference as the bond rolls, taken as a price gain."
     % (INP["Starting Bond Expiry"], bp(BOND_BP), bp(S3["spread_bp"], dp=1))),
]
for _i, (_hd, _big, _col, _bd) in enumerate(_cards):
    _cx = M + _i * (_cw3 + 0.30)
    card(s, _cx, _y0, _cw3, 3.55, fill=ICE_BG if _i != 1 else WHITE, line=None if _i != 1 else RULE)
    tbox(s, _cx + 0.22, _y0 + 0.20, _cw3 - 0.44, 0.34, _hd, size=14, bold=True, font=HFONT)
    tbox(s, _cx + 0.22, _y0 + 0.62, _cw3 - 0.44, 0.50, _big, size=24, bold=True, font=HFONT, colour=_col)
    tbox(s, _cx + 0.22, _y0 + 1.30, _cw3 - 0.44, 2.10, _bd, size=11.5, colour=GREY, line=1.16)
_cap = 100e6 * 1e-4 / 1.1e6 * 100
note(s, M, 5.42, CW, "On the capital",
     "Everything above is per 100m of bond notional. The capital committed is %sm, so each 1bp a year of net carry is "
     "%.1f%% a year on capital, and the roll-down, realised once at a one-year duration, is worth about %.0f%% of capital per "
     "100bp of tightening. The option premium is the cost that pays for the floor; the IRRs on the scenario page are after it."
     % ("1.1", _cap, 100e6 * 1e-2 / 1.1e6 * 100), size=11.5, line_=RULE, fill=WHITE)   # 100bp x 1y duration = 1% of notional
footnote(s, "Levels on %s: bond yield from Bloomberg; matched-maturity swap implied by the model's entry spread of %s; basis from "
            "the 5-year 6m Euribor swap less the 5-year €STR OIS. Roll-down ignores convexity and any change in the curve. "
            "Source: Bloomberg, Liminality calculations." % (longdate(DATA_DATE), bp(INP["Entry spread"], dp=1)), w=7.20)
internal_note(s, 8.55, 6.38, 4.16, "Charlie, 2026-10-05: make this page more explicable. The Euribor vs €STR legs make it much "
                                   "harder to understand.", size=9.0)

# ================================================================ 10. what a swap spread is, and is not
# Charlie's argument, from his edit of 2026-10-05, set as prose; wording for his review
s = sl()
title(s, "A swap spread is not, in the usual case, a credit spread", "Why the gap exists, and what moves it")
_y = bullets(s, M, 1.62, CW, [
    ("Sovereigns that borrow in a currency they print do not, as a rule, default on that debt. A swap spread on such a "
     "bond is therefore not generally read as a measure of credit risk.", {"size": 14.0}),
    ("We would argue it is instead the product of three things:", {"size": 14.0}),
], gap=12, line=1.14)
_items = [("Plumbing", "An externality of problems in the global financing system that were created by the new regulatory "
                       "regimes introduced after the global financial crisis: balance-sheet and leverage rules that make it "
                       "costly for banks to hold and finance government bonds."),
          ("Financing risk", "Intertwined with that, the risk and cost of financing a leveraged bond position through time, which "
                             "is why the spread gaps when levered holders are forced out."),
          ("Supply", "Made more acute by the growth in government bond issuance since the crisis, which has to be absorbed by "
                     "balance sheets that are now more constrained.")]
_cw3 = (CW - 0.60) / 3
for _i, (_hd, _bd) in enumerate(_items):
    _cx = M + _i * (_cw3 + 0.30)
    card(s, _cx, _y + 0.10, _cw3, 2.75, fill=ICE_BG if _i % 2 == 0 else WHITE, line=None if _i % 2 == 0 else RULE)
    _n = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(_cx + 0.22), Inches(_y + 0.32), Inches(0.46), Inches(0.46))
    _n.fill.solid(); _n.fill.fore_color.rgb = NAVY; _n.line.fill.background(); _n.shadow.inherit = False
    _tf = _n.text_frame; _tf.margin_left = _tf.margin_right = 0
    _p = _tf.paragraphs[0]; _p.alignment = PP_ALIGN.CENTER
    _r = _p.add_run(); _r.text = "i" * (_i + 1) if _i < 2 else "iii"; _r.font.size, _r.font.bold, _r.font.name = Pt(14), True, HFONT
    _r.font.color.rgb = WHITE
    tbox(s, _cx + 0.82, _y + 0.36, _cw3 - 1.04, 0.36, _hd, size=14, bold=True, font=HFONT)
    tbox(s, _cx + 0.22, _y + 0.98, _cw3 - 0.44, 1.75, _bd, size=11.8, colour=GREY, line=1.16)
internal_note(s, M, _y + 3.05, CW, "Prose drafted from Charlie's message of 2026-10-05 (\"not a function of credit risk ... (i) an externality "
                                   "of plumbing problems ... (ii) financing risk ... (iii) growing government bond issuance\"). The expansions "
                                   "under each heading are Claude's and need his read.", size=9.5)

# ================================================================ 11. France is different
s = sl()
title(s, "France is different: it does not print the currency it borrows in",
      "So a French swap spread can carry sovereign risk in a way a US or UK spread, in practice, does not")
_y = bullets(s, M, 1.62, 7.55, [
    ("The United States and the United Kingdom issue debt in a currency their own central bank creates. France issues in "
     "euros, which the ECB controls on behalf of twenty members.", {"size": 13.5}),
    ("A French swap spread can therefore price some probability of a sovereign credit event, which is exactly what it "
     "did for Italy in 2011 and what the market has started to ask about France.", {"size": 13.5}),
    ("That sets the bar for this investment much higher than for a US swap spread investment. The structure meets it two ways: the "
     "bond rolls to a 1-year maturity by expiry, and the floor caps the loss at the capital posted.", {"size": 13.5}),
    ("The question the scenario page answers is how far the 1-year spread would have to move for the floor to bind: "
     "break-even at %s, full impairment at %s, against an Italian low of %s in November 2011."
     % (bp(NAMED["BE"]["spread_bp"]), bp(NAMED["IMP"]["spread_bp"]), bp(IT["1y"]["min"])), {"size": 13.5}),
], gap=11, line=1.14)
_x, _w = 8.55, 4.16
stat(s, _x, 1.62, _w, bp(NAMED["BE"]["spread_bp"]), "1-year France spread at expiry for break-even", vcolour=NAVY, h=1.22)
stat(s, _x, 2.98, _w, bp(IT["1y"]["min"]), "Italy's 1-year spread at its worst, %s" % longdate(IT["1y"]["min_date"]), vcolour=NEG, h=1.22)
stat(s, _x, 4.34, _w, "%d days" % IT["1y"]["days_below_stress"], "trading days Italy's 1-year spread spent below %s, all in late 2011"
     % bp(IT["1y"]["stress_level_bp"]), vcolour=VIOLET, h=1.22)
footnote(s, FOOT_CONSTRUCTION)
internal_note(s, M, 5.75, 7.55, "Prose drafted from Charlie's message of 2026-10-05 (\"for France, they don't print their own currency, so there "
                                "IS potentially sovereign risk ... this makes the bar MUCH higher\"). Needs his read.", size=9.5)

# ================================================================ 12a. the French fiscal situation (placeholder, Charlie 2026-10-05)
s = sl()
title(s, "The French fiscal situation", "Placeholder: having introduced the credit question, engage it")
bullets(s, M, 1.62, CW, [
    "[Deficit and debt-to-GDP: level, path, and how France compares with Italy, Spain and Germany]",
    "[Interest cost: the share of revenue going to debt service as yields reset, and the feedback loop]",
    "[Debt structure: average maturity, who holds it (domestic, foreign, the ECB), issuance calendar]",
    "[The budget process and the ratings path]",
], size=14.0, gap=12, line=1.14)
internal_note(s, M, 4.45, CW, "Placeholder page requested by Charlie, 2026-10-05: after \"France is different\" introduces credit risk, "
                              "this page engages it with the fiscal facts. Bracketed items are Claude's suggested outline. Data: Eurostat "
                              "government finance statistics, Agence France Trésor for the debt structure.", size=10)

# ================================================================ 12b. French politics (placeholder, moved after the fiscal page, Charlie 2026-10-05)
s = sl()
title(s, "French politics: the parties and the election", "Placeholder")
bullets(s, M, 1.62, CW, [
    "[More explanation of French politics, particularly the parties]",
    "[Parties: polling, positions on the budget and on the debt; the presidential calendar]",
    "[What each plausible outcome would mean for the budget and for the debt]",
], size=14.0, gap=12, line=1.14)
internal_note(s, M, 3.60, CW, "Placeholder page requested by Charlie, 2026-10-05, moved here after the fiscal page so the credit-risk "
                              "section runs: France is different, the fiscal situation, the politics, why no default, the ECB and EU. "
                              "Content, charts and sources to follow: polling and the 2027 calendar.", size=10)

# ================================================================ 11b. why France will not default (placeholder, Charlie 2026-10-05)
s = sl()
title(s, "Why we do not think France will default, or leave the euro",
      "Greece wiped out private creditors. Why is it extremely unlikely that France would end up the same way?")
bullets(s, M, 1.62, CW, [
    "[Why we do not think France will default on its debt]",
    "[Why we do not think France will leave the euro]",
    "[What would have to be true for either, and how the structure behaves on the way there: mark-to-market before expiry, "
    "the floor at expiry, break-even at %s on the 1-year spread]" % bp(NAMED["BE"]["spread_bp"]),
], size=14.0, gap=12, line=1.14)
internal_note(s, M, 3.90, CW, "Placeholder page requested by Charlie, 2026-10-05, placed after \"France is different\" because it answers "
                              "the question that page raises. Content to come: the debt structure (maturity, domestic and ECB holdings), "
                              "the ECB's instruments (TPI, OMT), the political arithmetic of leaving, and the market's own pricing (CDS, "
                              "redenomination risk in the 2017 and 2022 elections).", size=10)

# ================================================================ 11c. the ECB and EU as stabilisers (placeholder, Charlie 2026-10-05)
s = sl()
title(s, "The ECB and the EU as stabilisers of bond prices", "Placeholder: the historic role of the ECB and the EU")
bullets(s, M, 1.62, CW, [
    "[2010 to 2012: SMP purchases, the LTROs, “whatever it takes” and OMT; what each did to spreads]",
    "[2015 onwards: the asset purchase programme and the ECB as the largest holder of French debt]",
    "[2020: PEPP and the EU recovery fund (NGEU), the first large common issuance]",
    "[2022: the Transmission Protection Instrument, announced before it was needed]",
    "[What that history implies for a 1-year French spread at the option's expiry]",
], size=14.0, gap=12, line=1.14)
internal_note(s, M, 4.80, CW, "Placeholder page requested by Charlie, 2026-10-05, after the no-default page. The bracketed items are "
                              "Claude's suggested outline, not Charlie's words. Data to show: the 1-year and 5-year spreads of Italy and "
                              "Spain around each intervention date, which the repo already holds from 2010.", size=10)

# ================================================================ 12. base case: the roll
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
    {"name": "1-year point", "x": _x1, "y": _y1, "colour": GOLD, "width": 2.0},
    {"name": "FRTR 3¼ 02/25/32", "x": _xb, "y": _yb, "colour": NEG, "width": 2.5},
], xmin=_start5, xmax=str(DATA_DATE), major_years=1)
_x, _w = 9.25, 3.46
stat(s, _x, 1.62, _w, bp(BOND_BP), "the bond today, %.1f years to maturity" % INP["Starting Bond Expiry"], vcolour=NEG, h=1.18)
stat(s, _x, 2.95, _w, bp(S3["spread_bp"], dp=1), "the 1-year point today, interpolated to the bond's maturity at expiry", vcolour=GOLD, h=1.18)
stat(s, _x, 4.28, _w, bp(S3["spread_bp"] - BOND_BP, sign=True), "spread tightening from the roll alone if the curve is unchanged, "
     "worth %s a year" % pc(S3["irr"] * 100, 0), vcolour=POS, h=1.18)
_five = ("The 5-year point is at its cheapest since %s today." % PCT_YEAR
         if dt.date.fromisoformat(L5["min_date"]) == DATA_DATE else
         "The 5-year point reached %s in the euro crisis (%s)." % (bp(L5["min"]), longdate(L5["min_date"])))
tbox(s, _x, 5.62, _w, 0.80, "The 1-year point has never closed below %s since %s (%s). %s"
     % (bp(L1["min"]), PCT_YEAR, longdate(L1["min_date"]), _five), size=10.5, colour=GREY, line=1.12)
footnote(s, FOOT_CONSTRUCTION)

# ================================================================ 13. scenario analysis
s = sl()
title(s, "Scenario analysis: %.0f-year IRR and multiple at expiry" % round(INP["Yrs Time to Expiry"]),
      "Returns depend on where the 1-year France swap spread is when the option expires. The history since %s is on the left; "
      "the scenario levels are the dashed lines" % PCT_YEAR)
_x1, _y1 = weekly("fra_1y_%s" % B, SH["pct_start"])
_cols = {"S1": POS, "S2": POS, "S3": GOLD, "S4": NAVY, "S5": VIOLET, "BE": GREY, "S6": NEG, "IMP": NEG}
_order = [n["id"] for n in SC["named"]]              # richest first, as scenario_returns.py sorts them
_series = [{"name": "1-year France spread", "x": _x1, "y": _y1, "colour": NAVY, "width": 1.75}]
# each scenario line carries its MOIC at the right-hand end (Charlie, round 2). The labels are text boxes placed from
# the axis scale with the plot area pinned, and stacked where lines are too close for separate labels (round 3).
_x_end = str(DATA_DATE)
for _id in _order:
    _n = NAMED[_id]
    _series.append(flat(_id, _n["spread_bp"], _cols[_id], SH["pct_start"], _x_end, width=1.5))
_cx, _cy, _cw, _ch = M, 1.72, 5.90, 4.60
_pl = (0.11, 0.04, 0.72, 0.86)          # inner plot area as fractions of the chart frame
_ymin, _ymax = -650, 150
xy_chart(s, _cx, _cy, _cw, _ch, _series, legend=False, ymin=_ymin, ymax=_ymax, xmin=SH["pct_start"], xmax=_x_end,
         major_years=4, plot_layout=_pl)
_plot_right = _cx + (_pl[0] + _pl[2]) * _cw
_plot_top, _plot_h = _cy + _pl[1] * _ch, _pl[3] * _ch
def _ypos(level):
    return _plot_top + (_ymax - level) / (_ymax - _ymin) * _plot_h
_lab_h, _gap = 0.17, 0.02
_labels = []                             # (id, line y, label y) with collisions pushed down the page
for _id in _order:
    _n = NAMED[_id]
    _ly = _ypos(_n["spread_bp"])
    _ty = _ly - _lab_h / 2
    if _labels and _ty < _labels[-1][2] + _lab_h + _gap:
        _ty = _labels[-1][2] + _lab_h + _gap
    _labels.append((_id, _ly, _ty))
for _id, _ly, _ty in _labels:
    _n = NAMED[_id]
    _txt = "%.1fx" % _n["moic"] if _n["moic"] > 0 else "0x"
    _ln = s.shapes.add_connector(1, Inches(_plot_right), Inches(_ly), Inches(_plot_right + 0.22), Inches(_ty + _lab_h / 2))
    _ln.line.color.rgb = _cols[_id]; _ln.line.width = Pt(0.75)
    tbox(s, _plot_right + 0.26, _ty, 0.70, _lab_h, _txt, size=9, bold=True, colour=_cols[_id], space_after=0, line=1.0)
_rows = [["", "Scenario: 1-year spread at expiry", "Spread", "IRR", "MOIC"]]
_gap1 = NAMED["S3"]["spread_bp"] - L1["min"]
_s3 = "Roll to spot: curve unchanged (%s above the 1-year low since %s)" % (bp(_gap1), PCT_YEAR) if _gap1 > 1.5 \
    else "Roll to spot: curve unchanged (within 1bp of the 1-year low since %s)" % PCT_YEAR
_s4 = ("No roll: the bond's spread unchanged (the 5-year point's cheapest since %s)" % PCT_YEAR
       if CUR["days_5y_below_frtr32"] == 0 else
       "No roll: the bond's spread unchanged (within %s of the 5-year low since %s)" % (bp(abs(L5["min"] - BOND_BP)), PCT_YEAR))
_short = {"S1": "Median since %s" % PCT_YEAR, "S2": "10th percentile since %s" % PCT_YEAR, "S3": _s3, "S4": _s4,
          # the S-numbers on the slide follow the table order, not the ids

          "S5": "Italy's 2011 crisis level: below this for only %d trading days" % IT["1y"]["days_below_stress"],
          "BE": "Investment break-even",
          "S6": "Italy's 1-year point at its euro-crisis low, %s" % dt.date.fromisoformat(IT["1y"]["min_date"]).strftime("%#d %b %Y" if os.name == "nt" else "%-d %b %Y"),
          "IMP": "Full impairment at expiry"}
_k = 0
for _id in _order:
    _n = NAMED[_id]
    _k += _id not in ("BE", "IMP")
    _rows.append(["", _short[_id], bp(_n["spread_bp"], dp=1 if _n["spread_bp"] != round(_n["spread_bp"]) else 0),
                  pc(_n["irr"] * 100, 1) if _n["moic"] > 0 else "total loss", "%.2fx" % _n["moic"] if _n["moic"] > 0 else "0"])
_tx, _tw = 6.80, 5.91
_rowh, _headh = 0.40, 0.36
_bot = table(s, _tx, 1.72, _tw, _rows, colw=[0.32, 3.49, 0.72, 0.70, 0.68], size=10.0, rowh=_rowh, headh=_headh,
             neutral=range(1, len(_rows)), aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT])
for _i, _id in enumerate(_order):
    _cy = 1.72 + _headh + _rowh * _i + (_rowh - 0.14) / 2
    _d = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(_tx + 0.09), Inches(_cy), Inches(0.14), Inches(0.14))
    _d.fill.solid(); _d.fill.fore_color.rgb = _cols[_id]; _d.line.fill.background(); _d.shadow.inherit = False
tbox(s, _tx, _bot + 0.14, _tw, 0.90,
     "Model: trade date %s, option expiry %s (%.1f years), financing €STR + %dbp, floor %dbp below the forward spread, "
     "%sm of capital including the option premium per 100m of bond notional, gross of fees. Entry spread %s. IRR and MOIC are "
     "one horizon apart. Spread percentiles are daily since %s."
     % (longdate(INP["Trade Date"]), longdate(INP["Opt Expiry"]), INP["Yrs Time to Expiry"], INP["Funding E+ (bps)"],
        -INP["Floor strike (from ATMF)"], "1.1", bp(INP["Entry spread"], dp=1), PCT_YEAR),
     size=9.5, colour=GREY, line=1.12)
footnote(s, FOOT_CONSTRUCTION, w=5.90)
internal_note(s, 7.10, _bot + 1.10, 4.20, "Returns at %s and %s are interpolated between the spreadsheet's grid points. The axis runs "
              "to %s so the loss levels show, as in the draft." % (bp(NAMED["S3"]["spread_bp"], dp=1), bp(NAMED["S5"]["spread_bp"]), bp(-650)), size=9.0)

# ================================================================ 14. the stress analogue
s = sl()
title(s, "The stress analogue: Italy and Spain in the euro crisis",
      "1-year swap spreads versus 6m Euribor, weekly, 2010 to 2013: the point the bond rolls to")
# 1-year only (Charlie, round 2: the four-line version was too noisy). The 5-year lines are in the data if wanted.
_xa, _ya = weekly("ita_1y_%s" % B, "2010-01-01", "2013-12-31")
_xs, _ys = weekly("esp_1y_%s" % B, "2010-01-01", "2013-12-31")
_xf, _yf = weekly("fra_1y_%s" % B, "2010-01-01", "2013-12-31")
xy_chart(s, M, 1.55, 8.30, 4.95, [
    {"name": "Italy", "x": _xa, "y": _ya, "colour": NEG, "width": 2.25},
    {"name": "Spain", "x": _xs, "y": _ys, "colour": RGBColor.from_string("2A9D8F"), "width": 2.0},
    {"name": "France", "x": _xf, "y": _yf, "colour": NAVY, "width": 2.0},
    flat("Break-even", NAMED["BE"]["spread_bp"], GREY, "2010-01-01", "2013-12-31", width=1.5,
         label="break-even %s" % bp(NAMED["BE"]["spread_bp"])),
], xmin="2010-01-01", xmax="2014-06-30", major_years=1)
_x, _w = 9.25, 3.46
stat(s, _x, 1.55, _w, bp(IT["1y"]["min"]), "Italy's 1-year spread at its worst, %s" % longdate(IT["1y"]["min_date"]), vcolour=NEG, h=1.50)
_sp = IT["1y"]["days_below_stress_span"]
stat(s, _x, 3.20, _w, "%d days" % IT["1y"]["days_below_stress"], "trading days Italy's 1-year spread spent below %s, %s to %s; never since"
     % (bp(IT["1y"]["stress_level_bp"]), longdate(_sp[0]), longdate(_sp[1])), vcolour=VIOLET, h=1.50)
FC = E["france_crisis"]["1y"]
stat(s, _x, 4.85, _w, bp(FC["min"]), "the lowest France's 1-year spread reached in 2010 to 2013 (%s): it never went negative"
     % longdate(FC["min_date"]) if FC["min"] >= 0 else
     "France's 1-year spread at its worst in the euro crisis, %s" % longdate(FC["min_date"]), vcolour=NAVY, h=1.50)
SP = E["spain"]["1y"]
footnote(s, "The 1-year point is the relevant comparison for a bond that has rolled to one year: break-even needs it below %s at expiry. "
            "Spain's 1-year series starts %s and bottomed at %s on %s. %s"
            % (bp(NAMED["BE"]["spread_bp"]), longdate(SP["first"]), bp(SP["min"]), longdate(SP["min_date"]), FOOT_CONSTRUCTION))

# ================================================================ 15. risks
s = sl()
title(s, "Risks")
_y = bullets(s, M, 1.62, CW, [
    ("French swap spreads could continue to gap lower, and we could have mark-to-market losses from here. But for "
     "permanent impairment at expiry, it would likely require [x]", {"size": 14.0}),
    ("[Far left wins in April presidential election, Mélenchon looks to “cancel” the debt]", {"size": 14.0}),
    ("[France leaves the EU]", {"size": 14.0}),
], gap=12, line=1.14)
note(s, M, _y + 0.30, CW, "What the structure does and does not protect against",
     "The floor caps the loss at the capital posted and removes refinancing risk until %s. It does not protect against "
     "the spread being below %s at expiry, which is where break-even sits; full impairment is at %s. Mark-to-market "
     "losses before expiry are possible without any loss at expiry."
     % (longdate(INP["Opt Expiry"]), bp(NAMED["BE"]["spread_bp"]), bp(NAMED["IMP"]["spread_bp"])), size=12.0, line_=RULE, fill=WHITE)
internal_note(s, M, 5.60, CW, "Bullets are Charlie's from the 2026-10-04 draft, brackets included. The callout below them is new and "
                              "states the structure's limit in the body of the slide rather than a footnote.", size=10)

# ================================================================ 17. hedges: the low-coupon / high-coupon pair (Charlie, 2026-10-05)
HP = json.load(open(os.path.join(DATA, "hedge_pair_2026-10-02.json"), encoding="utf-8"))
HL, HH = HP["low"], HP["high"]
HSCREEN = os.path.join(HERE, "..", "analysis", "data", "raw", "hedge_pair_frtr_0.5_2040_vs_4.5_2041_bbg_screen_2026-10-02.png")
s = sl()
title(s, "Hedges: a low-coupon / high-coupon OAT pair",
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
     "Sized DV01-neutral: %.2f face of the low coupon bought per 100 of the high coupon sold, so the pair has no duration. "
     "If the market moves to pricing a %d%% recovery and both bonds converge to %d, the pair earns %+.0f points per 100 sold "
     "(%+.0f on the long leg, %+.0f on the short). It costs %.1f points a year of net carry at today's yields. The payoff "
     "is positive at any common price down to %d."
     % (DN["face_low_per_100_high"] * 100, DN["recovery"], DN["recovery"], DN["at_recovery"]["net"], DN["at_recovery"]["long_leg"],
        DN["at_recovery"]["short_leg"], -DN["net_carry_per_year"], DN["convergence"][-1]["common_price"]),
     size=10.0, colour=GREY, line=1.12)
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
footnote(s, "Prices and yields as of %s; history daily from Bloomberg (YLD_YTM_MID, PX_LAST). Durations and the clean-price check computed "
            "from the quoted yields with annual coupons and ACT/ACT (computed clean prices %.3f and %.3f). Convergence payoffs ignore carry; "
            "sizing is DV01-neutral on today's durations. Source: Bloomberg, Liminality calculations."
            % (longdate(HP["asof"]), HL["computed_clean"], HH["computed_clean"]), w=7.30)

# ================================================================ 16. appendix: election odds
s = sl()
title(s, "Appendix: presidential election odds", "Polymarket, next French presidential election, as captured in the 2026-10-04 draft")
if os.path.exists(POLYMARKET):
    s.shapes.add_picture(POLYMARKET, Inches(M), Inches(1.60), Inches(7.60))
bullets(s, 8.55, 1.70, 4.16, ["Le Pen is expected to win. Mélenchon is about 13% currently.",
                              "[French presidential calendar to follow]"], size=13.2, gap=10, line=1.12)
footnote(s, "Source: Polymarket.com, screenshot as of the draft of 4 October 2026. Third-party chart, not Liminality data.")
internal_note(s, 8.55, 3.40, 4.16, "The election calendar page (draft slide 11, '[insert]') is still to be supplied. The Polymarket "
                                   "picture is the draft's; a fresh capture is needed before circulation.", size=10)

# ================================================================ appendix: ESTR vs Euribor (moved from the body, Charlie 2026-10-05)
s = sl()
title(s, "Appendix: €STR and Euribor, the two floating rates in the trade",
      "6m Euribor swap rate less €STR OIS rate, 1-year and 5-year, weekly since 2007")
_xb1, _yb1 = weekly("basis_1y", "2007-01-01")
_xb5, _yb5 = weekly("basis_5y", "2007-01-01")
xy_chart(s, M, 1.55, 7.60, 4.30, [
    {"name": "1-year", "x": _xb1, "y": _yb1, "colour": GOLD, "width": 1.75},
    {"name": "5-year", "x": _xb5, "y": _yb5, "colour": NAVY, "width": 2.0},
], xmin="2007-01-01", xmax=str(DATA_DATE), ymin=0)
_x, _w = 8.55, 4.16
note(s, _x, 1.55, _w, "€STR",
     "The euro short-term rate: the overnight rate at which euro-area banks borrow unsecured, published by the ECB since "
     "October 2019 as the successor to EONIA. The euro counterpart of SOFR as the near risk-free benchmark, and the rate "
     "our financing is set over.", size=10.8, line_=RULE, fill=WHITE)
note(s, _x, 3.22, _w, "6m Euribor",
     "The rate at which euro-area banks lend to each other unsecured for six months. It carries a term and bank-credit "
     "premium over €STR, so it sits above it, by more in a funding stress. It is the floating leg of the standard euro "
     "swap, and so of ours.", size=10.8, line_=RULE, fill=WHITE)
note(s, _x, 4.89, _w, "Why it helps the trade",
     "We receive 6m Euribor on the swap and pay €STR + %dbp on the financing, so we are long the basis. It averaged %s at "
     "1 year in 2008 to 2012 and is %s today." % (INP["Funding E+ (bps)"], bp(BASIS["1y"]["mean_2008_2012"]), bp(BASIS["1y"]["current"])),
     size=10.8, fill=ICE_BG)
tbox(s, M, 5.95, 7.60, 0.70, "The spread history in this deck is measured against the 6m Euribor swap, the curve the trade pays fixed on. "
     "Measured against €STR every spread would sit lower by the basis shown here; the appendix shows both.", size=10.5, colour=GREY, line=1.14)
footnote(s, "Source: Bloomberg EUSA (6m Euribor swaps) and EESWE (€STR OIS; EONIA less 8.5bp before October 2019, the ECB's recalibration). "
            "Liminality calculations.")

# ================================================================ 18. appendix: both bases
s = sl()
title(s, "Appendix: the swap curve the spread is measured against",
      "France 5-year swap spread versus the 6m Euribor swap and versus €STR OIS, weekly since 2007")
_xe, _ye = weekly("fra_5y_eur6m", "2007-01-01")
_xo, _yo = weekly("fra_5y_ois", "2007-01-01")
xy_chart(s, M, 1.55, 8.30, 4.95, [
    {"name": "vs 6m Euribor swap (used in this deck)", "x": _xe, "y": _ye, "colour": NAVY, "width": 2.0},
    {"name": "vs €STR OIS (the financing leg)", "x": _xo, "y": _yo, "colour": GOLD, "width": 1.75},
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

prs.save(OUT)
print("wrote", os.path.relpath(OUT, os.path.join(HERE, "..")), "with", N[0], "slides")
