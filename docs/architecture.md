# Architecture

This document describes the current BEKAL architecture on `master` after the V0.2 Windows desktop release.

## Design goals

BEKAL is intentionally:

- local-first;
- single-user in the current release;
- conservative with uncertain receipt data;
- explicit about review before persistence;
- independent of required paid AI/cloud OCR services;
- structured so the user-facing desktop shell does not rewrite the proven receipt-processing core.

## Current technology stack

| Layer | Technology |
| --- | --- |
| Desktop shell | Tauri 2 / Rust |
| Frontend | React + TypeScript + Vite |
| Backend | FastAPI / Python |
| Database | PostgreSQL |
| Migrations | Alembic |
| PDF text | local PDF parsing |
| OCR fallback | local Tesseract |
| Desktop runtime | Docker Desktop + packaged Docker Compose template |
| Development runtime | Docker Compose |
| Installer | Tauri NSIS bundle |

## Packaged Windows topology

```text
Windows user
   │
   ▼
BEKAL.exe
Tauri 2
   │
   ├── bundled React frontend
   │
   └── desktop lifecycle manager
           │
           ├── prepare private runtime
           ├── start packaged Docker services
           ├── apply Alembic migrations
           ├── wait for DB health
           └── show window
                    │
                    ▼
             127.0.0.1:8000
                 FastAPI
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     PostgreSQL         private runtime-data
   Docker volume        receipt PDFs/candidates
```

The packaged Compose project is named `bekal-desktop`.

The packaged desktop does **not** start a frontend Docker container. The React frontend is bundled directly into the Tauri application.

## Installed runtime location

The V0.2 installed runtime is materialized under the Tauri local application-data directory:

```text
%LOCALAPPDATA%\com.haziqzes.bekal\runtime\
├── .env
├── docker-compose.yml
├── backend\
└── runtime-data\
```

The `.env` file is generated locally and remains private. Managed runtime files can be refreshed by compatible application updates. Private receipt data is preserved separately.

PostgreSQL data lives in the stable named Docker volume for the packaged Compose project.

## Runtime isolation

Release builds use the packaged per-user runtime even if BEKAL is launched from a shell whose current directory happens to be a Project-BEKAL source checkout.

Repository auto-discovery is retained only for debug/development behavior or an explicit `BEKAL_REPO_ROOT` override.

This rule prevents an installed release from accidentally attaching itself to a development Compose stack merely because of the caller's working directory.

## Network boundary

The packaged FastAPI service is bound only to:

```text
127.0.0.1:8000
```

Packaged PostgreSQL is not exposed to a host TCP port.

The Tauri UI accesses the loopback FastAPI service. Browser development mode uses the Vite `/api` proxy. The backend CORS policy allows only the expected Tauri application origins rather than a wildcard.

V0.2 does not provide authentication because the released topology is local and single-user. If BEKAL is ever exposed beyond loopback, authentication and transport security must be designed before that deployment model is considered supported.

## Browser development topology

The repository development stack remains available:

```text
Docker Compose
├── frontend  -> localhost:5173
├── backend   -> localhost:8000
└── postgres
```

This mode exists for development, testing, and recovery work. It is not the recommended end-user installation path.

## Receipt-processing pipeline

```text
PDF
 ↓
Validate
 ↓
Temporary candidate
 ↓
Embedded-text extraction
 ↓
Usable text?
 ├── yes -> parse
 └── no  -> local Tesseract OCR -> parse
 ↓
Conservative normalization
 ↓
Review warnings / total checks
 ↓
Human review beside original PDF
 ↓
Explicit Confirm & Save
 ↓
PostgreSQL + private original PDF
 ↓
History / Dashboard / CSV
```

### Input validation

Receipt intake validates PDF characteristics and uses internal UUID candidate identifiers. Original user filenames are never trusted as storage paths.

### Temporary candidate

Extraction does not immediately create a permanent receipt. Candidate state remains temporary until explicit confirmation.

### Extraction order

Selectable PDF text is preferred. OCR is a fallback, not the default. Missing fields stay unknown rather than being fabricated.

### Review

The frontend owns temporary edits while the candidate is being reviewed. The original PDF stays visible as the source of truth.

### Persistence

Confirmed structured data is stored in PostgreSQL. The original receipt PDF is stored as a private file, with the database holding its relative reference and hash rather than the PDF bytes.

Core entities are:

```text
receipts
receipt_items
products
product_aliases
categories
```

## Saved-receipt behavior

Receipt History uses API routes to list, view, update, and delete saved receipts. Private PDFs are served only through receipt-aware API access; the private storage root is not exposed as a general static directory.

Structured edits do not replace the original PDF.

## Dashboard and export

Dashboard analytics are computed from permanently saved receipt data. Missing monetary values remain incomplete rather than being inferred.

CSV exports are generated on demand in memory from saved data. The server does not retain generated export files.

## Failure and recovery model

Database changes and filesystem changes cannot be made perfectly atomic with one transaction.

BEKAL therefore uses conservative ordering, rollback/cleanup paths, and startup reconciliation around private receipt file operations. Interrupted states are handled so that receipt evidence is preserved for recovery rather than silently discarded where possible.

## Lifecycle ownership

The desktop lifecycle manager distinguishes between services that were already running and services started by the current BEKAL session.

A normal desktop close stops only services that the application owns. It does not remove persistent PostgreSQL volumes or private receipt files.

## Privacy boundary

The public repository may contain source code, migrations, documentation, and synthetic fixtures.

It must not contain real receipts, private exports, database data, generated local `.env` files, secrets, credentials, or private runtime content.

See [Privacy & Security](privacy-security.md).

## Explicit architecture non-goals in V0.2

V0.2 does not attempt to:

- replace PostgreSQL with an embedded database;
- remove Docker Desktop;
- add cloud synchronization;
- add authentication/accounts;
- expose the backend to a LAN or the public internet;
- provide Android/iOS clients;
- implement native multi-device synchronization;
- integrate HANA directly into BEKAL;
- replace the receipt-processing core with a cloud AI dependency.

Those would be separate architecture decisions, not documentation-level extensions of V0.2.
