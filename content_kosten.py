"""Kosten-Ratgeber je Branche („Was kostet eine Website für …?“).
Nur eigene Preise aus PREISE und die Beispielpakete aus BEISPIELE – keine erfundenen Marktzahlen.
Fremdkosten (z. B. Buchungstools) werden genannt, aber ohne Betrag, weil sie vom Anbieter abhängen."""

KOSTEN = {
    "friseur": {
        "paket": "web_start",
        "warum": "Für die meisten Salons passt Website Start genau: Leistungen mit Preisen, Galerie, Team, Anfahrt und ein Knopf zur Online-Buchung. Mehr Seiten braucht es erst bei mehreren Filialen oder vielen Spezialleistungen wie Hochzeitsfrisuren oder Extensions.",
        "fremd": ["Online-Terminbuchung: Das Buchungstool (z. B. das, das Sie schon an der Kasse nutzen) kostet beim Anbieter extra. Wir binden es auf Ihrer Website ein.", "Fotos: Handyfotos nach unserer Motivliste reichen meist. Ein Fotograf kostet extra, ist aber kein Muss."],
        "teurer": ["mehrere Filialen mit eigenen Seiten", "Online-Shop für Pflegeprodukte", "Seiten in mehreren Sprachen"],
        "frage": ("Brauche ich als Salon überhaupt eine Website, wenn ich Instagram habe?", "Instagram zeigt Ihre Arbeit, aber bei „Friseur in der Nähe“ entscheidet Google. Dort zählen Google-Profil, Bewertungen und eine Website mit Leistungen, Preisen und Buchung. Instagram binden wir als Galerie ein."),
    },
    "barber": {
        "paket": "web_start",
        "warum": "Ein Barbershop braucht vor allem eine schnelle Seite mit Preisen, Fotos der Schnitte, Öffnungszeiten und Online-Buchung. Das deckt Website Start ab. Wer schnell neue Stammkunden will, ergänzt Google-Anzeigen im Umkreis.",
        "fremd": ["Buchungstool beim Anbieter Ihrer Wahl, Kosten je nach Anbieter.", "Werbebudget für Google-Anzeigen (falls gewünscht) zahlen Sie direkt an Google."],
        "teurer": ["mehrere Standorte", "Gutschein- oder Produktverkauf online", "Seiten in mehreren Sprachen"],
        "frage": ("Lohnen sich Google-Anzeigen für einen Barbershop?", "Oft ja, wenn der Laden neu ist oder Lücken im Kalender hat. Die Anzeige erscheint bei „Barber in der Nähe“ im Umkreis von wenigen Kilometern. Wir zeigen Ihnen jeden Monat, was eine Buchung gekostet hat."),
    },
    "dachdecker-solar": {
        "paket": "web_wachstum",
        "warum": "Dachdecker und Solarbetriebe bieten meist mehrere Leistungen an (Dach, Reparatur, Photovoltaik, Notdienst) und arbeiten in mehreren Orten. Für jede wichtige Leistung und jeden Ort eine eigene Seite bringt mehr Anfragen. Deshalb passt Website Wachstum besser als Start.",
        "fremd": ["Werbebudget für Google-Anzeigen (z. B. für den Notdienst) zahlen Sie direkt an Google.", "Drohnen- oder Profifotos von Referenzdächern kosten extra, Handyfotos gehen für den Start."],
        "teurer": ["Rechner für PV-Anlagen oder Förderung", "Anbindung an eine Handwerkersoftware", "sehr viele Orts- und Leistungsseiten"],
        "frage": ("Brauche ich für jeden Ort eine eigene Seite?", "Für die wichtigsten zwei bis fünf Orte ja, aber nur mit echtem Inhalt: Referenzen, Anfahrt, Besonderheiten vor Ort. Kopierte Seiten mit getauschtem Ortsnamen wertet Google ab."),
    },
    "steuerberater": {
        "paket": "web_wachstum",
        "warum": "Kanzleien werden über ihre Schwerpunkte gefunden, zum Beispiel Ärzte, Handwerk oder Erbschaft. Eigene Seiten je Schwerpunkt und ein Karrierebereich für Fachangestellte sprechen für Website Wachstum. Für eine sehr kleine Kanzlei ist Website Start ausreichend und günstiger.",
        "fremd": ["Mandantenportal oder digitale Belegübermittlung: läuft über Ihre Kanzlei-Software, wir verlinken oder binden es ein.", "Pflichtangaben für Steuerberater im Impressum (Kammer, Berufsordnung) liefern Sie, wir setzen sie um."],
        "teurer": ["mehrere Standorte", "Mandanten-Login mit eigener Programmierung", "Seiten in mehreren Sprachen"],
        "frage": ("Was muss eine Kanzlei-Website rechtlich beachten?", "Neben Impressum und Datenschutz gelten die Berufsregeln für Steuerberater, etwa Angaben zur Kammer. Die Inhalte prüfen Sie oder Ihre Kammer, wir sorgen dafür, dass alles an der richtigen Stelle steht."),
    },
    "pflegedienste": {
        "paket": "web_wachstum",
        "warum": "Ein Pflegedienst spricht zwei Gruppen an: Angehörige, die schnell Hilfe suchen, und Pflegekräfte, die einen neuen Arbeitgeber suchen. Dafür braucht es Seiten für Leistungen und Einzugsgebiet und einen Bereich für Bewerber. Das passt zu Website Wachstum.",
        "fremd": ["Werbebudget für Stellenanzeigen auf Instagram, Facebook oder Google zahlen Sie direkt an die Plattform.", "Fotos vom echten Team wirken am besten, Handyfotos nach unserer Liste reichen."],
        "teurer": ["mehrere Standorte oder Tagespflege mit eigener Seite", "Online-Bewerbung mit Anbindung an eine Bewerbersoftware", "Seiten in mehreren Sprachen"],
        "frage": ("Kann die Website auch bei der Personalsuche helfen?", "Ja. Eine Karriereseite mit Bewerbung in 60 Sekunden ist in Website Wachstum möglich. Wer zusätzlich Anzeigen schalten will, nimmt das Recruiting-Paket dazu."),
    },
    "bestatter": {
        "paket": "web_start",
        "warum": "Bei einem Trauerfall zählen schnelle Erreichbarkeit, ein ruhiger Auftritt und klare Informationen zu Ablauf und Kosten. Das passt gut in Website Start. Mehr Seiten lohnen sich bei Vorsorge-Beratung oder mehreren Standorten.",
        "fremd": ["Online-Gedenkseiten oder Traueranzeigen laufen oft über einen eigenen Anbieter, wir verlinken oder binden sie ein.", "Telefon rund um die Uhr: Das organisieren Sie, wir zeigen die Nummer gut sichtbar."],
        "teurer": ["eigene Gedenkseiten mit Kerzen und Kondolenzbuch", "mehrere Standorte", "Kostenrechner für Bestattungsarten"],
        "frage": ("Sollte ein Bestatter Preise auf der Website zeigen?", "Ein grober Rahmen hilft Angehörigen, die sich in einer schweren Lage orientieren wollen. Welche Preise Sie nennen, entscheiden Sie, wir bereiten es verständlich auf."),
    },
    "tierarztpraxen": {
        "paket": "web_start",
        "warum": "Tierhalter suchen Öffnungszeiten, Notdienst, Leistungen und am liebsten einen Online-Termin. Für eine Praxis mit einem Standort ist Website Start die richtige Wahl. Bei vielen Fachgebieten oder einem Karrierebereich für Tiermedizinische Fachangestellte passt Website Wachstum besser.",
        "fremd": ["Online-Terminbuchung über Ihre Praxissoftware oder einen Buchungsanbieter, Kosten je nach Anbieter.", "Fotos von Praxis und Team mit dem Handy nach unserer Motivliste."],
        "teurer": ["mehrere Standorte oder Klinik mit vielen Fachbereichen", "Karrierebereich mit Anzeigen", "Seiten in mehreren Sprachen"],
        "frage": ("Wie wichtig ist der Notdienst auf der Website?", "Sehr wichtig. Wer abends ein krankes Tier hat, sucht genau danach. Notdienst-Nummer und Regeln stehen bei uns ganz oben und im Google-Profil."),
    },
}
