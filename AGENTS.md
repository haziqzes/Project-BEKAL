# AGENTS.md — Project BEKAL

> **Project:** BEKAL  
> **Owner / Creator:** Wan Mohamad Haziq Mirza  
> **Canonical local workspace:** `C:\Projects\Project-BEKAL`  
> **Repository:** `haziqzes/Project-BEKAL`  
> **Repository status:** Public, MIT licensed  
> **Current stable release:** `v0.2.0`  
> **Current mission:** Post-release maintenance only; no new product milestone is implicitly approved  
> **Last updated:** 2026-10-15

---

## 1. Purpose

This file is the persistent operating contract for coding agents working on Project BEKAL.

The owner grants broad implementation authority inside the BEKAL repository for already-approved work. Routine implementation, testing, documentation, refactoring, and bug fixing may continue without repeated approval when they stay inside the accepted milestone and preserve product/privacy boundaries.

The core rule is:

> **Implementation may change when justified, but product scope, privacy/security boundaries, persistent-data semantics, accepted architecture, licensing, and repository visibility must not be silently redefined.**

Stop for owner input when a decision materially changes one of those boundaries.

---

## 2. Project identity

BEKAL is a standalone, local-first grocery receipt intelligence platform created by **Wan Mohamad Haziq Mirza**.

Current user goal:

> Turn receipt PDFs into reviewed, structured, private data that can be saved, maintained, analyzed, and exported.

Canonical workflow:

```text
PDF
 ↓
Validate
 ↓
Extract / local OCR fallback
 ↓
Normalize / flag uncertainty
 ↓
Review beside original PDF
 ↓
Confirm & Save
 ↓
PostgreSQL + private original PDF
 ↓
History / Dashboard / CSV
```

The original PDF is the source of truth.

BEKAL is intentionally separate from Project HANA. Any future integration should use an explicit API boundary rather than direct database coupling.

---

## 3. Current release state

### V0.1 — complete

V0.1 established the public receipt-processing core:

- PDF intake/preview;
- embedded-text extraction;
- local Tesseract OCR fallback;
- metadata and line-item parsing;
- conservative normalization;
- editable review/manual fallback;
- explicit Confirm & Save;
- duplicate warning;
- PostgreSQL persistence;
- private original-PDF storage;
- Receipt History with view/edit/delete;
- monthly Dashboard;
- UTF-8 CSV exports;
- interrupted-file reconciliation;
- synthetic regression coverage;
- public-repository safety/history scanning.

### V0.2 — complete and released

V0.2 added:

- Tauri 2 native Windows shell;
- bundled React desktop UI;
- packaged loopback API bridge;
- conservative local service lifecycle ownership;
- private per-user installed runtime;
- generated private runtime `.env`;
- Windows NSIS installer;
- Start Menu integration;
- Windows CI packaging/auditing;
- owner-machine install/relaunch/uninstall/reinstall acceptance.

Public release:

```text
Tag:       v0.2.0
Installer: BEKAL_0.2.0_x64-setup.exe
SHA-256:   E110665D77686000D872E9FD391C41AC40D21ECEC682CEB7381CD1C9A4895722
```

The V0.2 release is closed. Do not keep calling it incomplete because a new idea appeared.

---

## 4. Current mission

BEKAL is in **post-release maintenance**.

Routine allowed work includes:

- bug fixes;
- dependency/security maintenance;
- tests/CI reliability;
- documentation cleanup;
- installer/release quality corrections;
- small reversible usability/accessibility fixes that do not redefine product scope.

No new product milestone is automatically active.

Mobile clients, cloud sync, authentication, multi-user accounts, pantry/recipe/budget features, replacing Docker/PostgreSQL, or remote network exposure require an explicit new milestone/architecture decision.

See `docs/roadmap.md`.

---

## 5. Source-of-truth documents

Read current documentation before substantial work.

Priority when current documents conflict:

1. `AGENTS.md` — operating contract and current mission
2. `docs/privacy-security.md` — privacy/security boundary
3. `docs/architecture.md` — current architecture/runtime invariants
4. `docs/development.md` — current development/release workflow
5. `docs/roadmap.md` — milestone/backlog boundary
6. `README.md` / `docs/README.md` — current public/user overview
7. `docs/user-guide.md` / `docs/installation.md` — current user behavior

Historical planning documents live under `docs/archive/` and may describe earlier project states. They are evidence/history, not current instructions.

If a conflict affects scope, privacy, persistent data, licensing, repository visibility, public-release policy, or major architecture, stop and raise it to the owner rather than silently selecting a new direction.

---

## 6. Accepted architecture

### Desktop

- Tauri 2 / Rust
- product name `BEKAL`
- identifier `com.haziqzes.bekal`
- bundled React frontend
- Windows NSIS installer

### Frontend

- React
- TypeScript
- Vite

UI principles:

- simple;
- calm;
- readable;
- low clutter;
- functional before decorative;
- understandable without developer knowledge.

### Backend

- Python
- FastAPI

Keep receipt-processing logic testable and separate from HTTP route glue.

### Database

- PostgreSQL
- Alembic migrations

Core entities:

```text
receipts
receipt_items
products
product_aliases
categories
```

### OCR

- prefer usable embedded PDF text;
- local Tesseract fallback for scanned PDFs;
- do not make paid/cloud OCR mandatory for the core path.

### Packaged runtime

Installed runtime:

```text
%LOCALAPPDATA%\com.haziqzes.bekal\runtime
```

Packaged Compose project:

```text
bekal-desktop
```

Invariants:

- FastAPI bound only to `127.0.0.1:8000`;
- packaged PostgreSQL has no host TCP exposure;
- release builds use the packaged runtime even when launched from a source-repository working directory;
- repository discovery is debug-only unless `BEKAL_REPO_ROOT` is explicitly supplied;
- a normal close stops only services owned by the current desktop session;
- normal shutdown/update/uninstall must not silently erase private receipt/database data.

### Development mode

The repository Docker Compose stack may run frontend/backend/PostgreSQL for development and testing.

Browser development mode remains supported but is not the preferred end-user installation path.

---

## 7. Receipt-processing rules

### Input

Current supported user input is receipt PDF.

Both paths must remain supported:

1. selectable-text PDF;
2. scanned/image PDF requiring OCR.

### Candidate before persistence

Extraction creates a temporary candidate first.

```text
Candidate
 ↓
Review
 ↓
Edit
 ↓
Explicit confirmation
 ↓
Permanent database + PDF storage
```

Do not silently persist extraction results merely because parsing succeeded.

### Uncertainty

Missing/uncertain values remain unknown and should be visibly reviewable.

Do not fabricate certainty or invent receipt contents to improve apparent extraction quality.

### Manual fallback

A failed/weak extraction must still allow manual entry beside the original PDF.

---

## 8. Privacy and repository safety

Core rule:

> **Source code may be public. User data must remain private.**

Never commit:

- real receipt PDFs/images;
- receipt-derived private OCR caches;
- PostgreSQL data directories/dumps;
- real CSV exports;
- private logs containing receipt data;
- real `.env` files;
- passwords, keys, tokens, credentials, private keys;
- user backups/private configuration.

`.env.example` is an intentionally public non-secret template and is allowed.

Use synthetic fixtures only for committed tests/demos.

Treat `.gitignore`, repository safety tooling, and CI privacy gates as security-relevant. Do not weaken them to make a change pass.

Run:

```powershell
python scripts/check_repository_safety.py --history
```

before public-facing merges/releases and after any change that could affect tracked/private file boundaries.

---

## 9. Authentication and remote access

V0.2 is local and single-user. Authentication is not part of the supported local topology.

Do **not** treat the current unauthenticated loopback API as safe for LAN/public exposure.

Any future remote/mobile/multi-user deployment requires a new security architecture covering at least authentication, authorization, transport security, session handling, exposure boundaries, and data ownership/synchronization.

---

## 10. Git authority and workflow

Inside this repository, an approved coding agent may:

- inspect history;
- create/edit/move/delete project files;
- refactor;
- update documentation;
- install project dependencies;
- run Docker/Compose;
- run migrations;
- run tests/builds/audits;
- use Git;
- create scoped branches/commits/PRs;
- push normal project commits when required by the accepted task.

Do not rewrite substantial user-authored history unless explicitly instructed.

Do not change the MIT license or repository visibility without explicit owner approval.

For substantial work:

1. establish repository/branch/HEAD/working-tree/origin state;
2. identify objective, affected subsystem, preserved behavior, non-goals, and evidence;
3. make the smallest coherent change;
4. run appropriate checks;
5. fix root causes rather than weakening gates;
6. review the full diff;
7. update current documentation when reality changes;
8. run final Git/privacy checks;
9. commit/push on a scoped branch;
10. open/update PR;
11. require green CI before merge;
12. require owner-machine acceptance when installer/runtime behavior changed;
13. merge only when gates pass;
14. remove temporary branches after merge;
15. verify exact final repository state.

Routine reversible implementation choices inside an approved task do not require repeated owner approval.

---

## 11. Testing expectations

Coverage percentage is not the goal. Core workflow reliability is.

Relevant checks include:

- PDF validation;
- text/OCR fallback selection;
- metadata/item parsing;
- normalization/category/quantity-unit logic;
- total/review validation;
- duplicate handling;
- persistence/update/delete;
- private PDF/recovery behavior;
- dashboard analytics;
- CSV export;
- API health;
- end-to-end synthetic workflow;
- frontend production build;
- dependency audits;
- repository history/privacy scan;
- Rust format/check/audit;
- Windows installer build/verification for packaging changes.

Use synthetic receipts only.

---

## 12. Material stop conditions

Stop and ask the owner before a decision that materially changes:

- product milestone/scope/finish line;
- privacy/security boundary;
- authentication/network-exposure model;
- irreversible persistent-data semantics;
- database/file migration of real data;
- accepted architecture;
- major framework/dependency strategy;
- required paid/external infrastructure;
- software license;
- repository visibility/public-release policy.

Useful ideas outside the accepted task go to the backlog rather than silently expanding the task.

---

## 13. Documentation hygiene

Current behavior belongs in:

```text
README.md
docs/README.md
docs/installation.md
docs/user-guide.md
docs/architecture.md
docs/development.md
docs/privacy-security.md
docs/roadmap.md
CHANGELOG.md
CONTRIBUTING.md
SECURITY.md
```

Historical milestone/planning snapshots belong under `docs/archive/`.

Do not create new root-level draft/spec files when an existing current document can be updated.

Release tags remain immutable snapshots even when current docs on `master` improve afterward.

---

## 14. Owner-run Windows PowerShell convention

When the owner must run a multi-step Windows command, produce **one self-contained PowerShell 5.1-compatible copy/paste block**.

Use this shape:

```powershell
& {
    $ErrorActionPreference = 'Stop'
    Set-StrictMode -Version Latest

    # ============================================================
    # 1. STRICT ENTRY STATE
    # ============================================================

    # Verify path/repository/branch/HEAD/remote/preconditions.
    # Fail closed before mutation.

    # ============================================================
    # 2. MAIN OPERATION
    # ============================================================

    # Perform the bounded mutation.

    # ============================================================
    # 3. VERIFICATION
    # ============================================================

    # Run tests/checks/audits.

    # ============================================================
    # 4. FINAL STATE
    # ============================================================

    # Verify final invariants.

    # ============================================================
    # 5. FINAL RESULT
    # ============================================================

    # Print concise summary only after all gates pass.
}
```

Rules:

- always wrap the full operation in `& { ... }`;
- set `$ErrorActionPreference = 'Stop'`;
- normally use `Set-StrictMode -Version Latest`;
- fail closed before mutation;
- keep mutation in MAIN OPERATION;
- run tests/audits in VERIFICATION;
- verify branch/HEAD/working tree/runtime invariants in FINAL STATE;
- print a final result only after all gates pass;
- use PowerShell 5.1-compatible syntax unless explicitly told otherwise;
- use `@(...)` where scalar/array collapse could break StrictMode logic;
- never assign to built-in `$Host`;
- allow tracked `.env.example` while rejecting real `.env` / secret `.env.*` files;
- do not weaken safety/privacy/test gates to make a script continue;
- prefer one copy/paste block over multiple disconnected commands.

---

## 15. Final operating principle

When uncertain, return to this:

> **BEKAL exists to reliably turn receipt PDFs into reviewed, structured, private, useful data.**

If a task strengthens that path and belongs to the accepted mission, do it.

If it changes the mission, architecture, privacy boundary, or product scope, stop and make that decision explicit first.

---

**Project BEKAL**  
Created by **Wan Mohamad Haziq Mirza**
