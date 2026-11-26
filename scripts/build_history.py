import json,re
from pathlib import Path
from decimal import Decimal
import pdfplumber
root=Path(__file__).resolve().parents[1]
versions=[]
for date in ['2025-11-27','2026-03-05','2026-09-09']:
 records=[]
 with pdfplumber.open(root/f'data/sources/approved-{date}.pdf') as pdf:
  for pno,p in enumerate(pdf.pages,1):
   for t in p.extract_tables():
    for row in t:
     if row[0] and row[0].isdigit():
      row=[re.sub(r'\s+','',s or '') for s in row]
      records.append(dict(number=int(row[0]),applicant=row[1],district=row[2],section=row[3],subsection=row[4],parcels=row[5],area_m2=float(Decimal(row[6].replace(',',''))),note=row[7],page=pno))
 ids=[r['number'] for r in records]; assert len(ids)==len(set(ids)) and sorted(ids)==list(range(1,max(ids)+1))
 versions.append({'date':date,'count':len(records),'listed_area_ha':sum(r['area_m2'] for r in records)/10000,'file':f'data/sources/approved-{date}.pdf','records':records})
(root/'data/history.json').write_text(json.dumps(versions,ensure_ascii=False,indent=2)+'\n')
print([(x['date'],x['count']) for x in versions])
