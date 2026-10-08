"""Ausführliche Inhalte der Leistungsseiten (/leistungen/<slug>/).
Aufbau je Seite: Suchintention zuerst beantworten, dann Für-wen, Vorgehen im Detail, Kosten, typische Fehler, Messung, Fragen.
Regeln: keine erfundenen Zahlen oder Ergebnisse; Preise kommen aus content.PREISE; kurze Sätze, keine Werbefloskeln."""
from content import PREISE as P, eur, REC_GARANTIE, REC_GARANTIE_TEXT, REC_WECHSEL_TEXT, REC_WECHSEL_PREIS

TIEFE = {
# ---------------------------------------------------------------------------------------------- Google Ads
"google-ads": {
 "seo": "Google Ads für lokale Betriebe: Betreuung zum Festpreis",
 "kurz": "Google Ads für Handwerk, Praxen und Kanzleien: Anzeigen nur auf Suchen mit Auftragsabsicht, feste Betreuung ab 290 € im Monat, Bericht in Kosten pro Anfrage.",
 "intro_h2": "Was Google Ads für einen lokalen Betrieb leisten",
 "intro": [
  "Google Ads sind die Anzeigen über und neben den normalen Suchergebnissen und in Google Maps. Sie zahlen nur, wenn jemand klickt. Für lokale Betriebe ist das der schnellste Weg zu Anfragen: Die Anzeige erscheint genau dann, wenn jemand „Dachdecker Bielefeld“ oder „Tierarzt Notdienst“ eingibt.",
  "Ob daraus Aufträge werden, hängt vor allem von drei Dingen ab: Auf welche Suchbegriffe Sie bieten, wohin der Klick führt und ob Sie messen, was danach passiert. Genau daran arbeiten wir jeden Monat.",
 ],
 "fuer_wen": [
  ("Notdienste und dringende Anliegen", "Rohrbruch, Sturmschaden, krankes Tier: Wer jetzt sucht, ruft das erste passende Ergebnis an. Ohne Anzeige sind Sie dort oft nicht zu sehen."),
  ("Leistungen mit hohem Auftragswert", "Dachsanierung, Photovoltaik, Steuerberatung für Unternehmen: Ein einziger Auftrag kann die Anzeigenkosten eines ganzen Jahres decken."),
  ("Neue Angebote und neue Orte", "SEO braucht Monate. Anzeigen bringen ab dem ersten Tag Sichtbarkeit, während die Website in der normalen Suche aufholt."),
 ],
 "abschnitte": [
  ("Suchbegriffe: nur wo ein Auftrag dahintersteht", [
   "„Dach reparieren lassen“ und „Dachziegel selber verlegen“ klingen ähnlich, bringen aber völlig verschiedene Besucher. Wir trennen Suchen mit Auftragsabsicht von Informationssuchen und Jobsuchen und bieten nur auf die erste Gruppe.",
   "Dazu pflegen wir eine Ausschlussliste mit Begriffen wie „Ausbildung“, „Gehalt“, „gebraucht“ oder „kostenlos“. Sie wächst jeden Monat mit den Suchanfragen, die tatsächlich Klicks ausgelöst haben.",
  ], None),
  ("Zielseite statt Startseite", [
   "Wer nach „Steuerberater Existenzgründung“ sucht und auf einer allgemeinen Startseite landet, sucht oft nicht weiter, sondern geht zurück. Jede Kampagne bekommt deshalb eine eigene Seite, die genau dieses Anliegen beantwortet: Leistung, Ort, Ablauf, Preisrahmen, Kontakt.",
   "Eine passende Zielseite verbessert auch den Qualitätsfaktor bei Google. Das senkt den Preis pro Klick.",
  ], None),
  ("Messen, was zählt: Anrufe und Anfragen", [
   "Klicks allein sagen wenig. Wir messen Anrufe über die Anzeige und die Website sowie abgeschickte Formulare. Das läuft datenschutzfreundlich, nur mit Einwilligung und mit Googles Consent Mode.",
   "Im Monatsbericht sehen Sie deshalb nicht „1.200 Impressionen“, sondern: so viele Anfragen, so viel hat eine Anfrage gekostet, das haben wir geändert.",
  ], None),
  ("Kampagnenarten, die für lokale Betriebe passen", [
   "Wir setzen vor allem Suchkampagnen ein, ergänzt um Anzeigen in Google Maps. Performance-Max- oder Display-Kampagnen nutzen wir nur, wenn genug Messdaten vorliegen, denn sie verteilen das Budget sonst schwer kontrollierbar auf viele Kanäle.",
  ], ["Suchkampagnen mit Begriffen pro Leistung und Ort", "Anzeigenerweiterungen: Anruf, Standort, Leistungen, Bewertungen", "Zeitplan: Anzeigen nur, wenn jemand ans Telefon geht", "Umkreis passend zu Ihrem Einsatzgebiet"]),
 ],
 "kosten": {
  "text": "Es gibt zwei Kostenblöcke: unsere Betreuung zum Festpreis und Ihr Werbebudget, das Sie direkt an Google zahlen. Wir verdienen nicht mehr, wenn Sie mehr ausgeben.",
  "zeilen": [("Einrichtung (Konto, Messung, Kampagnen, Zielseite)", eur(P["ads_setup"]) + " einmalig"), ("Betreuung", eur(P["ads"]) + " im Monat, monatlich kündbar"),
             ("Werbebudget", "legen Sie fest, wird direkt von Google abgebucht"), ("Im Wachstumsprogramm", "Betreuung enthalten")],
  "hinweis": "Wie hoch das Budget sein sollte, hängt von den Klickpreisen in Ihrer Branche und Region ab. Die prüfen wir vor dem Start mit Googles eigenem Planungswerkzeug und rechnen gemeinsam aus, wie viele Anfragen realistisch sind.",
 },
 "fehler": [
  ("Weitgehend passende Keywords ohne Ausschlüsse", "Google spielt die Anzeige dann auch bei Jobsuchen, Anleitungen oder Nachbarorten aus. Das Budget ist schnell weg."),
  ("Alle Klicks auf die Startseite", "Besucher müssen selbst suchen, was sie wollten. Viele springen ab."),
  ("Keine Anrufmessung", "Gerade im Handwerk ruft die Mehrheit an, statt ein Formular zu schicken. Ohne Messung wirken gute Kampagnen wie schlechte."),
  ("Automatische Empfehlungen ungeprüft übernehmen", "Google schlägt oft höhere Budgets und breitere Zielgruppen vor. Wir übernehmen nur, was Ihre Zahlen stützen."),
 ],
 "messung": [("Kosten pro Anfrage", "Werbekosten geteilt durch Anrufe und Formulare"), ("Anteil passender Anfragen", "Wie viele Anfragen passen wirklich zu Ihrem Angebot?"),
             ("Suchbegriffe", "Welche Suchen haben Klicks ausgelöst, welche schließen wir aus?"), ("Anzeigenanteil", "Wie oft erscheinen Sie bei relevanten Suchen?")],
 "faq": [
  ("Muss ich ein eigenes Google-Ads-Konto haben?", "Ja, das Konto läuft auf Ihren Namen und bleibt Ihnen. Wir bekommen Zugriff als Verwalter. Wenn Sie gehen, behalten Sie alles."),
  ("Können Sie garantieren, dass ich ganz oben stehe?", "Nein. Die Position hängt von Gebot, Qualität der Anzeige und Wettbewerb ab und wechselt bei jeder Suche. Wir steuern auf Kosten pro Anfrage, nicht auf Platz eins um jeden Preis."),
  ("Lohnt sich Google Ads, wenn ich schon bei Google gefunden werde?", "Oft ja, für dringende Suchen und neue Leistungen. Wir prüfen vorher, bei welchen Begriffen Sie organisch schon gut stehen, und bieten dort weniger oder gar nicht."),
 ],
},
# ---------------------------------------------------------------------------------------------- SEO
"seo": {
 "seo": "Lokale SEO: bei Google Maps und ChatGPT gefunden werden",
 "kurz": "Lokale SEO für Betriebe: Google-Unternehmensprofil, Seiten pro Leistung und Ort, Bewertungen und Technik. Ab 490 € im Monat, Bericht in Anrufen und Anfragen.",
 "intro_h2": "Was lokale SEO ist und warum sie anders funktioniert",
 "intro": [
  "Bei lokalen Suchen wie „Friseur in der Nähe“ oder „Steuerberater Münster“ zeigt Google zuerst eine Karte mit drei Betrieben, darunter die normalen Ergebnisse. Lokale SEO sorgt dafür, dass Sie an beiden Stellen auftauchen. Sie ist der Teil der Suchmaschinenoptimierung, der sich um Ort, Nähe und Vertrauen dreht.",
  "Google bewertet dabei vor allem drei Dinge: Relevanz (passt Ihr Angebot zur Suche?), Entfernung (wie nah sind Sie?) und Bekanntheit (Bewertungen, Erwähnungen, Links). Die Entfernung können wir nicht ändern. Relevanz und Bekanntheit schon.",
  "Dazu kommt ein neuer Weg: Immer mehr Menschen fragen ChatGPT, Gemini oder Googles KI-Übersicht nach Empfehlungen. Diese Systeme greifen auf dieselben Grundlagen zurück: verständliche Seiten, strukturierte Daten, einheitliche Einträge und Bewertungen.",
 ],
 "fuer_wen": [
  ("Betriebe mit festem Einzugsgebiet", "Handwerk, Praxen, Salons, Kanzleien: Kunden kommen aus 10 bis 30 km Umkreis und suchen mit Ortsangabe oder „in der Nähe“."),
  ("Mehrere Orte oder Filialen", "Für jeden Standort ein eigenes Profil und eine eigene Seite, sauber getrennt und ohne doppelte Texte."),
  ("Wer unabhängig von Portalen werden will", "Statt pro Anfrage an Vermittlungsportale zu zahlen, bauen Sie eine eigene Sichtbarkeit auf, die bleibt."),
 ],
 "abschnitte": [
  ("Google-Unternehmensprofil: das Schaufenster in Maps", [
   "Für viele Suchende ist das Profil der erste Kontakt, noch vor der Website. Wir richten es vollständig ein: Hauptkategorie und passende Zusatzkategorien, Leistungen mit Beschreibung, Einzugsgebiet, Öffnungszeiten inklusive Feiertagen, Fotos und Fragen mit Antworten.",
   "Danach pflegen wir es laufend mit Beiträgen und neuen Fotos und indem wir jede Bewertung beantworten. Ein gepflegtes Profil zeigt Google und Kunden, dass der Betrieb aktiv ist.",
  ], None),
  ("Eine Seite pro Leistung und Ort", [
   "Eine einzige Seite „Unsere Leistungen“ kann nicht für zehn verschiedene Suchen gut ranken. Wir bauen für jede wichtige Leistung eine eigene Seite und für die wichtigsten Orte im Einzugsgebiet eigene Abschnitte oder Seiten.",
   "Wichtig: Jede Ortsseite braucht eigenen Inhalt, zum Beispiel Einsätze in diesem Ort, Anfahrt und Besonderheiten. Kopierte Seiten mit ausgetauschtem Ortsnamen wertet Google ab. Solche Seiten bauen wir nicht.",
  ], None),
  ("Bewertungen: mehr, regelmäßiger, beantwortet", [
   "Die Zahl, die Aktualität und die Antworten auf Bewertungen beeinflussen Ranking und Klickrate. Wir richten einen einfachen Ablauf ein: Nach jedem Auftrag bekommt der Kunde einen Kurzlink per SMS oder E-Mail. Gekaufte oder vorformulierte Bewertungen gibt es bei uns nicht. Das verstößt gegen Googles Richtlinien und gegen das Wettbewerbsrecht.",
  ], None),
  ("Einheitliche Einträge im Netz", [
   "Name, Adresse und Telefonnummer müssen überall gleich lauten: im Google-Profil, auf der Website, bei Apple Karten, Bing, Branchenbüchern und Kammerverzeichnissen. Abweichungen verunsichern Suchmaschinen. Wir prüfen die wichtigsten Verzeichnisse und gleichen sie an.",
  ], None),
  ("Technik, die Google und KI lesen können", [
   "Schnelle Ladezeit auf dem Handy, saubere Überschriften, strukturierte Daten (LocalBusiness, Leistungen, Fragen) und eine klare Seitenstruktur. Das hilft der Google-Suche genauso wie KI-Assistenten, die Ihre Seite zusammenfassen sollen.",
  ], ["Ladezeit und Darstellung auf dem Handy", "Strukturierte Daten nach schema.org", "Search Console einrichten und Fehler beheben", "Interne Verlinkung zwischen Leistungen, Orten und Ratgebern"]),
 ],
 "kosten": {
  "text": "Lokale SEO ist laufende Arbeit: Profil pflegen, Inhalte ausbauen, Bewertungen begleiten. Deshalb arbeiten wir mit einem festen Monatspreis.",
  "zeilen": [("SEO Lokal: Profil, Technik, Einträge, 1 neue oder überarbeitete Seite pro Monat", eur(P["seo_lokal"]) + " im Monat"), ("SEO Plus: 2–3 Seiten pro Monat, Bewertungsablauf", eur(P["seo_plus"]) + " im Monat"),
             ("Mindestlaufzeit", "6 Monate, danach monatlich kündbar"), ("Im Wachstumsprogramm", "SEO Plus enthalten")],
  "hinweis": "Erste Veränderungen sehen Sie meist nach acht bis zwölf Wochen, belastbare Ergebnisse nach etwa sechs Monaten. Wer schneller Anfragen braucht, kombiniert SEO am Anfang mit Google Ads.",
 },
 "fehler": [
  ("Falsche Hauptkategorie im Profil", "Die Kategorie ist eines der stärksten Signale in Maps. „Bauunternehmen“ statt „Dachdecker“ kostet Sichtbarkeit."),
  ("Kopierte Ortsseiten", "Zwanzig gleiche Seiten mit anderem Ortsnamen bringen selten etwas und können der ganzen Website schaden."),
  ("Bewertungen ohne Antwort", "Gerade auf kritische Bewertungen achten Interessenten. Eine sachliche Antwort wirkt oft stärker als fünf Sterne."),
  ("Alte Einträge mit falscher Nummer", "Umzug oder neue Telefonnummer, aber Branchenbücher zeigen noch die alten Daten. Das kostet Anrufe und Vertrauen."),
 ],
 "messung": [("Anrufe und Routen aus dem Profil", "direkt aus dem Google-Unternehmensprofil"), ("Klicks aus der Suche", "Google Search Console, je Seite und Suchbegriff"),
             ("Positionen für Ihre Kernbegriffe", "5 bis 10 Begriffe, monatlich aus mehreren Orten gemessen"), ("Nennung in KI-Antworten", "Werden Sie bei „bester … in …“ genannt?")],
 "faq": [
  ("Was ist der Unterschied zwischen SEO und Google Ads?", "Bei Google Ads zahlen Sie für jeden Klick, die Anzeigen stoppen, sobald das Budget endet. SEO baut Sichtbarkeit in den unbezahlten Ergebnissen auf. Das dauert länger, bleibt aber bestehen."),
  ("Kann ich erreichen, dass ChatGPT mich empfiehlt?", "Garantieren kann das niemand. Aber KI-Assistenten nutzen öffentliche Quellen: Ihre Website, Ihr Profil, Bewertungen, Verzeichnisse. Je klarer und einheitlicher diese sind, desto eher werden Sie genannt. Wir messen das monatlich."),
  ("Was brauchen Sie von mir?", "Zugang zum Google-Profil (oder wir legen es mit Ihnen an), Fotos aus Ihrem Betrieb und rund eine Stunde im ersten Monat. Danach melden wir uns nur, wenn wir eine kurze Freigabe brauchen, zum Beispiel für eine Antwort auf eine Bewertung."),
 ],
},
# ---------------------------------------------------------------------------------------------- Websites
"webentwicklung": {
 "seo": "Website erstellen lassen: für Betriebe, ab 1.490 € Festpreis",
 "kurz": "Website erstellen lassen für Handwerk, Praxen und Kanzleien: schnell, mobil, datenschutzfreundlich, in 2–4 Wochen online. Festpreis ab 1.490 €, Website und Domain gehören Ihnen.",
 "intro_h2": "Was eine Website für einen lokalen Betrieb leisten muss",
 "intro": [
  "Die meisten Besucher kommen über das Handy, haben ein konkretes Anliegen und wenig Geduld. Eine gute Betriebs-Website beantwortet deshalb in wenigen Sekunden: Was bieten Sie an, wo, für wen, und wie erreiche ich Sie? Alles andere kommt danach.",
  "Wir bauen Websites, die drei Aufgaben erfüllen: gefunden werden (Technik und Inhalte für Google und KI-Suche), überzeugen (Fotos aus dem Betrieb, klare Leistungen, Bewertungen) und Anfragen auslösen (Anrufknopf, kurze Formulare, Online-Termin).",
 ],
 "fuer_wen": [
  ("Betriebe ohne eigene Website", "Bisher nur Google-Profil oder Facebook? Eine eigene Seite macht Sie unabhängig und bringt Anfragen, die nicht über Portale laufen."),
  ("Veraltete Baukasten-Seiten", "Langsam, nicht fürs Handy gebaut, seit Jahren nicht gepflegt. Wir übernehmen, was gut ist, und leiten alte Adressen sauber um."),
  ("Betriebe, die Personal suchen", "Mit Karriereseite und Kurzbewerbung wird die Website auch zum Werkzeug fürs Recruiting."),
 ],
 "abschnitte": [
  ("Aufbau, der zu Anfragen führt", [
   "Oben steht, was Sie tun und wo. Darunter folgen die wichtigsten Leistungen mit eigener Seite, Vertrauen (Bewertungen, Team, Meisterbrief, Zertifikate, aber nur, was es wirklich gibt) und der Weg zum Kontakt. Auf dem Handy bleibt ein Anrufknopf immer erreichbar.",
   "Statt eines langen Kontaktformulars fragen wir nur, was Sie für den Rückruf brauchen. Je nach Branche ergänzen wir Fotos-hochladen, Online-Termin oder Rückrufwunsch.",
  ], None),
  ("Zwei Pakete", [
   f"Website Start ({eur(P['web_start'])}) eignet sich für Betriebe mit wenigen Leistungen: bis fünf Seiten, Kontakt, Rechtstexte, Google-Profil verknüpft. Website Wachstum ({eur(P['web_wachstum'])}) ist für alle, die über Google wachsen wollen: bis fünfzehn Seiten, eigene Seiten pro Leistung und Ort, Karriereseite und strukturierte Daten.",
  ], None),
  ("Schnell, sicher und ohne Cookie-Banner", [
   "Wir bauen schlanke Seiten ohne schwere Baukasten-Technik. Ziel ist eine Ladezeit unter einer Sekunde auf dem Handy. Schriften liegen auf dem eigenen Server, es gibt keine Tracker ohne Einwilligung. In vielen Fällen braucht die Website dadurch gar kein Cookie-Banner.",
   "Barrierearm bauen wir ohnehin: ausreichende Kontraste, lesbare Schriftgrößen, Bedienung per Tastatur, Bildbeschreibungen. Seit dem 28. Juni 2025 verlangt das Barrierefreiheitsstärkungsgesetz das für bestimmte Online-Angebote an Verbraucher. Ob es für Sie gilt, klären wir im Gespräch.",
  ], None),
  ("Texte und Fotos", [
   "Sie liefern Stichworte über ein Online-Formular, wir schreiben daraus die Texte und Sie geben frei. Fotos sind am besten echt: Team, Arbeiten, Räume, Fahrzeuge. Wir schicken Ihnen eine Motivliste. Stockfotos setzen wir nur sparsam und gekennzeichnet ein.",
  ], None),
 ],
 "kosten": {
  "text": "Sie zahlen einen Festpreis für den Bau und einen Monatsbetrag für Hosting, Sicherheit und kleine Änderungen. Was es kostet, steht vorher fest.",
  "zeilen": [("Website Start (bis 5 Seiten)", eur(P["web_start"]) + " einmalig"), ("Website Wachstum (bis 15 Seiten, Orts- und Karriereseiten)", eur(P["web_wachstum"]) + " einmalig"),
             ("Pflege & Hosting Start / Wachstum", f"{P['pflege_start']} € bzw. {P['pflege_wachstum']} € im Monat, 12 Monate Laufzeit"), ("Zahlung", "50 % bei Auftrag, 50 % nach Abnahme")],
  "hinweis": "Domain, Inhalte und Dateien gehören Ihnen. Wenn Sie die Pflege beenden, bekommen Sie alles übergeben.",
 },
 "fehler": [
  ("Startseite ohne klare Aussage", "Slogans wie „Ihr Partner für alles rund ums Haus“ sagen nicht, was Sie tun und wo. Besucher und Google brauchen Klartext."),
  ("Telefonnummer nur als Bild oder im Impressum", "Auf dem Handy muss die Nummer antippbar und überall sichtbar sein."),
  ("Lange Formulare", "Jedes zusätzliche Pflichtfeld kostet Anfragen. Name, Kontakt und Anliegen reichen für den ersten Schritt."),
  ("Relaunch ohne Weiterleitungen", "Alte Adressen, die bei Google gut standen, führen nach dem Umbau ins Leere. Wir leiten jede alte Seite auf die passende neue um."),
 ],
 "messung": [("Ladezeit und Technik", "Google PageSpeed und Lighthouse, Ziel mindestens 90 von 100"), ("Anfragen", "Formulare, Klicks auf Telefon und E-Mail, ohne Cookies gezählt"),
             ("Erreichbarkeit", "Prüfung alle 10 Minuten, bei Ausfall sofortige Meldung"), ("Sichtbarkeit", "Klicks aus der Google-Suche je Seite")],
 "faq": [
  ("Wie lange dauert es, bis die Website online ist?", "Zwei bis vier Wochen, je nach Paket. Den größten Einfluss hat, wie schnell Inhalte und Fotos kommen. Dafür gibt es eine Frist von sieben Tagen."),
  ("Kann ich meine bisherige Domain behalten?", "Ja. Wir ziehen die Website um und richten Weiterleitungen ein, damit bestehende Google-Positionen erhalten bleiben."),
  ("Brauche ich ein Cookie-Banner?", "Nur, wenn Dienste eingebunden werden, die eine Einwilligung brauchen, zum Beispiel Google Ads-Messung oder eine eingebettete Karte. Dann bauen wir ein Banner ein, bei dem Ablehnen genauso einfach ist wie Zustimmen."),
 ],
},
# ---------------------------------------------------------------------------------------------- Recruiting
"recruiting": {
 "seo": "Recruiting für Handwerk, Pflege und Praxen: Bewerbungen ohne Portale",
 "kurz": "Fachkräfte finden ohne Stellenportale: Karriereseite, Bewerbung in 60 Sekunden, Anzeigen im Umkreis und Google Jobs. Für Handwerk, Pflege, Praxen und Kanzleien.",
 "intro_h2": "Warum Stellenanzeigen allein oft nicht mehr reichen",
 "intro": [
  "Wer heute eine Pflegefachkraft, einen Gesellen oder eine Fachangestellte sucht, konkurriert mit vielen Betrieben um wenige Menschen. Die meisten davon haben bereits einen Job und schauen nicht aktiv in Stellenbörsen. Sie wechseln trotzdem, wenn das Angebot passt und die Bewerbung einfach ist.",
  "Unser Recruiting setzt deshalb dort an, wo diese Menschen ohnehin sind: auf Instagram, Facebook und in der Google-Suche. Die Anzeige führt auf eine Karriereseite, die zeigt, wie der Arbeitsalltag bei Ihnen aussieht. Die Bewerbung dauert eine Minute.",
 ],
 "fuer_wen": [
  ("Pflegedienste und Einrichtungen", "Pflegefachkräfte, Pflegehilfskräfte und Auszubildende, oft in Teilzeit und mit Wunsch nach verlässlichen Dienstplänen."),
  ("Handwerksbetriebe", "Gesellen, Monteure, Meister und Azubis, die Wert auf Fahrzeug, Werkzeug und ein gutes Team legen."),
  ("Praxen und Kanzleien", "Medizinische, tiermedizinische und Steuerfachangestellte, die planbare Arbeitszeiten suchen."),
 ],
 "abschnitte": [
  ("Die Karriereseite: konkret statt austauschbar", [
   "Sätze wie „junges dynamisches Team“ lesen Bewerber in jeder Anzeige. Überzeugend sind konkrete Angaben: Gehaltsrahmen, Arbeitszeiten, Dienstplan, Fahrzeug, Urlaub, wer die Kollegen sind. Wir sammeln diese Argumente mit Ihnen und zeigen sie mit echten Fotos aus Ihrem Betrieb.",
  ], None),
  ("Bewerbung in 60 Sekunden", [
   "Statt Lebenslauf und Anschreiben fragen wir nur wenige Dinge: Qualifikation, gewünschte Stunden, Name und Telefonnummer. Den Rest klären Sie im Gespräch. Das senkt die Hürde gerade für Menschen, die nicht aktiv suchen.",
  ], None),
  ("Anzeigen im Umkreis und Google Jobs", [
   "Die Anzeigen laufen auf Instagram und Facebook im Umkreis von meist 20 bis 30 km und bei Bedarf in der Google-Suche.",
   "Zusätzlich markieren wir jede Stelle mit strukturierten Daten. Dann kann sie in Google Jobs erscheinen, der Stellensuche direkt in Google, ohne Gebühren pro Anzeige.",
  ], None),
  ("Schnell nachfassen", [
   "Wer innerhalb eines Tages zurückruft, hat deutlich bessere Chancen als nach einer Woche. Jede Bewerbung kommt deshalb sofort per E-Mail oder WhatsApp bei Ihnen an, mit allen Angaben auf einen Blick.",
  ], None),
 ],
 "kosten": {
  "text": "Einrichtung und Betreuung zum Festpreis, das Werbebudget zahlen Sie direkt an Meta bzw. Google.",
  "zeilen": [("Einrichtung (Karriereseite, Kurzbewerbung, Kampagnen)", eur(P["rec_setup"]) + " einmalig"), ("Betreuung", eur(P["rec"]) + " im Monat"),
             ("Werbebudget", "ab 1.000 € im Monat je Stelle, zahlen Sie direkt an Meta bzw. Google"), ("Laufzeit", "3 Monate, danach monatlich kündbar"),
             ("Stelle besetzt", f"Wechsel auf die nächste Stelle: {REC_WECHSEL_PREIS} € für neue Werbemittel (30 % der Einrichtung)"), ("Bewerbungs-Garantie", f"weniger als {REC_GARANTIE['bewerbungen']} Bewerbungen in {REC_GARANTIE['wochen']} Wochen: nächster Monat kostenlos (ab {REC_GARANTIE['budget']} Werbebudget im Monat)")],
  "hinweis": "Zum Vergleich: Viele Stellenportale berechnen pro Anzeige und Laufzeit, Personalvermittler oft einen Anteil des Jahresgehalts. Bei uns zahlen Sie einen festen Betrag, egal wie viele Bewerbungen kommen. Zum Werbebudget: Branchenberichte von Recruiting-Anbietern nennen 30 bis 120 € je Bewerbung über Facebook und Instagram, in Großstädten eher mehr. Mit 1.000 € im Monat sind das grob 8 bis 30 Bewerbungen.",
 },
 "fehler": [
  ("Kein Gehaltsrahmen", "Ohne Angabe bewerben sich viele gar nicht erst. Ein Rahmen reicht."),
  ("Bewerbung nur per E-Mail mit Unterlagen", "Wer abends am Handy scrollt, hat keinen Lebenslauf griffbereit."),
  ("Tagelang keine Rückmeldung", "Gute Leute haben mehrere Angebote. Schnell anrufen ist der wichtigste Schritt."),
  ("Stockfotos statt echtem Team", "Bewerber wollen sehen, mit wem sie arbeiten."),
 ],
 "messung": [("Bewerbungen", "Anzahl je Stelle und Woche"), ("Kosten je Bewerbung", "Werbebudget geteilt durch Bewerbungen"),
             ("Passende Bewerbungen", "Anteil, der zum Gespräch eingeladen wird"), ("Einstellungen", "Was am Ende zählt: Wie viele haben angefangen?")],
 "faq": [
  ("Funktioniert das auch für Azubis?", "Ja, mit eigener Ansprache und eigener Seite. Für Schüler zählen andere Dinge: Ausbildungsinhalte, Übernahme, Team, Fahrzeug."),
  ("Brauche ich eigene Social-Media-Kanäle?", "Nein. Die Anzeigen laufen über ein Werbekonto. Eine Facebook-Seite für Ihren Betrieb legen wir bei Bedarf mit Ihnen an."),
  ("Wie funktioniert die Bewerbungs-Garantie?", REC_GARANTIE_TEXT),
  ("Was passiert, wenn die Stelle schnell besetzt ist?", REC_WECHSEL_TEXT),
  ("Was passiert mit den Bewerberdaten?", "Sie gehen direkt an Sie und werden bei uns nur so lange gespeichert, wie es für die Weiterleitung nötig ist. Die Datenschutzhinweise auf der Karriereseite erstellen wir mit."),
 ],
},
# ---------------------------------------------------------------------------------------------- Wachstumsprogramm
"wachstum": {
 "seo": "Online-Marketing für lokale Betriebe: Website, SEO und Ads",
 "kurz": "Wachstumsprogramm für lokale Betriebe: neue Website, lokale SEO und Google Ads zusammen geplant, mit festem Ziel und Monatsbericht, Gespräch auf Wunsch. 1.490 € Einrichtung, 1.190 € im Monat.",
 "intro_h2": "Warum die Bausteine zusammen besser wirken",
 "intro": [
  "Anzeigen bringen schnell Besucher. SEO bringt auf Dauer Besucher, ohne pro Klick zu zahlen. Die Website entscheidet, wie viele davon anfragen. Wer nur einen dieser Bausteine angeht, verschenkt oft die Wirkung der anderen: Gute Anzeigen auf eine schwache Seite kosten viel, eine gute Seite ohne Sichtbarkeit bringt wenig.",
  "Im Wachstumsprogramm planen wir alle drei zusammen, auf ein Ziel hin, das wir vorher schriftlich festhalten. Zum Beispiel: 25 passende Anfragen im Monat für Dachsanierung im Kreis Gütersloh.",
 ],
 "fuer_wen": [
  ("Betriebe mit hohem Auftragswert", "Wenn ein Neukunde mehrere tausend Euro bringt, rechnet sich ein festes Monatsbudget für Sichtbarkeit schnell."),
  ("Wer wachsen oder ein neues Standbein aufbauen will", "Neue Leistung, neuer Ort, zweiter Standort: Das Programm baut die Sichtbarkeit genau dafür auf."),
  ("Wer einen Ansprechpartner statt drei Dienstleistern will", "Sie haben einen Ansprechpartner und bekommen einen gemeinsamen Bericht für alles."),
 ],
 "abschnitte": [
  ("Die ersten 30 Tage", [
   "Neue Website (Paket Wachstum), Google-Profil vollständig, Messung von Anrufen und Anfragen, erste Suchkampagnen auf die wichtigsten Leistungen. Ab Tag eins sehen Sie im Bericht, woher Anfragen kommen.",
  ], None),
  ("Monat 2 bis 6", [
   "Wir bauen Seiten für Leistungen und Orte aus, richten den Bewertungsablauf ein und schärfen die Anzeigen nach. Budget fließt dorthin, wo Anfragen am günstigsten entstehen.",
  ], None),
  ("Monat 7 bis 12", [
   "Mit wachsender organischer Sichtbarkeit können Anzeigen oft sparsamer eingesetzt werden. Wir bauen aus, was wirkt, und lassen weg, was nichts bringt. Jedes Quartal legen wir gemeinsam die nächsten Schritte fest.",
  ], None),
 ],
 "kosten": {
  "text": "Ein Paket statt drei Rechnungen. Einzeln würden die enthaltenen Leistungen im ersten Jahr mehr kosten.",
  "zeilen": [("Einrichtung inklusive Website Wachstum", eur(P["prog_setup"]) + " einmalig"), ("Programm (SEO Plus, Ads-Betreuung, Pflege, Monatsbericht, Gespräch auf Wunsch)", eur(P["programm"]) + " im Monat"),
             ("Laufzeit", "12 Monate"), ("Werbebudget", "separat, direkt an Google")],
  "hinweis": f"Zum Vergleich einzeln im ersten Jahr: Website Wachstum, Pflege, SEO Plus, Ads-Einrichtung und Ads-Betreuung ergeben {eur(P['web_wachstum'] + 12 * P['pflege_wachstum'] + 12 * P['seo_plus'] + P['ads_setup'] + 12 * P['ads'])}, im Programm sind es {eur(P['prog_setup'] + 12 * P['programm'])}.",
 },
 "fehler": [
  ("Ziel nur „mehr Sichtbarkeit“", "Ohne messbares Ziel lässt sich nicht sagen, ob es funktioniert. Wir vereinbaren Anfragen, Termine oder Bewerbungen."),
  ("Anzeigen ohne fertige Website starten", "Dann zahlen Sie für Besucher, die nicht anfragen. Deshalb kommt im Programm die Website zuerst."),
  ("Nach drei Monaten alles umwerfen", "SEO wirkt verzögert. Wir bewerten jeden Baustein nach seiner eigenen Zeitachse."),
 ],
 "messung": [("Zielwert", "die vereinbarte Zahl, monatlich mit Verlauf"), ("Anfragen nach Quelle", "Anzeigen, Google-Suche, Maps, direkt"),
             ("Kosten pro Anfrage", "über alle Kanäle"), ("Sichtbarkeit", "Positionen und Nennung in KI-Antworten")],
 "faq": [
  ("Kann ich mit einem einzelnen Baustein starten und später wechseln?", "Ja. Viele starten mit einer Website oder SEO und wechseln später ins Programm. Was bereits gebaut ist, nutzen wir weiter."),
  ("Wer schreibt die Inhalte?", "Wir, auf Grundlage Ihrer Angaben. Sie geben alles frei, bevor es online geht."),
  ("Wie viel Zeit brauche ich pro Monat?", "Nach dem ersten Monat kaum Zeit: Sie bekommen jeden Monat einen Bericht. Ein 30-Minuten-Gespräch dazu gibt es, wenn Sie möchten. Ab und zu brauchen wir eine kurze Freigabe."),
 ],
},
}
