# Master-Prompt: Lotwerk-Betriebssystem aufbauen

> Lebendes Dokument. Wird bei jeder Änderung an Angebot, Preisen oder Abläufen fortgeschrieben.
> Verwendung: Den Abschnitt „Kontext“ + **eine** Stufe in eine neue Claude-Code-Sitzung kopieren.
> Immer nur eine Stufe pro Sitzung. Erst wenn eine Stufe läuft und abgenommen ist, die nächste starten.

---

## Kontext (immer mitgeben)

Du baust das interne Betriebssystem der Agentur **Lotwerk** (Arbeitsname). Lotwerk verkauft lokalen Betrieben
(Friseure, Barbershops, Dachdecker & Solar, Steuerberater, Pflegedienste, Bestatter, Tierarztpraxen)
Websites, lokale SEO, Google Ads, Recruiting-Kampagnen und ein Wachstumsprogramm. Der Gründer arbeitet allein
bis 10.000 € MRR, danach kommt ein Team.

**Ziel des Systems:** Der Gründer verkauft, entscheidet und gibt frei. Erstellung, Prüfung, Überwachung,
Berichte, Abrechnung und Kennzahlen laufen automatisiert oder werden von KI vorbereitet.

**Bestehendes Setup – nutze es, ersetze nichts ohne Grund:**
- GitHub: `MarvGo6/Agentur` (Agentur-Website, statisch, Python `build.py` → `dist/`, Vorschau-Generator `vorschau.py`,
  Finanzmodell `finanzen/`, Businessplan `businessplan/`, dieser Plan `betrieb/`)
- Vercel: Team „liferpg“, Projekt „lotwork“ (Deploy bei Push auf `main`)
- Supabase: Projekt „Lotwerk Agentur“ (`mlvraqrtejfwamwhyici`, eu-west-1). Tabelle `agentur_anfragen` + ntfy-Trigger existieren.
  Entwurf des Betriebs-Schemas: `betrieb/schema.sql`
- Cloudflare (DNS, Turnstile), ntfy (Push), Claude API
- **Nicht anfassen:** Supabase-Projekt des Vertriebs-OS (`mscipkkvljajnwjfabjv`) – anderes Geschäft, getrennt halten.

**Automatisierungen:** vollständige Liste mit Reihenfolge, Stunden-Ersparnis und Kosten in `betrieb/Automatisierungsplan.pdf`
(Quelle: `betrieb/automatisierung.py`). IDs dort (V1–V6, E1–E5, Ü1–Ü3, B1–B9, F1–F5, S1–S2) in Commits und PRs nennen.
Das Finanzmodell rechnet „von Hand“ und „automatisiert ab Kunde 5“; Recruiting wird erst ab Juni 2027 verkauft.

**Preise (Quelle der Wahrheit: `content.py` → `PREISE`):** Website Start 1.490 €, Website Wachstum 2.990 €,
Pflege 49/89 €/Monat, SEO Lokal 390 €, SEO Plus 690 €/Monat, Google Ads 390 € + 290 €/Monat,
Recruiting 1.490 € + 790 €/Monat, Wachstumsprogramm 1.490 € Einrichtung + 1.190 €/Monat (12 Monate).

**Unverhandelbare Regeln:**
1. KI veröffentlicht nie direkt auf eine Kunden-Website. Jede Änderung = Pull Request mit Vorschau-Link + Freigabe durch den Gründer.
2. KI erfindet keine Bewertungen, Zahlen, Zertifikate, Preise, Namen oder Zitate. Fehlendes wird `[PRÜFEN]` und blockiert den Launch.
3. Alle Daten in Supabase (EU). RLS auf jeder Tabelle. Service-Role-Schlüssel nur serverseitig. Geheimnisse nur in GitHub/Vercel/Supabase Secrets.
4. DSGVO: keine Tracker ohne Einwilligung, keine Google Fonts von Google-Servern, AV-Verträge, Löschfristen für Formulardaten (90 Tage).
5. Jede Automatisierung meldet Fehler per ntfy und legt eine Aufgabe im Dashboard an.
6. Deutsch in allen Oberflächen und Texten. Einfach, klar, keine Fachbegriffe ohne Erklärung.
7. Vor dem Bauen: bestehende Dateien lesen, auf GitHub/Vercel nach Änderungen von anderen Geräten prüfen.

---

## Stufe 1 – Grundbetrieb (ab Kunde 1)

1. `betrieb/schema.sql` prüfen und als Migration in „Lotwerk Agentur“ einspielen. Gründer als Admin eintragen.
2. Repo `lotwerk-sites` anlegen (Monorepo): `generator/` aus `vorschau.py` ableiten (Seitenaufbauten mosaic, fullbleed,
   bleed, type, cover, quiet, blob; Bausteine stats, services, split, steps, prices, team, quotes, faq, contact),
   `kunden/<slug>/kunde.json` nach `betrieb/kunde.beispiel.json`, JSON-Schema-Prüfung, Build je Kunde nach `kunden/<slug>/dist`.
3. GitHub Action **Abnahme-Prüfung** bei jedem PR: Lighthouse (Handy) ≥ 90 in allen Kategorien, axe ohne schwere Fehler,
   keine toten Links, Impressum + Datenschutz vorhanden, keine externen Fonts/Tracker, `LocalBusiness`-Schema gültig,
   kein `[PRÜFEN]` mehr im Inhalt. Ergebnis als Kommentar im PR und Zeile in `checks`.
4. Zentrale Formular-Funktion (Supabase Edge Function): speichert in `anfragen`, prüft Turnstile, leitet per E-Mail an den Kunden weiter, ntfy an Gründer.
5. Uptime/SSL/Domain-Checks (Supabase Cron oder GitHub Action, alle 5 Min. bzw. täglich) → `checks`, Fehler → ntfy + `aufgaben`.
**Fertig, wenn:** eine Beispiel-Kundenseite aus `kunde.json` gebaut, geprüft, auf Vercel live und überwacht ist.

## Stufe 2 – Dashboard v1 (ab Kunde 3)

Eigenes Repo `lotwerk-dashboard`, Next.js (App Router) + Supabase Auth, auf Vercel, nur Admins.
Seiten: **Cockpit** (MRR, Netto-Wachstum, Kündigungen, Kasse, offene Rechnungen, Auslastung in Std. von 170, Fortschritt zu 10.000 €),
**Pipeline** (Kanban über `interessenten.status`), **Kunden** (Verträge, Umsatz, Stunden, Deckungsbeitrag/Std.),
**Websites** (Status, Uptime, Lighthouse, Anfragen), **Aufgaben**, **Zeiten** (Start/Stopp-Knopf).
Außerdem **Auswertungen** (`berichte`, `seitenaufrufe`, `messwerte`), **Rechnungen**, **Zahlungen**, **Freigaben**, **Einstellungen**.
Lexware-Office-Abgleich (täglich): Rechnungen und Zahlstatus → `rechnungen`. GoCardless-Webhooks: Mandate, Einzüge, Rückläufer → `rechnungen` + `aufgaben`.
Plan-Werte aus `finanzen/modell.py` als Vergleichslinie.
**Zentrale Steuerung (Knöpfe, alle über serverseitige Route Handlers, Schlüssel nur in Vercel Secrets):**
Neue Website (kunde.json → Build → Vorschau, GitHub- + Vercel-API) · Live schalten / zurückrollen (Vercel-API) ·
Domain verbinden (Vercel- + Cloudflare-API) · Betrieb analysieren (Funktion `analyse`) · Angebot/Rechnung als Entwurf (Lexware-API) ·
Lastschrift anfragen/einziehen (GoCardless-API) · Monatsbericht senden (Funktion `bericht`) · Kündigung abwickeln (Laufzeitende, Export, Lastschrift stopp).
Jede Aktion schreibt eine Zeile in `aufgaben` oder `ki_laeufe` (Protokoll). Nichts geht ohne Freigabe live.
Mobil zuerst (der Gründer nutzt das iPhone), Dunkelmodus.
**Fertig, wenn:** der Gründer morgens in 2 Minuten sieht, was Geld bringt, was brennt und was freigegeben werden muss.

## Stufe 3 – KI-Erstellung (ab Kunde 5)

1. **Vorschau-Generator:** Eingabe Google-Place-ID + alte Website-URL → Claude (Opus) erzeugt `kunde.json`
   (nur belegbare Fakten, Rest `[PRÜFEN]`) → Build unter `vorschau-<slug>.<agentur-domain>` (noindex) → Eintrag in `interessenten` + `ki_laeufe`.
2. **Lead-Liste:** Google Places API je Branche + Stadt → `interessenten`, Schnell-Analyse (PageSpeed, Bewertungen, Handy-tauglich) → `potenzial` 0–100.
3. **Website-Erstellung nach Auftrag:** Inhalte-Formular des Kunden + Vorschau → finale `kunde.json` + Unterseiten (Leistung × Ort) als PR.
Kosten je Lauf in `ki_laeufe.kosten_eur` protokollieren.
**Fertig, wenn:** aus einer Place-ID in < 15 Minuten eine prüfbare Vorschau entsteht, ohne erfundene Inhalte.

## Stufe 4 – KI-Optimierung & Berichte (ab Kunde 8–10)

1. Monatslauf (1. des Monats): Search Console, PageSpeed, Statistik, Google-Profil → `messwerte`.
2. Claude schreibt je Kunde einen **Monatsbericht** (1 Seite, Klartext, PDF) → Freigabe im Dashboard → Versand.
3. Claude schlägt **max. 3 Verbesserungen** je Kunde vor → PRs mit Vorschau → Freigabe-Seite im Dashboard.
4. **KI-Sichtbarkeit:** monatlich „bester [Branche] in [Stadt]“ an mehrere KI-Assistenten, speichern ob der Kunde genannt wird (`messwerte.ki_genannt`).
5. Entwürfe für Antworten auf neue Google-Bewertungen.
**Fertig, wenn:** Betreuung je Kunde ≤ 4 Std./Monat und jeder Kunde pünktlich seinen Bericht bekommt.

## Stufe 5 – Team (ab 10.000 € MRR)

Rollen im Dashboard (Inhaber, Closer, Umsetzer), Closer sehen Pipeline + Provision, Umsetzer sehen Aufgaben + Zeiten.
Freigaben für Live-Änderungen bleiben beim Inhaber. Onboarding-Checklisten als Seiten im Dashboard.

---

## Bereits umgesetzt (Stand 2026-10-07)

- Supabase „Lotwerk Agentur“: Betriebs-Schema aus `betrieb/schema.sql` eingespielt (Interessenten, Kunden, Verträge, Rechnungen, Kosten, Zeiten, Websites, Checks, Messwerte, Aufgaben, KI-Läufe, Berichte, Seitenaufrufe, Einstellungen).
- Edge Functions in `supabase/functions/`: `monitor` (Erreichbarkeit täglich, PageSpeed montags), `analyse` (Website-Befund + Potenzial für Interessenten), `bericht` (Wochen-/Monatsbericht, Löschfrist Seitenaufrufe). Schutz über `x-cron-secret` aus Tabelle `einstellungen`.
- Datenbank-Jobs (pg_cron) über `public.funktion_starten(name)`: 05:15 UTC täglich, alle 30 Min., Mo 06:00 UTC, am 1. 06:30 UTC.
- Website zählt anonym Seitenaufrufe und Klicks (Tabelle `seitenaufrufe`, nur INSERT für anon). Kein Zugriff auf Gerätedaten (§ 25 TDDDG): nur Pfad + Ereignis, keine Cookies, kein Referrer, keine Bildschirmgröße → kein Banner nötig.
- Einwilligungs-Baustein für Kunden-Websites: `betrieb/bausteine/einwilligung.js` (nur einsetzen, wenn zustimmungspflichtige Dienste genutzt werden; Consent Mode v2, Zwei-Klick für Karten/Videos, Widerruf-Link). Getestet.
- `analyse` prüft zusätzlich: Tracking ohne Einwilligung, direkt eingebettete Karten/Videos, Impressum-/Datenschutz-Link.
- Abfragen: `betrieb/abfragen.sql`. Leistungen und Abnahme: `betrieb/Leistungshandbuch.pdf`.
- Offen: `psi_key` in `einstellungen` (Google PageSpeed API-Schlüssel).

## Änderungsprotokoll
- 2026-10-06: Erste Fassung (Stufen 1–5, Regeln, Setup, Preise inkl. Programm-Einrichtung 1.490 €, KI-Suche als Kennzahl).
- 2026-10-06: Datensammlung und Automatisierungen in Supabase umgesetzt, Leistungshandbuch ergänzt.
- 2026-10-07: Automatisierungsplan (30 Automatisierungen, 5 Phasen), Finanzmodell mit zwei Varianten, Recruiting ab Juni 2027.
- 2026-10-07: Cookie-Konformität (Zählung ohne Endgerätezugriff, Einwilligungs-Baustein, Analyse-Prüfungen), Dashboard als zentrale Steuerung erweitert.
