-- Lotwerk – fertige Abfragen für die Auswertung (Supabase → SQL Editor → einfügen → Run)
-- Alle Daten liegen im Projekt "Lotwerk Agentur". Nichts hier verändert Daten, außer Abschnitt 1.

-- 1) Neue Interessenten zur Analyse eintragen (die Analyse läuft automatisch alle 30 Minuten, je 3 Betriebe)
insert into interessenten (name, branche, ort, website_alt, quelle) values
  ('Musterbetrieb GmbH', 'Dachdecker', 'Musterstadt', 'https://www.example.de', 'recherche');
-- sofort statt in 30 Minuten starten:
select public.funktion_starten('analyse');

-- 2) Beste Verkaufschancen: hohes Potenzial, noch nicht kontaktiert
select name, branche, ort, website_alt, potenzial, pagespeed_mobil,
       befund->'befund' as befund
from interessenten
where status = 'neu' and potenzial is not null
order by potenzial desc, pagespeed_mobil nulls last
limit 20;

-- 3) Befund eines Betriebs in Klartext (für die Präsentation "Persönliche Analyse")
select name, jsonb_array_elements_text(befund->'befund') as punkt
from interessenten where name ilike '%Muster%';

-- 4) Pipeline: wie viele Interessenten in welcher Stufe
select status, count(*), round(avg(potenzial)) as potenzial_schnitt
from interessenten group by status order by count(*) desc;

-- 5) Website: Aufrufe, Klicks auf Ersteinschätzung und Anfragen der letzten 30 Tage
select
  count(*) filter (where ereignis = 'aufruf')   as aufrufe,
  count(*) filter (where ereignis = 'cta')      as klicks_ersteinschaetzung,
  count(*) filter (where ereignis = 'formular') as formulare,
  (select count(*) from agentur_anfragen where created_at > now() - interval '30 days') as anfragen
from seitenaufrufe where zeit > now() - interval '30 days';

-- 6) Welche Seiten führen zu Klicks auf die Ersteinschätzung? (Konversion je Seite)
select pfad,
  count(*) filter (where ereignis = 'aufruf') as aufrufe,
  count(*) filter (where ereignis = 'cta')    as cta,
  round(100.0 * count(*) filter (where ereignis = 'cta') / nullif(count(*) filter (where ereignis = 'aufruf'), 0), 1) as quote_prozent
from seitenaufrufe where zeit > now() - interval '30 days'
group by pfad order by aufrufe desc limit 20;

-- 7) Woher kommen Besucher? (Domain des Verweises) und mit welchem Gerät?
select coalesce(herkunft, 'direkt / unbekannt') as herkunft, count(*) from seitenaufrufe
where ereignis = 'aufruf' and zeit > now() - interval '30 days' group by 1 order by 2 desc;
select geraet, count(*) from seitenaufrufe where ereignis = 'aufruf' and zeit > now() - interval '30 days' group by 1;

-- 8) Anfragen nach Thema und Einstiegsseite
select thema, count(*) from agentur_anfragen group by thema order by 2 desc;

-- 9) Letzte Berichte lesen
select art, von, bis, text from berichte order by von desc limit 8;

-- 10) Überwachung: letzte Prüfungen und offene Aufgaben
select w.domain, c.art, c.ok, c.wert, c.zeit from checks c join websites w on w.id = c.website_id order by c.zeit desc limit 20;
select titel, quelle, angelegt from aufgaben where erledigt_am is null order by prioritaet, angelegt;

-- 11) Neue Kunden-Website zur Überwachung anmelden
insert into websites (domain, status) values ('www.kunde-beispiel.de', 'live');

-- 12) Zeitpläne ansehen (Datenbank-Jobs)
select jobname, schedule, active from cron.job order by jobname;
