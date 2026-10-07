#!/usr/bin/env python3
"""Baut die statische Website nach dist/. Aufruf: python3 build.py"""
import json, shutil, html
from pathlib import Path
from datetime import date

from content import PREISE, eur, LEISTUNGEN, BRANCHEN, BEISPIELE, KAPITEL, RATGEBER, FAQ
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

NAV = [("/leistungen/", "Leistungen"), ("/branchen/", "Branchen"), ("/beispiele/", "Beispiele"),
       ("/preise/", "Preise"), ("/ratgeber/", "Ratgeber")]


def layout(path, title, desc, body, schema=None, crumbs=None):
    nav = "".join(f'<a href="{h}"{" aria-current=page" if path.startswith(h) else ""}>{t}</a>' for h, t in NAV)
    robots = '<meta name="robots" content="noindex,nofollow">' if C["preview"] else '<meta name="robots" content="index,follow">'
    ld = [{"@context": "https://schema.org", "@type": "ProfessionalService", "name": NAME, "url": DOMAIN + "/",
           "email": C["email"], "areaServed": "DE", "description": C["tagline"]}]
    if crumbs:
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": DOMAIN + u} for i, (u, n) in enumerate(crumbs)]})
    if schema:
        ld.append(schema)
    crumb_html = ""
    if crumbs and len(crumbs) > 1:
        crumb_html = '<div class="wrap"><nav class="crumbs" aria-label="Brotkrumen">' + " / ".join(
            f'<a href="{u}">{e(n)}</a>' if i < len(crumbs) - 1 else e(n) for i, (u, n) in enumerate(crumbs)) + "</nav></div>"
    full_title = title if NAME in title else f"{title} | {NAME}"
    bar = '<div class="preview-bar">Vorschau – diese Seite ist noch nicht öffentlich.</div>' if C["preview"] else ""
    return f"""<!doctype html>
<html lang="de"{f' data-sb="{C["supabase_url"]}" data-key="{C["supabase_key"]}"' if C.get("supabase_url") else ""}><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(full_title)}</title><meta name="description" content="{e(desc)}">{robots}
<link rel="canonical" href="{DOMAIN}{path}"><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta property="og:title" content="{e(full_title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="{DOMAIN}{path}"><meta property="og:locale" content="de_DE">
<meta name="theme-color" content="#f2f0eb"><link rel="preload" href="/fonts/intertight.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/style.css">
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
</div><div class="ft-mark" aria-hidden="true">{NAME}<span>.</span></div><div class="legal"><span>© {date.today().year} {NAME}</span><span><a href="/impressum/" style="display:inline">Impressum</a> · <a href="/datenschutz/" style="display:inline">Datenschutz</a></span></div></div></footer>
<script src="/main.js" defer></script></body></html>"""


def write(path, title, desc, body, prio=0.6, **kw):
    out = DIST / path.strip("/") / "index.html" if path != "/404.html" else DIST / "404.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(layout(path, title, desc, body, **kw), encoding="utf-8")
    if path not in ("/404.html", "/danke/"):
        PAGES.append((path, prio))


def cta(titel="Wo verlieren Sie heute Anfragen?", text="In 20 Minuten sehen wir uns Ihre Website, Ihr Google-Profil und drei Mitbewerber an. Sie bekommen eine ehrliche Einschätzung – auch wenn wir danach nicht zusammenarbeiten.", btn="Kostenlose Ersteinschätzung erhalten", href=EINSCH):
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
        hit = next(BILDCACHE.glob(f"{pid}.*"), None)
        if not hit:
            url = f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&fm=webp&w=1400"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Lotwerk-Build)"})
                with urllib.request.urlopen(req, timeout=20) as r:
                    typ, data = r.headers.get("Content-Type", ""), r.read()
                if typ.startswith("image/") and len(data) > 5000:
                    hit = BILDCACHE / f"{pid}.{'webp' if 'webp' in typ else 'jpg'}"
                    hit.write_bytes(data)
            except Exception:
                hit = None
        if hit:
            shutil.copy(hit, DIST / "bilder" / hit.name)
            vorschau.FOTO[pid] = hit.name
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
    ("1", "Bedarf", "Das Dach tropft, der Pony ist zu lang, der Vater braucht Pflege.", "Noch keine Entscheidung – aber ab jetzt wird gesucht.", ""),
    ("2", "Suche bei Google, Maps &amp; KI", "„Dachdecker in der Nähe“ bei Google – oder „Welcher Friseur in Musterstadt ist gut?“ bei ChatGPT. Fast immer auf dem Handy.", "Wer hier nicht oben steht oder von der KI nicht genannt wird, wird nicht gesehen.", "google"),
    ("3", "Vergleich", "Drei Anbieter, Sterne, Fotos, erste Eindrücke. Dauer: wenige Minuten.", "Bewertungen und ein gepflegtes Profil entscheiden, wer angeklickt wird.", ""),
    ("4", "Die Website", "Was kostet es? Wie läuft es ab? Wer sind die Menschen? Kann ich sofort anfragen?", "Hier fällt die Entscheidung – oder der Kunde geht zurück zur Suche.", "web"),
    ("5", "Anfrage &amp; Wiederkommen", "Termin, Rückruf, Fotos schicken. Danach: Bewertung, Empfehlung, Stammkunde.", "Ein einfacher nächster Schritt und Erinnerungen machen aus Kunden Stammkunden.", ""),
]


def customer_journey():
    stufen = "".join(f'<li class="cj-step{" hl" if hl else ""}"><span class="cj-n">{int(n):02d}{"<span class=cj-tag>· " + ("Sichtbarkeit" if hl == "google" else "Überzeugung") + "</span>" if hl else ""}</span><h3>{t}</h3><p>{tut}</p><p class="cj-key">{key}</p></li>' for n, t, tut, key, hl in CJ_STUFEN)
    return f'''<section class="cj" id="customer-journey"><div class="wrap">
<div class="sec-head"><span class="idx"><b>(01)</b> Kundenweg</span><h2>Bevor jemand anruft, hat er sich <em>längst entschieden.</em></h2>
<p>Gesucht, verglichen, Ihre Website angesehen – meist in wenigen Minuten, meist auf dem Handy. Zwei Stellen entscheiden: ob man Sie bei Google und in KI-Antworten findet, und ob Ihre Website dann überzeugt.</p></div>
<ol class="cj-line">{stufen}</ol>
<div class="split-row" style="margin-top:clamp(56px,7vw,96px);border-top:1px solid var(--line)"><div><p class="kicker">Sichtbarkeit</p><h3>Seite 2 ist <em class="serif">unsichtbar.</em></h3>
<p>Bei lokalen Suchen zeigt Google zuerst eine Karte mit drei Betrieben. Wer dort und in den ersten Treffern steht, bekommt den Großteil der Anfragen. Deshalb arbeiten wir an Google-Profil, Bewertungen und einer Seite für jede Leistung und jeden Ort.</p><a class="more" href="/leistungen/seo/">Wie wir Sie nach oben bringen</a></div>
<div class="serp" aria-hidden="true"><div class="serp-q">dachdecker in der nähe</div><div class="serp-map"><i style="left:22%;top:40%"></i><i class="me" style="left:52%;top:55%"></i><i style="left:74%;top:30%"></i></div>
<div class="serp-r me"><b>Ihr Betrieb</b><span class="st">★★★★★ 4,9 (126)</span><span>Geöffnet · Anrufen · Website · Route</span></div>
<div class="serp-r"><b>Mitbewerber A</b><span class="st">★★★★☆ 4,3 (41)</span></div><div class="serp-r"><b>Mitbewerber B</b><span class="st">★★★★☆ 4,1 (18)</span></div>
<div class="serp-more">Seite 2 – hier sucht fast niemand mehr.</div></div></div>
<div class="facts"><div><b>27,6 %<sup>1</sup></b><span>aller Klicks gehen an das erste Suchergebnis</span></div><div><b>0,63 %<sup>1</sup></b><span>klicken überhaupt auf Seite 2</span></div><div><b>93 %<sup>3</sup></b><span>lesen Bewertungen, bevor sie einen Betrieb wählen</span></div><div><b>+32 %<sup>4</sup></b><span>mehr Absprünge, wenn die Seite 3 statt 1 Sekunde lädt</span></div></div>
<div class="split-row"><div><p class="kicker">Neu: Suche mit KI</p><h3>Immer öfter fragt der Kunde nicht Google, <em class="serif">sondern ChatGPT.</em></h3>
<p>Die Hälfte der Deutschen nutzt zumindest manchmal einen KI-Chat statt der klassischen Suche.<sup>5</sup> ChatGPT, Gemini und Googles KI-Übersicht nennen meist nur zwei, drei Betriebe – und stützen sich auf dieselben Signale: gepflegtes Profil, gute Bewertungen und eine Website, die Leistungen, Orte und Preise klar beschreibt.</p><a class="more" href="/leistungen/seo/">Sichtbar bei Google und KI</a></div>
<div class="ai-chat" aria-hidden="true"><div class="ai-q">Welcher Dachdecker in Musterstadt ist zuverlässig und macht auch Photovoltaik?</div>
<div class="ai-a"><span class="ai-l">KI-Assistent</span><p>Empfehlenswert sind zum Beispiel:</p><ol><li class="me"><b>Ihr Betrieb</b> – Meisterbetrieb, 4,9 Sterne aus 126 Bewertungen, Dach und PV aus einer Hand, Festpreis-Angebot in 5 Tagen.</li><li><b>Mitbewerber A</b> – 4,3 Sterne, vor allem Reparaturen.</li></ol><span class="ai-src">Quellen: Google-Profil · ihr-betrieb.de · Bewertungen</span></div></div></div>
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
    tl = [("Tag 1", "Ersteinschätzung", "20 Minuten per Telefon oder Video. Wir sagen ehrlich, ob wir helfen können.", "Kostenlos und unverbindlich"),
          ("Tag 3", "Angebot", "Ziel, Umfang und Zeitplan auf einer Seite.", "Festpreis statt Stundenzettel"),
          ("Tag 10", "Entwurf", "Die Startseite live im Browser. Sie testen auf Ihrem Handy und geben Feedback.", "Zweite Rate erst nach Ihrer Freigabe"),
          ("Tag 21", "Start", "Website online, Google-Profil überarbeitet, Messung aktiv.", "Website, Domain und Zugänge gehören Ihnen"),
          ("Jeden Monat", "Pflege & Bericht", f"Updates, Sicherheit und kleine Änderungen laufen im Hintergrund. Ein Ansprechpartner: {PERSON}.", "Bericht in Anrufen und Anfragen")]
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
<section><div class="wrap"><div class="sec-head"><span class="idx"><b>(04)</b> So arbeiten wir</span><h2>In drei Wochen online – <em>und das ist Ihnen sicher.</em></h2><p>Ihr Aufwand: etwa zwei bis drei Stunden im ersten Monat, danach rund 30 Minuten im Monat.</p></div>
<ol class="tl tl5">{tlh}</ol>
<div class="proof"><div class="proof-box"><p class="kicker">Prüfen Sie uns selbst</p><p>Diese Website ist so gebaut, wie wir Ihre bauen. Messen Sie die Ladezeit mit dem kostenlosen Werkzeug von Google.</p><a class="more" href="https://pagespeed.web.dev/analysis?url={DOMAIN}/" rel="noopener" target="_blank">Mit Google PageSpeed testen ↗</a></div>
<div class="proof-box ph"><p class="kicker">Kundenstimmen</p><p>{todo("ECHTE GOOGLE-BEWERTUNGEN EINBINDEN")}</p><p class="small">Zwei bis drei Bewertungen mit Vorname, Ort und Sternen, verlinkt auf das Google-Profil.</p></div>
<div class="proof-box ph"><p class="kicker">Fallstudie</p><p>{todo("ERSTES KUNDENPROJEKT EINBINDEN")}</p><p class="small">Vorher/Nachher und Anfragen nach drei Monaten – nur mit Freigabe des Kunden.</p></div></div>
{faq_mini(fq)}</div></section>
{cta()}"""
    write("/", f"{NAME} – Websites & Google-Sichtbarkeit für lokale Betriebe", "Websites, lokale SEO und Google Ads für Handwerk, Kanzleien, Pflegedienste und Praxen in ganz Deutschland. Festpreis, erster Entwurf nach 7 Tagen.", body, prio=1.0, crumbs=[("/", "Start")])


def leistungen():
    lst = sorted(LEISTUNGEN, key=lambda l: SVC_ORDER.index(l["slug"]))
    write("/leistungen/", "Leistungen: Websites, SEO, Google Ads, Recruiting", "Websites ab 1.490 €, lokale SEO ab 390 €/Monat, Google Ads ab 290 €/Monat und Recruiting für lokale Betriebe – alles zum Festpreis.",
          f'<section class="hero"><div class="wrap"><p class="kicker">Leistungen</p><h1>Fünf Leistungen für <em>mehr Anfragen.</em></h1><p class="lead">Mehr passende Anfragen – und die Fachkräfte, um sie abzuarbeiten. Jede Leistung funktioniert allein. Zusammen wirken sie stärker.</p></div></section><section style="padding-top:0;border:0"><div class="wrap">{svc_liste(lst)}</div></section>{cta()}',
          prio=0.9, crumbs=[("/", "Start"), ("/leistungen/", "Leistungen")])
    for l in LEISTUNGEN:
        p = f"/leistungen/{l['slug']}/"
        steps = "".join(f"<li><h3>{a}</h3><p>{b}</p></li>" for a, b in l["ablauf"])
        others = [o for o in sorted(LEISTUNGEN, key=lambda x: SVC_ORDER.index(x["slug"])) if o is not l]
        glance = "".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in l["eckdaten"])
        href = f"/kontakt/?thema={l['k']}"
        body = f"""<section class="hero"><div class="wrap grid"><div><p class="kicker">{l["titel"]}</p><h1>{l["h1"]}</h1><p class="lead">{l["lead"]}</p><div class="actions"><a class="btn" href="{href}">{l["cta"]} <span class="ar">→</span></a><a class="link" href="/preise/">Alle Preise</a></div></div>
<aside class="glance" aria-label="Auf einen Blick"><p class="kicker">Auf einen Blick</p><dl>{glance}</dl></aside></div></section>
<section><div class="wrap grid2"><div><h2 class="h2s">Was Sie bekommen</h2>{ticks(l["punkte"])}</div><div><h2 class="h2s">So gehen wir vor</h2><ol class="steps">{steps}</ol></div></div></section>
<section><div class="wrap">{faq_mini(l["faq"])}</div></section>
<section><div class="wrap"><h2 class="h2s" style="margin-bottom:28px">Passt gut dazu</h2>{svc_liste(others)}</div></section>{cta(f"{l['titel']} für Ihren Betrieb?", "Wir sehen uns Ihre Ausgangslage an und sagen Ihnen, ob sich das für Sie lohnt – kostenlos und ehrlich.", l["cta"], href)}"""
        write(p, l["seo"], l["kurz"], body, prio=0.8, schema=faq_schema(l["faq"]),
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
          f'<section class="hero"><div class="wrap"><p class="kicker">Beispiele</p><h1>Sieben Betriebe, <em>sieben Kundenwege.</em></h1><p class="lead">Jedes Beispiel erzählt, wie ein Kunde sucht, vergleicht und sich entscheidet – und was wir an jeder Stelle bauen. Mit echtem Paketpreis – und einer vollständigen Vorschau-Website zum Durchklicken.</p><p class="note">Die Betriebe sind erfundene Beispiele, damit Sie Ablauf und Kosten realistisch einschätzen können. Preise entsprechen unserer aktuellen Preisliste.</p></div></section><section style="padding-top:0"><div class="wrap gallery">{cards}</div></section>{cta()}',
          prio=0.9, crumbs=[("/", "Start"), ("/beispiele/", "Beispiele")])
    for b in BEISPIELE:
        p = f"/beispiele/{b['slug']}/"
        stages = "".join(f'<li class="stage"><span class="dot">{i+1}</span><h3>{t}</h3><div class="split"><div class="they"><span class="lbl">Der Kunde</span>{k}</div><div class="we"><span class="lbl">Was wir bauen</span>{w}</div></div></li>' for i, (t, k, w) in enumerate(b["kundenweg"]))
        rows = "".join(f'<tr><td>{n}</td><td class="r">{eur(v)}</td></tr>' for n, v in b["paket"])
        hinweis = f'<p class="note" style="margin-top:14px">{b["paket_hinweis"]}</p>' if b.get("paket_hinweis") else ""
        kap = [b["ausgang"], f'<p class="quote" style="font-size:1.3rem">{b["ziel"]}</p>',
               f'<p>So findet ein typischer Kunde zu {b["name"]} – und das haben wir an jeder Station gebaut:</p><ol class="journey">{stages}</ol>',
               ticks(b["umsetzung"]) + f'<p><strong>Aufgabe des Betriebs:</strong> {b["aufgabe"]}</p>',
               f'<div class="tablewrap"><table><thead><tr><th>Baustein</th><th class="r">Betrag</th></tr></thead><tbody>{rows}</tbody><tfoot><tr><td>Erstes Jahr gesamt</td><td class="r">{eur(paket_summe(b))}</td></tr></tfoot></table></div>{hinweis}',
               f"<p>{b['erwartung']}</p>"]
        chapters = "".join(f'<div class="chapter" id="kapitel-{i+1}"><div><div class="n">{i+1:02d}</div><span class="kicker" style="margin-top:8px">{KAPITEL[i]}</span></div><div>{c if c.startswith("<") else "<p>"+c+"</p>"}</div></div>' for i, c in enumerate(kap))
        nxt = BEISPIELE[(BEISPIELE.index(b) + 1) % len(BEISPIELE)]
        body = f"""<section class="hero"><div class="wrap grid"><div><p class="kicker">Beispiel · {b["branche"]} · erfundener Betrieb</p><h1>{b["name"]}</h1><p class="lead">{b["teaser"]}</p><p><span class="pill">{b["ort"]}</span> <span class="pill">{eur(paket_summe(b))} im ersten Jahr</span></p><div class="actions"><a class="btn" href="/vorschau/{b["slug"]}/">Beispiel-Website öffnen <span class="ar">→</span></a><a class="link" href="#kapitel-3">Zum Kundenweg</a></div></div><div class="showcase small"><a href="/vorschau/{b["slug"]}/" class="sc-desk">{frame(b["slug"], eager=True)}</a><a href="/vorschau/{b["slug"]}/" class="sc-phone">{frame(b["slug"], mobil=True, eager=True)}</a></div></div></section>
<section style="padding-top:0"><div class="wrap">{chapters}<p class="note">Erfundenes Beispiel zur Veranschaulichung. Ergebnisse hängen von Markt, Wettbewerb und Mitarbeit ab und sind nicht garantiert.</p><p style="margin-top:22px"><a class="more" href="/beispiele/{nxt["slug"]}/">Nächstes Beispiel: {nxt["name"]} ({nxt["branche"]}) →</a></p></div></section>{cta("Wie sieht Ihr Kundenweg aus?", "Im Erstgespräch skizzieren wir ihn gemeinsam – kostenlos.")}"""
        write(p, f"Beispiel {b['branche']}: {b['name']}", b["teaser"], body, prio=0.7,
              crumbs=[("/", "Start"), ("/beispiele/", "Beispiele"), (p, b["branche"])])


def preise():
    P = PREISE
    def box(t, amt, per, items, feat=False, note="", k="website"):
        return f'<div class="card price{" feat" if feat else ""}">{"<span class=pill>Beliebt</span>" if feat else ""}<h2 class="h3" style="margin-top:8px">{t}</h2><div class="amt">{amt}</div><div class="per">{per}</div>{ticks(items)}{f"<p class=note>{note}</p>" if note else ""}<a class="btn{"" if feat else " ghost"}" href="/kontakt/?thema={k}" style="margin-top:18px">Angebot anfragen</a></div>'
    web = box("Website Start", eur(P["web_start"]), f"einmalig · Pflege {P['pflege_start']} €/Monat (12 Monate)", ["Bis zu 5 Seiten", "Texte und Struktur inklusive", "Google-Unternehmensprofil eingerichtet", "Kontakt- oder Buchungsformular", "Fertig in 2–3 Wochen"]) + \
          box("Website Wachstum", eur(P["web_wachstum"]), f"einmalig · Pflege {P['pflege_wachstum']} €/Monat (12 Monate)", ["Bis zu 15 Seiten", "Eigene Seiten je Leistung und Ort", "Karriere- oder Bewerbungsbereich", "Ratgeber-Bereich", "Anruf- und Formularmessung"], feat=True) + \
          box("Wachstumsprogramm", eur(P["programm"]), f"pro Monat · 12 Monate · {eur(P['prog_setup'])} Einrichtung", ["Website Wachstum inklusive", "SEO Plus inklusive", "Google-Ads-Betreuung inklusive", "Monatsgespräch und Bericht", "Gemeinsames, messbares Ziel"], k="wachstum", note=f"Einzeln im ersten Jahr: {eur(P['web_wachstum'] + 12*P['pflege_wachstum'] + 12*P['seo_plus'] + P['ads_setup'] + 12*P['ads'])}")
    monat = [("SEO Lokal", P["seo_lokal"], "Profil, Verzeichnisse, 1 neue Seite pro Monat, Bericht. 6 Monate Mindestlaufzeit."),
             ("SEO Plus", P["seo_plus"], "Wie Lokal, plus 2–3 Inhalte pro Monat, Bewertungsprozess, Wettbewerbsanalyse."),
             ("Google-Ads-Betreuung", P["ads"], f"Einrichtung {P['ads_setup']} € einmalig. Monatlich kündbar, Budget separat."),
             ("Recruiting-Paket", P["rec"], f"Karriereseite, Bewerbung in 60 Sekunden, Anzeigen im Umkreis. Einrichtung {eur(P['rec_setup'])} einmalig, Budget separat."),
             ("Pflege & Hosting Start", P["pflege_start"], "Hosting, Updates, Sicherheit, kleine Änderungen. 12 Monate Laufzeit, verlängert sich jährlich."),
             ("Pflege & Hosting Wachstum", P["pflege_wachstum"], "Wie Start, plus 1 Stunde Änderungen pro Monat. 12 Monate Laufzeit, verlängert sich jährlich.")]
    rows = "".join(f"<tr><td><strong>{n}</strong></td><td>{d}</td><td class='r'>{eur(v)}/Monat</td></tr>" for n, v, d in monat)
    faq = [("Sind die Preise Endpreise?", "Ja. " + C["impressum"]["ust"]), ("Gibt es versteckte Kosten?", "Nein. Werbebudget für Anzeigen zahlen Sie direkt an Google oder Meta. Fremdkosten wie spezielle Buchungstools besprechen wir vorher."), ("Kann ich klein anfangen?", "Ja. Viele starten mit einer Website Start und ergänzen später SEO oder Anzeigen.")]
    body = f"""<section class="hero"><div class="wrap"><p class="kicker">Preise</p><h1>Feste Preise. <em>Vorab.</em></h1><p class="lead">Sie wissen vorher, was es kostet. Ohne Stundenzettel, ohne Prozente vom Werbebudget.</p></div></section>
<section style="padding-top:0"><div class="wrap grid3">{web}</div></section>
<section style="padding-top:0"><div class="wrap"><div class="feature-row"><div><p class="kicker">Recruiting</p><h2 class="h2s">Recruiting-Paket: Fachkräfte statt Stellenportale</h2><p>Karriereseite mit echten Einblicken, Bewerbung in 60 Sekunden ohne Lebenslauf und Anzeigen im Umkreis – für Pflege, Handwerk, Praxen und Kanzleien.</p><a class="more" href="/leistungen/recruiting/">Mehr zum Recruiting-Paket →</a></div><div><div class="amt" style="font:600 2.2rem var(--serif)">{eur(P["rec"])}<small style="font:500 .9rem var(--sans);color:var(--ink-2)"> / Monat</small></div><p style="color:var(--ink-2)">Einrichtung {eur(P["rec_setup"])} einmalig · Werbebudget separat · nach 3 Monaten monatlich kündbar</p><a class="btn" href="/kontakt/?thema=recruiting">Recruiting-Paket besprechen <span class="ar">→</span></a></div></div></div></section>
<section><div class="wrap"><h2 class="h2s">Laufende Leistungen</h2><div class="tablewrap"><table><thead><tr><th>Leistung</th><th>Umfang</th><th class="r">Preis</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>
<section><div class="wrap"><div class="grid2 faq-mini"><div><h2 class="h2s">Fragen zu den Preisen</h2><p>Durchgerechnete Pakete finden Sie in den <a href="/beispiele/">Beispielen</a>.</p></div><div>{faq_html(faq)}</div></div></div></section>{cta("Welches Paket passt zu Ihnen?", "Wir empfehlen nur, was sich für Ihren Betrieb rechnet. Die Ersteinschätzung ist kostenlos.")}"""
    write("/preise/", "Preise für Website, SEO und Google Ads", "Website ab 1.490 €, SEO ab 390 €/Monat, Google Ads ab 290 €/Monat, Recruiting-Paket 790 €/Monat, Wachstumsprogramm 1.190 €/Monat plus Einrichtung. Feste Preise ohne Überraschungen.", body, prio=0.9, schema=faq_schema(faq), crumbs=[("/", "Start"), ("/preise/", "Preise")])


def ablauf():
    steps = [("Erstgespräch (20 Min.)", "Per Telefon oder Video. Wir fragen nach Ihren Zielen, Ihren Kunden und dem, was bisher nicht funktioniert hat."),
             ("Kurzanalyse", "Wir sehen uns Website, Google-Profil und Ihre drei stärksten Mitbewerber an. Sie bekommen die wichtigsten Punkte schriftlich."),
             ("Angebot mit Festpreis", "Binnen zwei Werktagen. Mit Ziel, Umfang, Zeitplan und Preis."),
             ("Start-Workshop (60 Min.)", "Wir gehen den Kundenweg gemeinsam durch und sammeln alles, was wir für Texte brauchen."),
             ("Umsetzung", "Sie sehen nach einer Woche den ersten Entwurf im Browser. Feedback per E-Mail oder kurzem Call."),
             ("Freischaltung", "Website online, Messung aktiv, Profil und Kampagnen laufen."),
             ("Monatlich", "Bericht mit den Zahlen, die zählen: Anfragen, Anrufe, Kosten pro Anfrage. Einmal im Quartal planen wir die nächsten Schritte.")]
    body = f"""<section class="hero"><div class="wrap grid2"><div><p class="kicker">Ablauf</p><h1>So arbeiten wir <em>zusammen.</em></h1><p class="lead">Klare Schritte, wenig Aufwand für Sie. Rechnen Sie im ersten Monat mit zwei bis drei Stunden Ihrer Zeit – danach mit etwa 30 Minuten im Monat.</p></div><div><ol class="steps">{"".join(f"<li><h3>{a}</h3><p>{b}</p></li>" for a,b in steps)}</ol></div></div></section>
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
<div class="k-more"><ol class="steps next"><li><h2>Sie schicken die Anfrage</h2><p>Zwei Minuten. Name und E-Mail reichen.</p></li><li><h2>Wir schauen vorab</h2><p>Website, Google-Profil und drei Mitbewerber in Ihrer Region.</p></li><li><h2>20 Minuten Gespräch</h2><p>Per Telefon oder Video. Sie erfahren, wo Anfragen verloren gehen – auch wenn wir danach nicht zusammenarbeiten.</p></li></ol>
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
    write("/danke/", "Danke für Ihre Anfrage", "Ihre Anfrage ist vorbereitet.", f'<section class="hero"><div class="wrap prose"><h1>Danke!</h1><p class="lead">{"Ihre Anfrage ist bei uns angekommen." if C.get("supabase_url") else "Ihre Nachricht ist in Ihrem E-Mail-Programm vorbereitet – bitte dort noch absenden."} Wir melden uns innerhalb eines Werktags. Hat sich kein E-Mail-Programm geöffnet? Schreiben Sie direkt an <a href="mailto:{C["email"]}">{C["email"]}</a>.</p><p><a class="btn" href="/beispiele/">In der Zwischenzeit: Beispiele ansehen</a></p></div></section>')


DS_SUPABASE = "<p>Wenn Sie uns per E-Mail oder über das Kontaktformular schreiben, verarbeiten wir Ihre Angaben (Name, Betrieb, E-Mail, Telefon, Thema, Nachricht und die Seite, von der Sie das Formular abgeschickt haben) zur Bearbeitung der Anfrage und zur Anbahnung eines Vertrags (Art. 6 Abs. 1 lit. b DSGVO). Die Angaben aus dem Formular werden in einer Datenbank bei Supabase Inc. gespeichert; die Daten liegen in einem Rechenzentrum in der EU. Mit Supabase besteht ein Auftragsverarbeitungsvertrag. Wir löschen Anfragen, aus denen kein Auftrag entsteht, spätestens nach 12 Monaten; ansonsten gelten die gesetzlichen Aufbewahrungsfristen.</p>"
DS_MAIL = "<p>Wenn Sie uns per E-Mail oder über das Kontaktformular schreiben (das Formular öffnet Ihr E-Mail-Programm mit einer vorbereiteten Nachricht), verarbeiten wir Ihre Angaben zur Bearbeitung der Anfrage und zur Anbahnung eines Vertrags (Art. 6 Abs. 1 lit. b DSGVO). Wir löschen Anfragen, aus denen kein Auftrag entsteht, spätestens nach 12 Monaten; ansonsten gelten die gesetzlichen Aufbewahrungsfristen.</p>"


def rechtliches():
    DS_FORM = DS_SUPABASE if C.get("supabase_url") else DS_MAIL
    i = C["impressum"]
    imp = f"""<section class="hero"><div class="wrap prose"><h1>Impressum</h1>
<h2>Angaben gemäß § 5 DDG</h2><p>{i["inhaber"]}<br>{NAME}<br>{i["strasse"]}<br>{i["ort"]}</p>
<h2>Kontakt</h2><p>Telefon: {i["telefon"]}<br>E-Mail: <a href="mailto:{i["email"]}">{i["email"]}</a></p>
<h2>Umsatzsteuer</h2><p>{i["ust"]}</p>
<h2>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h2><p>{i["inhaber"]}, Anschrift wie oben.</p>
<h2>Verbraucherstreitbeilegung</h2><p>Wir sind nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
<h2>Haftung für Inhalte und Links</h2><p>Wir erstellen die Inhalte dieser Seiten mit Sorgfalt, übernehmen aber keine Gewähr für Vollständigkeit und Aktualität. Für Inhalte verlinkter externer Seiten sind ausschließlich deren Betreiber verantwortlich.</p></div></section>"""
    write("/impressum/", "Impressum", "Impressum und Anbieterkennzeichnung.", imp, prio=0.2)
    ds = f"""<section class="hero"><div class="wrap prose"><h1>Datenschutzerklärung</h1>
<h2>1. Verantwortlicher</h2><p>{i["inhaber"]}, {i["strasse"]}, {i["ort"]}, E-Mail: {i["email"]}</p>
<h2>2. Grundsatz</h2><p>Diese Website verwendet keine Cookies und keine Einbindungen von Drittanbietern. Schriften werden lokal ausgeliefert. Eine Einwilligung über ein Cookie-Banner ist daher nicht erforderlich.</p>
<h2>2a. Anonyme Reichweitenmessung</h2><p>Um zu verstehen, welche Seiten hilfreich sind, zählen wir Seitenaufrufe und Klicks auf Kontakt-, Telefon- und E-Mail-Links. Gespeichert werden nur die aufgerufene Seite, die Art des Ereignisses (z. B. „Aufruf“ oder „Klick auf Kontakt“) und der Zeitpunkt. Wir setzen keine Cookies, speichern nichts auf Ihrem Gerät, lesen keine Informationen aus Ihrem Gerät aus (z. B. Bildschirmgröße oder Herkunftsseite), speichern keine IP-Adressen und vergeben keine Kennungen – ein Rückschluss auf Ihre Person ist nicht möglich. Die Daten liegen bei Supabase Inc. in einem Rechenzentrum in der EU (Auftragsverarbeitungsvertrag besteht) und werden nach spätestens 25 Monaten gelöscht. Bei der Übertragung verarbeitet der Server technisch bedingt Ihre IP-Adresse, speichert sie aber nicht in unserer Datenbank. Rechtsgrundlage ist unser berechtigtes Interesse an einer bedarfsgerechten Gestaltung der Website (Art. 6 Abs. 1 lit. f DSGVO).</p>
<h2>3. Hosting</h2><p>Die Website wird bei Vercel Inc., 440 N Barranca Ave #4133, Covina, CA 91723, USA gehostet. Beim Aufruf verarbeitet Vercel technisch notwendige Daten (IP-Adresse, Zeitpunkt, aufgerufene Seite, Browserinformationen) zur Auslieferung und zur Abwehr von Angriffen. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO. Vercel ist unter dem EU-US Data Privacy Framework zertifiziert; zusätzlich besteht ein Auftragsverarbeitungsvertrag mit Standardvertragsklauseln.</p>
<h2>4. Kontaktaufnahme und Kontaktformular</h2>{DS_FORM}
<h2>5. Ihre Rechte</h2><p>Sie haben das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch (Art. 15–21 DSGVO) sowie das Recht auf Beschwerde bei einer Datenschutz-Aufsichtsbehörde.</p>
<h2>6. Speicherung im Browser</h2><p>Wenn Sie zwischen hellem und dunklem Design wechseln, wird diese Einstellung ausschließlich in Ihrem Browser gespeichert (localStorage) und nicht an uns übertragen.</p>
<p>Stand: {date.today().strftime("%m/%Y")}</p></div></section>"""
    write("/datenschutz/", "Datenschutzerklärung", "Informationen zum Datenschutz auf dieser Website.", ds, prio=0.2)
    write("/404.html", "Seite nicht gefunden", "Diese Seite gibt es nicht.", '<section class="hero"><div class="wrap prose"><p class="kicker">404</p><h1>Diese Seite gibt es nicht (mehr).</h1><p class="lead">Vielleicht hilft einer dieser Wege weiter:</p><p><a class="btn" href="/">Zur Startseite</a> <a class="btn ghost" href="/beispiele/">Beispiele</a></p></div></section>')


HEADERS = {"X-Content-Type-Options": "nosniff", "Referrer-Policy": "strict-origin-when-cross-origin",
           "X-Frame-Options": "SAMEORIGIN", "Permissions-Policy": "camera=(), microphone=(), geolocation=(), interest-cohort=()",
           "Strict-Transport-Security": "max-age=63072000; includeSubDomains",
           "Content-Security-Policy": f"default-src 'self'; connect-src 'self'{(' ' + C['supabase_url']) if C.get('supabase_url') else ''}; img-src 'self' data: https://images.pexels.com; style-src 'self' 'unsafe-inline'; script-src 'self'; font-src 'self'; form-action 'self' mailto:; base-uri 'self'; frame-ancestors 'self'"}


def extras():
    shutil.copytree(ROOT / "static", DIST, dirs_exist_ok=True)
    (DIST / "favicon.svg").write_text(FAVICON)
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
                          {"source": "/fonts/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]}]}
    (DIST / "vercel.json").write_text(json.dumps(vercel, indent=2))


if __name__ == "__main__":
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir()
    for f in (startseite, leistungen, branchen, beispiele, preise, ablauf, faq_page, ratgeber, kontakt, rechtliches, vorschauseiten):
        f()
    extras()
    n = len(list(DIST.rglob("*.html")))
    print(f"{n} Seiten gebaut → {DIST}")
