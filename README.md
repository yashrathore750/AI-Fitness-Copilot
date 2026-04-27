# AI Fitness Copilot

FastAPI backend for a hybrid fitness system that separates deterministic nutrition and activity analysis from recommendation generation.

## What is implemented

- Async FastAPI API with SQLite-by-default and PostgreSQL-ready SQLAlchemy models
- User, food log, activity log, and nutrition reference persistence
- Deterministic daily nutrition aggregation and calorie expenditure estimation
- Rule-based deficiency detection with severity scoring
- Context building and fallback insight generation for actionable recommendations
- Focused end-to-end test for the daily analysis workflow

## Run locally

1. Install dependencies:

   ```powershell
   pip install -e .[dev]
   ```

2. Start the API:

   ```powershell
   uvicorn app.main:app --reload
   ```

3. Open docs:

   `http://127.0.0.1:8000/docs`

## Run with Docker

SQLite is file-based, so the development container uses a mounted volume for the database file instead of a separate database service.

1. Build and start the API:

   ```powershell
   docker compose up --build
   ```

2. Open docs:

   `http://127.0.0.1:8000/docs`

3. Stop the stack:

   ```powershell
   docker compose down
   ```

4. Remove the persisted SQLite volume if you want a clean database:

   ```powershell
   docker compose down -v
   ```

## Key endpoints

- `POST /users`
- `POST /food-log`
- `GET /food-log`
- `POST /activity`
- `GET /activity`
- `GET /analysis/today`

## Notes

- The default database is local SQLite for a zero-friction start.
- In Docker development, SQLite is persisted in the `sqlite_data` volume at `/app/data/fitness_copilot.db`.
- Set `DATABASE_URL` to a PostgreSQL URL when moving beyond local development.
- The insight engine is intentionally local and deterministic for now; it is the seam where an LLM provider can be added next.