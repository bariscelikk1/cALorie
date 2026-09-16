create extension if not exists pgcrypto;

create table if not exists jobs (
  id uuid primary key default gen_random_uuid(),
  access_token uuid not null default gen_random_uuid(),
  status text not null default 'queued'
    check (status in ('queued', 'processing', 'done', 'error')),
  video_key text not null
    check (video_key ~ '^uploads/[0-9a-f-]{36}\.(mp4|mov|webm)$'),
  weight_kg numeric not null check (weight_kg between 30 and 250),
  exercise text not null
    check (exercise in ('squat', 'jumping_jack', 'push_up')),
  result_json jsonb,
  error_message text,
  created_at timestamptz not null default now(),
  started_at timestamptz,
  completed_at timestamptz,
  updated_at timestamptz not null default now()
);

-- Upgrade the original Phase-0 table when this script is applied to an
-- existing project. Defaults keep old demonstration rows readable.
alter table jobs add column if not exists access_token uuid default gen_random_uuid();
alter table jobs add column if not exists exercise text default 'squat';
alter table jobs add column if not exists error_message text;
alter table jobs add column if not exists started_at timestamptz;
alter table jobs add column if not exists completed_at timestamptz;
alter table jobs add column if not exists updated_at timestamptz default now();
update jobs set access_token = gen_random_uuid() where access_token is null;
update jobs set exercise = 'squat' where exercise is null;
update jobs set updated_at = created_at where updated_at is null;
alter table jobs alter column access_token set not null;
alter table jobs alter column exercise set not null;
alter table jobs alter column updated_at set not null;

create index if not exists jobs_status_created_at_idx on jobs (status, created_at);

create or replace function set_jobs_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists jobs_set_updated_at on jobs;
create trigger jobs_set_updated_at
before update on jobs
for each row execute function set_jobs_updated_at();

alter table jobs enable row level security;

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'workout-videos', 'workout-videos', false, 104857600,
  array['video/mp4', 'video/quicktime', 'video/webm']
)
on conflict (id) do update set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;
