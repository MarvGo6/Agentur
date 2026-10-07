"""Erzeugt betrieb/Automatisierungsplan.html und .pdf – welche Automatisierungen gebaut werden, in welcher Reihenfolge,
was sie an Stunden sparen und was sie kosten. Zahlen aus finanzen/modell.py (Variante "automatisiert ab Kunde 5").
Neu erzeugen: python3 betrieb/automatisierung.py"""
import sys, json, subprocess, os
from pathlib import Path
from datetime import date
ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "finanzen")); sys.path.insert(0, str(ROOT))
import modell as M
from content import eur

NAME = json.loads((ROOT / "config.json").read_text())["name"]
G = M.G
def e0(v): return eur(round(v))
def h(v): return f"{v:g}".replace(".", ",") + " h"
def tab(kopf, zeilen, cls=""): return f'<table class="{cls}"><thead><tr>' + "".join(f"<th>{k}</th>" for k in kopf) + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in z) + "</tr>" for z in zeilen) + "</tbody></table>"
def liste(xs): return "<ul>" + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"

# ------------------------------------------------------------------ Modell: von Hand vs. automatisiert
RES = {(n, v): M.rechne(n, variante=v) for n in M.SZENARIEN for v in M.VARIANTEN}
def kennz(n, v):
    r = RES[(n, v)]; z = M.zielmonat(r)
    return {"ziel": r[z - 1]["label"] if z else "–", "einmal": sum(x["einmal"] for x in r[:z]) if z else 0,
            "m12": r[11]["mrr"], "m24": r[23]["mrr"], "erg24": sum(x["ergebnis"] for x in r), "h12": r[11]["stunden"],
            "ab": next((x["label"] for x in r if x["auto"]), "–")}
K = {k: kennz(*k) for k in RES}
B0, B1 = K[("Basis", "hand")], K[("Basis", "auto")]
# Puffer: Automatisierung erst ab Kunde 10
SPAET = M.rechne("Basis", dict(G, auto_ab_kunde=10), variante="auto"); ZS = M.zielmonat(SPAET)
SPAET_AB = next(x["label"] for x in SPAET if x["auto"])

# ------------------------------------------------------------------ Die Automatisierungen
# id, name, was passiert (Auslöser → Ergebnis, Freigabe), Werkzeuge, spart, Bau (h), laufende Kosten, Status, Phase
A = [
 # Vertrieb
 ("V1", "Lead-Liste", "Wöchentlich (Mo) oder per Knopf: „20 Betriebe Dachdecker, Bielefeld“ → Name, Website, Telefon, Bewertungen in <i>interessenten</i>", "Google Places API, Supabase-Funktion", "1 h je Abschluss", 4, "Google-Kontingent, meist 0–10 €", "gebaut – Places-Schlüssel fehlt", 1),
 ("V2", "Website-Analyse", "Alle 30 Min. je 3 neue Interessenten → Potenzial 0–100 + Befund in Klartext (inkl. Cookie-/Impressum-Prüfung)", "Supabase-Funktion <i>analyse</i>, PageSpeed", "1 h je Abschluss", 0, "0 €", "läuft", 0),
 ("V3", "KI-Vorschau-Website", "Für Interessenten mit Potenzial ≥ 50: Claude erstellt <i>kunde.json</i> nur aus belegten Fakten (Rest [PRÜFEN]) → Generator → Vorschau-Link (noindex)", "Claude API, Generator, Vercel", "1 h je Abschluss", 14, "ca. 0,20–1 € je Vorschau", "gebaut – Claude-Schlüssel fehlt", 1),
 ("V4", "Nachricht & Nachfassen", "KI-Entwurf der Erstnachricht aus dem Befund; Erinnerung per Push an Tag 3 und 7; Status-Pflege in der Pipeline", "Claude API, ntfy, Supabase", "0,5 h je Abschluss", 4, "< 5 €", "läuft (Entwürfe mit Claude-Schlüssel)", 1),
 ("V5", "Angebot per Knopf", "Option wählen → Angebotsentwurf in Lexware + passende Präsentation; nach Annahme: Kunde + Verträge angelegt", "Lexware-Office-API, Supabase", "0,5 h je Abschluss", 5, "0 €", "später (Lexware)", 1),
 ("V6", "Anfragen-Push", "Jede Anfrage über deine Website sofort als Push aufs Handy", "Supabase-Trigger, ntfy", "–", 0, "0 €", "läuft", 0),
 # Erstellung
 ("E1", "Inhalte-Formular online", "Nach Auftrag: Link an den Kunden, Texte/Fotos/Leistungen hochladen, Erinnerung bei Frist (7 Tage) → Rohdaten in <i>kunde.json</i>", "Supabase (Formular + Speicher), E-Mail", "2 h je Website", 6, "0 €", "läuft", 1),
 ("E2", "KI-Texte", "Claude schreibt Startseite, Leistungs- und Ortsseiten, FAQ, Seitentitel aus Formular + Vorschau. Unbelegtes = [PRÜFEN], du prüfst", "Claude API", "5 h je Website", 8, "ca. 1–3 € je Website", "gebaut – Claude-Schlüssel fehlt", 1),
 ("E3", "Build- & Vorschau-Pipeline", "Repo <i>lotwerk-sites</i>: jede Änderung = Pull Request → Build → Vorschau-Link zur Freigabe", "GitHub Actions, Vercel", "4 h je Website", 12, "in Vercel Pro enthalten", "läuft", 0),
 ("E4", "Abnahme-Prüfung", "Bei jedem PR: Lighthouse, Barrierefreiheit, tote Links, Cookie-Check, Schema, kein [PRÜFEN] → Ergebnis im PR + <i>checks</i>", "GitHub Actions, Lighthouse, axe", "2 h je Website", 6, "0 €", "läuft", 0),
 ("E5", "Livegang per Knopf", "Domain anlegen, DNS setzen, SSL prüfen, Weiterleitungen, Website in die Überwachung", "Vercel-API, Cloudflare-API", "1 h je Website", 6, "0 €", "gebaut – Vercel-Token fehlt", 1),
 # Betrieb
 ("Ü1", "Überwachung", "Täglich Erreichbarkeit, montags PageSpeed; Ausbau: alle 5 Min. Erreichbarkeit, SSL-Ablauf, monatlicher Cookie-Check → Push + Aufgabe", "Supabase-Funktion <i>monitor</i>", "Pflege 0,25 → 0,1 h", 3, "0 €", "läuft", 1),
 ("Ü2", "Formular-Funktion für Kunden", "Zentrale Funktion für alle Kunden-Formulare: Spamschutz, E-Mail an den Kunden, Speicherung 90 Tage, Push bei Fehler", "Supabase-Funktion, Cloudflare Turnstile", "Pflicht vor Livegang", 5, "0 €", "läuft (Mail: Resend-Schlüssel)", 0),
 ("Ü3", "Löschfristen", "Anfragen nach 90 Tagen, Seitenaufrufe nach 25 Monaten automatisch löschen", "Supabase (Zeitplan)", "–", 1, "0 €", "läuft", 0),
 # Betreuung
 ("B1", "Messwerte-Sammler", "Monatlich je Kunde: Klicks/Impressionen, Anrufe/Routen aus dem Google-Profil, Besucher, Ads-Kennzahlen → <i>messwerte</i>", "Search Console API, Business Profile API, Plausible API", "Programm 1 h · SEO 0,5 h je Monat", 10, "0 €", "wartet auf Zugänge", 2),
 ("B2", "Monatsbericht je Kunde", "Claude schreibt eine Seite Klartext aus den Messwerten → PDF → Freigabe im Dashboard → Versand", "Claude API, Supabase-Funktion <i>bericht</i>", "Programm 1,5 h · SEO 1 h", 8, "ca. 0,10–0,30 € je Bericht", "läuft (Text mit Claude-Schlüssel)", 2),
 ("B3", "Google-Profil-Beiträge", "4 Beitragsentwürfe pro Monat je Kunde zur Freigabe, danach Veröffentlichung (API oder 1-Klick-Kopie)", "Claude API, Business Profile API", "Programm 1 h · SEO 0,5 h", 5, "< 1 € je Kunde", "gebaut – Schlüssel fehlen", 2),
 ("B4", "Bewertungen beantworten", "Neue Bewertung erkannt → Antwortentwurf → Push → du gibst frei", "Business Profile API, Claude API", "Programm 0,5 h · SEO 0,25 h", 4, "< 1 €", "wartet auf Google-Freigabe", 3),
 ("B5", "Verbesserungs-PRs", "Monatlich höchstens 3 Vorschläge je Kunde (Seitentitel, Ortsseite, FAQ, Ladezeit) als PR mit Vorschau", "Claude API, GitHub, Vercel", "Programm 1 h · SEO 0,75 h", 10, "ca. 1–2 € je Kunde", "gebaut – Schlüssel fehlen", 3),
 ("B6", "Ads-Wächter", "Wöchentlich Suchbegriffe prüfen, Ausschlüsse vorschlagen, Warnung bei Kosten ohne Anfragen", "Google Ads API, Claude API", "Programm 1 h", 8, "0 €", "wartet auf Ads-Token", 3),
 ("B7", "KI-Sichtbarkeit", "Monatlich „bester [Branche] in [Ort]“ an KI-Assistenten → wird der Kunde genannt? (Kennzahl im Bericht)", "Claude API u. a.", "– (Produktwert)", 4, "< 5 €", "gebaut – Schlüssel fehlen", 3),
 ("B8", "SEO-Startpaket", "Bei SEO-Auftrag: Audit (aus V2), Ortsseiten-Entwürfe, Profil-Checkliste als Entwurf", "V2, E2", "5 h je SEO-Einrichtung", 4, "ca. 1 €", "gebaut (über E2 + V2)", 2),
 ("B9", "Recruiting-Bausteine", "Karriereseite und Anzeigentexte aus Bausteinen, wöchentliche Bewerbungszahlen", "Generator, Claude API, Meta/Google", "4 h Einrichtung · 3 h/Monat", 8, "< 5 €", "ab Juni 2027", 4),
 # Finanzen & Verwaltung
 ("F1", "Abo-Rechnungen & Abgleich", "Wiederkehrende Rechnungen in Lexware; täglicher Abgleich → <i>rechnungen</i>; überfällig → Aufgabe + Mahnentwurf", "Lexware-Office-API", "ca. 2 h im Monat", 6, "im Lexware-Tarif", "später", 0),
 ("F2", "Lastschrift", "Mandat beim Auftrag, monatlicher Einzug, Rückläufer → Push + Aufgabe", "GoCardless-API (Webhooks)", "ca. 1 h im Monat", 5, "ca. 1 % je Zahlung", "später", 0),
 ("F3", "Laufzeit-Wächter", "4 Monate vor Vertragsende/Kündigungsfrist → Aufgabe + Verlängerungs-Entwurf", "Supabase (Zeitplan)", "schützt Umsatz", 2, "0 €", "läuft", 0),
 ("F4", "Zeiterfassung", "Start/Stopp je Kunde und Tätigkeit am Handy → <i>zeiten</i>; Grundlage, um die Annahmen durch echte Werte zu ersetzen", "Supabase, später Dashboard", "–", 3, "0 €", "läuft", 0),
 ("F5", "Agentur-Berichte", "Wochenbericht montags, Monatsbericht am 1. als Push", "Supabase-Funktion <i>bericht</i>", "–", 0, "0 €", "läuft", 0),
 # Steuerung
 ("S1", "Dashboard v1", "Ein Ort für Pipeline, Kunden, Websites, Rechnungen, Zahlungen, Freigaben, Zeiten – mit Knöpfen für V5, E5, B2", "Next.js, Vercel, Supabase Auth", "Übersicht in 2 Min. statt 30", 30, "0 € extra", "läuft (/intern/)", 2),
 ("S2", "Nachtschicht mit Claude", "Geplante Sitzungen nachts: Vorschauen für neue Leads bauen, Verbesserungs-PRs vorbereiten, morgens Zusammenfassung per Push", "Claude Code Routinen, GitHub", "Arbeit läuft, während du schläfst", 1, "im Claude-Abo", "gebaut – Schlüssel fehlen", 3),
]
BEREICHE = [("V", "Vertrieb"), ("E", "Website-Erstellung"), ("Ü", "Betrieb & Überwachung"), ("B", "Betreuung: SEO, Ads, Programm"),
            ("F", "Finanzen & Verwaltung"), ("S", "Steuerung")]
PHASEN = [(0, "Phase 0 · vor Kunde 1", "Okt–Nov 2026", "Pflicht, bevor die erste Kunden-Website live geht: Formulare, Prüfung, Pipeline, Geld."),
          (1, "Phase 1 · Kunde 1–4", "Nov–Dez 2026", "Website-Erstellung und Vertrieb automatisieren – hier steckt die meiste Zeit je Abschluss."),
          (2, "Phase 2 · bis Kunde 5", f"Dez 2026 – {B1['ab']}", "Monatliche Betreuung automatisieren und Dashboard v1. Ab hier rechnet das Modell mit den automatisierten Stunden."),
          (3, "Phase 3 · Kunde 5–10", "Feb–Apr 2027", "Feinschliff: Bewertungen, Verbesserungen, Ads, Nachtschicht."),
          (4, "Phase 4 · nach 10.000 € MRR", "ab Jun 2027", "Recruiting dazu, Team-Rollen im Dashboard.")]
STATUS_OK = ("läuft",)
def st(s): return f'<span class="st {"ok" if s.startswith("läuft") else "gb" if s.startswith("gebaut") else "of"}">{s}</span>'
BAU = {p: sum(a[5] for a in A if a[8] == p) for p, *_ in PHASEN}

STUNDEN = [("Vertrieb je Abschluss", "h_vertrieb", "V1–V5"), ("Neue Website", "h_setup_web", "E1–E5"),
           ("Einrichtung Wachstumsprogramm (inkl. Website)", "h_setup_prog", "E1–E5, B8"), ("Einrichtung SEO", "h_setup_seo", "B8"),
           ("Einrichtung Recruiting", "h_setup_rec", "B9"), ("Programm-Kunde je Monat", "h_mon_prog", "B1–B6"),
           ("SEO-Kunde je Monat", "h_mon_seo", "B1–B5"), ("Recruiting-Kunde je Monat", "h_mon_rec", "B9"), ("Pflege-Kunde je Monat", "h_mon_pflege", "Ü1, E3")]

CSS = """@font-face{font-family:"Inter Tight";src:url(../static/fonts/intertight.woff2);font-weight:100 900}@font-face{font-family:"Instrument Serif";src:url(../static/fonts/instrumentserif-italic.woff2);font-style:italic}
@page{size:A4;margin:16mm 0}
body{font:9.2pt/1.5 "Inter Tight",sans-serif;color:#0f0f0e;margin:0;padding:0 16mm}
h1,h2,h3{font-weight:500;letter-spacing:-.02em;line-height:1.1}h1{font-size:34pt;margin:0;letter-spacing:-.04em}h1 em{font-family:"Instrument Serif";font-weight:400;color:#e84300}
h2{font-size:17pt;margin:0 0 9pt;border-top:1.5px solid #0f0f0e;padding-top:8pt}h3{font-size:10.5pt;font-weight:600;margin:10pt 0 4pt}
.nr{font-size:9pt;color:#ad3300;margin-right:8pt;font-weight:500}
p{margin:0 0 6pt}ul{margin:0 0 6pt;padding-left:14pt}li{margin:2pt 0}
.page{break-before:page}section{margin-bottom:12pt}
table{width:100%;border-collapse:collapse;font-size:8.3pt;margin:4pt 0 10pt}th,td{padding:4pt 4.5pt;border-bottom:1px solid #d3cfc4;text-align:left;vertical-align:top}th{font-weight:500;color:#5a5852;border-bottom-color:#0f0f0e}
tr{break-inside:avoid}td.r,th.r{text-align:right}
table.a td:first-child{font-weight:600;color:#ad3300;width:18pt}table.a td:nth-child(2){font-weight:600;width:78pt}table.a td:nth-child(5),table.a td:nth-child(6){white-space:nowrap}
.st{display:inline-block;font-size:7.4pt;padding:1pt 5pt;border-radius:8pt;font-weight:500}.st.ok{background:#dcefe6;color:#0f5c4a}.st.of{background:#f3e7dc;color:#8a3d10}.st.gb{background:#e3e8f5;color:#2c3f7a}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:16pt}
.box{border-left:2px solid #e84300;padding:5pt 10pt;margin:8pt 0;background:#f6f4ef}.warn{background:#fbefe8}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:8pt;margin:12pt 0}.kpi{border-top:1.5px solid #0f0f0e;padding-top:5pt;font-size:8.2pt;color:#5a5852}.ber.fest{break-inside:avoid}h3{break-after:avoid}.kpi b{display:block;font-size:13pt;font-weight:500;color:#0f0f0e;letter-spacing:-.02em}
.small{font-size:8pt;color:#5a5852}.cover{min-height:255mm;display:flex;flex-direction:column;justify-content:space-between}
.ph{border-top:1px solid #d3cfc4;padding:7pt 0;display:grid;grid-template-columns:120pt 1fr;gap:12pt;break-inside:avoid}.ph b{display:block;font-size:10pt}"""

def bereich(k, titel):
    zeilen = [[a[0], a[1], a[2], a[3], a[4], (h(a[5]) if a[5] else "–"), st(a[7])] for a in A if a[0].startswith(k)]
    return f'<div class="ber{" fest" if len(zeilen) <= 6 else ""}"><h3>{titel}</h3>' + tab(["", "Automatisierung", "Was passiert", "Werkzeuge", "Spart", "Bau", "Status"], zeilen, "a") + "</div>"

def phase(p, t, zeit, txt):
    items = ", ".join(f"<b style='display:inline;font-size:inherit'>{a[0]}</b> {a[1]}" for a in A if a[8] == p)
    return f'<div class="ph"><div><b>{t}</b><span class="small">{zeit}</span></div><div>{txt}<br>{items}<br><span class="small">Bauzeit ca. {BAU[p]} h (Claude baut, du prüfst und gibst Zugänge – deine Zeit ca. {round(BAU[p] * .25)} h)</span></div></div>'

vgl = []
for n in M.SZENARIEN:
    a, b = K[(n, "hand")], K[(n, "auto")]
    vgl.append([f"<b>{n}</b>", f"{a['ziel']} → <b>{b['ziel']}</b>", f"{e0(a['m12'])} → <b>{e0(b['m12'])}</b>", f"{e0(a['m24'])} → <b>{e0(b['m24'])}</b>",
                f"{e0(a['erg24'])} → <b>{e0(b['erg24'])}</b>", f"{a['h12']:.0f} → <b>{b['h12']:.0f} h</b>"])

HTML = f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><title>{NAME} – Automatisierungsplan</title><style>{CSS}</style></head><body>
<section class="cover"><div><p class="small">Automatisierungsplan · intern · Stand {date.today().strftime('%d.%m.%Y')}</p>
<h1>Halbe Zeit je Kunde, <em>doppelter Spielraum.</em></h1>
<p style="max-width:125mm;margin-top:14pt;font-size:11pt">Welche {len(A)} Automatisierungen du brauchst, in welcher Reihenfolge sie gebaut werden, was jede an Stunden spart und was sie kostet. {sum(1 for a in A if a[7].startswith('läuft'))} laufen bereits, {sum(1 for a in A if a[7].startswith('gebaut'))} sind gebaut und starten, sobald die Schlüssel hinterlegt sind.</p>
<div class="kpis"><div class="kpi"><b>{M.h_neu():.0f} → {M.h_neu(auto_an=True):.0f} h</b>Stunden je neuem Abschluss</div><div class="kpi"><b>{B0['ziel']} → {B1['ziel']}</b>10.000 € MRR (Basis)</div>
<div class="kpi"><b>{e0(B0['m12'])} → {e0(B1['m12'])}</b>MRR nach 12 Monaten</div><div class="kpi"><b>ca. {sum(a[5] for a in A)} h</b>Bauzeit gesamt, verteilt auf 6 Monate</div></div></div>
<div class="box">Grundregel bleibt: Die KI bereitet vor, du gibst frei. Nichts geht ohne Freigabe live, nichts wird erfunden. Jede Automatik meldet Fehler per Push und legt eine Aufgabe an.</div></section>

<section class="page"><h2><small class="nr">01</small>Wirkung im Finanzmodell</h2>
<p>Das Finanzmodell rechnet jetzt zwei Varianten. <b>Von Hand:</b> alle Stunden wie heute geschätzt. <b>Automatisiert ab Kunde 5:</b> ab dem 5. Abschluss gelten die Stunden „mit System“ und {e0(G['auto_kosten'])} zusätzliche Systemkosten pro Monat. Recruiting wird in beiden Varianten erst ab Juni 2027 verkauft.</p>
{tab(["Szenario", "10.000 € MRR", "MRR Monat 12", "MRR Monat 24", "Ergebnis 24 Monate", "Stunden Monat 12"], vgl)}
<p class="small">Format: von Hand → automatisiert. Ergebnis vor Steuern. Gleiche Vertriebsleistung in beiden Varianten – der Unterschied kommt allein aus der frei werdenden Zeit: Von Hand bist du nach wenigen Monaten bei 170 Stunden voll und kannst keine neuen Kunden mehr annehmen.</p>
<h3>Stunden-Annahmen: von Hand und mit System</h3>
{tab(["Aufgabe", "von Hand", "mit System", "durch"], [[t, h(G[k]), f"<b>{h(G['a_' + k])}</b>", d] for t, k, d in STUNDEN])}
<div class="cols"><div class="box">Im Basis-Plan ist der 5. Abschluss im <b>{B1['ab']}</b> – bis dahin müssen Phase 0–2 stehen. Das ist sportlich.</div>
<div class="box warn">Puffer: Läuft die Automatisierung erst ab Kunde 10 ({SPAET_AB}), erreichst du 10.000 € MRR im <b>{SPAET[ZS - 1]['label'] if ZS else '–'}</b> – immer noch {'früher als' if ZS and ZS < M.zielmonat(RES[('Basis', 'hand')]) else 'so früh wie'} von Hand ({B0['ziel']}).</div></div>
<p class="small">Alle Stunden sind Schätzungen. Ab Kunde 1 erfasst du deine Zeiten (F4); nach 3 Kunden werden die Annahmen im Modell durch echte Werte ersetzt.</p></section>

<section class="page"><h2><small class="nr">02</small>Alle Automatisierungen</h2>
{bereich("V", "Vertrieb")}{bereich("E", "Website-Erstellung")}</section>
<section>{bereich("Ü", "Betrieb & Überwachung")}{bereich("B", "Betreuung: SEO, Ads, Wachstumsprogramm")}</section>
<section>{bereich("F", "Finanzen & Verwaltung")}{bereich("S", "Steuerung")}</section>

<section class="page"><h2><small class="nr">03</small>Reihenfolge</h2>
<p>Gebaut wird in der Reihenfolge, in der die Arbeit anfällt – und nach Stunden-Ersparnis pro Bauaufwand. Jede Phase ist eine eigene Claude-Code-Sitzung mit dem Master-Prompt (<code>betrieb/PROMPT.md</code>).</p>
{''.join(phase(*p) for p in PHASEN)}
<h3>Was du dafür einrichten musst (einmalig)</h3>
{tab(["Zugang", "Wofür", "Wo eintragen"], [
 ["Claude API-Schlüssel", "V3, V4, E2, B2–B7", "Supabase-Tabelle <i>einstellungen</i>: <code>anthropic_key</code> und GitHub-Secret <code>ANTHROPIC_API_KEY</code>; Kostenlimit in der Claude Console setzen"],
 ["Supabase Service-Schlüssel", "Nachtschicht, Betreuung (GitHub Actions)", "GitHub-Secret <code>SUPABASE_SERVICE_KEY</code> (Supabase → Settings → API)"],
 ["Google Places API-Schlüssel", "V1", "<i>einstellungen</i>: <code>places_key</code>; Suchen in <code>lead_suchen</code>, z. B. <code>[{\"branche\":\"Dachdecker\",\"ort\":\"Bielefeld\"}]</code>"],
 ["Google PageSpeed API-Schlüssel", "V2, Ü1", "<i>einstellungen</i>: <code>psi_key</code>"],
 ["Resend (E-Mail-Versand)", "Ü2 Formulare an Kunden", "<i>einstellungen</i>: <code>resend_key</code>, <code>mail_absender</code> (z. B. „Lotwerk Formular &lt;formular@deine-domain.de&gt;“, Domain bei Resend bestätigen)"],
 ["Cloudflare Turnstile (optional)", "Ü2 Spamschutz", "<i>einstellungen</i>: <code>turnstile_secret</code>"],
 ["Vercel-Token, Cloudflare-Token", "E5 Livegang", "nur lokal bzw. als Secret: <code>VERCEL_TOKEN</code>, <code>CF_API_TOKEN</code>; Vercel-Verbindung für Team „liferpg“ neu verbinden"],
 ["Google Business Profile API", "B1, B3, B4", "bei Google beantragen – <b>früh</b>, Freigabe dauert Wochen"],
 ["Google Ads API (Entwickler-Token)", "B6", "Antrag über ein Google-Ads-Verwaltungskonto (MCC)"],
 ["Zugänge der Kunden (Search Console, Google-Profil, Ads)", "B1–B6", "werden im Inhalte-Formular (E1) erfragt"]])}</section>

<section><h2><small class="nr">04</small>Was bei dir bleibt</h2>
<div class="cols"><div>{liste(["Gespräche mit Interessenten und Kunden", "Preise, Angebote und Ausnahmen entscheiden", "Jede Veröffentlichung freigeben (Website, Beitrag, Bewertungsantwort, Bericht)", "Qualität: Stichproben, Texte gegenlesen, [PRÜFEN] klären"])}</div>
<div>{liste(["Zugänge und Konten anlegen (Kapitel 3)", "Zeiten erfassen (F4) – sonst bleiben die Stunden Schätzungen", "Monatlich 30 Min.: Modell gegen Ist prüfen", "Neue Automatisierungen nur, wenn eine Aufgabe dreimal von Hand gemacht wurde"])}</div></div>
<div class="box">Laufende Kosten aller Automatisierungen: im Modell {e0(G['auto_kosten'])} pro Monat ab Kunde 5 (vor allem Claude API). Bei 20 Kunden sind das rund {e0(G['auto_kosten'] / 20)} je Kunde und Monat.</div></section>
</body></html>"""

if __name__ == "__main__":                       # beim Import (z. B. betrieb/uebersicht.py) nur Daten, keine Dateien
    (HERE / "Automatisierungsplan.html").write_text(HTML, encoding="utf-8")
    js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage();
    await p.goto('file://{HERE}/Automatisierungsplan.html');await p.waitForTimeout(400);
    await p.pdf({{path:'{HERE}/Automatisierungsplan.pdf',format:'A4',printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',
    footerTemplate:'<div style="font-size:7pt;color:#888;width:100%;text-align:center;font-family:sans-serif">{NAME} · Automatisierungsplan · Seite <span class=pageNumber></span> von <span class=totalPages></span></div>',
    margin:{{top:'14mm',bottom:'14mm',left:'0',right:'0'}}}});await b.close();}})();"""
    (HERE / "_pdf.js").write_text(js)
    subprocess.run(["node", str(HERE / "_pdf.js")], check=True, env={**os.environ, "NODE_PATH": subprocess.check_output(["npm", "root", "-g"]).decode().strip()})
    (HERE / "_pdf.js").unlink()
    print("Automatisierungsplan.pdf erstellt")
