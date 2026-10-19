"""Baut index.html aus data/notare.csv.

Koordinaten: Mittelpunkt der Postleitzahl (data/plz_geocoord.csv), Notare mit
gleicher PLZ werden leicht im Kreis verteilt, damit sie einzeln anklickbar sind.
Grundkarte: Kreisgrenzen der Regierungsbezirke Köln und Düsseldorf (data/kreise.geo.json).
"""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"


def load_plz():
    with open(DATA / "plz_geocoord.csv", encoding="utf-8") as f:
        return {r[""]: (float(r["lat"]), float(r["lng"])) for r in csv.DictReader(f)}


def load_notare(plz):
    with open(DATA / "notare.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    by_plz = defaultdict(list)
    for r in rows:
        by_plz[r["plz"]].append(r)
    out = []
    for code, group in by_plz.items():
        lat, lng = plz[code]
        for i, r in enumerate(group):
            if len(group) > 1:
                a = 2 * math.pi * i / len(group)
                lat_i = lat + 0.0025 * math.sin(a)
                lng_i = lng + 0.004 * math.cos(a)
            else:
                lat_i, lng_i = lat, lng
            out.append({
                "amt": r["amt"], "name": r["name"], "strasse": r["strasse"],
                "plz": r["plz"], "ort": r["ort"], "seite": int(r["seite"]),
                "lat": round(lat_i, 5), "lng": round(lng_i, 5),
            })
    out.sort(key=lambda r: (r["ort"], r["name"]))
    return out


def simplify_ring(ring, step=2):
    pts = ring[::step]
    if pts[-1] != ring[-1]:
        pts.append(ring[-1])
    return [[round(x, 3), round(y, 3)] for x, y in pts]


NAMEN = {"Cleves": "Kreis Kleve", "Cologne Städte": "Köln", "Aachen": "Städteregion Aachen",
         "Aachen Städte": "Aachen", "Mülheim Städte": "Mülheim an der Ruhr", "Rhein-Sieg": "Rhein-Sieg-Kreis",
         "Mettmann": "Kreis Mettmann", "Wesel": "Kreis Wesel", "Viersen": "Kreis Viersen",
         "Heinsberg": "Kreis Heinsberg", "Düren": "Kreis Düren", "Euskirchen": "Kreis Euskirchen"}


def kreis_name(raw):
    return NAMEN.get(raw, raw.removesuffix(" Städte"))


def load_kreise():
    geo = json.load(open(DATA / "kreise.geo.json", encoding="utf-8"))
    feats = []
    for f in geo["features"]:
        p = f["properties"]
        if p["NAME_1"] != "Nordrhein-Westfalen" or p["NAME_2"] not in ("Köln", "Düsseldorf"):
            continue
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        coords = [[simplify_ring(r) for r in poly] for poly in polys]
        feats.append({
            "type": "Feature",
            "properties": {"name": kreis_name(p["NAME_3"]), "bezirk": p["NAME_2"]},
            "geometry": {"type": "MultiPolygon", "coordinates": coords},
        })
    return {"type": "FeatureCollection", "features": feats}


def main():
    notare = load_notare(load_plz())
    kreise = load_kreise()
    tpl = (ROOT / "template.html").read_text(encoding="utf-8")
    html = (tpl.replace("/*NOTARE*/[]", json.dumps(notare, ensure_ascii=False))
               .replace("/*KREISE*/{}", json.dumps(kreise, separators=(",", ":"))))
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    print(f"{len(notare)} Notare, {len(kreise['features'])} Kreise -> index.html ({len(html)//1024} KB)")


if __name__ == "__main__":
    main()
