# Lotwerk – Agentur-Website

Statische Website (32 Seiten), erzeugt mit Python ohne Abhängigkeiten.

- `config.json` – Name, Domain, E-Mail, Impressumsdaten, `preview` (true = noindex)
- `content.py` – alle Texte, Preise, Beispiele mit Kundenweg
- `drawings.py` – SVG-Zeichnungen
- `static/` – CSS, JS, Schriften (lokal, DSGVO-freundlich)
- `build.py` – baut nach `dist/`

```bash
python3 build.py      # baut dist/
```

Vercel: Build Command `python3 build.py`, Output Directory `dist`.
Vor dem Livegang: Impressum in `config.json` ausfüllen, `preview` auf `false`, eigene Domain eintragen.
