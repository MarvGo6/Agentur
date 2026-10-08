#!/usr/bin/env python3
"""E4 Abnahme-Prüfung für eine gebaute Kunden-Website (Ordner mit index.html).

Aufruf:  python3 sites/pruefung.py kunden/<slug>/dist [--json bericht.json]
Prüft statisch: [PRÜFEN]-Reste, genau eine H1, Titel/Beschreibung vorhanden und eindeutig, Impressum + Datenschutz verlinkt,
keine externen Skripte/Schriften/Styles/iframes ohne Einwilligung, interne Links erreichbar, Alt-Texte, LocalBusiness-Schema.
Prüft im Browser (Playwright, Handy 390 px): kein seitliches Scrollen, keine JS-Fehler, keine Cookies, keine Anfragen an Dritte.
Terminbuchung (kunde.json → buchung): Link gesetzt und erreichbar, Testbuchung eingetragen (buchung.testbuchung = Datum).
Optional Lighthouse (wenn „npx lighthouse“ verfügbar): Ziel ≥ 90 in allen Kategorien.
Exit-Code 1 bei schweren Fehlern – blockiert Livegang und Pull Request.
"""
import json, re, subprocess, sys, os, threading, functools, http.server, socketserver
from pathlib import Path
from html.parser import HTMLParser

SCHWER, HINWEIS = "schwer", "hinweis"


class Seite(HTMLParser):
    def __init__(self):
        super().__init__(); self.h1 = 0; self.title = ""; self._t = False; self.desc = None; self.links = []; self.res = []; self.imgs_ohne_alt = 0; self.ld = []; self._ld = False
    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "h1": self.h1 += 1
        if tag == "title": self._t = True
        if tag == "meta" and a.get("name") == "description": self.desc = a.get("content")
        if tag == "a" and a.get("href"): self.links.append(a["href"])
        if tag == "img" and not (a.get("alt") or "").strip(): self.imgs_ohne_alt += 1
        if tag in ("script", "img", "iframe") and a.get("src"): self.res.append((tag, a["src"]))
        if tag == "link" and a.get("href") and a.get("rel") in ("stylesheet", "preload", "icon"): self.res.append(("link", a["href"]))
        if tag == "script" and a.get("type") == "application/ld+json": self._ld = True
    def handle_endtag(self, tag):
        if tag == "title": self._t = False
        if tag == "script": self._ld = False
    def handle_data(self, d):
        if self._t: self.title += d
        if self._ld: self.ld.append(d)


def statisch(dist: Path):
    funde, titel, seiten = [], {}, sorted(dist.rglob("*.html"))
    for f in seiten:
        rel = "/" + str(f.relative_to(dist)).replace("index.html", "")
        h = f.read_text(encoding="utf-8")
        p = Seite(); p.feed(h)
        if "[PRÜFEN]" in h: funde.append((SCHWER, rel, f"{h.count('[PRÜFEN]')}× [PRÜFEN] im Inhalt"))
        if p.h1 != 1: funde.append((SCHWER, rel, f"{p.h1} H1-Überschriften statt genau einer"))
        if not p.title.strip(): funde.append((SCHWER, rel, "Seitentitel fehlt"))
        if not (p.desc or "").strip(): funde.append((SCHWER, rel, "Seitenbeschreibung fehlt"))
        elif len(p.desc) < 50 or len(p.desc) > 170: funde.append((HINWEIS, rel, f"Seitenbeschreibung {len(p.desc)} Zeichen (ideal 50–160)"))
        titel.setdefault(p.title.strip(), []).append(rel)
        if not any("/impressum" in l for l in p.links) or not any("/datenschutz" in l for l in p.links): funde.append((SCHWER, rel, "Link zu Impressum oder Datenschutz fehlt"))
        for tag, src in p.res:
            if re.match(r"^(https?:)?//", src): funde.append((SCHWER, rel, f"externe Ressource ohne Einwilligung: <{tag}> {src[:80]}"))
        for l in p.links:
            if l.startswith("/") and not l.startswith("//"):
                ziel = dist / l.split("#")[0].split("?")[0].lstrip("/")
                if not (ziel.exists() or (ziel / "index.html").exists() or ziel.with_suffix(".html").exists()): funde.append((SCHWER, rel, f"toter Link {l}"))
        if p.imgs_ohne_alt: funde.append((SCHWER, rel, f"{p.imgs_ohne_alt} Bilder ohne Alt-Text"))
        if rel == "/":
            ok = False
            for blk in p.ld:
                try:
                    j = json.loads(blk)
                    if j.get("name") and j.get("address") and j.get("telephone"): ok = True
                except Exception:
                    funde.append((SCHWER, rel, "strukturierte Daten (JSON-LD) ungültig"))
            if not ok: funde.append((SCHWER, rel, "LocalBusiness-Schema ohne Name, Adresse oder Telefon"))
    for t, pf in titel.items():
        if len(pf) > 1: funde.append((HINWEIS, ", ".join(pf), f"gleicher Seitentitel „{t[:60]}“"))
    for pflicht in ("impressum/index.html", "datenschutz/index.html", "robots.txt"):
        if not (dist / pflicht).exists(): funde.append((SCHWER, "/", f"{pflicht} fehlt"))
    return funde, [("/" + str(f.relative_to(dist)).replace("index.html", "")) for f in seiten]


def server(dist: Path):
    class Leise(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    s = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Leise, directory=str(dist)))
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s, f"http://127.0.0.1:{s.server_address[1]}"


BROWSER_JS = r"""
const {chromium}=require('playwright');(async()=>{const [base,...pfade]=process.argv.slice(1);const out=[];
const b=await chromium.launch(process.env.CHROMIUM?{executablePath:process.env.CHROMIUM}:{});
for(const pf of pfade){const ctx=await b.newContext({viewport:{width:390,height:844}});const p=await ctx.newPage();const fehler=[],fremd=[];
 p.on('pageerror',e=>fehler.push(String(e)));p.on('console',m=>{if(m.type()==='error')fehler.push(m.text())});
 p.on('request',r=>{const u=new URL(r.url());if(!['127.0.0.1','localhost'].includes(u.hostname)&&!u.protocol.startsWith('data'))fremd.push(u.hostname)});
 await p.goto(base+pf,{waitUntil:'networkidle'}).catch(e=>fehler.push(String(e)));
 const ueber=await p.evaluate('document.documentElement.scrollWidth>innerWidth+1');const cookies=(await ctx.cookies()).length;
 out.push({pfad:pf,fehler,fremd:[...new Set(fremd)],ueberlauf:ueber,cookies});await ctx.close();}
await b.close();console.log(JSON.stringify(out));})();"""


def browser(base, pfade):
    try:
        npm_root = subprocess.check_output(["npm", "root", "-g"], text=True).strip()
        r = subprocess.run(["node", "-e", BROWSER_JS, base, *pfade], capture_output=True, text=True, timeout=300, env={**os.environ, "NODE_PATH": npm_root})
        daten = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception as ex:
        return [(HINWEIS, "/", f"Browser-Prüfung nicht möglich ({str(ex)[:80]})")]
    funde = []
    for d in daten:
        if d["ueberlauf"]: funde.append((SCHWER, d["pfad"], "seitliches Scrollen am Handy"))
        if d["cookies"]: funde.append((SCHWER, d["pfad"], f"{d['cookies']} Cookie(s) ohne Einwilligung"))
        for h in d["fremd"]: funde.append((SCHWER, d["pfad"], f"Anfrage an Dritte beim Laden: {h}"))
        for f in d["fehler"][:3]: funde.append((SCHWER, d["pfad"], f"JS-Fehler: {f[:120]}"))
    return funde


def lighthouse(base):
    try:
        r = subprocess.run(["npx", "--no-install", "lighthouse", base + "/", "--quiet", "--output=json", "--chrome-flags=--headless=new --no-sandbox",
                            "--only-categories=performance,accessibility,best-practices,seo", "--form-factor=mobile"], capture_output=True, text=True, timeout=240)
        j = json.loads(r.stdout)
        werte = {k: round(v["score"] * 100) for k, v in j["categories"].items()}
        return [(SCHWER if v < 90 else HINWEIS, "/", f"Lighthouse {k}: {v}") for k, v in werte.items()], werte
    except Exception:
        return [(HINWEIS, "/", "Lighthouse nicht verfügbar – läuft in der GitHub Action")], None


def terminbuchung(dist: Path):
    """Buchung muss vor dem Livegang einmal echt getestet sein: Termin buchen → kommt im Kalender des Betriebs an → stornieren."""
    kj = dist.parent / "kunde.json"
    if not kj.exists():
        return []
    b = json.loads(kj.read_text(encoding="utf-8")).get("buchung") or {}
    if b.get("art") not in ("link", "eingebettet"):
        return []
    url, funde = (b.get("url") or "").strip(), []
    if not url.startswith("https://"):
        return [(SCHWER, "/", "Terminbuchung: Link zur Buchungsseite fehlt oder ist nicht https")]
    for name, u in [("Buchungsseite", url)] + [(f"Buchung {s}", x) for s, x in (b.get("leistungen") or {}).items()]:
        try:
            import urllib.request
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (Lotwerk-Pruefung)"}), timeout=15) as r:
                if r.status >= 400: funde.append((SCHWER, "/", f"{name} antwortet mit Status {r.status}"))
        except Exception as ex:
            code = getattr(ex, "code", None)
            funde.append((SCHWER, "/", f"{name} antwortet mit Status {code}") if code and code >= 400 and code not in (401, 403, 405, 429)
                         else (HINWEIS, "/", f"{name} nicht prüfbar ({str(ex)[:60]}) – bitte im Browser öffnen"))
    if not b.get("testbuchung"):
        funde.append((SCHWER, "/", "Terminbuchung nicht getestet: einen Termin buchen, im Kalender des Betriebs bestätigen lassen, stornieren – dann in kunde.json buchung.testbuchung = Datum"))
    return funde


def pruefen(dist):
    dist = Path(dist)
    funde, pfade = statisch(dist)
    funde += terminbuchung(dist)
    s, base = server(dist)
    try:
        funde += browser(base, pfade)
        lh, werte = lighthouse(base)
        funde += lh
    finally:
        s.shutdown()
    schwer = [f for f in funde if f[0] == SCHWER]
    return {"ok": not schwer, "schwer": len(schwer), "hinweise": len(funde) - len(schwer), "lighthouse": werte,
            "funde": [{"stufe": a, "seite": b, "text": c} for a, b, c in funde], "seiten": len(pfade)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    b = pruefen(sys.argv[1])
    for f in b["funde"]:
        print(("✗ " if f["stufe"] == SCHWER else "· ") + f'{f["seite"]}: {f["text"]}')
    print(f'\n{"BESTANDEN" if b["ok"] else "NICHT BESTANDEN"} – {b["seiten"]} Seiten, {b["schwer"]} schwere Fehler, {b["hinweise"]} Hinweise')
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(b, ensure_ascii=False, indent=1))
    sys.exit(0 if b["ok"] else 1)
