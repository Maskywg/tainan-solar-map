"""Convert the official 1140318 town SHP snapshot into a Tainan-only web GeoJSON.
Requires pyshp and shapely; source ZIP may be supplied as first argument.
"""
import sys,json,zipfile,io,hashlib
from pathlib import Path
import shapefile
from shapely.geometry import shape,mapping
root=Path(__file__).resolve().parents[1]
zpath=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/tainan-towns.zip')
z=zipfile.ZipFile(zpath);base='TOWN_MOI_1140318'
r=shapefile.Reader(shp=io.BytesIO(z.read(base+'.shp')),shx=io.BytesIO(z.read(base+'.shx')),dbf=io.BytesIO(z.read(base+'.dbf')),encoding=z.read(base+'.CPG').decode().strip())
features=[]
for item in r.iterShapeRecords():
 p=item.record.as_dict()
 if p['COUNTYNAME']!='臺南市':continue
 g=shape(item.shape.__geo_interface__);simplified=g.simplify(.00008,preserve_topology=True)
 features.append({'type':'Feature','properties':{k:p[k] for k in ['TOWNCODE','TOWNNAME','COUNTYNAME']},'geometry':mapping(simplified)})
assert len(features)==37
(root/'data/tainan-districts.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,separators=(',',':'))+'\n')
(root/'data/sources/boundaries-source.json').write_text(json.dumps({'title':'鄉(鎮、市、區)界線1140318','date':'2025-03-18','provider':'內政部國土測繪中心','dataset':'https://data.gov.tw/dataset/7441','download_url':'https://www.tgos.tw/tgos/VirtualDir/Product/3fe61d4a-ca23-4f45-8aca-4a536f40f290/鄉(鎮、市、區)界線1140318.zip','source_zip_sha256':hashlib.sha256(zpath.read_bytes()).hexdigest(),'license':'政府資料開放授權條款第1版','processing':'篩出臺南市37區；以0.00008度拓撲保留簡化作網頁展示，非權利界址。','checked_on':'2026-11-27'},ensure_ascii=False,indent=2)+'\n')
print('37 official district polygons,', (root/'data/tainan-districts.geojson').stat().st_size,'bytes')
