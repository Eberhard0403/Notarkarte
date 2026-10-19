# Notarkarte Rheinland

Interaktive Karte der Notarinnen und Notare im Kammerbezirk Rheinland (Quelle: Notarsuche auf notar.de).

- `data/notare.csv` – erfasste Einträge (Seite der Trefferliste, Amt, Name, Straße, PLZ, Ort)
- `data/plz_geocoord.csv` – PLZ-Mittelpunkte (WZBSocialScienceCenter/plz_geocoord)
- `data/kreise.geo.json` – Kreisgrenzen (isellsoap/deutschlandGeoJSON)
- `template.html` + `build.py` → `index.html`

Neue Einträge in `data/notare.csv` ergänzen, dann `python3 build.py`.
