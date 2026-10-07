"""Gemeinsame Helfer für die KI-Skripte (E2 Texte, V3 Vorschau): Claude-Aufruf mit festem Antwortformat, Supabase-Zugriff, Kostenprotokoll.
Schlüssel kommen aus Umgebungsvariablen: ANTHROPIC_API_KEY, SUPABASE_SERVICE_KEY (nur lokal bzw. als GitHub-Secret, nie im Code)."""
import json, os, re, sys, urllib.request
from pathlib import Path
from typing import List, Optional, Tuple

import anthropic
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
SB = json.loads((ROOT / "config.json").read_text())["supabase_url"]
MODELL = "claude-opus-5-5"
sys.path.insert(0, str(ROOT))
import vorschau as V  # noqa: E402

ICONS = sorted(V._I)

# ------------------------------------------------------------------ Antwortformat (wird von Claude exakt eingehalten)
class Seo(BaseModel):
    title: str = Field(description="Seitentitel, max. 60 Zeichen, Leistung + Ort + Betrieb")
    description: str = Field(description="Meta-Beschreibung, 120–155 Zeichen")

class Hero(BaseModel):
    eb: str = Field(description="kurze Zeile über der Überschrift, z. B. 'Dachdecker-Meisterbetrieb in Bielefeld'")
    h1: str = Field(description="Hauptüberschrift, konkret, max. 8 Wörter, keine Floskeln")
    lead: str = Field(description="1–2 Sätze: was, für wen, wo, warum")
    chips: List[str] = Field(description="2–3 kurze belegte Fakten (z. B. 'Meisterbetrieb seit 1987'); leer, wenn nichts belegt")

class Frage(BaseModel):
    frage: str
    antwort: str

class Schritt(BaseModel):
    titel: str
    text: str

class OrtText(BaseModel):
    ort: str
    text: str = Field(description="2 Absätze mit echten, ortsbezogenen Aussagen aus den Angaben")

class Leistung(BaseModel):
    slug: str
    titel: str
    icon: str = Field(description="eines von: " + ", ".join(ICONS))
    kurz: str = Field(description="ein Satz")
    text: str = Field(description="2–4 Absätze, getrennt durch Leerzeile; nur belegte Fakten")
    punkte: List[str]
    faq: List[Frage]
    seo_description: str
    ortstexte: List[OrtText] = Field(description="nur für Orte aus dem Einzugsgebiet, zu denen es echte, unterschiedliche Aussagen gibt; sonst leer")

class Ueber(BaseModel):
    h2: str
    text: str
    punkte: List[str]

class Inhalt(BaseModel):
    seo: Seo
    hero: Hero
    cta: str = Field(description="Text des Hauptknopfs, z. B. 'Angebot anfordern'")
    leistungen_h2: str
    leistungen: List[Leistung]
    ueber: Optional[Ueber]
    ablauf: List[Schritt]
    faq: List[Frage]
    kontakt_h2: str
    kontakt_text: str
    ueber_kurz: str = Field(description="ein Satz für den Fußbereich")
    offene_fragen: List[str] = Field(description="was fehlt oder unklar ist und beim Kunden erfragt werden muss")

REGELN = """Du schreibst Website-Texte für einen lokalen Betrieb in Deutschland (Sie-Form, klar, konkret, ohne Marketing-Floskeln und Superlative).
Harte Regeln:
- Verwende ausschließlich Fakten aus den gelieferten Angaben. Erfinde keine Zahlen, Jahre, Zertifikate, Preise, Namen, Bewertungen oder Zitate.
- Fehlt eine Angabe, die ein Text braucht, schreibe genau „[PRÜFEN]“ an die Stelle und nimm die Frage in „offene_fragen“ auf.
- Lokale Suchmaschinen- und KI-Sichtbarkeit: Leistung und Ort natürlich nennen, Fragen so beantworten, wie Kunden sie stellen.
- Kurze Sätze. Keine Wiederholungen zwischen den Seiten.
- Keine Werbe- und KI-Floskeln: nicht „maßgeschneidert“, „ganzheitlich“, „aus einer Hand“, „Ihr Partner für …“, „mit Leidenschaft“, „ehrlich“, „echt“,
  „Mehrwert“, „innovativ“, „nahtlos“, „auf das nächste Level“, „in der heutigen Zeit“, „nicht nur …, sondern auch“. Keine Dreier-Aufzählungen als Stilmittel.
- Gedankenstriche nicht als Satzverbinder benutzen; lieber Punkt, Komma oder Doppelpunkt."""


def client():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY fehlt (als Umgebungsvariable bzw. GitHub-Secret setzen).")
    return anthropic.Anthropic(timeout=600)


def texte(angaben: dict, zusatz: str = "") -> Tuple[Inhalt, dict]:
    """Ein Aufruf → strukturierter Inhalt. Bei Ablehnung springt automatisch das empfohlene Ersatzmodell ein (fallbacks)."""
    r = client().messages.parse(
        model=MODELL, max_tokens=16000, system=REGELN + zusatz,
        output_config={"effort": "high"}, output_format=Inhalt,
        extra_headers={"anthropic-beta": "server-side-fallback-2026-07-01"}, extra_body={"fallbacks": "default"},
        messages=[{"role": "user", "content": "Angaben des Betriebs (JSON):\n" + json.dumps(angaben, ensure_ascii=False, indent=1)}],
    )
    if r.stop_reason == "refusal" or r.parsed_output is None:
        raise RuntimeError(f"Keine Texte erhalten (stop_reason={r.stop_reason}).")
    kosten = (r.usage.input_tokens * 4 + r.usage.output_tokens * 20) / 1e6 * 0.92
    return r.parsed_output, {"modell": r.model, "tokens_ein": r.usage.input_tokens, "tokens_aus": r.usage.output_tokens, "kosten_eur": round(kosten, 4)}


def slugify(s):
    s = s.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:48]


# ------------------------------------------------------------------ Supabase (Service-Schlüssel nur aus der Umgebung)
def db(pfad, methode="GET", daten=None, prefer=None):
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not key:
        sys.exit("SUPABASE_SERVICE_KEY fehlt.")
    h = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    if prefer: h["Prefer"] = prefer
    req = urllib.request.Request(f"{SB}/rest/v1/{pfad}", method=methode, headers=h, data=json.dumps(daten).encode() if daten is not None else None)
    with urllib.request.urlopen(req, timeout=30) as r:
        t = r.read().decode()
        return json.loads(t) if t else None


def protokoll(art, info, zusammenfassung, **bezug):
    try:
        db("ki_laeufe", "POST", {"art": art, "status": "wartet", "zusammenfassung": zusammenfassung[:300], **info, **bezug}, "return=minimal")
    except Exception as ex:
        print("Hinweis: Protokoll nicht gespeichert:", ex)


def als_kunde_json(i: Inhalt) -> dict:
    """Strukturierten Inhalt in das kunde.json-Format des Generators übersetzen."""
    d = i.model_dump()
    for l in d["leistungen"]:
        l["faq"] = [[f["frage"], f["antwort"]] for f in l["faq"]]
        l["ortstexte"] = {o["ort"]: o["text"] for o in l["ortstexte"]}
        if l["icon"] not in ICONS: l["icon"] = "check"
        l["slug"] = slugify(l["slug"] or l["titel"])
    d["ablauf"] = [[s["titel"], s["text"]] for s in d["ablauf"]]
    d["faq"] = [[f["frage"], f["antwort"]] for f in d["faq"]]
    if not d.get("ueber"): d.pop("ueber", None)
    return d
