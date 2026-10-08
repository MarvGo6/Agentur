#!/usr/bin/env python3
"""Baut die statische Website nach dist/. Aufruf: python3 build.py"""
import json, shutil, html
from pathlib import Path
from datetime import date

from content_leistungen import TIEFE
from content import PREISE, eur, REC_GARANTIE, LEISTUNGEN, BRANCHEN, BEISPIELE, KAPITEL, RATGEBER, FAQ
from drawings import LOGO, FAVICON
import vorschau

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
C = json.loads((ROOT / "config.json").read_text())
NAME, DOMAIN = C["name"], C["domain"].rstrip("/")
PAGES = []  # (pfad, prio) für die Sitemap
e = html.escape

def todo(t):
    """Sichtbarer Platzhalter für Angaben, die noch fehlen."""
    return f'<span class="todo">[{t}]</span>'


PHONE = C.get("phone") or todo("TELEFONNUMMER ERGÄNZEN")
ORT = C.get("standort") or todo("STANDORT ERGÄNZEN")
PERSON = C.get("ansprechpartner") or todo("NAME ERGÄNZEN")
EINSCH = "/kontakt/?thema=einschaetzung"
# Tracking (config.json → "tracking"): leere Werte = aus. GA4, Google Ads und Meta laden nur nach Einwilligung.
T = {k: v.strip() for k, v in (C.get("tracking") or {}).items() if not k.startswith("_") and isinstance(v, str) and v.strip()}
EINW = any(k in T for k in ("ga4", "google_ads", "meta_pixel"))  # zustimmungspflichtige Dienste → Einwilligungs-Banner


def ph(v):
    """Angabe aus config.json; leer oder „[…]“ → sichtbarer Platzhalter."""
    v = (v or "").strip()
    return todo((v.strip("[]") if v else "ANGABE") + " ERGÄNZEN") if not v or v.startswith("[") else e(v)

NAV = [("/leistungen/", "Leistungen"), ("/branchen/", "Branchen"), ("/beispiele/", "Beispiele"),
       ("/preise/", "Preise"), ("/ratgeber/", "Ratgeber")]


def layout(path, title, desc, body, schema=None, crumbs=None, noindex=False, js=None):
    nav = "".join(f'<a href="{h}"{" aria-current=page" if path.startswith(h) else ""}>{t}</a>' for h, t in NAV)
    robots = '<meta name="robots" content="noindex,nofollow">' if C["preview"] or noindex else '<meta name="robots" content="index,follow">'
    ld = [{"@context": "https://schema.org", "@type": "ProfessionalService", "name": NAME, "url": DOMAIN + "/",
           "email": C["email"], "areaServed": "DE", "description": C["tagline"]}]
    if crumbs:
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + u} for i, (u, n) in enumerate(crumbs)]})
    if schema:
        ld.extend(schema if isinstance(schema, list) else [schema])
    crumb_html = ""
    if crumbs and len(crumbs) > 1:
        crumb_html = '<div class="wrap"><nav class="crumbs" aria-label="Brotkrumen">' + " / ".join(
            f'<a href="{u}">{e(n)}</a>' if i < len(crumbs) - 1 else e(n) for i, (u, n) in enumerate(crumbs)) + "</nav></div>"
    full_title = title if NAME in title else f"{title} | {NAME}"
    bar = '<div class="preview-bar">Vorschau – diese Seite ist noch nicht öffentlich.</div>' if C["preview"] else ""
    return f"""<!doctype html>
<html lang="de"{f' data-sb="{C["supabase_url"]}" data-key="{C["supabase_key"]}"' if C.get("supabase_url") else ""}><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(full_title)}</title><meta name="description" content="{e(desc)}">{robots}
{"".join(f'<meta name="{n}" content="{e(T[k])}">' for k, n in (("search_console", "google-site-verification"), ("bing", "msvalidate.01")) if k in T)}
<link rel="canonical" href="{DOMAIN}{path}"><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta property="og:title" content="{e(full_title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="{DOMAIN}{path}"><meta property="og:locale" content="de_DE">
<meta name="theme-color" content="#f2f0eb"><link rel="preload" href="/fonts/intertight.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/style.css">{'<link rel="stylesheet" href="/intern.css">' if js else ""}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head><body>{bar}<a class="skip" href="#inhalt">Zum Inhalt</a>
<header class="top"><div class="wrap"><a class="logo" href="/" aria-label="{NAME} Startseite">{LOGO}{NAME}</a>
<button class="burger" aria-label="Menü" aria-expanded="false">☰</button>
<nav class="nav" aria-label="Hauptnavigation">{nav}<button class="theme" aria-label="Hell/Dunkel umschalten">◐</button><a class="btn" href="{EINSCH}">Ersteinschätzung</a></nav></div></header>
<main id="inhalt">{crumb_html}{body}</main>
<footer><div class="wrap"><div class="cols">
<div><a class="logo" href="/">{LOGO}{NAME}</a><p style="margin-top:16px;max-width:22em">{e(C["tagline"])}</p><p>Aus {ORT} für Betriebe in ganz Deutschland.<br><a href="mailto:{C["email"]}" style="display:inline;color:inherit;text-decoration:underline">{C["email"]}</a><br>{PHONE}</p></div>
<div><p class="fh">Leistungen</p>{"".join(f'<a href="/leistungen/{l["slug"]}/">{l["titel"]}</a>' for l in LEISTUNGEN)}</div>
<div><p class="fh">Branchen</p>{"".join(f'<a href="/branchen/{b["slug"]}/">{b["titel"]}</a>' for b in BRANCHEN)}</div>
<div><p class="fh">Agentur</p><a href="/beispiele/">Beispiele</a><a href="/ablauf/">Ablauf</a><a href="/preise/">Preise</a><a href="/faq/">Häufige Fragen</a><a href="/kontakt/">Kontakt</a></div>
</div><div class="ft-mark" aria-hidden="true">{NAME}<span>.</span></div><div class="legal"><span>© {date.today().year} {NAME}</span><span><a href="/impressum/" style="display:inline">Impressum</a> · <a href="/datenschutz/" style="display:inline">Datenschutz</a> · <a href="/agb/" style="display:inline">AGB</a>{' · <a href="#" data-einwilligung style="display:inline">Datenschutz-Einstellungen</a>' if EINW else ""}</span></div></div></footer>
{'<script src="/dienste.js" defer></script><script src="/einwilligung.js" defer></script>' if EINW and not js else ""}<script src="/main.js" defer></script>{f'<script src="/{js}" defer></script>' if js else ""}</body></html>"""


def write(path, title, desc, body, prio=0.6, **kw):
    out = DIST / path.strip("/") / "index.html" if path != "/404.html" else DIST / "404.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(layout(path, title, desc, body, **kw), encoding="utf-8")
    if path not in ("/404.html", "/danke/") and not kw.get("noindex"):
        PAGES.append((path, prio))


def cta(titel="Wo verlieren Sie heute Anfragen?", text="In 20 Minuten sehen wir uns Ihre Website und Ihr Google-Profil an. Danach wissen Sie, was sich für Ihren Betrieb lohnt, auch wenn wir nicht zusammenarbeiten.", btn="Kostenlose Ersteinschätzung erhalten", href=EINSCH):
    return f'''<section class="cta-x"><div class="wrap"><div><p class="kicker">Nächster Schritt</p><h2>{titel}</h2></div><div><p>{text}</p><a class="btn" href="{href}">{btn} <span class="ar">→</span></a>
<p class="cta-alt">Lieber direkt? <a href="mailto:{C["email"]}">{C["email"]}</a> · {PHONE}</p></div></div></section>'''


def faq_html(items):
    return "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in items)


def faq_schema(items):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}


def ticks(items):
    return '<ul class="ticks">' + "".join(f"<li>{x}</li>" for x in items) + "</ul>"


def frame(slug, mobil=False, eager=False):
    """Browser- bzw. Handyrahmen. Screenshot als Platzhalter, darüber die echte Vorschau-Seite als verkleinerte Live-Ansicht."""
    art = "m" if mobil else "d"
    img = ROOT / "static" / "vorschau-bilder" / f"{slug}-{art}.webp"
    name = next(b["name"] for b in BEISPIELE if b["slug"] == slug)
    lazy = "" if eager else ' loading="lazy"'
    w, h = (390, 780) if mobil else (1440, 900)
    pic = f'<img src="/vorschau-bilder/{slug}-{art}.webp" alt="Vorschau der Website {e(name)}" width="{w}" height="{h}"{lazy} decoding="async">' if img.exists() else '<div class="ph"></div>'
    live = f'<div class="lv">{pic}<iframe data-src="/vorschau/{slug}/?embed=1" width="{w}" height="{h}" title="Live-Ansicht {e(name)}" tabindex="-1" aria-hidden="true" scrolling="no"></iframe></div>'
    if mobil:
        return f'<div class="phone"><div class="ip"><div class="scr"><div class="sb" aria-hidden="true"><span>9:41</span><i class="di"></i><span class="si"><b></b><b></b><b></b><b></b><em></em></span></div>{live}<i class="hi" aria-hidden="true"></i></div></div></div>'
    return f'<div class="browser"><div class="bar"><i></i><i></i><i></i><span>{e(name.lower().replace(" ", "-").replace("&", "und"))}.de</span></div>{live}</div>'


BILDCACHE = ROOT / ".bildcache"


def bilder_laden():
    """Lädt die Pexels-Fotos der Vorschau-Seiten (Vercel-Build hat Internet). Fehlschläge werden übersprungen –
    dann zeigen die Seiten ihre Zeichnungen."""
    import urllib.request
    BILDCACHE.mkdir(exist_ok=True)
    (DIST / "bilder").mkdir(parents=True, exist_ok=True)
    ok = 0
    for pid in vorschau.alle_fotos():
        groessen = {}
        for w in vorschau.BREITEN:                     # je Foto drei Breiten, damit Handy und Kacheln kleine Dateien laden
            hit = next(BILDCACHE.glob(f"{pid}-{w}.*"), None)
            if not hit:
                url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&fm=webp&w={w}"
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Lotwerk-Build)"})
                    with urllib.request.urlopen(req, timeout=20) as r:
                        typ, data = r.headers.get("Content-Type", ""), r.read()
                    if typ.startswith("image/") and len(data) > 2000:
                        hit = BILDCACHE / f"{pid}-{w}.{'webp' if 'webp' in typ else 'jpg'}"
                        hit.write_bytes(data)
                except Exception:
                    hit = None
            if hit:
                shutil.copy(hit, DIST / "bilder" / hit.name)
                groessen[w] = hit.name
        if groessen:
            vorschau.FOTO[pid] = groessen
            ok += 1
    print(f"Fotos: {ok} von {len(vorschau.alle_fotos())} geladen")


def vorschauseiten():
    bilder_laden()
    for slug, d in vorschau.DEMOS.items():
        out = DIST / "vorschau" / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(vorschau.page(d, NAME, f"/beispiele/{slug}/"), encoding="utf-8")


def paket_summe(b):
    return sum(v for _, v in b["paket"])


# ------------------------------------------------------------------ Seiten
def galerie(items):
    return "".join(f'''<article class="show"><a class="show-img" href="/vorschau/{b["slug"]}/">{frame(b["slug"])}</a>
<div class="show-meta"><div><span class="pill">{b["branche"]}</span><h3>{b["name"]}</h3></div><span class="price-mini">{eur(paket_summe(b))}<small>im 1. Jahr</small></span></div>
<div class="show-links"><a href="/vorschau/{b["slug"]}/">Live-Vorschau →</a><a href="/beispiele/{b["slug"]}/">Kundenweg &amp; Preis</a></div></article>''' for b in items)


CJ_STUFEN = [
    ("1", "Bedarf", "Das Dach tropft, der Pony ist zu lang, der Vater braucht Pflege.", "Noch keine Entscheidung. Aber ab jetzt wird gesucht.", ""),
    ("2", "Suche bei Google, Maps &amp; KI", "„Dachdecker in der Nähe“ bei Google oder „Welcher Friseur in Musterstadt ist gut?“ bei ChatGPT. Fast immer auf dem Handy.", "Wer hier nicht oben steht oder von der KI nicht genannt wird, wird nicht gesehen.", "google"),
    ("3", "Vergleich", "Drei Anbieter, Sterne, Fotos, erste Eindrücke. Dauer: wenige Minuten.", "Bewertungen und ein gepflegtes Profil entscheiden, wer angeklickt wird.", ""),
    ("4", "Die Website", "Was kostet es? Wie läuft es ab? Wer sind die Menschen? Kann ich sofort anfragen?", "Hier fällt die Entscheidung, oder der Kunde geht zurück zur Suche.", "web"),
    ("5", "Anfrage &amp; Wiederkommen", "Termin, Rückruf, Fotos schicken. Danach: Bewertung, Empfehlung, Stammkunde.", "Ein einfacher nächster Schritt und Erinnerungen machen aus Kunden Stammkunden.", ""),
]


def customer_journey():
    stufen = "".join(f'<li class="cj-step{" hl" if hl else ""}"><span class="cj-n">{int(n):02d}{"<span class=cj-tag>· " + ("Sichtbarkeit" if hl == "google" else "Überzeugung") + "</span>" if hl else ""}</span><h3>{t}</h3><p>{tut}</p><p class="cj-key">{key}</p></li>' for n, t, tut, key, hl in CJ_STUFEN)
    return f'''<section class="cj" id="customer-journey"><div class="wrap">
<div class="sec-head"><span class="idx"><b>(01)</b> Kundenweg</span><h2>Bevor jemand anruft, hat er sich <em>längst entschieden.</em></h2>
<p>Gesucht, verglichen, Ihre Website angesehen: meist in wenigen Minuten, meist auf dem Handy. Zwei Stellen entscheiden: ob man Sie bei Google und in KI-Antworten findet, und ob Ihre Website dann überzeugt.</p></div>
<ol class="cj-line">{stufen}</ol>
<div class="split-row" style="margin-top:clamp(56px,7vw,96px);border-top:1px solid var(--line)"><div><p class="kicker">Sichtbarkeit</p><h3>Seite 2 ist <em class="serif">unsichtbar.</em></h3>
<p>Bei lokalen Suchen zeigt Google zuerst eine Karte mit drei Betrieben. Wer dort und in den ersten Treffern steht, bekommt den Großteil der Anfragen. Deshalb arbeiten wir an Google-Profil, Bewertungen und einer Seite für jede Leistung und jeden Ort.</p><a class="more" href="/leistungen/seo/">Wie wir Sie nach oben bringen</a></div>
<div class="serp" aria-hidden="true"><div class="serp-q">dachdecker in der nähe</div><div class="serp-map"><i style="left:22%;top:40%"></i><i class="me" style="left:52%;top:55%"></i><i style="left:74%;top:30%"></i></div>
<div class="serp-r me"><b>Ihr Betrieb</b><span class="st">★★★★★ 4,9 (126)</span><span>Geöffnet · Anrufen · Website · Route</span></div>
<div class="serp-r"><b>Mitbewerber A</b><span class="st">★★★★☆ 4,3 (41)</span></div><div class="serp-r"><b>Mitbewerber B</b><span class="st">★★★★☆ 4,1 (18)</span></div>
<div class="serp-more">Seite 2: Hier sucht fast niemand mehr.</div></div></div>
<div class="facts"><div><b>27,6 %<sup>1</sup></b><span>aller Klicks gehen an das erste Suchergebnis</span></div><div><b>0,63 %<sup>1</sup></b><span>klicken überhaupt auf Seite 2</span></div><div><b>93 %<sup>3</sup></b><span>lesen Bewertungen, bevor sie einen Betrieb wählen</span></div><div><b>+32 %<sup>4</sup></b><span>mehr Absprünge, wenn die Seite 3 statt 1 Sekunde lädt</span></div></div>
<div class="split-row"><div><p class="kicker">Neu: Suche mit KI</p><h3>Immer öfter fragt der Kunde nicht Google, <em class="serif">sondern ChatGPT.</em></h3>
<p>Die Hälfte der Deutschen nutzt zumindest manchmal einen KI-Chat statt der klassischen Suche.<sup>5</sup> ChatGPT, Gemini und Googles KI-Übersicht nennen meist nur zwei, drei Betriebe und stützen sich auf dieselben Signale: gepflegtes Profil, gute Bewertungen und eine Website, die Leistungen, Orte und Preise klar beschreibt.</p><a class="more" href="/leistungen/seo/">Sichtbar bei Google und KI</a></div>
<div class="ai-chat" aria-hidden="true"><div class="ai-q">Welcher Dachdecker in Musterstadt ist zuverlässig und macht auch Photovoltaik?</div>
<div class="ai-a"><span class="ai-l">KI-Assistent</span><p>Empfehlenswert sind zum Beispiel:</p><ol><li class="me"><b>Ihr Betrieb</b>: Meisterbetrieb, 4,9 Sterne aus 126 Bewertungen, Dach und PV vom selben Team, Festpreis-Angebot in 5 Tagen.</li><li><b>Mitbewerber A</b>: 4,3 Sterne, vor allem Reparaturen.</li></ol><span class="ai-src">Quellen: Google-Profil · ihr-betrieb.de · Bewertungen</span></div></div></div>
<p class="cj-src">1 Backlinko, Analyse von 4 Mio. Google-Ergebnissen · 2 Think with Google, mobile „in der Nähe“-Suchen · 3 BrightLocal, Local Consumer Review Survey 2025 · 4 Google/SOASTA, mobile Ladezeiten · 5 Bitkom, KI-Chats und Internetsuche 2025. Internationale Erhebungen, Werte für Deutschland können abweichen.</p></div></section>
'''


def arbeiten():
    out = []
    for i, b in enumerate(BEISPIELE, 1):
        out.append(f'''<article class="work-item"><a href="/vorschau/{b["slug"]}/">{frame(b["slug"])}</a>
<div class="work-meta"><span class="wm-n">{i:02d}</span><h3>{b["name"]}</h3><span class="wm-b">{b["branche"]} · Beispielbetrieb</span><a class="wm-l" href="/beispiele/{b["slug"]}/">Kundenweg ansehen</a></div></article>''')
    return "".join(out)


SVC_ORDER = ["webentwicklung", "seo", "google-ads", "recruiting", "wachstum"]


def svc_liste(items, preis=True):
    return f'<ul class="svc{"" if preis else " np"}">' + "".join(f'<li><a href="/leistungen/{l["slug"]}/"><span class="n">{i:02d}</span><span class="t">{l["titel"]}</span><span class="d">{l["kurz"]}</span>{f"<span class=p>{l[chr(97)+chr(98)]}</span>" if preis else ""}<span class="a" aria-hidden="true">→</span></a></li>' for i, l in enumerate(items, 1)) + "</ul>"


def faq_mini(items):
    return f'<div class="grid2 faq-mini"><div><h3 class="h2s">Häufige Fragen</h3><p>Ihre Frage fehlt? <a href="/faq/">Alle Antworten</a> oder <a href="{EINSCH}">direkt fragen</a>.</p></div><div>{faq_html(items)}</div></div>'


def startseite():
    lst = sorted(LEISTUNGEN, key=lambda l: SVC_ORDER.index(l["slug"]))
    fq = [f for f in FAQ if f[0] in ("Garantieren Sie Ergebnisse?", "Wem gehört die Website?", "Was muss ich selbst beitragen?", "Gibt es lange Vertragslaufzeiten?")]
    tl = [("Tag 1", "Ersteinschätzung", "20 Minuten per Telefon oder Video. Danach wissen Sie, ob und wie wir helfen können.", "Kostenlos und unverbindlich"),
          ("Tag 3", "Angebot", "Ziel, Umfang und Zeitplan auf einer Seite.", "Festpreis statt Stundenzettel"),
          ("Tag 10", "Entwurf", "Die Startseite live im Browser. Sie testen auf Ihrem Handy und geben Feedback.", "Zweite Rate erst nach Ihrer Freigabe"),
          ("Tag 21", "Start", "Website online, Google-Profil überarbeitet, Messung aktiv.", "Website, Domain und Zugänge gehören Ihnen"),
          ("Jeden Monat", "Pflege & Bericht", f"Updates, Sicherheit und Technik laufen im Hintergrund, ohne Arbeit für Sie. Änderungswünsche schicken Sie kurz per E-Mail. Ein Ansprechpartner: {PERSON}.", "Bericht in Anrufen und Anfragen")]
    # Kundenstimmen und Fallstudie sind ausgeblendet, bis es echte Inhalte gibt. VOR DER LIVESCHALTUNG einbinden (CLAUDE.md → Offene Punkte).
    # Vorlage: <div class="proof-box"><p class="kicker">Kundenstimmen</p>…</div> und <div class="proof-box"><p class="kicker">Fallstudie</p>…</div>
    belege = ""
    tlh = "".join(f'<li><span class="d">{d}</span><h3>{t}</h3><p>{x}</p><p class="usp">{u}</p></li>' for d, t, x, u in tl)
    body = f"""
<section class="h-hero"><div class="wrap">
<p class="kicker">Webagentur für lokale Betriebe · aus {ORT} für ganz Deutschland</p>
<h1>Websites und Google-Sichtbarkeit für <em>lokale Betriebe.</em></h1>
<div class="h-row"><p class="lead">Für Handwerk, Kanzleien, Pflegedienste und Praxen. Wir bauen Ihre Website, bringen Sie bei Google und in Maps nach vorn und zeigen Ihnen jeden Monat, wie viele Anfragen daraus entstehen.</p>
<div class="actions"><a class="btn" href="{EINSCH}">Kostenlose Ersteinschätzung <span class="ar">→</span></a><a class="link" href="#vorschau">Beispiel-Websites ansehen</a></div></div></div>
<div class="h-stage"><div class="wrap"><div class="showcase"><a href="/vorschau/dachdecker-solar/" class="sc-desk">{frame("dachdecker-solar", eager=True)}</a><a href="/vorschau/friseur/" class="sc-phone">{frame("friseur", mobil=True, eager=True)}</a></div></div></div>
</section>
{customer_journey()}
<section id="vorschau"><div class="wrap"><div class="sec-head"><span class="idx"><b>(02)</b> Beispiel-Websites</span><h2>So könnte Ihre Website <em>aussehen.</em></h2>
<p>Sieben vollständig gebaute Websites für erfundene Beispielbetriebe. Jede folgt dem Kundenweg ihrer Branche. Klicken Sie sich durch, gern auch auf dem Handy.</p></div>
<div class="work">{arbeiten()}</div></div></section>
<section><div class="wrap"><div class="sec-head"><span class="idx"><b>(03)</b> Leistungen</span><h2>Alles zwischen Suche <em>und Anfrage.</em></h2><p>Einzeln buchbar oder als Programm mit gemeinsamem Ziel.</p></div>{svc_liste(lst, preis=False)}</div></section>
<section><div class="wrap"><div class="sec-head"><span class="idx"><b>(04)</b> So arbeiten wir</span><h2>In drei Wochen online, <em>mit festem Zeitplan.</em></h2><p>Ihr Aufwand: rund eine Stunde im ersten Monat, dazu ein paar Fotos mit dem Handy. Danach haben Sie keine Arbeit damit, außer Sie möchten etwas ändern.</p></div>
<ol class="tl tl5">{tlh}</ol>
<div class="proof"><div class="proof-box"><p class="kicker">Prüfen Sie uns selbst</p><p>Diese Website ist so gebaut, wie wir Ihre bauen. Messen Sie die Ladezeit mit dem kostenlosen Werkzeug von Google.</p><a class="more" href="https://pagespeed.web.dev/analysis?url={DOMAIN}/" rel="noopener" target="_blank">Mit Google PageSpeed testen ↗</a></div>
{belege}</div>
{faq_mini(fq)}</div></section>
{cta()}"""
    write("/", f"{NAME} – Websites & Google-Sichtbarkeit für lokale Betriebe", "Websites, lokale SEO und Google Ads für Handwerk, Kanzleien, Pflegedienste und Praxen in ganz Deutschland. Festpreis, erster Entwurf nach 7 Tagen.", body, prio=1.0, crumbs=[("/", "Start")])


def leistungen():
    lst = sorted(LEISTUNGEN, key=lambda l: SVC_ORDER.index(l["slug"]))
    write("/leistungen/", "Leistungen: Websites, SEO, Google Ads, Recruiting", "Websites ab 1.790 €, lokale SEO ab 490 €/Monat, Google Ads ab 290 €/Monat und Recruiting für lokale Betriebe. Alles zum Festpreis.",
          f'<section class="hero"><div class="wrap"><p class="kicker">Leistungen</p><h1>Fünf Leistungen für <em>mehr Anfragen.</em></h1><p class="lead">Mehr passende Anfragen und die Fachkräfte, um sie abzuarbeiten. Jede Leistung funktioniert allein. Zusammen wirken sie stärker.</p></div></section><section style="padding-top:0;border:0"><div class="wrap">{svc_liste(lst)}</div></section>{cta()}',
          prio=0.9, crumbs=[("/", "Start"), ("/leistungen/", "Leistungen")])
    for l in LEISTUNGEN:
        p = f"/leistungen/{l['slug']}/"
        t = TIEFE[l["slug"]]
        steps = "".join(f"<li><h3>{a}</h3><p>{b}</p></li>" for a, b in l["ablauf"])
        others = [o for o in sorted(LEISTUNGEN, key=lambda x: SVC_ORDER.index(x["slug"])) if o is not l]
        glance = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in l["eckdaten"])
        href = f"/kontakt/?thema={l['k']}"
        faq = l["faq"] + t["faq"]
        anker = [("worum", t["intro_h2"]), ("leistung", "Was Sie bekommen")] + [(f"a{i}", h) for i, (h, _, _) in enumerate(t["abschnitte"])] + \
                [("kosten", "Kosten"), ("fehler", "Typische Fehler"), ("messung", "Was wir messen"), ("fragen", "Häufige Fragen")]
        toc = '<nav class="toc" aria-label="Auf dieser Seite"><p class="kicker">Auf dieser Seite</p><ol>' + "".join(f'<li><a href="#{a}">{e(h)}</a></li>' for a, h in anker) + "</ol></nav>"
        fuer = "".join(f'<div class="fw"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a, b in t["fuer_wen"])
        absch = "".join(
            f'<section id="a{i}"><div class="wrap grid2 tief"><h2 class="h2s">{e(h)}</h2><div class="prose">{"".join(f"<p>{e(x)}</p>" for x in ps)}{ticks([e(x) for x in liste]) if liste else ""}</div></div></section>'
            for i, (h, ps, liste) in enumerate(t["abschnitte"]))
        k = t["kosten"]
        kosten = (f'<section id="kosten"><div class="wrap grid2 tief"><h2 class="h2s">Was kostet {e(l["titel"])}?</h2><div class="prose"><p>{e(k["text"])}</p>'
                  f'<div class="tablewrap"><table class="kosten"><tbody>{"".join(f"<tr><th scope=row>{e(a)}</th><td>{e(b)}</td></tr>" for a, b in k["zeilen"])}</tbody></table></div>'
                  f'<p class="note">{e(k["hinweis"])}</p><p><a href="/preise/">Alle Preise im Überblick</a></p></div></div></section>')
        fehler = "".join(f'<div class="fw"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a, b in t["fehler"])
        mess = "".join(f"<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>" for a, b in t["messung"])
        dienst = {"@context": "https://schema.org", "@type": "Service", "name": l["titel"], "description": t["kurz"], "areaServed": "DE",
                  "provider": {"@type": "ProfessionalService", "name": NAME, "url": DOMAIN + "/"}, "url": DOMAIN + p}
        body = f"""<section class="hero"><div class="wrap grid"><div><p class="kicker">{l["titel"]}</p><h1>{l["h1"]}</h1><p class="lead">{l["lead"]}</p><div class="actions"><a class="btn" href="{href}">{l["cta"]} <span class="ar">→</span></a><a class="link" href="/preise/">Alle Preise</a></div></div>
<aside class="glance" aria-label="Auf einen Blick"><p class="kicker">Auf einen Blick</p><dl>{glance}</dl></aside></div></section>
<section id="worum"><div class="wrap grid2 tief"><div><h2 class="h2s">{e(t["intro_h2"])}</h2>{toc}</div><div class="prose">{"".join(f"<p>{e(x)}</p>" for x in t["intro"])}<h3>Für wen sich das lohnt</h3><div class="fwl">{fuer}</div><p class="note">Beispiele nach Branche: {", ".join(f'<a href="/branchen/{b["slug"]}/">{b["titel"]}</a>' for b in BRANCHEN)}.</p></div></div></section>
<section id="leistung"><div class="wrap grid2"><div><h2 class="h2s">Was Sie bekommen</h2>{ticks(l["punkte"])}</div><div><h2 class="h2s">So gehen wir vor</h2><ol class="steps">{steps}</ol></div></div></section>
{absch}{kosten}
<section id="fehler"><div class="wrap"><h2 class="h2s" style="margin-bottom:28px">Typische Fehler, die wir vermeiden</h2><div class="fwg">{fehler}</div></div></section>
<section id="messung"><div class="wrap grid2 tief"><h2 class="h2s">Was wir jeden Monat messen</h2><div><dl class="glance mess">{mess}</dl><p class="note">Sie bekommen jeden Monat einen kurzen Bericht in Klartext.</p></div></div></section>
<section id="fragen"><div class="wrap">{faq_mini(faq)}</div></section>
<section><div class="wrap"><h2 class="h2s" style="margin-bottom:28px">Passt gut dazu</h2>{svc_liste(others)}</div></section>{cta(f"{l['titel']} für Ihren Betrieb?", "Wir sehen uns Ihre Ausgangslage an und sagen Ihnen, ob sich das für Sie lohnt. Kostenlos und unverbindlich.", l["cta"], href)}"""
        write(p, t["seo"], t["kurz"], body, prio=0.8, schema=[faq_schema(faq), dienst],
              crumbs=[("/", "Start"), ("/leistungen/", "Leistungen"), (p, l["titel"])])


def branchen():
    cards = "".join(f'<article class="show"><a class="show-img" href="/branchen/{b["slug"]}/">{frame(b["beispiel"])}</a><div class="show-meta"><div><h3>{b["titel"]}</h3></div></div><p style="color:var(--ink-2);margin:8px 0 0">{b["lead"]}</p><div class="show-links"><a href="/branchen/{b["slug"]}/">{b["seo_h1"]}</a><a href="/vorschau/{b["beispiel"]}/">Beispiel-Website</a></div></article>' for b in BRANCHEN)
    write("/branchen/", "Branchen: Websites für Friseure, Handwerk, Kanzleien, Pflege und Praxen", "Websites und Google-Sichtbarkeit für Friseure, Barbershops, Dachdecker, Steuerberater, Pflegedienste, Bestatter und Tierarztpraxen.",
          f'<section class="hero"><div class="wrap"><p class="kicker">Branchen</p><h1>Jede Branche hat ihren <em>eigenen Kundenweg.</em></h1><p class="lead">Ein Notfall am Dach läuft anders ab als die Suche nach einer Kanzlei. Deshalb starten wir nie mit einer Vorlage, sondern mit der Frage: Wie entscheiden Ihre Kunden?</p></div></section><section style="padding-top:0"><div class="wrap gallery">{cards}</div></section>{cta()}',
          prio=0.9, crumbs=[("/", "Start"), ("/branchen/", "Branchen")])
    for b in BRANCHEN:
        p = f"/branchen/{b['slug']}/"
        bsp = next(x for x in BEISPIELE if x["slug"] == b["beispiel"])
        body = f"""<section class="hero"><div class="wrap grid"><div><p class="kicker">{b["titel"]}</p><h1>{b["seo_h1"]}</h1><p class="lead"><b class="claim">{b["claim"]}</b> {b["lead"]}</p><div class="actions"><a class="btn" href="{EINSCH}">{b["cta"]} <span class="ar">→</span></a><a class="link" href="/vorschau/{bsp["slug"]}/">Beispiel-Website ansehen</a></div></div><div class="showcase small"><a href="/vorschau/{bsp["slug"]}/" class="sc-desk">{frame(bsp["slug"], eager=True)}</a><a href="/vorschau/{bsp["slug"]}/" class="sc-phone">{frame(bsp["slug"], mobil=True, eager=True)}</a></div></div></section>
<section><div class="wrap grid2"><div><h2 class="h2s">Kommt Ihnen das bekannt vor?</h2><ul class="ticks">{"".join(f"<li>{x}</li>" for x in b["probleme"])}</ul></div><div><h2 class="h2s">Was wir dagegen tun</h2>{ticks(b["loesung"])}</div></div></section>
<section><div class="wrap grid2" style="align-items:start"><div class="bignum"><div class="num">{b["zahl"][0]}</div><p>{b["zahl"][1]}</p></div><div><p class="kicker">Beispiel-Website · erfundener Betrieb</p><h2 class="h2s">{bsp["name"]}</h2><p>{bsp["teaser"]}</p><p><strong>{eur(paket_summe(bsp))}</strong> im ersten Jahr.</p><div class="actions"><a class="btn ghost" href="/vorschau/{bsp["slug"]}/">Beispiel-Website öffnen</a><a class="link" href="/beispiele/{bsp["slug"]}/">Kundenweg &amp; Preis</a></div></div></div></section>
<section style="padding-top:0;border:0"><div class="wrap"><p class="promise"><b>Fachkräfte gesucht?</b> Mit dem Recruiting-Paket kommen Bewerbungen über Ihre eigene Karriereseite statt über teure Portale. <a href="/leistungen/recruiting/">Zum Recruiting-Paket</a></p></div></section>{cta(btn=b["cta"])}"""
        write(p, b["seo_h1"], b["lead"], body, prio=0.8, crumbs=[("/", "Start"), ("/branchen/", "Branchen"), (p, b["titel"])])


def beispiele():
    cards = galerie(BEISPIELE)
    write("/beispiele/", "Beispiele mit Kundenweg und Preis", "Sieben durchgerechnete Beispiele: Kundenweg, Umsetzung, Paket und Preis für Friseur, Barber, Dachdecker, Steuerberater, Pflegedienst, Bestatter und Tierarzt.",
          f'<section class="hero"><div class="wrap"><p class="kicker">Beispiele</p><h1>Sieben Betriebe, <em>sieben Kundenwege.</em></h1><p class="lead">Jedes Beispiel erzählt, wie ein Kunde sucht, vergleicht und sich entscheidet, und was wir an jeder Stelle bauen. Mit Paketpreis aus unserer Preisliste und einer vollständigen Vorschau-Website zum Durchklicken.</p><p class="note">Die Betriebe sind erfundene Beispiele, damit Sie Ablauf und Kosten realistisch einschätzen können. Preise entsprechen unserer aktuellen Preisliste.</p></div></section><section style="padding-top:0"><div class="wrap gallery">{cards}</div></section>{cta()}',
          prio=0.9, crumbs=[("/", "Start"), ("/beispiele/", "Beispiele")])
    for b in BEISPIELE:
        p = f"/beispiele/{b['slug']}/"
        stages = "".join(f'<li class="stage"><span class="dot">{i+1}</span><h3>{t}</h3><div class="split"><div class="they"><span class="lbl">Der Kunde</span>{k}</div><div class="we"><span class="lbl">Was wir bauen</span>{w}</div></div></li>' for i, (t, k, w) in enumerate(b["kundenweg"]))
        rows = "".join(f'<tr><td>{n}</td><td class="r">{eur(v)}</td></tr>' for n, v in b["paket"])
        hinweis = f'<p class="note" style="margin-top:14px">{b["paket_hinweis"]}</p>' if b.get("paket_hinweis") else ""
        kap = [b["ausgang"], f'<p class="quote" style="font-size:1.3rem">{b["ziel"]}</p>',
               f'<p>So findet ein typischer Kunde zu {b["name"]} . Das haben wir an jeder Station gebaut:</p><ol class="journey">{stages}</ol>',
               ticks(b["umsetzung"]) + f'<p><strong>Aufgabe des Betriebs:</strong> {b["aufgabe"]}</p>',
               f'<div class="tablewrap"><table><thead><tr><th>Baustein</th><th class="r">Betrag</th></tr></thead><tbody>{rows}</tbody><tfoot><tr><td>Erstes Jahr gesamt</td><td class="r">{eur(paket_summe(b))}</td></tr></tfoot></table></div>{hinweis}',
               f"<p>{b['erwartung']}</p>"]
        chapters = "".join(f'<div class="chapter" id="kapitel-{i+1}"><div><div class="n">{i+1:02d}</div><span class="kicker" style="margin-top:8px">{KAPITEL[i]}</span></div><div>{c if c.startswith("<") else "<p>"+c+"</p>"}</div></div>' for i, c in enumerate(kap))
        nxt = BEISPIELE[(BEISPIELE.index(b) + 1) % len(BEISPIELE)]
        body = f"""<section class="hero"><div class="wrap grid"><div><p class="kicker">Beispiel · {b["branche"]} · erfundener Betrieb</p><h1>{b["name"]}</h1><p class="lead">{b["teaser"]}</p><p><span class="pill">{b["ort"]}</span> <span class="pill">{eur(paket_summe(b))} im ersten Jahr</span></p><div class="actions"><a class="btn" href="/vorschau/{b["slug"]}/">Beispiel-Website öffnen <span class="ar">→</span></a><a class="link" href="#kapitel-3">Zum Kundenweg</a></div></div><div class="showcase small"><a href="/vorschau/{b["slug"]}/" class="sc-desk">{frame(b["slug"], eager=True)}</a><a href="/vorschau/{b["slug"]}/" class="sc-phone">{frame(b["slug"], mobil=True, eager=True)}</a></div></div></section>
<section style="padding-top:0"><div class="wrap">{chapters}<p class="note">Erfundenes Beispiel zur Veranschaulichung. Ergebnisse hängen von Markt, Wettbewerb und Mitarbeit ab und sind nicht garantiert.</p><p style="margin-top:22px"><a class="more" href="/beispiele/{nxt["slug"]}/">Nächstes Beispiel: {nxt["name"]} ({nxt["branche"]}) →</a></p></div></section>{cta("Wie sieht Ihr Kundenweg aus?", "Im Erstgespräch skizzieren wir ihn gemeinsam, kostenlos.")}"""
        write(p, f"Beispiel {b['branche']}: {b['name']}", b["teaser"], body, prio=0.7,
              crumbs=[("/", "Start"), ("/beispiele/", "Beispiele"), (p, b["branche"])])


def preise():
    P = PREISE
    def box(t, amt, per, items, feat=False, note="", k="website"):
        return f'<div class="card price{" feat" if feat else ""}">{"<span class=pill>Beliebt</span>" if feat else ""}<h2 class="h3" style="margin-top:8px">{t}</h2><div class="amt">{amt}</div><div class="per">{per}</div>{ticks(items)}{f"<p class=note>{note}</p>" if note else ""}<a class="btn{"" if feat else " ghost"}" href="/kontakt/?thema={k}" style="margin-top:18px">Angebot anfragen</a></div>'
    web = box("Website Start", eur(P["web_start"]), f"einmalig · Pflege {P['pflege_start']} €/Monat (12 Monate)", ["Bis zu 5 Seiten", "Texte und Struktur inklusive", "Google-Unternehmensprofil eingerichtet", "Kontakt- oder Buchungsformular", "Fertig in 2–3 Wochen"]) + \
          box("Website Wachstum", eur(P["web_wachstum"]), f"einmalig · Pflege {P['pflege_wachstum']} €/Monat (12 Monate)", ["Bis zu 15 Seiten", "Eigene Seiten je Leistung und Ort", "Karriere- oder Bewerbungsbereich", "Ratgeber-Bereich", "Anruf- und Formularmessung"], feat=True) + \
          box("Wachstumsprogramm", eur(P["programm"]), f"pro Monat · 12 Monate · {eur(P['prog_setup'])} Einrichtung", ["Website Wachstum inklusive", "SEO Plus inklusive", "Google-Ads-Betreuung inklusive", "Monatsbericht, Gespräch auf Wunsch", "Gemeinsames, messbares Ziel"], k="wachstum", note=f"Einzeln im ersten Jahr: {eur(P['web_wachstum'] + 12*P['pflege_wachstum'] + 12*P['seo_plus'] + P['ads_setup'] + 12*P['ads'])}")
    monat = [("SEO Lokal", P["seo_lokal"], "Profil, Verzeichnisse, 1 neue Seite pro Monat, Bericht. 6 Monate Mindestlaufzeit."),
             ("SEO Plus", P["seo_plus"], "Wie Lokal, plus 2–3 Inhalte pro Monat, Bewertungsprozess."),
             ("Google-Ads-Betreuung", P["ads"], f"Einrichtung {P['ads_setup']} € einmalig. Monatlich kündbar, Budget separat."),
             ("Recruiting Basis", P["rec_basis"], f"Eine Stelle: Karriereseite, Bewerbung in 60 Sekunden, Anzeigen auf Instagram und Facebook, Anpassung monatlich. Einrichtung {eur(P['rec_basis_setup'])} einmalig, Budget separat, 3 Monate Mindestlaufzeit."),
             ("Recruiting Komplett", P["rec"], f"Mehrere Stellen, auch Google-Anzeigen, wöchentlich nachgesteuert. Bewerbungs-Garantie, Stellenwechsel für 30 % der Einrichtung. Einrichtung {eur(P['rec_setup'])} einmalig, Budget separat."),
             ("Pflege & Hosting Start", P["pflege_start"], "Hosting, Updates, Sicherheit, kleine Änderungen. 12 Monate Laufzeit, verlängert sich jährlich."),
             ("Pflege & Hosting Wachstum", P["pflege_wachstum"], "Wie Start, plus 1 Stunde Änderungen pro Monat. 12 Monate Laufzeit, verlängert sich jährlich.")]
    rows = "".join(f"<tr><td><strong>{n}</strong></td><td>{d}</td><td class='r'>{eur(v)}/Monat</td></tr>" for n, v, d in monat)
    faq = [("Sind die Preise Endpreise?", "Ja. " + C["impressum"]["ust"]), ("Gibt es versteckte Kosten?", "Nein. Werbebudget für Anzeigen zahlen Sie direkt an Google oder Meta. Fremdkosten wie spezielle Buchungstools besprechen wir vorher."), ("Kann ich klein anfangen?", "Ja. Viele starten mit einer Website Start und ergänzen später SEO oder Anzeigen.")]
    body = f"""<section class="hero"><div class="wrap"><p class="kicker">Preise</p><h1>Feste Preise. <em>Vorab.</em></h1><p class="lead">Sie wissen vorher, was es kostet. Ohne Stundenzettel, ohne Prozente vom Werbebudget.</p></div></section>
<section style="padding-top:0"><div class="wrap grid3">{web}</div></section>
<section style="padding-top:0"><div class="wrap"><div class="feature-row"><div><p class="kicker">Recruiting</p><h2 class="h2s">Recruiting-Paket: Fachkräfte statt Stellenportale</h2><p>Karriereseite mit Einblicken in den Arbeitsalltag, Bewerbung in 60 Sekunden ohne Lebenslauf und Anzeigen im Umkreis. Für Pflege, Handwerk, Praxen und Kanzleien.</p><a class="more" href="/leistungen/recruiting/">Mehr zum Recruiting-Paket →</a></div><div><div class="amt" style="font:600 2.2rem var(--serif)"><small style="font:500 .9rem var(--sans);color:var(--ink-2)">ab </small>{eur(P["rec_basis"])}<small style="font:500 .9rem var(--sans);color:var(--ink-2)"> / Monat</small></div><p style="color:var(--ink-2)"><b>Basis</b> (1 Stelle): {eur(P["rec_basis_setup"])} Einrichtung + {eur(P["rec_basis"])} / Monat<br><b>Komplett</b>: {eur(P["rec_setup"])} Einrichtung + {eur(P["rec"])} / Monat<br>Werbebudget separat · nach 3 Monaten monatlich kündbar · Komplett mit Bewerbungs-Garantie und Stellenwechsel für 30 % der Einrichtung</p><a class="btn" href="/kontakt/?thema=recruiting">Recruiting-Paket besprechen <span class="ar">→</span></a></div></div></div></section>
<section><div class="wrap"><h2 class="h2s">Laufende Leistungen</h2><div class="tablewrap"><table><thead><tr><th>Leistung</th><th>Umfang</th><th class="r">Preis</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>
<section><div class="wrap"><div class="grid2 faq-mini"><div><h2 class="h2s">Fragen zu den Preisen</h2><p>Durchgerechnete Pakete finden Sie in den <a href="/beispiele/">Beispielen</a>.</p></div><div>{faq_html(faq)}</div></div></div></section>{cta("Welches Paket passt zu Ihnen?", "Wir empfehlen nur, was sich für Ihren Betrieb rechnet. Die Ersteinschätzung ist kostenlos.")}"""
    write("/preise/", "Preise für Website, SEO und Google Ads", "Website ab 1.790 €, SEO ab 490 €/Monat, Google Ads ab 290 €/Monat, Recruiting-Paket 790 €/Monat, Wachstumsprogramm 1.390 €/Monat plus Einrichtung. Feste Preise ohne Überraschungen.", body, prio=0.9, schema=faq_schema(faq), crumbs=[("/", "Start"), ("/preise/", "Preise")])


def ablauf():
    steps = [("Erstgespräch (20 Min.)", "Per Telefon oder Video. Wir fragen nach Ihren Zielen, Ihren Kunden und dem, was bisher nicht funktioniert hat."),
             ("Kurzanalyse", "Wir sehen uns Ihre Website und Ihr Google-Profil an. Sie bekommen die wichtigsten Punkte schriftlich."),
             ("Angebot mit Festpreis", "Binnen zwei Werktagen. Mit Ziel, Umfang, Zeitplan und Preis."),
             ("Start-Workshop (60 Min.)", "Wir gehen den Kundenweg gemeinsam durch und sammeln alles, was wir für Texte brauchen."),
             ("Umsetzung", "Sie sehen nach einer Woche den ersten Entwurf im Browser. Feedback per E-Mail oder kurzem Call."),
             ("Freischaltung", "Website online, Messung aktiv, Profil und Kampagnen laufen."),
             ("Monatlich", "Bericht mit den Zahlen, die zählen: Anfragen, Anrufe, Kosten pro Anfrage. Einmal im Quartal planen wir die nächsten Schritte.")]
    body = f"""<section class="hero"><div class="wrap grid2"><div><p class="kicker">Ablauf</p><h1>So arbeiten wir <em>zusammen.</em></h1><p class="lead">Klare Schritte, wenig Aufwand für Sie. Im ersten Monat brauchen wir rund eine Stunde Ihrer Zeit. Danach haben Sie keine Arbeit damit, außer Sie möchten etwas ändern.</p></div><div><ol class="steps">{"".join(f"<li><h3>{a}</h3><p>{b}</p></li>" for a,b in steps)}</ol></div></div></section>
<section><div class="wrap"><dl class="principles"><div><dt>Ohne Anfahrt</dt><dd>Alles läuft per Telefon, Video und E-Mail. Aus {ORT} für ganz Deutschland.</dd></div><div><dt>Alle Zugänge bei Ihnen</dt><dd>Google-Profil, Anzeigenkonto, Domain: Sie haben jederzeit Zugriff. Nichts läuft über Umwege.</dd></div><div><dt>Klare Laufzeiten</dt><dd>Pflege 12 Monate, SEO 6 Monate, Google Ads monatlich kündbar. Alles steht vorher im Angebot.</dd></div></dl></div></section>{cta()}"""
    write("/ablauf/", "Ablauf der Zusammenarbeit", "Vom Erstgespräch bis zum Monatsbericht: so arbeiten wir mit Ihnen zusammen.", body, prio=0.7, crumbs=[("/", "Start"), ("/ablauf/", "Ablauf")])


def faq_page():
    write("/faq/", "Häufige Fragen", "Antworten zu Laufzeiten, Preisen, Eigentum an der Website, Datenschutz und Zusammenarbeit.",
          f'<section class="hero"><div class="wrap grid2"><div><p class="kicker">FAQ</p><h1>Häufige <em>Fragen.</em></h1><p class="lead">Ihre Frage ist nicht dabei? <a href="/kontakt/">Schreiben Sie uns.</a></p></div><div>{faq_html(FAQ)}</div></div></section>{cta()}',
          prio=0.6, schema=faq_schema(FAQ), crumbs=[("/", "Start"), ("/faq/", "Häufige Fragen")])


def ratgeber():
    cards = '<ul class="svc rg">' + "".join(f'<li><a href="/ratgeber/{r["slug"]}/"><span class="n">{r["min"]} Min.</span><span class="t">{r["titel"]}</span><span class="d">{r["kurz"]}</span><span class="a" aria-hidden="true">→</span></a></li>' for r in RATGEBER) + "</ul>"
    write("/ratgeber/", "Ratgeber", "Praxiswissen zu Websites, lokaler SEO, Google Ads und Google-Unternehmensprofil für kleine Betriebe.",
          f'<section class="hero"><div class="wrap"><p class="kicker">Ratgeber</p><h1>Wissen, das Sie <em>selbst umsetzen können.</em></h1><p class="lead">Ohne Fachchinesisch. Vieles davon schaffen Sie an einem Nachmittag.</p></div></section><section style="padding-top:0;border:0"><div class="wrap">{cards}</div></section>{cta()}',
          prio=0.7, crumbs=[("/", "Start"), ("/ratgeber/", "Ratgeber")])
    for r in RATGEBER:
        p = f"/ratgeber/{r['slug']}/"
        schema = {"@context": "https://schema.org", "@type": "Article", "headline": r["titel"], "description": r["kurz"],
                  "author": {"@type": "Organization", "name": NAME}, "publisher": {"@type": "Organization", "name": NAME},
                  "datePublished": date.today().isoformat(), "inLanguage": "de"}
        others = '<ul class="svc rg">' + "".join(f'<li><a href="/ratgeber/{o["slug"]}/"><span class="n">{o["min"]} Min.</span><span class="t">{o["titel"]}</span><span class="d">{o["kurz"]}</span><span class="a" aria-hidden="true">→</span></a></li>' for o in RATGEBER if o is not r) + "</ul>"
        body = f"""<section class="hero" style="padding-bottom:20px"><div class="wrap"><p class="kicker">Ratgeber · {r["min"]} Min. Lesezeit</p><h1 style="max-width:16em">{r["titel"]}</h1><p class="lead">{r["kurz"]}</p></div></section>
<section style="padding-top:0"><div class="wrap"><article class="prose">{r["body"]}</article></div></section>
<section><div class="wrap"><h2 class="h2s" style="margin-bottom:28px">Weiterlesen</h2>{others}</div></section>{cta()}"""
        write(p, r["titel"], r["kurz"], body, prio=0.6, schema=schema, crumbs=[("/", "Start"), ("/ratgeber/", "Ratgeber"), (p, r["titel"])])


def kontakt():
    opts = [("einschaetzung", "Kostenlose Ersteinschätzung"), ("website", "Neue Website"), ("seo", "Bei Google gefunden werden (SEO)"), ("ads", "Google Ads"),
            ("recruiting", "Mitarbeiter gewinnen (Recruiting-Paket)"), ("wachstum", "Wachstumsprogramm"), ("unklar", "Noch unklar")]
    sel = "".join(f'<option data-k="{k}">{t}</option>' for k, t in opts)
    body = f"""<section class="hero"><div class="wrap k-grid"><div class="k-intro"><p class="kicker">Kontakt</p><h1>Kostenlose <em>Ersteinschätzung.</em></h1><p class="lead">Schreiben Sie kurz, worum es geht. Wir melden uns innerhalb eines Werktags mit zwei Terminvorschlägen.</p></div>
<div class="k-more"><ol class="steps next"><li><h2>Sie schicken die Anfrage</h2><p>Zwei Minuten. Name und E-Mail reichen.</p></li><li><h2>Wir schauen vorab</h2><p>Ihre Website und Ihr Google-Profil.</p></li><li><h2>20 Minuten Gespräch</h2><p>Per Telefon oder Video. Sie erfahren, wo Anfragen verloren gehen, auch wenn wir danach nicht zusammenarbeiten.</p></li></ol>
<dl class="contact-alt"><div><dt>E-Mail</dt><dd><a href="mailto:{C['email']}">{C['email']}</a></dd></div><div><dt>Telefon</dt><dd>{PHONE}</dd></div><div><dt>Ansprechpartner</dt><dd>{PERSON}</dd></div></dl></div>
<div class="form-wrap k-form"><form id="anfrage" data-to="{C['email']}" {f'data-sb="{C["supabase_url"]}" data-key="{C["supabase_key"]}"' if C.get("supabase_url") else ""}>
<label>Ihr Name *<input name="name" required autocomplete="name"></label>
<label>E-Mail *<input name="email" type="email" required autocomplete="email"></label>
<label>Telefon (falls Sie einen Rückruf möchten)<input name="telefon" type="tel" autocomplete="tel"></label>
<label>Betrieb und Ort<input name="betrieb" autocomplete="organization" placeholder="z. B. Malerbetrieb in Kassel"></label>
<label>Worum geht es?<select name="thema">{sel}</select></label>
<label>Nachricht (optional)<textarea name="nachricht" rows="3" placeholder="Was soll in sechs Monaten anders sein?"></textarea></label>
<label class="check"><input type="checkbox" name="einwilligung" required> <span>Ich bin einverstanden, dass meine Angaben zur Bearbeitung der Anfrage verwendet werden. Mehr in der <a href="/datenschutz/">Datenschutzerklärung</a>.</span></label>
<label class="hp" aria-hidden="true">Website<input name="website" tabindex="-1" autocomplete="off"></label>
<button class="btn" type="submit">Ersteinschätzung anfordern</button><p class="form-msg" role="status">Kostenlos und unverbindlich. Antwort innerhalb eines Werktags.</p>
</form></div></div></section>"""
    write("/kontakt/", "Kostenlose Ersteinschätzung anfragen", "Kostenlose Ersteinschätzung zu Website, Google-Sichtbarkeit und Anzeigen für Ihren Betrieb. Antwort innerhalb eines Werktags.", body, prio=0.8, crumbs=[("/", "Start"), ("/kontakt/", "Kontakt")])
    write("/danke/", "Danke für Ihre Anfrage", "Ihre Anfrage ist vorbereitet.", f'<section class="hero"><div class="wrap prose"><h1>Danke!</h1><p class="lead">{"Ihre Anfrage ist bei uns angekommen." if C.get("supabase_url") else "Ihre Nachricht ist in Ihrem E-Mail-Programm vorbereitet. Bitte dort noch absenden."} Wir melden uns innerhalb eines Werktags. Hat sich kein E-Mail-Programm geöffnet? Schreiben Sie direkt an <a href="mailto:{C["email"]}">{C["email"]}</a>.</p><p><a class="btn" href="/beispiele/">In der Zwischenzeit: Beispiele ansehen</a></p></div></section>')


DS_SUPABASE = "<p>Wenn Sie uns per E-Mail oder über das Kontaktformular schreiben, verarbeiten wir Ihre Angaben (Name, Betrieb, E-Mail, Telefon, Thema, Nachricht die Seite, von der Sie das Formular abgeschickt haben, und – falls Sie über einen Link mit Kampagnen-Kennzeichnung gekommen sind – dessen Quelle, z. B. „google-ads“) zur Bearbeitung der Anfrage und zur Anbahnung eines Vertrags (Art. 6 Abs. 1 lit. b DSGVO). Die Angaben aus dem Formular werden in einer Datenbank bei Supabase Inc. gespeichert; die Daten liegen in einem Rechenzentrum in der EU. Mit Supabase besteht ein Auftragsverarbeitungsvertrag. Über neue Anfragen werden wir per Push-Nachricht (ntfy.sh) informiert; diese enthält nur Thema und Betrieb, keine Kontaktdaten. Wir löschen Anfragen, aus denen kein Auftrag entsteht, spätestens nach 12 Monaten; ansonsten gelten die gesetzlichen Aufbewahrungsfristen.</p>"
DS_MAIL = "<p>Wenn Sie uns per E-Mail oder über das Kontaktformular schreiben (das Formular öffnet Ihr E-Mail-Programm mit einer vorbereiteten Nachricht), verarbeiten wir Ihre Angaben zur Bearbeitung der Anfrage und zur Anbahnung eines Vertrags (Art. 6 Abs. 1 lit. b DSGVO). Wir löschen Anfragen, aus denen kein Auftrag entsteht, spätestens nach 12 Monaten; ansonsten gelten die gesetzlichen Aufbewahrungsfristen.</p>"


def ds_dienste():
    """Datenschutz-Abschnitte für zustimmungspflichtige Dienste – nur für die in config.json eingetragenen."""
    teile = []
    if "ga4" in T:
        teile.append("<h3>Google Analytics 4</h3><p>Mit Ihrer Einwilligung nutzen wir Google Analytics 4 der Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Irland. Google Analytics setzt Cookies und verarbeitet Nutzungsdaten (z. B. aufgerufene Seiten, Verweildauer, Geräte- und Browserinformationen, ungefährer Standort), damit wir sehen, welche Inhalte hilfreich sind und woher Besucher kommen. IP-Adressen werden von Google Analytics 4 nicht gespeichert. Eine Übermittlung in die USA ist möglich; Google ist unter dem EU-US Data Privacy Framework zertifiziert. Die Daten werden nach " + todo("SPEICHERDAUER AUS GA4-EINSTELLUNG, z. B. 14 MONATE") + " gelöscht. Rechtsgrundlage: Art. 6 Abs. 1 lit. a DSGVO, § 25 Abs. 1 TDDDG.</p>")
    if "google_ads" in T:
        teile.append("<h3>Google Ads Conversion-Messung</h3><p>Mit Ihrer Einwilligung messen wir mit Google Ads (Google Ireland Limited, Gordon House, Barrow Street, Dublin 4, Irland), ob Besucher nach dem Klick auf eine unserer Anzeigen eine Anfrage senden oder anrufen. Dazu wird ein Cookie mit einer Klick-Kennung gesetzt (höchstens 90 Tage). Senden Sie danach das Kontaktformular ab, speichern wir diese Klick-Kennung zusammen mit Ihrer Anfrage, um Google später mitteilen zu können, ob aus der Anzeige ein Auftrag entstanden ist. Wir erhalten von Google nur zusammengefasste Zahlen, keine Angaben zu einzelnen Personen. Eine Übermittlung in die USA ist möglich; Google ist unter dem EU-US Data Privacy Framework zertifiziert. Rechtsgrundlage: Art. 6 Abs. 1 lit. a DSGVO, § 25 Abs. 1 TDDDG.</p>")
    if "meta_pixel" in T:
        teile.append("<h3>Meta-Pixel</h3><p>Mit Ihrer Einwilligung nutzen wir das Meta-Pixel der Meta Platforms Ireland Limited, Merrion Road, Dublin 4, Irland, um zu messen, ob Anzeigen auf Facebook und Instagram zu Anfragen führen. Dabei werden Cookies gesetzt und Nutzungsdaten (z. B. aufgerufene Seiten, Geräteinformationen, IP-Adresse) an Meta übertragen, das sie auch eigenen Profilen zuordnen kann. Für die Erhebung und Übermittlung sind wir mit Meta gemeinsam verantwortlich (Art. 26 DSGVO, Vereinbarung: facebook.com/legal/controller_addendum). Eine Übermittlung in die USA ist möglich; Meta ist unter dem EU-US Data Privacy Framework zertifiziert. Rechtsgrundlage: Art. 6 Abs. 1 lit. a DSGVO, § 25 Abs. 1 TDDDG.</p>")
    return "".join(teile)


def rechtliches():
    DS_FORM = DS_SUPABASE if C.get("supabase_url") else DS_MAIL
    i = C["impressum"]
    zusatz = "".join(f"<h2>{t}</h2><p>{e(i[k])}</p>" for k, t in (("ustid", "Umsatzsteuer-Identifikationsnummer"), ("register", "Registereintrag")) if (i.get(k) or "").strip())
    imp = f"""<section class="hero"><div class="wrap prose"><h1>Impressum</h1>
<h2>Angaben gemäß § 5 DDG</h2><p>{ph(i["inhaber"])}<br>{NAME}<br>{ph(i["strasse"])}<br>{ph(i["ort"])}</p>
<h2>Kontakt</h2><p>Telefon: {ph(i["telefon"])}<br>E-Mail: <a href="mailto:{i["email"]}">{i["email"]}</a></p>
<h2>Umsatzsteuer</h2><p>{e(i["ust"])}</p>{zusatz}
<h2>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h2><p>{ph(i["inhaber"])}, Anschrift wie oben.</p>
<h2>Verbraucherstreitbeilegung</h2><p>Wir sind nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
<h2>Haftung für Inhalte und Links</h2><p>Wir erstellen die Inhalte dieser Seiten mit Sorgfalt, übernehmen aber keine Gewähr für Vollständigkeit und Aktualität. Für Inhalte verlinkter externer Seiten sind ausschließlich deren Betreiber verantwortlich.</p></div></section>"""
    write("/impressum/", "Impressum", "Impressum und Anbieterkennzeichnung.", imp, prio=0.2)

    grundsatz = ("Diese Website setzt ohne Ihre Einwilligung keine Cookies und lädt keine Dienste von Drittanbietern. Schriften werden lokal ausgeliefert. "
                 "Die in Abschnitt 7 genannten Messdienste laden wir nur, wenn Sie im Fenster „Ihre Datenschutz-Einstellungen“ zustimmen. Ihre Entscheidung speichern wir ausschließlich in Ihrem Browser (localStorage) für höchstens 12 Monate; das ist dafür unbedingt erforderlich (§ 25 Abs. 2 Nr. 2 TDDDG). "
                 "Sie können Ihre Einwilligung jederzeit mit Wirkung für die Zukunft über „Datenschutz-Einstellungen“ im Fußbereich widerrufen."
                 if EINW else
                 "Diese Website verwendet keine Cookies und keine Einbindungen von Drittanbietern. Schriften werden lokal ausgeliefert. Eine Einwilligung über ein Cookie-Banner ist daher nicht erforderlich.")
    i_ = C["impressum"]
    ds = f"""<section class="hero"><div class="wrap prose"><h1>Datenschutzerklärung</h1>
<h2>1. Verantwortlicher</h2><p>{ph(i_["inhaber"])}, {ph(i_["strasse"])}, {ph(i_["ort"])}, E-Mail: {i_["email"]}</p>
<h2>2. Grundsatz</h2><p>{grundsatz}</p>
<h2>2a. Anonyme Reichweitenmessung</h2><p>Um zu verstehen, welche Seiten hilfreich sind, zählen wir Seitenaufrufe und Klicks auf Kontakt-, Telefon- und E-Mail-Links. Gespeichert werden nur die aufgerufene Seite, die Art des Ereignisses (z. B. „Aufruf“ oder „Klick auf Kontakt“) und der Zeitpunkt. Kommen Sie über einen Link mit Kampagnen-Kennzeichnung (z. B. aus einer Anzeige), speichern wir zusätzlich nur die Quelle als Wort (z. B. „google-ads“) – nicht die Klick-Kennung. Wir setzen dafür keine Cookies, speichern nichts auf Ihrem Gerät, lesen keine Informationen aus Ihrem Gerät aus (z. B. Bildschirmgröße oder Herkunftsseite), speichern keine IP-Adressen und vergeben keine Kennungen – ein Rückschluss auf Ihre Person ist nicht möglich. Die Daten liegen bei Supabase Inc. in einem Rechenzentrum in der EU (Auftragsverarbeitungsvertrag besteht) und werden nach spätestens 25 Monaten gelöscht. Bei der Übertragung verarbeitet der Server technisch bedingt Ihre IP-Adresse, speichert sie aber nicht in unserer Datenbank. Rechtsgrundlage ist unser berechtigtes Interesse an einer bedarfsgerechten Gestaltung der Website (Art. 6 Abs. 1 lit. f DSGVO).</p>
<h2>3. Hosting</h2><p>Die Website wird bei Vercel Inc., 440 N Barranca Ave #4133, Covina, CA 91723, USA gehostet. Beim Aufruf verarbeitet Vercel technisch notwendige Daten (IP-Adresse, Zeitpunkt, aufgerufene Seite, Browserinformationen) zur Auslieferung und zur Abwehr von Angriffen. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO. Vercel ist unter dem EU-US Data Privacy Framework zertifiziert; zusätzlich besteht ein Auftragsverarbeitungsvertrag mit Standardvertragsklauseln.</p>
<h2>4. Kontaktaufnahme und Kontaktformular</h2>{DS_FORM}
<h2>5. Ihre Rechte</h2><p>Sie haben das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch (Art. 15–21 DSGVO) sowie das Recht auf Beschwerde bei einer Datenschutz-Aufsichtsbehörde. Eine erteilte Einwilligung können Sie jederzeit mit Wirkung für die Zukunft widerrufen (Art. 7 Abs. 3 DSGVO).</p>
<h2>6. Speicherung im Browser</h2><p>Wenn Sie zwischen hellem und dunklem Design wechseln, wird diese Einstellung ausschließlich in Ihrem Browser gespeichert (localStorage) und nicht an uns übertragen.</p>
{"<h2>7. Dienste mit Einwilligung</h2>" + ds_dienste() if EINW else ""}
<p>Stand: {date.today().strftime("%m/%Y")}</p></div></section>"""
    write("/datenschutz/", "Datenschutzerklärung", "Informationen zum Datenschutz auf dieser Website.", ds, prio=0.2)

    # AGB – Grundlage: Vertragsbausteine aus betrieb/handbuch.py. Vor Veröffentlichung anwaltlich prüfen lassen.
    agb = [
        ("Geltungsbereich", "Diese Bedingungen gelten für alle Verträge zwischen " + NAME + " (Inhaber: " + ph(i["inhaber"]) + ") und unseren Kunden. Wir arbeiten ausschließlich für Unternehmer im Sinne von § 14 BGB, nicht für Verbraucher. Abweichende Bedingungen des Kunden gelten nur, wenn wir ihnen ausdrücklich in Textform zustimmen."),
        ("Vertragsschluss und Leistungsumfang", "Der Vertrag kommt durch die Annahme unseres Angebots in Textform (z. B. per E-Mail) zustande. Der Umfang ergibt sich abschließend aus dem Angebot und der Leistungsbeschreibung. Zusätzliche Leistungen bieten wir vorab an und erbringen sie nur nach Freigabe."),
        ("Mitwirkung des Kunden", "Der Kunde stellt Inhalte, Fotos und Zugänge innerhalb von 7 Tagen nach Auftrag bereit und benennt eine Person für Freigaben. Verzögerungen verschieben den Zeitplan entsprechend. Der Kunde versichert, dass er an gelieferten Inhalten (Texte, Fotos, Logos) die nötigen Rechte hat, und stellt uns von Ansprüchen Dritter frei, die auf solchen Inhalten beruhen."),
        ("Abnahme", "Bei Websites und anderen einmaligen Leistungen sind zwei Korrekturrunden enthalten. Der Entwurf gilt als abgenommen, wenn der Kunde nicht innerhalb von 10 Tagen nach Vorlage begründete Mängel mitteilt; auf diese Folge weisen wir bei der Vorlage hin."),
        ("Preise und Zahlung", "Es gelten die Preise aus dem Angebot. " + e(i["ust"]) + " Einmalige Leistungen werden zu 50 % bei Auftrag und zu 50 % nach Abnahme des Entwurfs berechnet. Monatliche Leistungen werden " + todo("ABRECHNUNGSWEISE ERGÄNZEN, z. B. MONATLICH IM VORAUS PER SEPA-LASTSCHRIFT") + " berechnet. Rechnungen sind innerhalb von " + todo("ZAHLUNGSZIEL ERGÄNZEN, z. B. 14 TAGEN") + " ohne Abzug fällig."),
        ("Laufzeiten und Kündigung", "Pflege & Hosting: 12 Monate, Verlängerung um jeweils 12 Monate, wenn nicht spätestens 3 Monate vor Ablauf gekündigt wird. SEO: 6 Monate Mindestlaufzeit, danach monatlich kündbar. Recruiting-Paket: 3 Monate, danach monatlich kündbar. Google Ads: monatlich kündbar. Wachstumsprogramm: 12 Monate. Kündigungen bedürfen der Textform. Das Recht zur außerordentlichen Kündigung aus wichtigem Grund bleibt unberührt."),
        ("Werbebudgets und Konten", "Werbebudgets für Google, Meta o. Ä. zahlt der Kunde direkt an die jeweilige Plattform. Werbe-, Google- und Domain-Konten laufen auf den Namen des Kunden."),
        ("Keine Ergebnisgarantie", "Platzierungen, Anfragen oder Bewerbungen hängen von Dritten (Suchmaschinen, Plattformen, Markt, Wettbewerb) ab und werden nicht garantiert. Wir schulden die sorgfältige Erbringung der beschriebenen Leistungen."),
        ("Recruiting-Paket: Stellenwechsel und Bewerbungs-Garantie", "Die folgenden Regeln gelten für Recruiting Komplett, nicht für Recruiting Basis. Ist eine beworbene Stelle besetzt, kann der Kunde für die restliche Laufzeit auf eine andere offene Stelle wechseln. Für die neuen Werbemittel (Karriereseite, Anzeigen) berechnen wir 30 % der Einrichtungsgebühr. Gehen in den ersten " + str(REC_GARANTIE["wochen"]) + " Wochen der Kampagne weniger als " + REC_GARANTIE["bewerbungen"] + " Bewerbungen ein, entfällt die Betreuungsgebühr für den folgenden Monat. Voraussetzung ist, dass der Kunde das im Angebot vereinbarte Werbebudget vollständig eingesetzt, die Inhalte fristgerecht geliefert und Bewerber innerhalb von 48 Stunden kontaktiert hat. Ein Anspruch auf Einstellungen besteht nicht."),
        ("Nutzungsrechte", "Nach vollständiger Zahlung erhält der Kunde die zeitlich und räumlich unbeschränkten Nutzungsrechte an Website, Texten und Gestaltung, die wir für ihn erstellt haben. Bei Vertragsende übergeben wir alle Dateien. Fremde Bestandteile (z. B. Schriften, Bilddatenbanken, Programme) unterliegen den Lizenzen ihrer Anbieter."),
        ("Rechtstexte", "Vorlagen für Impressum, Datenschutzerklärung oder Einwilligungs-Fenster sind eine Arbeitshilfe. Eine Rechtsberatung erfolgt nicht; die Verantwortung für die rechtliche Richtigkeit der eigenen Website trägt der Kunde."),
        ("Datenschutz", "Soweit wir für den Kunden personenbezogene Daten verarbeiten (z. B. Formularanfragen, Hosting, Auswertungen), schließen die Parteien einen Auftragsverarbeitungsvertrag nach Art. 28 DSGVO."),
        ("Referenzen", "Wir nennen den Kunden nur mit seiner ausdrücklichen Zustimmung als Referenz oder zeigen seine Website als Beispiel."),
        ("Haftung", "Wir haften unbeschränkt bei Vorsatz und grober Fahrlässigkeit, bei Verletzung von Leben, Körper oder Gesundheit sowie nach dem Produkthaftungsgesetz. Bei leicht fahrlässiger Verletzung wesentlicher Vertragspflichten ist die Haftung auf den vertragstypischen, vorhersehbaren Schaden begrenzt; im Übrigen ist die Haftung für leichte Fahrlässigkeit ausgeschlossen. Für Ausfälle von Diensten Dritter (z. B. Hosting-Anbieter, Suchmaschinen, Werbeplattformen) haften wir nur, soweit wir sie zu vertreten haben."),
        ("Schlussbestimmungen", "Es gilt das Recht der Bundesrepublik Deutschland. Gerichtsstand ist, soweit gesetzlich zulässig, der Sitz von " + NAME + " (" + ph(i["ort"]) + "). Sollte eine Bestimmung unwirksam sein, bleibt der Vertrag im Übrigen wirksam."),
    ]
    body = (f'<section class="hero"><div class="wrap prose"><h1>Allgemeine Geschäftsbedingungen</h1><p>{todo("ENTWURF – VOR VERÖFFENTLICHUNG ANWALTLICH PRÜFEN LASSEN")}</p>'
            '<p class="lead">Für Verträge mit Unternehmern. Das Wichtigste: klare Leistungen, feste Laufzeiten, Ihre Website gehört Ihnen.</p>'
            + "".join(f"<h2>§ {n} {t}</h2><p>{x}</p>" for n, (t, x) in enumerate(agb, 1)) +
            f'<p>Stand: {date.today().strftime("%m/%Y")}</p></div></section>')
    write("/agb/", "Allgemeine Geschäftsbedingungen", "Allgemeine Geschäftsbedingungen von " + NAME + " für Unternehmer.", body, prio=0.2)
    write("/404.html", "Seite nicht gefunden", "Diese Seite gibt es nicht.", '<section class="hero"><div class="wrap prose"><p class="kicker">404</p><h1>Diese Seite gibt es nicht (mehr).</h1><p class="lead">Vielleicht hilft einer dieser Wege weiter:</p><p><a class="btn" href="/">Zur Startseite</a> <a class="btn ghost" href="/beispiele/">Beispiele</a></p></div></section>')


# Zustimmungspflichtige Dienste: nur Konfiguration und Messpunkte – geladen wird erst über einwilligung.js nach Zustimmung.
DIENSTE_JS = r"""/* Erzeugt von build.py aus config.json → tracking. Nicht von Hand ändern. */
(function () {
  var T = __T__, w = window, an = {};
  w.dataLayer = w.dataLayer || []; w.gtag = w.gtag || function () { w.dataLayer.push(arguments); };
  var g = 0;
  function google(id) {
    if (!g) { g = 1; var s = document.createElement("script"); s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(id); document.head.appendChild(s); gtag("js", new Date()); }
    setTimeout(function () { gtag("config", id); }, 0);            // erst nach dem Consent-Update von einwilligung.js
  }
  function fertig(id) { setTimeout(function () { an[id] = 1; if (location.pathname === "/danke/") melden("formular", id); }, 0); }
  // Messpunkte: formular (Danke-Seite), telefon, mail, cta
  function melden(art, nur) {
    function ok(id) { return an[id] && (!nur || nur === id); }
    if (ok("anzeigen")) { var l = art === "formular" ? T.ads_label_anfrage : art === "telefon" ? T.ads_label_anruf : ""; if (l) gtag("event", "conversion", { send_to: T.google_ads + "/" + l }); }
    if (ok("statistik")) { var n = { formular: "generate_lead", telefon: "anruf_klick", mail: "mail_klick", cta: "kontakt_klick" }[art]; if (n) gtag("event", n, { send_to: T.ga4 }); }
    if (ok("meta") && w.fbq) { if (art === "formular") fbq("track", "Lead"); else if (art === "telefon" || art === "mail") fbq("track", "Contact"); }
  }
  w.lwKonversion = function (art) { melden(art); };
  var D = [];
  if (T.ga4) D.push({ id: "statistik", name: "Google Analytics", zweck: "Zeigt uns, welche Seiten hilfreich sind und woher Besucher kommen.", anbieter: "Google Ireland Ltd.",
    gcm: ["analytics_storage"], laden: function () { google(T.ga4); fertig("statistik"); } });
  if (T.google_ads) D.push({ id: "anzeigen", name: "Google Ads Conversion-Messung", zweck: "Misst, welche Anzeigen zu Anfragen führen.", anbieter: "Google Ireland Ltd.",
    gcm: ["ad_storage", "ad_user_data", "ad_personalization"], laden: function () { google(T.google_ads); fertig("anzeigen"); } });
  if (T.meta_pixel) D.push({ id: "meta", name: "Meta-Pixel", zweck: "Misst, welche Anzeigen auf Facebook und Instagram zu Anfragen führen.", anbieter: "Meta Platforms Ireland Ltd.",
    laden: function () {
      !function (f, b, e, v, n, t, s) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
        if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = "2.0"; n.queue = []; t = b.createElement(e); t.async = !0; t.src = v;
        s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s); }(w, document, "script", "https://connect.facebook.net/en_US/fbevents.js");
      fbq("init", T.meta_pixel); fbq("track", "PageView"); fertig("meta");
    } });
  w.LW_DIENSTE = D;
})();
"""


def csp():
    """Content-Security-Policy; Google/Meta-Adressen nur, wenn die Dienste in config.json eingetragen sind."""
    sb = (" " + C["supabase_url"]) if C.get("supabase_url") else ""
    script, connect, img, frame = "", "", "", ""
    if "ga4" in T or "google_ads" in T:
        script += " https://www.googletagmanager.com"
        connect += " https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com https://www.google.com https://googleads.g.doubleclick.net https://*.doubleclick.net"
        img += " https://*.google-analytics.com https://*.googletagmanager.com https://www.google.com https://www.google.de https://googleads.g.doubleclick.net"
        frame += " https://*.doubleclick.net https://www.googletagmanager.com"
    if "meta_pixel" in T:
        script += " https://connect.facebook.net"; connect += " https://www.facebook.com https://connect.facebook.net"; img += " https://www.facebook.com"
    return (f"default-src 'self'; connect-src 'self'{sb}{connect}; img-src 'self' data: https://images.pexels.com{img}; style-src 'self' 'unsafe-inline'; "
            f"script-src 'self'{script}; font-src 'self'; {("frame-src 'self'" + frame + '; ') if frame else ''}form-action 'self' mailto:; base-uri 'self'; frame-ancestors 'self'")


HEADERS = {"X-Content-Type-Options": "nosniff", "Referrer-Policy": "strict-origin-when-cross-origin",
           "X-Frame-Options": "SAMEORIGIN", "Permissions-Policy": "camera=(), microphone=(), geolocation=(), interest-cohort=()",
           "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
           "Content-Security-Policy": csp()}


def intern():
    """Steuerzentrale (nur Admins, Supabase-Anmeldung) und Inhalte-Formular für Kunden – beide nicht in der Sitemap, noindex."""
    write("/intern/", "Steuerzentrale", "Interner Bereich.", '<section class="in-wrap"><div class="wrap" id="app"><noscript>Bitte JavaScript aktivieren.</noscript></div></section>',
          noindex=True, js="intern.js")
    feld = lambda n, l, typ="text", req=False, ph="": f'<label>{l}<input name="{n}" type="{typ}"{" required" if req else ""} placeholder="{e(ph)}"></label>'
    text = lambda n, l, ph="", rows=3: f'<label>{l}<textarea name="{n}" rows="{rows}" placeholder="{e(ph)}"></textarea></label>'
    form = f"""<form id="inhalte" class="in-form" hidden>
<fieldset><legend>1 · Ihr Betrieb</legend>{feld("betrieb", "Name des Betriebs", req=True)}{feld("adresse", "Adresse")}<div class="in-two">{feld("telefon", "Telefon", "tel")}{feld("email", "E-Mail für Anfragen", "email", True)}</div>
{text("oeffnungszeiten", "Öffnungszeiten", "z. B. Mo–Fr 7–17 Uhr, Notdienst 24/7")}{text("einzugsgebiet", "Einzugsgebiet", "Orte, die Sie anfahren bzw. aus denen Ihre Kunden kommen")}</fieldset>
<fieldset><legend>2 · Leistungen und Preise</legend>{text("leistungen", "Was bieten Sie an?", "Eine Leistung pro Zeile", 5)}{text("top3", "Welche drei Leistungen bringen das meiste Geld?", "", 3)}
{text("preise", "Preise oder Preisrahmen, die wir zeigen dürfen", "Leer lassen, wenn keine Preise gezeigt werden sollen")}</fieldset>
<fieldset><legend>3 · Was Sie auszeichnet</legend>{text("besonderheiten", "Was unterscheidet Sie von anderen?", "z. B. Meisterbetrieb seit 1987, Spezialisierung (bitte nur Belegbares)", 4)}
{text("team", "Team (Namen und Rollen, nur mit Einverständnis)", "", 3)}{feld("google_profil", "Link zu Ihrem Google-Profil", "url", ph="https://g.page/…")}
<label class="check"><input type="checkbox" name="bewertungen_zitieren" value="ja"> <span>Wir dürfen Google-Bewertungen auf der Website zitieren.</span></label></fieldset>
<fieldset><legend>4 · Termine und Buchung</legend><label>Wie sollen Kunden Termine bekommen?<select name="buchung_art"><option value="">Bitte wählen</option>
<option value="programm">Wir haben schon ein Buchungsprogramm (z. B. Salon-, Kassen- oder Praxissoftware, Treatwell, Microsoft Bookings)</option>
<option value="neu">Wir möchten Online-Buchung, haben aber noch kein Programm</option><option value="rueckruf">Lieber Rückruf statt Online-Buchung</option>
<option value="keine">Keine Termine, nur Anfragen</option></select></label>
<div class="in-two">{feld("buchung_programm", "Welches Programm?", ph="z. B. Treatwell, Shore, Microsoft Bookings")}{feld("buchung_link", "Link zu Ihrer Buchungsseite", "url", ph="https://…")}</div>
{text("buchung_kalender", "In welchem Kalender sollen die Termine landen?", "z. B. Google-Kalender, Outlook, Kalender in der Praxissoftware")}
{text("buchung_leistungen", "Welche Leistungen sollen online buchbar sein? Wie lange dauern sie?", "z. B. Herrenschnitt 30 Min., Erstgespräch 20 Min.")}</fieldset>
<fieldset><legend>5 · Fotos und Logo</legend><p class="in-muted">15–30 Fotos sind ideal: Team, Arbeiten, Räume, Fahrzeuge. Logo gern als SVG oder PDF. Höchstens 15 MB pro Datei.</p>
<label class="btn ghost in-file">Dateien auswählen<input id="in-upload" type="file" multiple accept="image/jpeg,image/png,image/webp,image/heic,image/svg+xml,application/pdf"></label><ul id="in-dateien" class="in-list"></ul>
{text("farben", "Farben oder Wünsche zur Gestaltung", "z. B. Firmenfarbe Dunkelblau, Websites, die Ihnen gefallen")}</fieldset>
<fieldset><legend>6 · Zugänge und Freigabe</legend>{feld("domain", "Ihre Domain (falls vorhanden)", ph="betrieb.de")}{feld("domain_anbieter", "Bei welchem Anbieter liegt die Domain?", ph="z. B. IONOS, Strato")}
{feld("alte_website", "Bisherige Website", "url")}{text("stellen", "Nur bei Recruiting: offene Stellen, Gehaltsrahmen, Arbeitszeiten, Vorteile")}
{feld("ansprechpartner", "Wer gibt Inhalte frei und ist Ansprechpartner?", req=True)}</fieldset>
<label class="check"><input type="checkbox" name="bestaetigung" value="ja" required> <span>Die Angaben stimmen, und wir haben die Rechte an den hochgeladenen Fotos.</span></label>
<div class="in-row"><button class="btn">Angaben abschicken</button><span class="in-muted">Alles wird automatisch zwischengespeichert.</span></div></form>"""
    write("/inhalte/", "Ihre Inhalte für die Website", "Inhalte-Formular für Kunden.",
          f'<section class="in-wrap"><div class="wrap narrow"><p class="kicker">Inhalte-Formular</p><h1>Ihre Inhalte für die neue Website</h1><p id="in-info" class="lead">Lädt …</p><p id="in-status" role="status"></p>{form}</div></section>',
          noindex=True, js="inhalte.js")


def extras():
    shutil.copytree(ROOT / "static", DIST, dirs_exist_ok=True)
    vorschauen = sorted((ROOT / "vorschauen").glob("*/kunde.json"))  # V3: KI-Vorschauen für Interessenten (noindex, nicht in der Sitemap)
    if vorschauen:
        import sys; sys.path.insert(0, str(ROOT / "sites")); import generator
        for k in vorschauen:
            out, _ = generator.bauen(k.parent, vorschau=True)
            shutil.copytree(out, DIST / "v" / k.parent.name, dirs_exist_ok=True)
    (DIST / "favicon.svg").write_text(FAVICON)
    if EINW:
        shutil.copy(ROOT / "betrieb" / "bausteine" / "einwilligung.js", DIST / "einwilligung.js")
        (DIST / "dienste.js").write_text(DIENSTE_JS.replace("__T__", json.dumps({k: v for k, v in T.items() if k in ("ga4", "google_ads", "ads_label_anfrage", "ads_label_anruf", "meta_pixel")})))
    robots = "User-agent: *\nDisallow: /\n" if C["preview"] else f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n"
    (DIST / "robots.txt").write_text(robots)
    today = date.today().isoformat()
    urls = "".join(f"<url><loc>{DOMAIN}{p}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>" for p, pr in PAGES)
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    h = dict(HEADERS)
    if C["preview"]:
        h["X-Robots-Tag"] = "noindex, nofollow"
    (DIST / "_headers").write_text("/*\n" + "".join(f"  {k}: {v}\n" for k, v in h.items()))
    vercel = {"cleanUrls": True, "trailingSlash": True,
              "headers": [{"source": "/(.*)", "headers": [{"key": k, "value": v} for k, v in h.items()]},
                          {"source": "/fonts/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
                          {"source": "/bilder/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},  # Name = Pexels-ID + Breite, ändert sich nie
                          {"source": "/vorschau-bilder/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=86400, stale-while-revalidate=604800"}]}]}
    (DIST / "vercel.json").write_text(json.dumps(vercel, indent=2))


if __name__ == "__main__":
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir()
    for f in (startseite, leistungen, branchen, beispiele, preise, ablauf, faq_page, ratgeber, kontakt, rechtliches, vorschauseiten, intern):
        f()
    extras()
    n = len(list(DIST.rglob("*.html")))
    print(f"{n} Seiten gebaut → {DIST}")
