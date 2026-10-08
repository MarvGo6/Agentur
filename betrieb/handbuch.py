"""Erzeugt betrieb/Leistungshandbuch.html und .pdf – wie jede Leistung geliefert, geprüft und abgerechnet wird,
plus Textbausteine für Angebot/AGB und die Beschreibung der Datensammlung. Neu erzeugen: python3 betrieb/handbuch.py"""
import sys, json, subprocess, os
from pathlib import Path
from datetime import date
ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from content import PREISE as P, eur

NAME = json.loads((ROOT / "config.json").read_text())["name"]


def liste(xs): return "<ul>" + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"
def check(xs): return '<ul class="chk">' + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"
def tab(kopf, zeilen): return "<table><thead><tr>" + "".join(f"<th>{k}</th>" for k in kopf) + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in z) + "</tr>" for z in zeilen) + "</tbody></table>"


LEISTUNGEN = [
 {"titel": "Website Start", "preis": f"{eur(P['web_start'])} einmalig · Pflege {P['pflege_start']} €/Monat (12 Monate)", "dauer": "2–3 Wochen", "aufwand": "10–16 h",
  "enthalten": ["Bis zu 5 Seiten aus dem Baukasten (Aufbau passend zur Branche)", "Texte auf Basis des Inhalte-Formulars, vom Kunden freigegeben", "Kontaktformular, Telefon antippbar; Online-Terminbuchung: Anbindung Ihres Buchungsprogramms (Link oder eingebettet) inkl. Testbuchung, sonst Rückruf-Formular", "Google-Unternehmensprofil eingerichtet bzw. überarbeitet", "Impressum, Datenschutz (Vorlage, vom Kunden zu prüfen), strukturierte Daten (LocalBusiness)", "Domain-Anbindung, SSL, Weiterleitungen von der alten Seite"],
  "nicht": ["Fotoshooting vor Ort (Motivliste für Handyfotos wird gestellt)", "Shop, Mitgliederbereich, Schnittstellen zu Fremdsoftware", "Einrichtung eines neuen Buchungsprogramms (Kosten des Anbieters zahlt der Kunde direkt; Einrichtungspreis [PRÜFEN])", "Mehr als zwei Korrekturrunden"],
  "ablauf": [("Tag 1", "Ersteinschätzung, Angebot"), ("Tag 3", "Auftrag, 50 % Rechnung, Inhalte-Formular an Kunden"), ("Tag 3–8", "Kunde liefert Inhalte (Frist 7 Tage)"), ("Tag 10", "Entwurf im Browser, 1. Korrekturrunde"), ("Tag 14–21", "2. Runde, Abnahme, Livegang, 50 % Rechnung")]},
 {"titel": "Website Wachstum", "preis": f"{eur(P['web_wachstum'])} einmalig · Pflege {P['pflege_wachstum']} €/Monat (12 Monate)", "dauer": "3–4 Wochen", "aufwand": "16–28 h",
  "enthalten": ["Bis zu 15 Seiten: je Leistung und wichtigem Ort eine Seite", "Karriere- oder Bewerbungsbereich mit Kurzbewerbung", "Ratgeber-Bereich mit 2 Startartikeln", "Anruf- und Formularmessung (datenschutzfreundlich)", "Alles aus Website Start"],
  "nicht": ["Wie Website Start", "Laufende neue Inhalte (→ SEO Lokal/Plus)"],
  "ablauf": [("Woche 1", "Auftrag, Inhalte-Formular, Seitenplan"), ("Woche 2", "Entwurf Startseite + 2 Leistungsseiten"), ("Woche 3", "Alle Seiten, Korrekturen"), ("Woche 4", "Abnahme, Livegang, Profil, Messung")]},
 {"titel": "Pflege & Hosting", "preis": f"{P['pflege_start']} € (Start) bzw. {P['pflege_wachstum']} € (Wachstum) im Monat · 12 Monate, verlängert sich um 12 Monate, Kündigung 3 Monate vor Ablauf", "dauer": "laufend", "aufwand": "0,25–0,5 h je Kunde/Monat",
  "enthalten": ["Hosting (Vercel), SSL, tägliche Erreichbarkeitsprüfung (automatisch)", "Technische Aktualisierungen, Sicherung über Versionsverlauf (Git)", "Kleine Änderungen: Start nach Absprache, Wachstum bis 1 h/Monat", "Reaktion auf Störungen am selben Werktag"],
  "nicht": ["Neue Seiten oder Funktionen (Angebot nach Aufwand)", "Inhalte von Dritten (z. B. Buchungstool) – nur Einbindung"],
  "ablauf": [("Täglich", "Automatische Prüfung, Push bei Ausfall"), ("Montags", "PageSpeed-Messung (sobald API-Schlüssel hinterlegt)"), ("Bei Bedarf", "Änderungswünsche per E-Mail, Umsetzung binnen 3 Werktagen")]},
 {"titel": "SEO Lokal / SEO Plus", "preis": f"{P['seo_lokal']} € bzw. {P['seo_plus']} € im Monat · 6 Monate Mindestlaufzeit, danach monatlich", "dauer": "laufend", "aufwand": "5–8 h je Kunde/Monat",
  "enthalten": ["Google-Profil pflegen: Beiträge, Fotos, Leistungen, Antworten auf Bewertungen (Entwurf, Freigabe durch Kunden)", "Lokal: 1 neue oder überarbeitete Seite/Monat · Plus: 2–3", "Verzeichnis-Einträge einheitlich (Name, Adresse, Telefon)", "Plus: Bewertungsprozess (QR-Karte)", "Monatsbericht: Anrufe, Routen, Klicks, Anfragen, Platzierungen"],
  "nicht": ["Garantie bestimmter Platzierungen", "Linkkauf oder andere riskante Methoden"],
  "ablauf": [("Monat 1", "Bestandsaufnahme, Profil, Technik, Verzeichnisse"), ("Monat 2–6", "Inhalte nach Plan, Bewertungen"), ("Jeden Monat", "Bericht + 15 Minuten Gespräch (optional)")]},
 {"titel": "Google Ads", "preis": f"{eur(P['ads_setup'])} Einrichtung + {P['ads']} €/Monat · monatlich kündbar · Werbebudget direkt an Google", "dauer": "Start in 5 Werktagen", "aufwand": "4 h Einrichtung, 2–3 h/Monat",
  "enthalten": ["Konto auf den Namen des Kunden, Verwaltungszugriff für uns", "Kampagnen nur auf Suchbegriffe mit Kaufabsicht, Ausschlussliste", "Zielseite je Kampagne (bei Website-Kunden)", "Anruf- und Formularmessung", "In den ersten 4 Wochen wöchentliche, danach zweiwöchentliche Optimierung", "Monatsbericht: Kosten je Anfrage"],
  "nicht": ["Werbebudget (zahlt der Kunde direkt an Google)", "Display-, YouTube- oder Shopping-Kampagnen ohne gesondertes Angebot"],
  "ablauf": [("Tag 1–3", "Suchbegriffe, Budgetrechnung, Freigabe"), ("Tag 5", "Kampagne live"), ("Woche 2–4", "Lernphase, wöchentliche Anpassung"), ("Ab Monat 2", "Zweiwöchentliche Optimierung, Monatsbericht")],
  "hinweis": "Vor dem ersten Kunden: Google-Ads-Zertifizierung (Google Skillshop, kostenlos). Erste 1–2 Kunden als Pilot mit kleinem Budget."},
 {"titel": "Recruiting-Paket", "preis": f"{eur(P['rec_setup'])} Einrichtung + {P['rec']} €/Monat · 3 Monate Mindestlaufzeit · Werbebudget direkt an Meta/Google", "dauer": "Start in 2 Wochen", "aufwand": "10 h Einrichtung, 6–7 h/Monat",
  "enthalten": ["Karriereseite je Stelle mit Gehaltsrahmen, Team, echten Fotos", "Kurzbewerbung in 60 Sekunden (ohne Lebenslauf)", "Strukturierte Daten für Google Jobs", "Anzeigen im Umkreis (Meta; Stellenanzeigen-Vorgaben beachten)", "Jede Bewerbung sofort per E-Mail an den Kunden", "Monatsbericht: Bewerbungen, Kosten je Bewerbung"],
  "nicht": ["Einstellungsgarantie – wir liefern Bewerbungen, die Auswahl trifft der Kunde", "Bewerbergespräche, Vorauswahl"],
  "ablauf": [("Woche 1", "Arbeitgeber-Check, Fotos, Gehaltsrahmen freigeben"), ("Woche 2", "Karriereseite + Kampagne live"), ("Woche 3–6", "Anzeigen nach Bewerbungsqualität anpassen")],
  "hinweis": "Pflicht des Kunden: Bewerber innerhalb von 48 Stunden zurückrufen – sonst verpufft die Kampagne."},
 {"titel": "Wachstumsprogramm", "preis": f"{eur(P['prog_setup'])} Einrichtung (inkl. Website) + {eur(P['programm'])}/Monat · 12 Monate", "dauer": "laufend", "aufwand": "12 h Einrichtung, 13 h/Monat",
  "enthalten": ["Website Wachstum, Pflege, SEO Plus und Google-Ads-Betreuung", "Ein messbares Ziel, vorher schriftlich vereinbart (z. B. Anfragen/Monat)", "Monatliches Gespräch (30 Min.) mit Zahlen", "Quartalsplanung"],
  "nicht": ["Werbebudget", "Ergebnisgarantie – bei deutlicher Planabweichung nach 6 Monaten Umwandlung in reine Pflege möglich"],
  "ablauf": [("Monat 1", "Website, Profil, Messung, erste Kampagnen"), ("Monat 2–6", "Inhalte, Bewertungen, Anzeigen nachschärfen"), ("Monat 7–12", "Ausbauen, was wirkt")]},
]

ABNAHME = ["Lighthouse (Handy): Leistung, Barrierefreiheit, Best Practices, SEO jeweils ≥ 90 – Ziel, Abweichung begründen",
           "Auf iPhone und Android geprüft: keine abgeschnittenen Texte, kein seitliches Scrollen, Buttons gut erreichbar",
           "Telefonnummer antippbar, Formular-Testanfrage kommt beim Kunden an",
           "Impressum und Datenschutz vorhanden und vom Kunden bestätigt",
           "Cookie-Check: Browser-Entwicklertools → Anwendung → Cookies/Speicher leer beim ersten Aufruf; Netzwerk zeigt keine Anfragen an Google, Meta & Co. vor der Einwilligung",
           "Keine externen Schriften; Karten und Videos nur per Zwei-Klick-Lösung; Einwilligungs-Baustein nur, wenn zustimmungspflichtige Dienste genutzt werden",
           "Strukturierte Daten (LocalBusiness) gültig, Seitentitel und Beschreibungen gesetzt",
           "Alle Bilder mit Alt-Text, eine H1 pro Seite",
           "Kein Platzhalter [PRÜFEN] mehr im Inhalt; alle Aussagen vom Kunden belegt",
           "Weiterleitungen alter Adressen eingerichtet, Google-Profil verlinkt",
           "Website zur Überwachung angemeldet (Tabelle websites)"]

INHALTE = ["Betriebsname, Adresse, Telefon, E-Mail, Öffnungszeiten", "Einzugsgebiet: Orte, die Sie anfahren bzw. aus denen Kunden kommen",
           "Leistungen: Was bieten Sie an? Welche drei bringen das meiste Geld?", "Preise oder Preisrahmen, die gezeigt werden dürfen",
           "Was unterscheidet Sie? (Meisterbetrieb, Erfahrung, Spezialisierung – nur Belegbares)", "Team: Namen, Rollen, Fotos (mit Einverständnis)",
           "Fotos: 15–30 Bilder nach Motivliste (Team, Arbeiten, Räume, Fahrzeuge)", "Logo als Datei, Farben falls vorhanden",
           "Bewertungen: Link zum Google-Profil, Erlaubnis zum Zitieren", "Zugänge: Domain, Google-Profil, ggf. alte Website",
           "Stellen (bei Recruiting): Gehaltsrahmen, Arbeitszeiten, Vorteile", "Wer gibt Inhalte frei und ist Ansprechpartner?"]

BERICHT = ["Kurzfazit in drei Sätzen", "Anfragen: Formular, Anrufe, E-Mails – mit Vormonat", "Sichtbarkeit: Profilaufrufe, Routen, Klicks aus Google",
           "Platzierungen für 5–10 wichtige Suchbegriffe", "Was wir getan haben (Liste)", "Was wir nächsten Monat tun", "Was wir vom Kunden brauchen"]

BAUSTEINE = [
 ("Leistungsumfang", "Der Umfang ergibt sich abschließend aus dem Angebot und dieser Leistungsbeschreibung. Zusätzliche Leistungen werden vorab angeboten und nur nach Freigabe erbracht."),
 ("Mitwirkung", "Der Kunde stellt Inhalte, Fotos und Zugänge innerhalb von 7 Tagen nach Auftrag bereit und benennt eine Person für Freigaben. Verzögerungen verschieben den Zeitplan entsprechend."),
 ("Abnahme & Zahlung", "Einmalige Leistungen: 50 % bei Auftrag, 50 % nach Abnahme des Entwurfs. Der Entwurf gilt als abgenommen, wenn der Kunde nicht innerhalb von 10 Tagen begründete Mängel mitteilt. Zwei Korrekturrunden sind enthalten."),
 ("Laufzeiten", "Pflege & Hosting: 12 Monate, Verlängerung um jeweils 12 Monate, Kündigung 3 Monate vor Ablauf. SEO: 6 Monate Mindestlaufzeit, danach monatlich kündbar. Recruiting: 3 Monate, danach monatlich. Google Ads: monatlich kündbar. Wachstumsprogramm: 12 Monate."),
 ("Werbebudgets", "Werbebudgets für Google, Meta o. Ä. zahlt der Kunde direkt an die Plattform. Die Konten laufen auf den Namen des Kunden."),
 ("Keine Ergebnisgarantie", "Platzierungen, Anfragen oder Bewerbungen hängen von Dritten (Suchmaschinen, Markt, Wettbewerb) ab und werden nicht garantiert. Geschuldet ist die sorgfältige Erbringung der beschriebenen Leistungen."),
 ("Eigentum", "Nach vollständiger Zahlung erhält der Kunde die Nutzungsrechte an Website, Texten und Gestaltung. Domain und Konten laufen auf den Kunden. Bei Vertragsende werden alle Dateien übergeben."),
 ("Rechtstexte", "Impressum- und Datenschutz-Vorlagen sind eine Arbeitshilfe. Die Verantwortung für die rechtliche Richtigkeit trägt der Kunde; eine Rechtsberatung erfolgt nicht."),
 ("Datenschutz", "Soweit personenbezogene Daten (z. B. Formularanfragen) verarbeitet werden, schließen die Parteien einen Auftragsverarbeitungsvertrag."),
]

DATEN = [
 ("Anfragen über deine Website", "agentur_anfragen", "bei jedem Absenden", "Push aufs Handy, Wochenbericht, Abfrage 8"),
 ("Seitenaufrufe & Klicks (anonym)", "seitenaufrufe", "bei jedem Besuch", "Welche Seiten führen zur Ersteinschätzung? Abfragen 5–7"),
 ("Website-Analyse von Interessenten", "interessenten (befund, potenzial)", "alle 30 Min., je 3", "Liste der besten Chancen (Abfrage 2), Befund für die Präsentation (Abfrage 3)"),
 ("Überwachung aller Websites", "checks, messwerte, aufgaben", "täglich 7:15 Uhr, PageSpeed montags", "Push bei Ausfall, offene Aufgaben (Abfrage 10)"),
 ("Wochen- und Monatsbericht", "berichte", "Mo 8:00 Uhr · am 1. 8:30 Uhr", "Push mit Kurzfassung, Verlauf (Abfrage 9)"),
 ("Kunden, Verträge, Rechnungen, Zeiten", "kunden, vertraege, rechnungen, zeiten, kosten", "manuell bzw. später Lexware-Abgleich", "MRR, Deckungsbeitrag je Kunde (Sichten)"),
]

def leistung(l, i):
    ab = "".join(f"<tr><td class='t'>{a}</td><td>{b}</td></tr>" for a, b in l["ablauf"])
    hin = f'<div class="box warn">{l["hinweis"]}</div>' if l.get("hinweis") else ""
    return f'''<section class="lst"><h2><small class="nr">{i:02d}</small>{l["titel"]}</h2>
<dl class="eck"><div><dt>Preis</dt><dd>{l["preis"]}</dd></div><div><dt>Dauer</dt><dd>{l["dauer"]}</dd></div><div><dt>Dein Aufwand</dt><dd>{l["aufwand"]}</dd></div></dl>
<div class="cols"><div><h3>Enthalten</h3>{check(l["enthalten"])}</div><div><h3>Nicht enthalten</h3>{liste(l["nicht"])}<h3>Ablauf</h3><table class="ab">{ab}</table></div></div>{hin}</section>'''

HTML = f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><title>{NAME} – Leistungshandbuch</title><style>
@font-face{{font-family:"Inter Tight";src:url(../static/fonts/intertight.woff2);font-weight:100 900}}@font-face{{font-family:"Instrument Serif";src:url(../static/fonts/instrumentserif-italic.woff2);font-style:italic}}
@page{{size:A4;margin:18mm 0}}
body{{font:9.4pt/1.5 "Inter Tight",sans-serif;color:#0f0f0e;margin:0;padding:0 18mm}}
h1,h2,h3{{font-weight:500;letter-spacing:-.02em;line-height:1.1}}h1{{font-size:36pt;margin:0;letter-spacing:-.04em}}h1 em,h2 em{{font-family:"Instrument Serif";font-weight:400;color:#e84300}}
h2{{font-size:18pt;margin:0 0 10pt;border-top:1.5px solid #0f0f0e;padding-top:8pt}}h3{{font-size:11pt;font-weight:600;margin:10pt 0 4pt}}
.nr{{font-size:9pt;color:#ad3300;margin-right:8pt;font-weight:500}}
p{{margin:0 0 6pt}}ul{{margin:0 0 6pt;padding-left:14pt}}li{{margin:2pt 0}}
.chk{{list-style:none;padding:0}}.chk li{{padding-left:14pt;position:relative}}.chk li::before{{content:"";position:absolute;left:0;top:5pt;width:6pt;height:6pt;background:#e84300}}
.page{{break-before:page}}.lst{{break-inside:avoid;margin-bottom:16pt}}
table{{width:100%;border-collapse:collapse;font-size:8.8pt;margin:4pt 0 10pt}}th,td{{padding:4.5pt 5pt;border-bottom:1px solid #d3cfc4;text-align:left;vertical-align:top}}th{{font-weight:500;color:#5a5852;border-bottom-color:#0f0f0e}}
table.ab td.t{{width:62pt;color:#ad3300;font-weight:500}}
.eck{{display:grid;grid-template-columns:2fr 1fr 1fr;gap:0;margin:0 0 6pt;border-bottom:1px solid #d3cfc4}}.eck div{{padding:4pt 8pt 6pt 0}}.eck dt{{color:#5a5852;font-size:8pt}}.eck dd{{margin:0;font-weight:500}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:18pt}}
.box{{border-left:2px solid #e84300;padding:5pt 10pt;margin:8pt 0;background:#f6f4ef}}.warn{{background:#fbefe8}}
.small{{font-size:8.2pt;color:#5a5852}}.cover{{min-height:250mm;display:flex;flex-direction:column;justify-content:space-between}}
pre{{font:7.6pt/1.4 ui-monospace,Menlo,monospace;background:#f6f4ef;padding:8pt;white-space:pre-wrap}}
</style></head><body>
<section class="cover"><div><p class="small">Leistungshandbuch · intern · Stand {date.today().strftime('%d.%m.%Y')}</p><h1>So liefern wir, <em>was wir verkaufen.</em></h1>
<p style="max-width:120mm;margin-top:14pt;font-size:11pt">Für jede Leistung: Umfang, Ablauf, Abnahme und dein Zeitaufwand. Dazu Vorlagen, Textbausteine für Angebot und AGB und die automatische Datensammlung.</p></div>
<div class="box">Grundregel: Nur verkaufen, was in diesem Handbuch beschrieben ist. Alles andere wird vorher als Zusatzangebot geklärt.</div></section>

<section class="page"><h2><small class="nr">00</small>Grundsätze</h2>
<div class="cols"><div><h3>Qualität</h3>{check(["Bauen aus erprobten Bausteinen (Generator), nicht bei null", "Jede Website besteht die Abnahme-Checkliste (Kapitel 08)", "KI schreibt Entwürfe – du prüfst, der Kunde gibt frei", "Nichts erfinden: Zahlen, Bewertungen, Zertifikate nur mit Beleg"])}
<h3>Kommunikation</h3>{liste(["Antwort auf Kundenanfragen innerhalb eines Werktags", "Störungen: Reaktion am selben Werktag", "Ein fester Ansprechpartner, alles schriftlich per E-Mail bestätigt"])}</div>
<div><h3>Wochenstruktur (allein)</h3>{tab(["Tag", "Schwerpunkt"], [["Montag", "Vertrieb: Interessenten, Ersteinschätzungen, Angebote"], ["Di–Do", "Umsetzung: Websites, Einrichtungen"], ["Freitag", "Pflege, SEO- und Ads-Kontrolle, Berichte, Verwaltung"]])}
<h3>Kapazität & Vertretung</h3>{liste(["Grenze 170 h/Monat – ist der Monat voll, Start im Folgemonat statt Überlastung", "Zeiten je Kunde erfassen (Tabelle zeiten) – zeigt echten Stundenlohn", "1–2 Freelancer (Texte, Ads) als Vertretung vorab finden", "Alle Zugänge beim Kunden, dokumentiert im Passwort-Manager"])}</div></div>
<h3>Vor dem ersten Kunden erledigen</h3>{check(["AGB + Auftragsverarbeitungsvertrag (Vorlage mit Bausteinen aus Kapitel 09, anwaltlich prüfen lassen)", "Berufs- bzw. IT-Haftpflicht (ca. 15–30 €/Monat)", "Google-Ads-Zertifizierung (Skillshop, kostenlos)", "Vercel Pro und Supabase Pro (kommerzielle Nutzung, Backups)", "Google-PageSpeed-API-Schlüssel hinterlegen (Kapitel 10)"])}</section>

<section class="page">{"".join(leistung(l, i) for i, l in enumerate(LEISTUNGEN, 1))}</section>

<section class="page"><h2><small class="nr">08</small>Abnahme-Checkliste Website</h2>{check(ABNAHME)}
<h2 style="margin-top:18pt"><small class="nr">08b</small>Inhalte-Formular für Kunden</h2><p class="small">Wird nach Auftrag verschickt (später als Formular im Dashboard). Frist: 7 Tage.</p>{liste(INHALTE)}
<h2 style="margin-top:18pt"><small class="nr">08c</small>Monatsbericht – Gliederung</h2><p class="small">Eine Seite. Die Zahlen kommen automatisch aus der Datenbank, der Text als KI-Entwurf zur Freigabe.</p>{liste(BERICHT)}</section>

<section class="page"><h2><small class="nr">09</small>Textbausteine für Angebot und AGB</h2>
<div class="box warn">Arbeitsgrundlage – vor Verwendung anwaltlich prüfen lassen (insbesondere Verlängerungsklausel, Abnahmefiktion, Haftung).</div>
{tab(["Thema", "Formulierung"], [[a, b] for a, b in BAUSTEINE])}</section>

<section class="page"><h2><small class="nr">10</small>Daten sammeln, auswerten, nutzen</h2>
<p>Alles läuft im Supabase-Projekt „Lotwerk Agentur“ (EU). Zeitgesteuert über Datenbank-Jobs, die drei Funktionen (<i>monitor</i>, <i>analyse</i>, <i>bericht</i>) aufrufen. Ergebnisse kommen als Push über ntfy aufs Handy.</p>
{tab(["Was", "Wo (Tabelle)", "Wann", "Wofür"], [list(d) for d in DATEN])}
<h3>So nutzt du die Daten</h3>{liste(["<b>Interessenten analysieren:</b> Betrieb mit Website in die Tabelle <i>interessenten</i> eintragen – nach spätestens 30 Minuten stehen Potenzial (0–100) und Befund in Klartext da. Der Befund passt direkt auf die Folie „Ausgangslage“ der Präsentation „Persönliche Analyse“.", "<b>Website verbessern:</b> Konversion je Seite (Abfrage 6) zeigt, welche Seiten zur Ersteinschätzung führen – schwache Seiten überarbeiten.", "<b>Planen:</b> Wochenbericht montags aufs Handy; Monatsbericht für den Vergleich mit dem Finanzmodell.", "<b>Später:</b> Das Dashboard liest dieselben Tabellen – keine Doppelpflege."])}
<p>Fertige Abfragen: <code>betrieb/abfragen.sql</code> (Supabase → SQL Editor → einfügen → Run).</p>
<h3>Offen</h3>{liste(["<b>Google-PageSpeed-API-Schlüssel</b> (kostenlos, Google Cloud Console → „PageSpeed Insights API“ aktivieren → API-Schlüssel). Ohne Schlüssel liefert Google oft keine Messung. Eintragen: <code>insert into einstellungen values ('psi_key','DEIN-SCHLÜSSEL');</code>", "Search Console und Google-Profil-Daten je Kunde (benötigt Freigabe des Kunden, Stufe 4 im Betriebsplan)"])}
<h3>Datenschutz</h3>{liste(["Seitenaufrufe anonym: keine Cookies, keine IP-Speicherung, keine Kennung; kein Zugriff auf Informationen im Endgerät (§ 25 TDDDG) – gezählt werden nur Seite und Ereignis; Löschung nach 25 Monaten (automatisch im Monatsbericht)", "Datenschutzerklärung der Website ist entsprechend ergänzt", "Website-Analysen nutzen nur öffentlich abrufbare Seiten der Betriebe"])}</section>

<section class="page"><h2><small class="nr">11</small>Cookies und Einwilligung</h2>
<div class="box warn">Zusammenfassung der Rechtslage zur Orientierung, keine Rechtsberatung. Für die eigenen AGB, Datenschutzerklärungen und Sonderfälle anwaltlich prüfen lassen.</div>
<h3>Die Regeln in einem Satz je Gesetz</h3>{tab(["Regel", "Bedeutung für Websites"], [
 ["§ 25 TDDDG", "Wer Informationen im Endgerät speichert oder ausliest (Cookies, localStorage, Fingerprinting, Bildschirmgröße), braucht eine Einwilligung – außer es ist für den vom Nutzer gewünschten Dienst unbedingt erforderlich."],
 ["Art. 6 und 7 DSGVO", "Einwilligung muss freiwillig, informiert, eindeutig und jederzeit so leicht widerrufbar sein, wie sie erteilt wurde."],
 ["Art. 44 ff. DSGVO", "Übermittlung in Drittländer (z. B. USA) nur mit Grundlage – Dienste mit EU-Sitz oder EU-US Data Privacy Framework bevorzugen und in der Datenschutzerklärung nennen."],
 ["Rechtsprechung / Aufsicht", "„Ablehnen“ auf der ersten Ebene gleichwertig zu „Akzeptieren“; keine vorangekreuzten Kästchen; keine Dienste vor der Entscheidung laden; Google Fonts vom Google-Server ohne Einwilligung wurde abgemahnt (LG München I, 2022)."]])}
<h3>Lotwerk-Standard für Kunden-Websites</h3>{check([
 "<b>Grundsatz: ohne Banner auskommen.</b> Schriften lokal, Formulare über unsere Funktion, Statistik ohne Cookies (z. B. unsere anonyme Zählung oder eine cookielose Lösung mit EU-Hosting). Dann ist kein Banner nötig.",
 "<b>Nur wenn der Kunde Google Ads-Conversion, Meta-Pixel o. Ä. will:</b> Einwilligungs-Baustein <code>betrieb/bausteine/einwilligung.js</code> einbinden. Er startet Google Consent Mode v2 mit „abgelehnt“, lädt nichts vor der Zustimmung und zeigt drei gleich gestaltete Knöpfe.",
 "<b>Karten und Videos</b> als Zwei-Klick-Lösung (<code>&lt;div class=\"lw-extern\" …&gt;</code>) – Platzhalter mit Hinweis, Laden erst nach Klick. Alternative: statisches Kartenbild mit Link zu Google Maps.",
 "<b>Widerruf</b>: Link „Datenschutz-Einstellungen“ im Fußbereich (<code>data-einwilligung</code>).",
 "<b>Datenschutzerklärung</b> nennt jeden Dienst mit Anbieter, Zweck, Rechtsgrundlage, Speicherdauer und Drittlandbezug.",
 "<b>Erneute Abfrage</b> nach 12 Monaten oder sobald ein Dienst dazukommt (macht der Baustein automatisch)."])}
<h3>Im Vertrieb nutzen</h3><p>Die automatische Website-Analyse meldet jetzt auch: Tracking ohne erkennbare Einwilligung, direkt eingebettete Karten/Videos, fehlende Links zu Impressum und Datenschutz, Google Fonts von Google-Servern. Das sind sachliche Punkte für die „Persönliche Analyse“ – als Risiko benennen, nicht als Rechtsberatung.</p></section>
</body></html>"""

if __name__ == "__main__":                       # beim Import (z. B. betrieb/uebersicht.py) nur Daten, keine Dateien
    (HERE / "Leistungshandbuch.html").write_text(HTML, encoding="utf-8")
    js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage();
    await p.goto('file://{HERE}/Leistungshandbuch.html');await p.waitForTimeout(400);
    await p.pdf({{path:'{HERE}/Leistungshandbuch.pdf',format:'A4',printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',
    footerTemplate:'<div style="font-size:7pt;color:#888;width:100%;text-align:center;font-family:sans-serif">{NAME} · Leistungshandbuch · Seite <span class=pageNumber></span> von <span class=totalPages></span></div>',
    margin:{{top:'16mm',bottom:'16mm',left:'0',right:'0'}}}});await b.close();}})();"""
    (HERE / "_pdf.js").write_text(js)
    subprocess.run(["node", str(HERE / "_pdf.js")], check=True, env={**os.environ, "NODE_PATH": subprocess.check_output(["npm", "root", "-g"]).decode().strip()})
    (HERE / "_pdf.js").unlink()
    print("Leistungshandbuch.pdf erstellt")
