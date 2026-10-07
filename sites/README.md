# Kunden-Websites: Generator, Prüfung, Livegang, KI

| Schritt | Befehl | Was passiert |
|---|---|---|
| 1. Inhalte einsammeln | Steuerzentrale `/intern/` → Kunden → „Inhalte-Link erzeugen“ | Kunde füllt `/inhalte/?t=…` aus, lädt Fotos hoch; Push + Aufgabe, sobald abgeschickt |
| 2. Texte schreiben (KI) | `python3 sites/ki_texte.py kunden/<slug> --token <token>` | Claude schreibt die Texte in `kunden/<slug>/kunde.json`; Fakten 1:1 aus dem Formular, Lücken = `[PRÜFEN]` |
| 3. Fotos | in `kunden/<slug>/fotos/` legen (aus Supabase-Speicher „inhalte“) | im JSON z. B. `"hero": {"foto": {"datei": "team.jpg", "alt": "…"}}` |
| 4. Bauen | `python3 sites/generator.py kunden/<slug>` | `kunden/<slug>/dist/` – Startseite, Leistungsseiten, Ortsseiten (nur mit eigenem Text), Karriere, Impressum, Datenschutz, Sitemap |
| 5. Prüfen | `python3 sites/pruefung.py kunden/<slug>/dist` | blockiert bei `[PRÜFEN]`, fehlenden Rechtstexten, externen Diensten, Cookies, toten Links, Handy-Überlauf, JS-Fehlern; Lighthouse in der GitHub Action |
| 6. Live | `python3 sites/livegang.py kunden/<slug> --probe`, dann ohne `--probe` | Vercel-Projekt, Domain + www, DNS (Cloudflare automatisch), Überwachung auf „live“ |

Jede Änderung an `kunden/**` läuft als Pull Request durch die Action **Kunden-Websites prüfen**.

## kunde.json – wichtigste Felder
`slug`, `domain`, `branche`, `vorlage` (Design: `friseur`, `barber`, `dachdecker-solar`, `steuerberater`, `pflegedienst`, `bestatter`, `tierarzt`),
`schema_typ` (z. B. `RoofingContractor`), `firma{name, claim, adresse{strasse, plz, ort}, telefon, email, oeffnungszeiten[]}`,
`marke{farben{brand, …}, mark}`, `seo{title, description}`, `hero{eb, h1, lead, chips[], foto}`, `cta`, `einzugsgebiet[]`,
`leistungen[{slug, titel, icon, kurz, text, punkte[], faq[[f,a]], seo_description, ortstexte{Ort: Text}}]`, `ueber`, `ablauf[[t,x]]`, `faq[[f,a]]`,
`team[{name, rolle}]`, `bewertungen[{text, name, quelle}]` (nur echte, mit Erlaubnis), `vertrauen{bewertung, bewertungen, quelle, siegel[]}`,
`formular{schluessel}` (aus der Steuerzentrale → Websites), `recruiting{aktiv, stellen[], text, vorteile[]}`,
`rechtliches{impressum{inhaber|vertreten, rechtsform, register, ust_id|ust_hinweis, kammer}}`,
`tracking{dienste[]}` (nur mit Einwilligungs-Baustein, siehe `betrieb/bausteine/einwilligung.js`).
Muster: `kunden/_muster/kunde.json` (erfunden, besteht die Prüfung).

## KI-Läufe (Claude, Modell `claude-opus-5-5`)
- `vorschau_ki.py` – V3: nachts Vorschauen für die besten Interessenten (Action **Nachtschicht**), erscheinen unter `/v/<slug>-<zufall>/` (noindex).
- `betreuung_ki.py beitraege | sichtbarkeit | verbesserungen` – B3/B7/B5 monatlich (Action **Betreuung**).
- Alle Ergebnisse sind Entwürfe: Freigabe in der Steuerzentrale bzw. per Pull Request. Kosten je Lauf stehen in `ki_laeufe`.
