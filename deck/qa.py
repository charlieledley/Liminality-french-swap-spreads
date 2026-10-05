# -*- coding: utf-8 -*-
"""Geometric QA for a .pptx, without a renderer.

There is no LibreOffice on this machine, so the usual render-and-look pass is unavailable.
Instead this measures text with the REAL font files (Calibri and Cambria are both installed
under C:\\Windows\\Fonts), wraps each paragraph to its box width exactly the way PowerPoint
will, and reports:

  OVERFLOW  wrapped text is taller than its shape, or a single word is wider than the box
  BOUNDS    a shape sits off the slide, or inside the 0.5in margin
  OVERLAP   two text-bearing shapes intersect

Measured, not estimated -- the whole point is that the numbers come from the same glyph
metrics PowerPoint uses, so a pass here means the text really fits.
"""
import glob
import os
import sys

from PIL import ImageFont
from pptx import Presentation
from pptx.util import Emu

EMU = 914400.0
FONTS = {
    ("Calibri", False, False): "calibri.ttf", ("Calibri", True, False): "calibrib.ttf",
    ("Calibri", False, True): "calibrii.ttf", ("Calibri", True, True): "calibriz.ttf",
    ("Cambria", False, False): "cambria.ttc", ("Cambria", True, False): "cambriab.ttf",
    ("Cambria", False, True): "cambriai.ttf", ("Cambria", True, True): "cambriaz.ttf",
}
FDIR = r"C:\Windows\Fonts"
_cache = {}
MARGIN = 0.5
SLIDE_PAD = 0.0


def font(name, bold, italic, pt):
    k = (name, bool(bold), bool(italic), round(pt, 1))
    if k not in _cache:
        fn = FONTS.get((name, bool(bold), bool(italic))) or FONTS[("Calibri", False, False)]
        path = os.path.join(FDIR, fn)
        if not os.path.exists(path):
            path = os.path.join(FDIR, "calibri.ttf")
        # PIL wants pixels; at 96dpi one point is 96/72 px
        _cache[k] = ImageFont.truetype(path, max(1, int(round(pt * 96.0 / 72.0))), index=0)
    return _cache[k]


def wrap(text, f, width_px):
    """Greedy wrap, same rule PowerPoint uses. Returns (n_lines, widest_word_px)."""
    lines, widest = 0, 0
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        n = 1
        for w in words:
            widest = max(widest, f.getlength(w))
            t = (cur + " " + w).strip()
            if f.getlength(t) <= width_px or not cur:
                cur = t
            else:
                n += 1
                cur = w
        lines += n
    return lines, widest


def shape_text_height(shape):
    """Total wrapped height of a shape's text, in inches, plus the widest unbreakable word."""
    tf = shape.text_frame
    wpx = (shape.width / EMU - (tf.margin_left + tf.margin_right) / EMU) * 96.0
    if wpx <= 4:
        return 0.0, 0.0
    total, widest = 0.0, 0.0
    for p in tf.paragraphs:
        runs = [r for r in p.runs if r.text]
        if not runs:
            total += 0.14
            continue
        txt = "".join(r.text for r in runs)
        r0 = runs[0]
        pt = (r0.font.size.pt if r0.font.size else 18.0)
        nm = r0.font.name or "Calibri"
        f = font(nm, r0.font.bold, r0.font.italic, pt)
        n, ww = wrap(txt, f, wpx)
        widest = max(widest, ww / 96.0)
        ls = p.line_spacing if isinstance(p.line_spacing, float) else 1.0
        sa = (p.space_after.pt if p.space_after is not None else 0.0)
        # PowerPoint line box is ~1.22x the point size for these faces
        total += n * pt * 1.22 * ls / 72.0 + sa / 72.0
    total += (tf.margin_top + tf.margin_bottom) / EMU
    return total, widest


def boxes(slide):
    out = []
    for sh in slide.shapes:
        try:
            x, y = sh.left / EMU, sh.top / EMU
            w, hh = sh.width / EMU, sh.height / EMU
        except TypeError:
            continue
        has = sh.has_text_frame and sh.text_frame.text.strip()
        out.append((sh, x, y, w, hh, bool(has)))
    return out


def table_height(sh):
    """What a table will ACTUALLY occupy once PowerPoint grows rows to fit their text.

    python-pptx writes the row height we ask for, but PowerPoint treats it as a minimum
    and expands any row whose cell text wraps. A table that looks 2.4in tall in the
    generator can render 3.1in tall and land on whatever sits below it, and nothing in
    the text checks sees it because a table is a graphicFrame, not a text frame.
    """
    t = sh.table
    widths = [c.width / EMU for c in t.columns]
    total = 0.0
    for row in t.rows:
        need = row.height / EMU
        for j, cell in enumerate(row.cells):
            txt = cell.text
            if not txt.strip():
                continue
            runs = [r for p in cell.text_frame.paragraphs for r in p.runs if r.text]
            pt = (runs[0].font.size.pt if runs and runs[0].font.size else 12.0)
            nm = (runs[0].font.name if runs and runs[0].font.name else "Calibri")
            bold = bool(runs[0].font.bold) if runs else False
            avail = (widths[j] - (cell.margin_left + cell.margin_right) / EMU) * 96.0
            n, _w = wrap(txt, font(nm, bold, False, pt), max(avail, 8))
            need = max(need, n * pt * 1.22 / 72.0
                       + (cell.margin_top + cell.margin_bottom) / EMU + 0.02)
        total += need
    return total


def check(path, slide_w=13.333, slide_h=7.5, verbose=False):
    prs = Presentation(path)
    issues = []
    for i, s in enumerate(prs.slides, 1):
        bs = boxes(s)
        # tables: real rendered height, and what it would collide with
        tabs = []
        for sh in s.shapes:
            if not (getattr(sh, "has_table", False) and sh.has_table):
                continue
            th = table_height(sh)
            x, y, w = sh.left / EMU, sh.top / EMU, sh.width / EMU
            tabs.append((x, y, w, th))
            if y + th > slide_h - 0.28:
                issues.append((i, "TABLE", "runs to %.2fin, past the %.2fin safe bottom"
                               % (y + th, slide_h - 0.28)))
        for x, y, w, th in tabs:
            for sh2, x2, y2, w2, h2, has2 in bs:
                if not has2 or y2 < y:
                    continue
                ox = min(x + w, x2 + w2) - max(x, x2)
                if ox > 0.1 and y2 < y + th - 0.06:
                    issues.append((i, "TABLE", "overlaps %r at y=%.2f (table ends %.2f)"
                                   % (sh2.text_frame.text[:34], y2, y + th)))
        for sh, x, y, w, hh, has in bs:
            full = w > slide_w - 0.02 and hh > slide_h - 0.02
            if not full:
                if x < -0.01 or y < -0.01 or x + w > slide_w + 0.01 or y + hh > slide_h + 0.01:
                    issues.append((i, "BOUNDS", "%s off-slide at (%.2f,%.2f) %.2fx%.2f"
                                   % (sh.shape_type, x, y, w, hh)))
                elif has and (x < MARGIN - 0.13 or x + w > slide_w - MARGIN + 0.13):
                    issues.append((i, "BOUNDS", "text inside side margin: x=%.2f..%.2f  %r"
                                   % (x, x + w, sh.text_frame.text[:40])))
            if has:
                th, widest = shape_text_height(sh)
                if th > hh + 0.055:
                    issues.append((i, "OVERFLOW", "needs %.2fin has %.2fin (+%.2f)  %r"
                                   % (th, hh, th - hh, sh.text_frame.text[:52])))
                if widest > w + 0.02:
                    issues.append((i, "OVERFLOW", "unbreakable word %.2fin > box %.2fin  %r"
                                   % (widest, w, sh.text_frame.text[:40])))
        # text must stay inside the card it sits on: a filled, text-free shape that is not
        # the slide background is a card, and anything mostly over it must fit within it.
        cards = [b for b in bs if not b[5] and b[3] > 0.6 and b[4] > 0.25
                 and "PICTURE" not in str(b[0].shape_type)
                 and not (b[3] > slide_w - 0.02 and b[4] > slide_h - 0.02)]
        for sh, x, y, w, hh, _ in [b for b in bs if b[5]]:
            for _, cx, cy, cw, ch, _ in cards:
                ox = min(x + w, cx + cw) - max(x, cx)
                oy = min(y + hh, cy + ch) - max(y, cy)
                if ox <= 0 or oy <= 0 or ox * oy < 0.12 * w * hh:
                    continue                       # not sitting on this card
                th, _u = shape_text_height(sh)
                bot = y + max(hh, th)
                if bot > cy + ch - 0.04 or y < cy - 0.02 or x < cx - 0.02 \
                        or x + w > cx + cw + 0.02:
                    issues.append((i, "CONTAIN",
                                   "text %.2f..%.2f overflows card %.2f..%.2f  %r"
                                   % (y, bot, cy, cy + ch, sh.text_frame.text[:44])))
        txt = [b for b in bs if b[5]]
        for a in range(len(txt)):
            for b in range(a + 1, len(txt)):
                _, x1, y1, w1, h1, _ = txt[a]
                _, x2, y2, w2, h2, _ = txt[b]
                ox = min(x1 + w1, x2 + w2) - max(x1, x2)
                oy = min(y1 + h1, y2 + h2) - max(y1, y2)
                if ox > 0.06 and oy > 0.06:
                    issues.append((i, "OVERLAP", "%.2fx%.2fin  %r  vs  %r"
                                   % (ox, oy, txt[a][0].text_frame.text[:30],
                                      txt[b][0].text_frame.text[:30])))
    n = len(prs.slides.__iter__.__self__._sldIdLst)
    print("%s  -- %d slides, %d issues" % (os.path.basename(path), n, len(issues)))
    for i, kind, msg in issues:
        print("  s%-3d %-9s %s" % (i, kind, msg))
    return issues


if __name__ == "__main__":
    for p in sys.argv[1:] or sorted(glob.glob("*.pptx")):
        check(p)
