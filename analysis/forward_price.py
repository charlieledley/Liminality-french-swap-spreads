# -*- coding: utf-8 -*-
"""The forward-price view of the return (Jeff's framing of 2026-10-08, rebuilt from the repo's data).

The structure buys the bond today and finances it at EUR STR + 17bp to the expiry of the floor. The
all-in cost of the bond at expiry is its forward price: today's dirty price compounded at the
financing rate, less the coupons received, compounded the same way. At expiry the bond has one
year left and is worth 103.25 / (1 + y), where y is the 1-year swap rate at that time less the
1-year France swap spread. The gain "just on the bonds" is that price less the forward price.

Conventions (decision 0009):
  - clean price on the trade date from Bloomberg (analysis/data/frtr32_price_yield_bbg_2026-10-07.csv);
    settlement T+1 (2026-10-05, the model's), annual coupons, ACT/ACT, annual compounding;
  - financing at a flat term rate: EUR STR OIS interpolated to the expiry tenor from the 1y and 5y
    Bloomberg EESWE points on the trade date, plus the 17bp funding spread;
  - expiry = the model's 2031-02-25 (the bond's coupon date, one year before maturity);
  - the 1-year swap at expiry is today's 1-year 6m Euribor swap for the spot scenarios (the curve
    assumed unchanged) and the 4.4y1y forward swap, from the par curve, for the forward row;
  - scenario spreads are the model's named points (deck/data/scenario_irr_moic_2026-10-05.json).

Jeff's figures of 2026-10-08 (3.33% repo to 2026-02-20, 1-year swap 3.33%, roll to spot at -3bp) are
kept in the output for the reconciliation on the slide.
"""
import csv
import datetime as dt
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "deck", "data")
ASOF = "2026-10-05"
COUPON = 3.25
MATURITY = dt.date(2032, 2, 25)


def frac(d0, d1):
    """ACT/ACT year fraction between two dates, coupon periods being whole years here."""
    return (d1 - d0).days / 365.0 if (d1 - d0).days < 366 else (d1 - d0).days / 365.25


def coupon_dates(settle, until):
    d = MATURITY
    out = []
    while d > settle:
        if d <= until:
            out.append(d)
        d = dt.date(d.year - 1, d.month, d.day)
    return sorted(out)


def price_one_year(y_pct):
    """Clean price of the bond with exactly one year left: one coupon plus principal."""
    return (100 + COUPON) / (1 + y_pct / 100.0)


def yield_one_year(price):
    return ((100 + COUPON) / price - 1) * 100.0


def build():
    SC = json.load(open(os.path.join(DATA, f"scenario_irr_moic_{ASOF}.json"), encoding="utf-8"))
    SH = json.load(open(os.path.join(DATA, f"spread_history_{ASOF}.json"), encoding="utf-8"))
    CV = json.load(open(os.path.join(DATA, "curve_2026-10-02.json"), encoding="utf-8"))
    inp = SC["model_inputs"]
    trade = dt.date.fromisoformat(inp["Trade Date"])
    settle = dt.date.fromisoformat(inp["SettlementDate"])
    expiry = dt.date.fromisoformat(inp["Opt Expiry"])
    with open(os.path.join(HERE, "data", "frtr32_price_yield_bbg_2026-10-07.csv"), encoding="utf-8") as f:
        px = {r["date"]: r for r in csv.DictReader(f)}[inp["Trade Date"]]
    clean = float(px["frtr32_px_last"])
    ytm = float(px["frtr32_yld_ytm_mid"])
    prev_cpn = dt.date(2026, 2, 25)
    accrued = COUPON * (settle - prev_cpn).days / 365.0
    dirty = clean + accrued
    # financing: EUR STR OIS interpolated to the expiry tenor, plus the funding spread
    lv = SH["levels_pct"]
    T = (expiry - settle).days / 365.25
    ois = lv["bbg_estr_1y"] + (lv["bbg_estr_5y"] - lv["bbg_estr_1y"]) * (T - 1) / 4.0
    fin = ois + inp["Funding E+ (bps)"] / 100.0
    g = 1 + fin / 100.0
    fv_dirty = dirty * g ** T
    cpns = coupon_dates(settle, expiry)
    fv_cpns = sum(COUPON * g ** ((expiry - c).days / 365.25) for c in cpns)
    fwd_dirty = fv_dirty - fv_cpns
    fwd_accrued = 0.0 if expiry.month == 2 and expiry.day == 25 else COUPON * (expiry - dt.date(expiry.year, 2, 25)).days / 365.0
    fwd_clean = fwd_dirty - fwd_accrued
    fwd_yield = yield_one_year(fwd_clean)
    # the 1-year swap at expiry: spot today (curve unchanged) and the 4.4y1y forward from the par curve
    yrs, sw = CV["years"], CV["swap_rate_pct"]

    def par(t):
        for i in range(len(yrs) - 1):
            if yrs[i] <= t <= yrs[i + 1]:
                w = (t - yrs[i]) / (yrs[i + 1] - yrs[i])
                return sw[i] + w * (sw[i + 1] - sw[i])
        return sw[-1]

    s1 = sw[0]
    t_exp = (expiry - settle).days / 365.25
    t_mat = (MATURITY - settle).days / 365.25
    fwd_1y_swap = ((1 + par(t_mat) / 100) ** t_mat / (1 + par(t_exp) / 100) ** t_exp - 1) * 100
    fwd_spread_bp = (fwd_1y_swap - fwd_yield) * 100          # swap minus bond: negative, the bond cheap to the swap
    swap_matched = ytm + inp["Entry spread"] / 100.0
    named = {n["id"]: n for n in SC["named"]}
    rows = []
    for sid, label in [("S1", "Median since 2010"), ("S3", "Roll to spot: curve unchanged"), ("S4", "No roll: spread unchanged"),
                       ("S5", "Italy's 2011 crisis level"), ("BE", "Break-even after costs"), ("IMP", "Full impairment")]:
        s = named[sid]["spread_bp"]
        y = s1 - s / 100.0
        p = price_one_year(y)
        rows.append({"id": sid, "label": label, "spread_bp": s, "yield_pct": y, "price": p, "gain_points": p - fwd_clean,
                     "gain_eur_m_per_100m": (p - fwd_clean), "moic": named[sid]["moic"]})
    rows.append({"id": "FWD", "label": "Forward: what today's prices assume", "spread_bp": fwd_spread_bp, "yield_pct": fwd_yield,
                 "price": fwd_clean, "gain_points": 0.0, "gain_eur_m_per_100m": 0.0, "moic": None})
    be = next(r for r in rows if r["id"] == "BE")
    terms = json.load(open(os.path.join(DATA, "structure_terms_2026-10-07.json"), encoding="utf-8"))
    out = {
        "asof": inp["Trade Date"], "settlement": str(settle), "expiry": str(expiry), "years_to_expiry": T,
        "bond": {"name": inp["Bond Underlier"], "coupon": COUPON, "maturity": str(MATURITY), "clean_price": clean, "accrued": accrued,
                 "dirty_price": dirty, "yield_pct": ytm, "swap_matched_pct": swap_matched, "entry_spread_bp": inp["Entry spread"]},
        "financing": {"estr_ois_interp_pct": ois, "funding_spread_bp": inp["Funding E+ (bps)"], "rate_pct": fin,
                      "note": "flat term rate: Bloomberg EESWE 1y and 5y interpolated to the expiry tenor, plus the funding spread"},
        "forward": {"coupons_received": [str(c) for c in cpns], "fv_of_dirty_price": fv_dirty, "fv_of_coupons": fv_cpns,
                    "dirty_price": fwd_dirty, "accrued_at_expiry": fwd_accrued, "clean_price": fwd_clean, "implied_yield_pct": fwd_yield,
                    "forward_1y_swap_pct": fwd_1y_swap, "implied_spread_bp": fwd_spread_bp, "spot_1y_swap_pct": s1},
        "rows": rows,
        "breakeven_check": {"price_gain_points": be["gain_points"], "floor_cost_pct_notional": terms["floor_cost_pct_notional"],
                            "residual_points": be["gain_points"] - terms["floor_cost_pct_notional"],
                            "note": "at the model's break-even the bond-only gain less the floor's cost is the residual; the model nets the "
                                    "swap's own P&L, the floating-leg basis and bid-offer, which this page does not"},
        "jeff_2026_10_08": {"source": "docs/drafts/deck-jeff-outline-edit-v2-received-2026-10-08.pptx, pages 9 to 11",
                            "repo_pct": 3.33, "forward_date": "2031-02-20", "forward_price": 94.72, "forward_yield_pct": 8.93,
                            "forward_1y_swap_pct": 3.52, "spot_1y_swap_pct": 3.33, "forward_spread_bp": -540,
                            "roll_to_spot_bp": -3, "basis_4_4y_bp": 33,
                            "rows": {"S3": [-3, 3.36, 99.89, 5.2], "S4": [-83, 4.16, 99.12, 4.4], "BE": [-445, 7.79, 95.73, 1.0],
                                     "S5": [-350, None, 96.60, 1.9], "S1": [28, None, 100.19, 5.5]}},
    }
    return out


if __name__ == "__main__":
    out = build()
    p = os.path.join(DATA, f"forward_price_{ASOF}.json")
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    f, b, j = out["forward"], out["bond"], out["jeff_2026_10_08"]
    print("wrote", os.path.relpath(p, os.path.join(HERE, "..")))
    print(f"clean {b['clean_price']:.2f}  accrued {b['accrued']:.3f}  dirty {b['dirty_price']:.2f}  ytm {b['yield_pct']:.2f}")
    print(f"financing {out['financing']['rate_pct']:.2f}% (OIS {out['financing']['estr_ois_interp_pct']:.2f} + 17bp), T {out['years_to_expiry']:.2f}y")
    print(f"forward clean {f['clean_price']:.2f} (Jeff {j['forward_price']})  implied yield {f['implied_yield_pct']:.2f} (Jeff {j['forward_yield_pct']})")
    print(f"4.4y1y fwd swap {f['forward_1y_swap_pct']:.2f} (Jeff {j['forward_1y_swap_pct']})  spot 1y swap {f['spot_1y_swap_pct']:.2f} (Jeff {j['spot_1y_swap_pct']})")
    print(f"forward implied spread {f['implied_spread_bp']:.0f}bp (Jeff {j['forward_spread_bp']})")
    print(f"\n{'id':4s} {'label':36s} {'spread':>7s} {'yield':>6s} {'price':>7s} {'gain':>6s}   Jeff: spread yield price gain")
    for r in out["rows"]:
        jj = j["rows"].get(r["id"])
        print(f"{r['id']:4s} {r['label']:36s} {r['spread_bp']:7.1f} {r['yield_pct']:6.2f} {r['price']:7.2f} {r['gain_points']:6.2f}   {jj if jj else ''}")
    bc = out["breakeven_check"]
    print(f"\nbreak-even: bond-only gain {bc['price_gain_points']:.2f} less floor {bc['floor_cost_pct_notional']:.2f} = {bc['residual_points']:.2f} points")
