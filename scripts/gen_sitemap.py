#!/usr/bin/env python3
"""Regenerate sitemap.xml for dcostdaily.com. Run after every digest update, before deploy.
Digests have no pages of their own: today's renders on / and all of them on /archive,
so those two get lastmod = newest digest date. Static pages get their file's mtime.
Add a new page by adding it to PAGES. Generated SEO pages (ev-cost/, tesla/, guides/ from
gen_pages.py, plus compare/ and ev-vs-gas/ from gen_compare.py) are picked up automatically from their folders."""
import glob
import json, os, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://dcostdaily.com"
PAGES = [("/", "index.html", "daily", "1.0"), ("/archive", "archive.html", "daily", "0.7"),
         ("/calculator", "calculator.html", "monthly", "0.8"), ("/chargers", "chargers.html", "monthly", "0.8")]
dates = [d["date"] for d in json.load(open(os.path.join(ROOT, "data", "digests.json")))]
newest = max(dates)[:10]
out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for path, f, freq, pri in PAGES:
    if not os.path.exists(os.path.join(ROOT, f)): continue
    lm = newest if path in ("/", "/archive") else datetime.date.fromtimestamp(os.path.getmtime(os.path.join(ROOT, f))).isoformat()
    out.append(f"  <url><loc>{BASE}{path}</loc><lastmod>{lm}</lastmod><changefreq>{freq}</changefreq><priority>{pri}</priority></url>")
# Generated SEO pages: every .html in these folders. index.html maps to the folder URL.
for d, freq, pri in (("ev-cost", "monthly", "0.7"), ("tesla", "monthly", "0.7"), ("guides", "monthly", "0.6"), ("compare", "monthly", "0.7"), ("ev-vs-gas", "monthly", "0.6")):
    for fp in sorted(glob.glob(os.path.join(ROOT, d, "*.html"))):
        name = os.path.basename(fp)[:-5]
        path = f"/{d}/" if name == "index" else f"/{d}/{name}"
        lm = datetime.date.fromtimestamp(os.path.getmtime(fp)).isoformat()
        out.append(f"  <url><loc>{BASE}{path}</loc><lastmod>{lm}</lastmod><changefreq>{freq}</changefreq><priority>{pri if name != 'index' else '0.8'}</priority></url>")
out.append("</urlset>")
open(os.path.join(ROOT, "sitemap.xml"), "w").write("\n".join(out) + "\n")
print("sitemap.xml:", len(out) - 3, "urls, newest digest", newest)
