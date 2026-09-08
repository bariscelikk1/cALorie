create table jobs (
  id uuid primary key default gen_random_uuid(),
  status text not null default 'queued',
  video_key text not null,
  weight_kg numeric not null,
  result_json jsonb,
  created_at timestamptz not null default now()
);
