# BEKAL

BEKAL is a local-first receipt intelligence project created by **Wan Mohamad Haziq Mirza**. V0.1 established the receipt-processing core; V0.2 adds a native Windows desktop shell and installer while preserving the same private, local-first backend and data model. The current codebase includes PDF receipt intake, local extraction/OCR, editable review, confirmed persistence, saved-receipt history and editing, a monthly dashboard, CSV export, recovery checks, and a Tauri-based Windows application.

## Windows application (V0.2)

BEKAL V0.2 can be installed as a normal per-user Windows application. Docker Desktop remains a prerequisite because PostgreSQL and FastAPI continue to run locally in containers.

The installed application:

- launches as `BEKAL.exe` from Windows rather than requiring a browser tab;
- starts its private `bekal-desktop` PostgreSQL/FastAPI runtime when required;
- keeps FastAPI bound only to `127.0.0.1:8000` and does not expose PostgreSQL to host TCP;
- stores private writable runtime data under the user's local application-data directory, outside the source repository;
- preserves the generated private `.env`, receipt PDFs, and PostgreSQL data across normal shutdown, uninstall, and reinstall;
- installs a Start Menu shortcut and uses the BEKAL application branding.

The installer is intentionally unsigned in V0.2. Verify published checksums before running downloaded installer artifacts.

See [V0.2 Windows packaging](docs/v0.2-windows-packaging.md) for the packaging/runtime contract and acceptance evidence.

## Docker/browser development quick start

Requires Docker Desktop with Compose.

1. Copy `.env.example` to `.env` and set a local PostgreSQL password.
2. Run `docker compose up --build -d`.
3. Run `docker compose ps` and wait until `frontend`, `backend`, and `postgres` are healthy.
4. Run `docker compose exec backend alembic upgrade head`.
5. Open `http://localhost:5173`. Select a PDF, review and correct the candidate beside the original, then explicitly confirm to save. Use **Receipt History** to view/edit/delete saved receipts and download CSVs; use **Dashboard** for the selected month's overview.

API checks: `http://localhost:8000/api/health` and `http://localhost:8000/api/health/db`.

Run smoke tests with `docker compose exec backend python -m pytest`, or from a host Python environment with `python -m pip install -e '.[dev]'` in `backend/`. Run the frontend build with `npm ci` followed by `npm run build` in `frontend/`.

Stop services with `docker compose down`. PostgreSQL data persists in its named volume. `docker compose down --volumes` removes that database volume.

## Scope and privacy

The approved V0.1 scope is in `BEKAL_Requirements_V0.1.md` and the other `BEKAL_*` design documents. Recipes, pantry tracking, budgeting, authentication, mobile apps, and cloud services remain outside the current product scope.

Real receipts, database files, exports, credentials, and runtime data belong outside source control. `runtime-data/` holds private local receipt files and is ignored by Git. Use only synthetic fixtures in `examples/synthetic/`.

Phase 1 PDFs are held in `runtime-data/candidates/` for at most one hour. They are removed when discarded, on backend restart, after expiry, or after a confirmed save. The original filename is never used as a storage path. Upload and extraction alone do not save receipt data to PostgreSQL.

Phase 2 attempts selectable PDF text first and runs local Tesseract OCR only if that text is unusable. The candidate view shows the extraction method, available receipt metadata, and line items. Missing fields remain blank. Extraction results are returned to the browser only; they are not saved to PostgreSQL. The Docker backend includes Tesseract. Host-based backend development needs a local Tesseract installation for scanned PDFs.

Phase 3 prepares conservative product names, initial categories, quantity/unit guesses only when supported, and review warnings. In the browser, edit receipt fields and item rows, add or delete rows, and compare item totals with the subtotal or receipt total. When extraction produces no usable data or fails, the same form supports manual entry with the original PDF visible. Edits remain temporary until explicit confirmation.

Phase 4 adds **Confirm & Save** after the user checks an acknowledgement beside the original PDF. The backend warns about likely duplicates and lets the user choose whether to continue. Confirmed metadata, item rows, products, categories, and applicable aliases are saved in PostgreSQL; the original PDF is copied to ignored private `runtime-data/receipts/YYYY/MM/` storage. The temporary candidate is removed after a successful save. Database/file errors keep the candidate available for retry. A machine crash in the narrow interval between file creation and database commit could leave an orphan private PDF; ordinary save errors clean it up.

Phase 5 adds a saved-receipt history table, private original-PDF viewing, explicit metadata and item edits, and confirmed deletion of a saved receipt and its PDF. Phase 6 adds a read-only calendar-month dashboard based only on saved receipts. It shows known spending, receipt count, category item spending, product purchase occurrences, comparable unit prices, and recent receipts. Missing totals remain marked as incomplete. Phase 7 adds on-demand UTF-8 `receipts.csv` and `items.csv` downloads from saved data. Export files are not stored by the server; downloaded copies contain private receipt data and should be kept outside Git.

Phase 8 adds a synthetic end-to-end regression check and startup reconciliation for interrupted private-PDF saves and deletes. Unreferenced PDFs are kept in ignored private `runtime-data/receipts/.recovery/` for manual review.

## Release status

BEKAL V0.1 is complete and publicly released. BEKAL V0.2 desktop packaging has completed its owner-machine acceptance gate: native installation, packaged-runtime isolation, loopback-only FastAPI, non-exposed PostgreSQL, receipt/dashboard/history behavior, owned-service shutdown, relaunch persistence, uninstall data preservation, reinstall restoration, product version metadata, and Start Menu integration all passed with the corrected Windows installer.

Repository release gates include Git-history privacy scanning, backend tests and Python dependency auditing, frontend build and npm auditing, Rust format/check and dependency auditing, Windows NSIS packaging, installer verification, and GitHub Actions CI.

## License

BEKAL is released under the **MIT License**. See `LICENSE`.

See [architecture](docs/architecture.md), [development notes](docs/development.md), [V0.1 release candidate checks](docs/release-candidate.md), [public-release preparation](docs/public-release-preparation.md), and [V0.2 Windows packaging](docs/v0.2-windows-packaging.md) for details.
