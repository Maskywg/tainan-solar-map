"""Data integrity, scope safeguards, provenance, and static-asset validation."""
import csv,hashlib,json,re
from pathlib import Path
from html.parser import HTMLParser
from PIL import Image
root=Path(__file__).resolve().parents[1]
load=lambda name:json.loads((root/'data'/name).read_text())
a=load('approved.json');d=load('districts.json');h=load('history.json');p=load('pending.json');g=load('tainan-districts.geojson')
assert len(a)==799 and {r['source_number'] for r in a}==set(range(1,800))
assert len({r['id'] for r in a})==799
assert all(r['geometry'] is None and r['construction_status']=='unverified' and r['image_checked_on'] is None for r in a)
assert all(1<=r['source_page']<=16 and r['area_m2']>0 for r in a)
assert len(d)==len({r['code'] for r in d})==37
assert {r['name'] for r in d}=={r['properties']['TOWNNAME'] for r in g['features']}
assert {r['code'] for r in d}=={r['properties']['TOWNCODE'] for r in g['features']}
assert sum(r['approval_count'] for r in d)==13357
assert abs(sum(r['capacity_kwp'] for r in d)-4809584.763)<0.001
assert sum(len(r['districts'])>1 for r in a)==2
assert sum(r['facility_type']=='ancillary' for r in a)==21
assert sum(r['register_count'] for r in d)==801
assert next(r for r in d if r['name']=='南化區')['register_count']==11
assert next(r for r in d if r['name']=='新化區')['register_count']==25
for number,section,area in [(17,'中坑段',659.46),(34,'知母義段',16832),(58,'宅子港段',2029),(235,'永昌段；莊禮段',6164.51),(713,'𦰡拔林段；潭頂段',14974),(799,'宅子港段',5221)]:
 r=next(r for r in a if r['source_number']==number);assert (r['section'],r['area_m2'])==(section,area)
assert [(v['date'],v['count']) for v in h]==[('2025-11-27',826),('2026-03-05',818),('2026-09-09',799)]
assert all(len(v['records'])==v['count'] for v in h)
assert len(p)==28 and all(not r['districts'] and r['geometry'] is None and r['status']=='pending' for r in p)
assert hashlib.md5((root/'data/sources/approved-2026-09-09.pdf').read_bytes()).hexdigest()=='f8b546a16be2ccdb9c13fc050299d413'
m=load('source-manifest.json')
for file,digest in m['hashes'].items():assert hashlib.sha256((root/'data/sources'/file).read_bytes()).hexdigest()==digest,file
for source in m['sources']:assert (root/'data'/source['file']).is_file(),source
class HTML(HTMLParser):
 def __init__(self):super().__init__();self.meta={};self.links=[];self.ids=[]
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if tag=='meta':self.meta[attrs.get('property',attrs.get('name'))]=attrs.get('content')
  if 'id' in attrs:self.ids.append(attrs['id'])
  for k in ['src','href']:
   if k in attrs:self.links.append(attrs[k])
x=HTML();x.feed((root/'index.html').read_text());assert len(x.ids)==len(set(x.ids))
for u in x.links:
 if u.startswith(('http:','https:','data:','#')):continue
 assert (root/u.split('#')[0].split('?')[0]).exists(),u
required=['og:type','og:title','og:description','og:url','og:image','og:image:width','og:image:height','og:image:alt','twitter:card','twitter:title','twitter:description','twitter:image','twitter:image:alt']
assert all(x.meta.get(k) for k in required)
assert x.meta['og:url']=='https://maskywg.github.io/tainan-solar-map/'
assert x.meta['og:image']==x.meta['twitter:image']=='https://maskywg.github.io/tainan-solar-map/og-observatory-20261127.png'
with Image.open(root/'og-observatory-20261127.png') as im:assert im.size==(1200,630);im.verify()
with (root/'data/approved.csv').open(encoding='utf-8-sig') as f:assert len(list(csv.DictReader(f)))==799
print('PASS: 799 records / 37 districts / source hashes / scope safeguards / historical counts / internal assets / share preview')
