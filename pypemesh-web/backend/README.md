# pypemesh-web/backend

FastAPI backend that wraps `pypemesh-core`. Deploys to Railway or Fly.io
(not Vercel — Vercel's Python runtime isn't suitable for long solver jobs).

## Dev

```bash
cd pypemesh-web/backend
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Opens at http://localhost:8000. Docs at http://localhost:8000/docs.

## Deploy

Railway: point at `pypemesh-web/backend`, Docker build, set PORT env.
Fly.io: `fly launch` from this directory.
