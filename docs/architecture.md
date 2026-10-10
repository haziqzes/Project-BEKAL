# Foundation architecture

The React + TypeScript frontend uses Vite's local `/api` proxy to reach FastAPI. FastAPI exposes process and PostgreSQL health checks. PostgreSQL uses a private Docker volume. A host-mounted, ignored `runtime-data/` directory is reserved for confirmed receipt PDFs in a later phase.

Alembic has an empty foundation revision so migration commands work now. Receipt tables and persistence will be added in Phase 4. The approved V0.1 design remains in the repository's `BEKAL_*` documents.

Phase 1 adds `POST /api/candidates` for PDF-only temporary intake, `GET /api/candidates/{id}/pdf` for preview, and `DELETE /api/candidates/{id}` for early discard. The API verifies the extension, content type, 10 MiB size limit, PDF header, and readable unencrypted PDF structure. Accepted files use UUID names in the ignored `runtime-data/candidates/` directory. Candidate metadata exists only in backend memory; files expire after one hour and are cleared on restart or shutdown. A separate filename helper reserves the `YYYY-MM-DD_store.pdf` convention for a later confirmed-save phase.

The frontend renders the original candidate PDF locally with PDF.js and page controls. This rendering does not extract or save receipt data.
