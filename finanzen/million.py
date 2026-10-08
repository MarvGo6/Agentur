"""Ausbau-Plan: Teamaufbau ab dem Monat nach Erreichen von 10.000 € MRR im Solo-Plan (Basis).
Treiber ist die Vertriebskapazität (Closer). Die Umsetzung übernimmt ab hier das Team (Mischsatz je Stunde).
Ziel: Jahresumsatz-Tempo von 1 Mio. € (Monatsumsatz × 12). Unabhängige Referenz zur Excel-Datei."""
import modell as M

SOLO = M.rechne("Basis")
ZIEL = M.zielmonat(SOLO)                 # Monat, in dem 10.000 € MRR erreicht sind
STARTMONAT = ZIEL + 1                    # erster Monat mit Team
MONATE = 12
LABELS = [M.label(STARTMONAT + i) for i in range(MONATE)]
JAHRE = [M.kalenderjahr(STARTMONAT + i) for i in range(MONATE)]

_s = SOLO[ZIEL - 1]
START = {"pflege": _s["k_pflege"], "seo": _s["k_seo"], "ads": 0.0, "prog": _s["k_prog"], "rec": _s["k_rec"]}

A = {
    # Preise (Durchschnitt je Abschluss)
    "p_web": 3050, "p_pflege": 89, "p_seo": 650, "p_ads": 290, "p_ads_setup": 490, "p_prog": 1390, "p_prog_setup": 1490,
    "p_rec_setup": 1490, "p_rec": 790,
    # Mix der Abschlüsse
    "mix_web": 0.50, "mix_prog": 0.25, "mix_rec": 0.25,
    "att_seo": 0.35, "att_ads": 0.20,          # Zusatzbuchung bei Website-Abschlüssen
    # Kündigungen pro Monat
    "ch_pflege": 0.01, "ch_seo": 0.03, "ch_ads": 0.04, "ch_prog": 0.02, "ch_rec": 0.05,
    # Vertrieb
    "deals_closer": 5.0,                       # Abschlüsse je eingearbeitetem Closer/Monat
    "ramp": [0.25, 0.5, 0.75],                 # Leistung in den ersten drei Monaten eines neuen Closers
    "deals_gruender": 3.0,                     # Gründer verkauft weiter und führt das Team
    "closer_fix": 3500, "sdr_fix": 2600,       # Fixgehalt (Arbeitgeberbrutto) Closer / Terminierer
    "provision": 0.08,                         # Provision auf den Umsatz
    "anteil_paid": 0.5, "cac_paid": 900,       # Anteil Abschlüsse über Werbung, Werbekosten je Abschluss
    # Umsetzung durch Team/Freelancer
    "h_web": 20, "h_seo": 6, "h_ads": 3, "h_prog": 13, "h_rec_setup": 10, "h_rec": 7, "h_pflege": 0.3,
    "h_satz": 46,                              # Mischsatz Angestellte/Freelancer je Stunde
    # Gemeinkosten
    "overhead_start": 1500, "overhead_end": 4000, "gruender": 5000,
}

# Personen im Vertrieb je Monat (inkl. Gründer); Terminierer (SDR) separat
CLOSER = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6]
SDR = [0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6]


def rechne(a=A, closer=CLOSER, sdr=SDR):
    k = dict(START)
    rows, kasse, zugang = [], 0.0, []
    for i in range(MONATE):
        zugang.extend([i] * max(0, closer[i] - 1 - len(zugang)))       # Eintrittsmonate angestellter Closer
        deals = a["deals_gruender"] + sum(a["deals_closer"] * (a["ramp"][i - m] if i - m < len(a["ramp"]) else 1) for m in zugang)
        n_web, n_prog, n_rec = deals * a["mix_web"], deals * a["mix_prog"], deals * a["mix_rec"]
        n = {"pflege": n_web, "seo": n_web * a["att_seo"], "ads": n_web * a["att_ads"], "prog": n_prog, "rec": n_rec}
        for s in k:
            k[s] = k[s] * (1 - a["ch_" + s]) + n[s]
        mrr = (k["pflege"] * a["p_pflege"] + k["seo"] * a["p_seo"] + k["ads"] * a["p_ads"]
               + k["prog"] * a["p_prog"] + k["rec"] * a["p_rec"])
        einmal = n_web * a["p_web"] + n["ads"] * a["p_ads_setup"] + n_prog * a["p_prog_setup"] + n_rec * a["p_rec_setup"]
        umsatz = mrr + einmal
        stunden = (n_web * a["h_web"] + k["seo"] * a["h_seo"] + k["ads"] * a["h_ads"] + k["prog"] * a["h_prog"]
                   + n_rec * a["h_rec_setup"] + k["rec"] * a["h_rec"] + k["pflege"] * a["h_pflege"])
        k_lief = stunden * a["h_satz"]
        k_vertrieb = max(0, closer[i] - 1) * a["closer_fix"] + sdr[i] * a["sdr_fix"] + umsatz * a["provision"]
        k_werbung = deals * a["anteil_paid"] * a["cac_paid"]
        k_overhead = a["overhead_start"] + (a["overhead_end"] - a["overhead_start"]) * i / (MONATE - 1)
        kosten = k_lief + k_vertrieb + k_werbung + k_overhead + a["gruender"]
        erg = umsatz - kosten
        kasse += erg
        rows.append({"monat": LABELS[i], "jahr": JAHRE[i], "closer": closer[i], "sdr": sdr[i], "deals": deals, "mrr": mrr,
                     "einmal": einmal, "umsatz": umsatz, "stunden": stunden, "fte": stunden / 140, "k_lief": k_lief,
                     "k_vertrieb": k_vertrieb, "k_werbung": k_werbung, "k_overhead": k_overhead, "kosten": kosten,
                     "ergebnis": erg, "kasse": kasse, **{f"k_{s}": v for s, v in k.items()}})
    return rows


def umsatz_jahr(jahr, team=None):
    """Kalenderjahresumsatz: Solo-Monate bis zum Zielmonat + Team-Monate danach."""
    team = team or rechne()
    solo = sum(x["umsatz"] for x in SOLO[:ZIEL] if x["jahr"] == jahr)
    return solo + sum(x["umsatz"] for x in team if x["jahr"] == jahr)


def tempo_monat(team=None):
    """Erster Monat, in dem Monatsumsatz × 12 ≥ 1 Mio. €."""
    team = team or rechne()
    return next((x["monat"] for x in team if x["umsatz"] * 12 >= 1_000_000), None)


if __name__ == "__main__":
    r = rechne()
    print(f"Solo-Ziel 10k in Monat {ZIEL} ({SOLO[ZIEL-1]['label']}), Team ab {LABELS[0]}. Start-Kunden:", {k: round(v, 1) for k, v in START.items()})
    for x in r:
        print(f"{x['monat']}: Abschlüsse {x['deals']:4.1f}  Umsatz {x['umsatz']:8.0f}  MRR {x['mrr']:8.0f}  Kosten {x['kosten']:8.0f}  Erg {x['ergebnis']:7.0f}  Kasse {x['kasse']:8.0f}  VZ {x['fte']:4.1f}")
    print(f"Umsatz erste 12 Team-Monate: {sum(x['umsatz'] for x in r):,.0f} €  Ergebnis {sum(x['ergebnis'] for x in r):,.0f} €  "
          f"tiefster Kassenstand {min(x['kasse'] for x in r):,.0f} €")
    print(f"Umsatz Kalenderjahr 2027: {umsatz_jahr(2027, r):,.0f} €   1-Mio-Tempo ab: {tempo_monat(r)}")
