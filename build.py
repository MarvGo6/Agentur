#!/usr/bin/env python3
"""Baut die statische Website nach dist/. Aufruf: python3 build.py"""
import json, shutil, html
from pathlib import Path
from datetime import date

from content import PREISE, eur, LEISTUNGEN, BRANCHEN, BEISPIELE, KAPITEL, RATGEBER, FAQ
from drawings import HERO, LEISTUNG, BRANCHE, ICON, LOGO, FAVICON
import vorschau

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
C = json.loads((ROOT / "config.json").read_text())
NAME, DOMAIN = C["name"], C["domain"].rstrip("/")
PAGES = []  # (pfad, prio) für die Sitemap
e = html.escape

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
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(full_title)}</title><meta name="description" content="{e(desc)}">{robots}
<link rel="canonical" href="{DOMAIN}{path}"><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta property="og:title" content="{e(full_title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="{DOMAIN}{path}"><meta property="og:locale" content="de_DE">
<meta name="theme-color" content="#f2f0eb"><link rel="preload" href="/fonts/intertight.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/style.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head><body>{bar}<a class="skip" href="#inhalt">Zum Inhalt</a>
<header class="top"><div class="wrap"><a class="logo" href="/" aria-label="{NAME} Startseite">{LOGO}{NAME}</a>
<button class="burger" aria-label="Menü" aria-expanded="false">☰</button>
<nav class="nav" aria-label="Hauptnavigation">{nav}<button class="theme" aria-label="Hell/Dunkel umschalten">◐</button><a class="btn" href="/kontakt/">Erstgespräch</a></nav></div></header>
<main id="inhalt">{crumb_html}{body}</main>
<footer><div class="wrap"><div class="cols">
<div><a class="logo" href="/">{LOGO}{NAME}</a><p style="margin-top:16px;max-width:22em">{e(C["tagline"])}</p><p>Remote aus Deutschland für ganz Deutschland.<br><a href="mailto:{C["email"]}" style="display:inline;color:inherit;text-decoration:underline">{C["email"]}</a></p></div>
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


def cta(titel="Reden wir 20 Minuten.", text="Kostenlos und unverbindlich. Sie erfahren, wo Ihr größter Hebel liegt – auch wenn wir danach nicht zusammenarbeiten."):
    return f'<section class="cta-x"><div class="wrap"><div><p class="kicker">Nächster Schritt</p><h2>{titel}</h2></div><div><p>{text}</p><a class="btn" href="/kontakt/">Erstgespräch anfragen <span class="ar">→</span></a></div></div></section>'


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
<div class="split-row"><div><p class="kicker">Überzeugung</p><h3>Google bringt Besucher. <em class="serif">Die Website macht daraus Kunden.</em></h3>
<p>76 % der Menschen, die „in der Nähe“ suchen, besuchen noch am selben Tag einen Betrieb.<sup>2</sup> Ob es Ihrer ist, entscheidet sich in Sekunden auf dem Handy.</p><a class="more" href="#vorschau">Fertige Beispiel-Websites ansehen</a></div>
<ul class="vs"><li><s>Visitenkarte mit Telefonnummer im Kleingedruckten</s><span>Antworten auf die Fragen Ihrer Kunden: Preise, Ablauf, Menschen</span></li><li><s>Lädt langsam, auf dem Handy kaum bedienbar</s><span>Unter einer Sekunde, gebaut für das Handy</span></li><li><s>„Rufen Sie uns an“ – zu den Öffnungszeiten</s><span>Termin buchen, Fotos schicken, Rückruf anfordern – auch abends um zehn</span></li></ul></div>
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
<div class="work-meta"><span class="wm-n">{i:02d}</span><h3>{b["name"]}</h3><span class="wm-p">{eur(paket_summe(b))} · 1. Jahr</span><span class="wm-b">{b["branche"]}</span><a class="wm-l" href="/beispiele/{b["slug"]}/">Kundenweg &amp; Preis</a></div></article>''')
    return "".join(out)


def startseite():
    svc = "".join(f'<li><a href="/leistungen/{l["slug"]}/"><span class="n">{i:02d}</span><span class="t">{l["titel"]}</span><span class="d">{l["kurz"]}</span><span class="a" aria-hidden="true">→</span></a></li>' for i, l in enumerate(LEISTUNGEN, 1))
    mq = "".join(f'<a href="/branchen/{b["slug"]}/">{b["titel"]}</a>' for b in BRANCHEN)
    body = f"""
<section class="h-hero"><div class="wrap">
<p class="kicker">Websites · Lokale SEO · Google Ads · Recruiting</p>
<h1>Websites, die das Telefon <em>klingeln</em> lassen.</h1>
<div class="h-row"><p class="lead">Für Handwerk, Kanzleien, Pflege und Praxen bauen wir den ganzen Weg von der Suche bis zur Anfrage. Schnell, gut auffindbar, zum Festpreis – und Sie sehen das Ergebnis, bevor Sie bezahlen.</p>
<div class="actions"><a class="btn" href="/kontakt/">Erstgespräch vereinbaren <span class="ar">→</span></a><a class="link" href="#vorschau">Arbeiten ansehen</a></div>
<dl class="h-facts"><div><dt>Erster Entwurf</dt><dd>nach 7 Tagen</dd></div><div><dt>Ladezeit</dt><dd>unter 1 Sekunde</dd></div><div><dt>Preis</dt><dd>fest, vorab</dd></div><div><dt>Eigentum</dt><dd>gehört Ihnen</dd></div></dl></div></div>
<div class="h-stage"><div class="wrap"><div class="showcase"><a href="/vorschau/dachdecker-solar/" class="sc-desk">{frame("dachdecker-solar", eager=True)}</a><a href="/vorschau/friseur/" class="sc-phone">{frame("friseur", mobil=True, eager=True)}</a></div></div></div>
</section>
<div class="marquee" aria-label="Branchen"><div class="mq-track">{mq}{mq.replace('<a ', '<a tabindex="-1" aria-hidden="true" ')}</div></div>
{customer_journey()}
<section id="vorschau"><div class="wrap"><div class="sec-head"><span class="idx"><b>(02)</b> Arbeiten</span><h2>Sehen, was Sie bekommen – <em>bevor Sie bezahlen.</em></h2>
<p>Sieben vollständige Websites für typische Betriebe. Jede mit eigenem Aufbau, eigener Schrift und dem Kundenweg ihrer Branche. Zum Durchklicken, auch auf dem Handy.</p></div>
<div class="work">{arbeiten()}</div></div></section>
<section><div class="wrap"><div class="sec-head"><span class="idx"><b>(03)</b> Leistungen</span><h2>Alles zwischen Suche <em>und Anfrage.</em></h2><p>Einzeln buchbar oder als Programm mit gemeinsamem Ziel.</p></div><ul class="svc">{svc}</ul></div></section>
<section><div class="wrap"><div class="sec-head"><span class="idx"><b>(04)</b> Zusagen</span><h2>Woran Sie uns <em>messen können.</em></h2></div>
<div class="pledges"><div><b>7 Tage</b><span>bis Sie den ersten Entwurf Ihrer Website im Browser sehen</span></div><div><b>&lt;1 s</b><span>Ladezeit auf dem Handy – Standard bei jeder Website</span></div><div><b>0</b><span>Tracking-Cookies, kein Cookie-Banner nötig</span></div><div><b>1</b><span>Ansprechpartner für Website, SEO und Anzeigen</span></div></div>
<p class="promise"><b>Unsere Zusage:</b> Sie sehen den kompletten Entwurf im Browser, bevor die zweite Rechnungshälfte fällig wird. Passt etwas nicht, überarbeiten wir ihn, bevor es weitergeht.</p></div></section>
<section><div class="wrap"><div class="sec-head"><span class="idx"><b>(05)</b> Ablauf</span><h2>In drei Wochen <em>online.</em></h2></div>
<ol class="tl"><li><span class="d">Tag 1</span><h3>Erstgespräch</h3><p>20 Minuten, kostenlos. Wir hören zu und sagen ehrlich, ob wir helfen können.</p></li><li><span class="d">Tag 3</span><h3>Festpreis-Angebot</h3><p>Mit Ziel, Umfang und Zeitplan. Ohne Kleingedrucktes.</p></li><li><span class="d">Tag 10</span><h3>Entwurf</h3><p>Die Startseite live im Browser – auf Ihrem Handy testen, Feedback geben.</p></li><li><span class="d">Tag 21</span><h3>Start</h3><p>Website online, Google-Profil optimiert, Messung aktiv. Danach: monatliche Zahlen.</p></li></ol></div></section>
{cta("Wie würde Ihre Website aussehen?", "Im Erstgespräch skizzieren wir Ihren Kundenweg – und Sie bekommen eine ehrliche Einschätzung, auch wenn wir danach nicht zusammenarbeiten.")}"""
    write("/", f"{NAME} – Websites, SEO & Google Ads für lokale Betriebe", "Websites, die Kunden bringen: schnelle Websites, lokale SEO und Google Ads für Handwerk, Kanzleien, Pflege und Praxen. Mit Vorschau-Websites, Festpreis und einem Ansprechpartner.", body, prio=1.0, crumbs=[("/", "Start")])


def leistungen():
    cards = "".join(f'<a class="card" href="/leistungen/{l["slug"]}/">{ICON[l["key"]]}<h3>{l["titel"]}</h3><p>{l["kurz"]}</p><span class="more">Mehr erfahren →</span></a>' for l in LEISTUNGEN)
    write("/leistungen/", "Leistungen", "Google Ads, SEO, Websites und Wachstumsprogramm für lokale Betriebe.",
          f'<section class="hero"><div class="wrap"><span class="kicker">Leistungen</span><h1>Fünf Bausteine, ein Ziel</h1><p class="lead">Mehr passende Anfragen – und die Fachkräfte, um sie abzuarbeiten. Jeder Baustein funktioniert allein – zusammen wirken sie stärker.</p></div></section><section style="padding-top:0"><div class="wrap grid3">{cards}</div></section>{cta()}',
          prio=0.9, crumbs=[("/", "Start"), ("/leistungen/", "Leistungen")])
    for l in LEISTUNGEN:
        p = f"/leistungen/{l['slug']}/"
        steps = "".join(f"<li><h3>{a}</h3><p>{b}</p></li>" for a, b in l["ablauf"])
        others = "".join(f'<a class="card" href="/leistungen/{o["slug"]}/">{ICON[o["key"]]}<h3>{o["titel"]}</h3><p>{o["kurz"]}</p></a>' for o in LEISTUNGEN if o is not l)
        body = f"""<section class="hero"><div class="wrap grid"><div><span class="kicker">{l["titel"]}</span><h1>{l["h1"]}</h1><p class="lead">{l["lead"]}</p><div class="actions"><a class="btn" href="/kontakt/">Erstgespräch anfragen</a><a class="btn ghost" href="/preise/">Preise</a></div></div><div>{LEISTUNG[l["key"]]}</div></div></section>
<section class="band"><div class="wrap grid2"><div><h2>Was Sie bekommen</h2>{ticks(l["punkte"])}<p class="note"><strong>Preis:</strong> {l["preis"]}</p></div><div><h2>So gehen wir vor</h2><ol class="steps">{steps}</ol></div></div></section>
<section><div class="wrap grid2"><div><h2>Häufige Fragen</h2></div><div>{faq_html(l["faq"])}</div></div></section>
<section class="band"><div class="wrap"><h2>Passt gut dazu</h2><div class="grid3">{others}</div></div></section>{cta()}"""
        write(p, l["h1"], l["kurz"], body, prio=0.8, schema=faq_schema(l["faq"]),
              crumbs=[("/", "Start"), ("/leistungen/", "Leistungen"), (p, l["titel"])])


def branchen():
    cards = "".join(f'<article class="show"><a class="show-img" href="/branchen/{b["slug"]}/">{frame(b["beispiel"])}</a><div class="show-meta"><div><h3>{b["titel"]}</h3></div></div><p style="color:var(--ink-2);margin:8px 0 0">{b["lead"]}</p><div class="show-links"><a href="/branchen/{b["slug"]}/">Branche ansehen →</a><a href="/vorschau/{b["beispiel"]}/">Live-Vorschau</a></div></article>' for b in BRANCHEN)
    write("/branchen/", "Branchen", "Marketing für Dachdecker, Steuerberater, Pflegedienste, Bestatter und Tierarztpraxen.",
          f'<section class="hero"><div class="wrap"><span class="kicker">Branchen</span><h1>Jede Branche hat ihren eigenen Kundenweg</h1><p class="lead">Ein Notfall am Dach läuft anders ab als die Suche nach einer Kanzlei. Deshalb starten wir nie mit einer Vorlage, sondern mit der Frage: Wie entscheiden Ihre Kunden?</p></div></section><section style="padding-top:0"><div class="wrap gallery">{cards}</div></section>{cta()}',
          prio=0.9, crumbs=[("/", "Start"), ("/branchen/", "Branchen")])
    for b in BRANCHEN:
        p = f"/branchen/{b['slug']}/"
        bsp = next(x for x in BEISPIELE if x["slug"] == b["beispiel"])
        body = f"""<section class="hero"><div class="wrap grid"><div><span class="kicker">{b["titel"]}</span><h1>{b["h1"]}</h1><p class="lead">{b["lead"]}</p><div class="actions"><a class="btn" href="/kontakt/">Erstgespräch anfragen</a><a class="btn ghost" href="/vorschau/{bsp["slug"]}/">Fertige Beispiel-Website</a></div></div><div class="showcase small"><a href="/vorschau/{bsp["slug"]}/" class="sc-desk">{frame(bsp["slug"], eager=True)}</a><a href="/vorschau/{bsp["slug"]}/" class="sc-phone">{frame(bsp["slug"], mobil=True, eager=True)}</a></div></div></section>
<section class="band"><div class="wrap grid2"><div><h2>Kommt Ihnen das bekannt vor?</h2><ul class="ticks">{"".join(f"<li>{x}</li>" for x in b["probleme"])}</ul></div><div><h2>Was wir dagegen tun</h2>{ticks(b["loesung"])}</div></div></section>
<section><div class="wrap grid2" style="align-items:center"><div class="card"><div class="num">{b["zahl"][0]}</div><p style="margin-top:10px">{b["zahl"][1]}</p></div><div><span class="kicker">Beispiel-Website</span><h2>{bsp["name"]}</h2><p>{bsp["teaser"]}</p><p><strong>{eur(paket_summe(bsp))}</strong> im ersten Jahr.</p><div class="actions"><a class="btn" href="/vorschau/{bsp["slug"]}/">Live-Vorschau öffnen</a><a class="btn ghost" href="/beispiele/{bsp["slug"]}/">Kundenweg &amp; Preis</a></div></div></div></section>
<section style="padding-top:0"><div class="wrap"><div class="promise" style="display:flex;justify-content:space-between;gap:20px;align-items:center;flex-wrap:wrap"><div><b>Fachkräfte gesucht?</b> Mit dem Recruiting-Paket bekommen Sie Bewerbungen über die eigene Karriereseite statt über teure Portale.</div><a class="more" href="/leistungen/recruiting/" style="margin:0">Recruiting-Paket →</a></div></div></section>{cta()}"""
        write(p, b["h1"], b["lead"], body, prio=0.8, crumbs=[("/", "Start"), ("/branchen/", "Branchen"), (p, b["titel"])])


def beispiele():
    cards = galerie(BEISPIELE)
    write("/beispiele/", "Beispiele mit Kundenweg und Preis", "Sieben durchgerechnete Beispiele: Kundenweg, Umsetzung, Paket und Preis für Friseur, Barber, Dachdecker, Steuerberater, Pflegedienst, Bestatter und Tierarzt.",
          f'<section class="hero"><div class="wrap"><span class="kicker">Beispiele</span><h1>Sieben Betriebe, sieben Kundenwege</h1><p class="lead">Jedes Beispiel erzählt, wie ein Kunde sucht, vergleicht und sich entscheidet – und was wir an jeder Stelle bauen. Mit echtem Paketpreis – und einer vollständigen Vorschau-Website zum Durchklicken.</p><p class="note">Die Betriebe sind erfundene Beispiele, damit Sie Ablauf und Kosten realistisch einschätzen können. Preise entsprechen unserer aktuellen Preisliste.</p></div></section><section style="padding-top:0"><div class="wrap gallery">{cards}</div></section>{cta()}',
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
        body = f"""<section class="hero"><div class="wrap grid"><div><span class="kicker">Beispiel · {b["branche"]}</span><h1>{b["name"]}</h1><p class="lead">{b["teaser"]}</p><p><span class="pill">{b["ort"]}</span> <span class="pill">{eur(paket_summe(b))} im ersten Jahr</span></p><div class="actions"><a class="btn" href="/vorschau/{b["slug"]}/">Live-Vorschau öffnen</a><a class="btn ghost" href="#kapitel-3">Zum Kundenweg</a></div></div><div class="showcase small"><a href="/vorschau/{b["slug"]}/" class="sc-desk">{frame(b["slug"], eager=True)}</a><a href="/vorschau/{b["slug"]}/" class="sc-phone">{frame(b["slug"], mobil=True, eager=True)}</a></div></div></section>
<section style="padding-top:0"><div class="wrap">{chapters}<p class="note">Erfundenes Beispiel zur Veranschaulichung. Ergebnisse hängen von Markt, Wettbewerb und Mitarbeit ab und sind nicht garantiert.</p><p style="margin-top:22px"><a class="more" href="/beispiele/{nxt["slug"]}/">Nächstes Beispiel: {nxt["name"]} ({nxt["branche"]}) →</a></p></div></section>{cta("Wie sieht Ihr Kundenweg aus?", "Im Erstgespräch skizzieren wir ihn gemeinsam – kostenlos.")}"""
        write(p, f"Beispiel {b['branche']}: {b['name']}", b["teaser"], body, prio=0.7,
              crumbs=[("/", "Start"), ("/beispiele/", "Beispiele"), (p, b["branche"])])


def preise():
    P = PREISE
    def box(t, amt, per, items, feat=False, note=""):
        return f'<div class="card price{" feat" if feat else ""}">{"<span class=pill>Beliebt</span>" if feat else ""}<h2 class="h3" style="margin-top:8px">{t}</h2><div class="amt">{amt}</div><div class="per">{per}</div>{ticks(items)}{f"<p class=note>{note}</p>" if note else ""}<a class="btn{"" if feat else " ghost"}" href="/kontakt/" style="text-align:center;margin-top:14px">Anfragen</a></div>'
    web = box("Website Start", eur(P["web_start"]), f"einmalig · Pflege {P['pflege_start']} €/Monat", ["Bis zu 5 Seiten", "Texte und Struktur inklusive", "Google-Unternehmensprofil eingerichtet", "Kontakt- oder Buchungsformular", "Fertig in 2–3 Wochen"]) + \
          box("Website Wachstum", eur(P["web_wachstum"]), f"einmalig · Pflege {P['pflege_wachstum']} €/Monat", ["Bis zu 15 Seiten", "Eigene Seiten je Leistung und Ort", "Karriere- oder Bewerbungsbereich", "Ratgeber-Bereich", "Anruf- und Formularmessung"], feat=True) + \
          box("Wachstumsprogramm", eur(P["programm"]), f"pro Monat · 12 Monate · {eur(P['prog_setup'])} Einrichtung", ["Website Wachstum inklusive", "SEO Plus inklusive", "Google-Ads-Betreuung inklusive", "Monatsgespräch und Bericht", "Gemeinsames, messbares Ziel"], note=f"Einzeln im ersten Jahr: {eur(P['web_wachstum'] + 12*P['pflege_wachstum'] + 12*P['seo_plus'] + P['ads_setup'] + 12*P['ads'])}")
    monat = [("SEO Lokal", P["seo_lokal"], "Profil, Verzeichnisse, 1 neue Seite pro Monat, Bericht. 6 Monate Mindestlaufzeit."),
             ("SEO Plus", P["seo_plus"], "Wie Lokal, plus 2–3 Inhalte pro Monat, Bewertungsprozess, Wettbewerbsanalyse."),
             ("Google-Ads-Betreuung", P["ads"], f"Einrichtung {P['ads_setup']} € einmalig. Monatlich kündbar, Budget separat."),
             ("Recruiting-Paket", P["rec"], f"Karriereseite, Bewerbung in 60 Sekunden, Anzeigen im Umkreis. Einrichtung {eur(P['rec_setup'])} einmalig, Budget separat."),
             ("Pflege & Hosting Start", P["pflege_start"], "Hosting, Updates, Sicherheit, kleine Änderungen."),
             ("Pflege & Hosting Wachstum", P["pflege_wachstum"], "Wie Start, plus 1 Stunde Änderungen pro Monat.")]
    rows = "".join(f"<tr><td><strong>{n}</strong></td><td>{d}</td><td class='r'>{eur(v)}/Monat</td></tr>" for n, v, d in monat)
    faq = [("Sind die Preise Endpreise?", "Ja. " + C["impressum"]["ust"]), ("Gibt es versteckte Kosten?", "Nein. Werbebudget für Anzeigen zahlen Sie direkt an Google oder Meta. Fremdkosten wie spezielle Buchungstools besprechen wir vorher."), ("Kann ich klein anfangen?", "Ja. Viele starten mit einer Website Start und ergänzen später SEO oder Anzeigen.")]
    body = f"""<section class="hero"><div class="wrap"><span class="kicker">Preise</span><h1>Feste Preise. Keine Überraschungen.</h1><p class="lead">Sie wissen vorher, was es kostet. Ohne Stundenzettel, ohne Prozente vom Werbebudget.</p></div></section>
<section style="padding-top:0"><div class="wrap grid3">{web}</div></section>
<section style="padding-top:0"><div class="wrap"><div class="card" style="display:grid;grid-template-columns:1.4fr 1fr;gap:28px;align-items:center;border:2px solid var(--copper)"><div><span class="pill" style="background:var(--copper-soft);color:var(--copper-ink)">Neu</span><h2 style="margin-top:12px">Recruiting-Paket: Fachkräfte statt Stellenportale</h2><p>Karriereseite mit echten Einblicken, Bewerbung in 60 Sekunden ohne Lebenslauf und Anzeigen im Umkreis – für Pflege, Handwerk, Praxen und Kanzleien.</p><a class="more" href="/leistungen/recruiting/">Mehr zum Recruiting-Paket →</a></div><div><div class="amt" style="font:600 2.2rem var(--serif)">{eur(P["rec"])}<small style="font:500 .9rem var(--sans);color:var(--ink-2)"> / Monat</small></div><p style="color:var(--ink-2)">Einrichtung {eur(P["rec_setup"])} einmalig · Werbebudget separat · nach 3 Monaten monatlich kündbar</p><a class="btn" href="/kontakt/">Anfragen</a></div></div></div></section>
<section class="band"><div class="wrap"><h2>Laufende Leistungen</h2><div class="tablewrap"><table><thead><tr><th>Leistung</th><th>Umfang</th><th class="r">Preis</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>
<section><div class="wrap grid2"><div><h2>Fragen zu den Preisen</h2><p>Durchgerechnete Pakete finden Sie in unseren <a href="/beispiele/">Beispielen</a>.</p></div><div>{faq_html(faq)}</div></div></section>{cta()}"""
    write("/preise/", "Preise für Website, SEO und Google Ads", "Website ab 1.490 €, SEO ab 390 €/Monat, Google Ads ab 290 €/Monat, Recruiting-Paket 790 €/Monat, Wachstumsprogramm 1.190 €/Monat plus Einrichtung. Feste Preise ohne Überraschungen.", body, prio=0.9, schema=faq_schema(faq), crumbs=[("/", "Start"), ("/preise/", "Preise")])


def ablauf():
    steps = [("Erstgespräch (20 Min.)", "Per Telefon oder Video. Wir fragen nach Ihren Zielen, Ihren Kunden und dem, was bisher nicht funktioniert hat."),
             ("Kurzanalyse", "Wir sehen uns Website, Google-Profil und Ihre drei stärksten Mitbewerber an. Sie bekommen die wichtigsten Punkte schriftlich."),
             ("Angebot mit Festpreis", "Binnen zwei Werktagen. Mit Ziel, Umfang, Zeitplan und Preis."),
             ("Start-Workshop (60 Min.)", "Wir gehen den Kundenweg gemeinsam durch und sammeln alles, was wir für Texte brauchen."),
             ("Umsetzung", "Sie sehen nach einer Woche den ersten Entwurf im Browser. Feedback per E-Mail oder kurzem Call."),
             ("Freischaltung", "Website online, Messung aktiv, Profil und Kampagnen laufen."),
             ("Monatlich", "Bericht mit den Zahlen, die zählen: Anfragen, Anrufe, Kosten pro Anfrage. Einmal im Quartal planen wir die nächsten Schritte.")]
    body = f"""<section class="hero"><div class="wrap grid2"><div><span class="kicker">Ablauf</span><h1>So arbeiten wir zusammen</h1><p class="lead">Klare Schritte, wenig Aufwand für Sie. Rechnen Sie im ersten Monat mit zwei bis drei Stunden Ihrer Zeit – danach mit etwa 30 Minuten im Monat.</p></div><div><ol class="steps">{"".join(f"<li><h3>{a}</h3><p>{b}</p></li>" for a,b in steps)}</ol></div></div></section>
<section class="band"><div class="wrap grid3"><div class="card"><h3>Remote</h3><p>Alles läuft per Telefon, Video und E-Mail – schnell und ohne Anfahrt.</p></div><div class="card"><h3>Transparent</h3><p>Sie haben Zugriff auf alle Konten: Google-Profil, Ads, Domain. Nichts läuft über Umwege.</p></div><div class="card"><h3>Fair</h3><p>Monatlich kündbar, wo es sinnvoll ist. Längere Laufzeiten nur, wenn sie den Preis senken.</p></div></div></section>{cta()}"""
    write("/ablauf/", "Ablauf der Zusammenarbeit", "Vom Erstgespräch bis zum Monatsbericht: so arbeiten wir mit Ihnen zusammen.", body, prio=0.7, crumbs=[("/", "Start"), ("/ablauf/", "Ablauf")])


def faq_page():
    write("/faq/", "Häufige Fragen", "Antworten zu Laufzeiten, Preisen, Eigentum an der Website, Datenschutz und Zusammenarbeit.",
          f'<section class="hero"><div class="wrap grid2"><div><span class="kicker">FAQ</span><h1>Häufige Fragen</h1><p class="lead">Ihre Frage ist nicht dabei? <a href="/kontakt/">Schreiben Sie uns.</a></p></div><div>{faq_html(FAQ)}</div></div></section>{cta()}',
          prio=0.6, schema=faq_schema(FAQ), crumbs=[("/", "Start"), ("/faq/", "Häufige Fragen")])


def ratgeber():
    cards = "".join(f'<a class="card" href="/ratgeber/{r["slug"]}/"><span class="pill">{r["min"]} Min. Lesezeit</span><h3 style="margin-top:12px">{r["titel"]}</h3><p>{r["kurz"]}</p><span class="more">Lesen →</span></a>' for r in RATGEBER)
    write("/ratgeber/", "Ratgeber", "Praxiswissen zu Websites, lokaler SEO, Google Ads und Google-Unternehmensprofil für kleine Betriebe.",
          f'<section class="hero"><div class="wrap"><span class="kicker">Ratgeber</span><h1>Wissen, das Sie sofort nutzen können</h1><p class="lead">Ohne Fachchinesisch. Vieles davon können Sie selbst umsetzen.</p></div></section><section style="padding-top:0"><div class="wrap grid2">{cards}</div></section>{cta()}',
          prio=0.7, crumbs=[("/", "Start"), ("/ratgeber/", "Ratgeber")])
    for r in RATGEBER:
        p = f"/ratgeber/{r['slug']}/"
        schema = {"@context": "https://schema.org", "@type": "Article", "headline": r["titel"], "description": r["kurz"],
                  "author": {"@type": "Organization", "name": NAME}, "publisher": {"@type": "Organization", "name": NAME},
                  "datePublished": date.today().isoformat(), "inLanguage": "de"}
        others = "".join(f'<a class="card" href="/ratgeber/{o["slug"]}/"><h3>{o["titel"]}</h3><p>{o["kurz"]}</p></a>' for o in RATGEBER if o is not r)
        body = f"""<section class="hero" style="padding-bottom:20px"><div class="wrap"><span class="kicker">Ratgeber · {r["min"]} Min.</span><h1 style="max-width:16em">{r["titel"]}</h1><p class="lead">{r["kurz"]}</p></div></section>
<section style="padding-top:0"><div class="wrap"><article class="prose">{r["body"]}</article></div></section>
<section class="band"><div class="wrap"><h2>Weiterlesen</h2><div class="grid3">{others}</div></div></section>{cta()}"""
        write(p, r["titel"], r["kurz"], body, prio=0.6, schema=schema, crumbs=[("/", "Start"), ("/ratgeber/", "Ratgeber"), (p, r["titel"])])


def kontakt():
    body = f"""<section class="hero"><div class="wrap grid2"><div><span class="kicker">Kontakt</span><h1>Lassen Sie uns sprechen</h1><p class="lead">Erzählen Sie kurz, worum es geht. Wir melden uns innerhalb eines Werktags mit Terminvorschlägen für ein 20-minütiges Erstgespräch.</p>
{ticks(["Kostenlos und unverbindlich", "Ehrliche Einschätzung, auch wenn wir nicht passen", "Antwort innerhalb eines Werktags"])}
<p>Lieber direkt per E-Mail? <a href="mailto:{C['email']}">{C['email']}</a></p></div>
<div class="card"><form id="anfrage" data-to="{C['email']}" {f'data-sb="{C["supabase_url"]}" data-key="{C["supabase_key"]}"' if C.get("supabase_url") else ""}>
<label>Ihr Name<input name="name" required autocomplete="name"></label>
<label>Betrieb<input name="betrieb" autocomplete="organization"></label>
<label>E-Mail<input name="email" type="email" required autocomplete="email"></label>
<label>Telefon (optional)<input name="telefon" type="tel" autocomplete="tel"></label>
<label>Worum geht es?<select name="thema"><option>Neue Website</option><option>Bei Google gefunden werden (SEO)</option><option>Google Ads</option><option>Mitarbeiter gewinnen (Recruiting-Paket)</option><option>Wachstumsprogramm</option><option>Noch unklar</option></select></label>
<label>Nachricht<textarea name="nachricht" rows="4" placeholder="Was soll in sechs Monaten anders sein?"></textarea></label>
<label class="check"><input type="checkbox" name="einwilligung" required> <span>Ich bin einverstanden, dass meine Angaben zur Bearbeitung der Anfrage verwendet werden. Mehr in der <a href="/datenschutz/">Datenschutzerklärung</a>.</span></label>
<label class="hp" aria-hidden="true">Website<input name="website" tabindex="-1" autocomplete="off"></label>
<button class="btn" type="submit">Anfrage senden</button><p class="form-msg" role="status" style="font-size:.88rem;color:var(--ink-2);margin:0">Wir antworten innerhalb eines Werktags.</p>
</form></div></div></section>"""
    write("/kontakt/", "Kontakt & Erstgespräch", "Kostenloses Erstgespräch zu Website, SEO und Google Ads anfragen. Antwort innerhalb eines Werktags.", body, prio=0.8, crumbs=[("/", "Start"), ("/kontakt/", "Kontakt")])
    write("/danke/", "Danke für Ihre Anfrage", "Ihre Anfrage ist vorbereitet.", f'<section class="hero"><div class="wrap prose"><h1>Danke!</h1><p class="lead">{"Ihre Anfrage ist bei uns angekommen." if C.get("supabase_url") else "Ihre Nachricht ist in Ihrem E-Mail-Programm vorbereitet – bitte dort noch absenden."} Wir melden uns innerhalb eines Werktags. Hat sich kein E-Mail-Programm geöffnet? Schreiben Sie direkt an <a href="mailto:{C["email"]}">{C["email"]}</a>.</p><p><a class="btn" href="/beispiele/">Inzwischen Beispiele ansehen</a></p></div></section>')


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
<h2>2. Grundsatz</h2><p>Diese Website verwendet keine Cookies, keine Analyse-Tools und keine Einbindungen von Drittanbietern. Schriften werden lokal ausgeliefert. Eine Einwilligung über ein Cookie-Banner ist daher nicht erforderlich.</p>
<h2>3. Hosting</h2><p>Die Website wird bei Vercel Inc., 440 N Barranca Ave #4133, Covina, CA 91723, USA gehostet. Beim Aufruf verarbeitet Vercel technisch notwendige Daten (IP-Adresse, Zeitpunkt, aufgerufene Seite, Browserinformationen) zur Auslieferung und zur Abwehr von Angriffen. Rechtsgrundlage ist Art. 6 Abs. 1 lit. f DSGVO. Vercel ist unter dem EU-US Data Privacy Framework zertifiziert; zusätzlich besteht ein Auftragsverarbeitungsvertrag mit Standardvertragsklauseln.</p>
<h2>4. Kontaktaufnahme und Kontaktformular</h2>{DS_FORM}
<h2>5. Ihre Rechte</h2><p>Sie haben das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch (Art. 15–21 DSGVO) sowie das Recht auf Beschwerde bei einer Datenschutz-Aufsichtsbehörde.</p>
<h2>6. Speicherung im Browser</h2><p>Wenn Sie zwischen hellem und dunklem Design wechseln, wird diese Einstellung ausschließlich in Ihrem Browser gespeichert (localStorage) und nicht an uns übertragen.</p>
<p>Stand: {date.today().strftime("%m/%Y")}</p></div></section>"""
    write("/datenschutz/", "Datenschutzerklärung", "Informationen zum Datenschutz auf dieser Website.", ds, prio=0.2)
    write("/404.html", "Seite nicht gefunden", "Diese Seite gibt es nicht.", '<section class="hero"><div class="wrap prose"><span class="kicker">404</span><h1>Diese Seite gibt es nicht (mehr).</h1><p class="lead">Vielleicht hilft einer dieser Wege weiter:</p><p><a class="btn" href="/">Zur Startseite</a> <a class="btn ghost" href="/beispiele/">Beispiele</a></p></div></section>')


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
