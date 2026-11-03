#!/usr/bin/env python3
"""Add a thumbnail (og:image) to every digest story that does not have one yet.

Run after writing data/digests.json and before deploying:
    python3 /workspace/dcost-daily/scripts/add_images.py
Adds per story: image (URL or null when the source has none), imageAlt, imageCredit.
Stories that already have an "image" key are skipped, so it is safe to rerun.
Pass --all to retry stories marked null.
"""
import json, re, sys, html, urllib.request
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

PATH = "/workspace/dcost-daily/data/digests.json"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"
META = re.compile(r"<meta\b[^>]*>", re.I)
ATTR = re.compile(r'([a-zA-Z:_-]+)\s*=\s*("([^"]*)"|\'([^\']*)\')')
KEYS = ["og:image:secure_url", "og:image", "og:image:url", "twitter:image", "twitter:image:src"]

def get(url, n=600000):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,image/*,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.geturl(), r.headers.get("content-type", ""), r.read(n)

def og_image(url):
    final, ctype, body = get(url)
    found = {}
    for tag in META.findall(body.decode("utf-8", "ignore")):
        a = {m.group(1).lower(): (m.group(3) if m.group(3) is not None else m.group(4)) for m in ATTR.finditer(tag)}
        k = (a.get("property") or a.get("name") or "").lower()
        if k in KEYS and a.get("content") and k not in found:
            found[k] = html.unescape(a["content"].strip())
    for k in KEYS:
        if k in found:
            img = urljoin(final, found[k])
            if img.startswith("http://"):
                img = "https://" + img[7:]
            if not img.startswith("https://"):
                continue
            try:
                _, ct, _ = get(img, 2048)
                if ct.startswith("image/"):
                    return img
            except Exception:
                pass
    return None

def fill(s):
    try:
        s["image"] = og_image(s["url"])
    except Exception as e:
        print("  no page:", s["url"], e, file=sys.stderr)
        s["image"] = None
    s["imageAlt"] = s.get("title", "")
    s["imageCredit"] = s.get("source", "")
    print(("ok   " if s["image"] else "none ") + s["url"])

def main():
    retry = "--all" in sys.argv
    data = json.load(open(PATH))
    todo = [s for d in data for s in d.get("stories", []) if "image" not in s or (retry and not s.get("image"))]
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(fill, todo))
    with open(PATH, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"{len(todo)} stories checked")
    # 2026-10-19: keep sitemap.xml in step with the newest digest (same publish run).
    import subprocess, os
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen_sitemap.py")], check=False)

if __name__ == "__main__":
    main()
