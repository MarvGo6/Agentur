"""Erzeugt businessplan/Businessplan.html und .pdf. Alle Zahlen kommen aus finanzen/modell.py."""
import sys, json, subprocess
from pathlib import Path
from datetime import date
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "finanzen")); sys.path.insert(0, str(ROOT))
import modell as M
from content import PREISE as P, eur

C = json.loads((ROOT / "config.json").read_text())
NAME = C["name"]
R = {n: M.rechne(n) for n in M.SZENARIEN}
B = R["Basis"]; G = M.GEMEINSAM
COL = {"Konservativ": "#c26a2e", "Basis": "#1a8a68", "Optimistisch": "#5b6fc4"}


def e0(v): return eur(round(v))
def ziel(n): return next((x["monat"] for x in R[n] if x["mrr"] >= 10000), None)
def jahr(n, k, j): return sum(x[k] for x in R[n][(j - 1) * 12:j * 12])


def line_chart():
    W, H, l, t, r, b = 640, 300, 62, 20, 110, 40
    ymax = 18000
    sx = lambda m: l + (m - 1) / 23 * (W - l - r)
    sy = lambda v: t + (1 - v / ymax) * (H - t - b)
    g = []
    for v in range(0, ymax + 1, 3000):
        g.append(f'<line x1="{l}" x2="{W-r}" y1="{sy(v):.1f}" y2="{sy(v):.1f}" stroke="#e4ddd0" stroke-width="1"/>'
                 f'<text x="{l-8}" y="{sy(v)+4:.1f}" text-anchor="end">{eur(v)}</text>')
    for m in (1, 6, 12, 18, 24):
        g.append(f'<text x="{sx(m):.1f}" y="{H-b+20}" text-anchor="middle">M{m}</text>')
    g.append(f'<line x1="{l}" x2="{W-r}" y1="{sy(10000):.1f}" y2="{sy(10000):.1f}" stroke="#1c2220" stroke-dasharray="4 4" stroke-width="1"/>'
             f'<text x="{l+6}" y="{sy(10000)-6:.1f}" fill="#1c2220">Ziel 10.000 €</text>')
    for n, rows in R.items():
        pts = " ".join(f"{sx(x['monat']):.1f},{sy(x['mrr']):.1f}" for x in rows)
        g.append(f'<polyline points="{pts}" fill="none" stroke="{COL[n]}" stroke-width="2.2" stroke-linejoin="round"/>')
        last = rows[-1]
        g.append(f'<circle cx="{sx(24):.1f}" cy="{sy(last["mrr"]):.1f}" r="4" fill="{COL[n]}" stroke="#fff" stroke-width="2"/>'
                 f'<text x="{sx(24)+10:.1f}" y="{sy(last["mrr"])+4:.1f}" fill="#1c2220"><tspan font-weight="600">{n}</tspan> {e0(last["mrr"])}</text>')
    return f'<svg viewBox="0 0 {W} {H}" class="chart" font-size="11" fill="#4a524f" font-family="Inter,sans-serif">{"".join(g)}</svg>'


def bar_chart():
    x = B[-1]
    segs = [("SEO-Retainer", x["k_seo"] * G["preis_seo"]), ("Wachstumsprogramm", x["k_programm"] * G["preis_programm"]),
            ("Pflege & Hosting", x["k_pflege"] * G["preis_pflege"]), ("Ads-Betreuung", x["k_ads"] * G["preis_ads"])]
    W, rowh, l = 640, 38, 160
    mx = max(v for _, v in segs)
    g = []
    for i, (n, v) in enumerate(segs):
        y = 10 + i * rowh; w = (v / mx) * (W - l - 120)
        g.append(f'<text x="{l-10}" y="{y+17}" text-anchor="end" fill="#1c2220">{n}</text>'
                 f'<rect x="{l}" y="{y+4}" width="{w:.1f}" height="20" rx="4" fill="#1a8a68"/>'
                 f'<text x="{l+w+8:.1f}" y="{y+18}" fill="#1c2220" font-weight="600">{e0(v)}</text>')
    return f'<svg viewBox="0 0 {W} {10+len(segs)*rowh}" class="chart" font-size="12" font-family="Inter,sans-serif">{"".join(g)}</svg>'


def quartale():
    rows = ""
    for q in range(8):
        s = B[q * 3:q * 3 + 3]; z = s[-1]
        rows += (f"<tr><td>Q{q+1} (M{q*3+1}–{q*3+3})</td><td class=r>{e0(sum(x['umsatz'] for x in s))}</td><td class=r>{e0(sum(x['kosten'] for x in s))}</td>"
                 f"<td class=r>{e0(sum(x['ergebnis'] for x in s))}</td><td class=r>{e0(z['mrr'])}</td><td class=r>{z['k_pflege']:.0f}</td><td class=r>{z['k_seo']:.0f}</td><td class=r>{z['k_programm']:.0f}</td><td class=r>{z['eigen_std']:.0f}</td></tr>")
    return rows


def szen_table():
    def row(lab, f):
        return f"<tr><td>{lab}</td>" + "".join(f"<td class=r>{f(n)}</td>" for n in R) + "</tr>"
    return ("<table><thead><tr><th>Kennzahl</th>" + "".join(f"<th class=r>{n}</th>" for n in R) + "</tr></thead><tbody>"
            + row("Neue Website-Kunden / Monat (M1–6 · 7–12 · 13–24)", lambda n: " · ".join(str(v).replace(".", ",") for v in M.SZENARIEN[n]["web"]))
            + row("Anteil mit SEO / mit Ads", lambda n: f"{M.SZENARIEN[n]['q_seo']:.0%} / {M.SZENARIEN[n]['q_ads']:.0%}")
            + row("MRR Monat 12", lambda n: e0(R[n][11]["mrr"]))
            + row("MRR Monat 24", lambda n: e0(R[n][23]["mrr"]))
            + row("10.000 € MRR erreicht", lambda n: f"Monat {ziel(n)}" if ziel(n) else "nach Monat 24")
            + row("Umsatz Jahr 1 / Jahr 2", lambda n: f"{e0(jahr(n,'umsatz',1))} / {e0(jahr(n,'umsatz',2))}")
            + row("Ergebnis Jahr 1 / Jahr 2*", lambda n: f"{e0(jahr(n,'ergebnis',1))} / {e0(jahr(n,'ergebnis',2))}")
            + row("Eigene Stunden / Monat in M24", lambda n: f"{R[n][23]['eigen_std']:.0f} h")
            + "</tbody></table>")


z = ziel("Basis")
prog_einzeln = P["web_wachstum"] + 12 * P["pflege_wachstum"] + 12 * P["seo_plus"] + P["ads_setup"] + 12 * P["ads"]

HTML = f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Businessplan {NAME}</title>
<style>
@font-face{{font-family:Fraunces;src:url(../static/fonts/fraunces.woff2)}}@font-face{{font-family:Inter;src:url(../static/fonts/inter.woff2)}}
@page{{size:A4;margin:20mm 18mm 18mm}}
body{{font:10pt/1.5 Inter,sans-serif;color:#1c2220;margin:0;padding:0 18mm}}
h1,h2,h3{{font-family:Fraunces,Georgia,serif;font-weight:600;line-height:1.15}}
h2{{font-size:19pt;margin:0 0 8pt;color:#0f5c4a}}h3{{font-size:12.5pt;margin:14pt 0 5pt}}
p{{margin:0 0 7pt}}ul{{margin:0 0 8pt;padding-left:16pt}}li{{margin:2pt 0}}
.page{{margin-bottom:22pt}}.cover{{page-break-after:always}}table,.box,.kpis,svg{{break-inside:avoid}}h2,h3{{break-after:avoid;break-inside:avoid;page-break-inside:avoid}}tr{{break-inside:avoid}}
.kicker{{font-size:8pt;letter-spacing:.14em;text-transform:uppercase;color:#b0602a;font-weight:700;margin-bottom:4pt}}
table{{width:100%;border-collapse:collapse;font-size:9pt;margin:6pt 0 10pt}}th,td{{padding:5pt 6pt;border-bottom:1px solid #ddd5c6;text-align:left;vertical-align:top}}
th{{background:#efe8db}}.r{{text-align:right;white-space:nowrap}}
.box{{background:#f3efe6;border-left:3px solid #0f5c4a;padding:9pt 12pt;margin:8pt 0}}
.warn{{background:#f8ece2;border-left-color:#b0602a}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:8pt;margin:10pt 0}}.kpi{{border:1px solid #ddd5c6;border-radius:6pt;padding:8pt}}.kpi b{{display:block;font:600 16pt Fraunces,serif;color:#b0602a}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:16pt}}
.chart{{width:100%;height:auto;margin:6pt 0}}
.cover{{display:flex;flex-direction:column;justify-content:space-between;min-height:245mm}}
.cover h1{{font-size:38pt;margin:0;color:#0f5c4a}}.small{{font-size:8.5pt;color:#4a524f}}
</style></head><body>

<section class="page cover"><div><div class="kicker">Businessplan · Stand {date.today().strftime('%d.%m.%Y')}</div>
<h1>{NAME}</h1><p style="font:500 16pt Fraunces,serif;margin-top:10pt">Agentur für digitales Wachstum lokaler Betriebe</p>
<p style="max-width:120mm;margin-top:18pt">Websites, lokale SEO und Google Ads für Handwerk, Kanzleien, Pflege, Bestatter und Tierarztpraxen. Remote, ohne Startkapital, mit wiederkehrenden Umsätzen als Kern.</p></div>
<div class="kpis"><div class="kpi"><b>Monat {z}</b>10.000 € MRR im Basis-Szenario</div><div class="kpi"><b>{e0(B[23]['mrr'])}</b>MRR nach 24 Monaten</div><div class="kpi"><b>0 €</b>Startkapital nötig</div><div class="kpi"><b>{B[23]['eigen_std']:.0f} h</b>eigene Stunden/Monat in M24</div></div>
<p class="small">Alle Zahlen stammen aus dem beigefügten Finanzmodell (Finanzmodell.xlsx), das unabhängig in Python nachgerechnet wurde. Es sind Planwerte, keine Zusagen.</p></section>

<section class="page"><h2><small class="kicker" style="display:inline-block;font-family:Inter,sans-serif;margin-right:8pt;vertical-align:middle">01</small>Zusammenfassung</h2>
<p>{NAME} ist eine remote arbeitende Agentur, die lokalen und regionalen Betrieben zu mehr passenden Anfragen verhilft – über schnelle Websites, lokale Suchmaschinenoptimierung und Google Ads. Der Gründer tritt nicht persönlich mit Gesicht auf; die Marke, die Website und durchgerechnete Beispiele tragen den Vertrieb.</p>
<h3>Das Geschäftsmodell in drei Sätzen</h3>
<ul><li>Der Einstieg ist eine Website zum Festpreis ({eur(P['web_start'])} bis {eur(P['web_wachstum'])}). Sie bringt sofort Liquidität.</li>
<li>Jede Website zieht einen Pflegevertrag nach sich ({P['pflege_start']}–{P['pflege_wachstum']} € im Monat), ein Teil der Kunden zusätzlich SEO ({P['seo_lokal']}–{P['seo_plus']} €) oder Ads-Betreuung ({P['ads']} €).</li>
<li>Für Betriebe mit hohem Kundenwert gibt es das Wachstumsprogramm für {eur(P['programm'])} im Monat über zwölf Monate.</li></ul>
<h3>Ziel und Ergebnis der Planung</h3>
<p>Ziel sind <strong>10.000 € monatlich wiederkehrender Umsatz (MRR)</strong>. Im Basis-Szenario wird das in <strong>Monat {z}</strong> erreicht, nach 24 Monaten liegt der MRR bei {e0(B[23]['mrr'])}. Konservativ gerechnet sind es nach 24 Monaten {e0(R['Konservativ'][23]['mrr'])}, optimistisch {e0(R['Optimistisch'][23]['mrr'])}.</p>
{line_chart()}
<div class="box">Weil Websites einmalig bezahlt werden und Freelancer nur bei Bedarf eingekauft werden, ist das Ergebnis ab dem ersten Monat positiv. Es wird <strong>kein Startkapital</strong> benötigt. Der eigentliche Engpass ist nicht Geld, sondern die Kundengewinnung in den ersten sechs Monaten.</div></section>

<section class="page"><h2><small class="kicker" style="display:inline-block;font-family:Inter,sans-serif;margin-right:8pt;vertical-align:middle">02</small>Angebot</h2>
<p>Das Angebot ist bewusst nicht auf eine einzelne Leistung festgelegt. Alle Bausteine verfolgen dasselbe Ziel: mehr passende Anfragen – von Kunden oder von Bewerbern.</p>
<table><thead><tr><th>Baustein</th><th>Inhalt</th><th class=r>Preis</th></tr></thead><tbody>
<tr><td>Website Start</td><td>Bis 5 Seiten, Texte, Google-Profil, Formular, 2–3 Wochen</td><td class=r>{eur(P['web_start'])}</td></tr>
<tr><td>Website Wachstum</td><td>Bis 15 Seiten, Leistungs- und Ortsseiten, Karrierebereich, Messung</td><td class=r>{eur(P['web_wachstum'])}</td></tr>
<tr><td>Pflege & Hosting</td><td>Hosting, Updates, Sicherheit, kleine Änderungen</td><td class=r>{P['pflege_start']} / {P['pflege_wachstum']} €/Mon.</td></tr>
<tr><td>SEO Lokal / Plus</td><td>Profil, Verzeichnisse, Inhalte, Bewertungen, Bericht; 6 Monate Mindestlaufzeit</td><td class=r>{P['seo_lokal']} / {P['seo_plus']} €/Mon.</td></tr>
<tr><td>Google-Ads-Betreuung</td><td>Einrichtung {P['ads_setup']} €, Kampagnen, Zielseiten, Bericht, monatlich kündbar</td><td class=r>{P['ads']} €/Mon.</td></tr>
<tr><td>Wachstumsprogramm</td><td>Website Wachstum + Pflege + SEO Plus + Ads, Monatsgespräch, 12 Monate</td><td class=r>{eur(P['programm'])}/Mon.</td></tr></tbody></table>
<h3>Warum diese Struktur</h3>
<ul><li><strong>Einstieg mit niedriger Hürde:</strong> Eine Website ist für Betriebe leicht zu verstehen und zu kaufen.</li>
<li><strong>Wiederkehrender Umsatz als Kern:</strong> Pflege ist nahezu automatisch, SEO und Ads bringen den Großteil des MRR.</li>
<li><strong>Programm als Preisanker:</strong> Einzeln kosten die Programm-Bausteine im ersten Jahr {eur(prog_einzeln)}, im Programm {eur(12*P['programm'])}. Das macht die Entscheidung leicht und sichert zwölf Monate Umsatz.</li>
<li><strong>Keine Prozente vom Werbebudget:</strong> Das schafft Vertrauen und unterscheidet von klassischen Agenturen.</li></ul>
<h3>Beispielpakete (auf der Website ausführlich mit Kundenweg)</h3>
<table><thead><tr><th>Beispiel</th><th>Paket</th><th class=r>Jahr 1</th></tr></thead><tbody>
<tr><td>Friseur</td><td>Website Start + Pflege</td><td class=r>{eur(P['web_start']+12*P['pflege_start'])}</td></tr>
<tr><td>Bestatter</td><td>Website Start + Pflege + SEO Lokal</td><td class=r>{eur(P['web_start']+12*P['pflege_start']+12*P['seo_lokal'])}</td></tr>
<tr><td>Pflegedienst</td><td>Website Wachstum + Pflege + Ads</td><td class=r>{eur(P['web_wachstum']+12*P['pflege_wachstum']+P['ads_setup']+12*P['ads'])}</td></tr>
<tr><td>Steuerberater</td><td>Website Wachstum + Pflege + SEO Lokal</td><td class=r>{eur(P['web_wachstum']+12*P['pflege_wachstum']+12*P['seo_lokal'])}</td></tr>
<tr><td>Tierarzt</td><td>Website Wachstum + Pflege + SEO Plus</td><td class=r>{eur(P['web_wachstum']+12*P['pflege_wachstum']+12*P['seo_plus'])}</td></tr>
<tr><td>Dachdecker & Solar</td><td>Wachstumsprogramm</td><td class=r>{eur(12*P['programm'])}</td></tr></tbody></table></section>

<section class="page"><h2><small class="kicker" style="display:inline-block;font-family:Inter,sans-serif;margin-right:8pt;vertical-align:middle">03</small>Markt und Zielgruppen</h2>
<p>In Deutschland gibt es rund drei Millionen kleine und mittlere Unternehmen. Ein großer Teil hat eine veraltete oder langsame Website, ein unvollständiges Google-Profil und keine messbare Online-Kundengewinnung. Für das Ziel von 10.000 € MRR werden im Basis-Szenario nach 24 Monaten nur rund {B[23]['k_pflege']:.0f} aktive Pflegekunden, {B[23]['k_seo']:.0f} SEO-Kunden und {B[23]['k_programm']:.0f} Programmkunden benötigt. Der Markt ist also kein Engpass – die Kunst ist die Auswahl.</p>
<h3>Fünf Kernbranchen</h3>
<table><thead><tr><th>Branche</th><th>Warum attraktiv</th><th>Hauptbedarf</th></tr></thead><tbody>
<tr><td>Dachdecker & Solar</td><td>Hoher Auftragswert (Sanierung + PV oft &gt; 30.000 €), teure Leadportale</td><td>Eigene Anfragen, Notdienst-Ads, Recruiting</td></tr>
<tr><td>Steuerberater</td><td>Hohe Zahlungsfähigkeit, langfristige Mandate, Fachkräftemangel</td><td>Positionierung, Karriereseite, lokale SEO</td></tr>
<tr><td>Pflegedienste</td><td>Akuter Personalmangel, jede Pflegekraft ermöglicht neue Touren</td><td>Recruiting-Ads, Kurzbewerbung, Angehörigen-Infos</td></tr>
<tr><td>Bestatter</td><td>Hoher Einzelwert, Konkurrenz durch Ketten und Portale, wenig digital</td><td>Vertrauen, 24-h-Erreichbarkeit, Ortsseiten</td></tr>
<tr><td>Tierarztpraxen</td><td>Überlastete Empfänge, margenstarke Zusatzleistungen, TFA-Mangel</td><td>Online-Termine, Leistungsseiten, Recruiting</td></tr></tbody></table>
<h3>Ideales Kundenprofil</h3>
<ul><li>5 bis 50 Mitarbeitende, Inhaber entscheidet selbst</li><li>Ein neuer Kunde oder eine neue Fachkraft ist mindestens 2.000 € wert</li><li>Regional tätig, Einzugsgebiet bis ca. 50 km</li><li>Erkennbarer Leidensdruck: veraltete Website, fehlende Bewerbungen, Abhängigkeit von Portalen</li></ul>
<p>Zusätzlich sind Friseure, Kosmetik und ähnliche Betriebe gute Einstiegskunden für Website Start – kleinerer Wert, aber schneller Abschluss und gute Referenzen.</p>
<h3>Wettbewerb und Positionierung</h3>
<table><thead><tr><th>Wettbewerber</th><th>Stärke</th><th>Schwäche, die {NAME} nutzt</th></tr></thead><tbody>
<tr><td>Baukästen (Wix, Jimdo)</td><td>Günstig</td><td>Kunde muss alles selbst machen, keine Strategie</td></tr>
<tr><td>Lokale Freelancer</td><td>Persönlich, günstig</td><td>Oft nur Website, keine laufende Betreuung, Ausfallrisiko</td></tr>
<tr><td>Große Online-Marketing-Anbieter</td><td>Bekannt, viel Vertrieb</td><td>Lange Verträge, Standardpakete, wenig Branchenverständnis</td></tr>
<tr><td>Klassische Agenturen</td><td>Kreativ</td><td>Teuer, Stundenabrechnung, wenig Fokus auf Anfragen</td></tr></tbody></table>
<div class="box"><strong>Positionierung:</strong> Feste Preise, durchgerechnete Beispiele mit Kundenweg pro Branche, Ergebnisse in Anfragen statt Klicks, ein Ansprechpartner. Schnelle, schlanke Technik ohne Cookie-Banner als sichtbares Qualitätsmerkmal.</div></section>

<section class="page"><h2><small class="kicker" style="display:inline-block;font-family:Inter,sans-serif;margin-right:8pt;vertical-align:middle">04</small>Kundengewinnung ohne Gesicht</h2>
<p>Der Gründer möchte nicht persönlich vor der Kamera stehen. Das ist bei Betrieben dieser Größe kein Nachteil: Sie kaufen Ergebnisse, Klarheit und Verlässlichkeit. Die Kanäle sind entsprechend gewählt.</p>
<table><thead><tr><th>Kanal</th><th>Vorgehen</th><th>Ab Monat</th></tr></thead><tbody>
<tr><td>Gezielte Ansprache per E-Mail und Brief</td><td>Pro Woche 20–30 Betriebe einer Branche recherchieren, kurze persönliche Analyse (3 konkrete Punkte zu Website/Profil) senden. Kein Massenversand, DSGVO und UWG beachten (B2B, sachlicher Bezug).</td><td>1</td></tr>
<tr><td>Telefon-Nachfass</td><td>Kurzer Anruf nach Analyse-Versand; alternativ Terminlink.</td><td>1</td></tr>
<tr><td>Eigene Website & Ratgeber</td><td>Branchen- und Beispielseiten, Ratgeberartikel; langfristig organische Anfragen.</td><td>3</td></tr>
<tr><td>Partner</td><td>Steuerberater, Gründerberater, Druckereien, Fotografen, Webhoster – gegenseitige Empfehlungen, Provision 10 % des ersten Jahres.</td><td>2</td></tr>
<tr><td>Empfehlungen</td><td>Nach jedem Projekt aktiv nach einer Empfehlung fragen; ein Monat Pflege gratis pro erfolgreicher Empfehlung.</td><td>4</td></tr>
<tr><td>Eigene Google Ads</td><td>Kleines Budget auf „Website erstellen lassen + Branche“, sobald erste Referenzen online sind.</td><td>6</td></tr></tbody></table>
<h3>Vertriebstrichter (Basis-Szenario, Phase 2)</h3>
<p>Für {M.SZENARIEN['Basis']['web'][1]:.1f} neue Website-Kunden pro Monat werden bei konservativen Quoten etwa benötigt:</p>
<ul><li>100 recherchierte und angeschriebene Betriebe pro Monat</li><li>→ 8–10 Antworten oder Gespräche (8–10 %)</li><li>→ 4–5 Angebote</li><li>→ 1–2 Abschlüsse</li></ul>
<p>Der Zeitaufwand dafür liegt bei rund 25–30 Stunden im Monat. Durch Vorlagen, Recherche-Werkzeuge und KI-gestützte Analysen lässt sich das deutlich verkürzen.</p>
<h3>Vertrauen ohne Gesicht</h3>
<ul><li>Durchgerechnete Beispiele mit Preisen auf der Website</li><li>Eigene Website als Arbeitsprobe: schnell, klar, ohne Cookie-Banner</li><li>Kostenlose Kurzanalyse als Gesprächseinstieg</li><li>Faire Konditionen: monatlich kündbar, wo möglich; Website gehört dem Kunden</li><li>Echter Name im Impressum (Pflicht), aber kein Foto nötig</li></ul></section>

<section class="page"><h2><small class="kicker" style="display:inline-block;font-family:Inter,sans-serif;margin-right:8pt;vertical-align:middle">05</small>Leistungserbringung und Automatisierung</h2>
<p>Damit das Modell mit einer Person skaliert, wird die Leistung standardisiert und wo möglich automatisiert.</p>
<h3>Website-Fertigung</h3>
<ul><li>Eigener Generator (wie bei der Agentur-Website): Inhalte als Daten, Design als Vorlage, Ausgabe als schnelle statische Seite</li><li>Branchenvorlagen mit Kundenweg, Textbausteinen und Fragenkatalog</li><li>Hosting auf Vercel, Cloudflare oder Netlify – im Rahmen der kostenlosen Kontingente bzw. für wenige Euro</li><li>Ziel: Website Start in 12–15, Website Wachstum in 20–25 eigenen Stunden</li></ul>
<h3>SEO- und Ads-Betreuung</h3>
<ul><li>Monatliche Checkliste pro Kunde (Profil, Bewertungen, eine neue Seite, technische Prüfung)</li><li>Automatischer Monatsbericht aus Search Console, Google-Profil und Ads</li><li>Texte mit KI vorbereiten, fachlich prüfen und vom Kunden freigeben lassen</li></ul>
<h3>Zukauf von Leistungen</h3>
<p>Spitzen und Spezialaufgaben (Design, Texte, Programmierung) werden über Freelancer eingekauft – im Modell mit {G['std_satz']} € pro Stunde, {G['zukauf_web_std']} Stunden je Website, {G['zukauf_seo_std']} Stunden je SEO-Kunde und {G['zukauf_programm_std']} Stunden je Programmkunde im Monat. Bei regelmäßiger Beauftragung selbstständiger Kreativer fällt Künstlersozialabgabe an (ca. 5 %).</p>
<h3>Eigener Zeitbedarf (Basis-Szenario)</h3>
<table><thead><tr><th>Zeitpunkt</th><th class=r>Eigene Stunden / Monat</th><th>Einordnung</th></tr></thead><tbody>
<tr><td>Monat 6</td><td class=r>{B[5]['eigen_std']:.0f} h</td><td>Nebenberuflich machbar (+ Vertrieb)</td></tr>
<tr><td>Monat 12</td><td class=r>{B[11]['eigen_std']:.0f} h</td><td>Nebenberuflich machbar (+ Vertrieb)</td></tr>
<tr><td>Monat 18</td><td class=r>{B[17]['eigen_std']:.0f} h</td><td>Halbe Stelle</td></tr>
<tr><td>Monat 24</td><td class=r>{B[23]['eigen_std']:.0f} h</td><td>Halbe bis Dreiviertelstelle; Zukauf ausbauen</td></tr></tbody></table>
<p class="small">Ohne Vertriebszeit von zusätzlich ca. 25–30 Stunden im Monat.</p>

<h3>Organisation und Recht</h3>
<ul><li><strong>Gewerbeanmeldung</strong> (freies Gewerbe, keine Zulassung oder Meisterpflicht)</li><li><strong>Finanzamt:</strong> Fragebogen zur steuerlichen Erfassung; Kleinunternehmerregelung bis 25.000 € Vorjahresumsatz – laut Planung bereits im ersten Jahr überschritten, daher frühzeitig Regelbesteuerung prüfen</li><li><strong>Impressum</strong> mit echtem Namen und ladungsfähiger Anschrift (ggf. Geschäftsadresse)</li><li><strong>AV-Verträge</strong> mit Kunden für Hosting und Formulare</li><li><strong>Vermögensschadenhaftpflicht</strong> empfohlen (ca. 100–300 € im Jahr)</li><li>Eigene AGB und Angebotsvorlage mit Leistungsumfang, Laufzeit und Eigentumsregel</li></ul></section>

<section class="page"><h2><small class="kicker" style="display:inline-block;font-family:Inter,sans-serif;margin-right:8pt;vertical-align:middle">06</small>Finanzplan: Annahmen</h2>
<p>Das Modell rechnet 24 Monate mit drei Szenarien. Kundenzahlen sind Erwartungswerte (z. B. 1,3 Websites pro Monat = vier Websites in drei Monaten). Alle Annahmen stehen im Blatt „Annahmen“ der Excel-Datei und können geändert werden.</p>
<div class="cols" style="break-inside:avoid"><div><h3>Preise (Durchschnitt)</h3><table><tbody>
<tr><td>Website einmalig</td><td class=r>{eur(G['preis_web'])}</td></tr><tr><td>Pflege & Hosting</td><td class=r>{G['preis_pflege']} €/Mon.</td></tr>
<tr><td>SEO-Retainer</td><td class=r>{G['preis_seo']} €/Mon.</td></tr><tr><td>Ads-Betreuung</td><td class=r>{G['preis_ads']} €/Mon.</td></tr>
<tr><td>Ads-Einrichtung</td><td class=r>{G['preis_ads_setup']} €</td></tr><tr><td>Wachstumsprogramm</td><td class=r>{eur(G['preis_programm'])}/Mon.</td></tr></tbody></table></div>
<div><h3>Kündigungen pro Monat</h3><table><tbody>
<tr><td>Pflege</td><td class=r>{G['churn_pflege']:.0%}</td></tr><tr><td>SEO</td><td class=r>{G['churn_seo']:.0%}</td></tr>
<tr><td>Ads</td><td class=r>{G['churn_ads']:.0%}</td></tr><tr><td>Programm</td><td class=r>{G['churn_programm']:.0%}</td></tr></tbody></table>
<h3>Kosten pro Monat</h3><table><tbody><tr><td>Fixkosten (Tools, Infrastruktur, Versicherung, Buchhaltung)</td><td class=r>{G['fix_kosten']} €</td></tr><tr><td>Eigenes Marketing</td><td class=r>{G['marketing']} €</td></tr><tr><td>Freelancer-Stunde</td><td class=r>{G['std_satz']} €</td></tr></tbody></table></div></div>
<h3>Szenario-Hebel</h3>{szen_table()}
<p class="small">* Ergebnis vor Steuern und vor Unternehmerlohn. Der Gründer entnimmt sein Einkommen aus diesem Ergebnis.</p></section>

<section class="page"><h2><small class="kicker" style="display:inline-block;font-family:Inter,sans-serif;margin-right:8pt;vertical-align:middle">07</small>Finanzplan: Basis-Szenario</h2>
<table><thead><tr><th>Quartal</th><th class=r>Umsatz</th><th class=r>Kosten</th><th class=r>Ergebnis*</th><th class=r>MRR Ende</th><th class=r>Pflege</th><th class=r>SEO</th><th class=r>Progr.</th><th class=r>Std./Mon.</th></tr></thead><tbody>{quartale()}</tbody></table>
<p class="small">* vor Steuern und Unternehmerlohn. Kundenzahlen gerundet.</p>
<h3>Zusammensetzung des MRR in Monat 24</h3>{bar_chart()}
<p>SEO-Retainer und Wachstumsprogramm tragen zusammen rund drei Viertel des wiederkehrenden Umsatzes. Pflege ist klein, aber fast ohne Aufwand und senkt die Abwanderung, weil die Website beim Anbieter bleibt.</p>
<h3>Break-even und Kapitalbedarf</h3>
<ul><li><strong>Kapitalbedarf: 0 €.</strong> Der tiefste Kassenstand liegt in keinem Szenario unter null, weil Websites zur Hälfte bei Auftrag bezahlt werden.</li>
<li><strong>Wiederkehrender Break-even:</strong> Ab Monat {next(x['monat'] for x in B if x['mrr']>=x['kosten'])} deckt der MRR allein alle laufenden Kosten.</li>
<li><strong>Vollzeit-Einkommen:</strong> Ab ca. Monat {next(x['monat'] for x in B if x['ergebnis']>=6000)} liegt das monatliche Ergebnis über 6.000 € – genug für einen Unternehmerlohn inklusive Steuern und Sozialversicherung.</li>
<li><strong>Empfohlene Reserve:</strong> 1.500–3.000 € für Gewerbeanmeldung, Versicherung, erste Tools und als Puffer bei verzögerten Zahlungen.</li></ul></section>

<section class="page"><h2><small class="kicker" style="display:inline-block;font-family:Inter,sans-serif;margin-right:8pt;vertical-align:middle">08</small>Meilensteine und Prüfpunkte</h2>
<p>Viermal wird der Plan bewusst überprüft. Liegt der Ist-Wert deutlich unter dem Plan, greifen die genannten Maßnahmen.</p>
<table><thead><tr><th>Prüfpunkt</th><th>Plan (Basis)</th><th>Wenn deutlich darunter</th></tr></thead><tbody>
<tr><td><strong>Monat 3</strong></td><td>2–3 Websites verkauft, MRR ≈ {e0(B[2]['mrr'])}, 300 Betriebe angeschrieben, Website und 6 Beispiele online</td><td>Ansprache prüfen: Branche wechseln, Analyse-Mail kürzen, Telefon-Nachfass verdoppeln</td></tr>
<tr><td><strong>Monat 6</strong></td><td>MRR ≈ {e0(B[5]['mrr'])}, 4–5 Pflegekunden, erste SEO-Kunden, 2 Partner</td><td>Einstiegsangebot (z. B. Profil-Optimierung für 290 €) testen; Fokus auf eine Branche</td></tr>
<tr><td><strong>Monat 12</strong></td><td>MRR ≈ {e0(B[11]['mrr'])}, erster Programmkunde, 3 echte Referenzen mit Zahlen</td><td>Preise prüfen, Programm stärker anbieten, eigene Google Ads starten</td></tr>
<tr><td><strong>Monat 18</strong></td><td>MRR ≈ {e0(B[17]['mrr'])}, feste Freelancer, automatisierte Berichte</td><td>Leistungserbringung weiter auslagern, Vertriebszeit schützen</td></tr>
<tr><td><strong>Monat {z}</strong></td><td>10.000 € MRR</td><td>–</td></tr></tbody></table>
<h3>Die ersten 30 Tage</h3>
<ol><li>Name final festlegen, Domain sichern, Gewerbe anmelden, Finanzamt-Fragebogen</li><li>Impressum mit echten Daten, Website von Vorschau auf öffentlich schalten</li><li>Google-Unternehmensprofil für die Agentur (Service-Area ohne Adresse)</li><li>Erste Branche wählen (Empfehlung: Dachdecker & Solar oder Pflegedienste)</li><li>Liste mit 100 Betrieben, Vorlage für die Kurzanalyse</li><li>20 Analysen pro Woche versenden und nachfassen</li><li>Angebots-, Vertrags- und AV-Vorlagen fertigstellen</li><li>2–3 Partner ansprechen</li></ol></section>

<section class="page"><h2><small class="kicker" style="display:inline-block;font-family:Inter,sans-serif;margin-right:8pt;vertical-align:middle">09</small>Risiken, Grenzen und Hebel</h2>
<h3>Risiken und Gegenmaßnahmen</h3>
<table><thead><tr><th>Risiko</th><th>Wirkung</th><th>Gegenmaßnahme</th></tr></thead><tbody>
<tr><td>Langsamer Vertriebsstart</td><td>Ziel verschiebt sich um Monate (konservativ: nach Monat 24)</td><td>Feste Vertriebszeit pro Woche, Prüfpunkt Monat 3, Branchenwechsel</td></tr>
<tr><td>Höhere Kündigungsquote bei SEO</td><td>Bei 5 % statt 3 % sinkt der MRR in M24 spürbar</td><td>Klare Ziele, Monatsbericht, früh Erfolge zeigen</td></tr>
<tr><td>Abhängigkeit von Freelancern</td><td>Lieferverzug</td><td>Zwei Freelancer je Gewerk, Vorlagen und Dokumentation</td></tr>
<tr><td>Ausfall des Gründers</td><td>Betreuung stockt</td><td>Automatisierte Pflege, dokumentierte Abläufe, Vertretung</td></tr>
<tr><td>Rechtliche Risiken (Werbung, DSGVO)</td><td>Abmahnungen</td><td>Sachliche B2B-Ansprache, Opt-out, AV-Verträge, keine Tracking-Cookies</td></tr>
<tr><td>Preisdruck durch Baukästen und KI-Tools</td><td>Website allein wird billiger</td><td>Wert liegt in Strategie, Sichtbarkeit und Betreuung – nicht im Seitenbau</td></tr></tbody></table>
<h3>Grenzen des Modells</h3>
<ul><li>Kundenzahlen sind Durchschnittswerte; in der Realität kommen Abschlüsse unregelmäßig.</li><li>Zahlungsziele und Ausfälle sind nicht modelliert; die Reserve deckt das ab.</li><li>Steuern, Sozialversicherung und Unternehmerlohn sind nicht abgezogen.</li><li>Der Vertriebsaufwand ist nicht in den eigenen Stunden enthalten.</li></ul>
<h3>Größte Hebel</h3>
<ul><li><strong>Ein zusätzlicher Website-Kunde pro Quartal</strong> verschiebt das Ziel um mehrere Monate nach vorn.</li><li><strong>SEO-Quote von 35 % auf 45 %</strong> erhöht den MRR stärker als jede Preiserhöhung.</li><li><strong>Programm statt Einzelbausteine</strong> bei Kunden mit hohem Kundenwert.</li><li><strong>Branchenfokus:</strong> Vorlagen und Referenzen in einer Branche senken Aufwand und erhöhen Abschlussquoten.</li></ul>
<div class="box warn">Fazit: Das Ziel von 10.000 € MRR ist mit einer Person, ohne Startkapital und ohne öffentliches Auftreten erreichbar. Entscheidend ist ein konsequenter, wöchentlicher Vertrieb in den ersten zwölf Monaten.</div></section>
</body></html>"""

out = Path(__file__).parent
(out / "Businessplan.html").write_text(HTML, encoding="utf-8")
js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://{out}/Businessplan.html');await p.waitForTimeout(300);
await p.pdf({{path:'{out}/Businessplan.pdf',format:'A4',printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',
footerTemplate:'<div style="font-size:7pt;color:#888;width:100%;text-align:center;font-family:sans-serif">{NAME} · Businessplan · Seite <span class=pageNumber></span> von <span class=totalPages></span></div>',
margin:{{top:'18mm',bottom:'18mm',left:'0',right:'0'}}}});await b.close();}})();"""
(out / "_pdf.js").write_text(js)
subprocess.run(["node", str(out / "_pdf.js")], check=True, env={**__import__("os").environ, "NODE_PATH": subprocess.check_output(["npm", "root", "-g"]).decode().strip()})
(out / "_pdf.js").unlink()
print("Businessplan.pdf erstellt")
