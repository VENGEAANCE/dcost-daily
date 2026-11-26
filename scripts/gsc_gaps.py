#!/usr/bin/env python3
"""Find EV search opportunities in a private Google Search Console export."""
import argparse
import csv
from collections import defaultdict
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
GENERIC = {"/", "/archive"}
STOP = set("a an and are at by do does for from how i in is it much my of on or the to what with".split())
SYNONYMS = {"chargers": "charger", "charging": "charge", "charged": "charge",
            "prices": "cost", "price": "cost", "costs": "cost", "rates": "rate",
            "vehicles": "vehicle", "versus": "vs",
            "breakers": "breaker", "amps": "amp", "plugs": "plug", "outlets": "outlet"}
COMMERCIAL = set("charger charge breaker hardwired nema electricity rate cost gas".split())
LOW_INTENT = set("news digest archive newsletter login dcostdaily".split())


def terms(value):
    value = re.sub(r"\belectric vehicles?\b", "ev", value.lower())
    return frozenset(SYNONYMS.get(w, w) for w in re.findall(r"[a-z0-9]+", value) if w not in STOP)


class Headings(HTMLParser):
    def __init__(self):
        super().__init__()
        self.field = None
        self.parts = {"title": [], "h1": []}

    def handle_starttag(self, tag, attrs):
        if tag in self.parts:
            self.field = tag

    def handle_endtag(self, tag):
        if tag == self.field:
            self.field = None

    def handle_data(self, data):
        if self.field:
            self.parts[self.field].append(data)


def inventory():
    pages = {}
    for loc in ET.parse(ROOT / "sitemap.xml").findall(".//{*}loc"):
        path = urlsplit(loc.text).path
        file = ROOT / (path.lstrip("/") + ("index.html" if path.endswith("/") else ".html"))
        parser = Headings()
        parser.feed(file.read_text(encoding="utf-8"))
        pages[path] = [terms(path)] + [terms(" ".join(parts)) for parts in parser.parts.values()]
    return pages


def csv_rows(file, required):
    aliases = {"top queries": "query", "queries": "query", "top pages": "page", "pages": "page",
               "url": "page", "average position": "position"}
    with file.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        for row in reader:
            header = [aliases.get(s.strip().lower(), s.strip().lower()) for s in row]
            if required <= set(header):
                break
        else:
            raise ValueError(f"{file.name} needs columns {', '.join(sorted(required))}")
        for row in reader:
            if any(row):
                if len(row) != len(header):
                    raise ValueError(f"{file.name} row {reader.line_num} has the wrong column count")
                yield dict(zip(header, (s.strip() for s in row)))


def number(value):
    return float(value.replace(",", ""))


def load_metrics(file, dimensions):
    rows = []
    for row in csv_rows(file, dimensions | {"clicks", "impressions", "position"}):
        ctr = row.get("ctr", "")
        if ctr:
            row["ctr"] = number(ctr.rstrip("%")) / (100 if ctr.endswith("%") else 1)
        for field in ("clicks", "impressions"):
            row[field] = int(row[field].replace(",", ""))
        row["position"] = number(row["position"])
        if "page" in row:
            row["page"] = urlsplit(row["page"]).path or "/"
        rows.append(row)
    return rows


def match(tokens, pages, page_impressions):
    # Require most query terms to occur together in one slug, title, or H1.
    candidates = []
    for path, fields in pages.items():
        if path in GENERIC or not tokens:
            continue
        for field in fields:
            overlap = len(tokens & field)
            coverage = overlap / len(tokens)
            if coverage >= .75 and overlap >= min(2, len(tokens)):
                candidates.append((coverage, overlap / len(field), page_impressions[path], path))
    return max(candidates)[-1] if candidates else None


def report(folder, start, end):
    queries = load_metrics(folder / "queries.csv", {"query"})
    page_rows = load_metrics(folder / "pages.csv", {"page"})
    if not queries or not page_rows:
        raise ValueError("Both queries.csv and pages.csv need performance rows")
    combined = folder / "queries-pages.csv"
    pairs = load_metrics(combined, {"query", "page"}) if combined.exists() else []
    pages = inventory()
    page_impressions = defaultdict(int)
    for row in page_rows:
        page_impressions[row["page"]] += row["impressions"]
    by_query = defaultdict(list)
    for row in pairs:
        by_query[row["query"].casefold()].append(row)
    groups = defaultdict(list)
    for row in queries:
        tokens = terms(row["query"])
        if tokens:
            groups[tokens].append(row)

    opportunities = []
    for tokens, rows in groups.items():
        impressions = sum(r["impressions"] for r in rows)
        if not impressions or not tokens & COMMERCIAL or tokens & LOW_INTENT:
            continue
        destination = match(tokens, pages, page_impressions)
        attributed = defaultdict(int)
        for row in rows:
            for pair in by_query[row["query"].casefold()]:
                attributed[pair["page"]] += pair["impressions"]
        leader = max(attributed, key=lambda p: (attributed[p], p), default=None)
        majority = leader if leader and attributed[leader] > impressions / 2 else None
        if majority in pages and majority not in GENERIC and match(tokens, {majority: pages[majority]}, page_impressions):
            destination = majority
        best = min(r["position"] for r in rows)
        if destination and best <= 10 and majority not in GENERIC:
            continue
        reason = ("Most impressions go to the homepage or archive" if majority in GENERIC
                  else "Existing page ranks below position 10" if destination
                  else "No dedicated page matched")
        queries_sorted = sorted(rows, key=lambda r: (-r["impressions"], r["query"]))
        slug = "-".join(re.findall("[a-z0-9]+", queries_sorted[0]["query"].lower()))
        target = destination or "/guides/" + slug
        action = "Improve existing page" if target in pages else "Review new guide"
        charger = bool(tokens & {"charger", "breaker", "hardwired", "nema", "outlet"})
        opportunities.append((-impressions, target, [r["query"] for r in queries_sorted],
                              sum(r["clicks"] for r in rows), best, majority or destination,
                              reason, action, charger))
    lines = ["# Search Console content gaps", "",
             "These are automated candidates. See the [editorial decision](review.md) for the reviewed export.", "", f"Export period {start} through {end}.",
             f"Rows: {len(queries)} queries, {len(page_rows)} pages, {len(pairs)} query/page pairs.", "",
             "Queries with equal normalized terms form a cluster. Opportunities are ordered by total impressions. "
             "Position is the best query average in the cluster. Without query/page attribution, the current URL "
             "is a text match from the sitemap, title, or H1. Page-only totals break matching ties.", ""]
    for rank, (negative, target, names, clicks, pos, current, reason, action, picks) in enumerate(sorted(opportunities)[:10], 1):
        lines.extend([f"## {rank}. {names[0]}", "", "Queries: " + ", ".join(names),
                      f"Baseline: {-negative:,} impressions, {clicks:,} clicks, best average position {pos:.2f}.",
                      f"Current URL: {current or 'unknown'}. {reason}.",
                      f"{action}: {target}. Charger picks: {'yes' if picks else 'no'}.", ""])
    if not opportunities:
        lines.append("No qualifying opportunities in this export.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "data/gsc")
    parser.add_argument("--start", type=date.fromisoformat, required=True)
    parser.add_argument("--end", type=date.fromisoformat, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/gsc-gaps/report.md")
    args = parser.parse_args()
    if args.end < args.start:
        parser.error("end must be on or after start")
    try:
        result = report(args.input, args.start, args.end)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")


if __name__ == "__main__":
    main()
