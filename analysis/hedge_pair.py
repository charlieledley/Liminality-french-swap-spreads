# -*- coding: utf-8 -*-
"""The low-coupon / high-coupon OAT pair as a sovereign-stress hedge (Charlie, 2026-10-05).

Buy FRTR 0.5% 05/25/2040, sell FRTR 4.5% 04/25/2041. Same maturity area, yields 2.4bp apart on
2026-10-02, but the low-coupon bond trades at 59% of the high-coupon bond's price. Charlie's
point: if the market starts to price an actual sovereign default, bonds trade on price (points
of recovery) rather than on yield, so the two prices converge and the pair pays.

Inputs: analysis/data/hedge_pair_2026-10-02.csv, transcribed from Charlie's Bloomberg screenshot
(kept in analysis/data/raw/). Durations are not on the screen; they are computed here from the
quoted yield, annual coupons and ACT/ACT, settlement 2026-10-05, and the computed clean price is
checked against the quoted one so the convention is known to be close.

What the script computes
  - per 100 of face of each bond: price, accrued, modified duration, DV01
  - the pair under three sizings: DV01-neutral (the one the trade would use: buy DV01_high/DV01_low
    = 1.41 face of the low coupon per 1 of the high), equal face, and equal market value
  - the net carry of each sizing per year, in price points per 100 face of the short leg
  - the payoff if both bonds converge to one common price P* (recovery-style pricing), for a
    ladder of P* with 75 as the base assumption; with equal face the payoff is the current
    price gap whatever P* is
  - the net duration of each sizing, since neither is rate-neutral

Output: deck/data/hedge_pair_2026-10-02.json
"""
import datetime as dt
import json
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ASOF = "2026-10-02"
SETTLE = dt.date(2026, 10, 5)
CSV = os.path.join(HERE, "data", f"hedge_pair_{ASOF}.csv")
OUT = os.path.join(HERE, "..", "deck", "data", f"hedge_pair_{ASOF}.json")
CONVERGE_TO = [90, 80, 75, 60, 50, 40]
RECOVERY = 75                 # Charlie's base assumption, 2026-10-05


def cashflow_dates(maturity):
    d, out = maturity, []
    while d > SETTLE:
        out.append(d)
        d = d.replace(year=d.year - 1)
    return sorted(out)


def analytics(coupon, maturity, ytm, quoted_clean):
    """Annual-coupon bond, ACT/ACT, yield compounded annually. Returns dict of per-100-face figures."""
    dates = cashflow_dates(maturity)
    prev = dates[0].replace(year=dates[0].year - 1)
    frac0 = (dates[0] - SETTLE).days / (dates[0] - prev).days          # time to next coupon, in years
    accrued = coupon * (SETTLE - prev).days / (dates[0] - prev).days
    y = ytm / 100.0
    pv, dur = 0.0, 0.0
    for i, d in enumerate(dates):
        t = frac0 + i
        cf = coupon + (100.0 if d == maturity else 0.0)
        disc = cf / (1 + y) ** t
        pv += disc
        dur += t * disc
    dirty = pv
    clean = dirty - accrued
    macaulay = dur / dirty
    modified = macaulay / (1 + y)
    dv01 = modified * dirty / 10000.0           # price points per 100 face per 1bp
    return {"coupon": coupon, "maturity": str(maturity), "ytm": ytm, "quoted_clean": quoted_clean,
            "computed_clean": round(clean, 3), "accrued": round(accrued, 3), "dirty": round(dirty, 3),
            "macaulay": round(macaulay, 2), "modified_duration": round(modified, 2), "dv01_per_100": round(dv01, 4),
            "years_to_maturity": round((maturity - SETTLE).days / 365.25, 2)}


def build():
    d = pd.read_csv(CSV)
    lo = d.iloc[0]; hi = d.iloc[1]
    L = analytics(float(lo.coupon_pct), dt.date.fromisoformat(lo.maturity), float(lo.mid_ytm_pct), float(lo.last_price))
    H = analytics(float(hi.coupon_pct), dt.date.fromisoformat(hi.maturity), float(hi.mid_ytm_pct), float(hi.last_price))
    pl, ph = float(lo.last_price), float(hi.last_price)
    sizings = {}
    for name, f_lo in (("dv01_neutral", H["dv01_per_100"] / L["dv01_per_100"]),     # the sizing the trade would use (Charlie)
                       ("equal_face", 1.0), ("equal_market_value", ph / pl)):
        # carry per year per 100 face of the short leg: total return at the quoted yield on each leg's price
        carry = f_lo * L["ytm"] / 100 * pl - H["ytm"] / 100 * ph
        coupon_net = f_lo * L["coupon"] - H["coupon"]
        net_dv01 = f_lo * L["dv01_per_100"] - H["dv01_per_100"]
        rows = []
        for pstar in CONVERGE_TO:
            long_pl = f_lo * (pstar - pl)
            short_pl = ph - pstar
            rows.append({"common_price": pstar, "long_leg": round(long_pl, 2), "short_leg": round(short_pl, 2),
                         "net": round(long_pl + short_pl, 2)})
        at_r = next(r for r in rows if r["common_price"] == RECOVERY)
        sizings[name] = {"face_low_per_100_high": round(f_lo, 3), "market_value_low": round(f_lo * pl, 2),
                         "at_recovery": at_r, "recovery": RECOVERY,
                         "market_value_high": round(ph, 2), "net_carry_per_year": round(carry, 2),
                         "net_coupon_per_year": round(coupon_net, 2), "net_dv01_per_100_high": round(net_dv01, 4),
                         "convergence": rows}
    # weekly history of both bonds' yields and prices (Desktop API pull of 2026-10-05) for the page's chart
    hist = pd.read_csv(os.path.join(HERE, "data", "hedge_pair_history_bbg_2026-10-05.csv"), index_col=0, parse_dates=True)
    hist = hist.drop(columns=[c for c in hist.columns if c == "source"]).dropna().resample("W-FRI").last().dropna()
    gap = (hist.high_ytm - hist.low_ytm) * 100
    weekly = {"date": [str(x.date()) for x in hist.index],
              **{c: [round(float(v), 3) for v in hist[c]] for c in hist.columns}}
    history_stats = {"first": str(hist.index[0].date()), "last": str(hist.index[-1].date()),
                     "yield_gap_bp_mean": round(float(gap.mean()), 1), "yield_gap_bp_min": round(float(gap.min()), 1),
                     "yield_gap_bp_max": round(float(gap.max()), 1),
                     "price_ratio_first": round(float(hist.low_price.iloc[0] / hist.high_price.iloc[0]), 3),
                     "price_ratio_last": round(float(hist.low_price.iloc[-1] / hist.high_price.iloc[-1]), 3)}
    out = {"asof": ASOF, "settlement": str(SETTLE), "source": "Bloomberg screen 2026-10-02 16:00 via Charlie's screenshot; durations computed",
           "weekly": weekly, "history": history_stats,
           "low": {"name": lo.bond, "price": pl, **L}, "high": {"name": hi.bond, "price": ph, **H},
           "price_ratio": round(pl / ph, 3), "yield_gap_bp": round((H["ytm"] - L["ytm"]) * 100, 1),
           "price_gap": round(ph - pl, 3), "sizings": sizings,
           "convention_note": "Annual coupons, ACT/ACT, annual compounding, settlement T+1 from 2026-10-02; the computed clean "
                              "prices differ from the quoted ones by the amounts shown, which is the convention error to allow for."}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    return out


if __name__ == "__main__":
    o = build()
    for k in ("low", "high"):
        b = o[k]
        print(f"{b['name']:30s} price {b['price']:7.3f} (computed {b['computed_clean']:7.3f}) ytm {b['ytm']:.3f} "
              f"mod dur {b['modified_duration']:5.2f} dv01 {b['dv01_per_100']:.4f} yrs {b['years_to_maturity']}")
    print(f"price ratio {o['price_ratio']}, yield gap {o['yield_gap_bp']}bp, price gap {o['price_gap']}")
    for nm, sz in o["sizings"].items():
        print(f"\n{nm}: {sz['face_low_per_100_high']} face of low per 100 high; carry {sz['net_carry_per_year']:+.2f}/yr; "
              f"net coupon {sz['net_coupon_per_year']:+.2f}/yr; net DV01 {sz['net_dv01_per_100_high']:+.4f}")
        for r in sz["convergence"]:
            print(f"   both at {r['common_price']:3d}: long {r['long_leg']:+7.2f}  short {r['short_leg']:+7.2f}  net {r['net']:+7.2f}")
    print("wrote", os.path.relpath(OUT, os.path.join(HERE, "..")))
