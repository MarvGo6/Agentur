"""Alle Inhalte der Website. Preise stehen nur hier und werden überall daraus gerechnet."""

PREISE = {
    "web_start": 1490, "pflege_start": 49,
    "web_wachstum": 2990, "pflege_wachstum": 89,
    "seo_lokal": 390, "seo_plus": 690,
    "ads_setup": 390, "ads": 290,
    "prog_setup": 1490, "programm": 1190,
    "rec_setup": 1490, "rec": 790,
}

def eur(v):
    return f"{v:,.0f}".replace(",", ".") + " €"

# ---------------------------------------------------------------- Leistungen
LEISTUNGEN = [
 {"slug": "google-ads", "key": "ads", "titel": "Google Ads", "kurz": "Anzeigen, die bei Suchanfragen mit Kaufabsicht erscheinen – mit festem Budget und klarer Auswertung.",
  "h1": "Google Ads, die Anfragen bringen statt Klicks zu sammeln",
  "lead": "Wer „Dachdecker Notdienst“ oder „Steuerberater in der Nähe“ sucht, will jetzt handeln. Genau dort schalten wir Ihre Anzeigen – mit einem Budget, das Sie festlegen, und einem Bericht, den Sie verstehen.",
  "punkte": ["Kampagnen nur auf Suchbegriffe mit Kaufabsicht", "Eigene Zielseite pro Kampagne statt Startseite", "Ausschlussliste gegen teure Fehlklicks", "Anruf- und Formularmessung ohne Cookie-Banner-Chaos", "Monatlicher Bericht: Kosten pro Anfrage, nicht nur Klicks", "Monatlich kündbar nach der Einrichtung"],
  "ablauf": [("Suchbegriffe prüfen", "Wir schauen, wonach Ihre Kunden tatsächlich suchen und was ein Klick dort kostet."), ("Zielseite bauen", "Jede Kampagne bekommt eine Seite, die genau ein Anliegen beantwortet."), ("Start mit kleinem Budget", "Zwei bis vier Wochen lernen, dann umschichten auf das, was Anfragen bringt."), ("Monatlich nachschärfen", "Begriffe, Gebote und Texte werden laufend verbessert.")],
  "preis": "Einrichtung 390 € einmalig, Betreuung 290 € im Monat zzgl. Werbebudget, das direkt an Google geht.",
  "faq": [("Wie hoch sollte das Werbebudget sein?", "Für lokale Betriebe reichen oft 300 bis 900 € im Monat. Vor dem Start rechnen wir mit Ihnen anhand echter Klickpreise aus, was realistisch ist."), ("Bekommen Sie einen Anteil vom Budget?", "Nein. Das Budget zahlen Sie direkt an Google. Unsere Betreuung ist ein fester Betrag."), ("Wann sehe ich Ergebnisse?", "Anzeigen laufen ab Tag eins. Belastbare Zahlen gibt es meist nach drei bis sechs Wochen.")]},
 {"slug": "seo", "key": "seo", "titel": "SEO & lokale Sichtbarkeit", "kurz": "Bei Google und Maps oben stehen, wenn Menschen in Ihrer Region nach Ihnen suchen.",
  "h1": "Gefunden werden, wenn jemand in Ihrer Stadt sucht",
  "lead": "Die meisten Aufträge lokaler Betriebe beginnen mit einer Suche und einem Blick auf die Karte. Wir sorgen dafür, dass Sie dort auftauchen – mit sauberer Technik, guten Inhalten und einem gepflegten Google-Unternehmensprofil.",
  "punkte": ["Google-Unternehmensprofil vollständig einrichten und pflegen", "Eine Seite pro Leistung und Ort statt einer langen Leistungsliste", "Technische Prüfung: Ladezeit, Mobilansicht, strukturierte Daten", "Bewertungen systematisch einholen und beantworten", "Einträge in relevanten Verzeichnissen vereinheitlichen", "Monatlicher Bericht mit Rankings, Anrufen und Routenanfragen"],
  "ablauf": [("Bestandsaufnahme", "Wo stehen Sie heute, wo Ihre drei stärksten Mitbewerber?"), ("Grundlagen", "Profil, Technik, Verzeichnisse – die Dinge, die schnell wirken."), ("Inhalte", "Jeden Monat neue oder bessere Seiten zu Leistungen und Fragen Ihrer Kunden."), ("Vertrauen", "Bewertungen, Fotos, Antworten – damit aus Sichtbarkeit Anfragen werden.")],
  "preis": "SEO Lokal 390 € im Monat, SEO Plus 690 € im Monat. Mindestlaufzeit sechs Monate, danach monatlich kündbar.",
  "faq": [("Warum sechs Monate Mindestlaufzeit?", "Suchmaschinen brauchen Zeit, Änderungen zu bewerten. Die ersten Effekte sieht man oft nach acht bis zwölf Wochen, stabile Ergebnisse nach etwa einem halben Jahr."), ("Garantieren Sie Platz eins?", "Nein, das kann seriös niemand. Wir legen vorher messbare Ziele fest und berichten jeden Monat offen, wie weit wir sind."), ("Brauche ich dafür eine neue Website?", "Nicht unbedingt. Ist die bestehende Seite technisch in Ordnung, arbeiten wir damit.")]},
 {"slug": "webentwicklung", "key": "web", "titel": "Websites & Webentwicklung", "kurz": "Schnelle, klare Websites, die erklären, überzeugen und Anfragen auslösen.",
  "h1": "Websites, die schnell laden und Anfragen auslösen",
  "lead": "Eine gute Website beantwortet in zehn Sekunden drei Fragen: Was machen Sie, für wen, und wie erreiche ich Sie? Wir bauen Seiten, die genau das tun – schnell, barrierearm, ohne Baukasten-Ballast.",
  "punkte": ["Fertig in zwei bis vier Wochen", "Ladezeit unter einer Sekunde auf dem Handy", "Texte schreiben wir mit Ihnen – Sie liefern Stichworte", "Rechtssichere Grundstruktur ohne unnötige Cookies", "Pflege, Updates und Hosting zum festen Monatspreis", "Auf Wunsch Termin-, Bewerbungs- oder Anfrageformulare"],
  "ablauf": [("Gespräch", "30 Minuten: Ziele, Zielgruppe, Wunschanfragen."), ("Entwurf", "Nach einer Woche sehen Sie die Startseite im Browser."), ("Ausbau", "Alle Seiten, Texte, Bilder, Formulare."), ("Start & Pflege", "Freischaltung, Einrichtung bei Google, danach laufende Pflege.")],
  "preis": "Website Start ab 1.490 €, Website Wachstum ab 2.990 € einmalig. Pflege & Hosting 49 € bzw. 89 € im Monat.",
  "faq": [("Gehört mir die Website?", "Ja. Inhalte, Texte und Domain gehören Ihnen. Wenn Sie gehen, bekommen Sie alle Dateien."), ("Kann ich selbst Texte ändern?", "Ja. Kleine Änderungen machen wir im Rahmen der Pflege, auf Wunsch richten wir eine einfache Bearbeitung ein."), ("Was ist mit Fotos?", "Am besten echte Fotos von Ihnen und Ihrem Team. Wir sagen Ihnen genau, welche Motive wir brauchen.")]},
 {"slug": "recruiting", "key": "recruiting", "titel": "Recruiting-Paket", "kurz": "Fachkräfte finden über die eigene Karriereseite, Bewerbung in 60 Sekunden und Anzeigen im Umkreis.",
  "h1": "Bewerbungen von Fachkräften – ohne teure Stellenportale",
  "lead": "Pflegekräfte, Gesellen und Fachangestellte suchen nicht auf Portalen, sondern scrollen abends durch ihr Handy. Wir holen sie dort ab: mit einer Karriereseite, die zeigt, wie es bei Ihnen wirklich ist, einer Bewerbung ohne Lebenslauf und gezielten Anzeigen im Umkreis.",
  "punkte": ["Karriereseite mit Gehaltsrahmen, Team und echten Einblicken", "Bewerbung in 60 Sekunden – ohne Lebenslauf und Anschreiben", "Stellen erscheinen in Google Jobs (strukturierte Daten)", "Anzeigen auf Instagram, Facebook und Google im Umkreis von 20–30 km", "Jede Bewerbung sofort per E-Mail oder WhatsApp an Sie", "Monatlicher Bericht: Bewerbungen, Kosten je Bewerbung, Einstellungen"],
  "ablauf": [("Arbeitgeber-Check", "Was macht Ihren Betrieb attraktiv? Gehalt, Dienstplan, Team, Fahrzeug – wir sammeln die Argumente."), ("Karriereseite", "Eine Seite pro Stelle, mit Fotos aus Ihrem Betrieb und Kurzbewerbung."), ("Kampagnen", "Anzeigen im Umkreis, abgestimmt auf die Zielgruppe – mit eigenem Budget."), ("Nachfassen", "Wir zeigen Ihnen, wie schnelle Rückrufe die Einstellungsquote verdoppeln.")],
  "preis": "Einrichtung 1.490 € einmalig, Betreuung 790 € im Monat zzgl. Werbebudget. Monatlich kündbar nach drei Monaten.",
  "faq": [("Für welche Berufe funktioniert das?", "Besonders gut für Pflege, Handwerk, Praxen und Kanzleien – überall, wo Fachkräfte knapp sind und regional gesucht werden."), ("Wie viel Werbebudget brauche ich?", "Meist reichen 300 bis 800 € im Monat pro Stelle. Wir legen das vorher gemeinsam fest."), ("Was ist, wenn niemand Passendes kommt?", "Wir sehen nach zwei bis vier Wochen, wie viele und welche Bewerbungen kommen, und passen Ansprache, Umkreis und Stellenprofil an.")]},
 {"slug": "wachstum", "key": "wachstum", "titel": "Wachstumsprogramm", "kurz": "Website, SEO und Anzeigen aus einer Hand – mit einem Ziel und einem Monatsgespräch.",
  "h1": "Ein Programm, ein Ziel: mehr passende Anfragen",
  "lead": "Statt einzelne Bausteine zu kaufen, arbeiten wir zwölf Monate auf ein messbares Ziel hin: mehr Anfragen, mehr Bewerbungen oder mehr Termine. Website, SEO und Anzeigen greifen ineinander – und Sie haben einen Ansprechpartner.",
  "punkte": ["Website Wachstum inklusive, ohne Einmalkosten", "SEO Plus und Google-Ads-Betreuung inklusive", "Ein messbares Ziel, vorher schriftlich vereinbart", "Monatliches Gespräch mit klaren Zahlen", "Quartalsplanung: was wir als Nächstes angehen", "Günstiger als die Bausteine einzeln"],
  "ablauf": [("Zielbild", "Wir legen fest, was nach zwölf Monaten anders sein soll – in Zahlen."), ("Monat 1", "Website, Profil, Messung, erste Kampagnen."), ("Monat 2–6", "Inhalte, Bewertungen, Anzeigen nachschärfen."), ("Monat 7–12", "Ausbauen, was wirkt. Streichen, was nicht wirkt.")],
  "preis": "1.490 € Einrichtung (inkl. neuer Website) und 1.190 € im Monat bei zwölf Monaten Laufzeit, Werbebudget separat.",
  "faq": [("Warum zwölf Monate?", "Weil die Website-Erstellung im Preis steckt und SEO Zeit braucht. Die Laufzeit macht den Preis möglich."), ("Was, wenn das Ziel nicht erreicht wird?", "Wir sehen das früh in den Monatszahlen und steuern um. Liegen wir nach sechs Monaten deutlich hinter Plan, können Sie das Programm in reine Pflege umwandeln."), ("Für wen lohnt sich das?", "Für Betriebe, bei denen ein neuer Kunde oder eine neue Fachkraft mehrere tausend Euro wert ist.")]},
]

# ---------------------------------------------------------------- Branchen
BRANCHEN = [
 {"slug": "friseur", "draw": "friseur", "titel": "Friseure", "beispiel": "friseur",
  "h1": "Volle Terminbücher – auch dienstags um elf",
  "lead": "Neukundinnen suchen „Friseur in der Nähe“, schauen Fotos und Preise an und buchen abends online. Wer dort überzeugt, füllt die Lücken unter der Woche.",
  "probleme": ["Samstags ausgebucht, unter der Woche Leerlauf", "Kein Online-Termin – Anfragen gehen abends verloren", "Google-Profil mit alten Fotos und falschen Öffnungszeiten", "Instagram kostet Zeit, bringt aber kaum Buchungen"],
  "loesung": ["Online-Terminbuchung direkt auf der Website", "Preisliste und Vorher-nachher-Galerie", "Google-Profil mit aktuellen Fotos und Leistungen", "Bewertungs-QR-Code an der Kasse", "Erinnerung nach sechs Wochen für Stammkundinnen"],
  "zahl": ("3 Termine", "Drei zusätzliche Neukundinnen im Monat tragen das Paket mehrfach.")},
 {"slug": "barber", "draw": "barber", "titel": "Barbershops", "beispiel": "barber",
  "h1": "Weniger Warteschlange, mehr Stammkunden",
  "lead": "Barber-Kunden entscheiden in Sekunden: Fotos von Fades, Preise, freier Slot bei ihrem Barber. Wer online buchbar ist, gewinnt – und plant seine Tage statt auf Walk-ins zu hoffen.",
  "probleme": ["Walk-in-Chaos: mal Schlange, mal leerer Laden", "Kunden springen zum nächsten Shop, wenn es voll ist", "Preise und Leistungen stehen nur auf einem Schild im Laden", "Gute Barber wandern ab, weil die Auslastung schwankt"],
  "loesung": ["Online-Buchung pro Barber mit freien Slots", "Galerie mit Fades, Bartschnitten und Rasuren", "Klare Preise inkl. Kombi-Angeboten", "Google-Anzeigen auf „Barber in der Nähe“", "Stammkunden-Erinnerung nach drei Wochen"],
  "zahl": ("+20 %", "Typische Auslastungssteigerung, wenn Walk-ins durch planbare Termine ergänzt werden.")},
 {"slug": "dachdecker-solar", "draw": "dach", "titel": "Dachdecker & Solar", "beispiel": "dachdecker-solar",
  "h1": "Mehr Dach- und Solaranfragen aus Ihrer Region",
  "lead": "Ein Sturmschaden, eine Förderung, ein steigender Strompreis – Ihre Kunden suchen, wenn es dringend ist. Dann müssen Sie oben stehen und sofort erreichbar sein.",
  "probleme": ["Anfragen kommen fast nur über Empfehlungen und schwanken stark", "Portale verkaufen Ihre Leads an drei Mitbewerber gleichzeitig", "Die Website zeigt keine Referenzen und lädt auf dem Handy langsam", "Fachkräfte finden Sie kaum, Stellenanzeigen verpuffen"],
  "loesung": ["Eigene Seiten für Dachsanierung, Notdienst, Photovoltaik und Speicher je Ort", "Google Ads nur auf dringende Suchbegriffe wie „Dach undicht“", "Referenzgalerie mit Vorher-nachher und Ortsangabe", "Anfrageformular mit Fotoupload für eine schnelle Ersteinschätzung", "Karriereseite und Anzeigen für Gesellen und Monteure"],
  "zahl": ("1 Auftrag", "Eine einzige Dachsanierung deckt oft die Kosten eines ganzen Jahres Marketing.")},
 {"slug": "steuerberater", "draw": "steuer", "titel": "Steuerberater", "beispiel": "steuerberater",
  "h1": "Die richtigen Mandanten – und die Mitarbeiter, um sie zu betreuen",
  "lead": "Viele Kanzleien haben nicht zu wenig Arbeit, sondern die falsche. Wir helfen Ihnen, gezielt die Mandanten zu gewinnen, die zu Ihnen passen, und die Fachkräfte, die Sie dafür brauchen.",
  "probleme": ["Zu viele kleine, aufwendige Mandate, zu wenige passende", "Die Website sieht aus wie jede andere Kanzlei-Website", "Bewerbungen von Steuerfachangestellten bleiben aus", "Keine Zeit für Marketing neben dem Tagesgeschäft"],
  "loesung": ["Positionierung auf zwei bis drei Schwerpunkte, z. B. Handwerk oder Heilberufe", "Fachseiten, die Fragen Ihrer Wunschmandanten beantworten", "Karriereseite mit echten Einblicken und kurzer Bewerbung ohne Anschreiben", "Lokale Sichtbarkeit bei „Steuerberater + Ort“", "Erstgespräch-Buchung direkt über die Website"],
  "zahl": ("3–5 Mandate", "Wenige passende Mandate im Jahr machen den Unterschied in der Auslastung.")},
 {"slug": "pflegedienste", "draw": "pflege", "titel": "Pflegedienste", "beispiel": "pflegedienst",
  "h1": "Angehörige erreichen, Pflegekräfte gewinnen",
  "lead": "Pflegedienste haben zwei Zielgruppen: Familien, die schnell Hilfe brauchen, und Pflegekräfte, die einen guten Arbeitgeber suchen. Beide entscheiden online – meist abends auf dem Handy.",
  "probleme": ["Freie Touren, aber keine Pflegekräfte, um sie zu fahren", "Angehörige finden auf der Website keine klaren Antworten zu Kosten und Ablauf", "Stellenportale sind teuer und bringen wenig passende Bewerbungen", "Bewertungen sind veraltet oder fehlen"],
  "loesung": ["Bewerbung in 60 Sekunden – ohne Lebenslauf, per Handy", "Recruiting-Anzeigen im Umkreis von 20 Kilometern", "Seiten für Angehörige: Pflegegrad, Kosten, erste Schritte", "Rückrufformular statt Telefonwarteschleife", "Bewertungsprozess für zufriedene Familien"],
  "zahl": ("1 Pflegekraft", "Eine zusätzliche Pflegekraft ermöglicht oft eine ganze neue Tour.")},
 {"slug": "bestatter", "draw": "bestatter", "titel": "Bestatter", "beispiel": "bestatter",
  "h1": "Da sein, wenn eine Familie Sie sucht",
  "lead": "Im Trauerfall entscheiden Angehörige in wenigen Stunden – oft nach einer einzigen Suche. Ihre Website muss Ruhe ausstrahlen, Orientierung geben und jederzeit erreichbar sein.",
  "probleme": ["Große Ketten und Vergleichsportale stehen vor Ihnen bei Google", "Die Website wirkt veraltet und beantwortet Kostenfragen nicht", "Vorsorge-Gespräche kommen kaum über die Website", "Trauerfeiern und Gedenkseiten sind nirgends sichtbar"],
  "loesung": ["Klare 24-Stunden-Erreichbarkeit auf jeder Seite", "Würdevolle, ruhige Gestaltung mit echten Fotos", "Transparente Orientierungspreise für Bestattungsarten", "Ratgeberseiten: Was tun im Trauerfall?", "Lokale Sichtbarkeit in Ihren Orten und Ortsteilen"],
  "zahl": ("24/7", "Erreichbarkeit und Vertrauen entscheiden – nicht der lauteste Auftritt.")},
 {"slug": "tierarztpraxen", "draw": "tierarzt", "titel": "Tierarztpraxen", "beispiel": "tierarzt",
  "h1": "Weniger Telefonstress, mehr planbare Termine",
  "lead": "Tierhalter suchen nach Notdienst, Öffnungszeiten und Bewertungen. Eine gute Website nimmt Ihrem Empfang die Hälfte der Anrufe ab – und hilft, Tiermedizinische Fachangestellte zu finden.",
  "probleme": ["Das Telefon klingelt ununterbrochen mit Routinefragen", "Notdienstzeiten sind schwer zu finden", "TFA-Stellen bleiben monatelang unbesetzt", "Leistungen wie Zahnbehandlung oder Physiotherapie kennt kaum jemand"],
  "loesung": ["Online-Terminanfrage und Rezeptbestellung", "Notdienst-Hinweis prominent und aktuell", "Leistungsseiten für margenstarke Behandlungen", "Karriereseite für TFA und Tierärzte", "Bewertungen und Fotos im Google-Profil"],
  "zahl": ("−30 %", "So viele Routineanrufe lassen sich oft über die Website abfangen.")},
]

# ---------------------------------------------------------------- Beispiele mit Kundenweg
P = PREISE
BEISPIELE = [
 {"slug": "friseur", "draw": "friseur", "branche": "Friseur", "name": "Salon Kamm & Kante", "ort": "Kleinstadt, 25.000 Einwohner",
  "teaser": "Ein Salon mit zwei Stühlen will mehr Neukundinnen unter der Woche – ohne Instagram-Dauerstress.",
  "ausgang": "Inhaberin Sabine führt den Salon mit einer Mitarbeiterin. Samstags ist alles voll, dienstags und mittwochs bleiben Lücken. Eine Website gibt es nicht, nur ein selten gepflegtes Instagram-Profil und einen Google-Eintrag mit falschen Öffnungszeiten.",
  "ziel": "Mehr Termine unter der Woche, vor allem Neukundinnen aus dem Umkreis von zehn Kilometern.",
  "kundenweg": [
   ("Auslöser", "Lea ist neu in der Stadt. Ihr Pony muss geschnitten werden, ihr alter Friseur ist 200 Kilometer weg.", "Nichts – aber wir wissen: Genau in diesem Moment wird gesucht."),
   ("Suche", "Sie tippt „Friseur in der Nähe“ in Google Maps. Drei Salons erscheinen.", "Google-Profil komplett: richtige Zeiten, 20 Fotos, Leistungen mit Preisen, Kategorie „Damenfriseur“."),
   ("Vergleich", "Sie schaut Sterne und Fotos an. Wer hat aktuelle Bilder, wer antwortet auf Bewertungen?", "Bewertungs-QR-Code an der Kasse. Jede Bewertung wird freundlich beantwortet."),
   ("Prüfen", "Sie klickt auf die Website: Was kostet ein Schnitt? Sind die Leute sympathisch?", "Einseitige Website mit Preisliste, Teamfoto und Vorher-nachher-Bildern."),
   ("Kontakt", "Abends um 22 Uhr will sie nicht anrufen.", "Online-Terminbuchung über das bestehende Buchungstool, direkt eingebunden."),
   ("Danach", "Lea ist zufrieden und würde wiederkommen – wenn sie daran denkt.", "Erinnerung nach sechs Wochen per E-Mail aus dem Buchungstool, Bitte um Bewertung."),
  ],
  "umsetzung": ["Woche 1: Gespräch, Fotos mit dem Handy nach unserer Motivliste", "Woche 2: Website online, Google-Profil überarbeitet", "Woche 3: Buchungstool eingebunden, QR-Code-Aufsteller gedruckt", "Danach: Pflege, Bewertungen beantworten, Profil-Beiträge einmal im Monat"],
  "paket": [("Website Start (einmalig)", P["web_start"]), ("Pflege & Hosting, 12 × 49 €", 12 * P["pflege_start"])],
  "erwartung": "Realistisch ist eine spürbar bessere Auffindbarkeit in Maps innerhalb von zwei bis drei Monaten. Schon zwei bis drei Neukundinnen im Monat, die bleiben, tragen die Kosten mehrfach.",
  "aufgabe": "Fotos liefern, Bewertungen aktiv erfragen, Buchungstool aktuell halten."},
 {"slug": "dachdecker-solar", "draw": "dach", "branche": "Dachdecker & Solar", "name": "Brandt Bedachungen", "ort": "Landkreis, Einzugsgebiet 30 km",
  "teaser": "Ein Meisterbetrieb mit acht Leuten will weg von Leadportalen und hin zu eigenen Anfragen für Dach und Photovoltaik.",
  "ausgang": "Brandt Bedachungen hat volle Auftragsbücher im Sommer, im Winter wird es dünn. Für Photovoltaik kauft der Betrieb Leads bei Portalen – 60 bis 90 € pro Kontakt, den zwei Mitbewerber ebenfalls bekommen. Die Website ist zehn Jahre alt.",
  "ziel": "Zwölf eigene, qualifizierte Anfragen pro Monat für Sanierung und PV – und zwei neue Gesellen im ersten Jahr.",
  "kundenweg": [
   ("Auslöser", "Nach einem Sturm tropft es bei Familie Özdemir durch die Decke. Gleichzeitig denken sie seit Monaten über eine Solaranlage nach.", "Notdienst-Kampagne startet automatisch bei Sturmwarnungen mit höherem Tagesbudget."),
   ("Suche", "„Dachdecker Notdienst [Ort]“ am Handy, später am Laptop „Photovoltaik mit Dachsanierung“.", "Anzeige für Notdienst, eigene Seiten für „Dachsanierung mit PV“ in den zehn wichtigsten Orten."),
   ("Vergleich", "Sie öffnen drei Websites. Welche wirkt seriös, wer war schon in der Nachbarschaft?", "Referenzkarte mit 40 Projekten im Landkreis, Meisterbrief, Fotos vom echten Team."),
   ("Prüfen", "Was kostet das ungefähr? Gibt es Förderung? Wie lange dauert es?", "Ratgeberseite zu Kosten und Förderung, Ablauf in fünf Schritten, Antworten auf die zwölf häufigsten Fragen."),
   ("Kontakt", "Sie wollen nicht lange telefonieren, sondern Fotos schicken.", "Anfrageformular mit Fotoupload, Rückruf innerhalb von 24 Stunden zugesagt."),
   ("Danach", "Die Anlage läuft, die Nachbarn fragen nach.", "Bewertungsanfrage nach Abnahme, Projekt kommt mit Erlaubnis auf die Referenzkarte."),
  ],
  "umsetzung": ["Monat 1: Neue Website, Google-Profil, Messung von Anrufen und Formularen", "Monat 1: Google Ads für Notdienst und PV mit 700 € Budget", "Monat 2–4: Ortsseiten, Referenzkarte, Ratgeber Förderung", "Ab Monat 3: Recruiting-Seite und Anzeigen für Gesellen"],
  "paket": [("Einrichtung inkl. Website", P["prog_setup"]), ("Wachstumsprogramm, 12 × 1.190 €", 12 * P["programm"])],
  "paket_hinweis": "Enthalten: Website Wachstum, Pflege, SEO Plus, Google-Ads-Betreuung. Einzeln wären das im ersten Jahr " + eur(P["web_wachstum"] + 12 * P["pflege_wachstum"] + 12 * P["seo_plus"] + P["ads_setup"] + 12 * P["ads"]) + ". Werbebudget (hier 700 €/Monat) geht direkt an Google.",
  "erwartung": "Anzeigen bringen ab der zweiten Woche Anfragen. Organische Anfragen über die Ortsseiten wachsen meist ab dem vierten Monat. Eine einzige Sanierung mit PV liegt schnell bei 30.000 € und mehr.",
  "aufgabe": "Fotos von Baustellen schicken, Anfragen innerhalb von 24 Stunden zurückrufen, Kunden um Bewertungen bitten."},
 {"slug": "steuerberater", "draw": "steuer", "branche": "Steuerberatung", "name": "Kanzlei Weidner", "ort": "Mittelstadt, 80.000 Einwohner",
  "teaser": "Eine Kanzlei mit zwölf Mitarbeitenden will gezielt Handwerksbetriebe als Mandanten – und braucht dafür Personal.",
  "ausgang": "Die Kanzlei ist ausgelastet, aber mit vielen kleinen Privatmandaten. Gewünscht sind Handwerksbetriebe mit laufender Buchhaltung. Gleichzeitig fehlen zwei Steuerfachangestellte. Die Website ist korrekt, aber austauschbar.",
  "ziel": "Vier neue Handwerksmandate im Jahr und mindestens zwei Einstellungen.",
  "kundenweg": [
   ("Auslöser", "Malermeister Jens ärgert sich: Sein Steuerberater meldet sich nur zur Jahresabrechnung, Fragen zur Liquidität beantwortet niemand.", "Ratgeberartikel zu typischen Handwerker-Fragen, die genau diesen Frust aufgreifen."),
   ("Suche", "Er sucht „Steuerberater für Handwerker [Stadt]“ und fragt im Innungs-Stammtisch.", "Eigene Schwerpunktseite Handwerk, optimiert auf diese Suchbegriffe, plus Profil bei der Kreishandwerkerschaft."),
   ("Vergleich", "Er vergleicht zwei Kanzleien. Wer versteht sein Geschäft wirklich?", "Fallbeispiele aus dem Handwerk (anonymisiert), Branchenwissen, klare Leistungsbeschreibung."),
   ("Prüfen", "Er will wissen, wie ein Wechsel abläuft und was es kostet.", "Seite „Wechsel in fünf Schritten“ mit Orientierung zu Honoraren nach StBVV."),
   ("Kontakt", "Er bucht ein Erstgespräch – abends, online.", "Kalenderbuchung für 20-minütige Erstgespräche, automatisch mit Fragebogen."),
   ("Danach", "Die Zusammenarbeit läuft gut. Jens empfiehlt die Kanzlei im Stammtisch.", "Empfehlungskarte und Bewertungsbitte nach drei Monaten."),
  ],
  "umsetzung": ["Monat 1: Positionierungs-Workshop, neue Startseite und Schwerpunkt Handwerk", "Monat 2: Karriereseite mit Kurzbewerbung, Fotos vom Team", "Ab Monat 2: Ein Fachartikel pro Monat, lokale SEO", "Laufend: Bericht über Erstgespräche und Bewerbungen"],
  "paket": [("Website Wachstum (einmalig)", P["web_wachstum"]), ("Pflege & Hosting, 12 × 89 €", 12 * P["pflege_wachstum"]), ("SEO Lokal, 12 × 390 €", 12 * P["seo_lokal"])],
  "erwartung": "Erste Bewerbungen kommen oft schon in den ersten Wochen über die Karriereseite. Mandate über die Suche brauchen länger – mit vier bis sechs Monaten sollte man rechnen. Ein Handwerksmandat bringt typischerweise mehrere tausend Euro Honorar im Jahr.",
  "aufgabe": "Fachliche Freigabe der Artikel, 30 Minuten pro Monat für Themen, Erstgespräche führen."},
 {"slug": "pflegedienst", "draw": "pflege", "branche": "Ambulante Pflege", "name": "Pflege am Lindenhof", "ort": "Kreisstadt mit Umland",
  "teaser": "Ein ambulanter Dienst hat Anfragen, aber keine Pflegekräfte. Recruiting über das Handy löst den Engpass.",
  "ausgang": "Der Pflegedienst muss Anfragen von Familien ablehnen, weil Personal fehlt. Stellenportale kosten mehrere hundert Euro pro Anzeige und bringen kaum passende Bewerbungen. Die Website ist eine Visitenkarte von 2016.",
  "ziel": "Drei neue Pflegekräfte im ersten Halbjahr, danach gezielt Angehörige ansprechen.",
  "kundenweg": [
   ("Auslöser", "Pflegefachkraft Daniela ist unzufrieden mit ihren Schichten. Abends auf dem Sofa scrollt sie durch Instagram.", "Recruiting-Anzeigen im Umkreis von 20 km mit echten Fotos des Teams."),
   ("Suche", "Sie googelt „Pflegedienst Jobs [Ort]“ und schaut, wer in der Nähe ist.", "Jobseiten pro Stelle mit strukturierten Daten – dadurch erscheinen sie in Google Jobs."),
   ("Vergleich", "Was verdiene ich? Wie sind die Touren? Gibt es ein Dienstauto?", "Klare Angaben zu Gehaltsspanne, Tourenplanung, Dienstwagen und Team."),
   ("Prüfen", "Sie will wissen, wie es sich anfühlt, dort zu arbeiten.", "Kurze Zitate und Fotos aus dem Team, ehrliche Antworten auf häufige Fragen."),
   ("Kontakt", "Ein Lebenslauf liegt nicht griffbereit, Anschreiben will sie nicht.", "Bewerbung in 60 Sekunden: Name, Telefon, Qualifikation, Wunsch-Stunden. Rückruf in 48 Stunden."),
   ("Danach", "Daniela fängt an und erzählt ihrer Kollegin davon.", "Prämie für Mitarbeiterempfehlungen, auf der Karriereseite sichtbar."),
  ],
  "umsetzung": ["Woche 1–3: Neue Website mit Bereichen für Angehörige und Bewerber", "Woche 3: Recruiting-Kampagne mit 400 € Monatsbudget", "Monat 2: Angehörigen-Ratgeber zu Pflegegrad und Kosten", "Laufend: Anzeigen und Texte nach Bewerbungsqualität anpassen"],
  "paket": [("Website Wachstum (einmalig)", P["web_wachstum"]), ("Pflege & Hosting, 12 × 89 €", 12 * P["pflege_wachstum"]), ("Ads-Einrichtung (einmalig)", P["ads_setup"]), ("Ads-Betreuung, 12 × 290 €", 12 * P["ads"])],
  "paket_hinweis": "Werbebudget (hier 400 €/Monat) geht direkt an die Werbeplattform.",
  "erwartung": "Kurzbewerbungen kommen meist ab der ersten Kampagnenwoche. Nicht jede passt – entscheidend ist der schnelle Rückruf. Schon eine Einstellung spart die Kosten mehrerer Portal-Anzeigen.",
  "aufgabe": "Bewerber binnen 48 Stunden anrufen, Teamfotos ermöglichen, Gehaltsrahmen freigeben."},
 {"slug": "bestatter", "draw": "bestatter", "branche": "Bestattungen", "name": "Bestattungen Hollmann", "ort": "Familienbetrieb in dritter Generation",
  "teaser": "Ein Familienbetrieb will online so vertrauenswürdig wirken, wie er vor Ort ist – gegen Ketten und Portale.",
  "ausgang": "Hollmann ist im Ort bekannt, aber jüngere Angehörige suchen online und landen bei Vergleichsportalen. Die Website erklärt kaum etwas, Preise fehlen, die Telefonnummer ist klein im Fuß versteckt.",
  "ziel": "Bei Suchen im eigenen Ort und den fünf Nachbarorten oben stehen, mehr Vorsorgegespräche.",
  "kundenweg": [
   ("Auslöser", "Nachts ist Thomas’ Vater im Pflegeheim gestorben. Das Heim fragt, welcher Bestatter kommen soll.", "Nichts drängt sich auf – aber die Telefonnummer muss sofort und überall zu finden sein."),
   ("Suche", "Er sucht am Handy „Bestatter [Ort]“.", "Google-Profil mit 24-h-Nummer, Fotos des Hauses, Ortsseiten für alle Nachbarorte."),
   ("Vergleich", "Er sieht ein Portal und zwei lokale Häuser. Wer wirkt menschlich?", "Fotos der Familie Hollmann, ruhige Gestaltung, kurze Geschichte des Hauses."),
   ("Prüfen", "Was muss ich jetzt tun? Was kostet das ungefähr?", "Seite „Was tun im Trauerfall?“ und Orientierungspreise für Erd-, Feuer- und Seebestattung."),
   ("Kontakt", "Er ruft an – ein Mensch geht ran.", "24-h-Nummer als feste Leiste auf dem Handy, Rückrufformular für Vorsorgefragen."),
   ("Danach", "Monate später denkt seine Mutter über ihre eigene Vorsorge nach.", "Vorsorge-Ratgeber, Einladung zum Gespräch, dezente Bitte um Bewertung nach der Trauerfeier."),
  ],
  "umsetzung": ["Woche 1–2: Fotos vor Ort, Texte im Gespräch mit der Familie", "Woche 3: Website online, Profil und Verzeichnisse vereinheitlicht", "Ab Monat 2: Ortsseiten, Ratgeber Vorsorge, Bewertungen", "Laufend: Monatsbericht zu Anrufen und Profilaufrufen"],
  "paket": [("Website Start (einmalig)", P["web_start"]), ("Pflege & Hosting, 12 × 49 €", 12 * P["pflege_start"]), ("SEO Lokal, 12 × 390 €", 12 * P["seo_lokal"])],
  "erwartung": "Die Sichtbarkeit in Maps steigt bei sauberem Profil oft innerhalb weniger Wochen. Ortsseiten brauchen drei bis sechs Monate. Wenige zusätzliche Beauftragungen im Jahr tragen das Paket.",
  "aufgabe": "Texte freigeben, Bewertungen behutsam erfragen, Preise aktuell halten."},
 {"slug": "tierarzt", "draw": "tierarzt", "branche": "Tierarztpraxis", "name": "Tierarztpraxis am Mühlbach", "ort": "Kleintierpraxis, drei Tierärztinnen",
  "teaser": "Eine Praxis erstickt in Telefonaten. Online-Termine, klare Infos und eine Karriereseite schaffen Luft.",
  "ausgang": "Der Empfang verbringt den halben Tag am Telefon: Öffnungszeiten, Notdienst, Rezepte. Eine TFA-Stelle ist seit acht Monaten frei. Leistungen wie Zahnbehandlung und Physiotherapie werden kaum nachgefragt, obwohl die Praxis dafür ausgestattet ist.",
  "ziel": "Weniger Routineanrufe, mehr planbare Termine für Zahn und Physio, eine besetzte TFA-Stelle.",
  "kundenweg": [
   ("Auslöser", "Katze Mia frisst schlecht, Halterin Nina vermutet Zahnprobleme.", "Ratgeberseite „Zahnprobleme bei Katzen erkennen“ – genau das, was Nina sucht."),
   ("Suche", "Sie googelt „Tierarzt Zahnbehandlung Katze [Ort]“.", "Leistungsseite Zahnheilkunde mit Ablauf, Narkose-Infos und Preisrahmen."),
   ("Vergleich", "Bewertungen und Fotos: Wie gehen die mit ängstlichen Tieren um?", "Fotos aus der Praxis, Hinweis auf katzenfreundliche Abläufe, beantwortete Bewertungen."),
   ("Prüfen", "Hat die Praxis heute offen? Gibt es Notdienst?", "Öffnungszeiten und Notdienst als Erstes auf jeder Seite, automatisch aktuell."),
   ("Kontakt", "Sie möchte nicht in der Warteschleife hängen.", "Online-Terminanfrage und Rezeptbestellung, Bestätigung per E-Mail."),
   ("Danach", "Mia geht es besser. Nina bekommt eine Erinnerung zur Kontrolle.", "Recall-Erinnerungen aus der Praxissoftware, Bitte um Bewertung."),
  ],
  "umsetzung": ["Monat 1: Neue Website mit Terminanfrage und Rezeptbestellung", "Monat 1: Karriereseite für TFA mit Kurzbewerbung", "Ab Monat 2: Leistungsseiten Zahn, Physio, Senioren-Check", "Laufend: SEO Plus mit zwei neuen Ratgeberseiten pro Monat"],
  "paket": [("Website Wachstum (einmalig)", P["web_wachstum"]), ("Pflege & Hosting, 12 × 89 €", 12 * P["pflege_wachstum"]), ("SEO Plus, 12 × 690 €", 12 * P["seo_plus"])],
  "erwartung": "Online-Anfragen ersetzen Anrufe ab dem ersten Tag. Mehr Nachfrage für Zahn und Physio entsteht über Monate – eine Zahnsanierung unter Narkose liegt schnell bei mehreren hundert Euro.",
  "aufgabe": "Notdienstplan pflegen, Anfragen täglich bearbeiten, fachliche Freigabe der Ratgeber."},
]

BEISPIELE.insert(1, {"slug": "barber", "draw": "barber", "branche": "Barbershop", "name": "Blackline Barbers", "ort": "Szeneviertel, drei Stühle",
  "teaser": "Ein Barbershop mit drei Stühlen will weg vom Walk-in-Chaos – hin zu planbaren, vollen Tagen und Kunden, die alle drei Wochen wiederkommen.",
  "ausgang": "Inhaber Can und zwei Barber arbeiten fast nur mit Walk-ins. Freitags und samstags warten Kunden eine Stunde oder gehen wieder, montags bis mittwochs ist es ruhig. Es gibt ein Instagram-Profil, aber keine Website und keine Online-Buchung.",
  "ziel": "Mindestens 60 % der Termine vorab gebucht, weniger Leerlauf unter der Woche, mehr Stammkunden.",
  "kundenweg": [
   ("Auslöser", "Murat hat Freitag ein Date und sein Fade ist rausgewachsen.", "Anzeigen auf „Barber in der Nähe“ – genau dann, wenn er sucht."),
   ("Suche", "Er tippt „Barber“ in Google Maps und sieht vier Shops in der Umgebung.", "Google-Profil mit 30 Fotos von Fades und Bärten, Öffnungszeiten, Buchungs-Button."),
   ("Vergleich", "Er scrollt durch Fotos: Wer kann saubere Übergänge?", "Galerie nach Stil sortiert: Skin Fade, Taper, Bart, Rasur."),
   ("Prüfen", "Was kostet Haare plus Bart? Muss ich warten?", "Preisliste mit Kombi-Angeboten und sichtbar freien Slots pro Barber."),
   ("Buchung", "Er bucht Freitag 17:30 bei Can – in 20 Sekunden.", "Online-Buchung mit Wunsch-Barber, Bestätigung und Erinnerung per SMS."),
   ("Danach", "Drei Wochen später ist der Fade wieder fällig.", "Automatische Erinnerung nach 21 Tagen mit Direktlink zum Lieblingsbarber."),
  ],
  "umsetzung": ["Woche 1: Fotos im Laden nach unserer Motivliste, Buchungstool auswählen", "Woche 2: Website online, Google-Profil überarbeitet", "Woche 3: Google Ads mit 300 € Budget im Umkreis von 3 km", "Laufend: Galerie aktualisieren, Bewertungen beantworten"],
  "paket": [("Website Start (einmalig)", PREISE["web_start"]), ("Pflege & Hosting, 12 × 49 €", 12 * PREISE["pflege_start"]), ("Ads-Einrichtung (einmalig)", PREISE["ads_setup"]), ("Ads-Betreuung, 12 × 290 €", 12 * PREISE["ads"])],
  "paket_hinweis": "Werbebudget (hier 300 €/Monat) geht direkt an Google.",
  "erwartung": "Online-Buchungen kommen meist ab der ersten Woche. Ein Barber-Kunde, der alle drei Wochen kommt, bringt bei 35 € schnell über 500 € im Jahr – zehn neue Stammkunden tragen das Paket.",
  "aufgabe": "Buchungstool pflegen, Fotos von guten Schnitten machen, Kunden um Bewertungen bitten."})

KAPITEL = ["Ausgangslage", "Ziel", "Kundenweg", "Umsetzung", "Paket & Preis", "Was realistisch ist"]

# ---------------------------------------------------------------- Ratgeber
RATGEBER = [
 {"slug": "was-kostet-eine-website", "titel": "Was kostet eine Website für kleine Betriebe 2026?", "kurz": "Baukasten, Freelancer oder Agentur – was Sie wofür bekommen und welche laufenden Kosten oft vergessen werden.", "min": 6,
  "body": """
<p>Die ehrliche Antwort: zwischen 0 € und 20.000 €. Entscheidend ist nicht der Preis, sondern was die Website für Sie tun soll. Eine Website, die keine Anfragen bringt, ist auch für 500 € zu teuer.</p>
<h2>Die drei Wege im Überblick</h2>
<h3>Baukasten (z. B. Wix, Jimdo): 0–40 € im Monat</h3>
<p>Günstig und schnell, wenn Sie selbst Zeit investieren. Nachteile: Texte, Fotos und Struktur müssen Sie selbst erarbeiten, die Ladezeit ist oft mittelmäßig, und ein Umzug ist schwierig.</p>
<h3>Freelancer: 800–3.000 € einmalig</h3>
<p>Oft gutes Preis-Leistungs-Verhältnis. Klären Sie vorher, wer die Seite nach dem Start pflegt, Updates einspielt und erreichbar ist, wenn etwas nicht funktioniert.</p>
<h3>Agentur: 1.500–15.000 € einmalig</h3>
<p>Sie bekommen Konzept, Texte, Technik und Pflege aus einer Hand. Achten Sie darauf, dass Inhalte und Domain Ihnen gehören.</p>
<h2>Laufende Kosten, die oft vergessen werden</h2>
<ul><li>Domain und E-Mail: 2–10 € im Monat</li><li>Hosting: 0–30 € im Monat</li><li>Updates, Sicherheit, Backups: 20–80 € im Monat oder Ihre eigene Zeit</li><li>Änderungen an Texten und Bildern</li></ul>
<h2>Woran Sie eine gute Website erkennen</h2>
<ul><li>Sie lädt auf dem Handy in unter zwei Sekunden.</li><li>Man versteht in zehn Sekunden, was Sie anbieten und wo.</li><li>Telefonnummer und Kontakt sind auf jeder Seite sofort erreichbar.</li><li>Jede wichtige Leistung hat eine eigene Seite.</li></ul>
<h2>Unsere Preise zum Vergleich</h2>
<p>Website Start ab 1.490 €, Website Wachstum ab 2.990 €, jeweils mit Pflege und Hosting für 49 € bzw. 89 € im Monat. <a href="/preise/">Alle Preise ansehen</a>.</p>"""},
 {"slug": "lokale-seo-checkliste", "titel": "Lokale SEO: 12 Punkte, die Sie heute prüfen können", "kurz": "Eine Checkliste für Betriebe, die bei „… in der Nähe“ gefunden werden wollen – ohne Fachchinesisch.", "min": 7,
  "body": """
<p>Bei lokalen Suchen entscheidet Google nach drei Dingen: Relevanz, Entfernung und Bekanntheit. Die Entfernung können Sie nicht ändern – die anderen beiden schon.</p>
<h2>Google-Unternehmensprofil</h2>
<ol><li><strong>Hauptkategorie</strong> so genau wie möglich wählen („Dachdecker“, nicht „Bauunternehmen“).</li><li><strong>Öffnungszeiten</strong> inklusive Feiertagen aktuell halten.</li><li><strong>Mindestens 15 echte Fotos</strong>: Team, Räume, Arbeiten, Fahrzeuge.</li><li><strong>Leistungen</strong> einzeln mit kurzer Beschreibung eintragen.</li><li><strong>Jede Bewertung beantworten</strong>, auch die guten.</li></ol>
<h2>Website</h2>
<ol start="6"><li><strong>Name, Adresse, Telefon</strong> exakt gleich wie im Profil.</li><li><strong>Eine Seite pro Leistung</strong> – mit Ort im Titel.</li><li><strong>Strukturierte Daten</strong> (LocalBusiness) eingebunden.</li><li><strong>Mobil schnell</strong>: Testen Sie mit PageSpeed Insights.</li></ol>
<h2>Bekanntheit</h2>
<ol start="10"><li><strong>Einträge vereinheitlichen</strong>: Gelbe Seiten, Das Örtliche, Branchenverzeichnisse.</li><li><strong>Lokale Erwähnungen</strong>: Vereine, Sponsoring, Lokalzeitung.</li><li><strong>Bewertungen regelmäßig</strong> statt einmal viele – ein QR-Code an der Kasse wirkt Wunder.</li></ol>
<p class="note">Sie möchten das nicht selbst machen? Das ist genau unser Paket <a href="/leistungen/seo/">SEO Lokal</a>.</p>"""},
 {"slug": "google-ads-fuer-handwerker", "titel": "Google Ads für Handwerker: So verbrennen Sie kein Geld", "kurz": "Die fünf häufigsten Fehler bei Handwerker-Kampagnen und wie Sie mit 500 € im Monat sinnvoll starten.", "min": 6,
  "body": """
<p>Google Ads funktionieren für Handwerksbetriebe hervorragend – wenn man sie richtig einstellt. Die meisten Konten, die wir sehen, verschenken 30 bis 50 Prozent des Budgets.</p>
<h2>Fehler 1: Weitgehend passende Keywords</h2>
<p>Wer „Dach“ bucht, bezahlt auch für „Dachbox fürs Auto“. Nutzen Sie passende Wortgruppen und eine gepflegte Liste ausschließender Begriffe (Job, Ausbildung, selber machen, gebraucht …).</p>
<h2>Fehler 2: Alle Anzeigen auf die Startseite</h2>
<p>Wer „Dachrinne reparieren“ sucht, will eine Seite über Dachrinnen sehen. Eigene Zielseiten erhöhen die Anfragequote oft deutlich.</p>
<h2>Fehler 3: Zu großer Umkreis</h2>
<p>Stellen Sie das Gebiet auf das ein, was Sie wirklich anfahren wollen – und schließen Sie Orte aus, in denen Sie nicht arbeiten.</p>
<h2>Fehler 4: Keine Messung</h2>
<p>Ohne Anruf- und Formularmessung optimiert Google auf Klicks, nicht auf Anfragen. Das ist der teuerste Fehler.</p>
<h2>Fehler 5: Zu früh aufgeben</h2>
<p>Die ersten zwei bis vier Wochen sind Lernphase. Danach entscheiden die Zahlen.</p>
<h2>Ein sinnvoller Start mit 500 €</h2>
<ul><li>Eine Kampagne, zwei bis drei Anzeigengruppen für Ihre wichtigsten Leistungen</li><li>Nur Ihr echtes Einzugsgebiet</li><li>Anzeigen nur zu Zeiten, in denen jemand ans Telefon geht</li><li>Nach vier Wochen: Budget in die beste Anzeigengruppe umschichten</li></ul>
<p><a href="/leistungen/google-ads/">Wie wir Google Ads betreuen</a></p>"""},
 {"slug": "google-unternehmensprofil", "titel": "Google-Unternehmensprofil: Die unterschätzte Startseite", "kurz": "Warum viele Kunden Ihre Website nie sehen – und wie Sie das Profil in einer Stunde verbessern.", "min": 5,
  "body": """
<p>Viele Menschen entscheiden direkt in Google Maps: Sterne ansehen, Fotos durchblättern, anrufen. Ihre Website sehen sie nie. Das Profil ist damit oft wichtiger als die Startseite.</p>
<h2>Die Stunde, die sich lohnt</h2>
<ol><li><strong>10 Minuten</strong>: Kategorie, Zeiten, Telefonnummer, Website-Link prüfen.</li><li><strong>15 Minuten</strong>: Zehn aktuelle Fotos hochladen – Menschen vor Gebäuden.</li><li><strong>15 Minuten</strong>: Leistungen mit Beschreibung eintragen.</li><li><strong>10 Minuten</strong>: Offene Bewertungen beantworten.</li><li><strong>10 Minuten</strong>: Einen Beitrag mit aktuellem Angebot veröffentlichen.</li></ol>
<h2>So antworten Sie auf schlechte Bewertungen</h2>
<p>Ruhig, kurz, ohne Rechtfertigungsroman. Bedanken, Problem anerkennen, Lösung anbieten, offline weiterführen. Die Antwort lesen vor allem künftige Kunden.</p>
<h2>Bewertungen bekommen, ohne zu nerven</h2>
<p>Fragen Sie im Moment der größten Zufriedenheit: bei der Übergabe, nach dem Termin. Ein QR-Code auf einer Karte senkt die Hürde enorm. Kaufen Sie niemals Bewertungen – das ist unlauter und kann zur Sperre führen.</p>
<p class="note">Das Profil gehört bei allen unseren Paketen zur Grundausstattung.</p>"""},
]

FAQ = [
 ("Für wen arbeiten Sie?", "Für lokale und regionale Betriebe mit fünf bis fünfzig Mitarbeitenden – vor allem Handwerk, Kanzleien, Pflege, Praxen und Dienstleister, bei denen ein neuer Kunde viel wert ist."),
 ("Arbeiten Sie nur in bestimmten Regionen?", "Nein. Wir arbeiten vollständig remote in ganz Deutschland. Gespräche finden per Video oder Telefon statt."),
 ("Wie schnell kann es losgehen?", "Meist innerhalb von zwei Wochen nach dem Erstgespräch. Eine Website Start ist in zwei bis drei Wochen online."),
 ("Gibt es lange Vertragslaufzeiten?", "Websites kaufen Sie einmalig. Pflege und Ads sind monatlich kündbar, SEO hat sechs Monate Mindestlaufzeit, das Wachstumsprogramm zwölf Monate."),
 ("Wem gehört die Website?", "Ihnen. Domain, Inhalte und Dateien gehören Ihnen – auch wenn Sie die Zusammenarbeit beenden."),
 ("Was muss ich selbst beitragen?", "Ein Erstgespräch, Fotos nach unserer Motivliste und Freigaben. Den Rest übernehmen wir. Rechnen Sie mit zwei bis drei Stunden im ersten Monat."),
 ("Schreiben Sie auch die Texte?", "Ja. Sie erzählen, wir schreiben. Fachliche Inhalte geben Sie frei."),
 ("Setzen Sie Cookies und Tracking ein?", "So wenig wie möglich. Wir messen Anfragen datenschutzfreundlich und verzichten wo möglich auf Cookie-Banner."),
 ("Garantieren Sie Ergebnisse?", "Wir garantieren saubere Arbeit, klare Ziele und ehrliche Berichte. Rankings und Anfragen kann niemand seriös garantieren."),
 ("Helfen Sie auch bei der Mitarbeitersuche?", "Ja, mit dem Recruiting-Paket: Karriereseite, Bewerbung in 60 Sekunden und Anzeigen im Umkreis. Einrichtung 1.490 €, danach 790 € im Monat."),
 ("Wie läuft die Abrechnung?", "Einmalige Leistungen zur Hälfte bei Start, zur Hälfte bei Freischaltung. Monatliche Leistungen per Rechnung zum Monatsanfang."),
]
