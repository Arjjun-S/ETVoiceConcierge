-- Supabase schema for ET Voice Concierge
-- Creates users, calls, and conversations tables

create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  phone text,
  experience text,
  goal text,
  created_at timestamp default now()
);

create table if not exists calls (
  id uuid primary key default gen_random_uuid(),
  phone text,
  started_at timestamp,
  ended_at timestamp
);

-- Reset conversations to memory-friendly schema
drop table if exists conversations cascade;
create table conversations (
  id uuid primary key default gen_random_uuid(),
  user_id text,
  role text,
  content text,
  created_at timestamp default now()
);

-- Enable RLS on public tables
alter table if exists users enable row level security;
alter table if exists calls enable row level security;
alter table if exists conversations enable row level security;

-- Service role full access policies (used by backend service key)
do $$ begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'users' and policyname = 'service_role_users_full_access') then
    create policy service_role_users_full_access on public.users for all to service_role using (true) with check (true);
  end if;
  if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'calls' and policyname = 'service_role_calls_full_access') then
    create policy service_role_calls_full_access on public.calls for all to service_role using (true) with check (true);
  end if;
  if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'conversations' and policyname = 'service_role_conversations_full_access') then
    create policy service_role_conversations_full_access on public.conversations for all to service_role using (true) with check (true);
  end if;
end $$;
