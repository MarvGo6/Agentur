-- Eigenes Supabase-Projekt der Agentur "Lotwerk Agentur" (mlvraqrtejfwamwhyici, EU Irland) – getrennt von Vertriebs-OS.
-- Angewendet als Migration "agentur_anfragen". Öffentlich (anon) nur INSERT auf freigegebene Spalten.
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

-- Push-Benachrichtigung bei neuer Anfrage (Migration "anfrage_push_benachrichtigung").
-- Kanal: ntfy.sh, Thema lotwerk-anfragen-76ed1914b7fa7339 (in der ntfy-App abonnieren).
-- Bewusst ohne Name/E-Mail/Telefon – nur Thema und Betrieb. Fehler beim Senden blockieren das Speichern nie.
create extension if not exists pg_net with schema extensions;
create or replace function public.agentur_anfrage_benachrichtigen()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
  perform net.http_post(
    url := 'https://ntfy.sh/',
    body := jsonb_build_object(
      'topic', 'lotwerk-anfragen-76ed1914b7fa7339',
      'title', 'Neue Anfrage über die Website',
      'message', coalesce(new.thema, 'Ohne Thema') || ' · ' || coalesce(nullif(new.betrieb, ''), 'Betrieb nicht angegeben'),
      'tags', jsonb_build_array('incoming_envelope'),
      'priority', 4,
      'click', 'https://supabase.com/dashboard/project/mlvraqrtejfwamwhyici/editor'),
    headers := '{"Content-Type": "application/json"}'::jsonb);
  return new;
exception when others then return new;
end; $$;
revoke execute on function public.agentur_anfrage_benachrichtigen() from public, anon, authenticated;
create trigger agentur_anfrage_push after insert on public.agentur_anfragen
for each row execute function public.agentur_anfrage_benachrichtigen();
