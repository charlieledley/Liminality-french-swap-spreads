# -*- coding: utf-8 -*-
"""French swap spreads investor deck, first build (2026-10-05).

Running order follows docs/deck-plan-2026-10-04.md. Every figure on a slide is read from
deck/data/*.json, written by analysis/spread_history.py and analysis/scenario_returns.py;
nothing numeric is typed here. Text that Charlie left in brackets in his draft of 2026-10-04 is
carried as he wrote it and flagged with an internal note.

Conventions on every slide that shows a spread: 1y and 5y France swap spreads versus the 6m
Euribor swap, swap minus bond, so a cheap OAT reads negative (decisions 0002, 0003); Citi
constant-maturity yields from 2011-09-22, Bloomberg generic benchmarks before (0004);
percentiles since 2010-01-01 (0005). IRR and MOIC are Charlie's, gross of fees.

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
from pptx.enum.text import PP_ALIGN
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
OUT = os.path.join(HERE, "..", "exports", f"Liminality_French_Swap_Spreads_{ASOF}.pptx")
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
    """'lower than 99.8% of days since 2010' reads better than '0.2th percentile'."""
    return "lower than %s%% of days since %s" % (("%.1f" % (100 - pct)).rstrip("0").rstrip("."), since or PCT_YEAR)


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
             xmin=None, xmax=None, lab=9.5, major_years=2):
    """Lines against a date axis. series: list of dicts name, x (dates), y, colour, width, dash."""
    cd = XyChartData()
    for sr in series:
        ser = cd.add_series(sr["name"])
        for a, b in zip(sr["x"], sr["y"]):
            if b is not None:
                ser.add_data_point(serial(a) if isinstance(a, str) else a, b)
    gf = slide.shapes.add_chart(XL_CHART_TYPE.XY_SCATTER_LINES_NO_MARKERS, Inches(x), Inches(y),
                                Inches(w), Inches(h), cd)
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
    va, ca = c.value_axis, c.category_axis
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = RULE
    va.major_gridlines.format.line.width = Pt(0.6)
    va.format.line.fill.background()
    ca.has_major_gridlines = False
    ca.format.line.color.rgb = RULE
    for ax, fmt in ((va, yfmt), (ca, "yyyy")):
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
        ca.minimum_scale = serial(xmin)
    if xmax is not None:
        ca.maximum_scale = serial(xmax)
    # 366 for yearly ticks: 365 drifts a day a year and labels a leap year twice ("2012 2012")
    ca.major_unit = 366 if major_years == 1 else int(365.25 * major_years)
    return c


def weekly(col, start=None, end=None):
    xs, ys = [], []
    for d, v in zip(WK["date"], WK[col]):
        if (start and d < start) or (end and d > end):
            continue
        xs.append(d)
        ys.append(v)
    return xs, ys


def flat(name, level, colour, start, end, width=1.25):
    return {"name": name, "x": [start, end], "y": [level, level], "colour": colour, "width": width, "dash": True}


FOOT_CONSTRUCTION = ("Spreads are the swap rate less the bond yield, so a cheap OAT reads negative: versus the 6m Euribor swap "
                     "(Bloomberg EUSA), France and Italy yields from Citi constant-maturity series from September 2011 and "
                     "Bloomberg generic benchmarks before; the financing leg of the trade is €STR, which sat %s below the 1y "
                     "Euribor swap and %s below the 5y on %s. Source: Bloomberg, Citi, Liminality calculations."
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
    "French government bonds (“OATs”) have dislocated against European swaps in recent weeks as the market has "
    "grown nervous about French public finances, the budget negotiations and the presidential election in the "
    "spring. The 5-year OAT now yields %s more than the swap, the cheapest since %s, and the bond in the trade "
    "sits at %s." % (bp(-CUR["fra_5y"]), PCT_YEAR, bp(CUR["frtr32"])),
    "The entry point is attractive against history, and more so in recent days as levered investors were stopped "
    "out of positions.",
    "The exposure normally needs heavy leverage and continual refinancing. Here it is financed for %.1f years, "
    "non-recourse, at €STR + %dbp, with a floor %dbp below the forward spread." % (INP["Yrs Time to Expiry"], INP["Funding E+ (bps)"], -INP["Floor strike (from ATMF)"]),
    "Over the life of the option the bond rolls from the %.1f-year point of the curve to the 1-year point, where "
    "the spread has stayed anchored through fourteen years including the euro crisis. If nothing changes, the roll "
    "alone returns %s a year (%.1fx). If the bond's spread never recovers, %s (%.1fx). Permanent loss of capital "
    "needs the 1-year spread below %s at expiry, a level only Italy reached, for six weeks in late 2011."
    % (INP["Starting Bond Expiry"], pc(S3["irr"] * 100, 0), S3["moic"], pc(S4["irr"] * 100, 0), S4["moic"], bp(BE["spread_bp"])),
]
bullets(s, M, 1.62, 7.55, _items, size=13.2, gap=9, line=1.12)
_x, _w = 8.55, 4.16
stat(s, _x, 1.62, _w, bp(CUR["fra_5y"]), "5-year France swap spread, %s; %s"
     % (longdate(DATA_DATE), rarer(CUR[f"fra_5y_pct_since_{PCT_YEAR}"])), vcolour=NEG, h=1.30)
stat(s, _x, 3.07, _w, "%s | %.1fx" % (pc(S3["irr"] * 100, 0), S3["moic"]),
     "4-year IRR and multiple if the spread curve is unchanged at expiry (roll to spot)", vcolour=POS, h=1.30)
stat(s, _x, 4.52, _w, bp(BE["spread_bp"]), "1-year spread at expiry for break-even; %s for full impairment"
     % bp(NAMED["IMP"]["spread_bp"]), vcolour=NAVY, h=1.30)
footnote(s, "Returns gross of fees, from Liminality's scenario model with %sm of capital including the option premium per 100m of "
            "bond notional; see the scenario page for the construction. %s" % ("1.1", FOOT_CONSTRUCTION))

# ================================================================ 5. what is a swap spread
s = sl()
title(s, "What is a swap spread?", "The gap between a government bond yield and the swap rate of the same maturity")
_y = bullets(s, M, 1.62, 7.55, [
    ("A swap spread is the difference between the yield on a government bond, here a French OAT, and the fixed "
     "rate on an interest rate swap of the same maturity.", {}),
    ("To be “long” the swap spread, buy the OAT and pay fixed on the swap. The duration risk cancels; what is "
     "left is the bond's price relative to the swap curve.", {}),
    ("Throughout this deck the spread is quoted as the swap rate less the bond yield, so a bond that is cheap to "
     "swaps reads as a negative number.", {}),
    ("For most of the last fifteen years euro swaps have traded rich (lower yield) and government bonds cheap "
     "(higher yield), because many participants take duration synthetically through swaps. The size of that gap, "
     "and how far it can move, is the trade.", {}),
], size=13.2, gap=10, line=1.12)
_x, _w = 8.55, 4.16
stat(s, _x, 1.62, _w, bp(CUR["fra_1y"]), "1-year France swap spread, %s" % longdate(DATA_DATE), vcolour=NAVY, h=1.22)
stat(s, _x, 2.98, _w, bp(CUR["fra_5y"]), "5-year France swap spread, %s" % longdate(DATA_DATE), vcolour=NEG, h=1.22)
stat(s, _x, 4.34, _w, bp(L1["p50"]), "Median 1-year spread since %s" % PCT_YEAR, vcolour=GREY, h=1.22)
footnote(s, FOOT_CONSTRUCTION)

# ================================================================ 6. the dislocation
s = sl()
title(s, "The 5-year point has dislocated; the 1-year point has not",
      "France swap spreads versus the 6m Euribor swap, weekly, since %s" % PCT_YEAR)
_x1, _y1 = weekly("fra_1y_%s" % B, SH["pct_start"])
_x5, _y5 = weekly("fra_5y_%s" % B, SH["pct_start"])
xy_chart(s, M, 1.55, 8.30, 4.95, [
    {"name": "5-year", "x": _x5, "y": _y5, "colour": NAVY, "width": 2.0},
    {"name": "1-year", "x": _x1, "y": _y1, "colour": GOLD, "width": 2.0},
], xmin=SH["pct_start"], xmax=str(DATA_DATE))
_x, _w = 9.25, 3.46
stat(s, _x, 1.55, _w, bp(CUR["fra_5y"]), "5-year today, %s; the low was %s (%s)"
     % (rarer(CUR[f"fra_5y_pct_since_{PCT_YEAR}"]), bp(L5["min"]), longdate(L5["min_date"])), vcolour=NEG, h=1.50)
stat(s, _x, 3.20, _w, bp(CUR["fra_1y"]), "1-year today, %s; it has never closed below %s"
     % (rarer(CUR[f"fra_1y_pct_since_{PCT_YEAR}"]), bp(L1["min"])), vcolour=NAVY, h=1.50)
stat(s, _x, 4.85, _w, bp(CUR["frtr32"]), "FRTR 3¼ 02/25/2032, the bond in the trade, %.1f years to maturity"
     % INP["Starting Bond Expiry"], vcolour=NEG, h=1.50)
footnote(s, FOOT_CONSTRUCTION)

# ================================================================ 7. why the dislocation
s = sl()
title(s, "Why is there a dislocation?")
_cw = (CW - 0.40) / 2
card(s, M, 1.62, _cw, 3.80, fill=ICE_BG)
card(s, M + _cw + 0.40, 1.62, _cw, 3.80, fill=WHITE, line=RULE)
tbox(s, M + 0.28, 1.84, _cw - 0.56, 0.40, "Long-term factors", size=17, bold=True, font=HFONT)
tbox(s, M + _cw + 0.68, 1.84, _cw - 0.56, 0.40, "Short-term factors", size=17, bold=True, font=HFONT)
bullets(s, M + 0.28, 2.42, _cw - 0.56, ["[Budget, fiscal]", "[Political dysfunction, lack of will to fix the situation]"],
        size=13.5, gap=10, line=1.12)
bullets(s, M + _cw + 0.68, 2.42, _cw - 0.56, ["[Levered unwinds]",
        "[Rates globally moving higher, higher volatility in rates complex with global tightening cycle back in early innings]"],
        size=13.5, gap=10, line=1.12)
internal_note(s, M, 5.62, CW, "Bullets are Charlie's placeholders from the 2026-10-04 draft, in his brackets. The US deck's version of "
                              "this page (QT, dealer balance sheets, Treasury supply; year-end dealer inventories, Q1 crowding, "
                              "Liberation Day unwind) is the model for the final wording.", size=10)

# ================================================================ 8. what is the trade
s = sl()
title(s, "What is the trade?", "Long the bond, pay fixed on the swap, financed non-recourse for the life of the option")
_steps = [
    ("Buy the bond", "%s, maturing %s. On %s it yielded %s more than the matching 6m Euribor swap."
     % (INP["Bond Underlier"].replace("3 1/4", "3¼"), longdate(INP["Bond Maturity"]), longdate(INP["Trade Date"]), bp(-INP["Entry spread"]))),
    ("Pay fixed on the swap", "A 6m Euribor interest rate swap of the same maturity, so the package has no duration and "
     "its value moves only with the spread."),
    ("Finance the package", "A total return swap provides the leverage and locks the funding at €STR + %dbp until %s, "
     "the option expiry, %.1f years away." % (INP["Funding E+ (bps)"], longdate(INP["Opt Expiry"]), INP["Yrs Time to Expiry"])),
    ("The floor makes it non-recourse", "An option struck %dbp below the forward spread caps the loss at the capital "
     "committed: %sm per 100m of bond notional, option premium included." % (-INP["Floor strike (from ATMF)"], "1.1")),
]
_y = 1.62
for _i, (_hd, _bd) in enumerate(_steps):
    _iw = 7.55 - 1.10
    _hh = theight(_bd, _iw, T_CARD, BFONT, False, False, 1.14) + 0.72
    card(s, M, _y, 7.55, _hh, fill=ICE_BG if _i % 2 == 0 else WHITE, line=None if _i % 2 == 0 else RULE)
    _n = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(M + 0.20), Inches(_y + (_hh - 0.50) / 2), Inches(0.50), Inches(0.50))
    _n.fill.solid(); _n.fill.fore_color.rgb = NAVY; _n.line.fill.background(); _n.shadow.inherit = False
    _tf = _n.text_frame; _tf.margin_left = _tf.margin_right = 0
    _p = _tf.paragraphs[0]; _p.alignment = PP_ALIGN.CENTER
    _r = _p.add_run(); _r.text = str(_i + 1); _r.font.size, _r.font.bold, _r.font.name = Pt(18), True, HFONT
    _r.font.color.rgb = WHITE
    tbox(s, M + 0.90, _y + 0.16, _iw, 0.30, _hd, size=14.5, bold=True, font=HFONT, space_after=0)
    tbox(s, M + 0.90, _y + 0.52, _iw, _hh - 0.60, _bd, size=T_CARD, colour=GREY, line=1.14, space_after=0)
    _y += _hh + 0.16
# diagram: bank, Liminality, bond
_dx, _dw = 8.55, 4.16
card(s, _dx, 1.62, _dw, 0.95, fill=NAVY)
tbox(s, _dx + 0.15, 1.72, _dw - 0.30, 0.75, [("Bank", {"bold": True, "size": 14, "font": HFONT}),
     ("total return payer; holds the bond and the swap", {"size": 10.5})], colour=WHITE, align=PP_ALIGN.CENTER, space_after=2)
_a1 = s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(_dx + 0.55), Inches(2.67), Inches(0.42), Inches(0.72))
_a2 = s.shapes.add_shape(MSO_SHAPE.UP_ARROW, Inches(_dx + _dw - 0.97), Inches(2.67), Inches(0.42), Inches(0.72))
for _a, _c in ((_a1, POS), (_a2, GOLD)):
    _a.fill.solid(); _a.fill.fore_color.rgb = _c; _a.line.fill.background(); _a.shadow.inherit = False
tbox(s, _dx + 1.05, 2.70, _dw - 2.10, 0.66, [("total return on the spread package", {"colour": POS, "bold": True}),
     ("€STR + %dbp, fixed to expiry" % INP["Funding E+ (bps)"], {"colour": GOLD, "bold": True})],
     size=10.5, align=PP_ALIGN.CENTER, space_after=4)
card(s, _dx, 3.49, _dw, 0.95, fill=ICE_BG)
tbox(s, _dx + 0.15, 3.59, _dw - 0.30, 0.75, [("Liminality", {"bold": True, "size": 14, "font": HFONT}),
     ("total return receiver; posts %sm per 100m" % "1.1", {"size": 10.5, "colour": GREY})], colour=NAVY, align=PP_ALIGN.CENTER, space_after=2)
note(s, _dx, 4.62, _dw, "Limited downside",
     "The embedded floor, struck %dbp below the at-the-money forward spread, means the most that can be lost is the "
     "capital posted. There is no margin call and no refinancing before %s." % (-INP["Floor strike (from ATMF)"], longdate(INP["Opt Expiry"])),
     size=11.0, line_=RULE, fill=WHITE)
footnote(s, "Terms as modelled on %s. Entry spread %s versus the 6m Euribor swap, swap minus bond. Final terms are subject to "
            "documentation with the counterparty." % (longdate(INP["Trade Date"]), bp(INP["Entry spread"])))

# ================================================================ 9. base case: the roll
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
stat(s, _x, 1.62, _w, bp(CUR["frtr32"]), "the bond today, %.1f years to maturity" % INP["Starting Bond Expiry"], vcolour=NEG, h=1.18)
stat(s, _x, 2.95, _w, bp(S3["spread_bp"], dp=1), "the 1-year point today, interpolated to the bond's maturity at expiry", vcolour=GOLD, h=1.18)
stat(s, _x, 4.28, _w, bp(S3["spread_bp"] - CUR["frtr32"], sign=True), "spread tightening from the roll alone if the curve is unchanged, "
     "worth %s a year" % pc(S3["irr"] * 100, 0), vcolour=POS, h=1.18)
tbox(s, _x, 5.62, _w, 0.80, "The 1-year point has never closed below %s since %s (%s). The 5-year point reached %s in the euro "
     "crisis (%s)." % (bp(L1["min"]), PCT_YEAR, longdate(L1["min_date"]), bp(L5["min"]), longdate(L5["min_date"])),
     size=10.5, colour=GREY, line=1.12)
footnote(s, FOOT_CONSTRUCTION)

# ================================================================ 10. scenario analysis
s = sl()
title(s, "Scenario analysis: %.0f-year IRR and multiple at expiry" % round(INP["Yrs Time to Expiry"]),
      "Returns depend on where the 1-year France swap spread is when the option expires. The history since %s is on the left; "
      "the scenario levels are the dashed lines" % PCT_YEAR)
_x1, _y1 = weekly("fra_1y_%s" % B, SH["pct_start"])
_cols = {"S1": POS, "S2": POS, "S3": GOLD, "S4": NAVY, "S5": VIOLET, "BE": GREY, "S6": NEG, "IMP": NEG}
_series = [{"name": "1-year France spread", "x": _x1, "y": _y1, "colour": NAVY, "width": 1.75}]
for _id in ("S1", "S2", "S3", "S4", "S5", "BE", "S6", "IMP"):
    _n = NAMED[_id]
    _series.append(flat(_id, _n["spread_bp"], _cols[_id], SH["pct_start"], str(DATA_DATE)))
xy_chart(s, M, 1.72, 5.90, 4.60, _series, legend=False, ymin=-650, ymax=150, xmin=SH["pct_start"], xmax=str(DATA_DATE), major_years=4)
_rows = [["", "Scenario: 1-year spread at expiry", "Spread", "IRR", "MOIC"]]
_short = {"S1": "Median since %s" % PCT_YEAR, "S2": "10th percentile since %s" % PCT_YEAR,
          "S3": "Roll to spot: curve unchanged (within 1bp of the 1-year low since %s)" % PCT_YEAR,
          "S4": "No roll: the bond's spread unchanged (within 8bp of the 5-year euro-crisis low)",
          "S5": "Italy's 2011 crisis level: below this for only 29 trading days",
          "BE": "Investment break-even", "S6": "Italy's 1-year point at its euro-crisis low, 9 Nov 2011",
          "IMP": "Full impairment at expiry"}
for _id in ("S1", "S2", "S3", "S4", "S5", "BE", "S6", "IMP"):
    _n = NAMED[_id]
    _rows.append([_id if not _id in ("BE", "IMP") else "", _short[_id], bp(_n["spread_bp"], dp=1 if abs(_n["spread_bp"]) < 10 and _n["spread_bp"] != 0 else 0),
                  pc(_n["irr"] * 100, 1), "%.2fx" % _n["moic"] if _n["moic"] > 0 else "0"])
_tx, _tw = 6.80, 5.91
_rowh, _headh = 0.40, 0.36
_bot = table(s, _tx, 1.72, _tw, _rows, colw=[0.32, 3.49, 0.72, 0.70, 0.68], size=10.0, rowh=_rowh, headh=_headh,
             neutral=range(1, len(_rows)), aligns=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT])
for _i, _id in enumerate(("S1", "S2", "S3", "S4", "S5", "BE", "S6", "IMP")):
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

# ================================================================ 11. the stress analogue
s = sl()
title(s, "The stress analogue: Italy in the euro crisis",
      "Italy and France swap spreads versus 6m Euribor, weekly, 2010 to 2013")
_xa, _ya = weekly("ita_1y_%s" % B, "2010-01-01", "2013-12-31")
_xb5, _yb5 = weekly("ita_5y_%s" % B, "2010-01-01", "2013-12-31")
_xf, _yf = weekly("fra_1y_%s" % B, "2010-01-01", "2013-12-31")
_xf5, _yf5 = weekly("fra_5y_%s" % B, "2010-01-01", "2013-12-31")
xy_chart(s, M, 1.55, 8.30, 4.95, [
    {"name": "Italy 1-year", "x": _xa, "y": _ya, "colour": NEG, "width": 2.25},
    {"name": "Italy 5-year", "x": _xb5, "y": _yb5, "colour": VIOLET, "width": 1.75},
    {"name": "France 1-year", "x": _xf, "y": _yf, "colour": GOLD, "width": 1.75},
    {"name": "France 5-year", "x": _xf5, "y": _yf5, "colour": NAVY, "width": 1.75},
    flat("Break-even", NAMED["BE"]["spread_bp"], GREY, "2010-01-01", "2013-12-31"),
], xmin="2010-01-01", xmax="2013-12-31", major_years=1)
_x, _w = 9.25, 3.46
stat(s, _x, 1.55, _w, bp(IT["1y"]["min"]), "Italy's 1-year spread at its worst, %s" % longdate(IT["1y"]["min_date"]), vcolour=NEG, h=1.50)
stat(s, _x, 3.20, _w, "29 days", "trading days Italy's 1-year spread spent below %s, 4 Nov to 14 Dec 2011; never since"
     % bp(NAMED["S5"]["spread_bp"]), vcolour=VIOLET, h=1.50)
stat(s, _x, 4.85, _w, bp(L5["min"]), "France's 5-year spread at its worst, %s; today %s" % (longdate(L5["min_date"]), bp(CUR["fra_5y"])), vcolour=NAVY, h=1.50)
footnote(s, "Italy's 1-year point is the relevant comparison for a bond that has rolled to one year: break-even needs it below %s at expiry. "
            "%s" % (bp(NAMED["BE"]["spread_bp"]), FOOT_CONSTRUCTION))

# ================================================================ 12. risks
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

# ================================================================ 13. appendix: election odds
s = sl()
title(s, "Appendix: presidential election odds", "Polymarket, next French presidential election, as captured in the 2026-10-04 draft")
if os.path.exists(POLYMARKET):
    s.shapes.add_picture(POLYMARKET, Inches(M), Inches(1.60), Inches(7.60))
bullets(s, 8.55, 1.70, 4.16, ["Le Pen is expected to win. Mélenchon is about 13% currently.",
                              "[French presidential calendar to follow]"], size=13.2, gap=10, line=1.12)
footnote(s, "Source: Polymarket.com, screenshot as of the draft of 4 October 2026. Third-party chart, not Liminality data.")
internal_note(s, 8.55, 3.40, 4.16, "The election calendar page (draft slide 11, '[insert]') is still to be supplied. The Polymarket "
                                   "picture is the draft's; a fresh capture is needed before circulation.", size=10)

# ================================================================ 14. appendix: both bases
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
