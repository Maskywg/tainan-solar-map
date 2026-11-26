"""Re-extract the 28 masked pending applications from the preserved official table."""
from html.parser import HTMLParser
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
class Tables(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None
 def handle_starttag(self,t,a):
  if t=='tr':self.row=[]
  if t in ['td','th']:self.cell=''
 def handle_data(self,s):
  if self.cell is not None:self.cell+=s
 def handle_endtag(self,t):
  if t in ['td','th'] and self.row is not None and self.cell is not None:self.row.append(self.cell.strip());self.cell=None
  if t=='tr' and self.row:self.rows.append(self.row);self.row=None
p=Tables();p.feed((root/'data/sources/pending-2026-09-09.html').read_text())
rows=[r for r in p.rows if len(r)==4 and r[0].isdigit()];assert len(rows)==28
out=[dict(number=int(r[0]),applicant=r[1],application_date_roc=r[2],review_status=r[3],districts=[],status='pending',geometry=None,source_date='2026-09-09',source_url='https://economic.tainan.gov.tw/news_content.aspx?n=37460&s=7948121') for r in rows]
(root/'data/pending.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('28 pending applications rebuilt')
