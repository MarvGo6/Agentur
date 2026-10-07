#!/usr/bin/env python3
"""E2 KI-Texte: aus dem Inhalte-Formular des Kunden die Website-Texte schreiben und in kunden/<slug>/kunde.json eintragen.

Aufruf:  python3 sites/ki_texte.py kunden/<slug> --token <Inhalte-Token>     (liest das Formular aus Supabase)
         python3 sites/ki_texte.py kunden/<slug> --inhalte angaben.json      (liest eine lokale Datei)
Danach:  python3 sites/generator.py kunden/<slug> && python3 sites/pruefung.py kunden/<slug>/dist
Fakten (Name, Adresse, Telefon, Zeiten) übernimmt das Skript wörtlich aus dem Formular – die KI schreibt nur die Texte.
Alles, was fehlt, steht als [PRÜFEN] im Text und in „_offene_fragen“. Ohne Freigabe geht nichts live.
"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ki  # noqa: E402

zeilen = lambda t: [x.strip(" -•\t") for x in re.split(r"[\n;]+", t or "") if x.strip(" -•\t")]


def adresse(t):
    m = re.search(r"^(.*?),?\s*(\d{5})\s+(.+)$", (t or "").replace("\n", ", ").strip())
    return {"strasse": m.group(1).strip(", "), "plz": m.group(2), "ort": m.group(3).strip()} if m else {"strasse": t or None}


def main():
    if len(sys.argv) < 4: sys.exit(__doc__)
    ordner = Path(sys.argv[1]); ordner.mkdir(parents=True, exist_ok=True)
    if sys.argv[2] == "--token":
        f = ki.db(f"inhalte_formulare?select=id,kunde_id,website_id,daten,dateien&token=eq.{sys.argv[3]}")[0]
        d, bezug = f["daten"] or {}, {"kunde_id": f["kunde_id"], "website_id": f["website_id"]}
    else:
        d, bezug = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8")), {}
    datei = ordner / "kunde.json"
    k = json.loads(datei.read_text(encoding="utf-8")) if datei.exists() else {"slug": ordner.name, "vorlage": "dachdecker-solar"}
    # Fakten 1:1 aus dem Formular
    k["firma"] = {**k.get("firma", {}), "name": d.get("betrieb") or k.get("firma", {}).get("name") or "[PRÜFEN]", "adresse": adresse(d.get("adresse")),
                  "telefon": d.get("telefon") or None, "email": d.get("email") or None, "oeffnungszeiten": zeilen(d.get("oeffnungszeiten"))}
    k["einzugsgebiet"] = [x.strip() for x in re.split(r"[,\n;]+", d.get("einzugsgebiet") or "") if x.strip()]
    if d.get("domain"): k["domain"] = d["domain"].replace("https://", "").replace("http://", "").strip("/")
    if d.get("team"): k["team"] = [{"name": z.split(",")[0].strip(), "rolle": ",".join(z.split(",")[1:]).strip()} for z in zeilen(d["team"])]
    if d.get("stellen"): k["recruiting"] = {**k.get("recruiting", {}), "aktiv": True, "stellen": zeilen(d["stellen"])}
    angaben = {k_: v for k_, v in d.items() if v and k_ not in ("bestaetigung",)}
    angaben["branche"] = k.get("branche") or "[aus den Leistungen ableiten]"
    inhalt, info = ki.texte(angaben)
    k.update(ki.als_kunde_json(inhalt))
    k["_offene_fragen"] = k.pop("offene_fragen", [])
    datei.write_text(json.dumps(k, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"kunde.json geschrieben ({info['tokens_aus']} Token, ca. {info['kosten_eur']:.2f} €). Offene Fragen: {len(k['_offene_fragen'])}")
    for q in k["_offene_fragen"]: print("  ?", q)
    if bezug:
        ki.protokoll("erstellung", info, f"Texte für {k['firma']['name']}: {len(k['_offene_fragen'])} offene Fragen", **bezug)


if __name__ == "__main__":
    main()
