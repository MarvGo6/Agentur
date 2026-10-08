"""Erzeugt betrieb/Firmenuebersicht.html und .pdf – alles auf einen Blick: Außenansicht (Leistungen, Pakete, Kundenweg),
Plan bis 31.12.2027, Aufbau Paket → Inhalt → Ablauf → Automatisierung, Bestand und offene Punkte.
Alle Zahlen kommen aus content.py, finanzen/modell.py, finanzen/million.py, betrieb/handbuch.py und betrieb/automatisierung.py.
Neu erzeugen: python3 betrieb/uebersicht.py"""
import sys, json, subprocess, os
from pathlib import Path
from datetime import date
ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "finanzen"), str(ROOT), str(HERE)]
import modell as M, million as MIO
import handbuch as HB, automatisierung as AU
from content import PREISE as P, eur, BRANCHEN, BEISPIELE, LEISTUNGEN as WEB

C = json.loads((ROOT / "config.json").read_text())
NAME, G = C["name"], M.G
def e0(v): return eur(round(v))
def h(v): return f"{v:g}".replace(".", ",") + " h"
def tab(kopf, zeilen, cls=""): return f'<table class="{cls}"><thead><tr>' + "".join(f"<th>{k}</th>" for k in kopf) + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in z) + "</tr>" for z in zeilen) + "</tbody></table>"
def liste(xs): return "<ul>" + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"
def kunden(x): return x["k_pflege"] + x["k_prog"] + x["k_seo"] + x["k_rec"]
AID = {a[0]: a for a in AU.A}
def auto(ids): return " ".join(f'<span class="st {"ok" if AID[i][7].startswith("läuft") else "gb" if AID[i][7].startswith("gebaut") else "of"}">{i} {AID[i][1]}</span>' for i in ids)

# ------------------------------------------------------------------ Zahlen: Plan bis Dez 2027 (Monat 1 = Nov 2026)
BIS = next(x["monat"] for x in M.rechne("Basis") if x["label"] == "Dez 27")           # = 14
R = {(n, v): M.rechne(n, variante=v)[:BIS] for n in M.SZENARIEN for v in M.VARIANTEN}
PLAN, HAND = R[("Basis", "auto")], R[("Basis", "hand")]
def jahr(rows, j, k="umsatz"): return sum(x[k] for x in rows if x["jahr"] == j)
def ziel(rows): return next((x["label"] for x in rows if x["mrr"] >= 10000), "nach Dez 27")
def ust_monat(rows):
    """Monat, in dem der Umsatz 2027 die Kleinunternehmer-Grenze von 100.000 € übersteigt (Regel seit 2025)."""
    s = 0
    for x in rows:
        if x["jahr"] == 2027:
            s += x["umsatz"]
            if s > 100000: return x["label"]
    return None
TEAM = [x for x in MIO.rechne() if x["jahr"] == 2027]
U27_TEAM = MIO.umsatz_jahr(2027)
END, ENDH = PLAN[-1], HAND[-1]

monate = [[x["label"], f"{x['deals']:.1f}", f"{kunden(x):.0f}", f"<b>{e0(x['mrr'])}</b>", e0(x["umsatz"]), f"{x['stunden']:.0f} h",
           e0(y["mrr"]), f"{y['stunden']:.0f} h", e0(x["kasse"])] for x, y in zip(PLAN, HAND)]
szen = [[n, ziel(R[(n, "hand")]) + " → " + ziel(R[(n, "auto")]), e0(R[(n, "hand")][-1]["mrr"]) + " → " + e0(R[(n, "auto")][-1]["mrr"]),
         e0(jahr(R[(n, "hand")], 2027)) + " → " + e0(jahr(R[(n, "auto")], 2027))] for n in M.SZENARIEN]
quartale = []
for q, ms in (("Nov–Dez 26", ("Nov 26", "Dez 26")), ("Q1 2027", ("Jan 27", "Feb 27", "Mär 27")), ("Q2 2027", ("Apr 27", "Mai 27", "Jun 27")),
              ("Q3 2027", ("Jul 27", "Aug 27", "Sep 27")), ("Q4 2027", ("Okt 27", "Nov 27", "Dez 27"))):
    xs = [x for x in PLAN if x["label"] in ms]
    quartale.append([q, f"{sum(x['deals'] for x in xs):.0f}", e0(sum(x["umsatz"] for x in xs)), e0(xs[-1]["mrr"]), f"{kunden(xs[-1]):.0f}", f"{xs[-1]['stunden']:.0f} h"])

# ------------------------------------------------------------------ Pakete → Inhalt → Ablauf → Automatisierung
VERTRIEB = ["V1", "V2", "V3", "V4", "V5", "V6"]
STRUKTUR = {  # Titel im Leistungshandbuch → (Stunden-Schlüssel im Modell, Automatisierungen)
    "Website Start": (("h_setup_web",), ["E1", "E2", "E3", "E4", "E5", "Ü2"]),
    "Website Wachstum": (("h_setup_web",), ["E1", "E2", "E3", "E4", "E5", "Ü2"]),
    "Pflege & Hosting": (("h_mon_pflege",), ["Ü1", "Ü2", "Ü3", "F3"]),
    "SEO Lokal / SEO Plus": (("h_setup_seo", "h_mon_seo"), ["B8", "B1", "B2", "B3", "B4", "B5", "B7"]),
    "Google Ads": ((), ["B1", "B2", "B6"]),
    "Recruiting Basis": ((), ["E1", "B9", "Ü2", "B2"]),
    "Recruiting Komplett": (("h_setup_rec", "h_mon_rec"), ["E1", "B9", "Ü2", "B2"]),
    "Wachstumsprogramm": (("h_setup_prog", "h_mon_prog"), ["E1", "E2", "E3", "E4", "E5", "B1", "B2", "B3", "B4", "B5", "B6", "B7"]),
}
STD_TXT = {"h_setup_web": "Einrichtung", "h_mon_pflege": "je Monat", "h_setup_seo": "Einrichtung", "h_mon_seo": "je Monat",
           "h_setup_rec": "Einrichtung", "h_mon_rec": "je Monat", "h_setup_prog": "Einrichtung", "h_mon_prog": "je Monat"}
def paket(l):
    keys, ids = STRUKTUR[l["titel"]]
    std = " · ".join(f"{STD_TXT[k]} {h(G[k])} → <b>{h(G['a_' + k])}</b>" for k in keys) or f"laut Handbuch {l['aufwand']} (im Modell nicht eigens gerechnet)"
    return f"""<div class="pk"><h3>{l['titel']}</h3><p class="small">{l['preis']} · Lieferzeit: {l['dauer']}</p>
<div class="cols"><div><b>Enthalten</b>{liste(l['enthalten'])}</div><div><b>Nicht enthalten</b>{liste(l['nicht'])}
<b>Ablauf</b>{liste([f"{t}: {x}" for t, x in l['ablauf']])}</div></div>
<p><b>Deine Stunden</b> (von Hand → mit System): {std}</p><p><b>Automatisierungen:</b> {auto(ids)}</p></div>"""

# ------------------------------------------------------------------ Bestand
DOKUMENTE = [
    ("Businessplan", "businessplan/Businessplan.pdf", "Markt, Angebot, Vertrieb, Solo-Plan, Team-Ausbau, Risiken"),
    ("Finanzmodell", "finanzen/Finanzmodell.xlsx · modell.py · million.py", "3 Szenarien, von Hand / automatisiert, Team-Ausbau"),
    ("Betriebsplan", "betrieb/Betriebsplan.pdf", "Rollen, Werkzeuge, 5 Kernabläufe, Dashboard, Fahrplan in 5 Stufen"),
    ("Leistungshandbuch", "betrieb/Leistungshandbuch.pdf", "Lieferumfang, Abnahme-Checkliste, Inhalte-Liste, Vertragsbausteine"),
    ("Automatisierungsplan", "betrieb/Automatisierungsplan.pdf", f"{len(AU.A)} Automatisierungen mit Status, Phasen, Stunden-Ersparnis"),
    ("Master-Prompt", "betrieb/PROMPT.md", "Regeln und Stufen für neue Claude-Sitzungen, Stand „Bereits umgesetzt“"),
    ("Tracking & Rechtstexte", "betrieb/TRACKING.md", "Messung, Einwilligung, Platzhalter in Impressum/AGB"),
    ("Recherche", "RECHERCHE.md", "Muster gut sichtbarer Betriebe je Branche"),
    ("Kunden-Websites", "sites/README.md", "Generator, Abnahme-Prüfung, Livegang, KI-Skripte"),
]
SYSTEM = [
    ("Agentur-Website", "lotwork.vercel.app – Leistungen, 7 Branchen, Beispiele mit Vorschau-Websites, Preise, Ratgeber, Kontakt, Impressum, Datenschutz, AGB-Entwurf", "läuft (Vorschau, noindex)"),
    ("Steuerzentrale /intern/", "Cockpit, Aufgaben, Freigaben, Pipeline, Kunden/Verträge, Websites, Zeiten, Anfragen, Berichte", "läuft"),
    ("Kundenformular /inhalte/", "Kunde lädt Texte, Fotos, Leistungen hoch (E1)", "läuft"),
    ("Datenbank Supabase", "Interessenten, Kunden, Verträge, Rechnungen, Kosten, Zeiten, Websites, Checks, Messwerte, Aufgaben, KI-Läufe, Berichte, Seitenaufrufe", "läuft"),
    ("Funktionen Supabase", "monitor, analyse, bericht, formular, inhalte, leads, vertrieb + Zeitpläne", "läuft (teils ohne Schlüssel)"),
    ("Kunden-Websites sites/", "Generator, Abnahme-Prüfung, Livegang, KI-Texte, KI-Vorschauen, Betreuung; GitHub Actions", "gebaut – Schlüssel fehlen"),
    ("Meldungen", "Push über ntfy (Anfragen, Fehler, Berichte)", "läuft"),
]

U26 = jahr(PLAN, 2026)
UST_A, UST_H = ust_monat(PLAN), ust_monat(HAND)
LUECKEN = [
    ("Widerspruch: Weg ab Juli 2027", f"Der Businessplan stellt ab {MIO.LABELS[0]} ein Team ein (Umsatz 2027 dann {e0(U27_TEAM)}, Kasse zwischenzeitlich bis {e0(min(x['kasse'] for x in MIO.rechne()))}, 5.000 € Gründergehalt eingerechnet). Betriebs- und Automatisierungsplan rechnen allein mit Automatisierung weiter (Dez 27: {e0(END['mrr'])} MRR bei {END['stunden']:.0f} h). Das Team-Modell kennt die Automatisierung noch nicht.", "Entscheiden, sobald 10.000 € MRR zwei Monate stabil sind. Empfehlung: zuerst allein mit System, erste Einstellung (Umsetzung) erst bei mehr als 150 h im Monat. Danach das Team-Modell auf die automatisierten Stunden umstellen."),
    ("Widerspruch: Umsatzsteuer", f"Website, AGB und FAQ sagen „Kleinunternehmer, Endpreise“. Seit 2025 gilt: Im Gründungsjahr höchstens 25.000 € (2026 laut Plan {e0(U26)} – passt), im Folgejahr fällt die Regel weg, sobald der Umsatz im laufenden Jahr 100.000 € übersteigt. Das wäre laut Plan im {UST_A} (automatisiert) bzw. {UST_H} (von Hand) der Fall. Ab dann kommen 19 % dazu, mitten im Jahr. Der Businessplan nennt noch die alte 25.000-€-Grenze.", "Mit dem Steuerberater klären [PRÜFEN]. Weil alle Kunden Betriebe sind und sich die Umsatzsteuer zurückholen, spricht viel dafür, gleich mit Umsatzsteuer zu starten und Nettopreise zu nennen. Danach Website, AGB und FAQ anpassen."),
    ("Finanzmodell vereinfacht", "Google Ads wird im Solo-Modell nicht als eigener Abschluss gerechnet (nur im Wachstumsprogramm). Einmalbeträge fließen im Modell sofort, in Wirklichkeit 50 % bei Auftrag und 50 % nach Abnahme. Steuern, Krankenversicherung und Lebenshaltung sind nicht abgezogen: „Kasse“ heißt Gewinn vor Steuern.", "Ab dem ersten Kunden Ist-Werte (Zeiterfassung F4, Rechnungen) monatlich gegen das Modell halten."),
    ("Name und Domain", f"„{NAME}“ ist laut Betriebsplan ein Arbeitsname. Die Website läuft auf lotwork.vercel.app, die E-Mail-Adresse {C['email']} ist eingetragen, eine eigene Domain ist noch nicht verbunden.", "Name festlegen, Domain kaufen und verbinden, E-Mail einrichten [PRÜFEN]."),
    ("Rechtliches und Verträge", "Impressum ohne Name, Anschrift und Telefon. AGB-Entwurf ungeprüft (Zahlungsziel und Abrechnung fehlen). Vorlagen für Angebot und AV-Vertrag fehlen. Vermögensschadenhaftpflicht, Gewerbe und Finanzamt stehen im Businessplan als erste Schritte, im Repo ist dazu nichts vermerkt [PRÜFEN].", "Fahrplan Oktober 2026 (Kapitel 06) abarbeiten."),
    ("Schlüssel und Konten", "Claude, Resend und Absender, Google Places, PageSpeed, SUPABASE_SERVICE_KEY, Vercel-Token, Google Business Profile und Ads-Token fehlen. Vercel Pro und Supabase Pro sind vor dem ersten zahlenden Kunden Pflicht. Lexware, Geschäftskonto und GoCardless bewusst später.", f"Schlüssel eintragen. Danach laufen {sum(1 for x in AU.A if x[7].startswith('gebaut'))} gebaute Automatisierungen an."),
    ("Vertrauen ohne Kunden", "Keine echten Kundenstimmen, keine Fallstudie (Platzhalter auf der Startseite), kein Google-Profil der Agentur.", "Erste 2–3 Kunden als Pilot mit Freigabe für eine Fallstudie gewinnen."),
    ("Aufräumen", "Testdaten in Supabase (Anfragen „TEST Claude“, Inhalte-Formulare „TEST …“, Speicher „inhalte“). Supabase Auth: Site URL auf /intern/ setzen.", "Einmal erledigen."),
]
SCHRITTE = [
    ("Oktober 2026", "Grundlagen", ["Name und Domain festlegen, Gewerbe anmelden, Fragebogen Finanzamt", "Umsatzsteuer mit dem Steuerberater entscheiden, dann Preise und Texte anpassen", "Impressum ausfüllen, AGB prüfen lassen, Angebots- und AV-Vorlage", "Schlüssel eintragen (Claude, Resend, Places, PageSpeed), Testdaten löschen", "Erste Branche wählen (Empfehlung Businessplan: Dachdecker & Solar oder Steuerberater), 100 Betriebe in die Liste"]),
    ("November 2026", "Start Vertrieb", ["Website öffentlich schalten (preview aus), Google-Profil der Agentur", "Täglich 6 Betriebe anschreiben, Vorschau-Website in 48 Stunden", "Erster Kunde → Vercel Pro und Supabase Pro", f"Ziel: {PLAN[0]['deals']:.0f} Abschlüsse"]),
    ("Dez 26 – Feb 27", "System trägt", ["Ab Kunde 5 mit automatisierten Abläufen arbeiten (Modell: ab " + next(x['label'] for x in PLAN if x['auto']) + ")", "Monatsberichte, Profil-Beiträge, Verbesserungs-PRs mit Freigabe", f"Prüfpunkt Jan 27: MRR ≈ {e0(next(x['mrr'] for x in PLAN if x['label'] == 'Jan 27'))}, sonst Branche wechseln, Ansprache kürzen"]),
    ("Mär – Jun 27", "10.000 € MRR", [f"10.000 € MRR im Plan: {ziel(PLAN)} (von Hand: {ziel(HAND)})", "Ab Juni 2027: Recruiting-Paket verkaufen (B9), zuerst an Bestandskunden", "Abos vor Einzel-Websites, Wachstumsprogramm zuerst anbieten"]),
    ("Jul – Dez 27", "Ausbau", ["Entscheidung: allein mit System weiter oder Team (siehe Kapitel 07)", f"Plan Dez 27: {e0(END['mrr'])} MRR, {kunden(END):.0f} laufende Verträge, {END['stunden']:.0f} h im Monat", "Umsatzsteuer-Wechsel vorbereiten (falls Kleinunternehmer)", "Reserve für die erste Einstellung ansparen (Businessplan: 30.000–40.000 €)"]),
]

# ------------------------------------------------------------------ Selbstständig machen (Stand Okt 2026, Werte grob, mit Steuerberater prüfen)
CHECK = [
    ("Vor dem Start", [
        "Entscheiden: nebenberuflich starten (Job behalten, Krankenkasse läuft über den Arbeitgeber) oder hauptberuflich. Nebenberuflich ist es grob, solange Zeit und Einkommen aus der Selbstständigkeit unter denen aus dem Job bleiben (Faustregel: unter 20 h pro Woche).",
        "Arbeitgeber informieren, falls der Arbeitsvertrag Nebentätigkeiten genehmigungspflichtig macht [PRÜFEN Arbeitsvertrag].",
        "Gründungszuschuss nur bei Arbeitslosengeld I (mindestens 150 Tage Restanspruch): Antrag VOR dem Start, Stellungnahme einer fachkundigen Stelle (IHK, Steuerberater). Kein Rechtsanspruch.",
        "Kostenlose Gründungsberatung bei der IHK nutzen, Erstgespräch mit Steuerberater (auch zur Umsatzsteuer, Kapitel 13).",
        "Geschäftskonto eröffnen, privat und geschäftlich trennen.",
    ]),
    ("Anmelden (erste Woche)", [
        "Gewerbe für die Agentur ummelden bzw. erweitern (als ERGO-Vermittler besteht schon ein Gewerbe), ca. 20–60 €.",
        "Fragebogen zur steuerlichen Erfassung beim Finanzamt (ELSTER): Kleinunternehmer ja/nein, erwarteter Gewinn.",
        "IHK-Mitgliedschaft kommt automatisch; für Gründer mit kleinem Gewinn meist beitragsfrei.",
        "Berufsgenossenschaft (VBG): Unternehmen innerhalb einer Woche anmelden; eigene Absicherung freiwillig.",
        "Krankenkasse informieren: Das Einkommen aus Agentur und Vermittlung zählt zusammen für den Beitrag.",
        "Künstlersozialkasse: Abgabe von ca. 5 % auf eingekaufte Texte, Fotos, Design von Selbstständigen einplanen und melden.",
    ]),
    ("Absichern", [
        "Vermögensschaden- bzw. IT-Haftpflicht vor dem ersten Kunden (ca. 15–30 € im Monat).",
        "Hauptberuflich: Krankenkasse wählen. Gesetzlich freiwillig mit Krankengeld (Mindestbeitrag 2026 ca. 280–290 € im Monat inkl. Pflege, Höchstbeitrag ca. 1.200–1.300 €) oder privat (nur nach Beratung).",
        "Freiwillige Arbeitslosenversicherung: Antrag spätestens 3 Monate nach Start (ca. 50–100 € im Monat).",
        "Berufsunfähigkeitsversicherung prüfen (je jünger, desto günstiger).",
        "Altersvorsorge festlegen (keine Rentenpflicht für Selbstständige in diesem Beruf, Lücke selbst schließen).",
    ]),
    ("Laufend", [
        "30–40 % vom Gewinn auf ein eigenes Konto für Steuern und Krankenkasse.",
        "Belege sofort ablegen (Buchhaltung), Rechnungen mit allen Pflichtangaben.",
        "Einkommensteuer-Vorauszahlungen einplanen: Nach dem ersten Bescheid kommen Nachzahlung und Vorauszahlung oft gleichzeitig.",
        "Gewerbesteuer erst ab 24.500 € Gewinn im Jahr (Freibetrag).",
        "Ab ca. 50.000–80.000 € Gewinn im Jahr mit dem Steuerberater über eine GmbH bzw. Holding sprechen (Kapitel 15).",
    ]),
]
NETTO = [["Gewinn im Monat", "10.000 €"], ["Krankenkasse und Pflege (gesetzlich, Höchstbeitrag)", "ca. −1.250 €"],
         ["Einkommensteuer, Soli (ledig, grob)", "ca. −2.700 bis −3.200 €"], ["Gewerbesteuer (wird größtenteils mit Einkommensteuer verrechnet)", "ca. −100 bis −300 €"],
         ["Altersvorsorge, Versicherungen (selbst festlegen)", "ca. −500 bis −1.000 €"], ["<b>Bleibt zum Leben</b>", "<b>ca. 5.000–5.500 €</b>"]]

GRUPPE = [
    ("Büscher Unternehmensgruppe GmbH (Holding)", "Hält die Anteile an allen Firmen. Gewinne der Töchter fließen fast steuerfrei hinein (95 % steuerfrei, effektiv ca. 1,5 %) und können dort in neue Firmen oder Immobilien gesteckt werden. Verkauf einer Tochter ebenfalls zu 95 % steuerfrei."),
    ("Lotwerk GmbH", "Die Agentur und später Wachstumsberatung, Tochter der Büscher Unternehmensgruppe. Eigene Haftung, eigener Kundenstamm, später verkaufbar."),
    ("Immobilien GmbH (später)", "Nur Vermietung eigener Immobilien, ohne andere Tätigkeit: dann meist keine Gewerbesteuer (erweiterte Kürzung). Deshalb nie mit Agentur oder Bau mischen."),
    ("Bau GmbH (später)", "Hohe Haftungsrisiken (Gewährleistung, Personal). Eigene GmbH schützt den Rest der Gruppe."),
]

CSS = AU.CSS + """ul.check{list-style:none;padding-left:0}ul.check li{margin:3pt 0}
.pk{border-top:1px solid #d3cfc4;padding:6pt 0 4pt;break-inside:avoid}.pk h3{margin-top:2pt}.pk .cols{gap:12pt}.pk ul{font-size:8.4pt}
.teil{font-size:8pt;letter-spacing:.12em;text-transform:uppercase;color:#ad3300;margin:0 0 4pt}
table.m td,table.m th{padding:3pt 4pt;font-size:7.9pt}table.m td:not(:first-child),table.m th:not(:first-child){text-align:right}
.fl{display:flex;flex-wrap:wrap;gap:3pt}"""

leist_web = [[l["titel"], dict(l["eckdaten"]).get("Preis", ""), dict(l["eckdaten"]).get("Laufzeit", dict(l["eckdaten"]).get("Pflege & Hosting", ""))] for l in WEB]
pakete = [[b["branche"], " + ".join(t.split(" (")[0].split(",")[0] for t, _ in b["paket"]), e0(sum(v for _, v in b["paket"]))] for b in BEISPIELE]

HTML = f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><title>{NAME} – Firmenübersicht</title><style>{CSS}</style></head><body>
<section class="cover"><div><p class="small">Firmenübersicht · Stand {date.today().strftime('%d.%m.%Y')} · fasst Businessplan, Betriebsplan, Leistungshandbuch, Automatisierungsplan und Finanzmodell zusammen</p>
<h1>{NAME} auf einen Blick: <em>außen, innen, bis Ende 2027.</em></h1>
<p style="max-width:130mm;margin-top:14pt;font-size:11pt">{C['tagline']} Eine Agentur ohne Gesicht für lokale Betriebe. Der Gründer verkauft und gibt frei, Erstellung, Prüfung, Überwachung und Berichte laufen über das eigene System.</p>
<div class="kpis"><div class="kpi"><b>{ziel(PLAN)}</b>10.000 € MRR (Basis, mit System)</div><div class="kpi"><b>{e0(END['mrr'])}</b>MRR Dez 27 (allein, mit System)</div>
<div class="kpi"><b>{e0(jahr(PLAN, 2027))}</b>Umsatz 2027 (allein, mit System)</div><div class="kpi"><b>{sum(1 for a in AU.A if a[7].startswith('läuft'))} + {sum(1 for a in AU.A if a[7].startswith('gebaut'))}</b>Automatisierungen laufen + warten auf Schlüssel</div></div></div>
<div><p><b>Inhalt</b></p><p class="small">Teil A – Für Kunden: 01 Wer wir sind · 02 Leistungen und Preise · 03 Beispielpakete · 04 So arbeiten wir<br>
Teil B – Intern: 05 Plan Nov 26 – Dez 27 · 06 Fahrplan und Meilensteine · 07 Zweite Jahreshälfte: allein oder Team · 08 Vertrieb und Kosten<br>
Teil C – Aufbau: 09 Pakete → Inhalt → Ablauf → Automatisierung · 10 Alle Automatisierungen · 11 System<br>
Teil D – Bestand: 12 Was da ist · 13 Widersprüche und Lücken<br>Teil E – Gründer: 14 Checkliste selbstständig machen · 15 Später: Unternehmensgruppe mit Holding</p>
<div class="box">Planwerte, keine Zusagen. Monat 1 = November 2026 (erster Vertriebsmonat), der Plan läuft bis 31.12.2027. „Mit System“ heißt: Ab dem 5. Kunden gelten die Stunden aus dem Automatisierungsplan.</div></div></section>

<section class="page"><p class="teil">Teil A · Für Kunden</p><h2><small class="nr">01</small>Wer wir sind</h2>
<p>{NAME} hilft lokalen Betrieben zu mehr passenden Anfragen, von Kunden und von Fachkräften. Schwerpunkt sind {", ".join(b["titel"] for b in BRANCHEN)}.</p>
<div class="cols"><div><b>Was uns unterscheidet</b>{liste(["Feste Preise statt Stundenabrechnung", "Fertige Vorschau-Website für Ihren Betrieb, bevor Sie sich entscheiden", "Ergebnisse in Anfragen und Anrufen, nicht in Klicks", "Website und Domain gehören Ihnen", "Schnelle Technik, möglichst ohne Cookie-Banner", "Ein Ansprechpartner, Antwort innerhalb eines Werktags"])}</div>
<div><b>Für wen</b>{liste([f"{b['titel']}: {b['claim']}" for b in BRANCHEN])}</div></div>

<h2><small class="nr">02</small>Leistungen und Preise</h2>
{tab(["Leistung", "Preis", "Laufzeit"], leist_web)}
<p class="small">Einzelpreise: Website Start {eur(P['web_start'])}, Website Wachstum {eur(P['web_wachstum'])} · Pflege & Hosting {P['pflege_start']} € bzw. {P['pflege_wachstum']} € im Monat · SEO Lokal {P['seo_lokal']} €, SEO Plus {P['seo_plus']} € im Monat · Google Ads {P['ads_setup']} € + {P['ads']} € im Monat · Recruiting Basis {eur(P['rec_basis_setup'])} + {P['rec_basis']} € im Monat, Komplett {eur(P['rec_setup'])} + {P['rec']} € im Monat (Verkauf ab Juni 2027) · Wachstumsprogramm {eur(P['prog_setup'])} + {eur(P['programm'])} im Monat. Werbebudgets zahlt der Kunde direkt an Google oder Meta. {C['impressum']['ust']} <b>[PRÜFEN, siehe Kapitel 13]</b></p>

<h2><small class="nr">03</small>Beispielpakete (auf der Website mit Vorschau)</h2>
{tab(["Branche", "Paket", "1. Jahr"], pakete)}

<h2><small class="nr">04</small>So arbeiten wir</h2>
{tab(["Schritt", "Was passiert"], [["1 · Ersteinschätzung", "Kostenlos, 20 Minuten: Website und Google-Profil"], ["2 · Angebot", "Festpreis, auf Wunsch mit Vorschau-Website"], ["3 · Auftrag", "50 % Anzahlung, Inhalte-Formular online (Frist 7 Tage)"], ["4 · Entwurf", "Im Browser ansehen, zwei Korrekturrunden"], ["5 · Livegang", "Abnahme-Prüfung, Domain, Messung, Überwachung, 50 % Restzahlung"], ["6 · Betreuung", "Monatsbericht in Anfragen und Anrufen, Vorschläge zur Freigabe"]])}
</section>

<section class="page"><p class="teil">Teil B · Intern</p><h2><small class="nr">05</small>Plan Nov 26 – Dez 27 (Basis)</h2>
<p>Allein bis 10.000 € MRR. Vertriebstempo: 2 Abschlüsse in den ersten zwei Monaten, danach 3. Die Grenze setzen deine 170 Stunden im Monat. Planwerte „mit System“, Vergleich „von Hand“.</p>
{tab(["Monat", "Abschl.", "Verträge", "MRR", "Umsatz", "Stunden", "MRR v. Hand", "Std. v. Hand", "Gewinn kum."], monate, "m")}
<p class="small">Verträge = laufende Pflege-, SEO-, Programm- und Recruiting-Verträge. Gewinn kumuliert = vor Steuern, Krankenversicherung und Lebenshaltung; Kosten im Modell {G['fix_kosten']} € fix + {G['marketing']} € Marketing + ab Kunde 5 {G['auto_kosten']} € Systemkosten pro Monat.</p>
<div class="cols"><div><h3>Nach Quartalen (mit System)</h3>{tab(["Zeitraum", "Abschl.", "Umsatz", "MRR Ende", "Verträge", "Std."], quartale, "m")}</div>
<div><h3>Szenarien (von Hand → mit System)</h3>{tab(["Szenario", "10.000 € MRR", "MRR Dez 27", "Umsatz 2027"], szen)}
<p class="small">Konservativ 1/2, Basis 2/3, Optimistisch 3/4 Abschlüsse im Monat (Monat 1–2 / danach).</p></div></div>
<div class="kpis"><div class="kpi"><b>{e0(U26)}</b>Umsatz Nov–Dez 26</div><div class="kpi"><b>{e0(jahr(PLAN, 2027))}</b>Umsatz 2027 mit System</div><div class="kpi"><b>{e0(jahr(HAND, 2027))}</b>Umsatz 2027 von Hand</div><div class="kpi"><b>{e0(END['kasse'])}</b>Gewinn vor Steuern bis Dez 27</div></div>
</section>

<section class="page"><h2><small class="nr">06</small>Fahrplan und Meilensteine</h2>
{"".join(f'<div class="ph"><div><b>{z}</b><span class="small">{t}</span></div>{liste(xs)}</div>' for z, t, xs in SCHRITTE)}

<h2><small class="nr">07</small>Zweite Jahreshälfte 2027: allein mit System oder Team</h2>
<div class="cols"><div><h3>A · Allein mit System (Betriebsplan)</h3>{liste([f"MRR Dez 27: <b>{e0(END['mrr'])}</b>, {END['stunden']:.0f} h belegt", f"Umsatz 2027: {e0(jahr(PLAN, 2027))}", f"Gewinn Jul–Dez 27 vor Steuern: {e0(sum(x['ergebnis'] for x in PLAN if x['jahr'] == 2027 and x['monat'] >= 9))}", "Kein Personalrisiko, aber ab etwa Jan 28 wieder voll ausgelastet", "Obergrenze allein mit System: rund 26.900 € MRR (Betriebsplan)"])}</div>
<div><h3>B · Team ab {MIO.LABELS[0]} (Businessplan)</h3>{liste([f"MRR Dez 27: <b>{e0(TEAM[-1]['mrr'])}</b>, {TEAM[-1]['closer']} Closer / {TEAM[-1]['sdr']} Terminierer, {TEAM[-1]['fte']:.1f} Vollzeitkräfte Umsetzung", f"Umsatz 2027: {e0(U27_TEAM)}", f"Ergebnis Jul–Dez 27 nach 5.000 € Gründergehalt: {e0(sum(x['ergebnis'] for x in TEAM))}", f"Kasse im Ausbau zwischenzeitlich {e0(min(x['kasse'] for x in TEAM))} → Reserve 30.000–40.000 €", "1-Mio-Tempo ab " + str(MIO.tempo_monat())])}</div></div>
<div class="box">Das Team-Modell rechnet noch ohne Automatisierung (Umsetzung zu {MIO.A['h_satz']} € je Stunde). Mit System würden die Umsetzungskosten deutlich sinken. Empfehlung: erst A, dann schrittweise B. Erste Einstellung in der Umsetzung, sobald dauerhaft mehr als 150 h im Monat belegt sind, Closer erst, wenn die Abläufe dokumentiert sind (Voraussetzungen im Businessplan, Kapitel 10).</div>

<h2><small class="nr">08</small>Vertrieb und Kosten</h2>
<div class="cols"><div><h3>Vertriebstrichter (3 Abschlüsse im Monat)</h3>{liste(["ca. 120 Betriebe im Monat anschreiben (6 pro Arbeitstag), sachlich, B2B, mit Abmeldemöglichkeit", "bei 10 % Antwortquote ca. 12 Gespräche (3 pro Woche)", "bei 25 % Abschlussquote 3 Aufträge", "Vorschau-Website in 48 Stunden für Interessierte, Nachfassen nach 3 und 7 Tagen (V4)", "Partner: Steuerberater, Druckereien, Fotografen – ein Monat Pflege gratis je Empfehlung"])}</div>
<div><h3>Laufende Kosten (Betriebsplan, ca.-Werte)</h3>{tab(["Wann", "Was", "pro Monat"], [["Oktober 2026", "Lexware Office, Geschäftskonto, Domain", "ca. 30 €"], ["ab Kunde 1", "Vercel Pro, Supabase Pro, Statistik, GoCardless", "ca. 80–110 €"], ["ab Kunde 5", "Claude API, Google APIs", "ca. 130–180 €"], ["ab Kunde 8–10", "mehr KI-Nutzung, ggf. Better Stack", "ca. 180–260 €"]])}</div></div>
</section>

<section class="page"><p class="teil">Teil C · Aufbau</p><h2><small class="nr">09</small>Pakete → Inhalt → Ablauf → Automatisierung</h2>
<p>Für jedes Paket: was der Kunde bekommt, wie es geliefert wird, wie viel Zeit es dich kostet und welche Automatisierungen dabei helfen. Status: <span class="st ok">läuft</span> <span class="st gb">gebaut, Schlüssel fehlt</span> <span class="st of">später / wartet</span></p>
<div class="pk"><h3>Für alle Pakete: Vertrieb</h3><p><b>Deine Stunden je Abschluss:</b> {h(G['h_vertrieb'])} → <b>{h(G['a_h_vertrieb'])}</b> · <b>Automatisierungen:</b> {auto(VERTRIEB)}</p></div>
{"".join(paket(l) for l in HB.LEISTUNGEN)}
<p class="small">Im Schnitt kostet ein neuer Abschluss (Einrichtung, erster Betreuungsmonat, Vertrieb) {h(round(M.h_neu(), 1))} von Hand und {h(round(M.h_neu(auto_an=True), 1))} mit System.</p>
</section>

<section class="page"><h2><small class="nr">10</small>Alle Automatisierungen</h2>
{tab(["", "Name", "Was passiert", "Status"], [[a[0], a[1], a[2], AU.st(a[7])] for a in AU.A], "a")}

<h2><small class="nr">11</small>System</h2>
{tab(["Baustein", "Inhalt", "Status"], [[n, t, AU.st(s)] for n, t, s in SYSTEM])}
<p class="small">Regeln: KI veröffentlicht nie direkt (immer Pull Request mit Vorschau und Freigabe). Nichts wird erfunden, Fehlendes ist [PRÜFEN] und blockiert den Livegang. Daten in der EU, Zugriffsschutz auf jeder Tabelle, keine Tracker ohne Einwilligung.</p>
</section>

<section class="page"><p class="teil">Teil D · Bestand</p><h2><small class="nr">12</small>Was da ist</h2>
{tab(["Dokument", "Datei", "Inhalt"], [[a, f"<span class=small>{b}</span>", c] for a, b, c in DOKUMENTE])}
<p class="small">Diese Übersicht fasst die Dokumente zusammen und ersetzt sie nicht. Bei Änderungen an Preisen (content.py), Modell (finanzen/) oder Automatisierungen (automatisierung.py) neu erzeugen: <i>python3 betrieb/uebersicht.py</i>.</p>

<h2><small class="nr">13</small>Widersprüche und Lücken</h2>
{tab(["Punkt", "Befund", "Was zu tun ist"], [[f"<b>{a}</b>", b, c] for a, b, c in LUECKEN])}
</section>

<section class="page"><p class="teil">Teil E · Gründer</p><h2><small class="nr">14</small>Checkliste: selbstständig machen</h2>
<p class="small">Stand Oktober 2026. Beträge sind grobe Richtwerte aus öffentlichen Quellen (Krankenkassen-Tabellen 2026, Arbeitsagentur, IHK), keine Beratung. Vor Entscheidungen mit Steuerberater bzw. Krankenkasse abstimmen.</p>
{"".join(f"<h3>{t}</h3>" + "<ul class=check>" + "".join(f"<li>☐ {x}</li>" for x in xs) + "</ul>" for t, xs in CHECK)}
<h3>Was von 10.000 € Gewinn bleibt (grob, hauptberuflich, ledig, ohne Kinder)</h3>
{tab(["Posten", "pro Monat"], NETTO)}
<div class="box">Wichtig: 10.000 € MRR im Plan sind <b>Umsatz</b>, nicht Gewinn. Davon gehen erst die Kosten ab (Kapitel 08), dann Steuern und Krankenkasse. Schätzung, mit Steuerberater nachrechnen [PRÜFEN].</div>

<h2><small class="nr">15</small>Später: Unternehmensgruppe mit Holding</h2>
<p>Ziel: oben die <b>Büscher Unternehmensgruppe GmbH</b> als Holding, darunter je Geschäft eine eigene GmbH. Gewinne bleiben fast steuerfrei in der Gruppe und können in das nächste Geschäft fließen. Jede Firma haftet nur für sich.</p>
{tab(["Ebene", "Zweck"], [[f"<b>{a}</b>", b] for a, b in GRUPPE])}
<h3>Reihenfolge</h3>
<ul><li><b>Jetzt bis ca. 50.000–80.000 € Gewinn im Jahr:</b> Einzelunternehmen. Eine GmbH kostet Gründung (Notar, Handelsregister) und jedes Jahr Bilanz und Buchhaltung, je Firma grob 2.000–4.000 € [PRÜFEN Steuerberater].</li>
<li><b>Danach:</b> zuerst die Holding gründen, dann gründet die Holding die Marketing GmbH und das Einzelunternehmen wird eingebracht. Andersherum (erst GmbH, später unter eine Holding) geht auch, hat aber eine Sperrfrist von 7 Jahren für einen steuergünstigen Verkauf.</li>
<li><b>Gewinne, die du zum Leben brauchst,</b> zahlst du dir als Gehalt aus der Marketing GmbH. Nur was übrig bleibt, wandert in die Holding. Eine Holding lohnt sich also erst, wenn regelmäßig Geld übrig bleibt.</li>
<li><b>Stammkapital:</b> GmbH 25.000 € (zur Gründung mindestens 12.500 € einzahlen), UG ab 1 € (muss dann Rücklagen bilden).</li></ul>
<h3>ERGO bleibt außerhalb der Gruppe</h3>
<p>Marvin ist bereits selbstständiger gebundener Versicherungsvermittler für ERGO (Einzelunternehmen). Der Vertrag erlaubt keine GmbH als Vermittler. Die Vermittlung bleibt deshalb persönlich neben der Gruppe:</p>
<pre style="font-size:8.5pt;line-height:1.35">Marvin Büscher
├── Einzelunternehmen: gebundener Versicherungsvermittler (ERGO)
└── Büscher Unternehmensgruppe GmbH (Holding)
    ├── Lotwerk GmbH (Marketing, Wachstumsberatung)
    ├── Immobilien GmbH (später)
    └── Bau GmbH (später)</pre>
<ul><li><b>Bis zur GmbH:</b> Die Agentur läuft als zweite Tätigkeit im bestehenden Einzelunternehmen oder als eigener Betrieb. Gewerbe-Ummeldung bzw. -Erweiterung und Finanzamt informieren [PRÜFEN Steuerberater: ein oder zwei Betriebe, getrennte Buchhaltung].</li>
<li><b>Kleinunternehmer:</b> Steuerfreie Versicherungsprovisionen zählen nicht zur Umsatzgrenze. Für die Grenze zählt nur der Agentur-Umsatz [PRÜFEN Steuerberater].</li>
<li><b>Rentenversicherung:</b> Selbstständige mit im Wesentlichen nur einem Auftraggeber und ohne Angestellte können rentenversicherungspflichtig sein (§ 2 Nr. 9 SGB VI). Mit der Agentur kommen weitere Auftraggeber dazu. Klären lassen bei der Deutschen Rentenversicherung (Statusfeststellung) [PRÜFEN].</li>
<li><b>ERGO-Vertrag:</b> Ob Nebentätigkeiten gemeldet oder genehmigt werden müssen, im Vertrag nachsehen [PRÜFEN].</li></ul>
<h3>Vorsicht bei Agentur plus Versicherung</h3>
<ul><li>Kundendaten der Agentur dürfen nicht ohne Einwilligung für Versicherungsangebote genutzt werden (Datenschutz).</li>
<li>Der ERGO-Vertrag kann andere Tätigkeiten oder Werbung unter eigenem Namen einschränken [PRÜFEN Vertrag].</li>
<li>Für die Vermittlung gelten weiter Vermittlerregister und Weiterbildungspflicht (15 Stunden im Jahr), unabhängig von der Agentur.</li>
<li>Für die Marke Lotwerk gilt: Kunden sollen nicht das Gefühl haben, dass die Website ein Türöffner für Versicherungen ist.</li></ul>
</section>
</body></html>"""

if __name__ == "__main__":
    (HERE / "Firmenuebersicht.html").write_text(HTML, encoding="utf-8")
    js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://{HERE}/Firmenuebersicht.html');await p.waitForTimeout(400);
await p.pdf({{path:'{HERE}/Firmenuebersicht.pdf',format:'A4',printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',
footerTemplate:'<div style="font-size:7pt;color:#888;width:100%;text-align:center;font-family:sans-serif">{NAME} · Firmenübersicht · Seite <span class=pageNumber></span> von <span class=totalPages></span></div>',
margin:{{top:'14mm',bottom:'14mm',left:'0',right:'0'}}}});await b.close();}})();"""
    (HERE / "_pdf.js").write_text(js)
    subprocess.run(["node", str(HERE / "_pdf.js")], check=True, env={**os.environ, "NODE_PATH": subprocess.check_output(["npm", "root", "-g"]).decode().strip()})
    (HERE / "_pdf.js").unlink()
    print("Firmenuebersicht.pdf erstellt")
