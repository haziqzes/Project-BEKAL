# Development notes

From the repository root, run `docker compose up --build -d`. Use `docker compose ps` to confirm all three services report healthy. Run `docker compose exec backend alembic upgrade head` to apply the foundation migration.

The frontend is available at `http://localhost:5173`, the API at `http://localhost:8000/api/health`, and the database check at `http://localhost:8000/api/health/db`.

To exercise Phase 1, choose a PDF in the frontend and click **Validate and preview**. The backend returns a temporary UUID and an original-PDF preview URL. Click **Discard preview** to remove the candidate early. Candidates also expire after one hour and are cleared when the backend restarts. No receipt data is saved to PostgreSQL.

For host-based development, install frontend dependencies with `npm install` in `frontend/`, and install the backend with `python -m pip install -e '.[dev]'` in `backend/`. Set `DATABASE_URL` to a local PostgreSQL URL before running the database check or migrations. Run `npm run dev`, `uvicorn app.main:app --reload`, `npm run build`, and `python -m pytest` from their respective directories.
