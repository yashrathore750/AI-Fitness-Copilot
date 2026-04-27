# Frontend

React + TypeScript + Tailwind CSS UI for AI Fitness Copilot.

## Setup

```bash
npm install
npm run dev
```

Then open http://localhost:5173

## Build

```bash
npm run build
npm run preview
```

## Environment

The app proxies API calls from `/api/*` to the backend at `http://localhost:8001`.

Recommended workflow:

1. Start backend with Docker from repo root:

```bash
docker compose up --build
```

2. Run frontend locally:

```bash
npm run dev
```
