# cALorie

Upload a workout video, get an estimated calorie burn. See `/Users/bariscelik/.claude/plans/hola-we-are-starting-kind-waffle.md` for the full plan.

Two pieces:
- `web/` — Next.js frontend + API routes, deployed on Vercel.
- `worker/` — Python FastAPI service that does the actual video processing, deployed on Render.

Phase 0 status: scaffolded, using a **stub** worker (fake calorie numbers, no real video analysis yet) to prove the pipeline works end to end.

## One-time account setup (Phase 0)

You'll need four free accounts (no credit card required for any of them). Create each one yourself (sign-up flows aren't something I can do for you), then hand me the credentials listed so I can drop them into the env files.

### 1. Supabase (database + video storage) — done
Used for both the `jobs` table and the `workout-videos` storage bucket, both already created and wired up.

### 2. Upstash (job queue — QStash)
1. Go to https://upstash.com → sign up → **QStash** in the sidebar.
2. On the QStash overview page, copy the `QSTASH_TOKEN`.

### 3. Render (worker hosting)
1. Go to https://render.com → sign up → **New → Web Service**.
2. Connect this repo (once pushed to GitHub) and point it at the `worker/` directory.
3. Build command: `pip install -r requirements.txt`. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`.
4. Add environment variables `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` (same values as above) in Render's dashboard.
5. Once deployed, copy the service's public URL (e.g. `https://calorie-worker.onrender.com`) → `WORKER_URL`.

### 4. Vercel (frontend hosting)
1. Go to https://vercel.com → sign up → **New Project** → import this repo, root directory `web/`.
2. Add all variables from `web/.env.example` in Vercel's **Environment Variables** settings (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `QSTASH_TOKEN`, `WORKER_URL`).
3. Deploy.

## Local development

```bash
cd web
cp .env.example .env.local   # fill in the values collected above
npm run dev
```

```bash
cd worker
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
