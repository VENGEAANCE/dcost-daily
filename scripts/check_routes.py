from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import xml.etree.ElementTree as ET
root=Path(__file__).resolve().parent.parent
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  for key,value in attrs:
   if key in ('href','src') and value:self.links.append(value)
errors=[];count=0
for p in root.rglob('*.html'):
 text=p.read_text(encoding='utf-8');assert '\u2014' not in text,p
 parser=Links();parser.feed(text)
 for link in parser.links:
  url=urlsplit(link)
  if url.scheme or url.netloc or not url.path:continue
  target=root/unquote(url.path).lstrip('/') if url.path.startswith('/') else p.parent/unquote(url.path)
  if url.path.startswith(('/share','/og-image')):continue # Existing externally routed Workers.
  if not any(t.is_file() for t in [target,Path(str(target)+'.html'),target/'index.html']):errors.append((str(p.relative_to(root)),link))
  count+=1
for loc in ET.parse(root/'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
 p=root/urlsplit(loc.text).path.lstrip('/')
 assert any(t.is_file() for t in [p,Path(str(p)+'.html'),p/'index.html']),loc.text
assert not errors,errors
assert (root/'robots.txt').is_file()
print(f'{count} internal link/asset targets and all sitemap routes resolve; HTML contains no em dashes.')

