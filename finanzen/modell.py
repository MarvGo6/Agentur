"""Solo-Plan: Gründer macht Vertrieb und Umsetzung allein, bis 10.000 € MRR erreicht sind.
Abschlüsse sind durch Vertriebstempo UND verfügbare Stunden begrenzt. Unabhängige Referenz zur Excel-Datei."""

MONATE = 24
START_MONAT, START_JAHR = 11, 2026            # Monat 1 = November 2026
MONATSNAMEN = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]


def label(m):
    i = START_MONAT - 1 + m - 1
    return f"{MONATSNAMEN[i % 12]} {str(START_JAHR + i // 12)[2:]}"


def kalenderjahr(m):
    return START_JAHR + (START_MONAT - 1 + m - 1) // 12


PRODUKTE = ["web", "prog", "seo", "rec"]          # Art des Abschlusses
G = {
    # Preise (Ø je Abschluss)
    "preis_web": 2600,      # Ø Website Start 1.790 / Wachstum 3.490, danach Pflege
    "preis_pflege": 79,     # Ø Pflege & Hosting je Monat (59 / 99)
    "preis_prog": 1390, "preis_prog_setup": 1490, "preis_seo": 650, "preis_rec": 790, "preis_rec_setup": 1490,
    # Mix der Abschlüsse (vor dem Recruiting-Start wird dessen Anteil auf die anderen verteilt)
    "mix_web": 0.25, "mix_prog": 0.25, "mix_seo": 0.25, "mix_rec": 0.25,
    "rec_ab_monat": 8,      # Recruiting wird erst ab Monat 8 (Juni 2027) verkauft
    # Kündigungen pro Monat
    "churn_pflege": 0.01, "churn_prog": 0.02, "churn_seo": 0.03, "churn_rec": 0.05,
    # Stunden VON HAND: einmalig je Abschluss / laufend je Kunde und Monat
    "h_setup_web": 24, "h_setup_prog": 28, "h_setup_seo": 10, "h_setup_rec": 10,
    "h_mon_pflege": 0.25, "h_mon_prog": 13, "h_mon_seo": 6, "h_mon_rec": 7,
    "h_vertrieb": 10,       # Vertriebsstunden je Abschluss
    # Stunden AUTOMATISIERT (gilt in der Variante "automatisiert" ab dem Kunden auto_ab_kunde, siehe betrieb/Automatisierungsplan)
    "a_h_setup_web": 10, "a_h_setup_prog": 14, "a_h_setup_seo": 5, "a_h_setup_rec": 6,
    "a_h_mon_pflege": 0.1, "a_h_mon_prog": 7, "a_h_mon_seo": 3, "a_h_mon_rec": 4,
    "a_h_vertrieb": 6,
    "auto_ab_kunde": 5,     # ab dem 5. Abschluss laufen die Automatisierungen
    "auto_kosten": 150,     # zusätzliche Systemkosten (KI, APIs) pro Monat, sobald automatisiert
    "kapazitaet": 170,      # Arbeitsstunden pro Monat
    # Kosten pro Monat
    "fix_kosten": 205, "marketing": 150,
}
STUNDEN_KEYS = [k for k in G if k.startswith("h_")]
# Abschluss-Ziel (Vertriebstempo) pro Monat: Monat 1–2 / ab Monat 3
SZENARIEN = {"Konservativ": [1, 2], "Basis": [2, 3], "Optimistisch": [3, 4]}
VARIANTEN = {"hand": "von Hand", "auto": "automatisiert ab Kunde 5"}

KUNDE = {"web": "pflege", "prog": "prog", "seo": "seo", "rec": "rec"}  # Abschlussart -> laufender Vertrag


def mix(g, m):
    """Anteile der Abschlüsse in Monat m: vor dem Recruiting-Start ohne Recruiting, Rest anteilig hochgerechnet."""
    if m >= g["rec_ab_monat"]:
        return {p: g["mix_" + p] for p in PRODUKTE}
    d = 1 - g["mix_rec"]
    return {p: (0.0 if p == "rec" else g["mix_" + p] / d) for p in PRODUKTE}


def stunden(g, auto_an):
    """Stunden-Annahmen: von Hand oder automatisiert."""
    return {k: (g["a_" + k] if auto_an else g[k]) for k in STUNDEN_KEYS}


def h_neu(g=G, m=None, auto_an=False):
    """Ø Stunden je neuem Abschluss (Einrichtung + erster Betreuungsmonat + Vertrieb)."""
    mx, h = mix(g, m if m is not None else g["rec_ab_monat"]), stunden(g, auto_an)
    return sum(mx[p] * (h["h_setup_" + p] + h["h_mon_" + KUNDE[p]] + h["h_vertrieb"]) for p in PRODUKTE)


def rechne(name, g=G, variante="hand"):
    ziel = SZENARIEN[name]
    k = {"pflege": 0.0, "prog": 0.0, "seo": 0.0, "rec": 0.0}
    rows, kasse, kum = [], 0.0, 0.0
    for m in range(1, MONATE + 1):
        auto_an = variante == "auto" and kum >= g["auto_ab_kunde"] - 1
        h, mx = stunden(g, auto_an), mix(g, m)
        hn = h_neu(g, m, auto_an)
        laufend = sum(k[s] * h["h_mon_" + s] for s in k)
        kap = max(0.0, (g["kapazitaet"] - laufend) / hn)
        z = ziel[0] if m <= 2 else ziel[1]
        deals = min(z, kap)
        kum += deals
        for p in PRODUKTE:
            s = KUNDE[p]
            k[s] = k[s] * (1 - g["churn_" + s]) + deals * mx[p]
        mrr = sum(k[s] * g["preis_" + s] for s in k)
        einmal = deals * (mx["web"] * g["preis_web"] + mx["prog"] * g["preis_prog_setup"] + mx["rec"] * g["preis_rec_setup"])
        umsatz = mrr + einmal
        kosten = g["fix_kosten"] + g["marketing"] + (g["auto_kosten"] if auto_an else 0)
        erg = umsatz - kosten
        kasse += erg
        rows.append({"monat": m, "label": label(m), "jahr": kalenderjahr(m), "ziel": z, "kap": kap, "deals": deals, "kum": kum,
                     "auto": auto_an, "h_neu": hn, "laufend": laufend, "stunden": laufend + deals * hn, "mrr": mrr, "einmal": einmal,
                     "umsatz": umsatz, "kosten": kosten, "ergebnis": erg, "kasse": kasse,
                     **{f"k_{s}": v for s, v in k.items()}})
    return rows


def zielmonat(rows, schwelle=10000):
    return next((x["monat"] for x in rows if x["mrr"] >= schwelle), None)


# ------------------------------------------------------------------ Preise & Verdienst je Abschluss
PREISLISTE = [
    # Produkt, einmalig, monatlich, Std einmalig, Std/Monat, Hinweis
    ("Website Start", 1790, 0, 16, 0, "bis 5 Seiten, fertig in 2–3 Wochen"),
    ("Website Wachstum", 3490, 0, 28, 0, "bis 15 Seiten, Orts- und Karriereseiten"),
    ("Pflege & Hosting Start", 0, 59, 0, 0.25, "12 Monate Laufzeit"),
    ("Pflege & Hosting Wachstum", 0, 99, 0, 0.5, "12 Monate Laufzeit, inkl. 1 h Änderungen"),
    ("SEO Lokal", 0, 490, 4, 5, "6 Monate Mindestlaufzeit"),
    ("SEO Plus", 0, 890, 6, 8, "6 Monate Mindestlaufzeit"),
    ("Google-Ads-Betreuung", 490, 290, 4, 2.5, "zzgl. Werbebudget, monatlich kündbar"),
    ("Recruiting-Paket", 1490, 790, 10, 7, "zzgl. Werbebudget, 3 Monate Mindestlaufzeit"),
    ("Wachstumsprogramm", 1490, 1390, 28, 13, "12 Monate, Website + SEO Plus + Ads inklusive"),
]


def verdienst(vertrieb=10):
    out = []
    for n, e, m, he, hm, hinweis in PREISLISTE:
        umsatz = e + 12 * m
        stunden = he + 12 * hm + (0 if n.startswith("Pflege") else vertrieb)   # Pflege wird mit der Website verkauft
        out.append({"produkt": n, "einmal": e, "monatlich": m, "umsatz_j1": umsatz, "stunden_j1": stunden,
                    "eur_h": umsatz / stunden, "hinweis": hinweis})
    return out


if __name__ == "__main__":
    print(f"Stunden je neuem Abschluss (Ø inkl. Vertrieb): {h_neu():.1f} von Hand, {h_neu(auto_an=True):.1f} automatisiert")
    for n in SZENARIEN:
      for v in VARIANTEN:
        r = rechne(n, variante=v)
        z = zielmonat(r)
        print(f"{n:13s} {v:4s} 10k in Monat {z} ({r[z-1]['label'] if z else '-'})  MRR M6 {r[5]['mrr']:7.0f}  M12 {r[11]['mrr']:7.0f}  M24 {r[23]['mrr']:7.0f}  "
              f"Abschlüsse bis 10k {sum(x['deals'] for x in r[:z]) if z else '-'}  Std M12 {r[11]['stunden']:.0f}  Kasse M12 {r[11]['kasse']:8.0f}")
    for v in verdienst():
        print(f"  {v['produkt']:28s} {v['umsatz_j1']:7.0f} € / {v['stunden_j1']:5.0f} h = {v['eur_h']:4.0f} €/h")
