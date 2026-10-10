# Foundation architecture

The React + TypeScript frontend uses Vite's local `/api` proxy to reach FastAPI. FastAPI exposes process and PostgreSQL health checks. PostgreSQL uses a private Docker volume. A host-mounted, ignored `runtime-data/` directory is reserved for confirmed receipt PDFs in a later phase.

Alembic has an empty foundation revision so migration commands work now. Receipt tables and persistence will be added in Phase 4. The approved V0.1 design remains in the repository's `BEKAL_*` documents.

Phase 1 adds `POST /api/candidates` for PDF-only temporary intake, `GET /api/candidates/{id}/pdf` for preview, and `DELETE /api/candidates/{id}` for early discard. The API verifies the extension, content type, 10 MiB size limit, PDF header, and readable unencrypted PDF structure. Accepted files use UUID names in the ignored `runtime-data/candidates/` directory. Candidate metadata exists only in backend memory; files expire after one hour and are cleared on restart or shutdown. A separate filename helper reserves the `YYYY-MM-DD_store.pdf` convention for a later confirmed-save phase.

The frontend renders the original candidate PDF locally with PDF.js and page controls. This rendering does not extract or save receipt data.

Phase 2 adds `POST /api/candidates/{id}/extract`. The extraction module reads embedded text from all PDF pages, then checks for at least three nonempty lines, 25 alphanumeric characters, and a monetary amount. If that heuristic fails, it renders each page with PDFium and uses local Tesseract OCR. The parser returns available metadata and raw item candidates; missing fields are null and unparseable content returns `no_data`. The endpoint computes results on demand and never writes receipt data to PostgreSQL.

Phase 3 adds a pure review-preparation module to the extraction response. It retains each source item name, applies limited cleanup, assigns a predefined category only on whole-word matches, and flags unknown or inconsistent values. Quantity/unit inference from a name requires supporting price arithmetic; unsupported values remain null. The React review form owns edits in memory, recalculates warnings and totals after changes, and shows the original PDF alongside the form. Re-extraction replaces the review state. No candidate review endpoint writes to PostgreSQL or permanent file storage.
