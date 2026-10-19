# Notarkarte Rheinland

Interaktive Karte der Notarinnen und Notare im Kammerbezirk Rheinland (Quelle: Notarsuche auf notar.de, 409 Treffer).
Auf der Karte stehen nur Einträge mit der Amtsbezeichnung „Notar“ oder „Notarin“ (288) – keine Anwaltsnotare, keine Notariatsverwaltungen.

- `data/notare_alle.csv` – alle 409 Einträge (per Texterkennung aus den Screenshots, `pdf_seite` = Seite im PDF)
- `data/plz_geocoord.csv` – PLZ-Mittelpunkte (WZBSocialScienceCenter/plz_geocoord)
- `data/kreise.geo.json` – Kreisgrenzen (isellsoap/deutschlandGeoJSON)
- `template.html` + `build.py` → `index.html`

Eigene Angaben (Geburtsdatum, Telefon, E-Mail, Notiz) werden in der veröffentlichten Karte gespeichert, nicht in diesem Repository.
