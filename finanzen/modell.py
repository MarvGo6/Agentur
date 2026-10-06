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
    "preis_web": 2200,      # Ø Website Start 1.490 / Wachstum 2.990, danach Pflege
    "preis_pflege": 69,     # Ø Pflege & Hosting je Monat (49 / 89)
    "preis_prog": 1190, "preis_seo": 520, "preis_rec": 790, "preis_rec_setup": 1490,
    # Mix der Abschlüsse
    "mix_web": 0.25, "mix_prog": 0.25, "mix_seo": 0.25, "mix_rec": 0.25,
    # Kündigungen pro Monat
    "churn_pflege": 0.01, "churn_prog": 0.02, "churn_seo": 0.03, "churn_rec": 0.05,
    # Stunden (alles selbst gemacht): einmalig je Abschluss / laufend je Kunde und Monat
    "h_setup_web": 24, "h_setup_prog": 28, "h_setup_seo": 10, "h_setup_rec": 10,
    "h_mon_pflege": 0.25, "h_mon_prog": 13, "h_mon_seo": 6, "h_mon_rec": 7,
    "h_vertrieb": 10,       # Vertriebsstunden je Abschluss
    "kapazitaet": 170,      # Arbeitsstunden pro Monat
    # Kosten pro Monat
    "fix_kosten": 205, "marketing": 150,
}
# Abschluss-Ziel (Vertriebstempo) pro Monat: Monat 1–2 / ab Monat 3
SZENARIEN = {"Konservativ": [1, 2], "Basis": [2, 3], "Optimistisch": [3, 4]}

KUNDE = {"web": "pflege", "prog": "prog", "seo": "seo", "rec": "rec"}  # Abschlussart -> laufender Vertrag


def h_neu(g=G):
    return sum(g["mix_" + p] * (g["h_setup_" + p] + g["h_mon_" + KUNDE[p]] + g["h_vertrieb"]) for p in PRODUKTE)


def rechne(name, g=G):
    ziel = SZENARIEN[name]
    k = {"pflege": 0.0, "prog": 0.0, "seo": 0.0, "rec": 0.0}
    rows, kasse = [], 0.0
    for m in range(1, MONATE + 1):
        laufend = sum(k[s] * g["h_mon_" + s] for s in k)
        kap = max(0.0, (g["kapazitaet"] - laufend) / h_neu(g))
        z = ziel[0] if m <= 2 else ziel[1]
        deals = min(z, kap)
        for p in PRODUKTE:
            s = KUNDE[p]
            k[s] = k[s] * (1 - g["churn_" + s]) + deals * g["mix_" + p]
        mrr = sum(k[s] * g["preis_" + s] for s in k)
        einmal = deals * g["mix_web"] * g["preis_web"] + deals * g["mix_rec"] * g["preis_rec_setup"]
        umsatz = mrr + einmal
        kosten = g["fix_kosten"] + g["marketing"]
        erg = umsatz - kosten
        kasse += erg
        rows.append({"monat": m, "label": label(m), "jahr": kalenderjahr(m), "ziel": z, "kap": kap, "deals": deals,
                     "laufend": laufend, "stunden": laufend + deals * h_neu(g), "mrr": mrr, "einmal": einmal,
                     "umsatz": umsatz, "kosten": kosten, "ergebnis": erg, "kasse": kasse,
                     **{f"k_{s}": v for s, v in k.items()}})
    return rows


def zielmonat(rows, schwelle=10000):
    return next((x["monat"] for x in rows if x["mrr"] >= schwelle), None)


# ------------------------------------------------------------------ Preise & Verdienst je Abschluss
PREISLISTE = [
    # Produkt, einmalig, monatlich, Std einmalig, Std/Monat, Hinweis
    ("Website Start", 1490, 0, 16, 0, "bis 5 Seiten, fertig in 2–3 Wochen"),
    ("Website Wachstum", 2990, 0, 28, 0, "bis 15 Seiten, Orts- und Karriereseiten"),
    ("Pflege & Hosting Start", 0, 49, 0, 0.25, "monatlich kündbar"),
    ("Pflege & Hosting Wachstum", 0, 89, 0, 0.5, "inkl. 1 h Änderungen"),
    ("SEO Lokal", 0, 390, 4, 5, "6 Monate Mindestlaufzeit"),
    ("SEO Plus", 0, 690, 6, 8, "6 Monate Mindestlaufzeit"),
    ("Google-Ads-Betreuung", 390, 290, 4, 2.5, "zzgl. Werbebudget, monatlich kündbar"),
    ("Recruiting-Paket", 1490, 790, 10, 7, "zzgl. Werbebudget, 3 Monate Mindestlaufzeit"),
    ("Wachstumsprogramm", 0, 1190, 28, 13, "12 Monate, Website + SEO Plus + Ads inklusive"),
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
    print(f"Stunden je neuem Abschluss (Ø inkl. Vertrieb): {h_neu():.1f}")
    for n in SZENARIEN:
        r = rechne(n)
        z = zielmonat(r)
        print(f"{n:13s} 10k in Monat {z} ({r[z-1]['label'] if z else '-'})  MRR M6 {r[5]['mrr']:7.0f}  M12 {r[11]['mrr']:7.0f}  M24 {r[23]['mrr']:7.0f}  "
              f"Abschlüsse bis 10k {sum(x['deals'] for x in r[:z]) if z else '-'}  Std M12 {r[11]['stunden']:.0f}  Kasse M12 {r[11]['kasse']:8.0f}")
    for v in verdienst():
        print(f"  {v['produkt']:28s} {v['umsatz_j1']:7.0f} € / {v['stunden_j1']:5.0f} h = {v['eur_h']:4.0f} €/h")
