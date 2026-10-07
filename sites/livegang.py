#!/usr/bin/env python3
"""E5 Livegang per Knopf: geprüfte Kunden-Website auf Vercel veröffentlichen, Domain verbinden, DNS setzen, Überwachung anmelden.

Aufruf:  python3 sites/livegang.py kunden/<slug> --probe     (zeigt nur, was passieren würde)
         python3 sites/livegang.py kunden/<slug>             (führt aus – nur nach bestandener Abnahme-Prüfung)
Umgebung: VERCEL_TOKEN (Pflicht), VERCEL_TEAM_ID (falls Team), CF_API_TOKEN (optional: DNS bei Cloudflare automatisch),
          SUPABASE_SERVICE_KEY (optional: Website in der Überwachung auf „live“ setzen).
"""
import hashlib, json, os, sys, urllib.request, urllib.error
from datetime import date
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import generator, pruefung  # noqa: E402

VERCEL_IP, VERCEL_CNAME = "76.76.21.21", "cname.vercel-dns.com"


def anfrage(url, methode="GET", daten=None, token=None, roh=None, extra=None):
    h = {"Authorization": f"Bearer {token}"} if token else {}
    if daten is not None: h["Content-Type"] = "application/json"
    h.update(extra or {})
    body = roh if roh is not None else (json.dumps(daten).encode() if daten is not None else None)
    req = urllib.request.Request(url, method=methode, headers=h, data=body)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            t = r.read().decode(); return r.status, (json.loads(t) if t else {})
    except urllib.error.HTTPError as ex:
        t = ex.read().decode(); return ex.code, (json.loads(t) if t.startswith("{") else {"text": t})


def main():
    if len(sys.argv) < 2: sys.exit(__doc__)
    ordner, probe = Path(sys.argv[1]), "--probe" in sys.argv
    k = json.loads((ordner / "kunde.json").read_text(encoding="utf-8"))
    domain, projekt = k.get("domain"), "kunde-" + k["slug"].strip("_")
    if not domain: sys.exit("In kunde.json fehlt „domain“.")
    dist, offen = generator.bauen(ordner)
    bericht = pruefung.pruefen(dist)
    print(f"Abnahme-Prüfung: {'bestanden' if bericht['ok'] else 'NICHT bestanden'} ({bericht['schwer']} schwere Fehler)")
    if not bericht["ok"] and "--trotzdem" not in sys.argv:
        for f in bericht["funde"]:
            if f["stufe"] == "schwer": print("  ✗", f["seite"], f["text"])
        sys.exit("Abbruch: erst alle schweren Fehler beheben.")
    dateien = [p for p in dist.rglob("*") if p.is_file()]
    print(f"Plan: Projekt „{projekt}“, {len(dateien)} Dateien hochladen, Domain {domain} + www.{domain} verbinden, DNS A {VERCEL_IP} / CNAME www → {VERCEL_CNAME}")
    if probe: return

    token, team = os.environ.get("VERCEL_TOKEN"), os.environ.get("VERCEL_TEAM_ID")
    if not token: sys.exit("VERCEL_TOKEN fehlt.")
    q = f"?teamId={team}" if team else ""
    liste = []
    for p in dateien:                                            # 1) Dateien hochladen (nur neue, Vercel erkennt Dubletten am SHA)
        roh = p.read_bytes(); sha = hashlib.sha1(roh).hexdigest()
        st, _ = anfrage(f"https://api.vercel.com/v2/files{q}", "POST", token=token, roh=roh, extra={"x-vercel-digest": sha, "Content-Type": "application/octet-stream"})
        if st not in (200, 201): sys.exit(f"Upload {p.name} fehlgeschlagen ({st}).")
        liste.append({"file": str(p.relative_to(dist)), "sha": sha, "size": len(roh)})
    st, dep = anfrage(f"https://api.vercel.com/v13/deployments{q}", "POST", {"name": projekt, "files": liste, "target": "production",
                      "projectSettings": {"framework": None, "buildCommand": None, "installCommand": None, "outputDirectory": None}}, token)
    if st not in (200, 201): sys.exit(f"Deployment fehlgeschlagen ({st}): {dep}")
    print("Deployment:", "https://" + dep.get("url", ""))
    for d in (domain, f"www.{domain}"):                         # 2) Domains am Projekt (www leitet auf die Hauptdomain)
        body = {"name": d} if d == domain else {"name": d, "redirect": domain, "redirectStatusCode": 308}
        st, r = anfrage(f"https://api.vercel.com/v10/projects/{projekt}/domains{q}", "POST", body, token)
        print(f"Domain {d}: {'ok' if st in (200, 201) else r.get('error', {}).get('message', st)}")
    cf = os.environ.get("CF_API_TOKEN")                         # 3) DNS bei Cloudflare, sonst Anleitung
    zone = None
    if cf:
        st, z = anfrage(f"https://api.cloudflare.com/client/v4/zones?name={domain}", token=cf)
        zone = (z.get("result") or [{}])[0].get("id")
    if zone:
        for typ, name, inhalt in (("A", domain, VERCEL_IP), ("CNAME", f"www.{domain}", VERCEL_CNAME)):
            st, r = anfrage(f"https://api.cloudflare.com/client/v4/zones/{zone}/dns_records", "POST", {"type": typ, "name": name, "content": inhalt, "proxied": False, "ttl": 1}, cf)
            print(f"DNS {typ} {name}: {'gesetzt' if r.get('success') else r.get('errors')}")
    else:
        print(f"DNS beim Domain-Anbieter setzen:  A  @  {VERCEL_IP}   ·   CNAME  www  {VERCEL_CNAME}")
    if os.environ.get("SUPABASE_SERVICE_KEY"):                  # 4) Überwachung: Website auf live
        import ki
        ki.db(f"websites?domain=eq.{domain}", "PATCH", {"status": "live", "live_seit": date.today().isoformat(), "vercel_projekt_id": dep.get("projectId")}, "return=minimal")
        print("Überwachung: Website auf „live“ gesetzt.")
    print("Fertig. Nach der DNS-Umstellung prüft die Überwachung die Seite alle 10 Minuten.")


if __name__ == "__main__":
    main()
