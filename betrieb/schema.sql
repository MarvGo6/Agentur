-- Lotwerk Betrieb – Entwurf der Dashboard-Datenbank (Supabase-Projekt "Lotwerk Agentur")
-- Eingespielt im Supabase-Projekt "Lotwerk Agentur" (Migration betrieb_grundschema).
-- Zugriff: nur angemeldete Admins (Tabelle admins). Automatisierungen nutzen den Service-Role-Schlüssel serverseitig.

create table if not exists admins (user_id uuid primary key references auth.users on delete cascade, rolle text not null default 'inhaber');
create or replace function ist_admin() returns boolean language sql stable security definer set search_path = public
as $$ select exists (select 1 from admins where user_id = auth.uid()) $$;

-- ---------------------------------------------------------------- Vertrieb
create table if not exists interessenten (
  id uuid primary key default gen_random_uuid(),
  name text not null, branche text, ort text, telefon text, email text, website_alt text,
  google_place_id text unique, bewertung numeric(2,1), bewertungen_anzahl int,
  pagespeed_mobil int, potenzial int,                -- 0–100, aus Schnell-Analyse
  status text not null default 'neu' check (status in ('neu','vorschau','kontaktiert','termin','angebot','gewonnen','verloren','pausiert')),
  vorschau_url text, kontaktiert_am date, naechster_schritt date, verlustgrund text,
  quelle text, angelegt timestamptz not null default now()
);

create table if not exists kunden (
  id uuid primary key default gen_random_uuid(),
  interessent_id uuid references interessenten,
  firma text not null, ansprechpartner text, email text, telefon text, branche text, ort text,
  lexware_kontakt_id text, lastschrift_mandat boolean default false,
  status text not null default 'aktiv' check (status in ('aktiv','gekuendigt','pausiert')),
  seit date not null default current_date, gekuendigt_zum date
);

create table if not exists angebote (
  id uuid primary key default gen_random_uuid(),
  interessent_id uuid references interessenten, kunde_id uuid references kunden,
  option text, einmalig numeric(10,2), monatlich numeric(10,2),
  status text not null default 'offen' check (status in ('offen','angenommen','abgelehnt','abgelaufen')),
  gesendet_am date, entschieden_am date, lexware_id text
);

-- ---------------------------------------------------------------- Verträge & Geld
create table if not exists vertraege (
  id uuid primary key default gen_random_uuid(),
  kunde_id uuid not null references kunden on delete cascade,
  produkt text not null check (produkt in ('web_start','web_wachstum','pflege_start','pflege_wachstum','seo_lokal','seo_plus','ads','programm','recruiting')),
  einmalig numeric(10,2) default 0, monatlich numeric(10,2) default 0,
  start date not null, mindestlaufzeit_monate int default 0, ende date,
  aktiv boolean generated always as (ende is null) stored
);

create table if not exists rechnungen (
  id uuid primary key default gen_random_uuid(),
  kunde_id uuid references kunden, lexware_id text unique, nummer text,
  datum date not null, faellig date, netto numeric(10,2) not null, brutto numeric(10,2),
  art text check (art in ('einmalig','monatlich')), bezahlt_am date, mahnstufe int default 0
);

create table if not exists kosten (
  id uuid primary key default gen_random_uuid(),
  datum date not null, betrag numeric(10,2) not null,
  kategorie text not null check (kategorie in ('hosting','domain','ki','software','werbung','personal','sonstiges')),
  kunde_id uuid references kunden,                  -- leer = Gemeinkosten
  beschreibung text, beleg_lexware_id text
);

create table if not exists zeiten (
  id uuid primary key default gen_random_uuid(),
  kunde_id uuid references kunden,                  -- leer = intern/Vertrieb
  taetigkeit text check (taetigkeit in ('vertrieb','umsetzung','pflege','seo','ads','recruiting','verwaltung')),
  start timestamptz not null default now(), ende timestamptz, notiz text,
  minuten int generated always as (case when ende is null then null else (extract(epoch from ende - start) / 60)::int end) stored
);

-- ---------------------------------------------------------------- Websites & Überwachung
create table if not exists websites (
  id uuid primary key default gen_random_uuid(),
  kunde_id uuid references kunden on delete cascade,
  domain text unique, vercel_projekt_id text, repo_pfad text,          -- z. B. kunden/brandt-bedachungen
  status text not null default 'entwurf' check (status in ('vorschau','entwurf','live','gekuendigt')),
  live_seit date, domain_ablauf date, search_console boolean default false, statistik_id text
);

create table if not exists checks (                  -- Ergebnis jeder automatischen Prüfung
  id bigint generated always as identity primary key,
  website_id uuid not null references websites on delete cascade,
  art text not null check (art in ('uptime','ssl','formular','build','lighthouse','links','a11y','schema')),
  ok boolean not null, wert numeric, details jsonb, zeit timestamptz not null default now()
);
create index if not exists checks_web_zeit on checks (website_id, zeit desc);

create table if not exists messwerte (               -- Tages-/Monatswerte aus Search Console, Statistik, Google-Profil, KI-Abfrage
  website_id uuid not null references websites on delete cascade,
  datum date not null, kennzahl text not null,      -- z. B. besucher, klicks, impressionen, anrufe, routen, bewertungen, ki_genannt
  wert numeric not null, primary key (website_id, datum, kennzahl)
);

create table if not exists anfragen (                -- Formulare ALLER Kunden-Websites
  id uuid primary key default gen_random_uuid(),
  website_id uuid references websites on delete cascade,
  thema text, name text, kontakt text, nachricht text,
  weitergeleitet boolean default false, eingang timestamptz not null default now()
);

-- ---------------------------------------------------------------- Arbeit & KI
create table if not exists aufgaben (
  id uuid primary key default gen_random_uuid(),
  titel text not null, kunde_id uuid references kunden, website_id uuid references websites,
  quelle text default 'manuell' check (quelle in ('manuell','check','ki','frist')),
  prioritaet int default 2, faellig date, erledigt_am timestamptz, angelegt timestamptz not null default now()
);

create table if not exists ki_laeufe (
  id uuid primary key default gen_random_uuid(),
  art text not null check (art in ('vorschau','erstellung','optimierung','bericht','bewertungsantwort','analyse','ki_sichtbarkeit')),
  kunde_id uuid references kunden, website_id uuid references websites, interessent_id uuid references interessenten,
  modell text, tokens_ein int, tokens_aus int, kosten_eur numeric(8,4),
  ergebnis_url text,                                -- PR- oder Vorschau-Link
  status text not null default 'wartet' check (status in ('laeuft','wartet','freigegeben','abgelehnt','fehler')),
  zusammenfassung text, zeit timestamptz not null default now(), entschieden_am timestamptz
);

-- ---------------------------------------------------------------- Kennzahlen (Sichten)
create or replace view mrr_aktuell as
  select coalesce(sum(monatlich), 0) as mrr, count(distinct kunde_id) as kunden from vertraege where aktiv;

create or replace view deckungsbeitrag_kunde as
  select k.id, k.firma,
    coalesce((select sum(netto) from rechnungen r where r.kunde_id = k.id and r.datum > current_date - 365), 0) as umsatz_12m,
    coalesce((select sum(betrag) from kosten c where c.kunde_id = k.id and c.datum > current_date - 365), 0) as kosten_12m,
    coalesce((select sum(minuten) from zeiten z where z.kunde_id = k.id and z.start > now() - interval '365 days'), 0) / 60.0 as stunden_12m
  from kunden k;


-- ---------------------------------------------------------------- Datensammlung & Auswertung (Automatisierungen)
alter table interessenten add column if not exists befund jsonb;          -- Ergebnis der automatischen Website-Analyse
alter table interessenten add column if not exists analysiert_am timestamptz;
create index if not exists interessenten_offen on interessenten (analysiert_am) where website_alt is not null;

create table if not exists berichte (                -- wöchentliche/monatliche Auswertungen
  id uuid primary key default gen_random_uuid(),
  art text not null check (art in ('woche','monat')), von date not null, bis date not null,
  daten jsonb not null, text text, erstellt timestamptz not null default now(), unique (art, von)
);

create table if not exists einstellungen (            -- nur serverseitig lesbar (keine Policy)
  schluessel text primary key, wert text not null
);

create table if not exists seitenaufrufe (            -- anonym: keine IP, keine Cookies, keine Kennung; die Website sendet nur pfad + ereignis
  id bigint generated always as identity primary key,
  zeit timestamptz not null default now(),
  pfad text not null check (char_length(pfad) <= 200),
  herkunft text check (char_length(herkunft) <= 100),  -- Kampagnen-Quelle aus der Adresse (utm_source / google-ads / meta), kein Referrer
  geraet text check (geraet in ('handy','tablet','computer')),
  ereignis text not null default 'aufruf' check (ereignis in ('aufruf','cta','formular','telefon','mail','vorschau'))
);
create index if not exists seitenaufrufe_zeit on seitenaufrufe (zeit desc);

-- ---------------------------------------------------------------- Zugriffsschutz
do $$ declare t text; begin
  foreach t in array array['admins','interessenten','kunden','angebote','vertraege','rechnungen','kosten','zeiten','websites','checks','messwerte','anfragen','aufgaben','ki_laeufe','berichte','seitenaufrufe'] loop
    execute format('alter table %I enable row level security', t);
    execute format('drop policy if exists admin_alles on %I', t);
    execute format('create policy admin_alles on %I for all to authenticated using (ist_admin()) with check (ist_admin())', t);
  end loop;
end $$;
alter view mrr_aktuell set (security_invoker = on);
alter view deckungsbeitrag_kunde set (security_invoker = on);
alter table einstellungen enable row level security;  -- bewusst ohne Policy: nur Service-Rolle
drop policy if exists anon_zaehlen on seitenaufrufe;
create policy anon_zaehlen on seitenaufrufe for insert to anon with check (zeit > now() - interval '5 minutes');
grant insert (pfad, herkunft, geraet, ereignis) on seitenaufrufe to anon;


-- ---------------------------------------------------------------- Automatisierungen (Migrationen automatisierung_grundlagen, automatisierung_admin_speicher)
alter table websites add column if not exists formular_email text;                 -- Ü2: Empfänger der Formularanfragen
alter table websites add column if not exists formular_schluessel text unique default encode(extensions.gen_random_bytes(12), 'hex');
alter table anfragen add column if not exists seite text;
alter table anfragen add column if not exists daten jsonb;
alter table interessenten add column if not exists nachricht_entwurf text;         -- V4
alter table interessenten add column if not exists erinnert_am date;
alter table vertraege add column if not exists kuendigungsfrist_monate int not null default 3;   -- F3
alter table vertraege add column if not exists verlaengerung_monate int not null default 0;
alter table aufgaben add column if not exists schluessel text unique;                -- Automatiken legen jede Aufgabe nur einmal an
create table if not exists inhalte_formulare (id uuid primary key default gen_random_uuid(), kunde_id uuid references kunden on delete cascade,
  website_id uuid references websites on delete set null, titel text, token text unique not null default encode(extensions.gen_random_bytes(18), 'hex'),
  frist date not null default (current_date + 7), daten jsonb, dateien jsonb not null default '[]', eingereicht_am timestamptz, erinnert int not null default 0,
  angelegt timestamptz not null default now());                                       -- E1
create table if not exists kundenberichte (id uuid primary key default gen_random_uuid(), website_id uuid not null references websites on delete cascade,
  monat date not null, daten jsonb not null, text text, status text not null default 'entwurf' check (status in ('entwurf','freigegeben','gesendet')),
  erstellt timestamptz not null default now(), unique (website_id, monat));          -- B2
create table if not exists entwuerfe (id uuid primary key default gen_random_uuid(),
  art text not null check (art in ('nachricht','profil_beitrag','bewertungsantwort','verbesserung','ads','text')),
  kunde_id uuid references kunden on delete cascade, website_id uuid references websites on delete cascade, interessent_id uuid references interessenten on delete cascade,
  titel text, text text not null, meta jsonb, status text not null default 'offen' check (status in ('offen','freigegeben','verworfen','veroeffentlicht')),
  angelegt timestamptz not null default now(), entschieden_am timestamptz);          -- Freigaben in der Steuerzentrale
-- RLS wie oben (admin_alles) für inhalte_formulare, kundenberichte, entwuerfe.
-- Admin automatisch: Trigger lotwerk_admin auf auth.users (Adresse in einstellungen.admin_email, erst nach bestätigter E-Mail).
-- Speicher: privater Bucket „inhalte“ (Upload nur über signierte Links der Funktion inhalte, Lesen nur Admins).
-- Zeitpläne: lotwerk-erreichbarkeit */10, lotwerk-datenschutz am 2. 07:00 UTC, lotwerk-vertrieb Mo–Fr 05:30 UTC, lotwerk-leads Mo 05:00 UTC.

-- Steuerzentrale: Admins lesen und bearbeiten die Anfragen der Agentur-Website (Migration steuerzentrale_anfragen_lesen)
grant select, update on agentur_anfragen to authenticated;
create policy admin_alles on agentur_anfragen for all to authenticated using (ist_admin()) with check (ist_admin());

-- ---------------------------------------------------------------- Kampagnen-Zuordnung (Migration anfragen_kampagne)
alter table agentur_anfragen add column if not exists kampagne text check (char_length(kampagne) <= 200);  -- utm_source / utm_campaign, ohne Kennung
alter table agentur_anfragen add column if not exists gclid text check (char_length(gclid) <= 200);        -- nur mit Einwilligung „Google Ads“ (Offline-Conversions)
grant insert (kampagne, gclid) on agentur_anfragen to anon;

-- ---------------------------------------------------------------- Terminbuchung (Migration terminbuchung)
alter table websites add column if not exists buchung_url text;        -- Buchungsseite des Betriebs, täglich geprüft (checks.art = 'links', details.typ = 'buchung')
alter table websites add column if not exists buchung_anbieter text;
create or replace function public.klick_zaehlen(w uuid, k text) returns void   -- Klicks auf „Termin buchen“ → messwerte.buchung_klicks
language sql security definer set search_path = public as $$
  insert into messwerte (website_id, datum, kennzahl, wert) values (w, current_date, k, 1)
  on conflict (website_id, datum, kennzahl) do update set wert = messwerte.wert + 1;
$$;
revoke all on function public.klick_zaehlen(uuid, text) from public, anon, authenticated;
grant execute on function public.klick_zaehlen(uuid, text) to service_role;

-- ---------------------------------------------------------------- Wichtige Links (Migration links) – Steuerzentrale → „Links“
create table if not exists links (
  id uuid primary key default gen_random_uuid(),
  kategorie text not null, titel text not null, url text not null check (url ~ '^https://'),
  notiz text, kosten text, archiviert boolean not null default false,   -- archivieren statt löschen
  angelegt timestamptz not null default now()
);
alter table links enable row level security;
create policy admin_alles on links for all to authenticated using (ist_admin()) with check (ist_admin());
grant select, insert, update on links to authenticated;
