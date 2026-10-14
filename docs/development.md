# Development Guide

This guide describes the current development workflow for BEKAL after the V0.2 Windows desktop release.

## Repository layout

```text
Project-BEKAL/
├── backend/                 FastAPI, receipt logic, migrations, tests
├── frontend/                React UI + Tauri desktop shell
│   ├── src/
│   ├── scripts/
│   └── src-tauri/
├── desktop/                 packaged desktop Docker Compose template
├── docs/                    current documentation + archive
├── examples/synthetic/      public-safe synthetic receipt fixtures
├── scripts/                 repository safety tooling
├── .github/workflows/       CI
├── README.md
├── AGENTS.md
└── LICENSE
```

## Development principles

- Preserve the local-first privacy boundary.
- Use synthetic receipts only in committed tests and examples.
- Do not silently expand a milestone into unrelated product scope.
- Keep the original receipt PDF as the source of truth.
- Prefer conservative unknown/null values over fabricated certainty.
- Keep user-facing behavior consistent between browser development mode and the packaged desktop where practical.

Read `AGENTS.md` before substantial implementation work.

## Prerequisites

### Browser/Docker development

Required:

- Git
- Docker Desktop with Docker Compose
- Node.js/npm for direct frontend work

### Desktop development/builds

Additionally required:

- Rust toolchain
- Windows MSVC build tools
- Tauri prerequisites / WebView2 environment

### Optional host backend development

For running FastAPI outside Docker:

- Python
- PostgreSQL access
- Tesseract available on `PATH` for scanned-PDF OCR

The Docker backend already includes Tesseract.

## Environment setup

From the repository root:

```powershell
Copy-Item .env.example .env
```

Set a local PostgreSQL password in `.env`.

`.env.example` is intentionally tracked and public. Real `.env` files are private and must not be committed.

## Browser development mode

Start the repository stack:

```powershell
docker compose up --build -d
```

Check health:

```powershell
docker compose ps
```

Apply migrations:

```powershell
docker compose exec backend alembic upgrade head
```

Open:

```text
Frontend: http://localhost:5173
API:      http://localhost:8000/api/health
DB health:http://localhost:8000/api/health/db
```

Stop the development services with:

```powershell
docker compose down
```

The normal development shutdown preserves the PostgreSQL named volume.

## Backend tests

With the Docker stack available:

```powershell
docker compose exec -T backend pytest -q
```

For host-based backend development:

```powershell
cd backend
python -m pip install -e '.[dev]'
python -m pytest -q
```

Set `DATABASE_URL` appropriately when running database-backed operations outside Docker.

## Frontend development

```powershell
cd frontend
npm ci
npm run dev
```

Production build:

```powershell
npm run build
```

Dependency audit:

```powershell
npm audit --audit-level=low
```

## Tauri desktop development

The frontend package contains helper scripts that prepare generated icons and the packaged runtime template.

From `frontend/`:

```powershell
npm ci
npm run tauri -- dev
```

Release build:

```powershell
npm run tauri -- build
```

The Tauri configuration is in:

```text
frontend/src-tauri/tauri.conf.json
```

The current packaged application identity is:

```text
Product:     BEKAL
Version:     0.2.0
Identifier:  com.haziqzes.bekal
Bundle:      NSIS
Install mode: current user
```

## Packaged runtime preparation

The desktop build prepares a minimal runtime resource containing the backend and desktop Compose files required by the installed application.

The source template is built from repository files by:

```text
frontend/scripts/prepare-desktop-runtime.mjs
```

The installed application materializes managed runtime files into its private per-user application-data location on first run/update. Do not commit generated private runtime data.

## Repository safety gate

Run:

```powershell
python scripts/check_repository_safety.py --history
```

The safety gate treats `.env.example` as an allowed public template while rejecting real environment/secret files, private receipt/runtime content, sensitive file types, and configured credential patterns.

Do not weaken this check merely to make CI pass.

## Core verification set

A meaningful change should run the checks appropriate to the affected subsystem. The release-grade set includes:

```text
backend tests
Python dependency audit
frontend production build
npm dependency audit
repository history/privacy scan
Rust formatting/check
Rust dependency audit
Windows NSIS build/installer verification when desktop packaging changes
```

GitHub Actions performs the repository CI gates on pushed branches/PRs.

## Receipt workflow regression expectations

Changes to the core path should preserve:

```text
upload
→ validate
→ extract / OCR fallback
→ review / edit
→ confirm / save
→ history
→ dashboard
→ CSV export
```

Use synthetic fixtures only.

## Data and persistence changes

Any change that alters migrations, irreversible storage semantics, receipt-file layout, delete/recovery behavior, or upgrade compatibility is a material architecture decision. It must be reviewed as such rather than treated as a routine refactor.

## Desktop runtime changes

Changes to lifecycle ownership must preserve these invariants:

- packaged FastAPI stays loopback-only;
- packaged PostgreSQL is not host-exposed;
- an installed release does not accidentally attach to a source checkout because of the caller's current directory;
- shutdown stops only services owned by the current BEKAL session;
- normal shutdown/update/uninstall does not silently erase private receipt/database data.

## Documentation rule

Current behavior belongs in the current docs:

```text
docs/README.md
docs/installation.md
docs/user-guide.md
docs/architecture.md
docs/development.md
docs/privacy-security.md
docs/roadmap.md
```

Milestone planning snapshots and superseded release-candidate documents belong under `docs/archive/`.

Avoid creating new root-level draft documents when an existing current document can be updated.

## Branching and release workflow

For substantial work:

1. start from current `master`;
2. create a scoped feature/docs/maintenance branch;
3. establish current evidence before mutation;
4. make bounded changes with explicit non-goals;
5. run applicable checks;
6. review the full diff and repository-safety impact;
7. open a PR;
8. require green CI before merge;
9. perform owner-machine acceptance for changes that affect installer/runtime behavior;
10. merge only after gates pass;
11. remove the temporary branch after merge.

The current stable release tag is `v0.2.0`. Release tags should remain immutable historical snapshots even when documentation on `master` continues to improve.

## Scope boundary

BEKAL is separate from HANA. Future integration, if approved, should use an explicit API boundary rather than direct database coupling.

Mobile apps, cloud sync, authentication, multi-user accounts, and major deployment changes are not implicit maintenance work. They require a new accepted milestone/architecture decision.
