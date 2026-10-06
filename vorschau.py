"""Vorschau-Websites für die sechs Beispielbetriebe (fiktiv). Jede Seite hat eigene Marke, Farben und Schriften.
Aufbau und Bausteine orientieren sich an dem, was gut rankende Betriebe in Großstädten zeigen (siehe RECHERCHE.md)."""
import html as _h

e = _h.escape

# ------------------------------------------------------------------ Icons (Linien, 24er Raster)
_I = {
 "scissors": '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M8.1 8.1 20 20M8.1 15.9 20 4"/>',
 "drop": '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
 "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6"/>',
 "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
 "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/>',
 "shield": '<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z"/><path d="m9 12 2 2 4-4"/>',
 "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5 19 19M5 19l1.5-1.5M17.5 6.5 19 5"/>',
 "home": '<path d="M3 11 12 4l9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
 "wrench": '<path d="M14.5 6.5a4 4 0 0 0 5 5L12 19a2.1 2.1 0 0 1-3-3z"/><path d="M14.5 6.5 17 4"/>',
 "file": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M8 13h8M8 17h5"/>',
 "chart": '<path d="M4 20V4M4 20h16"/><path d="m7 15 4-4 3 3 5-6"/>',
 "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 14a6 6 0 0 1 3.5 6"/>',
 "heart": '<path d="M12 20s-8-4.5-8-10.5A4.5 4.5 0 0 1 12 7a4.5 4.5 0 0 1 8 2.5C20 15.5 12 20 12 20z"/>',
 "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 "leaf": '<path d="M5 19c0-9 6-14 15-14 0 9-5 15-14 15"/><path d="M5 19 13 11"/>',
 "paw": '<circle cx="7" cy="9" r="2"/><circle cx="12" cy="6" r="2"/><circle cx="17" cy="9" r="2"/><path d="M12 11c-3 0-6 4-6 6.5S8 21 12 19.5c4 1.5 6 .5 6-2S15 11 12 11z"/>',
 "tooth": '<path d="M7 3c-2.5 0-4 2-4 4.5 0 3 1.5 4.5 2 7.5.5 3 1 6 2.5 6s1.5-4 2.5-6c.5-1 1.5-1 2 0 1 2 1 6 2.5 6s2-3 2.5-6c.5-3 2-4.5 2-7.5C19 5 17.5 3 15 3c-1.5 0-2 .7-3 .7S8.5 3 7 3z"/>',
 "pill": '<rect x="3" y="9" width="18" height="6" rx="3" transform="rotate(-45 12 12)"/><path d="m9.5 9.5 5 5"/>',
 "steth": '<path d="M5 3v6a5 5 0 0 0 10 0V3"/><path d="M10 14v2a5 5 0 0 0 10 0v-2"/><circle cx="20" cy="12" r="2"/>',
 "map": '<path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
 "star": '<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1 6.2L12 17.3 6.5 20.2l1-6.2L3 9.6l6.2-.9z"/>',
 "euro": '<path d="M17 6.5A7 7 0 1 0 17 17.5"/><path d="M4 10h9M4 14h9"/>',
 "brief": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M3 13h18"/>',
 "flower": '<circle cx="12" cy="9" r="2.5"/><path d="M12 6.5c0-3 2.5-3.5 2.5-3.5s1 2.5-1 4M12 6.5c0-3-2.5-3.5-2.5-3.5s-1 2.5 1 4M14.5 9c3 0 3.5 2.5 3.5 2.5s-2.5 1-4-1M9.5 9c-3 0-3.5 2.5-3.5 2.5s2.5 1 4-1"/><path d="M12 11.5V21M12 17c-2-2-4-2-5-1.5M12 15c2-2 4-2 5-1.5"/>',
 "candle": '<rect x="9" y="10" width="6" height="11" rx="1"/><path d="M12 10V8M12 3c-1.5 2-1.5 3.5 0 5 1.5-1.5 1.5-3 0-5z"/>',
 "hand": '<path d="M7 11V5.5a1.5 1.5 0 0 1 3 0V10M10 9.5v-6a1.5 1.5 0 0 1 3 0v6M13 9.5V5a1.5 1.5 0 0 1 3 0v6M16 10a1.5 1.5 0 0 1 3 0v3a8 8 0 0 1-8 8 6 6 0 0 1-5-3l-3-5a1.5 1.5 0 0 1 2.5-1.5L7 13"/>',
 "car": '<path d="M5 16V11l2-5h10l2 5v5"/><path d="M3 16h18v3H3zM7 19v2M17 19v2"/><circle cx="7.5" cy="13" r="1"/><circle cx="16.5" cy="13" r="1"/>',
 "check": '<path d="m5 12 5 5 9-10"/>',
 "bolt": '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
 "chat": '<path d="M4 5h16v11H9l-5 4z"/>',
}

# ------------------------------------------------------------------ Fotos (Pexels, lizenzfrei; werden beim Build geladen)
FOTO = {}  # id -> Dateiname in /bilder/, wird von build.py gefüllt

PEXELS = "https://images.pexels.com/photos/{0}/pexels-photo-{0}.jpeg?auto=compress&cs=tinysrgb&w=1400"

def foto(pid, alt, cls="foto"):
    """Lokal gehostetes Foto, sonst direkt von Pexels. Lädt es nicht, blendet demo.js es aus (Zeichnung bleibt)."""
    f = FOTO.get(str(pid))
    src = f"/bilder/{f}" if f else PEXELS.format(pid)
    return f'<img class="{cls}" src="{src}" alt="{alt}" loading="lazy" decoding="async">'

def alle_fotos():
    ids = set()
    for d in DEMOS.values():
        if d.get("hero_foto"): ids.add(str(d["hero_foto"][0]))
        for k, v in d["sections"]:
            for pid, _ in v.get("fotos", []): ids.add(str(pid))
            if v.get("vis_foto"): ids.add(str(v["vis_foto"][0]))
    return sorted(ids)


def ic(name):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{_I[name]}</svg>'


# ------------------------------------------------------------------ Hero-Kunst je Marke
ART = {
 "friseur": '''<svg viewBox="0 0 600 560" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="fg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e9c9bd"/><stop offset="1" stop-color="#b9786a"/></linearGradient></defs>
<rect width="600" height="560" fill="url(#fg)"/><circle cx="430" cy="140" r="170" fill="#f4e4dc" opacity=".35"/>
<g fill="none" stroke="#1f1a19" stroke-width="2.4" stroke-linecap="round">
<path d="M330 470c-10-60-6-120 16-170 18-40 20-80 2-112-20-36-70-50-112-34-46 18-66 70-54 118 6 26 20 44 18 70-2 20-18 30-16 46 2 12 16 14 22 22 8 10-2 26 8 34 10 8 30 2 40 10 12 10 8 30 14 52"/>
<path d="M236 160c40-40 120-40 150 20 26 52 6 110 30 160 20 42 60 70 74 120" opacity=".9"/>
<path d="M250 150c60-30 130-6 146 56 14 50-4 96 22 140 22 38 52 58 64 104" opacity=".55"/>
<path d="M266 142c70-16 126 18 132 76 4 46-10 84 14 124 20 34 40 52 50 90" opacity=".35"/>
<path d="M226 176c-30 30-40 80-24 120" opacity=".6"/></g>
<g stroke="#1f1a19" stroke-width="2.4" fill="none"><circle cx="118" cy="420" r="18"/><circle cx="160" cy="440" r="18"/><path d="M132 408l80-110M146 430l92-80"/></g></svg>''',
 "barber": '''<svg viewBox="0 0 600 560" preserveAspectRatio="xMidYMid slice"><rect width="600" height="560" fill="#141518"/>
<circle cx="440" cy="150" r="200" fill="#1d1f23"/><g transform="translate(250 70)"><rect width="90" height="400" rx="45" fill="#f2efe9"/>
<clipPath id="bp"><rect width="90" height="400" rx="45"/></clipPath><g clip-path="url(#bp)" fill="#b8323a"><path d="M-40 40 130 -50 130 -20 -40 70z"/><path d="M-40 130 130 40 130 70 -40 160z"/><path d="M-40 220 130 130 130 160 -40 250z"/><path d="M-40 310 130 220 130 250 -40 340z"/><path d="M-40 400 130 310 130 340 -40 430z"/><path d="M-40 490 130 400 130 430 -40 520z"/></g>
<g fill="#c8a165"><rect x="-14" y="-24" width="118" height="28" rx="6"/><rect x="-14" y="396" width="118" height="28" rx="6"/></g></g>
<path d="M90 470 220 340" stroke="#c8a165" stroke-width="6" stroke-linecap="round"/><path d="M220 340 250 330 240 360z" fill="#c8a165"/></svg>''',
 "dach": '''<svg viewBox="0 0 600 560" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="dg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2b3a48"/><stop offset="1" stop-color="#151c23"/></linearGradient></defs>
<rect width="600" height="560" fill="url(#dg)"/><circle cx="455" cy="130" r="58" fill="#e8692b"/><circle cx="455" cy="130" r="92" fill="#e8692b" opacity=".14"/>
<path d="M0 400 120 300l120 100v160H0z" fill="#0f151b"/><path d="M200 420 360 270l160 150v140H200z" fill="#1b252e"/>
<path d="M360 270 520 420" stroke="#e8692b" stroke-width="5"/><path d="M200 420 360 270" stroke="#e8692b" stroke-width="5"/>
<g transform="translate(286 318) skewX(-43)" fill="#3c6e9e" stroke="#9cc3e6" stroke-width="1.4"><rect width="40" height="26"/><rect x="44" width="40" height="26"/><rect x="88" width="40" height="26"/><rect y="30" width="40" height="26"/><rect x="44" y="30" width="40" height="26"/><rect x="88" y="30" width="40" height="26"/></g>
<path d="M440 560V470h44v90" fill="#0f151b"/><path d="M0 470h600" stroke="#2c3843" stroke-width="1"/></svg>''',
 "steuer": '''<svg viewBox="0 0 600 560" preserveAspectRatio="xMidYMid slice"><rect width="600" height="560" fill="#14233c"/>
<g stroke="#b08d57" stroke-width="1" opacity=".35">''' + "".join(f'<path d="M{x} 0v560"/>' for x in range(40, 600, 40)) + "".join(f'<path d="M0 {y}h600"/>' for y in range(40, 560, 40)) + '''</g>
<path d="M60 430 170 370 260 392 360 290 450 300 545 170" fill="none" stroke="#d8b87a" stroke-width="4" stroke-linejoin="round"/>
<g fill="#d8b87a"><circle cx="170" cy="370" r="7"/><circle cx="360" cy="290" r="7"/><circle cx="545" cy="170" r="9"/></g>
<g fill="#22385c"><rect x="80" y="450" width="56" height="110"/><rect x="170" y="420" width="56" height="140"/><rect x="260" y="400" width="56" height="160"/><rect x="350" y="350" width="56" height="210"/><rect x="440" y="320" width="56" height="240"/></g></svg>''',
 "pflege": '''<svg viewBox="0 0 600 560" preserveAspectRatio="xMidYMid slice"><rect width="600" height="560" fill="#3f7d5c"/>
<circle cx="470" cy="120" r="210" fill="#4f9470"/><circle cx="90" cy="520" r="200" fill="#356b4f"/><circle cx="470" cy="120" r="120" fill="#5fa47f"/>
<g fill="none" stroke="#f7f1e6" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
<path d="M120 380c60-14 104-14 160 0l84 20c20 6 20 34-4 34h-82"/><path d="M120 436c90 0 170 14 240 0l124-56c20-8 12-40-12-34l-86 22"/>
<path d="M300 300c-56-42-84-70-84-106 0-26 20-46 46-46 17 0 30 9 38 22 8-13 21-22 38-22 26 0 46 20 46 46 0 36-28 64-84 106z" stroke="#f5b48a" stroke-width="3.4"/></g></svg>''',
 "bestatter": '''<svg viewBox="0 0 600 560" preserveAspectRatio="xMidYMid slice"><defs><radialGradient id="bg2" cx=".62" cy=".32" r=".7"><stop offset="0" stop-color="#5a5f63"/><stop offset="1" stop-color="#22272b"/></radialGradient></defs>
<rect width="600" height="560" fill="url(#bg2)"/><circle cx="372" cy="180" r="120" fill="#e9e1d2" opacity=".07"/>
<g fill="none" stroke="#c9ad7b" stroke-width="2.2" stroke-linecap="round">
<path d="M300 520V240"/><path d="M300 240c-46-16-76-60-62-120 46 16 62 60 62 120zM300 240c46-16 76-60 62-120-46 16-62 60-62 120zM300 236c-6-50 0-96 0-130 0 34 6 80 0 130z"/>
<path d="M300 340c-38-6-70-30-80-62M300 380c38-6 70-30 80-62"/><path d="M300 430c-24 0-44-14-52-34"/></g>
<path d="M120 520h360" stroke="#c9ad7b" stroke-width="1" opacity=".5"/></svg>''',
 "tierarzt": '''<svg viewBox="0 0 600 560" preserveAspectRatio="xMidYMid slice"><rect width="600" height="560" fill="#0e7c86"/>
<circle cx="480" cy="460" r="230" fill="#13909b"/><circle cx="110" cy="90" r="150" fill="#0a6c75"/>
<g fill="#f2b63c"><ellipse cx="300" cy="330" rx="84" ry="70"/><ellipse cx="196" cy="226" rx="32" ry="42"/><ellipse cx="270" cy="176" rx="32" ry="42"/><ellipse cx="352" cy="180" rx="32" ry="42"/><ellipse cx="420" cy="236" rx="32" ry="42"/></g>
<path d="M300 300v60M270 330h60" stroke="#0e7c86" stroke-width="12" stroke-linecap="round"/>
<g fill="#fff" opacity=".5"><circle cx="520" cy="110" r="5"/><circle cx="80" cy="420" r="4"/><circle cx="540" cy="300" r="3"/></g></svg>''',
}

MAP = '''<svg viewBox="0 0 600 380" class="map"><rect width="600" height="380" fill="var(--bg2)"/>
<g fill="none" stroke="var(--line)" stroke-width="2"><path d="M0 120c120 30 200-40 320 0s200 60 280 20"/><path d="M0 260c140-30 220 50 340 10s180-40 260 0"/><path d="M180 0c20 120-30 220 10 380"/><path d="M420 0c-30 130 40 240 0 380"/></g>
<circle cx="300" cy="190" r="150" fill="var(--brand)" opacity=".08" stroke="var(--brand)" stroke-dasharray="6 6"/>
{pins}<circle cx="300" cy="190" r="9" fill="var(--accent)" stroke="#fff" stroke-width="3"/></svg>'''

def mappins(n=40, seed=7):
    import random
    r = random.Random(seed); out = []
    for _ in range(n):
        a = r.random() * 6.283; d = r.random() ** .6 * 140
        import math
        x, y = 300 + math.cos(a) * d, 190 + math.sin(a) * d * .9
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="5" fill="var(--brand)" stroke="#fff" stroke-width="2"/>')
    return MAP.replace("{pins}", "".join(out))


# ------------------------------------------------------------------ Bausteine
def head(d, center=False):
    st = ' style="margin-inline:auto;text-align:center"' if center else ""
    eb = f'<span class="eyebrow">{d["eb"]}</span>' if d.get("eb") else ""
    p = f'<p>{d["p"]}</p>' if d.get("p") else ""
    return f'<div class="head"{st}>{eb}<h2>{d["h2"]}</h2>{p}</div>'

def sec(cls, inner, id_=""):
    return f'<section class="sec {cls}"{f" id={id_}" if id_ else ""}><div class="w">{inner}</div></section>'

def b_stats(d):
    return f'<section style="padding:36px 0"><div class="w"><div class="stats">{"".join(f"<div><b>{a}</b>{b}</div>" for a, b in d["items"])}</div></div></section>'

def b_services(d):
    cards = ""
    for it in d["items"]:
        icon, t, txt = it[:3]
        price = f'<div class="price-tag"><span>{it[3]}</span><b>{it[4]}</b></div>' if len(it) > 3 else ""
        cards += f'<div class="card"><div class="ic">{ic(icon)}</div><h3>{t}</h3><p>{txt}</p>{price}</div>'
    return sec(d.get("cls", ""), head(d) + f'<div class="g{d.get("cols", 3)}">{cards}</div>', d.get("id", ""))

def b_split(d):
    lst = '<ul class="list">' + "".join(f"<li>{x}</li>" for x in d.get("list", [])) + "</ul>" if d.get("list") else ""
    cta = f'<a class="btn" href="{d["cta"][1]}">{d["cta"][0]}</a>' if d.get("cta") else ""
    txt = f'<div><span class="eyebrow">{d.get("eb","")}</span><h2>{d["h2"]}</h2><p class="muted" style="font-size:1.1rem">{d["p"]}</p>{lst}{cta}</div>'
    vis = d["vis"]
    if d.get("vis_foto") and foto(*d["vis_foto"]):
        img = foto(*d["vis_foto"], cls="foto tall")
        vis = f'<div class="pw">{img}<div class="pw-card">{vis}</div></div>' if d.get("overlay") else img
    if d.get("fotos") and all(foto(p, a) for p, a in d["fotos"]):
        vis = '<div class="pgrid">' + "".join(foto(p, a) for p, a in d["fotos"]) + f'</div><div class="fb">{vis}</div>'
    vis = f'<div>{vis}</div>'
    inner = f'<div class="g2">{vis + txt if d.get("rev") else txt + vis}</div>'
    return sec(d.get("cls", ""), inner, d.get("id", ""))

def b_steps(d):
    items = "".join(f"<div><h3>{t}</h3><p>{x}</p></div>" for t, x in d["items"])
    return sec(d.get("cls", ""), head(d) + f'<div class="steps" style="--n:{len(d["items"])}">{items}</div>', d.get("id", ""))

def b_prices(d):
    rows = "".join(f'<tr><td><b>{n}</b>{f"<small>{s}</small>" if s else ""}</td><td class="r">{p}</td></tr>' for n, s, p in d["rows"])
    note = f'<p class="muted" style="font-size:.88rem;margin-top:14px">{d["note"]}</p>' if d.get("note") else ""
    side = d.get("side", "")
    tbl = f'<div><table class="tbl"><tbody>{rows}</tbody></table>{note}</div>'
    inner = head(d) + (f'<div class="g2" style="align-items:start">{tbl}<div>{side}</div></div>' if side else tbl)
    return sec(d.get("cls", ""), inner, d.get("id", ""))

def b_team(d):
    ppl = "".join(f'<div class="person"><div class="ph" style="--ph:{c}"><span>{i}</span></div><h3>{n}</h3><p>{r}</p></div>' for i, n, r, c in d["people"])
    return sec(d.get("cls", ""), head(d) + f'<div class="team" style="--n:{len(d["people"])}">{ppl}</div>', d.get("id", ""))

def b_quotes(d):
    q = "".join(f'<div class="quote"><div class="stars">★★★★★</div><p>„{t}“</p><footer><i>{n[0]}</i><span><b style="color:var(--ink)">{n}</b><br>{m}</span></footer></div>' for t, n, m in d["items"])
    return sec(d.get("cls", ""), head(d) + f'<div class="g3">{q}</div>', d.get("id", ""))

def b_faq(d):
    items = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in d["items"])
    return sec(d.get("cls", ""), f'<div class="g2" style="align-items:start"><div>{head(d)}</div><div class="faq">{items}</div></div>', d.get("id", ""))

def b_tags(d):
    tags = "".join(f"<span>{x}</span>" for x in d["items"])
    vis = d.get("vis", "")
    inner = f'<div class="g2"><div>{head(d)}<div class="tags">{tags}</div></div><div>{vis}</div></div>' if vis else head(d) + f'<div class="tags">{tags}</div>'
    return sec(d.get("cls", ""), inner, d.get("id", ""))

def b_paths(d):
    items = "".join(f'<a href="{h}" style="background:{bg};color:{fg}"><span class="eyebrow" style="color:{fg};opacity:.75">{eb}</span><h3 style="font-size:1.7rem">{t}</h3><p style="opacity:.82;max-width:26em">{x}</p><span class="go">→</span></a>' for eb, t, x, h, bg, fg in d["items"])
    return f'<section style="padding:30px 0 0"><div class="w"><div class="paths">{items}</div></div></section>'

def b_strip(d):
    imgs = [foto(p, a) for p, a in d["fotos"]]
    if not all(imgs):
        return ""
    cap = f'<p class="muted" style="margin-top:14px;font-size:.9rem">{d["cap"]}</p>' if d.get("cap") else ""
    return f'<section style="padding:0 0 20px"><div class="w"><div class="strip-f" style="--n:{len(imgs)}">{"".join(imgs)}</div>{cap}</div></section>'

def b_custom(d):
    return sec(d.get("cls", ""), d["html"], d.get("id", ""))

def b_cta(d):
    return f'<section class="sec" style="padding-top:20px"><div class="w"><div class="cta-band"><div><h2>{d["h2"]}</h2><p>{d["p"]}</p></div><a class="btn" href="{d["btn"][1]}">{d["btn"][0]}</a></div></div></section>'

FORMS = {
 "termin": lambda d: f'''<h3>Termin anfragen</h3><p class="ok">Wählen Sie Leistung und Wunschzeit – wir bestätigen per SMS.</p><form class="demo-form">
<label>Leistung<select>{"".join(f"<option>{o}</option>" for o in d.get("optionen", ["Schnitt &amp; Styling", "Farbe / Balayage", "Herrenschnitt", "Beratung"]))}</select></label>
<label>Wunschtermin</label><div class="slots"><i>Di 10:30</i><i class="on">Di 14:00</i><i>Mi 09:00</i><i>Mi 16:30</i><i>Do 11:00</i><i>Fr 15:30</i></div>
<div class="row"><label>Name<input placeholder="Vor- und Nachname"></label><label>Handy<input placeholder="Für die Bestätigung"></label></div>
<button class="btn">Termin anfragen</button><p class="ok">Vorschau – das Formular sendet nichts.</p></form>''',
 "anfrage": lambda d: f'''<h3>Kostenlose Ersteinschätzung</h3><p class="ok">Fotos genügen oft für eine erste Einschätzung. Rückruf innerhalb von 24 Stunden.</p><form class="demo-form">
<div class="opt"><label><input type="radio" name="t" checked> Dachsanierung</label><label><input type="radio" name="t"> Photovoltaik</label><label><input type="radio" name="t"> Reparatur / Sturmschaden</label><label><input type="radio" name="t"> Flachdach</label></div>
<div class="row"><label>Name<input placeholder="Ihr Name"></label><label>Telefon<input placeholder="Für den Rückruf"></label></div>
<label>Postleitzahl<input placeholder="z. B. 12345"></label><div class="drop">📷 Fotos vom Dach hierher ziehen (optional)</div>
<button class="btn">Anfrage senden</button><p class="ok">Vorschau – das Formular sendet nichts.</p></form>''',
 "erstgespraech": lambda d: f'''<h3>Erstgespräch buchen</h3><p class="ok">20 Minuten per Video oder Telefon – kostenlos und unverbindlich.</p><form class="demo-form">
<label>Worum geht es?<select><option>Laufende Buchhaltung &amp; Lohn</option><option>Jahresabschluss</option><option>Kanzleiwechsel</option><option>Gründung</option></select></label>
<label>Freie Termine diese Woche</label><div class="slots"><i>Mo 08:30</i><i>Di 12:00</i><i class="on">Mi 10:00</i><i>Do 17:30</i><i>Fr 09:00</i></div>
<div class="row"><label>Name<input></label><label>Betrieb<input placeholder="z. B. Malerbetrieb"></label></div><label>E-Mail<input></label>
<button class="btn">Termin bestätigen</button><p class="ok">Vorschau – das Formular sendet nichts.</p></form>''',
 "bewerbung": lambda d: f'''<h3>Bewerbung in 60 Sekunden</h3><p class="ok">Kein Lebenslauf, kein Anschreiben. Wir rufen Sie innerhalb von 48 Stunden an.</p><form class="demo-form">
<label>Ihre Qualifikation</label><div class="opt"><label><input type="radio" name="q" checked> Pflegefachkraft</label><label><input type="radio" name="q"> Pflegehelfer:in</label><label><input type="radio" name="q"> Azubi</label></div>
<label>Wunsch-Stunden</label><div class="opt"><label><input type="radio" name="s"> Vollzeit</label><label><input type="radio" name="s" checked> Teilzeit</label><label><input type="radio" name="s"> Minijob</label></div>
<div class="row"><label>Vorname<input></label><label>Handy<input placeholder="Für den Rückruf"></label></div>
<button class="btn acc">Jetzt bewerben</button><p class="ok">Vorschau – das Formular sendet nichts.</p></form>''',
 "rueckruf": lambda d: f'''<h3>Rückruf anfordern</h3><p class="ok">Für Fragen zur Vorsorge oder zu Kosten. Im Trauerfall rufen Sie bitte direkt an.</p><form class="demo-form">
<div class="row"><label>Name<input></label><label>Telefon<input></label></div>
<label>Wann passt es Ihnen?<select><option>Vormittags</option><option>Nachmittags</option><option>Abends</option></select></label>
<label>Ihr Anliegen (optional)<textarea rows="3"></textarea></label>
<button class="btn">Rückruf anfordern</button><p class="ok">Vorschau – das Formular sendet nichts.</p></form>''',
 "tierarzt": lambda d: f'''<h3>Termin oder Rezept</h3><p class="ok">Anfrage online – wir bestätigen werktags innerhalb von zwei Stunden.</p><form class="demo-form">
<div class="opt"><label><input type="radio" name="a" checked> Terminanfrage</label><label><input type="radio" name="a"> Rezept / Futter bestellen</label></div>
<div class="row"><label>Ihr Tier<select><option>Hund</option><option>Katze</option><option>Kaninchen</option><option>Anderes</option></select></label><label>Name des Tieres<input placeholder="z. B. Mia"></label></div>
<label>Anliegen<select><option>Impfung / Vorsorge</option><option>Zahnkontrolle</option><option>Physiotherapie</option><option>Krankheit / Beschwerden</option></select></label>
<div class="row"><label>Ihr Name<input></label><label>Telefon<input></label></div>
<button class="btn">Anfrage senden</button><p class="ok">Vorschau – das Formular sendet nichts.</p></form>''',
}

def b_contact(d):
    info = "".join(f'<div style="display:flex;gap:14px;margin:16px 0"><div class="ic" style="width:44px;height:44px;border-radius:12px;background:var(--soft);color:var(--brand);display:grid;place-items:center;flex:none"><span style="width:22px;height:22px;display:block">{ic(i)}</span></div><div><b>{t}</b><br><span class="muted">{x}</span></div></div>' for i, t, x in d["info"])
    return sec(d.get("cls", "tint"), f'<div class="g2" style="align-items:start"><div>{head(d)}{info}</div><div class="form">{FORMS[d["form"]](d)}</div></div>', "kontakt")

BLOCKS = {"stats": b_stats, "services": b_services, "split": b_split, "steps": b_steps, "prices": b_prices, "team": b_team,
          "quotes": b_quotes, "strip": b_strip, "faq": b_faq, "tags": b_tags, "paths": b_paths, "custom": b_custom, "cta": b_cta, "contact": b_contact}


def page(d, agentur, back):
    fonts = "".join(f'@font-face{{font-family:"{n}";src:url(/fonts/{f}.woff2) format("woff2");font-weight:300 800;font-display:swap}}' for n, f in d["fonts"])
    vars_ = ";".join(f"--{k}:{v}" for k, v in d["vars"].items())
    nav = "".join(f'<a href="{h}">{t}</a>' for t, h in d["nav"])
    strip = "".join(f"<span>{x}</span>" for x in d["strip"])
    h = d["hero"]
    acts = "".join(f'<a class="btn{"" if i == 0 else " alt"}" href="{u}">{t}</a>' for i, (t, u) in enumerate(h["ctas"]))
    chips = "".join(f"<span>{c}</span>" for c in h["chips"])
    body = "".join(BLOCKS[k](v) for k, v in d["sections"])
    ft = d["footer"]
    mbar = "".join(f'<a class="btn sm{"" if i == 0 else " alt"}" href="{u}">{t}</a>' for i, (t, u) in enumerate(d["mbar"]))
    return f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{d["name"]} – Vorschau | {agentur}</title><meta name="robots" content="noindex,nofollow">
<meta name="description" content="Vorschau einer Beispiel-Website von {agentur} für einen fiktiven Betrieb ({d["branche"]}).">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/demo.css">
<style>{fonts}:root{{{vars_}}}</style></head><body>
<div class="demo-bar">Vorschau einer Beispiel-Website von {agentur} · {d["name"]} ist ein fiktiver Betrieb · <a href="{back}">← Zurück zum Beispiel</a></div>
<div class="strip"><div class="w">{strip}</div></div>
<header class="hd"><div class="w"><a class="brand" href="#"><span class="mark">{d["mark"]}</span><span>{d["name"]}<small>{d["claim"]}</small></span></a><nav class="nav">{nav}</nav><a class="btn sm" href="{d["cta"][1]}">{d["cta"][0]}</a></div></header>
<section class="hero"><div class="w"><div><span class="eyebrow">{h["eb"]}</span><h1>{h["h1"]}</h1><p class="lead">{h["lead"]}</p><div class="acts">{acts}</div><div class="chips">{chips}</div></div>
<div class="stage"><div class="art">{ART[d["art"]]}{foto(*d["hero_foto"], cls="foto hero-img").replace(' loading="lazy"', ' fetchpriority="high"') if d.get("hero_foto") else ""}</div>{h["floats"]}</div></div></section>
{body}
<footer class="ft"><div class="w"><div class="cols"><div><div class="brand" style="color:#fff"><span class="mark">{d["mark"]}</span><span>{d["name"]}</span></div><p style="margin-top:16px;max-width:26em">{ft["about"]}</p></div>
{"".join(f'<div><h4>{t}</h4><ul>{"".join(f"<li>{x}</li>" for x in xs)}</ul></div>' for t, xs in ft["cols"])}</div>
<div class="bottom"><span>© {d["name"]} · fiktiver Beispielbetrieb</span><span>Website-Vorschau von {agentur} · Fotos: Pexels</span></div></div></footer>
<div class="mbar">{mbar}</div><script src="/demo.js" defer></script></body></html>"""


def fl(style, inner):
    return f'<div class="float" style="{style}">{inner}</div>'


# ------------------------------------------------------------------ Die sechs Betriebe
DEMOS = {}

DEMOS["friseur"] = {
 "hero_foto": (3993453, "Friseurin schneidet einer Kundin die Haare"),
 "name": "Kamm &amp; Kante", "branche": "Friseur", "claim": "Salon für Schnitt &amp; Farbe", "mark": "K&amp;K", "art": "friseur",
 "fonts": [("Bodoni Moda", "bodoni"), ("Manrope", "manrope")],
 "vars": {"bg": "#f7f2ed", "bg2": "#efe6de", "card": "#fffdfb", "ink": "#1d1918", "muted": "#6d625e", "line": "#e3d7ce", "brand": "#1d1918", "brand-ink": "#f7f2ed",
          "accent": "#b5705f", "soft": "#f1e1d9", "display": '"Bodoni Moda",Didot,serif', "body": "Manrope,system-ui,sans-serif", "dw": "500", "dls": "-.02em", "mr": "50%", "stage": "#c98b7a", "dark": "#1d1918", "ft": "#1d1918"},
 "strip": ["Di–Fr 9–19 Uhr · Sa 8–15 Uhr", "Marktstraße 8 · Musterstadt", '<span class="stars">★★★★★</span> 4,9 bei Google (Beispiel)'],
 "nav": [("Leistungen", "#leistungen"), ("Preise", "#preise"), ("Team", "#team"), ("Salon", "#salon")], "cta": ("Termin buchen", "#kontakt"),
 "hero": {"eb": "Friseursalon in Musterstadt", "h1": "Schnitte, die auch am dritten Tag noch sitzen.",
          "lead": "Zwei Stühle, viel Zeit für Beratung und Farben, die zu Ihnen passen. Termine online buchen – auch abends um zehn.",
          "ctas": [("Freien Termin finden", "#kontakt"), ("Preise ansehen", "#preise")],
          "chips": ['<span class="stars">★★★★★</span> <b>4,9</b> aus 187 Bewertungen', "Nur mit Termin – keine Wartezeit", "Olaplex &amp; vegane Farben"],
          "floats": fl("left:-18px;top:34px;width:250px", "<h4>Nächste freie Termine</h4><div class='slots'><i>Heute 16:30</i><i class='on'>Mi 10:00</i><i>Do 14:30</i></div>")
                  + fl("right:-12px;bottom:30px;width:240px", "<div class='stars'>★★★★★</div><p style='margin:6px 0 4px'>„Endlich jemand, der zuhört. Beste Farbe seit Jahren.“</p><span class='muted'>Lea, Neukundin</span>")},
 "sections": [
  ("services", {"id": "leistungen", "eb": "Leistungen", "h2": "Alles, was Ihr Haar braucht", "p": "Jede Behandlung beginnt mit einer ehrlichen Beratung – kostenlos und ohne Zeitdruck.", "cols": 3, "items": [
    ("scissors", "Schnitt &amp; Styling", "Waschen, Beratung, Schnitt und Föhnen – passend zu Gesicht, Haarstruktur und Alltag.", "Damen ab", "54 €"),
    ("drop", "Farbe &amp; Balayage", "Natürliche Verläufe, Grauabdeckung oder ein ganz neuer Look – mit pflegenden, veganen Farben.", "ab", "89 €"),
    ("spark", "Pflege &amp; Treatments", "Olaplex-Kur, Kopfhautpflege und Glossing für Glanz, der bleibt.", "ab", "29 €")]}),
  ("split", {"id": "salon", "eb": "Der Salon", "h2": "Klein, ruhig und mit Zeit für Sie", "p": "Bei uns gibt es keine Fließbandtermine. Zwei Stühle, ein Termin nach dem anderen – und am Ende eine Frisur, die Sie zu Hause selbst hinbekommen.",
    "fotos": [(705255, "Salon mit hellen Stühlen"), (3356170, "Haarschnitt im Salon"), (2799605, "Styling mit Rundbürste"), (853427, "Friseurstühle vor Spiegeln")],
    "list": ["Eine Ansprechpartnerin vom Waschen bis zum Föhnen", "Tipps für das Styling zu Hause", "Kaffee, Tee und WLAN"], "cta": ("Termin buchen", "#kontakt"),
    "vis": '<div class="ba"><div style="background:linear-gradient(160deg,#c9a28f,#7d5446)">Vorher</div><div style="background:linear-gradient(160deg,#e0b9a3,#a9604d)">Nachher</div><div style="background:linear-gradient(160deg,#b98d7a,#4c3029)">Balayage</div><div style="background:linear-gradient(160deg,#d8c2b5,#8c6b5f)">Bob</div></div>'}),
  ("prices", {"id": "preise", "cls": "tint", "eb": "Preise", "h2": "Transparente Preise", "p": "Alle Preise inklusive Waschen, Beratung und Styling. Für sehr langes Haar kann ein Aufschlag anfallen.", "rows": [
    ("Damenschnitt", "Waschen, Schnitt, Föhnen", "ab 54 €"), ("Herrenschnitt", "Waschen, Schnitt, Styling", "32 €"), ("Ansatzfarbe", "inkl. Schnitt", "ab 89 €"),
    ("Balayage", "inkl. Glossing und Schnitt", "ab 169 €"), ("Olaplex-Treatment", "als Zusatz", "29 €"), ("Kinder bis 12 Jahre", "", "22 €")],
    "side": '<div class="card"><h3>Neu bei uns?</h3><p>Beim ersten Termin nehmen wir uns 15 Minuten extra für die Beratung – ohne Aufpreis.</p><a class="btn" style="margin-top:18px" href="#kontakt">Ersttermin buchen</a></div>'}),
  ("team", {"id": "team", "eb": "Team", "h2": "Die Menschen hinter dem Spiegel", "people": [
    ("S", "Sabine Kante", "Inhaberin · Farbe &amp; Balayage", "#b5705f"), ("M", "Mila Roth", "Schnitt &amp; Kurzhaar", "#7c5a50"), ("J", "Jonas Peh", "Herren &amp; Barber · samstags", "#3b302d")]}),
  ("quotes", {"cls": "tint", "eb": "Stimmen", "h2": "Was Kundinnen sagen", "p": "Beispieltexte für die Vorschau.", "items": [
    ("Endlich ein Salon, in dem man sich nicht abgefertigt fühlt. Die Farbe ist genau so geworden, wie ich sie wollte.", "Lea M.", "Balayage"),
    ("Online gebucht, pünktlich drangekommen, toller Schnitt. Komme wieder.", "Tim K.", "Herrenschnitt"),
    ("Sabine hat mir ehrlich gesagt, was zu meinem Haar passt – und was nicht. Genau das habe ich gesucht.", "Jana R.", "Schnitt &amp; Pflege")]}),
  ("faq", {"eb": "Fragen", "h2": "Gut zu wissen", "items": [
    ("Kann ich auch ohne Termin kommen?", "Wir arbeiten nur mit Termin, damit niemand warten muss. Kurzfristige Lücken sehen Sie online."),
    ("Wie kurzfristig kann ich absagen?", "Bis 24 Stunden vorher kostenlos – einfach über den Link in der Bestätigung."),
    ("Welche Farben verwenden Sie?", "Vegane, ammoniakarme Farben und Olaplex für den Schutz der Haarstruktur."),
    ("Kann ich mit Karte zahlen?", "Ja, mit EC-Karte, Kreditkarte, Apple Pay und Google Pay.")]}),
  ("contact", {"eb": "Termin", "h2": "In 30 Sekunden zum Termin", "p": "Wählen Sie Leistung und Zeit – die Bestätigung kommt per SMS.", "form": "termin",
    "info": [("map", "Marktstraße 8, Musterstadt", "Parkplätze im Hof, Bus 4 bis Marktplatz"), ("clock", "Öffnungszeiten", "Di–Fr 9–19 Uhr · Sa 8–15 Uhr"), ("phone", "0123 456 789", "Lieber telefonisch? Gern zu den Öffnungszeiten.")]}),
 ],
 "footer": {"about": "Friseursalon für Schnitt und Farbe. Zwei Stühle, viel Zeit, ehrliche Beratung.", "cols": [("Salon", ["Marktstraße 8", "12345 Musterstadt", "0123 456 789"]), ("Öffnungszeiten", ["Di–Fr 9–19 Uhr", "Sa 8–15 Uhr", "So/Mo geschlossen"]), ("Mehr", ["Gutscheine", "Impressum", "Datenschutz"])]},
 "mbar": [("Termin buchen", "#kontakt"), ("Anrufen", "#kontakt")],
}

DEMOS["barber"] = {
 "hero_foto": (3998417, "Barber schneidet einem Kunden den Bart"),
 "name": "Blackline Barbers", "branche": "Barbershop", "claim": "Barbershop · Est. 2019", "mark": "BL", "art": "barber",
 "fonts": [("Archivo", "archivo"), ("Inter", "inter")],
 "vars": {"bg": "#111214", "bg2": "#18191c", "card": "#1c1d21", "ink": "#f2efe9", "muted": "#a7a29a", "line": "#2c2d32", "brand": "#c8a165", "brand-ink": "#111214",
          "accent": "#c8a165", "soft": "#2a2620", "display": "Archivo,Inter,sans-serif", "body": "Inter,system-ui,sans-serif", "dw": "800", "dls": "-.02em", "br": "4px", "mr": "4px", "cr": "8px", "rr": "10px",
          "strip": "#c8a165", "strip-ink": "#111214", "dark": "#18191c", "dark-ink": "#f2efe9", "ft": "#0a0a0b", "stage": "#141518", "star": "#c8a165"},
 "strip": ["Di–Fr 10–20 Uhr · Sa 9–18 Uhr", "Termine online – Walk-ins wenn frei", '<span class="stars">★★★★★</span> 4,9 bei Google (Beispiel)'],
 "nav": [("Services", "#leistungen"), ("Preise", "#preise"), ("Barber", "#team"), ("Shop", "#shop")], "cta": ("Jetzt buchen", "#kontakt"),
 "hero": {"eb": "Barbershop im Szeneviertel", "h1": "Saubere Fades. Scharfe Konturen. Kein Warten.",
          "lead": "Haare, Bart und Rasur bei drei Barbern, die ihr Handwerk lieben. Buch deinen Slot online – und sitz pünktlich im Stuhl.",
          "ctas": [("Slot buchen", "#kontakt"), ("Preise", "#preise")],
          "chips": ['<span class="stars">★★★★★</span> <b>4,9</b> · 412 Bewertungen', "Fade ab 32 €", "Heißtuch-Rasur"],
          "floats": fl("left:-16px;top:40px;width:240px", "<h4>Heute frei bei Can</h4><div class='slots'><i>16:00</i><i class='on'>17:30</i><i>19:00</i></div>")
                  + fl("right:-14px;bottom:36px;width:230px", "<h4>Haare + Bart</h4><div class='k'>49 €</div><span class='muted'>inkl. Heißtuch &amp; Styling</span>")},
 "sections": [
  ("strip", {"fotos": [(12304508, "Fade-Haarschnitt mit der Maschine"), (897265, "Klassische Rasur im Barbershop"), (9992819, "Bärtiger Kunde im Barbershop")], "cap": "Skin Fade, Taper, Bart in Form, Rasur mit dem Messer."}),
  ("services", {"id": "leistungen", "eb": "Services", "h2": "Was wir machen", "cols": 3, "items": [
    ("scissors", "Haarschnitt &amp; Fade", "Skin Fade, Taper oder klassischer Schnitt – mit Waschen und Styling.", "ab", "32 €"),
    ("spark", "Bart in Form", "Konturen mit dem Messer, Länge mit der Maschine, Pflege mit Öl und Balm.", "ab", "22 €"),
    ("drop", "Heißtuch-Rasur", "Die klassische Nassrasur mit heißen Tüchern und Messer. Zeit für dich.", "", "35 €")]}),
  ("prices", {"id": "preise", "cls": "tint", "eb": "Preise", "h2": "Klare Preise. Keine Überraschungen.", "rows": [
    ("Haarschnitt / Fade", "inkl. Waschen &amp; Styling", "32 €"), ("Haare + Bart", "inkl. Heißtuch", "49 €"), ("Bart trimmen &amp; Konturen", "", "22 €"),
    ("Heißtuch-Rasur", "mit Messer", "35 €"), ("Kids bis 12", "", "22 €"), ("Konturen nachziehen", "zwischen zwei Terminen", "12 €")],
    "side": '<div class="card"><h3>Stammkunden-Abo</h3><p>Zwei Schnitte im Monat zum Festpreis von 59 € – fester Slot bei deinem Barber inklusive.</p><a class="btn" style="margin-top:18px" href="#kontakt">Abo anfragen</a></div>'}),
  ("split", {"id": "shop", "eb": "Der Shop", "h2": "Drei Stühle. Gute Musik. Kein Fließband.", "p": "Jeder Termin hat 30 Minuten – genug Zeit für einen sauberen Übergang und ein kurzes Gespräch. Kaffee oder ein kaltes Getränk gibt es dazu.",
    "fotos": [(2318055, "Kunden im Barbershop"), (6007400, "Bartpflege mit dem Rasiermesser"), (3998421, "Barber bei der Arbeit"), (7697316, "Goldenes Rasiermesser")],
    "list": ["Termine pro Barber buchbar", "Erinnerung per SMS", "Kartenzahlung &amp; Apple Pay"], "cta": ("Slot buchen", "#kontakt"),
    "vis": '<div class="card"><h3>Walk-ins?</h3><p>Gerne, wenn ein Stuhl frei ist. Freie Slots siehst du online in Echtzeit.</p></div>'}),
  ("team", {"id": "team", "cls": "tint", "eb": "Barber", "h2": "Wähl deinen Barber", "people": [
    ("C", "Can", "Inhaber · Skin Fades &amp; Rasur", "#c8a165"), ("D", "Dario", "Taper &amp; Texturen", "#3a3b40"), ("L", "Lukas", "Bart &amp; Klassiker · Sa", "#6b5a3c")]}),
  ("quotes", {"eb": "Stimmen", "h2": "Was Kunden sagen", "p": "Beispieltexte für die Vorschau.", "items": [
    ("Bester Fade in der Gegend. Online gebucht, null Wartezeit, Can ist ein Künstler.", "Murat K.", "Skin Fade"),
    ("Die Heißtuch-Rasur ist pure Entspannung. Komme jetzt alle drei Wochen.", "Jonas B.", "Rasur"),
    ("Endlich ein Barber, bei dem der Bart nicht schief wird. Klare Preise, gute Vibes.", "Ali S.", "Haare + Bart")]}),
  ("contact", {"eb": "Buchen", "h2": "Slot sichern in 20 Sekunden", "p": "Wähl Service und Uhrzeit – Bestätigung kommt per SMS.", "form": "termin", "optionen": ["Haarschnitt / Fade", "Haare + Bart", "Bart trimmen", "Heißtuch-Rasur"],
    "info": [("map", "Kiezstraße 21, Musterstadt", "Zwei Minuten von der U-Bahn"), ("clock", "Di–Fr 10–20 · Sa 9–18 Uhr", "So/Mo geschlossen"), ("phone", "0123 456 789", "Lieber per WhatsApp? Gleiche Nummer.")]}),
 ],
 "footer": {"about": "Barbershop für Fades, Bärte und klassische Rasuren. Drei Stühle, keine Wartezeit mit Termin.", "cols": [("Shop", ["Kiezstraße 21", "12345 Musterstadt", "0123 456 789"]), ("Öffnungszeiten", ["Di–Fr 10–20 Uhr", "Sa 9–18 Uhr", "So/Mo geschlossen"]), ("Mehr", ["Gutscheine", "Impressum", "Datenschutz"])]},
 "mbar": [("Slot buchen", "#kontakt"), ("WhatsApp", "#kontakt")],
}

DEMOS["dachdecker-solar"] = {
 "hero_foto": (35237908, "Handwerker montiert Solarmodule auf einem Hausdach"),
 "name": "Brandt Bedachungen", "branche": "Dachdecker &amp; Solar", "claim": "Meisterbetrieb seit 1987", "mark": "B", "art": "dach",
 "fonts": [("Archivo", "archivo"), ("Inter", "inter")],
 "vars": {"bg": "#ffffff", "bg2": "#f2f4f6", "card": "#ffffff", "ink": "#151c23", "muted": "#58626c", "line": "#dfe4e9", "brand": "#e8692b", "brand-ink": "#ffffff", "accent": "#e8692b",
          "soft": "#fdebe1", "display": "Archivo,Inter,sans-serif", "body": "Inter,system-ui,sans-serif", "dw": "800", "dls": "-.025em", "br": "10px", "mr": "8px", "cr": "14px", "rr": "18px", "strip": "#e8692b", "dark": "#151c23", "ft": "#0f151b", "stage": "#151c23"},
 "strip": ['<i class="live"></i> <b>24/7 Notdienst: 0123 456 789</b>', "Meisterbetrieb · Innungsmitglied", "Einsatzgebiet 30 km um Musterstadt"],
 "nav": [("Leistungen", "#leistungen"), ("Photovoltaik", "#pv"), ("Referenzen", "#referenzen"), ("Ablauf", "#ablauf"), ("Karriere", "#karriere")], "cta": ("Angebot anfordern", "#kontakt"),
 "hero": {"eb": "Dachdecker-Meisterbetrieb · Musterstadt &amp; Umgebung", "h1": "Ein dichtes Dach. Und Strom vom eigenen.",
          "lead": "Dachsanierung, Reparatur und Photovoltaik aus einer Hand – vom eigenen Team, mit Festpreis-Angebot und einem Ansprechpartner von der Besichtigung bis zur Abnahme.",
          "ctas": [("Kostenlose Ersteinschätzung", "#kontakt"), ("Notdienst anrufen", "#kontakt")],
          "chips": ['<span class="stars">★★★★★</span> <b>4,9</b> · 126 Bewertungen', "<b>1.400+</b> Dächer seit 1987", "Festpreis-Angebot in 5 Tagen"],
          "floats": fl("left:-16px;top:40px;width:230px", "<h4 style='color:var(--brand)'>● Sturmschaden?</h4><div class='k'>60 Min.</div><span class='muted'>Durchschnittliche Anfahrt im Notdienst</span>")
                  + fl("right:-14px;bottom:36px;width:250px", "<h4>Dach + PV aus einer Hand</h4><span class='muted'>Ein Gerüst, ein Termin, ein Ansprechpartner – spart bis zu 15 % gegenüber getrennter Vergabe.</span>")},
 "sections": [
  ("stats", {"items": [("37 Jahre", "Meisterbetrieb in zweiter Generation"), ("1.400+", "sanierte Dächer im Landkreis"), ("320", "Photovoltaik-Anlagen montiert"), ("10 Jahre", "Gewährleistung auf Dacharbeiten")]}),
  ("strip", {"fotos": [(33404248, "Dachdecker deckt ein neues Dach"), (9875419, "Montage eines Solarmoduls"), (9729882, "Solarmodule auf einem Altbau")], "cap": "Aus unseren Projekten: Neueindeckung, PV-Montage, Altbausanierung."}),
  ("services", {"id": "leistungen", "eb": "Leistungen", "h2": "Alles rund ums Dach", "p": "Vom Ziegel bis zur Solaranlage – vom eigenen Team, nicht von Subunternehmern.", "cols": 3, "items": [
    ("home", "Dachsanierung", "Neueindeckung, Dämmung nach GEG und neue Dachfenster – mit Förderberatung."),
    ("sun", "Photovoltaik &amp; Speicher", "Planung, Montage und Anmeldung – ideal in Kombination mit der Sanierung."),
    ("wrench", "Reparatur &amp; Notdienst", "Sturmschäden, undichte Stellen, Dachrinnen – 24 Stunden erreichbar."),
    ("shield", "Flachdach", "Abdichtung mit Bitumen oder Kunststoff, Gründächer und Wartung."),
    ("drop", "Klempnerarbeiten", "Dachrinnen, Fallrohre und Kaminverkleidungen aus Zink und Kupfer."),
    ("file", "Förderung &amp; Gutachten", "Wir kümmern uns um BAFA- und KfW-Anträge und die Unterlagen für Ihre Versicherung.")]}),
  ("split", {"id": "pv", "cls": "dark", "eb": "Photovoltaik", "h2": "Dach neu? Dann gleich mit Solar.", "p": "Wer saniert, steht schon auf dem Gerüst. Wir planen Dach und Anlage zusammen – das spart Gerüstkosten, Termine und Abstimmung zwischen Gewerken.",
    "vis_foto": (12243093, "Wohnhaus mit Solaranlage auf dem Dach"), "overlay": True,
    "list": ["Ertragsprognose für Ihr Dach in 48 Stunden", "Speicher und Wallbox auf Wunsch", "Anmeldung beim Netzbetreiber inklusive"], "cta": ("PV-Check anfordern", "#kontakt"),
    "vis": '<div class="card" style="padding:34px"><span class="eyebrow">Beispielrechnung</span><h3 style="font-size:1.6rem">Einfamilienhaus, 9,8 kWp</h3><table class="tbl" style="margin-top:14px;background:transparent;border-color:rgba(255,255,255,.15)"><tbody><tr><td>Jahresertrag</td><td class="r">ca. 9.300 kWh</td></tr><tr><td>Eigenverbrauch mit Speicher</td><td class="r">ca. 65 %</td></tr><tr><td>Ersparnis pro Jahr</td><td class="r">ca. 1.900 €</td></tr></tbody></table><p style="margin-top:12px;font-size:.85rem">Unverbindliche Beispielwerte, abhängig von Ausrichtung und Verbrauch.</p></div>'}),
  ("tags", {"id": "referenzen", "eb": "Referenzen", "h2": "40 Projekte allein im letzten Jahr", "p": "Fragen Sie Ihre Nachbarn – gut möglich, dass wir dort schon waren.",
    "items": ["Musterstadt", "Nordheim", "Altdorf", "Bergen", "Lindau-Süd", "Wiesental", "Kirchberg", "Am See", "Feldkirchen", "Oberau"], "vis": f'<div class="mapbox">{mappins()}</div>'}),
  ("steps", {"id": "ablauf", "cls": "tint", "eb": "Ablauf", "h2": "In fünf Schritten zum neuen Dach", "items": [
    ("Anfrage", "Fotos schicken oder anrufen – Rückruf innerhalb von 24 Stunden."), ("Besichtigung", "Kostenlos vor Ort, mit Drohnenaufnahme des Daches."),
    ("Festpreis-Angebot", "Innerhalb von fünf Werktagen, inklusive Förderprüfung."), ("Ausführung", "Eigenes Team, feste Bauleitung, tägliches Aufräumen."), ("Abnahme", "Gemeinsamer Rundgang, Fotodokumentation, 10 Jahre Gewährleistung.")]}),
  ("quotes", {"eb": "Stimmen", "h2": "Was Bauherren sagen", "p": "Beispieltexte für die Vorschau.", "items": [
    ("Nach dem Sturm waren sie in einer Stunde da und haben provisorisch abgedichtet. Zwei Wochen später war das Dach komplett neu.", "Familie Özdemir", "Notdienst &amp; Sanierung"),
    ("Dach und Solaranlage in einem Rutsch, ein Ansprechpartner, Festpreis eingehalten. So muss das laufen.", "Peter W.", "Sanierung + PV 11 kWp"),
    ("Saubere Baustelle, freundliche Leute, und um die Förderung haben sie sich auch gekümmert.", "Anja L.", "Dachdämmung")]}),
  ("split", {"id": "karriere", "cls": "tint", "rev": True, "eb": "Karriere", "h2": "Wir suchen Dachdecker:innen", "p": "Unbefristet, übertariflich, mit eigenem Firmenwagen ab dem ersten Tag. Bewerbung per WhatsApp oder in zwei Minuten online.",
    "list": ["4-Tage-Woche im Winter möglich", "Moderne Ausrüstung und Kran", "Weiterbildung zum Meister wird unterstützt"], "cta": ("Jetzt bewerben", "#kontakt"),
    "vis": '<div class="card" style="padding:34px"><span class="eyebrow">Offene Stellen</span><h3>Dachdecker:in (Geselle)</h3><p>Vollzeit · ab sofort</p><hr style="border:0;border-top:1px solid var(--line);margin:18px 0"><h3>PV-Monteur:in</h3><p>Vollzeit · Quereinstieg möglich</p><hr style="border:0;border-top:1px solid var(--line);margin:18px 0"><h3>Ausbildung Dachdecker:in</h3><p>Start 1. August</p></div>'}),
  ("contact", {"cls": "", "eb": "Kontakt", "h2": "Fotos schicken, Einschätzung bekommen", "p": "Für viele Fragen reicht ein Handyfoto. Wir melden uns innerhalb von 24 Stunden – im Notfall sofort.", "form": "anfrage",
    "info": [("phone", "Notdienst 24/7: 0123 456 789", "Sturm, Wasser, Schäden – rund um die Uhr"), ("map", "Gewerbering 4, Musterstadt", "Einsatzgebiet: 30 km Umkreis"), ("clock", "Büro", "Mo–Fr 7–17 Uhr")]}),
 ],
 "footer": {"about": "Dachdecker-Meisterbetrieb seit 1987. Dachsanierung, Reparatur, Flachdach und Photovoltaik aus einer Hand.", "cols": [("Kontakt", ["Gewerbering 4", "12345 Musterstadt", "Notdienst 0123 456 789"]), ("Leistungen", ["Dachsanierung", "Photovoltaik", "Reparatur", "Flachdach"]), ("Unternehmen", ["Referenzen", "Karriere", "Impressum"])]},
 "mbar": [("Anfrage", "#kontakt"), ("Notdienst", "#kontakt")],
}

DEMOS["steuerberater"] = {
 "hero_foto": (7433848, "Beratungsgespräch in einem hellen Büro"),
 "name": "Kanzlei Weidner", "branche": "Steuerberatung", "claim": "Steuerberatung für das Handwerk", "mark": "W", "art": "steuer",
 "fonts": [("Instrument Serif", "instrument"), ("DM Sans", "dmsans")],
 "vars": {"bg": "#f8f7f4", "bg2": "#efece5", "card": "#ffffff", "ink": "#14233c", "muted": "#5b6577", "line": "#e1ddd3", "brand": "#14233c", "brand-ink": "#f8f7f4", "accent": "#a8834b",
          "soft": "#ece4d5", "display": '"Instrument Serif",Georgia,serif', "body": '"DM Sans",system-ui,sans-serif', "dw": "400", "dls": "-.01em", "br": "6px", "mr": "4px", "cr": "8px", "rr": "8px", "strip": "#14233c", "dark": "#14233c", "ft": "#0d1829"},
 "strip": ["Wir nehmen aktuell neue Mandate aus dem Handwerk an", "Mo–Do 8–17 · Fr 8–14 Uhr", "0123 456 789"],
 "nav": [("Für Handwerker", "#handwerk"), ("Leistungen", "#leistungen"), ("Kanzleiwechsel", "#wechsel"), ("Team", "#team"), ("Karriere", "#karriere")], "cta": ("Erstgespräch buchen", "#kontakt"),
 "hero": {"eb": "Steuerberatung · Musterstadt", "h1": "Ihr Handwerk läuft. Wir sorgen dafür, dass die Zahlen mitlaufen.",
          "lead": "Wir betreuen über 140 Handwerksbetriebe – mit monatlichen Zahlen, die Sie verstehen, festen Ansprechpartnern und Antworten innerhalb von 24 Stunden.",
          "ctas": [("20-Minuten-Erstgespräch", "#kontakt"), ("So läuft der Wechsel", "#wechsel")],
          "chips": ["<b>140+</b> Handwerksbetriebe", "DATEV-Digitalkanzlei", "Fachberater für Unternehmensnachfolge"],
          "floats": fl("left:-18px;top:46px;width:250px", "<h4>Ihre Monatszahlen</h4><div class='k' style='font-family:var(--body);font-weight:700'>+12,4 %</div><span class='muted'>Rohertrag ggü. Vorjahr – jeden Monat im Postfach.</span>")
                  + fl("right:-12px;bottom:36px;width:240px", "<h4>Nächster freier Termin</h4><div class='slots'><i class='on'>Mi 10:00</i><i>Do 17:30</i></div><span class='muted' style='display:block;margin-top:8px'>Erstgespräch per Video</span>")},
 "sections": [
  ("split", {"id": "handwerk", "eb": "Für wen wir arbeiten", "h2": "Spezialisiert auf Handwerk und Bau", "p": "Wir kennen die Fragen, die Sie nachts wachhalten: Liquidität bei langen Zahlungszielen, Abschlagsrechnungen, Fahrzeugflotte, Nachfolge. Deshalb beraten wir fast ausschließlich Handwerksbetriebe.",
    "vis_foto": (18947396, "Tischler in seiner Werkstatt"), "overlay": True,
    "list": ["Maler, Elektro, SHK, Dach, Tischler, Bau", "5 bis 80 Mitarbeitende", "Inhabergeführt, regional verwurzelt"], "cta": ("Passt das zu Ihnen?", "#kontakt"),
    "vis": '<div class="card" style="padding:36px;border-left:3px solid var(--accent)"><p style="font:400 1.7rem/1.35 var(--display);color:var(--ink);margin:0">„Wir nehmen nur so viele Mandate an, wie wir gut betreuen können. Aktuell haben wir Kapazität für vier neue Handwerksbetriebe.“</p><p style="margin-top:18px">— Dr. Martin Weidner, Steuerberater</p></div>'}),
  ("services", {"id": "leistungen", "cls": "tint", "eb": "Leistungen", "h2": "Mehr als Belege buchen", "cols": 3, "items": [
    ("file", "Finanz- und Lohnbuchhaltung", "Digital mit DATEV Unternehmen online. Belege per App – kein Pendelordner mehr."),
    ("chart", "Monatliches Controlling", "Eine Seite, fünf Kennzahlen, ein kurzer Kommentar. Damit Sie früh gegensteuern können."),
    ("brief", "Jahresabschluss &amp; Steuern", "Bilanz, Steuererklärungen und Gestaltung – vorausschauend statt rückblickend."),
    ("users", "Lohn &amp; Personal", "Lohnabrechnung, Baulohn, SOKA-BAU, Dienstwagen und Mitarbeiter-Benefits."),
    ("shield", "Betriebsprüfung", "Vorbereitung, Begleitung und klare Kommunikation mit dem Finanzamt."),
    ("hand", "Nachfolge &amp; Übergabe", "Bewertung, Übergabeplanung und steuerlich sinnvolle Gestaltung.")]}),
  ("steps", {"id": "wechsel", "eb": "Kanzleiwechsel", "h2": "Der Wechsel ist einfacher als gedacht", "p": "Wir übernehmen die Kommunikation mit Ihrer bisherigen Kanzlei. Sie unterschreiben, wir erledigen den Rest.", "items": [
    ("Erstgespräch", "20 Minuten, kostenlos. Wir klären, ob wir zueinander passen."), ("Angebot", "Transparentes Honorar nach StBVV, fest pro Monat."),
    ("Übergabe", "Wir fordern Daten und Unterlagen bei Ihrer alten Kanzlei an."), ("Einrichtung", "Digitale Belegübermittlung, Zugänge, feste Ansprechpartnerin."),
    ("Start", "Erste Monatsauswertung nach vier bis sechs Wochen.")]}),
  ("stats", {"items": [("24 h", "Antwortzeit auf Ihre Fragen"), ("140+", "Handwerksbetriebe in der Betreuung"), ("100 %", "digitale Belegverarbeitung"), ("1", "feste Ansprechpartnerin für Sie")]}),
  ("team", {"id": "team", "cls": "tint", "eb": "Team", "h2": "Ihre Ansprechpartner", "people": [
    ("MW", "Dr. Martin Weidner", "Steuerberater · Gründer", "#14233c"), ("SK", "Sandra Kühn", "Steuerberaterin · Bau &amp; SHK", "#2b4066"),
    ("AT", "Ali Tekin", "Bilanzbuchhalter", "#a8834b"), ("LB", "Lena Brandt", "Lohn &amp; Baulohn", "#5b6577")]}),
  ("split", {"id": "karriere", "cls": "dark", "eb": "Karriere", "h2": "Steuerfachangestellte gesucht", "p": "Flexible Arbeitszeiten, zwei Homeoffice-Tage, Mandanten aus dem Handwerk statt anonymer Masse. Bewerbung ohne Anschreiben in drei Minuten.",
    "vis_foto": (36733323, "Team bei einer Besprechung im Büro"), "overlay": True,
    "list": ["4-Tage-Woche möglich", "Fortbildung zum Steuerfachwirt bezahlt", "Moderne, voll digitale Kanzlei"], "cta": ("Offene Stellen", "#kontakt"),
    "vis": '<div class="card" style="padding:34px"><span class="eyebrow">Aus dem Team</span><p style="font:400 1.45rem/1.4 var(--display);margin:0;color:#fff">„Ich weiß bei jedem Mandanten, was er baut. Das macht die Arbeit viel greifbarer.“</p><p style="margin-top:14px">— Lena, seit 2021 bei uns</p></div>'}),
  ("faq", {"eb": "Fragen", "h2": "Häufige Fragen", "items": [
    ("Was kostet die Betreuung?", "Das Honorar richtet sich nach der Steuerberatervergütungsverordnung. Wir vereinbaren einen festen Monatsbetrag – ohne Überraschungen."),
    ("Wie lange dauert ein Kanzleiwechsel?", "In der Regel vier bis sechs Wochen. Zum Jahreswechsel ist es besonders einfach."),
    ("Muss ich vorbeikommen?", "Nein. Wir arbeiten digital, Gespräche gern per Video. Persönlich sind wir natürlich auch für Sie da."),
    ("Betreuen Sie auch Gründer?", "Ja, wenn Sie im Handwerk gründen oder einen Betrieb übernehmen.")]}),
  ("contact", {"eb": "Erstgespräch", "h2": "Lernen wir uns kennen", "p": "Im Erstgespräch klären wir, wo Sie stehen und ob wir der richtige Partner sind – ehrlich und ohne Verkaufsdruck.", "form": "erstgespraech",
    "info": [("map", "Am Rathausplatz 3, Musterstadt", "Parkhaus gegenüber"), ("phone", "0123 456 789", "Mo–Do 8–17 · Fr 8–14 Uhr"), ("chat", "Antwort binnen 24 Stunden", "Für Mandanten garantiert")]}),
 ],
 "footer": {"about": "Steuerberatung für Handwerk und Bau. Digital, persönlich, vorausschauend.", "cols": [("Kanzlei", ["Am Rathausplatz 3", "12345 Musterstadt", "0123 456 789"]), ("Leistungen", ["Buchhaltung", "Controlling", "Jahresabschluss", "Nachfolge"]), ("Mehr", ["Karriere", "Impressum", "Datenschutz"])]},
 "mbar": [("Erstgespräch", "#kontakt"), ("Anrufen", "#kontakt")],
}

DEMOS["pflegedienst"] = {
 "hero_foto": (18459198, "Pflegekraft unterstützt ältere Menschen"),
 "name": "Pflege am Lindenhof", "branche": "Ambulante Pflege", "claim": "Ambulanter Pflegedienst", "mark": "L", "art": "pflege",
 "fonts": [("Fraunces", "fraunces"), ("Figtree", "figtree")],
 "vars": {"bg": "#fbf8f2", "bg2": "#f1ece1", "card": "#ffffff", "ink": "#1f2e27", "muted": "#5d6b64", "line": "#e2dccf", "brand": "#3f7d5c", "brand-ink": "#ffffff", "accent": "#e07a4f",
          "accent-ink": "#ffffff", "soft": "#e3efe7", "display": "Fraunces,Georgia,serif", "body": "Figtree,system-ui,sans-serif", "dw": "600", "cr": "24px", "rr": "32px", "strip": "#2f6248", "dark": "#2f6248", "ft": "#1f2e27"},
 "strip": ["Pflegeberatung: 0123 456 789", "Mo–Fr 8–17 Uhr · Rufbereitschaft 24/7", "Alle Kassen · Zugelassen nach § 72 SGB XI"],
 "nav": [("Leistungen", "#leistungen"), ("Kosten", "#kosten"), ("Karriere", "#karriere"), ("Über uns", "#team")], "cta": ("Beratung anfragen", "#kontakt"),
 "hero": {"eb": "Ambulante Pflege in Musterstadt &amp; Umland", "h1": "Zuhause gut versorgt. Mit Menschen, die Zeit haben.",
          "lead": "Wir pflegen, wo Sie sich am wohlsten fühlen – mit festen Bezugspflegekräften, verlässlichen Zeiten und Hilfe bei allen Anträgen.",
          "ctas": [("Ich suche Pflege", "#kontakt"), ("Ich suche einen Job", "#karriere")],
          "chips": ['<span class="stars">★★★★★</span> <b>4,8</b> bei Google', "Alle Kassen", "Freie Kapazitäten in 4 Orten"],
          "floats": fl("left:-16px;top:40px;width:240px", "<h4>Rückruf heute noch</h4><span class='muted'>Anfragen bis 15 Uhr beantworten wir am selben Tag.</span>")
                  + fl("right:-14px;bottom:40px;width:250px;border-left:4px solid var(--accent)", "<h4 style='color:var(--accent)'>Wir stellen ein</h4><b>Bewerbung in 60 Sekunden</b><br><span class='muted'>Ohne Lebenslauf, Rückruf in 48 h</span>")},
 "sections": [
  ("paths", {"items": [("Für Angehörige", "Pflege organisieren", "Was steht uns zu, was kostet das, wie schnell geht es? Wir beraten kostenlos und kommen zum Erstbesuch nach Hause.", "#kontakt", "#e3efe7", "#1f2e27"),
                       ("Für Pflegekräfte", "Arbeiten mit Zeit für Menschen", "Feste Touren, Dienstwagen auch privat, 30 Tage Urlaub. Bewerbung in 60 Sekunden – ohne Lebenslauf.", "#karriere", "#e07a4f", "#ffffff")]}),
  ("services", {"id": "leistungen", "eb": "Leistungen", "h2": "Was wir für Sie tun", "p": "Alle Leistungen rechnen wir direkt mit Pflege- und Krankenkasse ab.", "cols": 3, "items": [
    ("hand", "Grundpflege", "Hilfe beim Waschen, Anziehen, Essen und Bewegen – würdevoll und in Ihrem Tempo."),
    ("steth", "Behandlungspflege", "Medikamente, Wundversorgung, Injektionen und Verbände nach ärztlicher Verordnung."),
    ("home", "Hauswirtschaft", "Einkaufen, Kochen, Wäsche und Ordnung – damit der Alltag leichter wird."),
    ("users", "Verhinderungspflege", "Entlastung für pflegende Angehörige – stundenweise oder mehrere Tage."),
    ("chat", "Pflegeberatung § 37.3", "Die Pflichtberatung für Pflegegeldempfänger – auf Wunsch auch bei Ihnen zu Hause."),
    ("file", "Hilfe bei Anträgen", "Pflegegrad beantragen, Widerspruch, Hilfsmittel – wir unterstützen Sie Schritt für Schritt.")]}),
  ("strip", {"fotos": [(271353, "Pflegekraft hält die Hand einer älteren Frau"), (8460373, "Lächelnde Pflegekraft in Dienstkleidung")]}),
  ("prices", {"id": "kosten", "cls": "tint", "eb": "Kosten", "h2": "Was kostet ambulante Pflege?", "p": "Die Pflegekasse übernimmt je nach Pflegegrad einen festen Betrag pro Monat (Pflegesachleistung). Wir erstellen Ihnen vorab einen kostenlosen Kostenvoranschlag.", "rows": [
    ("Pflegegrad 2", "Pflegesachleistung pro Monat", "bis 796 €"), ("Pflegegrad 3", "Pflegesachleistung pro Monat", "bis 1.497 €"), ("Pflegegrad 4", "Pflegesachleistung pro Monat", "bis 1.859 €"),
    ("Pflegegrad 5", "Pflegesachleistung pro Monat", "bis 2.299 €"), ("Entlastungsbetrag", "ab Pflegegrad 1, zusätzlich", "131 €")],
    "note": "Beispielwerte zur Orientierung, Stand 2026. Maßgeblich sind die aktuellen gesetzlichen Beträge.",
    "side": '<div class="card"><h3>Noch kein Pflegegrad?</h3><p>Wir helfen beim Antrag und bereiten Sie auf den Besuch des Medizinischen Dienstes vor. Das ist kostenlos.</p><a class="btn" style="margin-top:18px" href="#kontakt">Beratung anfragen</a></div>'}),
  ("split", {"id": "karriere", "cls": "dark", "eb": "Karriere", "h2": "Pflege, wie du sie gelernt hast", "p": "Bei uns hast du feste Patienten statt ständig neuer Gesichter, planbare Dienste und ein Team, das zusammenhält. Bewirb dich in 60 Sekunden – wir rufen dich an.",
    "list": ["3.900–4.400 € für Pflegefachkräfte (Vollzeit)", "Dienstwagen, auch privat nutzbar", "Wunschdienstplan und 30 Tage Urlaub", "Keine geteilten Dienste"],
    "vis": f'<div class="form">{FORMS["bewerbung"]({})}</div>'}),
  ("team", {"id": "team", "eb": "Über uns", "h2": "Ein Team aus der Region", "p": "28 Mitarbeitende, vier Touren, ein Ziel: dass Sie zu Hause bleiben können.", "people": [
    ("AH", "Anke Hoffmann", "Pflegedienstleitung", "#3f7d5c"), ("DK", "Daniela Kurz", "Pflegefachkraft · Wundexpertin", "#2f6248"), ("MS", "Murat Sahin", "Pflegefachkraft · Tourenleitung", "#e07a4f"), ("EB", "Elke Bauer", "Verwaltung &amp; Abrechnung", "#5d6b64")]}),
  ("faq", {"cls": "tint", "eb": "Fragen", "h2": "Häufige Fragen von Angehörigen", "items": [
    ("Wie schnell kann die Pflege starten?", "Bei freien Kapazitäten oft innerhalb einer Woche. Nach dem Erstgespräch kommen wir zum kostenlosen Erstbesuch."),
    ("In welchen Orten sind Sie unterwegs?", "Musterstadt, Nordheim, Altdorf und Bergen. Fragen Sie gern auch für angrenzende Orte."),
    ("Was zahlen wir selbst?", "Das hängt vom Pflegegrad und den Leistungen ab. Sie erhalten vorab einen kostenlosen Kostenvoranschlag."),
    ("Kommt immer dieselbe Pflegekraft?", "Wir arbeiten mit festen Bezugspflegekräften. Urlaubsvertretungen kündigen wir vorher an.")]}),
  ("contact", {"eb": "Beratung", "h2": "Wir rufen Sie zurück", "p": "Erzählen Sie uns kurz, worum es geht. Anfragen bis 15 Uhr beantworten wir am selben Tag.", "form": "rueckruf",
    "info": [("phone", "0123 456 789", "Mo–Fr 8–17 Uhr, sonst Rufbereitschaft"), ("map", "Lindenallee 12, Musterstadt", "Büro und Beratung"), ("car", "Einsatzgebiet", "Musterstadt, Nordheim, Altdorf, Bergen")]}),
 ],
 "footer": {"about": "Ambulanter Pflegedienst für Musterstadt und Umland. Zugelassen bei allen Kassen.", "cols": [("Kontakt", ["Lindenallee 12", "12345 Musterstadt", "0123 456 789"]), ("Leistungen", ["Grundpflege", "Behandlungspflege", "Hauswirtschaft", "Beratung"]), ("Mehr", ["Karriere", "Impressum", "Datenschutz"])]},
 "mbar": [("Beratung", "#kontakt"), ("Jobs", "#karriere")],
}

DEMOS["bestatter"] = {
 "hero_foto": (8986709, "Strauß weißer Blumen"),
 "name": "Bestattungen Hollmann", "branche": "Bestattungen", "claim": "Familienbetrieb seit 1952", "mark": "H", "art": "bestatter",
 "fonts": [("Cormorant Garamond", "cormorant"), ("Inter", "inter")],
 "vars": {"bg": "#f6f4f0", "bg2": "#ece8e1", "card": "#fdfcfa", "ink": "#22272b", "muted": "#61666a", "line": "#ddd7cd", "brand": "#22272b", "brand-ink": "#f6f4f0", "accent": "#9a7d4c",
          "soft": "#ece4d6", "display": '"Cormorant Garamond",Georgia,serif', "body": "Inter,system-ui,sans-serif", "dw": "500", "dls": "0", "br": "4px", "mr": "50%", "cr": "6px", "rr": "6px", "strip": "#22272b", "dark": "#2c3237", "ft": "#1b1f22"},
 "strip": ['<b>Tag und Nacht erreichbar: 0123 456 789</b>', "Musterstadt · Nordheim · Altdorf · Bergen", "Familienbetrieb in dritter Generation"],
 "nav": [("Im Trauerfall", "#trauerfall"), ("Bestattungsarten", "#arten"), ("Vorsorge", "#vorsorge"), ("Über uns", "#familie")], "cta": ("0123 456 789", "#kontakt"),
 "hero": {"eb": "Bestattungen in Musterstadt", "h1": "Wir sind da. Tag und Nacht.",
          "lead": "Wenn ein Mensch stirbt, müssen Sie nichts sofort entscheiden. Rufen Sie uns an – wir nehmen uns Zeit, erklären die nächsten Schritte und kümmern uns um alles Weitere.",
          "ctas": [("Jetzt anrufen", "#kontakt"), ("Was ist jetzt zu tun?", "#trauerfall")],
          "chips": ["Seit 1952 in Familienhand", "Eigener Abschiedsraum", "Transparente Kosten"],
          "floats": fl("left:-14px;bottom:40px;width:270px", "<h4>Rund um die Uhr erreichbar</h4><div class='k'>0123 456 789</div><span class='muted'>Auch an Sonn- und Feiertagen.</span>")},
 "sections": [
  ("steps", {"id": "trauerfall", "eb": "Im Trauerfall", "h2": "Was jetzt zu tun ist", "p": "Drei Schritte – den Rest übernehmen wir.", "items": [
    ("Ruhe bewahren", "Bei einem Tod zu Hause rufen Sie den Hausarzt oder den ärztlichen Bereitschaftsdienst (116 117) für die Todesbescheinigung. Im Pflegeheim oder Krankenhaus übernimmt das die Einrichtung."),
    ("Uns anrufen", "Wir kommen – zu jeder Uhrzeit – und besprechen in Ruhe, was Ihnen wichtig ist. Sie haben Zeit für den Abschied."),
    ("Unterlagen bereitlegen", "Personalausweis, Geburts- und ggf. Heiratsurkunde, Versicherungskarte. Alles Weitere erledigen wir mit Ihnen.")]}),
  ("prices", {"id": "arten", "cls": "tint", "eb": "Bestattungsarten &amp; Kosten", "h2": "Orientierung statt Ungewissheit", "p": "Unsere Leistungen zu festen Preisen. Friedhofsgebühren und Fremdleistungen wie Blumen oder Traueranzeigen kommen je nach Wunsch hinzu.", "rows": [
    ("Feuerbestattung", "Überführung, Formalitäten, Sarg, Einäscherung, Urne", "ab 1.890 €"), ("Erdbestattung", "Überführung, Formalitäten, Sarg, hygienische Versorgung", "ab 2.690 €"),
    ("Baumbestattung", "Feuerbestattung mit Beisetzung im Bestattungswald", "ab 2.290 €"), ("Seebestattung", "Feuerbestattung mit Beisetzung auf der Nord- oder Ostsee", "ab 2.490 €"),
    ("Trauerfeier", "Abschiedsraum, Dekoration, Begleitung", "ab 390 €")],
    "note": "Beispielpreise der Vorschau. Sie erhalten vor jeder Beauftragung einen schriftlichen Kostenvoranschlag.",
    "side": '<div class="card"><h3>Kein Kleingedrucktes</h3><p>Wir erklären jede Position und zeigen Ihnen, wo Sie sparen können. Es entstehen keine Kosten ohne Ihre Zustimmung.</p></div>'}),
  ("split", {"id": "vorsorge", "eb": "Vorsorge", "h2": "Selbst bestimmen, Angehörige entlasten", "p": "Mit einem Vorsorgevertrag legen Sie fest, wie Ihr Abschied aussehen soll – und sichern die Kosten über ein Treuhandkonto ab. Das Gespräch ist kostenlos und unverbindlich.",
    "vis_foto": (158251, "Sonnenlicht im Wald"), "overlay": True,
    "list": ["Wünsche schriftlich festhalten", "Kosten absichern – insolvenzgeschützt", "Gespräch bei Ihnen zu Hause oder bei uns"], "cta": ("Vorsorgegespräch vereinbaren", "#kontakt"),
    "vis": '<div class="card" style="padding:40px;text-align:center"><div style="width:64px;height:64px;margin:0 auto 18px;color:var(--accent)">' + ic("candle") + '</div><p style="font:500 1.7rem/1.35 var(--display);margin:0">„Meine Kinder sollen nicht rätseln müssen, was ich mir gewünscht hätte.“</p><p class="muted" style="margin-top:14px">Häufigster Grund für eine Vorsorge</p></div>'}),
  ("split", {"id": "familie", "cls": "dark", "rev": True, "eb": "Über uns", "h2": "Drei Generationen, ein Versprechen", "p": "1952 gründete Wilhelm Hollmann das Bestattungshaus. Heute führen Katrin und Jan Hollmann den Betrieb – mit eigenem Abschiedsraum, eigenen Fahrzeugen und viel Zeit für jede Familie.",
    "list": ["Persönliche Begleitung durch die Familie", "Abschiednahme am offenen Sarg möglich", "Trauerbegleitung auch nach der Beisetzung"],
    "vis": '<div class="team" style="--n:2"><div class="person"><div class="ph" style="--ph:#4a5157"><span>KH</span></div><h3 style="color:#fff">Katrin Hollmann</h3><p>Bestattermeisterin</p></div><div class="person"><div class="ph" style="--ph:#9a7d4c"><span>JH</span></div><h3 style="color:#fff">Jan Hollmann</h3><p>Geprüfter Bestatter</p></div></div>'}),
  ("strip", {"fotos": [(8963669, "Weiße Lilien auf einem Grabstein"), (8963947, "Weiße Blumen auf Stein")], "cap": "Baum-, See-, Erd- oder Feuerbestattung – wir zeigen Ihnen alle Möglichkeiten."}),
  ("faq", {"eb": "Fragen", "h2": "Was Angehörige uns oft fragen", "items": [
    ("Wie schnell muss ich mich entscheiden?", "Sie haben Zeit. In den meisten Bundesländern muss eine Bestattung erst innerhalb von 7 bis 10 Tagen erfolgen."),
    ("Kann ich mich in Ruhe verabschieden?", "Ja. In unserem Abschiedsraum können Sie sich in Ruhe und ohne Zeitdruck verabschieden."),
    ("Wer zahlt die Bestattung?", "In der Regel die Erben. Bei finanziellen Schwierigkeiten unterstützen wir bei Anträgen auf Kostenübernahme."),
    ("Kommen Sie auch nach Hause?", "Ja, wir kommen zu Ihnen – für das Gespräch ebenso wie zur Überführung.")]}),
  ("contact", {"eb": "Kontakt", "h2": "Wir sind für Sie da", "p": "Im Trauerfall rufen Sie bitte direkt an – Tag und Nacht. Für Vorsorge- und Kostenfragen können Sie auch einen Rückruf anfordern.", "form": "rueckruf",
    "info": [("phone", "0123 456 789", "Tag und Nacht, auch an Feiertagen"), ("map", "Friedhofstraße 2, Musterstadt", "Parkplätze direkt am Haus"), ("flower", "Abschiedsraum", "Besuche nach Vereinbarung, auch am Wochenende")]}),
 ],
 "footer": {"about": "Bestattungshaus in Familienhand seit 1952. Erd-, Feuer-, Baum- und Seebestattungen in Musterstadt und Umgebung.", "cols": [("Kontakt", ["Friedhofstraße 2", "12345 Musterstadt", "0123 456 789 (24 h)"]), ("Leistungen", ["Im Trauerfall", "Bestattungsarten", "Vorsorge", "Trauerbegleitung"]), ("Mehr", ["Über uns", "Impressum", "Datenschutz"])]},
 "mbar": [("Anrufen 24 h", "#kontakt"), ("Rückruf", "#kontakt")],
}

DEMOS["tierarzt"] = {
 "hero_foto": (6235242, "Tierarzt hält einen kleinen Hund im Arm"),
 "name": "Tierarztpraxis am Mühlbach", "branche": "Tierarztpraxis", "claim": "Kleintierpraxis", "mark": "M", "art": "tierarzt",
 "fonts": [("Outfit", "outfit")],
 "vars": {"bg": "#ffffff", "bg2": "#f0f7f7", "card": "#ffffff", "ink": "#12302f", "muted": "#557371", "line": "#d8e8e7", "brand": "#0e7c86", "brand-ink": "#ffffff", "accent": "#f2b63c", "accent-ink": "#12302f",
          "soft": "#dff1f2", "display": "Outfit,system-ui,sans-serif", "body": "Outfit,system-ui,sans-serif", "dw": "650", "dls": "-.02em", "cr": "22px", "rr": "30px", "mr": "12px", "strip": "#0e7c86", "dark": "#0b5d64", "ft": "#0b3b3e"},
 "strip": ['<i class="live"></i> Jetzt geöffnet · bis 19 Uhr', "Notdienst heute: Tierklinik Nordheim, 0123 999 000", "Termine: 0123 456 789"],
 "nav": [("Leistungen", "#leistungen"), ("Sprechzeiten", "#zeiten"), ("Team", "#team"), ("Karriere", "#karriere")], "cta": ("Termin anfragen", "#kontakt"),
 "hero": {"eb": "Kleintierpraxis in Musterstadt", "h1": "Ruhige Hände für Hund, Katze und Co.",
          "lead": "Drei Tierärztinnen, moderne Diagnostik und katzenfreundliche Abläufe. Termine und Rezepte bestellen Sie bequem online – ohne Warteschleife.",
          "ctas": [("Termin online anfragen", "#kontakt"), ("Rezept bestellen", "#kontakt")],
          "chips": ['<span class="stars">★★★★★</span> <b>4,9</b> · 310 Bewertungen', "Katzenfreundliche Abläufe", "Eigener Röntgen- &amp; Zahnbereich"],
          "floats": fl("left:-16px;top:40px;width:235px", "<h4><span class='live' style='display:inline-block;width:8px;height:8px;border-radius:50%;background:#3ddc84;margin-right:6px'></span>Heute geöffnet</h4><div class='k'>8–19 Uhr</div><span class='muted'>Akute Fälle ohne Termin bis 18 Uhr</span>")
                  + fl("right:-14px;bottom:36px;width:245px", "<h4>Rezept bestellt ✓</h4><span class='muted'>Abholbereit morgen ab 10 Uhr. Wir schicken Ihnen eine SMS.</span>")},
 "sections": [
  ("services", {"id": "leistungen", "eb": "Leistungen", "h2": "Von der Impfung bis zur Zahnbehandlung", "cols": 3, "items": [
    ("shield", "Vorsorge &amp; Impfungen", "Impfplan, Entwurmung, Gesundheits-Check und Beratung für Welpen und Kitten."),
    ("tooth", "Zahnheilkunde", "Zahnsteinentfernung, Zahnröntgen und Extraktionen unter schonender Narkose."),
    ("steth", "Innere Medizin", "Labordiagnostik, Ultraschall und Röntgen direkt in der Praxis."),
    ("heart", "Senioren-Check", "Frühzeitig erkennen, was ältere Tiere belastet – Niere, Herz, Gelenke."),
    ("paw", "Physiotherapie", "Nach Operationen und bei Arthrose – mit Unterwasserlaufband."),
    ("pill", "Online-Rezepte &amp; Futter", "Dauermedikamente und Diätfutter online bestellen und abholen.")]}),
  ("strip", {"fotos": [(6816836, "Katze bei der Ohrenreinigung"), (6235231, "Tierarzt untersucht einen Collie"), (7469222, "Tierärztin untersucht einen Hund")], "cap": "Ruhige Abläufe, eigener Katzenwartebereich, moderne Diagnostik."}),
  ("split", {"id": "zeiten", "cls": "tint", "eb": "Sprechzeiten", "h2": "Wann wir für Sie da sind", "p": "Routinetermine nach Vereinbarung, akute Fälle kommen ohne Termin – bitte rufen Sie kurz vorher an.",
    "list": ["Mo–Fr 8–12 und 14–19 Uhr", "Sa 9–12 Uhr", "Akutsprechstunde täglich bis 18 Uhr"], "cta": ("Termin anfragen", "#kontakt"),
    "vis": '<div class="notice" style="display:block;padding:30px"><h3 style="color:var(--brand)">Notfall außerhalb der Sprechzeiten?</h3><p>Der tierärztliche Notdienst wird im Wechsel organisiert. Den aktuellen Notdienst zeigen wir immer ganz oben auf dieser Seite.</p><a class="btn acc" href="#kontakt">Notdienst anzeigen</a></div>'}),
  ("stats", {"items": [("3", "Tierärztinnen, 7 TFA"), ("310+", "Bewertungen mit 4,9 Sternen"), ("2 h", "Antwort auf Online-Anfragen"), ("12.000", "betreute Patienten")]}),
  ("team", {"id": "team", "eb": "Team", "h2": "Wir kümmern uns um Ihr Tier", "people": [
    ("JM", "Dr. Julia Merz", "Tierärztin · Zahnheilkunde", "#0e7c86"), ("SA", "Sarah Aydın", "Tierärztin · Innere Medizin", "#0b5d64"), ("KL", "Kim Lorenz", "Tierärztin · Physiotherapie", "#f2b63c"), ("TFA", "Unser Praxisteam", "Sieben Tiermedizinische Fachangestellte", "#557371")]}),
  ("quotes", {"cls": "tint", "eb": "Stimmen", "h2": "Was Tierhalter sagen", "p": "Beispieltexte für die Vorschau.", "items": [
    ("Unsere ängstliche Katze war noch nie so entspannt beim Tierarzt. Separater Katzenwartebereich, ruhige Hände.", "Nina S.", "Katze Mia"),
    ("Rezept abends online bestellt, am nächsten Morgen abgeholt. Kein Telefonmarathon mehr.", "Thomas B.", "Hund Balu"),
    ("Die Zahnbehandlung wurde super erklärt, mit Kostenvoranschlag vorab. Sehr transparent.", "Familie Ritter", "Hund Emma")]}),
  ("split", {"id": "karriere", "cls": "dark", "eb": "Karriere", "h2": "TFA (m/w/d) gesucht", "p": "Planbare Dienste, kein Notdienst-Wochenende ohne Ausgleich, Fortbildungen und ein Team, das lacht. Bewerbung ohne Anschreiben in zwei Minuten.",
    "list": ["Übertarifliche Bezahlung", "Fortbildungsbudget 1.000 € pro Jahr", "Haustier darf mit zur Arbeit"], "cta": ("Jetzt bewerben", "#kontakt"),
    "vis": '<div class="card" style="padding:34px"><span class="eyebrow" style="color:var(--accent)">Offene Stellen</span><h3>Tiermedizinische:r Fachangestellte:r</h3><p>Voll- oder Teilzeit</p><hr style="border:0;border-top:1px solid rgba(255,255,255,.15);margin:18px 0"><h3>Tierärztin / Tierarzt</h3><p>Kleintier, ab sofort</p></div>'}),
  ("faq", {"eb": "Fragen", "h2": "Häufige Fragen", "items": [
    ("Muss ich einen Termin vereinbaren?", "Für Routineuntersuchungen ja – so vermeiden wir Wartezeiten. Akute Fälle behandeln wir täglich bis 18 Uhr auch ohne Termin."),
    ("Kann ich mit Karte zahlen?", "Ja, mit EC- und Kreditkarte. Bei größeren Behandlungen ist auch Ratenzahlung möglich."),
    ("Wie bestelle ich ein Rezept?", "Über das Formular auf dieser Seite. Abholbereit meist am nächsten Werktag."),
    ("Behandeln Sie auch Kaninchen und Meerschweinchen?", "Ja, wir behandeln alle gängigen Kleintiere.")]}),
  ("contact", {"eb": "Termin &amp; Rezept", "h2": "Online anfragen statt warten", "p": "Wir bestätigen Ihre Anfrage werktags innerhalb von zwei Stunden.", "form": "tierarzt",
    "info": [("map", "Mühlenweg 7, Musterstadt", "Eigene Parkplätze vor der Praxis"), ("clock", "Mo–Fr 8–12 &amp; 14–19 · Sa 9–12", "Akutsprechstunde täglich bis 18 Uhr"), ("phone", "0123 456 789", "Für Notfälle bitte immer anrufen")]}),
 ],
 "footer": {"about": "Kleintierpraxis mit drei Tierärztinnen. Vorsorge, Zahnheilkunde, Innere Medizin und Physiotherapie.", "cols": [("Praxis", ["Mühlenweg 7", "12345 Musterstadt", "0123 456 789"]), ("Sprechzeiten", ["Mo–Fr 8–12 &amp; 14–19", "Sa 9–12", "Akut bis 18 Uhr"]), ("Mehr", ["Karriere", "Impressum", "Datenschutz"])]},
 "mbar": [("Termin", "#kontakt"), ("Anrufen", "#kontakt")],
}
