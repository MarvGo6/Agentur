# Lotwerk – Agentur (Arbeitsname)

Digitale Agentur ohne Gesicht für lokale Betriebe (Friseure, Barbershops, Dachdecker & Solar, Steuerberater, Pflegedienste, Bestatter, Tierarztpraxen).
Gründer: Marvin (GitHub MarvGo6), allein bis 10.000 € MRR. Sprache überall: Deutsch, einfach, ohne Fachbegriffe.

## Arbeitsweise
- Umsetzen statt nachfragen. Vorhandene Verbindungen nutzen (GitHub, Vercel, Supabase, Cloudflare).
- Vor jeder Arbeit `git pull origin main` – es wird auch von anderen Geräten gearbeitet.
- Nichts erfinden (Zahlen, Bewertungen, Kunden, Zitate). Fehlendes als `[PRÜFEN]` bzw. `todo()` markieren.
- Commits direkt auf `main`, danach `git push origin main` (Vercel baut automatisch).

## Aufbau
- Agentur-Website: `build.py` → `dist/` (statisch), Inhalte in `content.py`, Stil `static/style.css`, Skripte `static/*.js`. Vercel-Projekt „lotwork“ (Team liferpg) → https://lotwork.vercel.app
- Steuerzentrale: `/intern/` (`static/intern.js`, Supabase Auth, nur Admins). Bereich „Links“ = Tabelle `links` (wichtige Links, archivieren statt löschen). Kundenformular: `/inhalte/` (`static/inhalte.js`).
- Supabase-Projekt **„Lotwerk Agentur“ `mlvraqrtejfwamwhyici`** (eu-west-1). NICHT anfassen: `mscipkkvljajnwjfabjv` (Vertriebs-OS, anderes Geschäft).
  - Schema: `betrieb/schema.sql`; Edge Functions: `supabase/functions/*` (gemeinsamer Code `_shared/db.ts`, beim Deploy als `db.ts` mitschicken; `verify_jwt: false`, Schutz über Header `x-cron-secret`).
  - Zeitpläne über `public.funktion_starten(name, query)` (pg_cron). Push über ntfy. Schlüssel in Tabelle `einstellungen`.
  - SQL mit `drop`/`delete` hängt im Supabase-Connector an einer Bestätigung → vermeiden oder den Nutzer bitten; Löschungen laufen über REST in den Funktionen.
  - Aus dem Container ist `*.supabase.co` gesperrt → Funktionen per `net.http_post` aus SQL testen.
- Kunden-Websites: `sites/` (Generator, Abnahme-Prüfung, Livegang, KI-Skripte), Kunden in `kunden/<slug>/kunde.json`, Anleitung `sites/README.md`.
- Planung: `betrieb/` (**Firmenübersicht** `uebersicht.py` = Zusammenfassung von allem inkl. Widersprüche/Lücken; Betriebsplan, Leistungshandbuch, Automatisierungsplan – PDFs werden aus den .py-Dateien erzeugt), `betrieb/PROMPT.md` (Master-Prompt, Stand „Bereits umgesetzt“), Finanzmodell `finanzen/` (Python + Excel mit Formeln, Varianten von Hand / automatisiert ab Kunde 5).
- PDFs/Screenshots: Node-Playwright (`NODE_PATH=$(npm root -g)`), kein Python-Playwright installiert.

## Offene Punkte (Stand 07.10.2026)
- Schlüssel fehlen: Claude (`anthropic_key` + GitHub-Secret `ANTHROPIC_API_KEY`), `SUPABASE_SERVICE_KEY` (GitHub-Secret), `places_key`, `psi_key`, `resend_key` + `mail_absender`.
- Google Business Profile API und Google-Ads-Token beantragen (B1, B3, B4, B6).
- Supabase Auth: Site URL auf `https://lotwork.vercel.app/intern/` setzen.
- Rechnungen/Lastschrift (Lexware Office, GoCardless) bewusst später.
- Website-Platzhalter: Telefon, Standort, Name, Anschrift (`config.json` → `impressum`); AGB-Entwurf `/agb/` anwaltlich prüfen (Zahlungsziel/Abrechnung ergänzen).
- Tracking: IDs in `config.json` → `tracking` eintragen, wenn Konten stehen (Anleitung `betrieb/TRACKING.md`).
- Entscheiden: Umsatzsteuer (Kleinunternehmer endet laut Plan Aug/Sep 27 – Steuerberater) und Weg ab Juli 2027 (allein mit System oder Team), siehe Firmenübersicht Kap. 13.
- Testdaten löschen (anfragen „TEST Claude“, inhalte_formulare „TEST …“, Speicher „inhalte“).
