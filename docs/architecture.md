# Foundation architecture

The React + TypeScript frontend uses Vite's local `/api` proxy to reach FastAPI. FastAPI exposes process and PostgreSQL health checks. PostgreSQL uses a private Docker volume. A host-mounted, ignored `runtime-data/` directory is reserved for confirmed receipt PDFs in a later phase.

Alembic has an empty foundation revision so migration commands work now. Receipt tables and persistence will be added in Phase 4. The approved V0.1 design remains in the repository's `BEKAL_*` documents.
