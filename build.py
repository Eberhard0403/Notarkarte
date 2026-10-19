"""Baut index.html aus data/notare_alle.csv.

Aufgenommen werden Einträge mit der Amtsbezeichnung "Notar" oder "Notarin" sowie
Notariatsverwalter/innen im Gebiet der reinen Notare. Dieses Gebiet ergibt sich aus den
Daten selbst: Orte, in denen Anwaltsnotare sitzen, gehören zum Anwaltsnotariat.
Verwalter, die schon als Notar/in auf der Karte stehen, werden nicht doppelt aufgenommen.

Koordinaten: Mittelpunkt der Postleitzahl (data/plz_geocoord.csv). Notare mit
gleicher PLZ werden spiralförmig um den Mittelpunkt verteilt, damit jeder
einzeln anklickbar ist.
Grundkarte: Kreisgrenzen der Regierungsbezirke Köln und Düsseldorf (data/kreise.geo.json).
"""
import csv
import json
import math
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
NUR_NOTAR = {"Notar", "Notarin"}
VERWALTER = {"Notariatsverwalter", "Notariatsverwalterin"}


def stadt(ort):
    """Grundname eines Ortes: "Wesel am Rhein" -> "Wesel", "Duisburg-Hamborn" -> "Duisburg"."""
    return re.split(r"[-,(]| am | an der ", ort)[0].strip()


def load_plz():
    with open(DATA / "plz_geocoord.csv", encoding="utf-8") as f:
        return {r[""]: (float(r["lat"]), float(r["lng"])) for r in csv.DictReader(f)}


def slug(text):
    text = unicodedata.normalize("NFKD", text.replace("ß", "ss")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def load_notare(plz):
    with open(DATA / "notare_alle.csv", encoding="utf-8") as f:
        alle = list(csv.DictReader(f, delimiter=";"))
    anwaltsorte = {stadt(r["ort"]) for r in alle if r["amt"].startswith("Rechtsanw")}
    rows = [r for r in alle if r["amt"] in NUR_NOTAR]
    notar_namen = {r["name"] for r in rows}
    rows += [r for r in alle if r["amt"] in VERWALTER
             and stadt(r["ort"]) not in anwaltsorte and r["name"] not in notar_namen]
    by_plz = defaultdict(list)
    for r in rows:
        by_plz[r["plz"]].append(r)
    out = []
    for code, group in by_plz.items():
        lat, lng = plz[code]
        group.sort(key=lambda r: r["strasse"])
        for i, r in enumerate(group):
            # Sonnenblumen-Spirale: gleichmäßiger Abstand auch bei vielen Notaren je PLZ
            rad, ang = 0.0011 * math.sqrt(i), i * 2.39996
            out.append({
                "id": f"{code}-{slug(r['name'])}"[:120],
                "amt": r["amt"], "name": r["name"], "strasse": r["strasse"],
                "plz": code, "ort": r["ort"],
                "lat": round(lat + rad * math.sin(ang), 5),
                "lng": round(lng + 1.55 * rad * math.cos(ang), 5),
            })
    ids = [n["id"] for n in out]
    assert len(ids) == len(set(ids)), "doppelte IDs"
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
