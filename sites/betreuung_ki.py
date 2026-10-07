#!/usr/bin/env python3
"""Monatliche Betreuung mit KI (läuft am 1. per GitHub Action „Betreuung“). Alles landet als Entwurf zur Freigabe in der Steuerzentrale.

  python3 sites/betreuung_ki.py beitraege       B3: 4 Google-Profil-Beiträge je Kunde (SEO/Programm) → entwuerfe
  python3 sites/betreuung_ki.py sichtbarkeit    B7: Fragt mit Websuche „beste/r <Branche> in <Ort>“ – wird der Kunde genannt? → messwerte ki_genannt
  python3 sites/betreuung_ki.py verbesserungen  B5: höchstens 3 Textverbesserungen je Kunde als Pull Request mit Vorschau

Quelle sind kunden/<slug>/kunde.json (Inhalte) und Supabase (Websites, Verträge, Messwerte).
Umgebung: ANTHROPIC_API_KEY, SUPABASE_SERVICE_KEY; für Pull Requests zusätzlich GH_TOKEN (in der Action automatisch).
"""
import json, re, subprocess, sys
from datetime import date
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ki  # noqa: E402

KUNDEN = ki.ROOT / "kunden"
FALLBACK = {"extra_headers": {"anthropic-beta": "server-side-fallback-2026-07-01"}, "extra_body": {"fallbacks": "default"}}


def kunden_mit_website():
    """kunde.json je Domain, verknüpft mit der Website-Zeile in Supabase (nur live)."""
    live = {w["domain"]: w for w in ki.db("websites?select=id,domain,kunde_id,kunden(firma,vertraege(produkt,ende))&status=eq.live")}
    for f in sorted(KUNDEN.glob("*/kunde.json")):
        if f.parent.name.startswith("_"): continue
        k = json.loads(f.read_text(encoding="utf-8"))
        w = live.get(k.get("domain"))
        if w: yield f.parent, k, w


def aktive_produkte(w):
    return {v["produkt"] for v in ((w.get("kunden") or {}).get("vertraege") or []) if not v.get("ende")}


# ------------------------------------------------------------------ B3 Google-Profil-Beiträge
class Beitrag(BaseModel):
    titel: str = Field(description="interner Titel, 3–6 Wörter")
    text: str = Field(description="80–150 Wörter, konkret, ein Thema, Handlungsaufruf am Ende; nur Fakten aus den Angaben")
    foto_idee: str = Field(description="welches Foto aus dem Betrieb dazu passt")

class Beitraege(BaseModel):
    beitraege: List[Beitrag]


def beitraege():
    monat = date.today().strftime("%B %Y")
    for ordner, k, w in kunden_mit_website():
        if not aktive_produkte(w) & {"seo_lokal", "seo_plus", "programm"}: continue
        angaben = {"betrieb": k["firma"]["name"], "branche": k.get("branche"), "ort": (k["firma"].get("adresse") or {}).get("ort"), "monat": monat,
                   "leistungen": [{"titel": l["titel"], "kurz": l.get("kurz")} for l in k.get("leistungen", [])], "einzugsgebiet": k.get("einzugsgebiet")}
        r = ki.client().messages.parse(model=ki.MODELL, max_tokens=6000, output_format=Beitraege, output_config={"effort": "medium"}, **FALLBACK,
            system="Du schreibst Google-Unternehmensprofil-Beiträge für einen lokalen Betrieb (Sie-Form). Vier Beiträge zu verschiedenen Leistungen oder saisonalen Anlässen des Monats. "
                   "Keine erfundenen Angebote, Preise, Rabatte oder Zahlen. Keine Telefonnummern im Text.",
            messages=[{"role": "user", "content": json.dumps(angaben, ensure_ascii=False)}])
        if r.parsed_output is None: continue
        for b in r.parsed_output.beitraege[:4]:
            ki.db("entwuerfe", "POST", {"art": "profil_beitrag", "website_id": w["id"], "kunde_id": w["kunde_id"], "titel": f"{k['firma']['name']}: {b.titel}",
                                        "text": b.text, "meta": {"foto_idee": b.foto_idee, "monat": monat}}, "return=minimal")
        print("Beiträge:", k["firma"]["name"])


# ------------------------------------------------------------------ B7 KI-Sichtbarkeit
def sichtbarkeit():
    heute = date.today().isoformat()
    for ordner, k, w in kunden_mit_website():
        ort = (k["firma"].get("adresse") or {}).get("ort")
        if not ort or not k.get("branche"): continue
        frage = f"Welche {k['branche']} in {ort} kannst du empfehlen? Nenne die drei besten mit kurzer Begründung."
        nachrichten = [{"role": "user", "content": frage}]
        for _ in range(4):                                     # pause_turn bei langen Websuchen fortsetzen
            r = ki.client().messages.create(model=ki.MODELL, max_tokens=4000, output_config={"effort": "low"}, messages=nachrichten,
                                            tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 5, "user_location": {"type": "approximate", "country": "DE", "city": ort}}], **FALLBACK)
            if r.stop_reason != "pause_turn": break
            nachrichten.append({"role": "assistant", "content": r.content})
        text = " ".join(b.text for b in r.content if b.type == "text")
        name = re.sub(r"\b(gmbh|ug|e\.k\.|ohg|kg|&|und)\b", " ", k["firma"]["name"].lower())
        genannt = any(t in text.lower() for t in [name.strip(), *[x for x in name.split() if len(x) > 4]])
        ki.db("messwerte?on_conflict=website_id,datum,kennzahl", "POST", {"website_id": w["id"], "datum": heute, "kennzahl": "ki_genannt", "wert": 1 if genannt else 0},
              "resolution=merge-duplicates,return=minimal")
        print("KI-Sichtbarkeit:", k["firma"]["name"], "genannt" if genannt else "nicht genannt")


# ------------------------------------------------------------------ B5 Verbesserungen als Pull Request
class Aenderung(BaseModel):
    feld: str = Field(description="Pfad in kunde.json, z. B. 'seo.description', 'hero.lead', 'leistungen.<slug>.text', 'leistungen.<slug>.seo_description'")
    neu: str
    begruendung: str = Field(description="ein Satz: welches Problem das löst (Messwert oder Prüfhinweis nennen)")

class Vorschlaege(BaseModel):
    aenderungen: List[Aenderung] = Field(description="höchstens 3; leer, wenn nichts Sinnvolles zu verbessern ist")

ERLAUBT = re.compile(r"^(seo\.(title|description)|hero\.(h1|lead)|leistungen\.[a-z0-9-]+\.(text|kurz|seo_description))$")


def setzen(k, feld, wert):
    teile = feld.split(".")
    if teile[0] == "leistungen":
        l = next((x for x in k.get("leistungen", []) if x["slug"] == teile[1]), None)
        if not l: return False
        l[teile[2]] = wert; return True
    k.setdefault(teile[0], {})[teile[1]] = wert; return True


def verbesserungen():
    sys.path.insert(0, str(ki.ROOT / "sites")); import generator, pruefung
    for ordner, k, w in kunden_mit_website():
        dist, _ = generator.bauen(ordner)
        hinweise = [f["text"] + " (" + f["seite"] + ")" for f in pruefung.pruefen(dist)["funde"]][:15]
        mw = ki.db(f"messwerte?select=datum,kennzahl,wert&website_id=eq.{w['id']}&order=datum.desc&limit=60")
        r = ki.client().messages.parse(model=ki.MODELL, max_tokens=8000, output_format=Vorschlaege, output_config={"effort": "high"}, **FALLBACK,
            system=ki.REGELN + "\nSchlage höchstens drei Textänderungen vor, die Auffindbarkeit oder Anfragen verbessern. Nur Felder mit diesen Pfaden: seo.title, seo.description, "
                   "hero.h1, hero.lead, leistungen.<slug>.text|kurz|seo_description. Keine neuen Fakten.",
            messages=[{"role": "user", "content": json.dumps({"kunde": k, "pruefhinweise": hinweise, "messwerte": mw}, ensure_ascii=False)}])
        aend = [a for a in (r.parsed_output.aenderungen if r.parsed_output else []) if ERLAUBT.match(a.feld)][:3]
        if not aend: continue
        for a in aend: setzen(k, a.feld, a.neu)
        ast = f"verbesserung/{ordner.name}-{date.today():%Y-%m}"
        subprocess.run(["git", "checkout", "-B", ast], check=True)
        (ordner / "kunde.json").write_text(json.dumps(k, ensure_ascii=False, indent=1), encoding="utf-8")
        subprocess.run(["git", "commit", "-am", f"{k['firma']['name']}: {len(aend)} Verbesserungsvorschläge ({date.today():%B %Y})"], check=True)
        subprocess.run(["git", "push", "-f", "-u", "origin", ast], check=True)
        text = "\n".join(f"- **{a.feld}**: {a.begruendung}" for a in aend) + "\n\nVorschau: siehe Vercel-Vorschau dieses Pull Requests. Erst nach Freigabe zusammenführen."
        subprocess.run(["gh", "pr", "create", "--title", f"{k['firma']['name']}: Verbesserungen {date.today():%m/%Y}", "--body", text, "--head", ast], check=False)
        ki.db("entwuerfe", "POST", {"art": "verbesserung", "website_id": w["id"], "kunde_id": w["kunde_id"], "titel": f"{k['firma']['name']}: Pull Request {ast}",
                                    "text": text}, "return=minimal")
        subprocess.run(["git", "checkout", "main"], check=True)
        print("Verbesserungen:", k["firma"]["name"], len(aend))


if __name__ == "__main__":
    {"beitraege": beitraege, "sichtbarkeit": sichtbarkeit, "verbesserungen": verbesserungen}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: sys.exit(__doc__))()
