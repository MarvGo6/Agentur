"""Referenzrechnung des Finanzmodells (unabhängig von Excel). Dient zur Validierung der Excel-Formeln."""

MONATE = 24
PHASEN = [(1, 6), (7, 12), (13, 24)]

GEMEINSAM = {
    "preis_web": 2200,        # Ø Einmalpreis Website (Mix Start/Wachstum)
    "preis_pflege": 69,       # Ø Pflege & Hosting pro Monat
    "preis_seo": 520,         # Ø SEO-Retainer (Mix Lokal/Plus)
    "preis_ads": 290,         # Ads-Betreuung
    "preis_ads_setup": 390,
    "preis_programm": 1190,
    "churn_pflege": 0.01, "churn_seo": 0.03, "churn_ads": 0.04, "churn_programm": 0.02,
    "fix_kosten": 205,        # Tools, Infrastruktur, Versicherung, Buchhaltung, Domain/Mail
    "marketing": 150,         # eigenes Marketing pro Monat
    "std_satz": 45,           # zugekaufte Freelancer-Stunde
    "zukauf_web_std": 8, "zukauf_seo_std": 2, "zukauf_programm_std": 5,
    "eigen_web_std": 20, "eigen_seo_std": 4, "eigen_ads_std": 2, "eigen_programm_std": 8, "eigen_pflege_std": 0.25,
}

SZENARIEN = {
    #                 Websites/Monat je Phase, SEO-Quote, Ads-Quote, Programm neu/Monat je Phase
    "Konservativ":  {"web": [0.5, 1.0, 1.2], "q_seo": 0.30, "q_ads": 0.15, "prog": [0, 0.10, 0.15]},
    "Basis":        {"web": [0.8, 1.3, 1.6], "q_seo": 0.35, "q_ads": 0.20, "prog": [0, 0.15, 0.25]},
    "Optimistisch": {"web": [1.0, 1.5, 2.0], "q_seo": 0.40, "q_ads": 0.25, "prog": [0.10, 0.25, 0.35]},
}


def phase(m, werte):
    for (a, b), v in zip(PHASEN, werte):
        if a <= m <= b:
            return v


def rechne(name):
    g, s = GEMEINSAM, SZENARIEN[name]
    k = {"pflege": 0.0, "seo": 0.0, "ads": 0.0, "programm": 0.0}
    rows, kasse = [], 0.0
    for m in range(1, MONATE + 1):
        web = phase(m, s["web"]); prog = phase(m, s["prog"])
        neu = {"pflege": web, "seo": web * s["q_seo"], "ads": web * s["q_ads"], "programm": prog}
        for seg in k:
            k[seg] = k[seg] * (1 - g["churn_" + seg]) + neu[seg]
        mrr = k["pflege"] * g["preis_pflege"] + k["seo"] * g["preis_seo"] + k["ads"] * g["preis_ads"] + k["programm"] * g["preis_programm"]
        einmal = web * g["preis_web"] + neu["ads"] * g["preis_ads_setup"]
        umsatz = mrr + einmal
        zukauf_std = web * g["zukauf_web_std"] + k["seo"] * g["zukauf_seo_std"] + k["programm"] * g["zukauf_programm_std"]
        kosten = g["fix_kosten"] + g["marketing"] + zukauf_std * g["std_satz"]
        ergebnis = umsatz - kosten
        kasse += ergebnis
        eigen = (web * g["eigen_web_std"] + k["seo"] * g["eigen_seo_std"] + k["ads"] * g["eigen_ads_std"]
                 + k["programm"] * g["eigen_programm_std"] + k["pflege"] * g["eigen_pflege_std"])
        rows.append({"monat": m, "mrr": mrr, "umsatz": umsatz, "kosten": kosten, "ergebnis": ergebnis,
                     "kasse": kasse, "eigen_std": eigen, **{f"k_{x}": v for x, v in k.items()}})
    return rows


if __name__ == "__main__":
    for n in SZENARIEN:
        r = rechne(n)
        ziel = next((x["monat"] for x in r if x["mrr"] >= 10000), None)
        print(f"{n:13s} MRR M12 {r[11]['mrr']:8.0f}  M18 {r[17]['mrr']:8.0f}  M24 {r[23]['mrr']:8.0f}  10k in Monat {ziel}  "
              f"Kasse M24 {r[23]['kasse']:9.0f}  Std/Monat M24 {r[23]['eigen_std']:5.0f}")
