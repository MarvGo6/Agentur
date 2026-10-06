"""1-Mio-Plan: Umsatzziel 1.000.000 € im Kalenderjahr 2027. Treiber ist die Vertriebskapazität (Closer),
die Kosten folgen aus Lieferstunden, Team, Werbung und Gemeinkosten. Unabhängige Referenz zur Excel-Datei."""

MONATE = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]

A = {
    # Preise (Durchschnitt je Deal)
    "p_web": 3200, "p_pflege": 79, "p_seo": 520, "p_ads": 290, "p_ads_setup": 390, "p_prog": 1190,
    "p_rec_setup": 1490, "p_rec": 790,
    # Deal-Mix je Abschluss
    "mix_web": 0.60, "mix_prog": 0.22, "mix_rec": 0.18,
    "att_seo": 0.35, "att_ads": 0.20,          # Zusatzbuchung bei Website-Deals
    # Kündigungen pro Monat
    "ch_pflege": 0.01, "ch_seo": 0.03, "ch_ads": 0.04, "ch_prog": 0.02, "ch_rec": 0.05,
    # Vertrieb
    "deals_closer": 5.5,                       # Abschlüsse je eingearbeitetem Closer/Monat
    "ramp": [0.25, 0.5, 0.75],                 # Leistung in den ersten drei Monaten eines neuen Closers
    "deals_gruender": 4.0,                     # Gründer verkauft nebenbei (liefert auch)
    "closer_fix": 3500, "sdr_fix": 2600,       # Fixgehalt (Arbeitgeberbrutto) Closer / Terminierer
    "provision": 0.08,                         # Provision auf den Umsatz
    "anteil_paid": 0.5, "cac_paid": 900,       # Anteil Deals über bezahlte Werbung, Werbekosten je Deal
    # Lieferung
    "h_web": 18, "h_seo": 5, "h_ads": 3, "h_prog": 12, "h_rec_setup": 10, "h_rec": 6, "h_pflege": 0.3,
    "h_satz": 46,                              # Mischsatz Angestellte/Freelancer je Stunde
    # Gemeinkosten
    "overhead_start": 1800, "overhead_end": 4500, "gruender": 5000,
}

# Personen im Vertrieb je Monat (inkl. Gründer); Terminierer (SDR) separat
CLOSER = [1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 7, 7]
SDR = [1, 1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 7]
START = {"pflege": 4, "seo": 1, "ads": 0, "prog": 0, "rec": 0}   # Kundenbestand Ende 2026


def rechne(a=A, closer=CLOSER, sdr=SDR):
    k = dict(START)
    rows, kasse, zugang = [], 0.0, []
    for i in range(12):
        zugang.extend([i] * max(0, closer[i] - 1 - len(zugang)))       # Eintrittsmonate angestellter Closer
        deals = a["deals_gruender"] + sum(a["deals_closer"] * (a["ramp"][i - m] if i - m < len(a["ramp"]) else 1) for m in zugang)
        n_web, n_prog, n_rec = deals * a["mix_web"], deals * a["mix_prog"], deals * a["mix_rec"]
        n = {"pflege": n_web, "seo": n_web * a["att_seo"], "ads": n_web * a["att_ads"], "prog": n_prog, "rec": n_rec}
        for s in k:
            k[s] = k[s] * (1 - a["ch_" + s]) + n[s]
        mrr = (k["pflege"] * a["p_pflege"] + k["seo"] * a["p_seo"] + k["ads"] * a["p_ads"]
               + k["prog"] * a["p_prog"] + k["rec"] * a["p_rec"])
        einmal = n_web * a["p_web"] + n["ads"] * a["p_ads_setup"] + n_rec * a["p_rec_setup"]
        umsatz = mrr + einmal
        stunden = (n_web * a["h_web"] + k["seo"] * a["h_seo"] + k["ads"] * a["h_ads"] + k["prog"] * a["h_prog"]
                   + n_rec * a["h_rec_setup"] + k["rec"] * a["h_rec"] + k["pflege"] * a["h_pflege"])
        k_lief = stunden * a["h_satz"]
        k_vertrieb = max(0, closer[i] - 1) * a["closer_fix"] + sdr[i] * a["sdr_fix"] + umsatz * a["provision"]
        k_werbung = deals * a["anteil_paid"] * a["cac_paid"]
        k_overhead = a["overhead_start"] + (a["overhead_end"] - a["overhead_start"]) * i / 11
        kosten = k_lief + k_vertrieb + k_werbung + k_overhead + a["gruender"]
        erg = umsatz - kosten
        kasse += erg
        rows.append({"monat": MONATE[i], "closer": closer[i], "sdr": sdr[i], "deals": deals, "mrr": mrr, "einmal": einmal,
                     "umsatz": umsatz, "stunden": stunden, "fte": stunden / 140, "k_lief": k_lief, "k_vertrieb": k_vertrieb,
                     "k_werbung": k_werbung, "k_overhead": k_overhead, "kosten": kosten, "ergebnis": erg, "kasse": kasse,
                     **{f"k_{s}": v for s, v in k.items()}})
    return rows


if __name__ == "__main__":
    r = rechne()
    for x in r:
        print(f"{x['monat']}: Deals {x['deals']:5.1f}  Umsatz {x['umsatz']:9.0f}  MRR {x['mrr']:8.0f}  Kosten {x['kosten']:8.0f}  Erg {x['ergebnis']:8.0f}  Kasse {x['kasse']:9.0f}  FTE {x['fte']:4.1f}")
    print(f"Umsatz 2027: {sum(x['umsatz'] for x in r):,.0f} €  Ergebnis: {sum(x['ergebnis'] for x in r):,.0f} €  "
          f"tiefster Kassenstand: {min(x['kasse'] for x in r):,.0f} €  Deals: {sum(x['deals'] for x in r):.0f}")
