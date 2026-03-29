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

create table if not exists conversations (
  id uuid primary key default gen_random_uuid(),
  call_id uuid references calls(id),
  user_text text,
  ai_text text,
  created_at timestamp default now()
);
