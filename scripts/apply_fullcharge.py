#!/usr/bin/env python3
"""Full Charge restyle (Oct 21 2026): shared markup swaps applied to every page and to the page template.
Idempotent. Run after gen_pages.py (it also patches gen_pages.py so regenerated pages keep the look).
Only markup that CSS cannot reach changes here: the wordmark, the font links and the asset version."""
import pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
V_NEW = "20261021fc"
FONTS = ('<link rel=preconnect href="https://fonts.googleapis.com"><link rel=preconnect href="https://fonts.gstatic.com" crossorigin>'
         '<link rel=stylesheet href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600&family=Barlow+Semi+Condensed:wght@500;600;700;800&display=swap">')
CELLS = "".join(f'<rect x="{x}" y="4" width="5" height="14" rx="1" fill="{c}"/>' for x, c in
                [(4, "#fff"), (10.5, "#fff"), (17, "#fff"), (23.5, "#fff"), (30, "#1d9bf0")])
WM_OLD = '<a class="wm" href="/">dcost daily</a>'
WM_NEW = ('<a class="wm" href="/" aria-label="dcost daily home"><svg class="wm-b" width="41" height="22" viewBox="0 0 41 22" aria-hidden="true">'
          '<rect x="1" y="1" width="36" height="20" rx="4" fill="none" stroke="#fff" stroke-width="2"/><rect x="37" y="7" width="3" height="8" rx="1" fill="#fff"/>'
          + CELLS + '</svg><b>DCOST</b><span>DAILY</span></a>')
def fix(t):
    t = t.replace(WM_OLD, WM_NEW)
    t = re.sub(r'\?v=(?:\d{8}[a-z]*|<function V at 0x[0-9a-f]+>)', '?v=' + V_NEW, t)
    if 'fonts.googleapis.com' not in t:
        t = t.replace('<link rel=stylesheet href="/style.css', FONTS + '<link rel=stylesheet href="/style.css', 1)
    return t
n = 0
for p in ROOT.rglob("*.html"):
    if "scripts" in p.parts: continue
    s = p.read_text(); t = fix(s)
    if t != s: p.write_text(t); n += 1
g = ROOT / "scripts/gen_pages.py"; s = g.read_text()
t = s.replace(WM_OLD, WM_NEW.replace("{", "{{").replace("}", "}}")) if WM_OLD in s else s
t = re.sub(r'^V = "\d{8}[a-z]*"', f'V = "{V_NEW}"', t, flags=re.M)
if 'fonts.googleapis.com' not in t:
    t = t.replace('<link rel=stylesheet href="/style.css?v={V}">', FONTS + '<link rel=stylesheet href="/style.css?v={V}">', 1)
if t != s: g.write_text(t)
print(f"pages updated: {n}")
