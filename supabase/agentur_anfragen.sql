-- Für ein EIGENES Supabase-Projekt der Agentur (getrennt von Vertriebs-OS). Im SQL-Editor des neuen Projekts ausführen,
-- danach URL und Publishable Key in config.json eintragen (supabase_url, supabase_key).
create table public.agentur_anfragen (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  name text not null check (char_length(name) between 2 and 120),
  betrieb text check (char_length(betrieb) <= 160),
  email text not null check (char_length(email) <= 200 and email ~* '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'),
  telefon text check (char_length(telefon) <= 40),
  thema text check (char_length(thema) <= 80),
  nachricht text check (char_length(nachricht) <= 4000),
  quelle text check (char_length(quelle) <= 200),
  einwilligung boolean not null check (einwilligung),
  status text not null default 'neu' check (status in ('neu','kontaktiert','termin','angebot','gewonnen','verloren'))
);
create index agentur_anfragen_created_idx on public.agentur_anfragen (created_at desc);
alter table public.agentur_anfragen enable row level security;
revoke all on public.agentur_anfragen from anon, authenticated;
grant insert (name, betrieb, email, telefon, thema, nachricht, quelle, einwilligung) on public.agentur_anfragen to anon;
create policy "Website darf Anfragen anlegen" on public.agentur_anfragen for insert to anon with check (status = 'neu' and einwilligung);
