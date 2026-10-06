"""Erzeugt finanzen/Finanzmodell.xlsx (mit Formeln) aus den Annahmen in modell.py (Solo) und million.py (Ausbau)."""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.chart import LineChart, Reference
import modell as M
import million as MI

F = "Arial"
BLUE, GREEN = Font(name=F, color="0000FF"), Font(name=F, color="008000")
NORM, BOLD, H1 = Font(name=F), Font(name=F, bold=True), Font(name=F, bold=True, size=14)
ITAL = Font(name=F, italic=True)
HEAD = PatternFill("solid", fgColor="0F5C4A"); HEADF = Font(name=F, bold=True, color="FFFFFF")
KEY = PatternFill("solid", fgColor="FFFF00"); SUB = PatternFill("solid", fgColor="EFE8DB")
EUR, NUM1, PCT = '#,##0 €;(#,##0 €);-', '#,##0.0;(#,##0.0);-', '0.0%;(0.0%);-'
TOP = Border(top=Side(style="thin"))
G, N = M.G, M.MONATE


def kopf(ws, row, texte, start=1):
    for j, t in enumerate(texte):
        c = ws.cell(row, start + j, t); c.font, c.fill = HEADF, HEAD


wb = Workbook()
U = wb.active; U.title = "Übersicht"

# ================================================================== Preise & Verdienst
P = wb.create_sheet("Preise")
P["A1"] = "Preisübersicht und Verdienst je Abschluss"; P["A1"].font = H1
P["A2"] = "Blaue Werte sind Eingaben. Stunden = alles selbst gemacht, inkl. Vertrieb je Abschluss (Pflege wird mit der Website verkauft)."; P["A2"].font = ITAL
P["A3"], P["B3"] = "Vertriebsstunden je Abschluss", 10; P["B3"].font = BLUE
kopf(P, 5, ["Produkt", "Einmalig", "Monatlich", "Std. einmalig", "Std. je Monat", "Umsatz 1. Jahr", "Stunden 1. Jahr", "€ je Stunde", "Hinweis"])
for i, (n, e, m, he, hm, hinweis) in enumerate(M.PREISLISTE, start=6):
    P.cell(i, 1, n).font = NORM
    for j, v in enumerate((e, m, he, hm), start=2):
        c = P.cell(i, j, v); c.font = BLUE; c.number_format = EUR if j < 4 else NUM1
    vt = "0" if n.startswith("Pflege") else "$B$3"
    P.cell(i, 6, f"=B{i}+12*C{i}").number_format = EUR
    P.cell(i, 7, f"=D{i}+12*E{i}+{vt}").number_format = NUM1
    c = P.cell(i, 8, f"=IF(G{i}>0,F{i}/G{i},0)"); c.number_format = EUR; c.font = BOLD
    P.cell(i, 9, hinweis).font = NORM
last_p = 5 + len(M.PREISLISTE)
P.cell(last_p + 2, 1, "Faustregel netto: Vom Gewinn 35–40 % für Einkommensteuer und Sozialversicherung zurücklegen (Steuerberater fragen).").font = ITAL
P.column_dimensions["A"].width = 30
for c in "BCDEFGH": P.column_dimensions[c].width = 14
P.column_dimensions["I"].width = 46

# ================================================================== Annahmen Solo
A = wb.create_sheet("Annahmen")
A["A1"] = "Annahmen Solo-Plan (Gründer macht Vertrieb und Umsetzung allein)"; A["A1"].font = H1
A["A2"] = "Blaue Zahlen sind Eingaben. Gelb = wichtigste Hebel. Monat 1 = November 2026."; A["A2"].font = ITAL
labels = [("preis_web", "Ø Website-Auftrag (einmalig)", EUR), ("preis_pflege", "Ø Pflege & Hosting / Monat", EUR), ("preis_prog", "Wachstumsprogramm / Monat", EUR), ("preis_prog_setup", "Programm-Einrichtung (inkl. Website)", EUR),
          ("preis_seo", "Ø SEO / Monat", EUR), ("preis_rec", "Recruiting-Paket / Monat", EUR), ("preis_rec_setup", "Recruiting-Einrichtung", EUR),
          ("mix_web", "Anteil Abschlüsse: Website (+ Pflege)", PCT), ("mix_prog", "Anteil Abschlüsse: Wachstumsprogramm", PCT),
          ("mix_seo", "Anteil Abschlüsse: SEO", PCT), ("mix_rec", "Anteil Abschlüsse: Recruiting", PCT),
          ("churn_pflege", "Kündigung Pflege / Monat", PCT), ("churn_prog", "Kündigung Programm / Monat", PCT),
          ("churn_seo", "Kündigung SEO / Monat", PCT), ("churn_rec", "Kündigung Recruiting / Monat", PCT),
          ("h_setup_web", "Std. je neuer Website", NUM1), ("h_setup_prog", "Std. Einrichtung Programm", NUM1), ("h_setup_seo", "Std. Einrichtung SEO", NUM1),
          ("h_setup_rec", "Std. Einrichtung Recruiting", NUM1), ("h_mon_pflege", "Std. je Pflege-Kunde / Monat", NUM1), ("h_mon_prog", "Std. je Programm-Kunde / Monat", NUM1),
          ("h_mon_seo", "Std. je SEO-Kunde / Monat", NUM1), ("h_mon_rec", "Std. je Recruiting-Kunde / Monat", NUM1),
          ("h_vertrieb", "Vertriebsstunden je Abschluss", NUM1), ("kapazitaet", "Arbeitsstunden pro Monat", NUM1),
          ("fix_kosten", "Fixkosten / Monat", EUR), ("marketing", "Eigenes Marketing / Monat", EUR)]
kopf(A, 4, ["Annahme", "Wert"])
R = {}
for i, (k, lab, fmt) in enumerate(labels, start=5):
    A.cell(i, 1, lab).font = NORM
    c = A.cell(i, 2, G[k]); c.font = BLUE; c.number_format = fmt
    R[k] = f"Annahmen!$B${i}"
for k in ("kapazitaet", "mix_rec", "h_vertrieb"):
    A[R[k].split("!")[1].replace("$", "")].fill = KEY
r0 = 5 + len(labels) + 1
A.cell(r0, 1, "Std. je neuem Abschluss (Ø, inkl. Vertrieb)").font = BOLD
hn = "+".join(f"{R['mix_' + p]}*({R['h_setup_' + p]}+{R['h_mon_' + M.KUNDE[p]]}+{R['h_vertrieb']})" for p in M.PRODUKTE)
c = A.cell(r0, 2, "=" + hn); c.number_format = NUM1; c.font = BOLD
R["h_neu"] = f"Annahmen!$B${r0}"
r1 = r0 + 2
kopf(A, r1, ["Abschluss-Ziel (Vertriebstempo)", *M.SZENARIEN.keys()])
A.cell(r1 + 1, 1, "Abschlüsse / Monat, Monat 1–2").font = NORM
A.cell(r1 + 2, 1, "Abschlüsse / Monat, ab Monat 3").font = NORM
ZR = {}
for j, (n, z) in enumerate(M.SZENARIEN.items()):
    for t in range(2):
        c = A.cell(r1 + 1 + t, 2 + j, z[t]); c.font = BLUE; c.fill = KEY; c.number_format = NUM1
    ZR[n] = (f"Annahmen!${L(2 + j)}${r1 + 1}", f"Annahmen!${L(2 + j)}${r1 + 2}")
A.column_dimensions["A"].width = 44
for c in "BCD": A.column_dimensions[c].width = 14

# ================================================================== Solo-Szenarien
LINES = [("Monat", "label"), ("Abschluss-Ziel (Vertrieb)", "ziel"), ("Laufende Stunden (Bestand)", "laufend"), ("Möglich nach Stunden", "kap"),
         ("Abschlüsse", "deals"), (None, None), ("Aktive Pflege-Kunden", "k_pflege"), ("Aktive Programm-Kunden", "k_prog"),
         ("Aktive SEO-Kunden", "k_seo"), ("Aktive Recruiting-Kunden", "k_rec"), (None, None), ("MRR", "mrr"), ("Einmalumsatz", "einmal"),
         ("Umsatz", "umsatz"), ("Kosten", "kosten"), ("Ergebnis vor Steuern (= Einkommen Gründer)", "erg"), ("Kasse kumuliert", "kasse"),
         ("Belegte Stunden", "stunden")]
ROWS = {}


def solo_sheet(name):
    ws = wb.create_sheet(f"Solo {name}")
    ws["A1"] = f"Solo-Plan · Szenario {name} (24 Monate ab Nov 2026)"; ws["A1"].font = H1
    ws["A2"] = "Abschlüsse = Minimum aus Vertriebstempo und freien Stunden. Kundenzahlen sind Erwartungswerte."; ws["A2"].font = ITAL
    Rr = {}; row = 3
    for lab, key in LINES:
        row += 1
        if key: Rr[key] = row
    row = 3
    for lab, key in LINES:
        row += 1
        if key is None:
            for c in range(1, N + 2): ws.cell(row, c).fill = SUB
            continue
        ws.cell(row, 1, lab).font = BOLD if key in ("deals", "mrr", "umsatz", "erg", "kasse") else NORM
        for m in range(1, N + 1):
            col, pc = L(m + 1), (L(m) if m > 1 else None)
            prev = lambda k: f"{pc}{Rr[k]}" if pc else "0"
            if key == "label":
                f = M.label(m)
            elif key == "ziel":
                f = f"={ZR[name][0] if m <= 2 else ZR[name][1]}"
            elif key == "laufend":
                f = "=" + "+".join(f"{prev('k_' + s)}*{R['h_mon_' + s]}" for s in ("pflege", "prog", "seo", "rec"))
            elif key == "kap":
                f = f"=MAX(0,({R['kapazitaet']}-{col}{Rr['laufend']})/{R['h_neu']})"
            elif key == "deals":
                f = f"=MIN({col}{Rr['ziel']},{col}{Rr['kap']})"
            elif key.startswith("k_"):
                s = key[2:]; p = {"pflege": "web", "prog": "prog", "seo": "seo", "rec": "rec"}[s]
                f = f"={prev(key)}*(1-{R['churn_' + s]})+{col}{Rr['deals']}*{R['mix_' + p]}"
            elif key == "mrr":
                f = "=" + "+".join(f"{col}{Rr['k_' + s]}*{R['preis_' + s]}" for s in ("pflege", "prog", "seo", "rec"))
            elif key == "einmal":
                f = f"={col}{Rr['deals']}*{R['mix_web']}*{R['preis_web']}+{col}{Rr['deals']}*{R['mix_prog']}*{R['preis_prog_setup']}+{col}{Rr['deals']}*{R['mix_rec']}*{R['preis_rec_setup']}"
            elif key == "umsatz":
                f = f"={col}{Rr['mrr']}+{col}{Rr['einmal']}"
            elif key == "kosten":
                f = f"={R['fix_kosten']}+{R['marketing']}"
            elif key == "erg":
                f = f"={col}{Rr['umsatz']}-{col}{Rr['kosten']}"
            elif key == "kasse":
                f = f"={prev('kasse')}+{col}{Rr['erg']}" if pc else f"={col}{Rr['erg']}"
            elif key == "stunden":
                f = f"={col}{Rr['laufend']}+{col}{Rr['deals']}*{R['h_neu']}"
            c = ws.cell(row, m + 1, f)
            if key == "label":
                c.font, c.fill = HEADF, HEAD
            else:
                c.number_format = NUM1 if key in ("ziel", "laufend", "kap", "deals", "stunden") or key.startswith("k_") else EUR
                c.font = BOLD if key in ("deals", "mrr", "umsatz", "erg", "kasse") else NORM
                if key in ("mrr", "umsatz", "erg"): c.border = TOP
    ws.cell(Rr["label"], 1).font, ws.cell(Rr["label"], 1).fill = HEADF, HEAD
    ws.column_dimensions["A"].width = 44
    for m in range(1, N + 1): ws.column_dimensions[L(m + 1)].width = 10
    ws.freeze_panes = "B5"
    ROWS[name] = Rr


for n in M.SZENARIEN: solo_sheet(n)

# ================================================================== Ausbau ab 10k
X = wb.create_sheet("Ausbau ab 10k")
X["A1"] = "Ausbau-Plan: Team ab dem Monat nach 10.000 € MRR (Solo Basis)"; X["A1"].font = H1
X["A2"] = "Startbestand kommt automatisch aus „Solo Basis“ (erster Monat mit MRR ≥ 10.000 €). Blaue Werte sind Eingaben."; X["A2"].font = ITAL
a = MI.A
inp = [("p_web", "Ø Website-Auftrag", EUR), ("p_pflege", "Pflege & Hosting / Monat", EUR), ("p_seo", "SEO / Monat", EUR), ("p_ads", "Ads-Betreuung / Monat", EUR),
       ("p_ads_setup", "Ads-Einrichtung", EUR), ("p_prog", "Wachstumsprogramm / Monat", EUR), ("p_prog_setup", "Programm-Einrichtung", EUR), ("p_rec_setup", "Recruiting-Einrichtung", EUR), ("p_rec", "Recruiting / Monat", EUR),
       ("mix_web", "Anteil Website-Abschlüsse", PCT), ("mix_prog", "Anteil Programm-Abschlüsse", PCT), ("mix_rec", "Anteil Recruiting-Abschlüsse", PCT),
       ("att_seo", "Website-Abschlüsse mit SEO", PCT), ("att_ads", "Website-Abschlüsse mit Ads", PCT),
       ("ch_pflege", "Kündigung Pflege", PCT), ("ch_seo", "Kündigung SEO", PCT), ("ch_ads", "Kündigung Ads", PCT), ("ch_prog", "Kündigung Programm", PCT), ("ch_rec", "Kündigung Recruiting", PCT),
       ("deals_closer", "Abschlüsse je eingearbeitetem Closer", NUM1), ("deals_gruender", "Abschlüsse Gründer / Monat", NUM1),
       ("closer_fix", "Fixkosten je Closer", EUR), ("sdr_fix", "Fixkosten je Terminierer", EUR), ("provision", "Provision auf Umsatz", PCT),
       ("anteil_paid", "Anteil Abschlüsse über Werbung", PCT), ("cac_paid", "Werbekosten je Abschluss", EUR),
       ("h_web", "Std. je Website", NUM1), ("h_seo", "Std. je SEO-Kunde / Monat", NUM1), ("h_ads", "Std. je Ads-Kunde / Monat", NUM1), ("h_prog", "Std. je Programm-Kunde / Monat", NUM1),
       ("h_rec_setup", "Std. je Recruiting-Einrichtung", NUM1), ("h_rec", "Std. je Recruiting-Kunde / Monat", NUM1), ("h_pflege", "Std. je Pflege-Kunde / Monat", NUM1),
       ("h_satz", "Mischsatz Umsetzung je Stunde", EUR), ("overhead_start", "Gemeinkosten erster Monat", EUR), ("overhead_end", "Gemeinkosten zwölfter Monat", EUR), ("gruender", "Gründergehalt / Monat", EUR)]
PR = {}
kopf(X, 4, ["Annahme", "Wert"])
for i, (k, lab, fmt) in enumerate(inp, start=5):
    X.cell(i, 1, lab).font = NORM
    c = X.cell(i, 2, a[k]); c.font = BLUE; c.number_format = fmt
    PR[k] = f"$B${i}"
r = 5 + len(inp)
for j, v in enumerate(a["ramp"]):
    X.cell(r + j, 1, f"Leistung neuer Closer im Monat {j+1}").font = NORM
    c = X.cell(r + j, 2, v); c.font = BLUE; c.number_format = PCT; PR[f"r{j+1}"] = f"$B${r+j}"
st = r + 4
B = ROWS["Basis"]; last = L(N + 1)
X.cell(st, 1, "Zielmonat 10.000 € MRR (aus Solo Basis)").font = BOLD
c = X.cell(st, 2, f"=COUNTIF('Solo Basis'!B{B['mrr']}:{last}{B['mrr']},\"<10000\")+1"); c.font = GREEN; PR["ziel"] = f"$B${st}"
for j, (s, lab) in enumerate([("pflege", "Pflege"), ("seo", "SEO"), ("prog", "Programm"), ("rec", "Recruiting")], start=1):
    X.cell(st + j, 1, f"Startbestand {lab}").font = NORM
    c = X.cell(st + j, 2, f"=INDEX('Solo Basis'!B{B['k_' + s]}:{last}{B['k_' + s]},1,{PR['ziel']})"); c.font = GREEN; c.number_format = NUM1
    PR["s_" + s] = f"$B${st + j}"
X.cell(st + 5, 1, "Startbestand Ads").font = NORM; c = X.cell(st + 5, 2, 0); c.font = BLUE; PR["s_ads"] = f"$B${st + 5}"
for k in ("deals_closer", "cac_paid", "mix_rec"): X[PR[k].replace("$", "")].fill = KEY

H = 4
kopf(X, H, ["Kennzahl"], start=4)
for m in range(MI.MONATE):
    c = X.cell(H, 5 + m, MI.LABELS[m]); c.font, c.fill = HEADF, HEAD
c = X.cell(H, 17, "Summe 12 Monate"); c.font, c.fill = HEADF, HEAD
lines = ["vertrieb", "sdr", "angest", "neu", "aequiv", "deals", "n_web", "n_seo", "n_ads", "n_prog", "n_rec", None,
         "k_pflege", "k_seo", "k_ads", "k_prog", "k_rec", None, "mrr", "einmal", "umsatz", "tempo", None,
         "stunden", "fte", "k_lief", "k_vertrieb", "k_werbung", "k_overhead", "k_gruender", "kosten", None, "erg", "kasse"]
labs = {"vertrieb": "Personen im Vertrieb (inkl. Gründer)", "sdr": "Terminierer", "angest": "Angestellte Closer", "neu": "davon neu", "aequiv": "Eingearbeitete Closer-Äquivalente",
        "deals": "Abschlüsse", "n_web": "neue Website-Kunden", "n_seo": "neue SEO-Kunden", "n_ads": "neue Ads-Kunden", "n_prog": "neue Programm-Kunden", "n_rec": "neue Recruiting-Kunden",
        "k_pflege": "Aktive Pflege-Kunden", "k_seo": "Aktive SEO-Kunden", "k_ads": "Aktive Ads-Kunden", "k_prog": "Aktive Programm-Kunden", "k_rec": "Aktive Recruiting-Kunden",
        "mrr": "MRR", "einmal": "Einmalumsatz", "umsatz": "Umsatz", "tempo": "Jahresumsatz-Tempo (Umsatz × 12)", "stunden": "Umsetzungsstunden", "fte": "Vollzeitstellen Umsetzung (140 h)",
        "k_lief": "Kosten Umsetzung", "k_vertrieb": "Kosten Vertrieb", "k_werbung": "Werbebudget", "k_overhead": "Gemeinkosten", "k_gruender": "Gründergehalt",
        "kosten": "Kosten gesamt", "erg": "Ergebnis vor Steuern", "kasse": "Kasse kumuliert"}
RW = {}; row = H
for key in lines:
    row += 1
    if key: RW[key] = row
row = H
for key in lines:
    row += 1
    if key is None:
        for cc in range(4, 18): X.cell(row, cc).fill = SUB
        continue
    X.cell(row, 4, labs[key]).font = BOLD if key in ("deals", "mrr", "umsatz", "kosten", "erg", "kasse") else NORM
    for m in range(MI.MONATE):
        col = L(5 + m); pc = L(4 + m) if m else None; pc2 = L(3 + m) if m > 1 else None
        if key == "vertrieb": f = MI.CLOSER[m]
        elif key == "sdr": f = MI.SDR[m]
        elif key == "angest": f = f"=MAX(0,{col}{RW['vertrieb']}-1)"
        elif key == "neu": f = f"=MAX(0,{col}{RW['angest']}-{pc}{RW['angest']})" if pc else f"={col}{RW['angest']}"
        elif key == "aequiv":
            f = f"={col}{RW['angest']}-(1-{PR['r1']})*{col}{RW['neu']}"
            if pc: f += f"-(1-{PR['r2']})*{pc}{RW['neu']}"
            if pc2: f += f"-(1-{PR['r3']})*{pc2}{RW['neu']}"
        elif key == "deals": f = f"={PR['deals_gruender']}+{col}{RW['aequiv']}*{PR['deals_closer']}"
        elif key == "n_web": f = f"={col}{RW['deals']}*{PR['mix_web']}"
        elif key == "n_seo": f = f"={col}{RW['n_web']}*{PR['att_seo']}"
        elif key == "n_ads": f = f"={col}{RW['n_web']}*{PR['att_ads']}"
        elif key == "n_prog": f = f"={col}{RW['deals']}*{PR['mix_prog']}"
        elif key == "n_rec": f = f"={col}{RW['deals']}*{PR['mix_rec']}"
        elif key.startswith("k_") and key[2:] in ("pflege", "seo", "ads", "prog", "rec"):
            s = key[2:]; neu = {"pflege": "n_web", "seo": "n_seo", "ads": "n_ads", "prog": "n_prog", "rec": "n_rec"}[s]
            prev = f"{pc}{RW[key]}" if pc else PR["s_" + s]
            f = f"={prev}*(1-{PR['ch_' + s]})+{col}{RW[neu]}"
        elif key == "mrr": f = f"={col}{RW['k_pflege']}*{PR['p_pflege']}+{col}{RW['k_seo']}*{PR['p_seo']}+{col}{RW['k_ads']}*{PR['p_ads']}+{col}{RW['k_prog']}*{PR['p_prog']}+{col}{RW['k_rec']}*{PR['p_rec']}"
        elif key == "einmal": f = f"={col}{RW['n_web']}*{PR['p_web']}+{col}{RW['n_ads']}*{PR['p_ads_setup']}+{col}{RW['n_prog']}*{PR['p_prog_setup']}+{col}{RW['n_rec']}*{PR['p_rec_setup']}"
        elif key == "umsatz": f = f"={col}{RW['mrr']}+{col}{RW['einmal']}"
        elif key == "tempo": f = f"={col}{RW['umsatz']}*12"
        elif key == "stunden": f = (f"={col}{RW['n_web']}*{PR['h_web']}+{col}{RW['k_seo']}*{PR['h_seo']}+{col}{RW['k_ads']}*{PR['h_ads']}+{col}{RW['k_prog']}*{PR['h_prog']}"
                                    f"+{col}{RW['n_rec']}*{PR['h_rec_setup']}+{col}{RW['k_rec']}*{PR['h_rec']}+{col}{RW['k_pflege']}*{PR['h_pflege']}")
        elif key == "fte": f = f"={col}{RW['stunden']}/140"
        elif key == "k_lief": f = f"={col}{RW['stunden']}*{PR['h_satz']}"
        elif key == "k_vertrieb": f = f"={col}{RW['angest']}*{PR['closer_fix']}+{col}{RW['sdr']}*{PR['sdr_fix']}+{col}{RW['umsatz']}*{PR['provision']}"
        elif key == "k_werbung": f = f"={col}{RW['deals']}*{PR['anteil_paid']}*{PR['cac_paid']}"
        elif key == "k_overhead": f = f"={PR['overhead_start']}+({PR['overhead_end']}-{PR['overhead_start']})*{m}/{MI.MONATE - 1}"
        elif key == "k_gruender": f = f"={PR['gruender']}"
        elif key == "kosten": f = f"=SUM({col}{RW['k_lief']}:{col}{RW['k_gruender']})"
        elif key == "erg": f = f"={col}{RW['umsatz']}-{col}{RW['kosten']}"
        elif key == "kasse": f = f"={pc}{RW['kasse']}+{col}{RW['erg']}" if pc else f"={col}{RW['erg']}"
        c = X.cell(row, 5 + m, f)
        c.font = BLUE if key in ("vertrieb", "sdr") else (BOLD if key in ("deals", "mrr", "umsatz", "kosten", "erg", "kasse") else NORM)
        c.number_format = EUR if key in ("mrr", "einmal", "umsatz", "tempo", "k_lief", "k_vertrieb", "k_werbung", "k_overhead", "k_gruender", "kosten", "erg", "kasse") else NUM1
    if key in ("deals", "n_web", "n_seo", "n_ads", "n_prog", "n_rec", "einmal", "umsatz", "stunden", "k_lief", "k_vertrieb", "k_werbung", "k_overhead", "k_gruender", "kosten", "erg"):
        c = X.cell(row, 17, f"=SUM(E{row}:P{row})"); c.font = BOLD; c.number_format = X.cell(row, 16).number_format
X.column_dimensions["A"].width = 40; X.column_dimensions["B"].width = 12; X.column_dimensions["C"].width = 3; X.column_dimensions["D"].width = 36
for m in range(13): X.column_dimensions[L(5 + m)].width = 11
X.freeze_panes = "E5"

# ================================================================== Übersicht
U["A1"] = "Übersicht – Solo-Plan bis 10.000 € MRR, danach Ausbau mit Team"; U["A1"].font = H1
U["A2"] = "Ergebnis vor Steuern. Im Solo-Plan ist das Ergebnis das Einkommen des Gründers (davon 35–40 % für Steuern/Sozialversicherung zurücklegen)."; U["A2"].font = ITAL
kopf(U, 4, ["Solo-Plan", *M.SZENARIEN.keys()])
kpis = [("MRR Monat 6 (Apr 27)", lambda R_: f"G{R_['mrr']}", EUR), ("MRR Monat 12 (Okt 27)", lambda R_: f"M{R_['mrr']}", EUR),
        ("MRR Monat 24 (Okt 28)", lambda R_: f"{last}{R_['mrr']}", EUR)]
row = 5
for lab, f, fmt in kpis:
    U.cell(row, 1, lab).font = NORM
    for j, n in enumerate(M.SZENARIEN):
        c = U.cell(row, 2 + j, f"='Solo {n}'!{f(ROWS[n])}"); c.font = GREEN; c.number_format = fmt
    row += 1
U.cell(row, 1, "Monat, in dem 10.000 € MRR erreicht werden").font = BOLD
for j, n in enumerate(M.SZENARIEN):
    Rr = ROWS[n]
    c = U.cell(row, 2 + j, f"=IF(MAX('Solo {n}'!B{Rr['mrr']}:{last}{Rr['mrr']})>=10000,COUNTIF('Solo {n}'!B{Rr['mrr']}:{last}{Rr['mrr']},\"<10000\")+1,\"nicht in 24 Monaten\")")
    c.font = GREEN; c.fill = KEY
row += 1
for lab, rng, fmt in [("Einkommen erste 12 Monate (vor Steuern)", ("B", "M", "erg"), EUR), ("Abschlüsse erste 12 Monate", ("B", "M", "deals"), NUM1)]:
    U.cell(row, 1, lab).font = NORM
    for j, n in enumerate(M.SZENARIEN):
        Rr = ROWS[n]
        c = U.cell(row, 2 + j, f"=SUM('Solo {n}'!{rng[0]}{Rr[rng[2]]}:{rng[1]}{Rr[rng[2]]})"); c.font = GREEN; c.number_format = fmt
    row += 1
U.cell(row, 1, "Belegte Stunden Monat 12").font = NORM
for j, n in enumerate(M.SZENARIEN):
    c = U.cell(row, 2 + j, f"='Solo {n}'!M{ROWS[n]['stunden']}"); c.font = GREEN; c.number_format = NUM1
row += 2
kopf(U, row, ["Ausbau ab 10.000 € MRR (Team)", "Wert"]); row += 1
for lab, f, fmt in [("Team-Start", f"=\"{MI.LABELS[0]}\"", "@"), ("Umsatz erste 12 Team-Monate", f"='Ausbau ab 10k'!Q{RW['umsatz']}", EUR),
                    ("Ergebnis erste 12 Team-Monate", f"='Ausbau ab 10k'!Q{RW['erg']}", EUR),
                    ("MRR nach 12 Team-Monaten", f"='Ausbau ab 10k'!P{RW['mrr']}", EUR),
                    ("Tiefster Kassenstand im Ausbau", f"=MIN(0,MIN('Ausbau ab 10k'!E{RW['kasse']}:P{RW['kasse']}))", EUR),
                    ("Jahresumsatz-Tempo im 12. Team-Monat", f"='Ausbau ab 10k'!P{RW['tempo']}", EUR)]:
    U.cell(row, 1, lab).font = NORM; c = U.cell(row, 2, f); c.font = GREEN; c.number_format = fmt; row += 1
U.column_dimensions["A"].width = 46
for c in "BCD": U.column_dimensions[c].width = 20
# Diagramm MRR Solo
d0 = row + 2
U.cell(d0, 1, "MRR je Monat (Solo)").font = BOLD
for j, n in enumerate(M.SZENARIEN): U.cell(d0, 2 + j, n).font = BOLD
for m in range(1, N + 1):
    U.cell(d0 + m, 1, M.label(m)).font = NORM
    for j, n in enumerate(M.SZENARIEN):
        c = U.cell(d0 + m, 2 + j, f"='Solo {n}'!{L(m + 1)}{ROWS[n]['mrr']}"); c.font = GREEN; c.number_format = EUR
ch = LineChart(); ch.title = "MRR im Solo-Plan"; ch.y_axis.title = "€"; ch.x_axis.title = "Monat"
ch.add_data(Reference(U, min_col=2, max_col=4, min_row=d0, max_row=d0 + N), titles_from_data=True)
ch.set_categories(Reference(U, min_col=1, min_row=d0 + 1, max_row=d0 + N))
for s, col in zip(ch.series, ("C26A2E", "1A8A68", "5B6FC4")):
    s.graphicalProperties.line.solidFill = col; s.graphicalProperties.line.width = 28000; s.smooth = False
ch.height, ch.width = 9, 18
U.add_chart(ch, "F4")

for ws in wb.worksheets:
    for row_ in ws.iter_rows():
        for c in row_:
            if c.font is None or c.font.name != F:
                c.font = Font(name=F, bold=c.font.bold if c.font else False, italic=c.font.italic if c.font else False,
                              color=c.font.color if c.font else None, size=c.font.size if c.font else 11)
wb.save("Finanzmodell.xlsx")
print("gespeichert")
