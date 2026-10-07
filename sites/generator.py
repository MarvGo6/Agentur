#!/usr/bin/env python3
"""E3 Generator für Kunden-Websites: kunden/<slug>/kunde.json (+ fotos/) → kunden/<slug>/dist/

Aufruf:  python3 sites/generator.py kunden/<slug>            (echte Website)
         python3 sites/generator.py kunden/<slug> --vorschau  (Vorschau für Interessenten: noindex, Hinweisleiste, Formular sendet nichts)

Gestaltung: Bausteine und Designs aus vorschau.py („vorlage“ = einer der Beispielbetriebe), angepasst über „marke“.
Regeln: Nichts wird erfunden. Fehlende Angaben stehen als [PRÜFEN] im Inhalt – die Abnahme-Prüfung (sites/pruefung.py) blockiert sie.
"""
import json, shutil, sys, html, re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import vorschau as V  # noqa: E402

AGENTUR = json.loads((ROOT / "config.json").read_text())
SB = AGENTUR["supabase_url"]
e = html.escape
P = "[PRÜFEN]"


def kfoto(pfad, alt, cls="foto"):
    """Kunden-Fotos liegen in kunden/<slug>/fotos/ und werden nach /fotos/ kopiert."""
    return f'<img class="{cls}" src="/fotos/{e(str(pfad).split("/")[-1])}" alt="{e(alt)}" loading="lazy" decoding="async">'


V.foto = kfoto  # Bausteine aus vorschau.py nutzen ab jetzt die Kunden-Fotos


def tel_link(t):
    return "tel:" + re.sub(r"[^\d+]", "", t or "")


def formular(k, vorschau):
    f = k.get("formular", {})
    themen = f.get("themen") or [l["titel"] for l in k.get("leistungen", [])][:5]
    opt = "".join(f'<label><input type="radio" name="thema" value="{e(t)}"{" checked" if i == 0 else ""}> {e(t)}</label>' for i, t in enumerate(themen))
    hinweis = "Vorschau – dieses Formular sendet nichts." if vorschau else "Ihre Angaben verwenden wir nur für die Antwort auf Ihre Anfrage. Mehr in der <a href=\"/datenschutz/\">Datenschutzerklärung</a>."
    return f'''<h3>{e(f.get("titel", "Anfrage senden"))}</h3><p class="ok">{e(f.get("text", "Wir melden uns innerhalb von 24 Stunden."))}</p>
<form class="lw-form" data-schluessel="{e(f.get("schluessel", ""))}" data-ziel="{SB}/functions/v1/formular"{" data-vorschau" if vorschau else ""}>
{f'<div class="opt">{opt}</div>' if opt else ""}<div class="row"><label>Name<input name="name" autocomplete="name" required></label><label>Telefon oder E-Mail<input name="kontakt" autocomplete="email" required></label></div>
<label>Ihre Nachricht<textarea name="nachricht" rows="4" required></textarea></label>
<label class="hp" aria-hidden="true">Firma<input name="firma2" tabindex="-1" autocomplete="off"></label>
<button class="btn">Anfrage senden</button><p class="ok" role="status">{hinweis}</p></form>'''


def kontakt_block(k, vorschau, h2=None):
    fi = k["firma"]
    a = fi.get("adresse") or {}
    info = [("phone", fi.get("telefon") or P, "Anrufen"), ("map", ", ".join(x for x in [a.get("strasse"), " ".join(filter(None, [a.get("plz"), a.get("ort")]))] if x) or P, "Adresse")]
    if fi.get("oeffnungszeiten"):
        info.append(("clock", "Öffnungszeiten", " · ".join(fi["oeffnungszeiten"])))
    rows = "".join(f'<div style="display:flex;gap:14px;margin:16px 0"><div class="ic" style="width:44px;height:44px;border-radius:12px;background:var(--soft);color:var(--brand);display:grid;place-items:center;flex:none"><span style="width:22px;height:22px;display:block">{V.ic(i)}</span></div><div><b>{t}</b><br><span class="muted">{x}</span></div></div>' for i, t, x in info)
    head = V.head({"eb": "Kontakt", "h2": h2 or k.get("kontakt_h2", "Schreiben Sie uns"), "p": k.get("kontakt_text", "")})
    return V.sec("tint", f'<div class="g2" style="align-items:start"><div>{head}{rows}</div><div class="form">{formular(k, vorschau)}</div></div>', "kontakt")


def basis(k):
    """Design-Grundlage aus der Vorlage, überschrieben mit der Marke des Kunden."""
    vl = V.DEMOS[k.get("vorlage", "dachdecker-solar")]
    vars_ = dict(vl["vars"])
    m = k.get("marke", {})
    for key, val in (m.get("farben") or {}).items():
        vars_[key] = val
    if (m.get("farben") or {}).get("brand"):
        vars_.setdefault("strip", m["farben"]["brand"]); vars_["strip"] = m["farben"].get("strip", m["farben"]["brand"])
    if (m.get("farben") or {}).get("brand") and "accent" not in m.get("farben", {}):
        vars_["accent"] = m["farben"]["brand"]
    return vl, vars_, vl["fonts"]


def schema(k, url):
    fi, a, v = k["firma"], k["firma"].get("adresse") or {}, k.get("vertrauen") or {}
    s = {"@context": "https://schema.org", "@type": k.get("schema_typ", "LocalBusiness"), "name": fi["name"], "url": url,
         "telephone": fi.get("telefon"), "email": fi.get("email"),
         "address": {"@type": "PostalAddress", "streetAddress": a.get("strasse"), "postalCode": a.get("plz"), "addressLocality": a.get("ort"), "addressCountry": "DE"},
         "areaServed": k.get("einzugsgebiet") or None, "openingHours": fi.get("oeffnungszeiten_schema") or None}
    if v.get("bewertung") and v.get("bewertungen"):
        s["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": v["bewertung"], "reviewCount": v["bewertungen"]}
    return json.dumps({x: y for x, y in s.items() if y}, ensure_ascii=False)


def seite(k, pfad, titel, beschreibung, body_sections, hero, vorschau, extra_schema=None, schlicht=False):
    vl, vars_, fonts = basis(k)
    fi = k["firma"]
    domain = k.get("domain") or "example.de"
    url = f"https://{domain}{pfad}"
    leist = k.get("leistungen", [])
    nav = [(l["titel"], f"/leistungen/{l['slug']}/") for l in leist[:4]] + ([("Karriere", "/karriere/")] if (k.get("recruiting") or {}).get("aktiv") else []) + [("Kontakt", "#kontakt")]
    d = {
        "layout": k.get("layout", vl.get("layout", "split")), "name": e(fi["name"]), "branche": e(k.get("branche", "")), "claim": e(fi.get("claim", "")),
        "mark": e((k.get("marke") or {}).get("mark") or fi["name"][:1]), "art": vl["art"], "fonts": fonts, "vars": vars_,
        "strip": [x for x in [f'<a href="{tel_link(fi.get("telefon"))}" style="color:inherit"><b>{e(fi.get("telefon") or P)}</b></a>',
                              e(" · ".join((fi.get("oeffnungszeiten") or [])[:1])), e(k.get("strip_text", ""))] if x],
        "nav": [(e(t), h) for t, h in nav], "cta": (e(k.get("cta", "Anfrage senden")), "#kontakt"),
        "hero": hero, "sections": body_sections, "trust": [e(s) for s in (k.get("vertrauen") or {}).get("siegel", [])],
        "hero_foto": (k["hero"]["foto"]["datei"], k["hero"]["foto"]["alt"]) if (k.get("hero") or {}).get("foto") else None,
        "footer": {"about": e(k.get("ueber_kurz", fi.get("claim", ""))), "cols": [
            ("Kontakt", [e(x) for x in [(fi.get("adresse") or {}).get("strasse"), " ".join(filter(None, [(fi.get("adresse") or {}).get("plz"), (fi.get("adresse") or {}).get("ort")])), fi.get("telefon"), fi.get("email")] if x]),
            ("Leistungen", [f'<a href="/leistungen/{l["slug"]}/" style="color:inherit">{e(l["titel"])}</a>' for l in leist[:6]]),
            ("Rechtliches", ['<a href="/impressum/" style="color:inherit">Impressum</a>', '<a href="/datenschutz/" style="color:inherit">Datenschutz</a>'] +
             (['<a href="#" data-einwilligung style="color:inherit">Datenschutz-Einstellungen</a>'] if (k.get("tracking") or {}).get("dienste") else []))]},
        "mbar": [("Anrufen", tel_link(fi.get("telefon"))), (e(k.get("cta", "Anfrage")), "#kontakt")],
    }
    lds = [schema(k, f"https://{domain}/")] + ([json.dumps(extra_schema, ensure_ascii=False)] if extra_schema else [])
    robots = "noindex,nofollow" if vorschau else "index,follow"
    head = (f'<title>{e(titel)}</title><meta name="description" content="{e(beschreibung)}"><meta name="robots" content="{robots}">'
            f'<link rel="canonical" href="{url}"><meta property="og:title" content="{e(titel)}"><meta property="og:description" content="{e(beschreibung)}"><meta property="og:url" content="{url}"><meta property="og:locale" content="de_DE">'
            + "".join(f'<script type="application/ld+json">{x}</script>' for x in lds))
    dienste = (k.get("tracking") or {}).get("dienste")
    scripts = ('<script src="/kunde.js" defer></script>' + (f'<script>window.LW_DIENSTE={json.dumps(dienste, ensure_ascii=False)};</script><script src="/einwilligung.js" defer></script>' if dienste else ""))
    bar = f'<div class="demo-bar">Vorschau für {e(fi["name"])} – erstellt von {AGENTUR["name"]} aus öffentlich verfügbaren Angaben. Noch nicht veröffentlicht.</div>' if vorschau else ""
    bottom = f'<span>© {date.today().year} {e(fi["name"])}</span><span><a href="/impressum/" style="color:inherit">Impressum</a> · <a href="/datenschutz/" style="color:inherit">Datenschutz</a></span>'
    h = V.page(d, AGENTUR["name"], "/", echt={"head": head, "bar": bar, "bottom": bottom, "scripts": scripts, "schlicht": schlicht})
    alt, neu = vl["vars"]["brand"], vars_.get("brand", vl["vars"]["brand"])
    return h.replace(alt, neu) if alt != neu else h        # Akzentfarbe der Vorlage auch in Grafiken durch die Kundenfarbe ersetzen


def hero_dict(k, h1=None, lead=None, eb=None):
    h = k.get("hero") or {}
    fi = k["firma"]
    chips = [e(c) for c in h.get("chips", [])]
    v = k.get("vertrauen") or {}
    if v.get("bewertung") and v.get("bewertungen"):
        chips.insert(0, f'<span class="stars">★★★★★</span> <b>{str(v["bewertung"]).replace(".", ",")}</b> · {v["bewertungen"]} Google-Bewertungen')
    return {"eb": e(eb or h.get("eb", "")), "h1": e(h1 or h.get("h1") or P), "lead": e(lead or h.get("lead") or P),
            "ctas": [(e(k.get("cta", "Anfrage senden")), "#kontakt"), ("Anrufen", tel_link(fi.get("telefon")))], "chips": chips, "floats": ""}


def startseite(k, vorschau):
    leist = k.get("leistungen", [])
    secs = []
    if leist:
        secs.append(("services", {"id": "leistungen", "eb": "Leistungen", "h2": e(k.get("leistungen_h2", "Unsere Leistungen")), "cols": 3,
                                  "items": [(l.get("icon", "check"), f'<a href="/leistungen/{l["slug"]}/" style="color:inherit">{e(l["titel"])}</a>', e(l.get("kurz", ""))) for l in leist]}))
    if k.get("ueber"):
        u = k["ueber"]
        secs.append(("split", {"id": "ueber", "eb": "Über uns", "h2": e(u.get("h2", "Über uns")), "p": e(u.get("text", "")), "list": [e(x) for x in u.get("punkte", [])],
                               "vis": "", **({"vis_foto": (u["foto"]["datei"], u["foto"]["alt"])} if u.get("foto") else {})}))
    if k.get("ablauf"):
        secs.append(("steps", {"id": "ablauf", "cls": "tint", "eb": "Ablauf", "h2": e(k.get("ablauf_h2", "So läuft es ab")), "items": [(e(t), e(x)) for t, x in k["ablauf"]]}))
    if k.get("einzugsgebiet"):
        secs.append(("tags", {"eb": "Einsatzgebiet", "h2": e(k.get("gebiet_h2", "Hier sind wir für Sie da")), "items": [e(o) for o in k["einzugsgebiet"]]}))
    if k.get("bewertungen"):  # nur echte Bewertungen mit Quelle und Erlaubnis
        secs.append(("quotes", {"eb": "Bewertungen", "h2": "Was Kunden sagen", "p": e((k.get("vertrauen") or {}).get("quelle", "")),
                                "items": [(e(b["text"]), e(b["name"]), e(b.get("quelle", "Google"))) for b in k["bewertungen"][:6]]}))
    if k.get("team"):
        secs.append(("team", {"id": "team", "eb": "Team", "h2": "Ihre Ansprechpartner", "people": [(e(p["name"][:1]), e(p["name"]), e(p.get("rolle", "")), "var(--soft)") for p in k["team"]]}))
    if k.get("faq"):
        secs.append(("faq", {"eb": "Fragen", "h2": "Häufige Fragen", "items": [(e(q), e(a)) for q, a in k["faq"]]}))
    html_ = seite(k, "/", (k.get("seo") or {}).get("title") or f'{k["firma"]["name"]} – {k.get("branche", "")}', (k.get("seo") or {}).get("description") or P,
                  secs, hero_dict(k), vorschau)
    return einfuegen_kontakt(html_, k, vorschau)


def einfuegen_kontakt(html_, k, vorschau, h2=None):
    return html_.replace('<footer class="ft">', kontakt_block(k, vorschau, h2) + '<footer class="ft">', 1)


def leistungsseite(k, l, vorschau, ort=None):
    titel = f'{l["titel"]} in {ort}' if ort else l["titel"]
    text = (l.get("ortstexte") or {}).get(ort) if ort else l.get("text")
    absaetze = "".join(f"<p>{e(x)}</p>" for x in (text or P).split("\n\n"))
    punkte = '<ul class="list">' + "".join(f"<li>{e(x)}</li>" for x in l.get("punkte", [])) + "</ul>" if l.get("punkte") else ""
    secs = [("custom", {"html": f'<div style="max-width:760px">{absaetze}{punkte}</div>'})]
    if l.get("faq"):
        secs.append(("faq", {"eb": "Fragen", "h2": f'Fragen zu {e(l["titel"])}', "items": [(e(q), e(a)) for q, a in l["faq"]]}))
    loc = (k["firma"].get("adresse") or {}).get("ort", "")
    seo_t = f'{titel} – {k["firma"]["name"]}' + (f" ({loc})" if loc and not ort else "")
    desc = l.get("seo_description") or (f'{l["titel"]} in {ort}: {l.get("kurz", "")}' if ort else l.get("kurz", P))
    svc = {"@context": "https://schema.org", "@type": "Service", "name": titel, "provider": {"@type": k.get("schema_typ", "LocalBusiness"), "name": k["firma"]["name"]},
           "areaServed": ort or (k.get("einzugsgebiet") or None)}
    return einfuegen_kontakt(seite(k, f'/leistungen/{l["slug"]}/' + (f'{slugify(ort)}/' if ort else ""), seo_t, desc, secs,
                                   hero_dict(k, h1=titel, lead=l.get("kurz"), eb=e(k["firma"]["name"])), vorschau, svc, schlicht=True), k, vorschau, f'{e(l["titel"])} anfragen')


def karriere(k, vorschau):
    r = k["recruiting"]
    stellen = "".join(f'<article class="card" style="padding:26px;margin-bottom:14px"><h3>{e(s["titel"] if isinstance(s, dict) else s)}</h3><p>{e(s.get("text", "") if isinstance(s, dict) else "")}</p></article>' for s in r.get("stellen", []))
    secs = [("custom", {"html": f'<div style="max-width:760px">{"".join(f"<p>{e(x)}</p>" for x in (r.get("text") or P).split(chr(10) * 2))}{stellen}</div>'})]
    if r.get("vorteile"):
        secs.append(("services", {"eb": "Vorteile", "h2": "Was Sie bei uns erwartet", "cols": 3, "items": [("check", e(v), "") for v in r["vorteile"]]}))
    return einfuegen_kontakt(seite(k, "/karriere/", f'Karriere – {k["firma"]["name"]}', r.get("seo_description") or P, secs,
                                   hero_dict(k, h1=r.get("h1") or "Arbeiten bei uns", lead=r.get("lead"), eb="Karriere"), vorschau, schlicht=True), k, vorschau, "Jetzt bewerben")


def recht(k, art, vorschau):
    fi, a, rt = k["firma"], k["firma"].get("adresse") or {}, k.get("rechtliches") or {}
    if art == "impressum":
        i = rt.get("impressum") or {}
        zeilen = [fi["name"] + (f' {i["rechtsform"]}' if i.get("rechtsform") else ""), i.get("inhaber") and f'Inhaber: {i["inhaber"]}' or (i.get("vertreten") and f'Vertreten durch: {i["vertreten"]}') or P,
                  a.get("strasse") or P, " ".join(filter(None, [a.get("plz"), a.get("ort")])) or P, f'Telefon: {fi.get("telefon") or P}', f'E-Mail: {fi.get("email") or P}']
        if i.get("register"): zeilen.append(i["register"])
        zeilen.append(f'USt-IdNr.: {i["ust_id"]}' if i.get("ust_id") else (i.get("ust_hinweis") or P))
        if i.get("kammer"): zeilen.append(i["kammer"])
        body = "<h2>Angaben gemäß § 5 DDG</h2><p>" + "<br>".join(e(z) for z in zeilen) + "</p>" + \
               "<h2>Verbraucherstreitbeilegung</h2><p>Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>"
        titel = "Impressum"
    else:
        dienste = (k.get("tracking") or {}).get("dienste") or []
        body = (f"<h2>1. Verantwortlicher</h2><p>{e(fi['name'])}, {e(a.get('strasse') or P)}, {e(' '.join(filter(None, [a.get('plz'), a.get('ort')])) or P)}, {e(fi.get('email') or P)}</p>"
                "<h2>2. Hosting</h2><p>Diese Website wird bei Vercel Inc. gehostet. Beim Aufruf werden technisch notwendige Daten (z. B. IP-Adresse, Zeitpunkt, aufgerufene Seite) "
                "verarbeitet, um die Website auszuliefern und abzusichern (Art. 6 Abs. 1 lit. f DSGVO). Mit Vercel besteht ein Vertrag zur Auftragsverarbeitung; die Übermittlung in die USA "
                "stützt sich auf das EU-US Data Privacy Framework.</p>"
                "<h2>3. Kontaktformular</h2><p>Wenn Sie uns über das Formular schreiben, verarbeiten wir Ihre Angaben, um Ihre Anfrage zu beantworten (Art. 6 Abs. 1 lit. b DSGVO). "
                "Die Anfrage wird über unseren Dienstleister (Supabase, Server in der EU) an uns weitergeleitet und dort nach spätestens 90 Tagen gelöscht.</p>"
                "<h2>4. Cookies</h2><p>" + ("Wir setzen keine Cookies und binden keine Dienste ein, die Ihr Gerät auslesen. Schriften werden von unserem eigenen Server geladen." if not dienste else
                "Technisch notwendige Speicherung: Ihre Datenschutz-Einstellung (lokal in Ihrem Browser). Folgende Dienste laden wir nur nach Ihrer Einwilligung (Art. 6 Abs. 1 lit. a DSGVO, § 25 Abs. 1 TDDDG); "
                "Sie können sie jederzeit über „Datenschutz-Einstellungen“ im Fußbereich widerrufen:</p><ul>" + "".join(f"<li><b>{e(x['name'])}</b> ({e(x.get('anbieter', ''))}): {e(x.get('zweck', ''))}</li>" for x in dienste) + "</ul><p>") + "</p>"
                "<h2>5. Ihre Rechte</h2><p>Sie haben das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und Widerspruch sowie das Recht, "
                "sich bei einer Datenschutz-Aufsichtsbehörde zu beschweren.</p>" + (f"<p>{e(rt['datenschutz_zusatz'])}</p>" if rt.get("datenschutz_zusatz") else ""))
        titel = "Datenschutzerklärung"
    secs = [("custom", {"html": f'<div style="max-width:760px">{body}</div>'})]
    h = seite(k, f"/{art}/", f'{titel} – {fi["name"]}', f'{titel} von {fi["name"]}: Angaben zum Anbieter und zum Umgang mit Ihren Daten.', secs, hero_dict(k, h1=titel, lead=" ", eb=e(fi["name"])), vorschau, schlicht=True)
    return h.replace('<meta name="robots" content="index,follow">', '<meta name="robots" content="noindex,follow">')


def slugify(s):
    s = s.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


KUNDE_JS = """(function(){document.querySelectorAll('.lw-form').forEach(function(f){f.addEventListener('submit',function(ev){ev.preventDefault();
var s=f.querySelector('[role=status]'),b=f.querySelector('button');if(f.hasAttribute('data-vorschau')){s.textContent='Vorschau – nichts gesendet.';return}
var d={schluessel:f.dataset.schluessel,seite:location.pathname};new FormData(f).forEach(function(v,k){d[k]=v});b.disabled=true;s.textContent='Wird gesendet …';
fetch(f.dataset.ziel,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}).then(function(r){return r.json().then(function(j){if(!r.ok)throw new Error(j.fehler);
f.reset();s.textContent='Danke! Ihre Anfrage ist angekommen. Wir melden uns schnell.';})}).catch(function(e){s.textContent=(e&&e.message)||'Senden fehlgeschlagen – bitte rufen Sie uns an.'}).finally(function(){b.disabled=false})})})})();"""


def bauen(ordner, vorschau=False):
    ordner = Path(ordner)
    k = json.loads((ordner / "kunde.json").read_text(encoding="utf-8"))
    out = ordner / ("vorschau" if vorschau else "dist")
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    seiten = {"/": startseite(k, vorschau)}
    for l in k.get("leistungen", []):
        seiten[f'/leistungen/{l["slug"]}/'] = leistungsseite(k, l, vorschau)
        for ort in (l.get("ortstexte") or {}):          # Ortsseiten nur mit eigenem Text je Ort – keine Kopien
            seiten[f'/leistungen/{l["slug"]}/{slugify(ort)}/'] = leistungsseite(k, l, vorschau, ort)
    if (k.get("recruiting") or {}).get("aktiv"):
        seiten["/karriere/"] = karriere(k, vorschau)
    seiten["/impressum/"] = recht(k, "impressum", vorschau)
    seiten["/datenschutz/"] = recht(k, "datenschutz", vorschau)
    if vorschau:  # Vorschau läuft unter agentur-domain/v/<ordner>/ – Pfade anpassen, offene Stellen still ausblenden
        basis_ = f"/v/{ordner.name}"
        seiten = {p: re.sub(r'(href|src)="/(?!/)', rf'\1="{basis_}/', h).replace("url(/fonts", f"url({basis_}/fonts").replace(f" {P}", "").replace(P, "") for p, h in seiten.items()}
    for pfad, h in seiten.items():
        ziel = out / pfad.strip("/") / "index.html" if pfad != "/" else out / "index.html"
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(h, encoding="utf-8")
    # Statische Dateien: Stil, Schriften der Vorlage, Fotos, Skripte
    (out / "site.css").write_text((ROOT / "static" / "demo.css").read_text(encoding="utf-8") +   # + Schutz gegen lange Wörter am Handy, Honigtopf-Feld
        "\nh1,h2,h3{overflow-wrap:break-word;hyphens:auto}.ft .cols>*{min-width:0;overflow-wrap:anywhere}.hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}\n", encoding="utf-8")
    (out / "fonts").mkdir()
    for _, datei in basis(k)[2]:
        shutil.copy(ROOT / "static" / "fonts" / f"{datei}.woff2", out / "fonts")
    if (ordner / "fotos").exists():
        shutil.copytree(ordner / "fotos", out / "fotos")
    (out / "kunde.js").write_text(KUNDE_JS)
    if (k.get("tracking") or {}).get("dienste"):
        shutil.copy(ROOT / "betrieb" / "bausteine" / "einwilligung.js", out / "einwilligung.js")
    farbe = (k.get("marke") or {}).get("farben", {}).get("brand", "#111")
    (out / "favicon.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="{farbe}"/></svg>')
    dom = k.get("domain") or "example.de"
    if vorschau:
        (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
    else:
        (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: https://{dom}/sitemap.xml\n")
        heute = date.today().isoformat()
        (out / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
                                         "".join(f"<url><loc>https://{dom}{p}</loc><lastmod>{heute}</lastmod></url>" for p in seiten if p not in ("/impressum/", "/datenschutz/")) + "</urlset>")
    csp = f"default-src 'self'; connect-src 'self' {SB}; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; font-src 'self'; frame-src 'self' https://www.google.com https://www.youtube-nocookie.com; base-uri 'self'; form-action 'self'"
    hdr = [{"key": "Content-Security-Policy", "value": csp}, {"key": "X-Content-Type-Options", "value": "nosniff"}, {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
           {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()"}] + ([{"key": "X-Robots-Tag", "value": "noindex, nofollow"}] if vorschau else [])
    (out / "vercel.json").write_text(json.dumps({"cleanUrls": True, "trailingSlash": True, "headers": [{"source": "/(.*)", "headers": hdr},
                                                {"source": "/fonts/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]}]}, indent=1))
    offen = sum(h.count(P) for h in seiten.values())
    print(f"{k['firma']['name']}: {len(seiten)} Seiten → {out}" + (f"  ·  {offen}× {P} offen" if offen else ""))
    return out, offen


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    bauen(sys.argv[1], "--vorschau" in sys.argv)
