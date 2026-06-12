# AI Job Tracker

Local-first job search tracker with FastAPI, SQLAlchemy, PostgreSQL, and a lightweight built-in AI analyzer.

> Under construction, but the core tracker and demo AI flow are usable.

## What It Does

- Save and review job applications.
- Track application status, deadlines, and keywords.
- View summary reports and a simple dashboard.
- Run a local AI-style description analyzer that suggests keywords, a summary, seniority, and a fit score.

## Quick Start With Docker

```bash
cp .env.example .env
cp frontend/.env.local.example frontend/.env.local
docker compose up -d --build
```

Open:

- App: http://127.0.0.1
- Frontend dev mode: http://127.0.0.1:3000
- API docs: http://127.0.0.1:8000/docs

## Local Development

If you want to run it without the full proxy stack:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d postgres
cd backend && alembic upgrade head
cd frontend && npm install && npm run dev
```

## Configuration

- Backend reads `DATABASE_URL` and `ALLOWED_ORIGINS` from `.env`.
- Backend optionally reads `API_KEY` from `.env` for simple header auth on write routes.
- Frontend reads `NEXT_PUBLIC_API_BASE_URL` and optional `NEXT_PUBLIC_API_KEY` from `frontend/.env.local`.
- For docker/proxy mode, use `NEXT_PUBLIC_API_BASE_URL=/api`.
- For local direct mode, use `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000`.

## Status

This is intentionally a portfolio-friendly work in progress. The stack is Docker-first, the main workflows work locally, and the AI feature is a local heuristic analyzer rather than a paid model integration.

## Useful Endpoints

- `POST /jobs`
- `GET /jobs`
- `GET /jobs/{job_id}`
- `PUT /jobs/{job_id}`
- `GET /jobs/{job_id}/application`
- `PUT /jobs/{job_id}/application`
- `POST /jobs/{job_id}/keywords`
- `GET /jobs/{job_id}/keywords`
- `GET /applications`
- `PUT /applications/{application_id}`
- `GET /reports/summary`
- `GET /reports/jobs-by-status`
- `GET /reports/jobs-by-company`
- `GET /reports/keyword-frequency`
- `GET /reports/salary-summary`
- `GET /reports/upcoming-deadlines`
- `POST /analyze-description`
