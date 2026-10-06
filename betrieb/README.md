# Lotwerk Betrieb – Plan für Automatisierung, Kontrolle und Dashboard

Interner Plan, **nicht Teil der Website** (`build.py` liest diesen Ordner nicht).
Ziel: Website-Erstellung, Überwachung, Optimierung, Abrechnung und Kontrolle so aufbauen,
dass ein Mensch (du) nur noch **entscheidet und freigibt** – den Rest erledigen Skripte und KI.

Stand: Oktober 2026 · Preise der Tools sind ca.-Werte, vor Abschluss prüfen.

---

## 1. Grundprinzipien

1. **Ein System, eine Datenquelle.** Alles, was du tracken willst, landet in *einer* Datenbank
   (Supabase-Projekt „Lotwerk Agentur“). Das Dashboard liest nur von dort.
2. **KI schlägt vor, Mensch gibt frei.** Keine KI veröffentlicht direkt auf einer Kunden-Website.
   Jede Änderung ist ein Pull Request auf GitHub mit Vorschau-Link → du klickst „Freigeben“.
3. **Alles ist Konfiguration.** Eine Kunden-Website = eine Datei `kunde.json` + Fotos.
   Der Generator (Weiterentwicklung von `vorschau.py`) baut daraus die Seite. KI füllt die Datei, nicht den Code.
4. **Getrennt von Vertriebs-OS.** Das Vertriebs-OS (eigenes Supabase-Projekt) bleibt unangetastet.
   Falls später gewünscht: nur lesender Abgleich, keine gemeinsame Datenbank.
5. **Erst manuell, dann automatisieren.** Jeder Schritt läuft 3–5 Mal von Hand mit Checkliste,
   bevor er automatisiert wird. Automatisiert wird, was Zeit frisst – nicht, was Spaß macht.

---

## 2. Gesamtbild

```
             ┌────────────── DASHBOARD (Next.js auf Vercel, nur du) ──────────────┐
             │ Kunden · MRR · Cash · Aufgaben · Websites · Leads · Stunden · KI   │
             └───────────────────────────────▲────────────────────────────────────┘
                                             │ liest/schreibt
                         ┌───────────────────┴───────────────────┐
                         │  SUPABASE „Lotwerk Agentur“ (EU)       │
                         │  Tabellen · Edge Functions · Cron      │
                         └──▲──────▲──────▲──────▲──────▲─────────┘
                            │      │      │      │      │
   A Akquise/Vorschau ──────┘      │      │      │      └────── E Finanzen
   B Auftrag → Launch ─────────────┘      │      └───────────── D Optimierung (KI)
                                          C Überwachung
   Ausführung: GitHub Actions (Builds, KI-Läufe, Checks) · Vercel (Hosting) · Cloudflare (DNS, Spam-Schutz)
   Meldungen: ntfy (Push aufs Handy) · E-Mail
```

---

## 3. Werkzeuge (Stack)

| Bereich | Werkzeug | Warum | Kosten ca. |
|---|---|---|---|
| Code & Freigaben | **GitHub** (vorhanden) | Jede Änderung als PR, Actions als Automatisierung | 0 € (Free reicht lange) |
| Hosting Kunden-Sites | **Vercel Pro** (vorhanden, Plan hochstufen) | Hobby-Plan ist **nicht für kommerzielle Nutzung** erlaubt → spätestens mit erstem zahlenden Kunden auf Pro | 20 $/Monat je Teammitglied |
| Datenbank, Login, Cron | **Supabase Pro** (vorhanden) | Free pausiert bei Inaktivität, keine Backups → für Kundendaten Pro | 25 $/Monat |
| DNS, Spam-Schutz | **Cloudflare** (vorhanden) | DNS gratis, Turnstile statt Captcha (DSGVO-freundlich) | 0 € |
| Domains .de | **INWX** (API) | Cloudflare verkauft keine .de-Domains | ca. 5–10 €/Jahr je Domain |
| KI | **Claude API** – Opus für Texte/Struktur, Haiku für Massen-Checks | Text, Code-Vorschläge, Auswertungen | ca. 2–10 € je Website-Erstellung, < 1 € je Monatslauf |
| Statistik Kunden-Sites | **Plausible** (EU) oder **Umami** selbst gehostet | Ohne Cookie-Banner, API fürs Dashboard | Plausible ab ca. 9 €/Monat |
| Such-Daten | **Google Search Console API**, **PageSpeed Insights API** | Rankings, Klicks, Ladezeit – kostenlos | 0 € |
| Google-Profil | **Google Business Profile API** (Antrag nötig) | Anrufe, Routen, Bewertungen | 0 € |
| Uptime | **Eigene Checks** (GitHub Actions/Supabase Cron) oder **Better Stack** | Seite erreichbar? SSL gültig? Formular geht? | 0–25 €/Monat |
| Meldungen | **ntfy** (vorhanden) | Push aufs Handy | 0 € |
| E-Mails (Formulare, Berichte) | **Brevo** oder **Resend** | Formular-Anfragen an Kunden, Monatsbericht | 0–20 €/Monat |
| Buchhaltung | **Lexware Office** (früher lexoffice) | Angebote, wiederkehrende Rechnungen, Belege, DATEV-Export für den Steuerberater, API | ca. 10–25 €/Monat |
| Zahlungseinzug | **GoCardless** (SEPA-Lastschrift) oder **Stripe** | Monatsbeträge automatisch einziehen | ca. 1 % + Fixbetrag je Zahlung |
| Bank | Geschäftskonto mit API (z. B. Qonto) | Kontoumsätze automatisch in Lexware Office | ca. 10–30 €/Monat |
| Verträge | **Docuseal** (selbst gehostet) oder **Yousign** (EU) | Angebot + AV-Vertrag digital unterschreiben | 0–30 €/Monat |
| Zeiterfassung | Eigene Tabelle im Dashboard (Start/Stopp-Knopf) | Stunden je Kunde → echter Verdienst je Stunde | 0 € |

Laufende Grundkosten am Anfang: **ca. 80–150 €/Monat**. Im Finanzmodell sind 205 € Fixkosten angesetzt – passt.

---

## 4. Die fünf Abläufe

### A · Akquise → Vorschau in 48 Stunden
| Schritt | Wer | Wie |
|---|---|---|
| 1. Betriebe finden | Skript | Liste aus Google Maps (Places API) je Branche + Stadt → Tabelle `interessenten` |
| 2. Schnell-Analyse | Skript + KI (Haiku) | PageSpeed-Wert, Handy-tauglich?, Bewertungen, Website vorhanden? → Punktzahl „Potenzial“ |
| 3. Vorschau erzeugen | KI (Opus) | Liest Google-Profil + alte Website → schreibt `kunde.json` (Texte, Leistungen, Farben) |
| 4. Bauen | GitHub Action | Generator baut `vorschau-<name>.lotwerk.de` (noindex) |
| 5. Prüfen & senden | **du** | Vorschau ansehen, ggf. korrigieren, Nachricht raus. Dashboard merkt sich: gesendet am … |

Messgrößen: Vorschauen/Woche, Antwortquote, Termine, Abschlussquote.

### B · Auftrag → Launch (Ziel: 21 Tage, davon < 8 h deine Zeit)
1. **Angebot** aus Vorlage (Lexware Office) → digital unterschrieben inkl. **AV-Vertrag** → Status „gewonnen“.
2. **Rechnung 1** (50 %) automatisch, **Lastschrift-Mandat** für Monatsbeträge.
3. **Inhalte-Formular** an den Kunden (Fotos, Leistungen, Preise, Team, Zugänge Google-Profil).
4. **KI baut** aus Formular + Vorschau die finale `kunde.json` und alle Unterseiten (Leistung × Ort).
5. **Automatische Abnahme-Prüfung** (GitHub Action, muss grün sein):
   - Lighthouse ≥ 90 in allen vier Kategorien (Handy)
   - Barrierefreiheit (axe), tote Links, Bilder mit Alt-Text
   - Impressum + Datenschutz vorhanden, keine Google-Fonts/Tracker ohne Einwilligung
   - Formular-Test (Testanfrage kommt an), strukturierte Daten (LocalBusiness) gültig
6. **du**: Entwurf ansehen → Kunde gibt frei → Rechnung 2.
7. **Domain** (INWX) + DNS (Cloudflare) + Vercel → live. Search Console, Statistik, Uptime werden automatisch angelegt.

### C · Überwachung (läuft ohne dich)
| Rhythmus | Prüfung | Bei Problem |
|---|---|---|
| alle 5 Min. | Seite erreichbar | Push sofort |
| täglich | SSL gültig, Domain-Ablauf, Formular-Testanfrage, Vercel-Build ok | Push + Aufgabe |
| wöchentlich | PageSpeed (Handy), Search-Console-Fehler, neue Bewertungen | Aufgabe im Dashboard |
| monatlich | Rankings, Klicks, Anrufe, Anfragen je Kunde | → Bericht (D) |

### D · Optimierung & Monatsbericht (KI)
- Am 1. jedes Monats sammelt ein Lauf alle Zahlen je Kunde.
- KI schreibt **Monatsbericht in Klartext** (1 Seite: was lief, was wir tun) → du liest 2 Min., Versand automatisch.
- KI schlägt **max. 3 Verbesserungen** vor (z. B. neue Ortsseite, besserer Seitentitel, FAQ aus Suchanfragen)
  → als **Pull Request mit Vorschau** → du gibst frei.
- **Bewertungsantworten**: KI entwirft, du oder der Kunde gibt frei.
- **KI-Sichtbarkeit**: monatlich fragt ein Skript ChatGPT/Gemini/Claude „bester [Branche] in [Stadt]“ und speichert, ob der Kunde genannt wird → eigene Kennzahl.

### E · Finanzen & Verwaltung
- **Wiederkehrende Rechnungen** (Pflege, SEO, Programm, Recruiting) in Lexware Office, Einzug per Lastschrift.
- Lexware Office → Dashboard (täglich): Umsätze, offene Posten, Mahnstufe.
- **Kosten je Kunde** (Vercel, Domain, KI-Verbrauch, Werbebudget-Durchlauf) + **Stunden je Kunde** → Deckungsbeitrag je Kunde.
- Belege per Foto/E-Mail in Lexware Office; Steuerberater bekommt DATEV-Export (monatlich).
- **Kündigung**: Ablauf-Checkliste (Website-Export/Repo-Übergabe, Domain-Transfer, Lastschrift stoppen) – „Website gehört Ihnen“ wird eingehalten.

---

## 5. Website-Generator: wie KI Websites baut, ohne Chaos

- **Ein Repo `lotwerk-sites`** (Monorepo): `generator/` (aus `vorschau.py` entwickelt), `kunden/<slug>/kunde.json`, `kunden/<slug>/fotos/`.
- **Ein Vercel-Projekt je Kunde**, Root-Verzeichnis = `kunden/<slug>`. Vorteil: Generator-Update verbessert alle Seiten, jede Seite deployt einzeln.
- **Branchen-Bausteine** statt Freitext: Seitenaufbau (mosaic, fullbleed, bleed, type, cover, quiet, blob – wie jetzt in den Vorschauen), Abschnitte, Formulare. KI wählt und befüllt, erfindet keinen Code.
- `kunde.json` hat ein **festes Schema** (siehe `kunde.beispiel.json`). Die KI-Ausgabe wird dagegen geprüft – ungültig = kein Build.
- **Leitplanken für die KI**: keine erfundenen Bewertungen, Zahlen, Zertifikate oder Preise. Alles, was nicht aus Kundenangaben stammt, wird als `[PRÜFEN]` markiert und blockiert den Launch.
- Formulare aller Kunden-Seiten schreiben in **eine** Tabelle `anfragen` (mit `website_id`) → Weiterleitung per E-Mail an den Kunden + Zähler im Dashboard (Beleg für den Monatsbericht).

---

## 6. Dashboard

Eigene kleine App (Next.js auf Vercel, Login per Supabase Auth, nur du; später Team mit Rollen).

| Seite | Inhalt | Datenquelle |
|---|---|---|
| **Cockpit** | MRR, Neukunden/Kündigungen, Cash, offene Rechnungen, Auslastung (Std. von 170), Ziel 10k-Fortschritt | `vertraege`, `rechnungen`, `zeiten` |
| **Pipeline** | Interessenten → Vorschau → Termin → Angebot → gewonnen/verloren, Quoten je Stufe | `interessenten`, `angebote` |
| **Kunden** | je Kunde: Verträge, Umsatz, Stunden, Deckungsbeitrag/Std., letzte Aktivität | `kunden`, `vertraege`, `zeiten`, `kosten` |
| **Websites** | Status, Uptime, Lighthouse, Ladezeit, Anfragen, Klicks, Rankings, KI-Nennung | `websites`, `checks`, `messwerte`, `anfragen` |
| **Aufgaben** | automatisch erzeugt (Fehler, Freigaben, Fristen) + eigene | `aufgaben` |
| **Freigaben** | offene KI-Vorschläge (PR-Link, Vorschau-Link, „Freigeben/Ablehnen“) | `ki_laeufe` |
| **Finanzen** | Umsatz/Kosten/Ergebnis je Monat, Plan vs. Ist (aus dem Finanzmodell) | `rechnungen`, `kosten`, Plan-Werte |
| **Zeiten** | Start/Stopp je Kunde und Tätigkeit | `zeiten` |

Entwurf der Tabellen: `schema.sql` (lokal mit PostgreSQL getestet, im Supabase-Projekt noch **nicht** eingespielt).

Wichtigste Kennzahlen, die automatisch berechnet werden:
MRR · Netto-MRR-Wachstum · Kündigungsrate · Kundengewinnungskosten · Deckungsbeitrag je Kunde und je Stunde ·
Auslastung · Tage bis Launch · Anfragen je Kunden-Website · Uptime · Ø Lighthouse · KI-Kosten je Kunde.

---

## 7. Ausbaustufen (passend zum Solo-Plan)

| Stufe | Wann | Was |
|---|---|---|
| **0 – Jetzt** | vor dem 1. Kunden | Name/Domain festlegen, Lexware Office + Geschäftskonto, Vorlagen (Angebot, AV-Vertrag, AGB), Checklisten A–E als Markdown, `schema.sql` einspielen |
| **1 – Grundbetrieb** | 1.–3. Kunde | Vercel Pro, Supabase Pro, Monorepo `lotwerk-sites`, Abnahme-Prüfung (B5) als GitHub Action, Uptime + ntfy, wiederkehrende Rechnungen |
| **2 – Dashboard v1** | ab 3 Kunden | Cockpit, Kunden, Websites, Aufgaben, Zeiten; Lexware-Abgleich |
| **3 – KI-Erstellung** | ab 5 Kunden | Vorschau-Generator (A3/A4), KI baut Unterseiten (B4), Schema-Prüfung |
| **4 – KI-Optimierung** | ab 8–10 Kunden | Monatsbericht automatisch, Verbesserungs-PRs, KI-Sichtbarkeits-Messung |
| **5 – Team** | ab 10.000 € MRR | Rollen im Dashboard, Closer sehen Pipeline, Umsetzer sehen Aufgaben; Freigaben bleiben bei dir |

Zeitgewinn-Ziel: Launch einer Website von ca. 24–28 h (Finanzmodell) auf **8–10 h** deiner Zeit,
Pflege je Kunde/Monat von 6–13 h auf **2–4 h**. Das hebt die Solo-Obergrenze deutlich über 14.000 € MRR.

---

## 8. Sicherheit & Datenschutz

- Geheimnisse (API-Schlüssel) nur in GitHub Secrets / Vercel / Supabase – nie im Code.
- Service-Role-Schlüssel nur serverseitig; Dashboard nur mit Login, RLS auf allen Tabellen.
- **AV-Verträge** mit allen Dienstleistern abschließen, die Kundendaten sehen: Vercel, Supabase, Anthropic, Lexware, Plausible, E-Mail-Anbieter.
- Formulardaten der Kunden: Speicherdauer festlegen (z. B. 90 Tage), danach automatisch löschen.
- KI bekommt keine personenbezogenen Daten aus Anfragen – nur Zahlen und Website-Inhalte.
- Tägliche Datenbank-Backups (Supabase Pro) + Repo = Backup aller Websites.

---

## 9. Nächste konkrete Schritte

1. Name + Domain festlegen (danach Impressum, `noindex` aus, E-Mail-Adresse).
2. Lexware Office + Geschäftskonto eröffnen, Vorlagen anlegen.
3. `schema.sql` prüfen und ins Supabase-Projekt „Lotwerk Agentur“ einspielen (sag Bescheid, dann mache ich das).
4. Beim ersten zahlenden Kunden: Vercel auf Pro, Supabase auf Pro.
5. Dashboard v1 bauen (Cockpit + Kunden + Aufgaben) – eigenes Repo `lotwerk-dashboard`.
