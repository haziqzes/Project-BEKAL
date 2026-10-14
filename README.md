# BEKAL

BEKAL is a local-first receipt intelligence project created by **Wan Mohamad Haziq Mirza**. V0.1 aims to turn receipt PDFs into reviewed, structured data for storage, simple analysis, and CSV export. The current codebase includes receipt intake, extraction, review, confirmed local persistence, saved-receipt history and editing, and a monthly dashboard.

## Quick start

Requires Docker Desktop with Compose.

1. Copy `.env.example` to `.env` and set a local PostgreSQL password.
2. Run `docker compose up --build -d`.
3. Run `docker compose ps` and wait until `frontend`, `backend`, and `postgres` are healthy.
4. Run `docker compose exec backend alembic upgrade head`.
5. Open `http://localhost:5173`. Select a PDF, review and correct the candidate beside the original, then explicitly confirm to save. Use **Receipt History** to view/edit/delete saved receipts and **Dashboard** for the selected month's overview.

API checks: `http://localhost:8000/api/health` and `http://localhost:8000/api/health/db`.

Run smoke tests with `docker compose exec backend python -m pytest`, or from a host Python environment with `python -m pip install -e '.[dev]'` in `backend/`. Run the frontend build with `npm ci` followed by `npm run build` in `frontend/`.

Stop services with `docker compose down`. PostgreSQL data persists in its named volume. `docker compose down --volumes` removes that database volume.

## Scope and privacy

The approved V0.1 scope is in `BEKAL_Requirements_V0.1.md` and the other `BEKAL_*` design documents. Recipes, pantry tracking, budgeting, authentication, mobile apps, and cloud services are outside V0.1.

Real receipts, database files, exports, credentials, and runtime data belong outside source control. `runtime-data/` holds private local receipt files and is ignored by Git. Use only synthetic fixtures in `examples/synthetic/`.

Phase 1 PDFs are held in `runtime-data/candidates/` for at most one hour. They are removed when discarded, on backend restart, after expiry, or after a confirmed save. The original filename is never used as a storage path. Upload and extraction alone do not save receipt data to PostgreSQL.

Phase 2 attempts selectable PDF text first and runs local Tesseract OCR only if that text is unusable. The candidate view shows the extraction method, available receipt metadata, and line items. Missing fields remain blank. Extraction results are returned to the browser only; they are not saved to PostgreSQL. The Docker backend includes Tesseract. Host-based backend development needs a local Tesseract installation for scanned PDFs.

Phase 3 prepares conservative product names, initial categories, quantity/unit guesses only when supported, and review warnings. In the browser, edit receipt fields and item rows, add or delete rows, and compare item totals with the subtotal or receipt total. When extraction produces no usable data or fails, the same form supports manual entry with the original PDF visible. Edits remain temporary until explicit confirmation.

Phase 4 adds **Confirm & Save** after the user checks an acknowledgement beside the original PDF. The backend warns about likely duplicates and lets the user choose whether to continue. Confirmed metadata, item rows, products, categories, and applicable aliases are saved in PostgreSQL; the original PDF is copied to ignored private `runtime-data/receipts/YYYY/MM/` storage. The temporary candidate is removed after a successful save. Database/file errors keep the candidate available for retry. A machine crash in the narrow interval between file creation and database commit could leave an orphan private PDF; ordinary save errors clean it up.

Phase 5 adds a saved-receipt history table, private original-PDF viewing, explicit metadata and item edits, and confirmed deletion of a saved receipt and its PDF. Phase 6 adds a read-only calendar-month dashboard based only on saved receipts. It shows known spending, receipt count, category item spending, product purchase occurrences, comparable unit prices, and recent receipts. Missing totals remain marked as incomplete. CSV export is a later phase.

The repository is intended to remain private during development. No software license has been selected.

See [architecture](docs/architecture.md) and [development notes](docs/development.md) for details.
