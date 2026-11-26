# 臺南市太陽光電開發全域監測地圖

原網址： https://maskywg.github.io/tainan-solar-map/ 。無建置步驟，GitHub Pages main 分支根目錄部署。

本版完成37區公開統計與799筆官方核准清冊整理；不是所有設備的實地普查或已設置面積調查。地號未定位者沒有生成案場座標；地圖上的9組原站重點位置僅為示意。官方行政區多邊形支援核准容量／清冊筆數設色、點選與資料庫聯動，設色不代表設施覆蓋。

## 資料

- `data/approved.json`：2026-09-09清冊799筆，含21筆明列附屬設施、2筆跨區案件，全部施工狀態未核實。
- `data/pending.json`：28件審查中未核准資料；原始來源遮名，未提供行政區、地段地號，不嘗試反推。
- `data/districts.json`：全市37區核准統計，與小案清冊面積分開。核准統計CSV未註明統計截止日，metadata更新日不等於統計截止日。
- `data/history.json`：2025-11-27（826筆）、2026-03-05（818筆）、2026-09-09（799筆）完整快照。跨版匹配依文字鍵值，不視為開工、拆除或新增設施。
- `data/tainan-districts.geojson`：國土測繪中心1140318版行政界，網頁展示用簡化，非地籍界址。
- `data/sources/`：官方PDF、CSV及未核准表格摘錄；界線來源資訊含上游ZIP校驗。
- `data/source-registry.json`：宣告資料來源；`source-manifest.json`另包含本機來源檔SHA-256。
- `legacy.html`、`data/legacy-zones.json`、`og-preview.png`：原站保留存檔，不以其內容作現況查證證據。

面積圖表扣除明列附屬設施、排除不能分區的跨區案件。尚未完成地籍聯集及同址去重；列載面積或其與行政區面積的比值，均不可當成實際光電覆蓋面積或占比。跨區涉及筆數可在各區各出現一次，不能直接合計全市件數。

## 重建與驗證

Python需要pdfplumber；影像驗證需Pillow。只重建資料即可，網站不需Python執行環境。

```sh
python3 scripts/build_pending.py
python3 scripts/build_history.py
python3 scripts/build_data.py
python3 scripts/validate.py
node --check app.js
python3 -m http.server 8765 --bind 127.0.0.1
```

行政界轉檔需pyshp及shapely。依`data/sources/boundaries-source.json`下載官方ZIP後執行：

```sh
python3 scripts/build_boundaries.py /path/to/towns.zip
python3 scripts/build_data.py
```

MapLibre GL JS 5.24.0已隨站保存（BSD-3-Clause，見vendor授權）。衛星、正射影像、WMS界線／段籍／坡度及全球DEM仍需網路；資料查詢與已保存的行政界不依賴這些圖磚服務。任何外部服務失敗均應顯示狀態，保留資料庫可用。

## 尚未完成

逐筆地籍定位、施工及歷史影像查核；全量屋頂／停車棚及2公頃以上案場整合；環評逐案關聯；集水區與環境敏感區套疊。透明與協力行動平台的設備查詢路徑本次回傳「無瀏覽權限」。完成這些之前，不應將本版宣稱為「全市所有設施已完整掌握」。

本次瀏覽器檢查涵蓋南化11筆、新化25筆與知母義段查詢、21筆附屬篩選、28件未核准、PDF詳情、分頁、3D地形、37區設色與390px手機版溢位檢查。來源查閱及頁面更新日期：2026-11-27（Asia/Taipei）。
