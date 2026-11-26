"""Rebuild published JSON from preserved official source snapshots (pdfplumber required)."""
import csv, json, re, hashlib
from pathlib import Path
from decimal import Decimal
import pdfplumber
ROOT=Path(__file__).resolve().parents[1]
def dump(name,obj): (ROOT/'data'/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def clean(s):return re.sub(r'\s+','',s or '')
records=[]
with pdfplumber.open(ROOT/'data/sources/approved-2026-09-09.pdf') as pdf:
 for page_no,page in enumerate(pdf.pages,1):
  for table in page.extract_tables():
   for row in table:
    if not row[0] or not row[0].isdigit():continue
    assert len(row)==8, row
    n,applicant,district,section,subsection,parcels,area,note=map(clean,row)
    ds=district.split('；'); ancillary=bool(re.search('升壓|變電|機電|電桿|電塔|開關|儲能',note))
    records.append(dict(id='approved-'+n,source_number=int(n),applicant=applicant,districts=ds,section=section,subsection=subsection,parcels=parcels,area_m2=float(Decimal(area.replace(',',''))),note=note,facility_type='ancillary' if ancillary else 'unclassified',status='approved',construction_status='unverified',geometry=None,location_accuracy='unlocated',source_id='approved-2026-09-09',source_page=page_no,source_date='2026-09-09',checked_on='2026-11-27',image_checked_on=None))
assert sorted(r['source_number'] for r in records)==list(range(1,800))
dump('approved.json',records)
stats=list(csv.DictReader((ROOT/'data/sources/district-statistics.csv').read_text(encoding='utf-8-sig').lstrip('\ufeff').splitlines()))
areas={clean(r['行政區別']):float(r['面積（平方公里）']) for r in csv.DictReader((ROOT/'data/sources/district-areas-2023-09.csv').read_text(encoding='utf-8-sig').lstrip('\ufeff').splitlines())}
districts=[]
for row in stats:
 d=row['行政區']
 if d=='總計':continue
 matches=[r for r in records if d in r['districts']]; single=[r for r in matches if len(r['districts'])==1]; nonanc=[r for r in single if r['facility_type']!='ancillary']; area=sum(Decimal(str(r['area_m2'])) for r in nonanc)
 districts.append(dict(name=d,code=row['地址-行政區域代碼'],approval_count=int(row['總件數[統計]']),capacity_kwp=float(row['裝置容量kWp']),district_area_km2=areas[d],register_count=len(matches),cross_district_count=len(matches)-len(single),ancillary_count=sum(r['facility_type']=='ancillary' for r in matches),register_nonancillary_area_m2=float(area),register_area_ratio_pct=float(area)/ (areas[d]*1e6)*100,sections=sorted({r['section'] for r in matches}),coverage_status='register_compared_spatial_pending'))
assert len(districts)==37
assert sum(d['approval_count'] for d in districts)==13357
assert abs(sum(d['capacity_kwp'] for d in districts)-4809584.763)<0.01
dump('districts.json',districts)
with (ROOT/'data/approved.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['清冊編號','申請人（照錄）','行政區','地段','小段','地號','清冊面積m2','備註','狀態','施工核對','PDF頁次'])
 for r in records:w.writerow([r['source_number'],r['applicant'],'；'.join(r['districts']),r['section'],r['subsection'],r['parcels'],r['area_m2'],r['note'],'已核准','未查證',r['source_page']])
metadata=json.loads((ROOT/'data/source-registry.json').read_text()); metadata['hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data/sources').iterdir() if p.is_file()}; dump('source-manifest.json',metadata)
print(json.dumps({'records':len(records),'districts':len(districts),'cross_district':[r for r in records if len(r['districts'])>1],'ancillary':sum(r['facility_type']=='ancillary' for r in records)},ensure_ascii=False))
