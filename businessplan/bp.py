"""Erzeugt businessplan/Businessplan.html und .pdf. Alle Zahlen kommen aus finanzen/modell.py (Solo) und million.py (Ausbau)."""
import sys, json, subprocess, os
from pathlib import Path
from datetime import date
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "finanzen")); sys.path.insert(0, str(ROOT))
import modell as M
import million as MI
from content import PREISE as P, eur

C = json.loads((ROOT / "config.json").read_text())
NAME = C["name"]
G = M.G
R = {n: M.rechne(n) for n in M.SZENARIEN}
B = R["Basis"]
ZB = M.zielmonat(B)
COL = {"Konservativ": "#c26a2e", "Basis": "#1a8a68", "Optimistisch": "#5b6fc4"}
T = MI.rechne()
T_UMSATZ = sum(x["umsatz"] for x in T); T_ERG = sum(x["ergebnis"] for x in T); T_KASSE = min(x["kasse"] for x in T)
U2027 = MI.umsatz_jahr(2027, T); TEMPO = MI.tempo_monat(T)
V = M.verdienst()


def e0(v): return eur(round(v))
def ziel(n): return M.zielmonat(R[n])
def lab(n): z = ziel(n); return f"Monat {z} ({R[n][z-1]['label']})" if z else "nach Monat 24"
def kap(nr, titel): return f'<h2><small class="kicker" style="display:inline-block;font-family:Inter,sans-serif;margin-right:8pt;vertical-align:middle">{nr:02d}</small>{titel}</h2>'


# ------------------------------------------------------------------ Diagramme
def line_chart():
    W, H, l, t, r, b = 640, 290, 62, 20, 118, 40
    ymax = 16000
    sx = lambda m: l + (m - 1) / 23 * (W - l - r)
    sy = lambda v: t + (1 - v / ymax) * (H - t - b)
    g = []
    for v in range(0, ymax + 1, 4000):
        g.append(f'<line x1="{l}" x2="{W-r}" y1="{sy(v):.1f}" y2="{sy(v):.1f}" stroke="#e4ddd0"/><text x="{l-8}" y="{sy(v)+4:.1f}" text-anchor="end">{eur(v)}</text>')
    for m in (1, 6, 12, 18, 24):
        g.append(f'<text x="{sx(m):.1f}" y="{H-b+18}" text-anchor="middle">{M.label(m)}</text>')
    g.append(f'<line x1="{l}" x2="{W-r}" y1="{sy(10000):.1f}" y2="{sy(10000):.1f}" stroke="#1c2220" stroke-dasharray="4 4"/>'
             f'<text x="{W-r-4}" y="{sy(10000)+14:.1f}" text-anchor="end" fill="#1c2220">Ziel 10.000 € – danach Team</text>')
    for n, rows in R.items():
        pts = " ".join(f"{sx(x['monat']):.1f},{sy(x['mrr']):.1f}" for x in rows)
        g.append(f'<polyline points="{pts}" fill="none" stroke="{COL[n]}" stroke-width="2.2" stroke-linejoin="round"/>')
        z = ziel(n)
        if z: g.append(f'<circle cx="{sx(z):.1f}" cy="{sy(rows[z-1]["mrr"]):.1f}" r="4" fill="{COL[n]}" stroke="#fff" stroke-width="2"/>')
    ys = sorted(((R[n][-1]["mrr"], n) for n in R), reverse=True)
    for i, (v, n) in enumerate(ys):
        g.append(f'<text x="{sx(24)+8:.1f}" y="{sy(v)+4+(i-1)*12:.1f}" fill="#1c2220"><tspan font-weight="600" fill="{COL[n]}">■</tspan> {n}</text>')
    return f'<svg viewBox="0 0 {W} {H}" class="chart" font-size="10.5" fill="#4a524f" font-family="Inter,sans-serif">{"".join(g)}</svg>'


def stunden_chart():
    W, H, l, t, r, b = 640, 170, 62, 14, 20, 30
    ymax = 180; bw = (W - l - r) / 24
    sy = lambda v: t + (1 - v / ymax) * (H - t - b)
    g = [f'<line x1="{l}" x2="{W-r}" y1="{sy(v):.1f}" y2="{sy(v):.1f}" stroke="#e4ddd0"/><text x="{l-8}" y="{sy(v)+4:.1f}" text-anchor="end">{v} h</text>' for v in (0, 85, 170)]
    for i, x in enumerate(B):
        x0 = l + i * bw + 2; y = sy(x["stunden"])
        g.append(f'<rect x="{x0:.1f}" y="{y:.1f}" width="{bw-4:.1f}" height="{sy(0)-y:.1f}" rx="2" fill="{"#1a8a68" if x["stunden"] < 169.5 else "#c26a2e"}"/>')
        if i in (0, 6, 11, 17, 23): g.append(f'<text x="{x0+(bw-4)/2:.1f}" y="{H-b+15}" text-anchor="middle">{x["label"]}</text>')
    return (f'<svg viewBox="0 0 {W} {H}" class="chart" font-size="10" fill="#4a524f" font-family="Inter,sans-serif">{"".join(g)}</svg>'
            '<div class="legend"><span><i style="background:#1a8a68"></i>Stunden belegt</span><span><i style="background:#c26a2e"></i>voll ausgelastet (170 h)</span></div>')


def ausbau_bars():
    W, H, l, t, r, b = 640, 240, 62, 16, 20, 34
    ymax = 150000; bw = (W - l - r) / 12
    sy = lambda v: t + (1 - v / ymax) * (H - t - b)
    g = [f'<line x1="{l}" x2="{W-r}" y1="{sy(v):.1f}" y2="{sy(v):.1f}" stroke="#e4ddd0"/><text x="{l-8}" y="{sy(v)+4:.1f}" text-anchor="end">{eur(v)}</text>' for v in range(0, ymax + 1, 50000)]
    g.append(f'<line x1="{l}" x2="{W-r}" y1="{sy(1e6/12):.1f}" y2="{sy(1e6/12):.1f}" stroke="#1c2220" stroke-dasharray="4 4"/><text x="{l+6}" y="{sy(1e6/12)-6:.1f}" fill="#1c2220">83.333 € / Monat = 1-Mio-Tempo</text>')
    for i, x in enumerate(T):
        x0 = l + i * bw + 5; w = bw - 10; ym, yt = sy(x["mrr"]), sy(x["umsatz"])
        g.append(f'<rect x="{x0:.1f}" y="{ym:.1f}" width="{w:.1f}" height="{sy(0)-ym:.1f}" fill="#1a8a68" rx="2"/>'
                 f'<rect x="{x0:.1f}" y="{yt:.1f}" width="{w:.1f}" height="{max(0, ym-yt-2):.1f}" fill="#c26a2e" rx="2"/>'
                 f'<text x="{x0+w/2:.1f}" y="{H-b+16}" text-anchor="middle">{x["monat"]}</text>')
    return (f'<svg viewBox="0 0 {W} {H}" class="chart" font-size="10" fill="#4a524f" font-family="Inter,sans-serif">{"".join(g)}</svg>'
            '<div class="legend"><span><i style="background:#1a8a68"></i>wiederkehrend (MRR)</span><span><i style="background:#c26a2e"></i>einmalig</span></div>')


# ------------------------------------------------------------------ Tabellen
def preis_tab():
    rows = ""
    for n, e, m, he, hm, hinweis in M.PREISLISTE:
        rows += f"<tr><td><b>{n}</b><br><span class=small>{hinweis}</span></td><td class=r>{e0(e) if e else '–'}</td><td class=r>{e0(m) + ' / Mon.' if m else '–'}</td></tr>"
    return f"<table><thead><tr><th>Leistung</th><th class=r>Einmalig</th><th class=r>Monatlich</th></tr></thead><tbody>{rows}</tbody></table>"


def verdienst_tab():
    rows = "".join(f"<tr><td>{v['produkt']}</td><td class=r>{e0(v['umsatz_j1'])}</td><td class=r>{v['stunden_j1']:.0f} h</td><td class=r><b>{e0(v['eur_h'])}</b></td></tr>" for v in V)
    return f"<table><thead><tr><th>Produkt</th><th class=r>Umsatz 1. Jahr</th><th class=r>Ihre Stunden 1. Jahr*</th><th class=r>€ je Stunde</th></tr></thead><tbody>{rows}</tbody></table>"


def szen_tab():
    def row(t, f): return f"<tr><td>{t}</td>" + "".join(f"<td class=r>{f(n)}</td>" for n in R) + "</tr>"
    return ("<table><thead><tr><th>Solo-Plan</th>" + "".join(f"<th class=r>{n}</th>" for n in R) + "</tr></thead><tbody>"
            + row("Abschlüsse pro Monat (Vertriebstempo, Monat 1–2 / ab 3)", lambda n: f"{M.SZENARIEN[n][0]} / {M.SZENARIEN[n][1]}")
            + row("MRR Monat 6 (Apr 27)", lambda n: e0(R[n][5]["mrr"]))
            + row("<b>10.000 € MRR erreicht</b>", lambda n: f"<b>{lab(n)}</b>")
            + row("MRR Monat 12 (Okt 27)", lambda n: e0(R[n][11]["mrr"]))
            + row("Obergrenze allein (Monat 24)", lambda n: e0(R[n][23]["mrr"]))
            + row("Einkommen 1. Jahr vor Steuern*", lambda n: e0(sum(x["ergebnis"] for x in R[n][:12])))
            + row("Abschlüsse 1. Jahr", lambda n: f"{sum(x['deals'] for x in R[n][:12]):.0f}")
            + "</tbody></table>")


def quartale():
    out = ""
    for q in range(8):
        s = B[q*3:q*3+3]; z = s[-1]
        out += (f"<tr><td>{s[0]['label']}–{z['label']}</td><td class=r>{sum(x['deals'] for x in s):.1f}</td><td class=r>{e0(sum(x['umsatz'] for x in s))}</td>"
                f"<td class=r>{e0(sum(x['ergebnis'] for x in s))}</td><td class=r>{e0(z['mrr'])}</td><td class=r>{z['k_prog']:.0f} / {z['k_seo']:.0f} / {z['k_rec']:.0f} / {z['k_pflege']:.0f}</td><td class=r>{z['stunden']:.0f} h</td></tr>")
    return out


def ausbau_quartale():
    out = ""
    for q in range(4):
        s = T[q*3:q*3+3]; z = s[-1]
        out += (f"<tr><td style='white-space:nowrap'>{s[0]['monat'].split()[0]}–{z['monat']}</td><td class=r>{sum(x['deals'] for x in s):.0f}</td><td class=r>{e0(sum(x['umsatz'] for x in s))}</td><td class=r>{e0(sum(x['kosten'] for x in s))}</td>"
                f"<td class=r>{e0(sum(x['ergebnis'] for x in s))}</td><td class=r>{e0(z['mrr'])}</td><td class=r>{z['closer']} / {z['sdr']}</td><td class=r>{z['fte']:.1f}</td></tr>")
    return out


def ausbau_sens():
    rows = ""
    for dc in (3, 4, 5, 6):
        a = dict(MI.A); a["deals_closer"] = dc; r = MI.rechne(a)
        u = sum(x["umsatz"] for x in r); tm = MI.tempo_monat(r)
        rows += f"<tr><td>{dc} Abschlüsse je Closer</td><td class=r>{e0(u)}</td><td class=r>{e0(sum(x['ergebnis'] for x in r))}</td><td class=r>{e0(min(x['kasse'] for x in r))}</td><td class=r>{tm or 'nach 12 Monaten'}</td></tr>"
    return rows


s0 = B[ZB - 1]
rec = next(v for v in V if v["produkt"] == "Recruiting Komplett")
ws = next(v for v in V if v["produkt"] == "Website Start")
deals_b = M.SZENARIEN["Basis"][1]

HTML = f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><title>Businessplan {NAME}</title>
<style>
@font-face{{font-family:Fraunces;src:url(../static/fonts/fraunces.woff2)}}@font-face{{font-family:Inter;src:url(../static/fonts/inter.woff2)}}
@page{{size:A4;margin:20mm 18mm 18mm}}
body{{font:10pt/1.5 Inter,sans-serif;color:#1c2220;margin:0;padding:0 18mm}}
h1,h2,h3{{font-family:Fraunces,Georgia,serif;font-weight:600;line-height:1.15}}
h2{{font-size:19pt;margin:0 0 8pt;color:#0f5c4a}}h3{{font-size:12.5pt;margin:14pt 0 5pt}}
p{{margin:0 0 7pt}}ul,ol{{margin:0 0 8pt;padding-left:16pt}}li{{margin:2pt 0}}
.page{{margin-bottom:22pt}}.cover{{page-break-after:always}}table,.box,.kpis,svg{{break-inside:avoid}}h2,h3{{break-after:avoid;break-inside:avoid;page-break-inside:avoid}}tr{{break-inside:avoid}}
.brk{{break-before:page}}
.kicker{{font-size:8pt;letter-spacing:.14em;text-transform:uppercase;color:#94491b;font-weight:700;margin-bottom:4pt}}
table{{width:100%;border-collapse:collapse;font-size:9pt;margin:6pt 0 10pt}}th,td{{padding:5pt 6pt;border-bottom:1px solid #ddd5c6;text-align:left;vertical-align:top}}
th{{background:#efe8db}}.r{{text-align:right;white-space:nowrap}}
.box{{background:#f3efe6;border-left:3px solid #0f5c4a;padding:9pt 12pt;margin:8pt 0}}
.warn{{background:#f8ece2;border-left-color:#b0602a}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:8pt;margin:10pt 0}}.kpi{{border:1px solid #ddd5c6;border-radius:6pt;padding:8pt}}.kpi b{{display:block;font:600 15pt Fraunces,serif;color:#94491b}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:16pt}}
.chart{{width:100%;height:auto;margin:6pt 0}}.legend{{display:flex;gap:16pt;font-size:8.5pt;color:#4a524f;margin:-2pt 0 8pt}}.legend i{{display:inline-block;width:9pt;height:9pt;border-radius:2pt;margin-right:5pt;vertical-align:-1pt}}
.cover{{display:flex;flex-direction:column;justify-content:space-between;min-height:245mm}}
.cover h1{{font-size:38pt;margin:0;color:#0f5c4a}}.small{{font-size:8.5pt;color:#4a524f}}
</style></head><body>

<section class="page cover"><div><div class="kicker">Businessplan · Stand {date.today().strftime('%d.%m.%Y')}</div>
<h1>{NAME}</h1><p style="font:500 16pt Fraunces,serif;margin-top:10pt">Agentur für digitales Wachstum lokaler Betriebe</p>
<p style="max-width:125mm;margin-top:18pt">Websites, lokale SEO, Google Ads und Recruiting für Handwerk, Kanzleien, Pflege, Praxen, Friseure und Barbershops. Remote, ohne Startkapital, mit wiederkehrenden Umsätzen als Kern.</p>
<p style="max-width:125mm"><b>Zwei Phasen:</b> Allein bis 10.000 € monatlich wiederkehrenden Umsatz (MRR) – erst dann Aufbau eines Teams.</p></div>
<div class="kpis"><div class="kpi"><b>{s0['label']}</b>10.000 € MRR allein (Basis)</div><div class="kpi"><b>{e0(B[23]['mrr'])}</b>Obergrenze allein</div><div class="kpi"><b>0 €</b>Startkapital</div><div class="kpi"><b>{TEMPO}</b>1-Mio-Tempo mit Team</div></div>
<p class="small">Alle Zahlen stammen aus dem beigefügten Finanzmodell (Finanzmodell.xlsx), das unabhängig in Python nachgerechnet wurde. Es sind Planwerte, keine Zusagen. Monat 1 = November 2026.</p></section>

<section class="page">{kap(1, "Zusammenfassung")}
<p>{NAME} hilft lokalen und regionalen Betrieben zu mehr passenden Anfragen – von Kunden und von Fachkräften. Das Angebot reicht von der Website zum Festpreis über SEO und Google Ads bis zum Recruiting-Paket und dem Wachstumsprogramm. Der Gründer tritt nicht mit Gesicht auf; Vorschau-Websites, durchgerechnete Beispiele und klare Preise tragen den Vertrieb.</p>
<h3>Der Plan in zwei Phasen</h3>
<ol><li><strong>Solo bis 10.000 € MRR:</strong> Der Gründer verkauft und setzt alles selbst um. Begrenzend sind nicht Kunden, sondern seine 170 Arbeitsstunden im Monat. Im Basis-Szenario ({deals_b} Abschlüsse pro Monat) wird das Ziel in <strong>{lab('Basis')}</strong> erreicht; allein liegt die Obergrenze bei rund {e0(B[23]['mrr'])} MRR.</li>
<li><strong>Ausbau mit Team ab {MI.LABELS[0]}:</strong> Erst dann werden Vertrieb und Umsetzung schrittweise mit Personal aufgebaut. Nach 12 Team-Monaten liegt das Jahresumsatz-Tempo über 1 Mio. € (ab <strong>{TEMPO}</strong>).</li></ol>
{line_chart()}
<div class="box">Im Solo-Plan braucht es <strong>kein Startkapital</strong>: Websites werden zur Hälfte bei Auftrag bezahlt, die Kosten sind gering. Das Ergebnis ist das Einkommen des Gründers – im Basis-Szenario rund <strong>{e0(sum(x['ergebnis'] for x in B[:12]))} vor Steuern im ersten Jahr</strong>.</div>
</section>

<section class="page">{kap(2, "Angebot und Preise")}
<p>Alle Preise sind Festpreise. Werbebudgets zahlt der Kunde direkt an Google oder Meta – ohne Aufschlag.</p>
{preis_tab()}
<h3>Beispielpakete (auf der Website mit Kundenweg und Vorschau-Website)</h3>
<table><thead><tr><th>Beispiel</th><th>Paket</th><th class=r>1. Jahr</th></tr></thead><tbody>
<tr><td>Friseur</td><td>Website Start + Pflege</td><td class=r>{eur(P['web_start']+12*P['pflege_start'])}</td></tr>
<tr><td>Barbershop</td><td>Website Start + Pflege + Google Ads</td><td class=r>{eur(P['web_start']+12*P['pflege_start']+P['ads_setup']+12*P['ads'])}</td></tr>
<tr><td>Bestatter</td><td>Website Start + Pflege + SEO Lokal</td><td class=r>{eur(P['web_start']+12*P['pflege_start']+12*P['seo_lokal'])}</td></tr>
<tr><td>Pflegedienst</td><td>Website Wachstum + Pflege + Ads (Recruiting)</td><td class=r>{eur(P['web_wachstum']+12*P['pflege_wachstum']+P['ads_setup']+12*P['ads'])}</td></tr>
<tr><td>Steuerberater</td><td>Website Wachstum + Pflege + SEO Lokal</td><td class=r>{eur(P['web_wachstum']+12*P['pflege_wachstum']+12*P['seo_lokal'])}</td></tr>
<tr><td>Tierarzt</td><td>Website Wachstum + Pflege + SEO Plus</td><td class=r>{eur(P['web_wachstum']+12*P['pflege_wachstum']+12*P['seo_plus'])}</td></tr>
<tr><td>Dachdecker & Solar</td><td>Wachstumsprogramm</td><td class=r>{eur(P['prog_setup'] + 12*P['programm'])}</td></tr></tbody></table>
<div class="box">Das Wachstumsprogramm ({eur(P['prog_setup'])} Einrichtung inkl. Website, dann {eur(P['programm'])} im Monat – {eur(P['prog_setup'] + 12*P['programm'])} im ersten Jahr) ist bewusst günstiger als seine Bausteine einzeln ({eur(P['web_wachstum'] + 12*P['pflege_wachstum'] + 12*P['seo_plus'] + P['ads_setup'] + 12*P['ads'])} im ersten Jahr). Das macht die Entscheidung leicht und sichert zwölf Monate Umsatz.</div>
</section>

<section class="page">{kap(3, "Verdienst je Abschluss")}
<p>Wie viel bringt ein Kunde im ersten Jahr – und wie viel Arbeit kostet er, wenn der Gründer alles selbst macht?</p>
{verdienst_tab()}
<p class="small">* Einrichtung, laufende Betreuung über 12 Monate und 10 Vertriebsstunden je Abschluss (Recherche, Anschreiben, Gespräch, Angebot). Pflege wird mit der Website verkauft und hat keinen eigenen Vertriebsaufwand.</p>
<h3>Was daraus folgt</h3>
<ul><li><strong>Recruiting Komplett</strong> (Verkauf ab Juni 2027) bringt mit {e0(rec['eur_h'])} je Stunde und {e0(rec['umsatz_j1'])} im ersten Jahr am meisten – und trifft den größten Engpass der Zielgruppen.</li>
<li><strong>Einzelne Websites</strong> lohnen sich allein am wenigsten ({e0(ws['eur_h'])} je Stunde bei Website Start). Sie sind Einstieg, nicht Ziel – das Ziel ist immer ein laufender Vertrag.</li>
<li><strong>Abos bauen sich auf:</strong> Ein Programm-Kunde bringt jeden Monat {eur(P['programm'])} – ohne erneuten Vertrieb. Der MRR wächst, solange Abschlüsse die Kündigungen übersteigen.</li></ul>
<h3>Vom Gewinn zum Netto</h3>
<p>Im Solo-Plan ist der Gewinn das Einkommen des Gründers. Als Faustregel sind <strong>35–40 % für Einkommensteuer, Kranken- und Pflegeversicherung und Altersvorsorge</strong> zurückzulegen. Bei 10.000 € MRR und kaum Kosten bleiben grob 5.000–6.000 € netto im Monat. Die genaue Rechnung macht der Steuerberater.</p>
</section>

<section class="page">{kap(4, "Markt und Zielgruppen")}
<p>Ein großer Teil kleiner Betriebe hat eine veraltete oder langsame Website, ein unvollständiges Google-Profil und keine messbare Kundengewinnung. Für 10.000 € MRR braucht der Solo-Plan nur rund {s0['k_prog'] + s0['k_seo'] + s0['k_rec']:.0f} laufende Betreuungsverträge – der Markt ist kein Engpass, die Auswahl schon.</p>
<table><thead><tr><th>Branche</th><th>Warum attraktiv</th><th>Hauptbedarf</th></tr></thead><tbody>
<tr><td>Dachdecker & Solar</td><td>Hoher Auftragswert, teure Leadportale</td><td>Eigene Anfragen, Notdienst-Ads, Recruiting</td></tr>
<tr><td>Steuerberater</td><td>Langfristige Mandate, Fachkräftemangel</td><td>Positionierung, Karriereseite, lokale SEO</td></tr>
<tr><td>Pflegedienste</td><td>Akuter Personalmangel</td><td>Recruiting-Paket, Angehörigen-Infos</td></tr>
<tr><td>Bestatter</td><td>Hoher Einzelwert, wenig digital</td><td>Vertrauen, 24-h-Erreichbarkeit, Ortsseiten</td></tr>
<tr><td>Tierarztpraxen</td><td>Überlastete Empfänge, TFA-Mangel</td><td>Online-Termine, Leistungsseiten, Recruiting</td></tr>
<tr><td>Friseure & Barbershops</td><td>Schneller Abschluss, gute Referenzen</td><td>Online-Buchung, Galerie, Google-Profil</td></tr></tbody></table>
<h3>Wettbewerb und Positionierung</h3>
<table><thead><tr><th>Wettbewerber</th><th>Stärke</th><th>Schwäche, die {NAME} nutzt</th></tr></thead><tbody>
<tr><td>Baukästen</td><td>Günstig</td><td>Kunde macht alles selbst, keine Strategie</td></tr>
<tr><td>Freelancer</td><td>Persönlich</td><td>Oft nur Website, keine laufende Betreuung</td></tr>
<tr><td>Große Anbieter</td><td>Bekannt</td><td>Lange Verträge, Standardpakete</td></tr>
<tr><td>Klassische Agenturen</td><td>Kreativ</td><td>Teuer, Stundenabrechnung, wenig Fokus auf Anfragen</td></tr></tbody></table>
<div class="box"><strong>Positionierung:</strong> Feste Preise, fertige Vorschau-Websites je Branche, Ergebnisse in Anfragen statt Klicks, ein Ansprechpartner, schnelle Technik, wo möglich ohne Cookie-Banner.</div>
</section>

<section class="page">{kap(5, "Kundengewinnung ohne Gesicht")}
<table><thead><tr><th>Kanal</th><th>Vorgehen</th></tr></thead><tbody>
<tr><td>Gezielte Ansprache</td><td>Täglich Betriebe einer Branche recherchieren und mit drei konkreten Punkten zu Website und Google-Profil anschreiben (B2B, sachlich, mit Abmeldemöglichkeit).</td></tr>
<tr><td>Vorschau in 48 Stunden</td><td>Interessierte Betriebe bekommen eine Vorschau ihrer eigenen neuen Website – mit dem Generator in wenigen Stunden erstellt.</td></tr>
<tr><td>Telefon-Nachfass</td><td>Kurzer Anruf zwei Tage nach der Analyse.</td></tr>
<tr><td>Eigene Website</td><td>Branchen-, Beispiel- und Ratgeberseiten bringen mit der Zeit organische Anfragen.</td></tr>
<tr><td>Partner & Empfehlungen</td><td>Steuerberater, Druckereien, Fotografen; ein Monat Pflege gratis je erfolgreicher Empfehlung.</td></tr></tbody></table>
<h3>Vertriebstrichter im Basis-Szenario</h3>
<p>{deals_b} Abschlüsse im Monat brauchen bei 25 % Abschlussquote rund {deals_b*4} Gespräche, also 3 pro Woche. Dafür werden bei 10 % Antwortquote rund {deals_b*40} Betriebe im Monat angeschrieben – etwa 6 pro Arbeitstag.</p>
<h3>Vertrauen ohne Gesicht</h3>
<ul><li>Fertige Vorschau-Websites für sieben Branchen</li><li>Durchgerechnete Beispiele mit Preisen</li><li>Faire Konditionen: Website gehört dem Kunden, klare Laufzeiten (Pflege 12 Monate)</li><li>Echter Name im Impressum (Pflicht), aber kein Foto nötig</li></ul>
</section>

<section class="page">{kap(6, "Allein arbeiten: Stunden als Engpass")}
<p>Im Solo-Plan entscheidet nicht der Markt, sondern die Zeit des Gründers. Jeder neue Abschluss kostet im Schnitt {M.h_neu():.0f} Stunden im ersten Monat (Einrichtung, Betreuung, Vertrieb), jeder laufende Vertrag Stunden in jedem Folgemonat.</p>
<h3>Belegte Stunden im Basis-Szenario</h3>{stunden_chart()}
<p>Ab {next(x['label'] for x in B if x['stunden'] >= 169.5)} sind alle 170 Stunden belegt. Neue Abschlüsse sind dann nur noch möglich, wenn Kunden kündigen – der MRR pendelt sich bei rund {e0(B[23]['mrr'])} ein. Genau hier setzt die Einstellung an.</p>
<h3>So gewinnt der Gründer Stunden</h3>
<ul><li><strong>Abos statt Einzel-Websites</strong> – sie bringen pro Stunde dauerhaft mehr.</li><li><strong>Standardisieren:</strong> Website-Generator, feste Leistungsumfänge, Monatsberichte als Vorlage.</li>
<li><strong>Feste Vertriebszeit:</strong> vormittags Akquise und Gespräche, nachmittags Umsetzung.</li><li><strong>Grenzen setzen:</strong> Sonderwünsche nur gegen Aufpreis.</li></ul>
<h3>Organisation und Recht</h3>
<ul><li>Gewerbeanmeldung (freies Gewerbe), Fragebogen zur steuerlichen Erfassung</li><li>Umsatzsteuer: Die Kleinunternehmergrenze (25.000 €) wird im ersten Jahr überschritten – Regelbesteuerung früh mit dem Steuerberater klären</li>
<li>Impressum mit echtem Namen und Anschrift, AV-Verträge mit Kunden, Vermögensschadenhaftpflicht</li><li>Angebots-, Vertrags- und AGB-Vorlagen</li></ul>
</section>

<section class="page">{kap(7, "Finanzplan Solo")}
{szen_tab()}
<p class="small">* Ergebnis vor Steuern = Einkommen des Gründers. Kosten: {eur(G['fix_kosten'])} Fixkosten und {eur(G['marketing'])} Marketing pro Monat. Kündigungen pro Monat: Pflege {G['churn_pflege']:.0%}, Programm {G['churn_prog']:.0%}, SEO {G['churn_seo']:.0%}, Recruiting {G['churn_rec']:.0%}. Mix der Abschlüsse je 25 % Website, Programm, SEO, Recruiting; Recruiting wird erst ab Juni 2027 verkauft, bis dahin je ein Drittel Website, Programm, SEO. Stunden „von Hand“ gerechnet – mit Automatisierung ab Kunde 5 siehe Betriebsplan.</p>
<h3>Basis-Szenario nach Quartalen</h3>
<table><thead><tr><th>Zeitraum</th><th class=r>Abschl.</th><th class=r>Umsatz</th><th class=r>Ergebnis*</th><th class=r>MRR Ende</th><th class=r>Prog / SEO / Rec / Pflege</th><th class=r>Std.</th></tr></thead><tbody>{quartale()}</tbody></table>
<h3>Kapital</h3>
<ul><li><strong>Kapitalbedarf: 0 €.</strong> Das Ergebnis ist ab dem ersten Monat positiv.</li><li><strong>Empfohlene Reserve:</strong> 3.000–5.000 € für Gewerbe, Versicherung, Tools und als Puffer bei Zahlungsverzug.</li>
<li><strong>Für den Ausbau ansparen:</strong> Aus dem Solo-Einkommen sollten bis {s0['label']} rund 20.000–30.000 € für den Teamaufbau zurückgelegt werden (siehe Kapitel 09).</li></ul>
</section>

<section class="page">{kap(8, "Meilensteine und Prüfpunkte")}
<table><thead><tr><th>Prüfpunkt</th><th>Plan (Basis)</th><th>Wenn deutlich darunter</th></tr></thead><tbody>
<tr><td><b>{B[2]['label']}</b></td><td>MRR ≈ {e0(B[2]['mrr'])}, 6–7 Abschlüsse, Vorschau-Websites als Routine</td><td>Branche wechseln, Ansprache kürzen, mehr Telefon-Nachfass</td></tr>
<tr><td><b>{B[5]['label']}</b></td><td>MRR ≈ {e0(B[5]['mrr'])}, Stundenbudget zu ≈ {B[5]['stunden']/170:.0%} belegt</td><td>Mehr Abos statt Einzel-Websites, Wachstumsprogramm stärker anbieten, Automatisierung (ab Kunde 5) fertig</td></tr>
<tr><td><b>{s0['label']}</b></td><td><b>10.000 € MRR</b> – Entscheidung über den Teamaufbau</td><td>Solo weiterführen, bis 10.000 € erreicht sind</td></tr>
<tr><td><b>{B[11]['label']}</b></td><td>Ohne Team: MRR ≈ {e0(B[11]['mrr'])} bei voller Auslastung</td><td>–</td></tr></tbody></table>
<h3>Die ersten 30 Tage</h3>
<ol><li>Name, Domain, Gewerbe, Finanzamt</li><li>Impressum ausfüllen, Website von Vorschau auf öffentlich schalten</li><li>Google-Unternehmensprofil für die Agentur</li><li>Erste Branche wählen (Empfehlung: Dachdecker & Solar oder Steuerberater – hoher Wert je Kunde, passt zum Wachstumsprogramm)</li>
<li>Liste mit 100 Betrieben, Vorlage für die Kurzanalyse</li><li>Täglich 6 Betriebe anschreiben, Vorschau-Websites für Interessierte</li><li>Angebots-, Vertrags- und AV-Vorlagen</li></ol>
</section>

<section class="page">{kap(9, f"Ausbau mit Team ab {MI.LABELS[0]}")}
<p>Sind 10.000 € MRR erreicht, beginnt der Aufbau: zuerst Unterstützung in der Umsetzung, dann Schritt für Schritt Vertrieb. Der Gründer verkauft weiter ({MI.A['deals_gruender']:.0f} Abschlüsse pro Monat) und führt das Team; die Umsetzung übernehmen Angestellte und Freelancer ({MI.A['h_satz']} € Mischsatz je Stunde).</p>
<div class="kpis"><div class="kpi"><b>{e0(T_UMSATZ)}</b>Umsatz erste 12 Team-Monate</div><div class="kpi"><b>{e0(T[-1]['mrr'])}</b>MRR nach 12 Team-Monaten</div><div class="kpi"><b>{TEMPO}</b>Jahresumsatz-Tempo ≥ 1 Mio. €</div><div class="kpi"><b>{e0(U2027)}</b>Umsatz Kalenderjahr 2027</div></div>
<h3>Umsatz pro Monat im Ausbau</h3>{ausbau_bars()}
<table><thead><tr><th>Quartal</th><th class=r>Abschl.</th><th class=r>Umsatz</th><th class=r>Kosten</th><th class=r>Ergebnis*</th><th class=r>MRR Ende</th><th class=r>Closer / SDR</th><th class=r>Umsetzung VZ</th></tr></thead><tbody>{ausbau_quartale()}</tbody></table>
<p class="small">* nach Gründergehalt ({eur(MI.A['gruender'])}/Monat), vor Steuern. Kosten: Umsetzung, Vertrieb (Fixum + {MI.A['provision']:.0%} Provision), Werbung ({eur(MI.A['cac_paid'])} je Abschluss für die Hälfte der Abschlüsse), Gemeinkosten.</p>
</section>

<section class="page">{kap(10, "Ausbau: Bedingungen und Grenzen")}
<h3>Ehrliche Einordnung zum 1-Mio-Ziel</h3>
<p>Wer allein bis 10.000 € MRR wächst und erst dann einstellt, kommt <strong>im Kalenderjahr 2027 auf rund {e0(U2027)} Umsatz</strong> – nicht auf 1 Mio. €. Das Tempo von 1 Mio. € pro Jahr wird ab <strong>{TEMPO}</strong> erreicht. Dafür ist das Risiko gering: Bis zur ersten Einstellung ist kein Fremdkapital nötig, und der Vertrieb ist bewiesen, bevor Gehälter anfallen.</p>
<h3>Wie empfindlich ist der Plan? (erste 12 Team-Monate)</h3>
<table><thead><tr><th>Leistung je Closer</th><th class=r>Umsatz</th><th class=r>Ergebnis</th><th class=r>Tiefster Kassenstand</th><th class=r>1-Mio-Tempo ab</th></tr></thead><tbody>{ausbau_sens()}</tbody></table>
<h3>Kapital für den Ausbau</h3>
<ul><li>Im Plan sinkt die Kasse in den ersten Team-Monaten auf <strong>{e0(T_KASSE)}</strong>, weil Gehälter vor dem Umsatz kommen.</li>
<li>Mit Zahlungszielen und Einarbeitung ist eine <strong>Reserve von 30.000–40.000 €</strong> sinnvoll – angespart aus der Solo-Phase oder über einen Gründungskredit.</li></ul>
<h3>Voraussetzungen vor jeder Einstellung</h3>
<ul><li>10.000 € MRR stabil über zwei Monate, Kündigungen im Plan</li><li>Gründer schließt selbst mindestens 3 Aufträge pro Monat ab</li><li>Standardprozesse dokumentiert (Website, SEO-Routine, Monatsbericht, Recruiting-Kampagne)</li>
<li>GmbH oder UG, Arbeitsverträge mit klaren Provisionsregeln, Lohnbuchhaltung über Steuerberater</li></ul>
</section>

<section class="page">{kap(11, "Risiken, Grenzen und Hebel")}
<table><thead><tr><th>Risiko</th><th>Wirkung</th><th>Gegenmaßnahme</th></tr></thead><tbody>
<tr><td>Langsamer Vertriebsstart</td><td>Ziel verschiebt sich (konservativ: {lab('Konservativ')})</td><td>Feste Vertriebszeit, Prüfpunkt nach 3 Monaten, Branchenwechsel</td></tr>
<tr><td>Überlastung allein</td><td>Qualität sinkt, Kündigungen steigen</td><td>Abos statt Einzelprojekte, Standardisierung, Sonderwünsche bepreisen</td></tr>
<tr><td>Höhere Kündigungen</td><td>MRR wächst langsamer</td><td>Monatsbericht mit Ergebnissen, klare Ziele je Kunde</td></tr>
<tr><td>Ausfall des Gründers</td><td>Betreuung stockt</td><td>Automatisierte Pflege, dokumentierte Abläufe, Vertretung durch Freelancer</td></tr>
<tr><td>Recht (Werbung, DSGVO)</td><td>Abmahnungen</td><td>Sachliche B2B-Ansprache, AV-Verträge, möglichst wenig Tracking</td></tr></tbody></table>
<h3>Grenzen des Modells</h3>
<ul><li>Kundenzahlen sind Durchschnittswerte; Abschlüsse kommen in Wirklichkeit unregelmäßig.</li><li>Steuern, Krankenversicherung und Altersvorsorge sind nicht abgezogen.</li><li>Zahlungsziele und Ausfälle sind nicht modelliert.</li></ul>
<h3>Größte Hebel</h3>
<ul><li><strong>Wachstumsprogramm</strong> zuerst anbieten – es trägt das MRR. <strong>Recruiting</strong> ab Juni 2027 als Zusatz für Bestandskunden (höchster Verdienst je Stunde).</li><li><strong>Ein Abschluss mehr pro Monat</strong> bringt das 10.000-€-Ziel um Monate nach vorn.</li><li><strong>Standardisierung</strong> erhöht die Solo-Obergrenze über {e0(B[23]['mrr'])} hinaus.</li></ul>
<div class="box warn">Fazit: 10.000 € MRR sind allein in {ZB} bis {ziel('Konservativ')} Monaten erreichbar – ohne Startkapital und ohne öffentliches Auftreten. Danach trägt ein schrittweise aufgebautes Team die Agentur in Richtung 1 Mio. € Jahresumsatz.</div>
</section>
</body></html>"""

out = Path(__file__).parent
(out / "Businessplan.html").write_text(HTML, encoding="utf-8")
js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage();
await p.goto('file://{out}/Businessplan.html');await p.waitForTimeout(300);
await p.pdf({{path:'{out}/Businessplan.pdf',format:'A4',printBackground:true,displayHeaderFooter:true,headerTemplate:'<span></span>',
footerTemplate:'<div style="font-size:7pt;color:#888;width:100%;text-align:center;font-family:sans-serif">{NAME} · Businessplan · Seite <span class=pageNumber></span> von <span class=totalPages></span></div>',
margin:{{top:'18mm',bottom:'18mm',left:'0',right:'0'}}}});await b.close();}})();"""
(out / "_pdf.js").write_text(js)
subprocess.run(["node", str(out / "_pdf.js")], check=True, env={**os.environ, "NODE_PATH": subprocess.check_output(["npm", "root", "-g"]).decode().strip()})
(out / "_pdf.js").unlink()
print("Businessplan.pdf erstellt")
