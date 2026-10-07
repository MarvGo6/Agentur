# Tracking & Rechtstexte – Anleitung

Alles läuft über `config.json`. Ein leerer Wert bedeutet: aus. Nach jeder Änderung `git push`, Vercel baut die Seite neu.

## Was schon läuft (ohne Einwilligung, ohne Banner)
- **Anonyme Zählung** (Tabelle `seitenaufrufe`): Aufrufe sowie Klicks auf Kontakt, Telefon und E-Mail, dazu abgeschickte Formulare.
- **Kampagnen-Quelle**: Kommt jemand über `?utm_source=…&utm_campaign=…`, einen Google-Anzeigen-Klick (`gclid`) oder einen Meta-Klick (`fbclid`), speichern wir nur die Quelle als Wort, also `google-ads / Kampagnenname`. Das landet in `seitenaufrufe.herkunft` und bei Anfragen in `agentur_anfragen.kampagne`. Es gibt keine Kennung und keine Cookies.
- Auswertung: `betrieb/abfragen.sql`, Abfrage 13. In der Steuerzentrale steht bei jeder Anfrage „über …“.
- **Tipp:** Links in Anzeigen, E-Mails und Social-Media-Profilen immer mit `utm_source` und `utm_campaign` versehen. Anzeigen am besten direkt auf `/kontakt/` oder eine eigene Zielseite leiten. Wechselt der Besucher die Seite, geht die Quelle ohne Einwilligung verloren.

## Einschalten, wenn es so weit ist
| Feld in `config.json` → `tracking` | Woher | Einwilligung nötig? |
|---|---|---|
| `search_console` | Google Search Console → Eigentum bestätigen → „HTML-Tag“ → nur den Code aus `content="…"` | nein |
| `bing` | Bing Webmaster Tools → „HTML Meta Tag“ → Code | nein |
| `ga4` | Google Analytics → Datenstream → Mess-ID `G-…` | ja |
| `google_ads` | Google Ads → Conversions → Tag einrichten → `AW-…` | ja |
| `ads_label_anfrage` | Conversion-Aktion „Anfrage“ → Label (Teil nach dem `/`) | – |
| `ads_label_anruf` | Conversion-Aktion „Anruf-Klick“ → Label | – |
| `meta_pixel` | Meta Events Manager → Pixel-ID (nur Ziffern) | ja |

Sobald `ga4`, `google_ads` oder `meta_pixel` eingetragen ist, passiert automatisch Folgendes:
- Das **Einwilligungs-Fenster** erscheint (`betrieb/bausteine/einwilligung.js`). Alle Knöpfe sind gleich gestaltet, nichts lädt vor der Zustimmung, Google Consent Mode v2 ist eingebaut.
- Im Fußbereich steht der Link **„Datenschutz-Einstellungen“** zum Widerrufen.
- Die **Datenschutzerklärung** bekommt Abschnitt 7 mit genau den eingetragenen Diensten.
- Die **Sicherheitsregeln (CSP)** lassen nur die Adressen dieser Dienste zu.
- **Messpunkte:** Anfrage = Aufruf der Danke-Seite, außerdem Klicks auf Telefon, E-Mail und Kontakt. Google Ads meldet die Conversion „Anfrage“ bzw. „Anruf“, GA4 meldet `generate_lead`, `anruf_klick`, `mail_klick` und `kontakt_klick`, Meta meldet `Lead` und `Contact`.
- **Google-Klick-Kennung:** Hat der Besucher Google Ads zugestimmt, speichern wir bei der Anfrage die `gclid`. Daraus wird später ein **Offline-Conversion-Import**: Google erfährt, welche Anzeige echte Aufträge bringt, nicht nur Anfragen. Die Liste liefert Abfrage 14.

## Vorher erledigen
1. Bei Google und Meta den **Auftragsverarbeitungsvertrag bzw. die Datenverarbeitungsbedingungen** in den Konto-Einstellungen bestätigen.
2. In GA4 die Speicherdauer auf 14 Monate stellen und den Platzhalter in der Datenschutzerklärung ersetzen (`build.py` → `ds_dienste`).
3. Google Ads: „Erweiterte Conversions“ erst einmal **aus** lassen, denn dabei würden E-Mail-Adressen gehasht übertragen.

## Rechtstexte – Platzhalter
- **Impressum und Datenschutz:** Angaben in `config.json` → `impressum` (`inhaber`, `strasse`, `ort`, `telefon`, optional `ustid`, `register`). Was noch in `[…]` steht, erscheint auf der Seite orange markiert.
- **AGB** (`/agb/`): Der Entwurf stammt aus den Vertragsbausteinen des Leistungshandbuchs. Offen sind noch Zahlungsziel und Abrechnungsweise der Monatsbeträge. **Vor dem Livegang anwaltlich prüfen lassen**, vor allem die Verlängerungsklausel, die Abnahme durch Schweigen und die Haftung. Danach den orangen Hinweis in `build.py` entfernen.
- Umsatzsteuer: Zurzeit steht dort Kleinunternehmer (`impressum.ust`). Fällt das weg, den Text ändern und `ustid` eintragen.
