#!/usr/bin/env python3
"""V3 KI-Vorschau: für die besten Interessenten ohne Vorschau eine Vorschau-Website bauen (noindex) und den Link eintragen.

Aufruf:  python3 sites/vorschau_ki.py [--anzahl 3]        (läuft nachts per GitHub Action „Nachtschicht“)
Quelle sind nur öffentliche Angaben: Google-Profil-Daten aus „interessenten“ und der Text der bisherigen Website.
Keine fremden Fotos, keine erfundenen Fakten; die Vorschau ist als solche gekennzeichnet und nicht in Suchmaschinen.
Ergebnis: vorschauen/<slug>-<zufall>/ (kunde.json + vorschau/) → wird mit der Agentur-Website unter /v/… veröffentlicht.
"""
import json, re, secrets, sys, urllib.request, html as H
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ki, generator  # noqa: E402

ZIEL = ki.ROOT / "vorschauen"
DOMAIN = json.loads((ki.ROOT / "config.json").read_text())["domain"].rstrip("/")
VORLAGE = [("friseur", "friseur"), ("barber", "barber"), ("dach", "dachdecker-solar"), ("solar", "dachdecker-solar"), ("steuer", "steuerberater"),
           ("pflege", "pflegedienst"), ("bestatt", "bestatter"), ("tierarzt", "tierarzt"), ("tierärzt", "tierarzt")]


def seitentext(url, max_zeichen=24000):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Lotwerk-Vorschau)"})
        roh = urllib.request.urlopen(req, timeout=20).read(2_000_000).decode("utf-8", "ignore")
    except Exception:
        return ""
    roh = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", roh)
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", roh))).strip()[:max_zeichen]


def main():
    n = int(sys.argv[sys.argv.index("--anzahl") + 1]) if "--anzahl" in sys.argv else 3
    liste = ki.db(f"interessenten?select=id,name,branche,ort,telefon,website_alt,bewertung,bewertungen_anzahl,befund&vorschau_url=is.null&status=eq.neu&potenzial=gte.50&order=potenzial.desc&limit={n}")
    for i in liste:
        text = seitentext(i["website_alt"]) if i.get("website_alt") else ""
        angaben = {"betrieb": i["name"], "branche": i.get("branche"), "ort": i.get("ort"), "telefon": i.get("telefon"),
                   "google_bewertung": i.get("bewertung"), "anzahl_bewertungen": i.get("bewertungen_anzahl"), "text_der_bisherigen_website": text or "keine Website"}
        try:
            inhalt, info = ki.texte(angaben, "\nDies ist eine unverbindliche Vorschau für ein Erstgespräch. Lass unbekannte optionale Angaben weg statt [PRÜFEN] zu schreiben.")
        except Exception as ex:
            print("übersprungen:", i["name"], ex); continue
        br = (i.get("branche") or "").lower()
        k = {"slug": ki.slugify(i["name"]), "branche": i.get("branche") or "", "vorlage": next((v for s, v in VORLAGE if s in br), "dachdecker-solar"),
             "firma": {"name": i["name"], "telefon": i.get("telefon"), "adresse": {"ort": i.get("ort")}},
             "vertrauen": {"bewertung": i.get("bewertung"), "bewertungen": i.get("bewertungen_anzahl"), "quelle": "Google"} if i.get("bewertungen_anzahl") else {},
             "formular": {}, **ki.als_kunde_json(inhalt)}
        ordner = ZIEL / f"{k['slug']}-{secrets.token_hex(3)}"
        ordner.mkdir(parents=True)
        (ordner / "kunde.json").write_text(json.dumps(k, ensure_ascii=False, indent=1), encoding="utf-8")
        generator.bauen(ordner, vorschau=True)
        url = f"{DOMAIN}/v/{ordner.name}/"
        ki.db(f"interessenten?id=eq.{i['id']}", "PATCH", {"vorschau_url": url}, "return=minimal")
        ki.protokoll("vorschau", info, f"Vorschau {i['name']}: {url}", interessent_id=i["id"])
        print("Vorschau:", i["name"], "→", url)


if __name__ == "__main__":
    main()
