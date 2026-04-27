# AI Fitness Copilot

This repository is split into two top-level apps:

- `backend`: FastAPI service, deterministic analysis, and LLM integration
- `frontend`: React + Vite client UI

## Directory Layout

- `backend/` contains all Python backend code, tests, and Docker config
- `frontend/` contains all React UI code
- `compose.yaml` in the repo root runs backend Docker only

## Run Backend (Docker)

```powershell
docker compose up --build
```

Backend API docs:

- http://127.0.0.1:8001/docs

## Run Frontend (Local Dev)

```powershell
cd frontend
npm install
npm run dev
```

Frontend app:

- http://127.0.0.1:5173

## Backend Local (No Docker)

```powershell
cd backend
pip install -e .[dev]
uvicorn app.main:app --reload
```

Backend docs (local run):

- http://127.0.0.1:8000/docs
