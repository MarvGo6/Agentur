"""Erzeugt betrieb/Betriebsplan.html und .pdf – den vertieften Businessplan für Struktur, Werkzeuge, Abläufe und Automatisierung.
Zahlen kommen aus finanzen/modell.py; der Master-Prompt aus betrieb/PROMPT.md. Neu erzeugen: python3 betrieb/plan.py"""
import sys, json, re, html, subprocess, os
from pathlib import Path
from datetime import date
ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "finanzen")); sys.path.insert(0, str(ROOT))
import modell as M
from content import PREISE as P, eur

NAME = json.loads((ROOT / "config.json").read_text())["name"]
def e0(v): return eur(round(v))

# ------------------------------------------------------------------ Wirkung der Automatisierung (Variante "automatisiert ab Kunde 5" im Finanzmodell)
AUTO = {k: M.G["a_" + k] for k in M.STUNDEN_KEYS}
HEUTE, AUTOM = M.rechne("Basis"), M.rechne("Basis", variante="auto")
M.SZENARIEN["Maximal"] = [6, 8]                      # Nachfrage unbegrenzt -> reine Kapazitätsgrenze
CAP0, CAP1 = M.rechne("Maximal")[23]["mrr"], M.rechne("Maximal", variante="auto")[23]["mrr"]
del M.SZENARIEN["Maximal"]
H0, H1 = M.h_neu(), M.h_neu(auto_an=True)
ERG0, ERG1 = sum(x["ergebnis"] for x in HEUTE[:24]), sum(x["ergebnis"] for x in AUTOM[:24])
def kunden(x): return x["k_pflege"] + x["k_prog"] + x["k_seo"] + x["k_rec"]
def monat_ab(n): return next(x["label"] for x in HEUTE if kunden(x) >= n)
VOLL = next((x["label"] for x in HEUTE if x["stunden"] >= M.G["kapazitaet"] - 0.5), "–")

STUNDEN = [  # Aufgabe, heute (Finanzmodell), automatisiert (Ziel), was die Zeit spart
    ("Vertrieb je Abschluss", M.G["h_vertrieb"], AUTO["h_vertrieb"], "Lead-Liste, Schnell-Analyse und Vorschau entstehen automatisch"),
    ("Neue Website", M.G["h_setup_web"], AUTO["h_setup_web"], "KI baut aus Formular + Vorschau, Prüfung läuft automatisch"),
    ("Einrichtung Wachstumsprogramm", M.G["h_setup_prog"], AUTO["h_setup_prog"], "Website, Profil, Tracking aus Vorlagen"),
    ("Einrichtung SEO", M.G["h_setup_seo"], AUTO["h_setup_seo"], "Audit + Ortsseiten als KI-Entwurf"),
    ("Einrichtung Recruiting", M.G["h_setup_rec"], AUTO["h_setup_rec"], "Karriereseite + Anzeigentexte aus Bausteinen"),
    ("Programm-Kunde je Monat", M.G["h_mon_prog"], AUTO["h_mon_prog"], "Bericht, Checks, Vorschläge automatisch"),
    ("SEO-Kunde je Monat", M.G["h_mon_seo"], AUTO["h_mon_seo"], "Messwerte + Verbesserungs-PRs von KI"),
    ("Recruiting-Kunde je Monat", M.G["h_mon_rec"], AUTO["h_mon_rec"], "Kennzahlen + Textvarianten automatisch"),
]

# ------------------------------------------------------------------ Bausteine
WER = {"du": ("Du", "#0f5c4a", "#fff"), "ki": ("KI", "#5b6fc4", "#fff"), "auto": ("Automatik", "#e4ddd0", "#1c2220"), "kunde": ("Kunde", "#b0602a", "#fff")}
def wer(*k): return " ".join(f'<span class="tag" style="background:{WER[x][1]};color:{WER[x][2]}">{WER[x][0]}</span>' for x in k)
def kap(nr, titel): return f'<h2><small class="nr">{nr:02d}</small>{titel}</h2>'
def tab(kopf, zeilen, cls=""):
    return (f'<table class="{cls}"><thead><tr>{"".join(f"<th>{k}</th>" for k in kopf)}</tr></thead><tbody>'
            + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in z) + "</tr>" for z in zeilen) + "</tbody></table>")

def ablauf(buchst, titel, ziel, ausloeser, schritte, vorher, nachher, kennz):
    rows = "".join(f'<tr><td class="n">{i}</td><td>{s}</td><td>{wer(*w)}</td><td>{t}</td><td>{erg}</td></tr>' for i, (s, w, t, erg) in enumerate(schritte, 1))
    return f'''<div class="flow"><div class="flow-h"><span class="big">{buchst}</span><div><h3>{titel}</h3><p class="small">{ziel}</p></div>
<div class="zeit"><b>{vorher}</b> → <b class="g">{nachher}</b><span>deine Zeit</span></div></div>
<p class="small"><b>Auslöser:</b> {ausloeser}</p>
<table class="ft"><thead><tr><th></th><th>Schritt</th><th>Wer</th><th>Werkzeug</th><th>Ergebnis</th></tr></thead><tbody>{rows}</tbody></table>
<p class="small"><b>Kennzahlen:</b> {kennz}</p></div>'''

# ------------------------------------------------------------------ Diagramme
def architektur():
    W, H = 640, 330
    def box(x, y, w, h, t, s="", fill="#fff", stroke="#cfc6b6", tc="#1c2220"):
        sub = f'<text x="{x+w/2}" y="{y+h/2+13}" text-anchor="middle" font-size="8.5" fill="{tc}" opacity=".8">{s}</text>' if s else ""
        return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}"/><text x="{x+w/2}" y="{y+h/2+(0 if s else 4)}" text-anchor="middle" font-weight="600" font-size="10.5" fill="{tc}">{t}</text>{sub}'
    def pfeil(x1, y1, x2, y2): return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#8a8172" stroke-width="1.3" marker-end="url(#a)"/>'
    g = ['<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0L10,5L0,10z" fill="#8a8172"/></marker></defs>']
    g.append(box(170, 6, 300, 44, "Dashboard (nur du, iPhone + Laptop)", "Cockpit · Pipeline · Kunden · Websites · Freigaben", "#0f5c4a", "#0f5c4a", "#fff"))
    g.append(box(170, 120, 300, 54, "Supabase „Lotwerk Agentur“ (EU)", "eine Datenbank · Login · Edge Functions · Cron", "#f3efe6", "#0f5c4a"))
    g.append(pfeil(320, 118, 320, 52)); g.append(pfeil(330, 52, 330, 118))
    links = [("GitHub", "Code · Freigaben (PR) · Actions"), ("Claude API", "Texte · Analysen · Vorschläge"), ("Google-Daten", "Places · Search Console · PageSpeed")]
    for i, (t, s) in enumerate(links):
        y = 80 + i * 62; g.append(box(6, y, 140, 48, t, s)); g.append(pfeil(146, y + 24, 168, 147))
    rechts = [("Lexware Office", "Angebote · Rechnungen · Belege"), ("GoCardless + Bank", "Lastschrift · Kontoumsätze"), ("ntfy + E-Mail", "Push · Berichte · Anfragen")]
    for i, (t, s) in enumerate(rechts):
        y = 80 + i * 62; g.append(box(494, y, 140, 48, t, s)); g.append(pfeil(492, y + 24, 472, 147))
    g.append(box(130, 240, 380, 40, "lotwerk-sites (Monorepo): Generator + kunde.json je Kunde", "", "#fff", "#5b6fc4"))
    g.append(pfeil(320, 238, 320, 176))
    for i, t in enumerate(["Kunde A", "Kunde B", "Kunde C", "Kunde …"]):
        x = 130 + i * 97; g.append(box(x, 296, 89, 28, t, "", "#efe8db")); g.append(pfeil(x + 44, 282, x + 44, 294))
    g.append('<text x="520" y="315" font-size="8.5" fill="#4a524f">je Kunde ein Vercel-Projekt</text>')
    return f'<svg viewBox="0 0 {W} {H}" class="chart" font-family="Inter,sans-serif">{"".join(g)}</svg>'

def mrr_vergleich():
    W, H, l, t, r, b = 640, 250, 62, 16, 150, 34
    ymax = 32000
    sx = lambda m: l + (m - 1) / 23 * (W - l - r); sy = lambda v: t + (1 - v / ymax) * (H - t - b)
    g = [f'<line x1="{l}" x2="{W-r}" y1="{sy(v):.1f}" y2="{sy(v):.1f}" stroke="#e4ddd0"/><text x="{l-8}" y="{sy(v)+4:.1f}" text-anchor="end">{eur(v)}</text>' for v in range(0, ymax + 1, 8000)]
    g += [f'<text x="{sx(m):.1f}" y="{H-b+18}" text-anchor="middle">{M.label(m)}</text>' for m in (1, 6, 12, 18, 24)]
    for rows, c, n in ((HEUTE, "#c26a2e", "heute (alles von Hand)"), (AUTOM, "#1a8a68", "automatisiert ab Kunde 5")):
        g.append(f'<polyline points="{" ".join(f"{sx(x["monat"]):.1f},{sy(x["mrr"]):.1f}" for x in rows)}" fill="none" stroke="{c}" stroke-width="2.4"/>')
        g.append(f'<text x="{sx(24)+8:.1f}" y="{sy(rows[-1]["mrr"])+4:.1f}" fill="{c}" font-weight="600">{e0(rows[-1]["mrr"])}</text><text x="{sx(24)+8:.1f}" y="{sy(rows[-1]["mrr"])+16:.1f}" font-size="8.5">{n}</text>')
    g.append(f'<line x1="{l}" x2="{W-r}" y1="{sy(10000):.1f}" y2="{sy(10000):.1f}" stroke="#1c2220" stroke-dasharray="4 4"/><text x="{l+6}" y="{sy(10000)-5:.1f}" fill="#1c2220">10.000 € – Start Team</text>')
    return f'<svg viewBox="0 0 {W} {H}" class="chart" font-size="10" fill="#4a524f" font-family="Inter,sans-serif">{"".join(g)}</svg>'

def cockpit():
    W, H = 640, 250
    g = ['<rect width="640" height="250" rx="10" fill="#16201c"/>', '<text x="18" y="26" fill="#efe9de" font-size="12" font-weight="600" font-family="Fraunces,serif">Cockpit</text><text x="622" y="26" fill="#7fd1b2" font-size="9" text-anchor="end">Heute · 3 Freigaben offen</text>']
    kp = [("MRR", "7.907 €", "+1.737 € ggü. Vormonat"), ("Ziel 10k", "79 %", "Basis-Plan: Mai 27"), ("Kasse", "41.380 €", "2 Rechnungen offen"), ("Auslastung", "142 / 170 h", "28 h frei")]
    for i, (a, b, c) in enumerate(kp):
        x = 18 + i * 153; g.append(f'<rect x="{x}" y="40" width="143" height="66" rx="8" fill="#22302a"/><text x="{x+12}" y="58" fill="#b9c2bd" font-size="8.5">{a}</text><text x="{x+12}" y="82" fill="#e8a26b" font-size="17" font-weight="600" font-family="Fraunces,serif">{b}</text><text x="{x+12}" y="98" fill="#b9c2bd" font-size="8">{c}</text>')
    g.append('<rect x="18" y="118" width="300" height="118" rx="8" fill="#22302a"/><text x="30" y="136" fill="#efe9de" font-size="9.5" font-weight="600">Freigaben &amp; Aufgaben</text>')
    for i, (t, c) in enumerate([("KI-Vorschlag: Ortsseite Nordheim · Brandt", "#5b6fc4"), ("Monatsbericht Kanzlei Weidner prüfen", "#5b6fc4"), ("SSL läuft in 9 Tagen ab · kamm-kante.de", "#e0965e"), ("Vorschau senden: Pflege am Lindenhof", "#7fd1b2")]):
        y = 154 + i * 20; g.append(f'<circle cx="34" cy="{y-3}" r="3.5" fill="{c}"/><text x="44" y="{y}" fill="#c9d3ce" font-size="8.5">{t}</text>')
    g.append('<rect x="330" y="118" width="292" height="118" rx="8" fill="#22302a"/><text x="342" y="136" fill="#efe9de" font-size="9.5" font-weight="600">MRR Plan vs. Ist</text>')
    pts_p = " ".join(f"{342+i*24},{226-v/14000*80:.0f}" for i, v in enumerate([1284, 2529, 4378, 6170, 7907, 9320, 10421, 11280, 11949, 12471, 12877])); g.append(f'<polyline points="{pts_p}" fill="none" stroke="#5f6b66" stroke-dasharray="3 3" stroke-width="1.5"/>')
    pts_i = " ".join(f"{342+i*24},{226-v/14000*80:.0f}" for i, v in enumerate([1100, 2700, 4600, 6200, 7907])); g.append(f'<polyline points="{pts_i}" fill="none" stroke="#7fd1b2" stroke-width="2.2"/>')
    g.append('<text x="610" y="232" fill="#b9c2bd" font-size="7.5" text-anchor="end">gestrichelt = Plan · grün = Ist (Beispielwerte)</text>')
    return f'<svg viewBox="0 0 {W} {H}" class="chart" font-family="Inter,sans-serif">{"".join(g)}</svg>'

# ------------------------------------------------------------------ Markdown (für den Prompt im Anhang)
def md(text):
    out, liste = [], None
    def inline(s):
        s = html.escape(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s); s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
        return s
    for line in text.splitlines():
        m = re.match(r"^(\s*)(\d+\.|-)\s+(.*)", line)
        if m:
            typ = "ol" if m.group(2)[0].isdigit() else "ul"
            if liste != typ:
                if liste: out.append(f"</{liste}>")
                out.append(f"<{typ}>"); liste = typ
            out.append(f"<li>{inline(m.group(3))}</li>"); continue
        if liste: out.append(f"</{liste}>"); liste = None
        if line.startswith("# "): continue
        if line.startswith("## "): out.append(f"<h3>{inline(line[3:])}</h3>")
        elif line.startswith("> "): out.append(f'<p class="small">{inline(line[2:])}</p>')
        elif line.strip() == "---": out.append("")
        elif line.strip(): out.append(f"<p>{inline(line)}</p>")
    if liste: out.append(f"</{liste}>")
    return "\n".join(out)

PROMPT = md((HERE / "PROMPT.md").read_text(encoding="utf-8"))
KUNDE_JSON = html.escape((HERE / "kunde.beispiel.json").read_text(encoding="utf-8"))

# ------------------------------------------------------------------ Inhalte
WERKZEUGE = [
    ("Code &amp; Freigaben", "GitHub", "vorhanden", "0 €", "Jede Änderung als Pull Request, Actions für Builds und Prüfungen", "GitLab"),
    ("Hosting Kunden-Sites", "Vercel Pro", "1", "ca. 19 €", "Hobby-Plan ist nicht für kommerzielle Nutzung erlaubt", "Netlify, Cloudflare Pages"),
    ("Datenbank, Login, Cron", "Supabase Pro", "1", "ca. 24 €", "Free pausiert und hat keine Backups", "–"),
    ("DNS, Spam-Schutz", "Cloudflare", "vorhanden", "0 €", "DNS, Turnstile statt Captcha", "–"),
    ("Domains .de", "INWX", "1", "ca. 1 € je Domain", "Cloudflare verkauft keine .de-Domains; API vorhanden", "united-domains"),
    ("KI", "Claude API", "3", "ca. 30–80 €", "Opus für Texte und Aufbau, Haiku für Massen-Checks", "–"),
    ("Statistik Kunden-Sites", "Plausible (EU)", "1", "ca. 9–19 €", "ohne Cookie-Banner, API fürs Dashboard", "Umami (selbst gehostet)"),
    ("Such- und Profildaten", "Google Search Console, PageSpeed, Places, Business Profile API", "3", "0–20 €", "Rankings, Ladezeit, Leads, Bewertungen", "–"),
    ("Uptime", "eigene Checks (Supabase Cron)", "1", "0 €", "Erreichbarkeit, SSL, Formular", "Better Stack (ca. 25 €)"),
    ("Meldungen", "ntfy + Brevo/Resend", "vorhanden / 1", "0–20 €", "Push aufs iPhone, E-Mails an Kunden", "–"),
    ("Buchhaltung", "Lexware Office", "0", "ca. 15–25 €", "Angebote, Abo-Rechnungen, Belege, DATEV-Export, API", "sevDesk"),
    ("Zahlungseinzug", "GoCardless (SEPA)", "1", "ca. 1 % je Zahlung", "Monatsbeträge automatisch einziehen", "Stripe"),
    ("Bank", "Geschäftskonto mit API", "0", "ca. 10–30 €", "Umsätze automatisch in Lexware Office", "–"),
    ("Verträge", "Docuseal / Yousign", "1", "0–30 €", "Angebot + AV-Vertrag digital unterschreiben", "–"),
    ("Dashboard", "Next.js auf Vercel + Supabase", "2", "0 € extra", "eigene App, alles an einem Ort", "Retool, Softr"),
    ("Zeiterfassung", "im Dashboard", "2", "0 €", "Stunden je Kunde → Verdienst je Stunde", "Clockify"),
]
KOSTEN = [("0 – Vorbereitung", "Oktober 2026", "Lexware Office, Geschäftskonto, Domain", "ca. 30 €", "6–10 h"),
          ("1 – Grundbetrieb", f"ab 1. Kunde ({monat_ab(1)})", "Vercel Pro, Supabase Pro, Plausible, GoCardless", "ca. 80–110 €", "20–30 h"),
          ("2 – Dashboard v1", f"ab 3 Kunden ({monat_ab(3)})", "keine neuen Abos", "ca. 80–110 €", "25–35 h"),
          ("3 – KI-Erstellung", f"ab 5 Kunden ({monat_ab(5)})", "Claude API, Google APIs", "ca. 130–180 €", "25–35 h"),
          ("4 – KI-Optimierung", f"ab 8–10 Kunden ({monat_ab(9)})", "mehr Claude-Nutzung, ggf. Better Stack", "ca. 180–260 €", "20–30 h"),
          ("5 – Team", "ab 10.000 € MRR (Mai 27)", "Sitze für Teammitglieder", "+ ca. 20 € je Person", "10–15 h")]

A = ablauf("A", "Akquise → Vorschau in 48 Stunden", "Interessante Betriebe finden, analysieren und mit einer fertigen Vorschau-Website ansprechen.",
    "wöchentlich (Montag) oder per Knopf im Dashboard: „20 neue Betriebe in [Branche, Stadt]“",
    [("Betriebe je Branche und Stadt sammeln", ("auto",), "Google Places API", "Liste in <i>interessenten</i>"),
     ("Schnell-Analyse: Ladezeit, Handy, Bewertungen, Website-Alter", ("auto", "ki"), "PageSpeed API, Claude Haiku", "Potenzial 0–100"),
     ("Top 5 der Woche auswählen", ("du",), "Dashboard · Pipeline", "Auswahl"),
     ("Vorschau-Website erzeugen (nur belegbare Inhalte)", ("ki",), "Claude Opus → kunde.json → Generator", "vorschau-[name] (noindex)"),
     ("Vorschau prüfen, Nachricht senden", ("du",), "Dashboard, E-Mail/Telefon", "Status „kontaktiert“"),
     ("Nachfassen nach 3 und 7 Tagen erinnern", ("auto",), "Supabase Cron → Aufgabe", "Termin oder „verloren“ + Grund")],
    "≈ 10 h", "≈ 7 h", "Vorschauen/Woche · Antwortquote · Termine · Abschlussquote · Kosten je Abschluss")
B = ablauf("B", "Auftrag → Launch in 21 Tagen", "Vom Ja des Kunden bis zur Website, die live ist, gemessen und überwacht wird.",
    "Angebot im Dashboard auf „angenommen“ (oder digitale Unterschrift eingegangen)",
    [("Angebot + AV-Vertrag unterschreiben lassen", ("kunde", "auto"), "Docuseal/Yousign", "Vertrag in <i>vertraege</i>"),
     ("Rechnung 1 (50 %) + Lastschrift-Mandat", ("auto",), "Lexware Office, GoCardless", "Rechnung, Mandat"),
     ("Inhalte-Formular: Fotos, Leistungen, Preise, Team, Zugänge", ("kunde",), "Formular im Dashboard-Kundenbereich", "Rohdaten"),
     ("Website bauen: kunde.json + alle Unterseiten (Leistung × Ort)", ("ki",), "Claude Opus, Generator", "Pull Request mit Vorschau"),
     ("Abnahme-Prüfung (Lighthouse, Barrierefreiheit, Links, Recht, Formular)", ("auto",), "GitHub Action", "grün = bereit"),
     ("Entwurf ansehen, Kunde zeigen, Freigabe", ("du", "kunde"), "Vorschau-Link", "Freigabe → Rechnung 2"),
     ("Domain, DNS, Statistik, Search Console, Überwachung anlegen", ("auto",), "INWX, Cloudflare, Vercel, Plausible", "live + gemessen")],
    "≈ 24–28 h", "≈ 8–10 h", "Tage bis Launch · Korrekturschleifen · Lighthouse · deine Stunden je Launch")
C_ = ablauf("C", "Überwachung rund um die Uhr", "Probleme erkennen, bevor der Kunde sie bemerkt.",
    "Zeitplan: alle 5 Minuten, täglich, wöchentlich",
    [("Erreichbarkeit jeder Seite (alle 5 Min.)", ("auto",), "Supabase Cron", "Push bei Ausfall"),
     ("SSL, Domain-Ablauf, Build-Status, Test-Anfrage über das Formular (täglich)", ("auto",), "Cron, Vercel API", "Aufgabe bei Fehler"),
     ("Ladezeit, Search-Console-Fehler, neue Bewertungen (wöchentlich)", ("auto",), "PageSpeed, Search Console, Business Profile", "Messwerte"),
     ("Nur bei Rot: ansehen und entscheiden", ("du",), "Dashboard · Aufgaben", "behoben / delegiert")],
    "≈ 2 h/Monat", "≈ 15 min/Monat", "Uptime · Ø Ladezeit · offene Fehler · Reaktionszeit")
D = ablauf("D", "Optimierung und Monatsbericht", "Jeden Monat messbar besser werden – und es dem Kunden zeigen.",
    "am 1. jedes Monats",
    [("Zahlen je Kunde sammeln: Besucher, Klicks, Anrufe, Anfragen, Rankings", ("auto",), "Plausible, Search Console, Business Profile", "<i>messwerte</i>"),
     ("KI-Sichtbarkeit messen: „bester [Branche] in [Stadt]“", ("auto", "ki"), "mehrere KI-Assistenten", "genannt ja/nein"),
     ("Monatsbericht in Klartext (1 Seite)", ("ki",), "Claude", "PDF-Entwurf"),
     ("Bis zu 3 Verbesserungen vorschlagen (z. B. Ortsseite, Titel, FAQ)", ("ki",), "Claude → Pull Requests", "Vorschau-Links"),
     ("Bericht und Vorschläge freigeben", ("du",), "Dashboard · Freigaben", "Versand / Live-Gang"),
     ("Antwortentwürfe auf neue Bewertungen", ("ki", "kunde"), "Business Profile", "Antwort veröffentlicht")],
    "≈ 6–13 h je Kunde", "≈ 2–4 h je Kunde", "Anfragen je Kunde · Klicks · KI-Nennungen · Kündigungsrate")
E = ablauf("E", "Finanzen und Verwaltung", "Geld kommt pünktlich, Kosten sind je Kunde zugeordnet, der Steuerberater hat alles.",
    "laufend; Abo-Rechnungen zum 1. des Monats",
    [("Abo-Rechnungen erstellen und per Lastschrift einziehen", ("auto",), "Lexware Office, GoCardless", "bezahlt / offen"),
     ("Zahlungseingänge abgleichen, Mahnstufen", ("auto",), "Bank-API → Lexware → Dashboard", "Mahnung als Entwurf"),
     ("Kosten je Kunde zuordnen (Hosting, Domain, KI, Werbung)", ("auto",), "Abrechnungs-APIs → <i>kosten</i>", "Deckungsbeitrag je Kunde"),
     ("Belege fotografieren/weiterleiten", ("du",), "Lexware-App", "Beleg verbucht"),
     ("Monatsabschluss + DATEV-Export", ("auto", "du"), "Lexware Office → Steuerberater", "Export"),
     ("Kündigung: Export, Domain-Übergabe, Lastschrift stoppen", ("auto", "du"), "Checkliste im Dashboard", "sauber beendet")],
    "≈ 6 h/Monat", "≈ 1 h/Monat", "MRR · Kasse · offene Posten · Deckungsbeitrag je Kunde und Stunde")

HTML = f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><title>{NAME} – Betriebsplan</title>
<style>
@font-face{{font-family:Fraunces;src:url(../static/fonts/fraunces.woff2)}}@font-face{{font-family:Inter;src:url(../static/fonts/inter.woff2)}}
@page{{size:A4;margin:20mm 18mm 18mm}}
body{{font:9.6pt/1.5 Inter,sans-serif;color:#1c2220;margin:0;padding:0 18mm}}
h1,h2,h3{{font-family:Fraunces,Georgia,serif;font-weight:600;line-height:1.15}}
h2{{font-size:19pt;margin:0 0 8pt;color:#0f5c4a}}h3{{font-size:12pt;margin:12pt 0 5pt}}
.nr{{font:700 8pt Inter,sans-serif;letter-spacing:.14em;color:#94491b;margin-right:8pt;vertical-align:middle}}
p{{margin:0 0 7pt}}ul,ol{{margin:0 0 8pt;padding-left:16pt}}li{{margin:2pt 0}}
.page{{break-before:page}}.cover{{break-before:auto}}
table,.box,.kpis,svg,.flow-h{{break-inside:avoid}}h2,h3{{break-after:avoid}}tr{{break-inside:avoid}}
.kicker{{font-size:8pt;letter-spacing:.14em;text-transform:uppercase;color:#94491b;font-weight:700;margin-bottom:4pt}}
table{{width:100%;border-collapse:collapse;font-size:8.6pt;margin:6pt 0 10pt}}th,td{{padding:4.5pt 5.5pt;border-bottom:1px solid #ddd5c6;text-align:left;vertical-align:top}}
th{{background:#efe8db}}.r{{text-align:right;white-space:nowrap}}td.n{{color:#94491b;font-weight:700;width:12pt}}
.box{{background:#f3efe6;border-left:3px solid #0f5c4a;padding:8pt 12pt;margin:8pt 0}}.warn{{background:#f8ece2;border-left-color:#b0602a}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:8pt;margin:10pt 0}}.kpi{{border:1px solid #ddd5c6;border-radius:6pt;padding:8pt;font-size:8.6pt}}.kpi b{{display:block;font:600 15pt Fraunces,serif;color:#94491b}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:16pt}}
.chart{{width:100%;height:auto;margin:6pt 0}}
.small{{font-size:8.4pt;color:#4a524f}}
.tag{{display:inline-block;font-size:7.4pt;font-weight:700;border-radius:8pt;padding:1pt 6pt;margin:0 2pt 2pt 0;white-space:nowrap}}
.flow{{margin:0 0 16pt;break-inside:avoid}}.flow-h{{display:flex;gap:10pt;align-items:center;border-top:2px solid #0f5c4a;padding-top:8pt;margin-bottom:4pt}}.flow-h h3{{margin:0}}.flow-h .small{{margin:0}}
.big{{font:600 26pt Fraunces,serif;color:#b0602a;width:26pt}}.zeit{{margin-left:auto;text-align:right;font-size:9pt;white-space:nowrap}}.zeit span{{display:block;font-size:7.5pt;color:#4a524f}}.zeit .g{{color:#0f5c4a}}
table.ft td:nth-child(2){{width:34%}}table.ft td:nth-child(3){{width:70pt}}table.ft td:nth-child(4){{width:24%}}
table.wz{{font-size:8pt}}table.wz th:nth-child(1){{width:15%}}table.wz th:nth-child(2){{width:17%}}table.wz th:nth-child(3){{width:9%}}table.wz th:nth-child(4){{width:12%}}table.wz th:nth-child(5){{width:31%}}
.cover{{display:flex;flex-direction:column;justify-content:space-between;min-height:245mm}}.cover h1{{font-size:34pt;margin:0;color:#0f5c4a}}
.prompt{{font-size:8.6pt}}.prompt h3{{font-size:10.5pt;color:#0f5c4a}}code,pre{{font-family:ui-monospace,Menlo,monospace;font-size:7.8pt;background:#f3efe6;border-radius:3pt;padding:0 2pt}}
pre{{padding:8pt;white-space:pre-wrap;line-height:1.35}}
.leg{{font-size:8pt;color:#4a524f;margin:2pt 0 10pt}}
</style></head><body>

<section class="cover"><div><div class="kicker">Betriebsplan · Struktur, Werkzeuge, Abläufe · Stand {date.today().strftime('%d.%m.%Y')}</div>
<h1>{NAME} als System</h1><p style="font:500 15pt Fraunces,serif;margin-top:10pt">Wie die Agentur so aufgebaut wird, dass du verkaufst und entscheidest – und der Rest automatisch läuft.</p>
<p style="max-width:130mm;margin-top:16pt">Dieser Plan vertieft den Businessplan um den Betrieb: Rollen, Werkzeuge, die fünf Kernabläufe, das Dashboard, den Fahrplan in fünf Stufen, Kosten, Risiken – und im Anhang den Prompt, mit dem die Umsetzung später an KI übergeben wird.</p></div>
<div class="kpis"><div class="kpi"><b>{e0(CAP0)}</b>Obergrenze allein heute (MRR)</div><div class="kpi"><b>{e0(CAP1)}</b>Obergrenze allein mit Automatisierung</div><div class="kpi"><b>{H0:.0f} → {H1:.0f} h</b>Stunden je neuem Abschluss</div><div class="kpi"><b>ca. 80–260 €</b>Systemkosten pro Monat je Stufe</div></div>
<p class="small">Zahlen aus dem Finanzmodell (finanzen/modell.py), Szenario Basis, Monat 1 = November 2026. Die Automatisierung greift im Modell ab dem 5. Abschluss; was dafür gebaut wird, steht im Automatisierungsplan. Recruiting wird erst ab Juni 2027 verkauft. Werkzeugpreise sind ca.-Werte, vor Abschluss prüfen.</p></section>

<section class="page">{kap(1, "Zusammenfassung")}
<p>Im Solo-Plan bist du ab <b>{VOLL}</b> voll ausgelastet – nicht der Markt begrenzt das Wachstum, sondern deine 170 Stunden. Jeder neue Abschluss kostet heute im Schnitt <b>{H0:.1f} Stunden</b> im ersten Monat, jeder laufende Kunde mehrere Stunden pro Monat. Genau dort setzt das System an.</p>
<div class="cols"><div><h3>Was das System leistet</h3><ul>
<li><b>Eine Datenbank, ein Dashboard:</b> Pipeline, Kunden, Websites, Geld und Zeit an einem Ort.</li>
<li><b>Websites aus Konfiguration:</b> Jede Kundenseite entsteht aus einer Datei; KI füllt sie, der Generator baut.</li>
<li><b>Automatische Abnahme:</b> Keine Seite geht live, die Prüfung nicht besteht.</li>
<li><b>Überwachung und Berichte</b> ohne Handarbeit.</li>
<li><b>Abrechnung</b> per Abo und Lastschrift, Kosten je Kunde.</li></ul></div>
<div><h3>Was bei dir bleibt</h3><ul>
<li>Verkaufen: Gespräche, Angebote, Beziehungen.</li>
<li>Entscheiden: welche Betriebe, welche Preise, welche Vorschläge.</li>
<li><b>Freigeben:</b> Jede KI-Änderung kommt als Vorschlag mit Vorschau – ein Klick.</li>
<li>Qualität: Stichproben, Kundenfeedback, Verbesserung der Bausteine.</li></ul></div></div>
{mrr_vergleich()}
<div class="box">Gleiche Vertriebsleistung (Basis: 2–3 Abschlüsse/Monat), weniger Stunden je Kunde: Nach 24 Monaten <b>{e0(HEUTE[23]['mrr'])} → {e0(AUTOM[23]['mrr'])} MRR</b>, Ergebnis vor Steuern über 24 Monate <b>{e0(ERG0)} → {e0(ERG1)}</b> (inkl. ca. {e0(M.G['auto_kosten'])} höherer Systemkosten pro Monat). Mehr Vertrieb erhöht die Obergrenze allein auf rund <b>{e0(CAP1)}</b>.</div>
</section>

<section class="page">{kap(2, "Struktur: Wer macht was")}
<p>Die Agentur besteht aus <b>dir</b>, einer Handvoll <b>automatischer Abläufe</b> und <b>KI-Rollen</b>, die zuarbeiten. Ab 10.000 € MRR kommen Menschen dazu – die Struktur bleibt gleich, nur die Rollen werden besetzt.</p>
{tab(["Rolle", "Aufgabe", "Solo-Phase", "ab 10.000 € MRR", "Werkzeug"], [
 ["<b>Inhaber</b>", "Vertrieb, Preise, Freigaben, Qualität", "du", "du (Freigaben, Schlüsselkunden)", "Dashboard"],
 ["<b>Closer</b>", "Erstgespräche, Angebote", "du", "1–6 Closer (Provision)", "Pipeline, Präsentationen"],
 ["<b>KI-Analyst</b>", "Leads bewerten, Wettbewerber, Zahlen auswerten", "KI", "KI", "Claude Haiku, Google-APIs"],
 ["<b>KI-Texter &amp; Bauer</b>", "kunde.json, Unterseiten, Anzeigentexte", "KI", "KI + Umsetzer prüft", "Claude Opus, Generator"],
 ["<b>Prüfer</b>", "Abnahme jeder Änderung", "Automatik", "Automatik + Umsetzer", "GitHub Actions"],
 ["<b>Wächter</b>", "Uptime, SSL, Formulare, Ladezeit", "Automatik", "Automatik", "Supabase Cron, ntfy"],
 ["<b>KI-Berichter</b>", "Monatsbericht, Verbesserungen, Bewertungsantworten", "KI + du", "KI + Umsetzer", "Claude, Dashboard"],
 ["<b>Umsetzer</b>", "Sonderwünsche, Fotos, Feinschliff", "du", "1–3 Umsetzer / Freelancer", "Aufgaben, Zeiten"],
 ["<b>Buchhaltung</b>", "Rechnungen, Belege, Abschluss", "Automatik + du", "Automatik + Steuerberater", "Lexware Office"]])}
<h3>Freigabe-Regel</h3>
<p>{wer("ki")} und {wer("auto")} dürfen vorbereiten, prüfen, messen und melden. Nur {wer("du")} (später auch ein freigegebener Umsetzer) schaltet etwas beim Kunden live. {wer("kunde")} liefert Inhalte und gibt Entwürfe frei.</p>
{kap(3, "Systemaufbau")}
{architektur()}
<p class="leg">Alle Daten laufen in einer Supabase-Datenbank zusammen. Kunden-Websites entstehen in einem gemeinsamen Repo und laufen je Kunde als eigenes Vercel-Projekt – ein Update des Generators verbessert alle Seiten, jede bleibt einzeln steuerbar.</p>
</section>

<section>{kap(4, "Werkzeuge")}
<p>Vorhandene Verbindungen (GitHub, Vercel, Supabase, Cloudflare, ntfy) bleiben die Basis. Neu kommen nur Werkzeuge mit API dazu – sonst lassen sie sich nicht ins Dashboard holen. „Stufe“ = ab wann es gebraucht wird (Kapitel 9).</p>
{tab(["Bereich", "Werkzeug", "Stufe", "Kosten/Monat", "Wofür", "Alternative"], [list(w) for w in WERKZEUGE], "wz")}
<div class="box warn"><b>Zwei Punkte vor dem ersten zahlenden Kunden:</b> Der Vercel-Hobby-Plan ist laut Nutzungsbedingungen nicht für kommerzielle Projekte gedacht → Pro. Das kostenlose Supabase-Projekt pausiert bei Inaktivität und hat keine Backups → Pro.</div>
</section>

<section class="page">{kap(5, "Die fünf Kernabläufe")}
<p>Legende: {wer("du")} {wer("ki")} {wer("auto")} {wer("kunde")} · „deine Zeit“ = heute (Finanzmodell) → mit System (Ziel).</p>
{A}{B}
{C_}{D}{E}</section>

<section>{kap(6, "Wirkung auf deine Zeit")}
{tab(["Aufgabe", "heute", "mit System", "Wodurch"], [[a, f"{h0:g} h", f"<b>{h1:g} h</b>", w] for a, h0, h1, w in STUNDEN])}
<div class="cols"><div class="box">Ø Stunden je neuem Abschluss (inkl. erstem Betreuungsmonat und Vertrieb): <b>{H0:.1f} h → {H1:.1f} h</b>.</div>
<div class="box">Obergrenze MRR allein (volle 170 h, unbegrenzte Nachfrage): <b>{e0(CAP0)} → {e0(CAP1)}</b>.</div></div>
<p class="small">Werte „mit System“ gelten im Modell ab Kunde 5; tatsächliche Werte im Dashboard (Zeiterfassung) messen und das Modell monatlich nachziehen.</p>
{kap(7, "Dashboard")}
{cockpit()}
<p class="leg">Entwurf des Cockpits (Beispielwerte). Mobil zuerst, Dunkelmodus.</p>
{tab(["Seite", "Was du siehst", "Wofür"], [
 ["Cockpit", "MRR, Ziel-Fortschritt, Kasse, Auslastung, offene Freigaben", "2-Minuten-Überblick am Morgen"],
 ["Pipeline", "Interessenten, Analyse-Befund, Vorschau, Termin, Angebot, Quoten", "Vertrieb steuern"],
 ["Kunden", "Verträge, Laufzeiten, Umsatz, Stunden, Deckungsbeitrag je Stunde", "gute und schlechte Kunden erkennen"],
 ["Websites", "Status, Uptime, Lighthouse, Anfragen, Klicks, KI-Nennung, Cookie-Check", "Qualität und Ergebnisse"],
 ["Auswertungen", "Wochen-/Monatsberichte, Seitenaufrufe, Konversion je Seite", "was wirkt"],
 ["Rechnungen", "offen, fällig, bezahlt, Mahnstufe", "Geld kommt rein"],
 ["Zahlungen", "Lastschrift-Mandate, Einzüge, Rückläufer", "Ausfälle sofort sehen"],
 ["Freigaben", "KI-Vorschläge mit Vorschau-Link", "ein Klick: freigeben/ablehnen"],
 ["Aufgaben · Zeiten", "aus Fehlern und Fristen + eigene; Start/Stopp je Kunde", "nichts vergessen, echter Stundenlohn"],
 ["Finanzen", "Umsatz, Kosten, Ergebnis je Monat, Plan vs. Ist", "auf Kurs?"]])}
<h3>Zentrale Steuerung – was du von dort auslöst</h3>
{tab(["Knopf im Dashboard", "Was im Hintergrund passiert", "Verbindung"], [
 ["Neue Website", "kunde.json aus Formular → Build → Vorschau-Link zur Freigabe", "GitHub-API, Vercel-API"],
 ["Live schalten / zurückrollen", "Deploy freigeben oder letzte Version wiederherstellen", "Vercel-API"],
 ["Domain verbinden", "Domain im Projekt anlegen, DNS-Einträge setzen, SSL prüfen", "Vercel-API, Cloudflare-API"],
 ["Betrieb analysieren", "Website-Befund und Potenzial in 1 Minute", "Supabase-Funktion analyse"],
 ["Angebot / Rechnung", "Entwurf aus Vertrag erzeugen, nach Freigabe versenden", "Lexware-Office-API"],
 ["Lastschrift", "Mandat anfragen, Monatsbetrag einziehen, Rückläufer melden", "GoCardless-API (Webhooks)"],
 ["Bericht senden", "Monatsbericht als PDF an den Kunden", "Supabase-Funktion bericht, E-Mail"],
 ["Kündigung", "Laufzeitende berechnen, Export, Domain-Übergabe, Lastschrift stoppen", "alle oben"]])}
<p class="small">Alle Schlüssel (Vercel, GitHub, Lexware, GoCardless, Cloudflare) liegen nur serverseitig (Vercel/Supabase Secrets). Das Dashboard ändert nie direkt eine Kunden-Website, sondern löst Vorschau → Freigabe → Live aus.</p>
</section>

<section class="page">{kap(8, "Datenmodell")}
<p>Eine Datenbank im Supabase-Projekt „Lotwerk Agentur“ (EU). Entwurf: <code>betrieb/schema.sql</code> (eingespielt, mit Zugriffsschutz auf jeder Tabelle). Zugriff nur nach Login als Inhaber; Automatisierungen schreiben serverseitig.</p>
{tab(["Tabelle", "Inhalt", "gefüllt von"], [
 ["interessenten", "Betriebe, Analyse, Potenzial, Status, Vorschau-Link", "Ablauf A"], ["angebote", "Option, Beträge, Status", "du, Lexware"],
 ["kunden · vertraege", "Firma, Produkte, Monatsbetrag, Laufzeit", "Ablauf B"], ["rechnungen · kosten", "Rechnungen, Zahlstatus, Kosten je Kunde", "Ablauf E"],
 ["zeiten", "Start/Stopp je Kunde und Tätigkeit", "du"], ["websites", "Domain, Vercel-Projekt, Status", "Ablauf B"],
 ["checks", "jede automatische Prüfung (ok/Fehler)", "Ablauf B, C"], ["messwerte", "Besucher, Klicks, Anrufe, KI-Nennung je Tag/Monat", "Ablauf D"],
 ["anfragen", "Formulare aller Kunden-Websites", "Kunden-Websites"], ["aufgaben", "To-dos aus Fehlern, Fristen, KI", "alle Abläufe"],
 ["ki_laeufe", "jeder KI-Auftrag mit Kosten, Ergebnis-Link, Freigabe", "KI-Rollen"]])}
<h3>Kennzahlen, die automatisch entstehen</h3>
<p>MRR · Netto-Wachstum · Kündigungsrate · Kosten je Abschluss · Deckungsbeitrag je Kunde und je Stunde · Auslastung · Tage bis Launch · Anfragen je Kunden-Website · Uptime · Ø Lighthouse · KI-Kosten je Kunde · KI-Nennungsquote.</p>
{kap(9, "Fahrplan in fünf Stufen")}
<p>Jede Stufe startet, wenn sie gebraucht wird – gekoppelt an die Kundenzahl im Basis-Plan. Aufbauzeit = deine Stunden mit Claude Code (Schätzung).</p>
{tab(["Stufe", "Start", "Neue Kosten", "System/Monat", "Aufbauzeit"], [[f"<b>{a}</b>", b, c, d, e] for a, b, c, d, e in KOSTEN])}
<div class="box warn">Wichtig: Im Basis-Plan bist du ab {VOLL} voll ausgelastet. Stufen 1–3 müssen <b>vorher</b> stehen – plane dafür feste 4–6 Stunden pro Woche ein, sonst frisst die Kundenarbeit die Zeit für das System.</div>
</section>

<section style="margin-top:14pt">{kap(10, "Risiken und Leitplanken")}
{tab(["Risiko", "Gegenmaßnahme"], [
 ["KI erfindet Inhalte (Bewertungen, Zahlen, Zertifikate)", "Nur belegbare Fakten; Rest wird [PRÜFEN] und blockiert den Launch; Stichproben"],
 ["Fehlerhafte Änderung geht live", "Nur über Pull Request + automatische Prüfung + deine Freigabe; Rücksprung per Klick (Vercel)"],
 ["Abhängigkeit von einzelnen Anbietern", "Standard-Technik (Postgres, statische Seiten, Git) – Umzug jederzeit möglich"],
 ["Datenschutz / Abmahnung", "AV-Verträge mit allen Dienstleistern, keine Tracker ohne Einwilligung, Löschfristen, EU-Hosting der Daten"],
 ["Kosten laufen aus dem Ruder (KI, APIs)", "Kosten je Lauf in ki_laeufe, Monatsbudget mit Warnung im Dashboard"],
 ["Du fällst aus", "Abläufe dokumentiert, Überwachung läuft weiter, Freelancer-Vertretung mit eingeschränkten Rechten"],
 ["Zu früh zu viel gebaut", "Jeder Ablauf erst 3–5-mal von Hand mit Checkliste, dann automatisieren"]])}
{kap(11, "Deine Entscheidungen und nächsten Schritte")}
<ol><li><b>Name und Domain</b> festlegen (Lotwerk ist Platzhalter) → Impressum, E-Mail, Vorschau-Subdomain.</li>
<li><b>Lexware Office und Geschäftskonto</b> eröffnen, Vorlagen für Angebot, AGB und AV-Vertrag anlegen.</li>
<li><b>Feste Aufbauzeit</b> im Kalender: 4–6 Stunden pro Woche bis Stufe 3 steht.</li>
<li><b>Mit dem ersten zahlenden Kunden:</b> Vercel Pro und Supabase Pro.</li>
<li><b>Stufe 1 starten:</b> Master-Prompt (Anhang A) – Kontext + Stufe 1 – in eine neue Claude-Code-Sitzung geben.</li></ol>
<p class="small">Der Prompt in Anhang A ist ein lebendes Dokument (<code>betrieb/PROMPT.md</code>) und wird bei jeder Änderung an Angebot, Preisen oder Abläufen fortgeschrieben. Dieses PDF wird daraus neu erzeugt.</p>
</section>

<section class="page prompt"><h2><small class="nr">A</small>Anhang: Master-Prompt</h2>
{PROMPT}</section>

<section class="page"><h2><small class="nr">B</small>Anhang: Beispiel einer Kunden-Konfiguration</h2>
<p>Aus dieser Datei baut der Generator eine komplette Kunden-Website. Die KI füllt nur diese Datei – Code ändert sie nicht.</p>
<pre>{KUNDE_JSON}</pre></section>
</body></html>"""

(HERE / "Betriebsplan.html").write_text(HTML, encoding="utf-8")
js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://{HERE}/Betriebsplan.html');await p.waitForTimeout(400);
await p.pdf({{path:'{HERE}/Betriebsplan.pdf',format:'A4',printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',
footerTemplate:'<div style="font-size:7pt;color:#888;width:100%;text-align:center;font-family:sans-serif">{NAME} · Betriebsplan · Seite <span class=pageNumber></span> von <span class=totalPages></span></div>',
margin:{{top:'18mm',bottom:'18mm',left:'0',right:'0'}}}});await b.close();}})();"""
(HERE / "_pdf.js").write_text(js)
subprocess.run(["node", str(HERE / "_pdf.js")], check=True, env={**os.environ, "NODE_PATH": subprocess.check_output(["npm", "root", "-g"]).decode().strip()})
(HERE / "_pdf.js").unlink()
print("Betriebsplan.pdf erstellt")
