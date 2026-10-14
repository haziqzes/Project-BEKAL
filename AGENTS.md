# AGENTS.md — Project BEKAL

> **Primary coding agent:** GPT-6 Astra / Codex  
> **Project:** BEKAL  
> **Owner / Creator:** Wan Mohamad Haziq Mirza  
> **Canonical local workspace:** `C:\Projects\Project-BEKAL`  
> **Repository:** `haziqzes/Project-BEKAL`  
> **Repository status:** Private during development  
> **Current target:** BEKAL V0.1  
> **Last updated:** 2026-10-14

---

# 1. Purpose

This file is the persistent operating contract and handoff document for any AI coding agent working on Project BEKAL.

Astra has broad working authority inside `C:\Projects\Project-BEKAL`. It may create, edit, delete, rename, move, refactor, test, document, and organize project files as needed to complete the approved V0.1 scope.

The core rule is:

> **Implementation may change freely when justified, but the product goal, privacy model, accepted architecture, and V0.1 finish line must not be silently changed.**

This file should be kept current as development progresses. At the end of each accepted phase, update the **Current Execution State** section before or with the phase handoff commit.

The owner has authorized routine continuation through the already-approved BEKAL V0.1 roadmap under the same confirmation-first operating philosophy used by Project HANA. Routine work inside an accepted phase may proceed without repeated owner approval. Stop and ask only when a decision materially changes approved scope, architecture, privacy/security, persistent-data semantics, licensing, repository visibility, public-release policy, or introduces a required paid/external dependency.

---

# 2. Project Identity

**BEKAL** is a standalone, local-first receipt intelligence platform created by **Wan Mohamad Haziq Mirza**.

BEKAL is intended to:

1. solve a real personal problem,
2. act as a serious learning platform,
3. become a strong GitHub / LinkedIn engineering portfolio project,
4. potentially become a public open-source project after V0.1 cleanup, privacy review, and license selection.

BEKAL is intentionally separate from Project HANA.

Repository tone:

> Casual enough to be approachable.  
> Professional enough to be credible.  
> Technical enough to demonstrate real engineering work.

---

# 3. Product Goal

BEKAL V0.1 has one primary job:

> **Turn receipt PDFs into clean, editable, structured data that can be stored, reviewed, analyzed, and exported.**

Canonical V0.1 workflow:

```text
PDF
 ↓
Extract
 ↓
Review / Edit
 ↓
Confirm
 ↓
Save
 ↓
Analyze
 ↓
Export CSV
```

Everything implemented for V0.1 should support this loop.

---

# 4. Current Execution State

## Completed

### Phase 0 — Foundation ✅

Accepted commit:

```text
1f58e45 Scaffold BEKAL Phase 0 foundation
```

Verified foundation includes:

- React + TypeScript frontend
- FastAPI backend
- PostgreSQL
- Docker Compose
- migration framework
- API / database health checks
- basic smoke tests
- local-first runtime structure
- privacy-conscious `.gitignore`

### Phase 1 — Receipt Intake ✅

Accepted commit:

```text
77dee57 feat: add temporary receipt PDF intake and preview
```

Verified Phase 1 behavior:

- PDF-only intake
- maximum upload size of 10 MiB
- backend PDF validation
- UUID candidate IDs
- temporary candidate storage
- one-hour candidate expiry
- cleanup on backend restart/shutdown
- manual discard
- original PDF preview with page controls
- no permanent receipt persistence
- no receipt data written to PostgreSQL
- synthetic PDF verified in browser
- backend tests passed
- frontend build passed
- dependency audit reported no vulnerabilities at acceptance time
- Docker services healthy

### Phase 2 — Receipt Extraction ✅

Accepted commit: `cc684f0 feat: add receipt text extraction and local OCR fallback` (pushed to private `origin/master`).

Verified Phase 2 behavior:

- embedded text is extracted from all pages and preferred when usable
- local Tesseract OCR handles scanned PDFs when embedded text is unusable
- temporary candidate responses contain available receipt metadata and line items
- missing values remain null and unreadable content reports `no_data`
- the frontend shows extraction method and candidate data beside the original PDF
- no receipt data is written to PostgreSQL
- synthetic text and scanned PDFs were verified in the browser
- backend tests and frontend build pass; all Compose services are healthy

### Phase 3 — Review & Normalization ✅

Accepted commit: `e8aa328 feat: add receipt review and normalization workflow` (pushed to private `origin/master`).

Verified Phase 3 behavior:

- conservative product-name cleanup, predefined categories, and supported quantity/unit inference
- missing or uncertain fields visibly flagged; item totals reconciled with subtotal or receipt total
- original PDF beside an editable temporary candidate
- pen action, row edit/save/cancel, add/delete rows, and editable metadata
- manual-entry form for no-data and extraction-error cases
- browser verification with synthetic text and scanned receipts; backend tests and frontend build pass
- PostgreSQL still contains only the foundation migration table; receipt data remains temporary

### Phase 4 — Persistence ✅

Accepted commit: `c6cf09c feat: persist confirmed receipts and original PDFs locally` (pushed to private `origin/master`).

Verified Phase 4 behavior:

- Alembic migration creates receipts, receipt items, products, aliases, and 16 predefined categories
- explicit review acknowledgement and Confirm & Save before permanent storage
- duplicate warning with an optional Save anyway action; UUID-based repeated-save protection
- simple product reuse and confirmed alias learning with conservative conflict handling
- private sanitized PDF naming, collision suffixes, and relative path references in PostgreSQL
- database and file error paths retain the temporary candidate; successful saves remove it
- synthetic text and scanned/OCR receipts were saved through the browser and inspected in PostgreSQL and private storage
- backend tests, frontend build, security audit, fresh and existing database migrations, and Compose health checks pass
- runtime PDFs, database data, `.env`, and other private data remain ignored by Git

### Phase 5 — Receipt History / CRUD ✅

Accepted commit: `dd5e91c feat: add saved receipt history and CRUD workflow` (pushed to private `origin/master`).

Verified Phase 5 behavior:

- simple date-first saved receipt history with item counts and deterministic ordering
- stored PDF accessed only by receipt ID, database relative path, and private-root containment checks
- side-by-side original PDF and persisted metadata/items, with explicit edits, row pen controls, add/delete rows, reconciliation, and update validation
- transactional updates preserve other receipts and shared products; aliases remain conservative
- explicit delete confirmation removes receipt/items/PDF; already-missing PDFs can be cleaned up
- 29 backend tests passed at acceptance time; frontend build and dependency checks passed
- a synthetic browser edit/reload/delete workflow was verified against PostgreSQL and private storage
- runtime PDFs, database data, `.env`, and other private data remained ignored by Git

### Phase 6 — Dashboard ✅

Implementation complete and verified in the Phase 6 dashboard commit that includes this handoff.

- read-only calendar-month API over permanently saved MYR receipts only
- known final-total spending with explicit missing-total count; receipt count and recent receipts
- top categories from known item line totals and most-purchased products from item-row occurrences
- conservative comparable unit prices using checked rows with positive quantity, same product/unit, and distinct receipts
- simple month selector and dashboard tables; recent receipt links reuse Phase 5 detail view
- empty and partial months handled without fabricating totals
- 33 backend tests pass, frontend build passes, synthetic browser checks pass

## Current Phase

### Phase 7 — CSV Export ✅

Implemented on-demand UTF-8 `receipts.csv` and `items.csv` downloads from saved MYR data. Exports are generated in memory and never stored by the backend. Nullable values stay blank, MYR fields remain decimal, and spreadsheet formula triggers in text are escaped. Empty exports, saved edits/deletes, backend tests, frontend build, audits, Compose health, and Git privacy were verified in the Phase 7 commit.

### Phase 8 — Testing / Stabilization ✅

Added a synthetic upload → extract → correct → save → view → CSV regression test. Startup reconciliation restores PDFs from interrupted deletes when the database row remains, finishes committed deletions, and quarantines unreferenced PDFs from interrupted saves in ignored private storage for manual review. Existing parser, normalization, database, duplicate, CSV, OCR, and failure-path tests remain passing. Verified build, audits, Compose health, and Git privacy in the Phase 8 commit.

### Phase 9 — V0.1 Release Candidate ✅

The frozen 13-step acceptance path has a synthetic end-to-end check through extraction, correction, save, history, dashboard, saved edit, both CSV exports, and PDF deletion. UI review, local Compose health, tests, build, audits, migrations, and Git privacy were checked. The repeatable release candidate verification and remaining limits are documented in `docs/release-candidate.md`.

### Phase 10 — Public-Release Preparation 🚧 Authorized / next implementation milestone

Review source and history privacy, safety checks, documentation, creator credit, and synthetic demo readiness. Do not select a software license or change repository visibility without owner approval.

---

# 5. V0.1 Scope Freeze

## Included in V0.1

- PDF receipt file picker
- text-based PDF support
- scanned/image PDF support
- embedded-text extraction before OCR
- local OCR fallback
- store-name extraction
- receipt-date extraction
- receipt/invoice number where available
- payment method where available
- subtotal, discounts, tax, and final total where available
- line-item extraction
- cleaned/canonical product names
- product categories
- quantity/unit inference when possible
- unit price and line total when possible
- simple review/confidence indicators
- original PDF beside extracted table
- row-level editing with pen/edit control
- add-row and delete-row capability
- editable receipt metadata
- receipt-total validation
- manual-entry fallback
- confirmation before permanent persistence
- duplicate-upload warning
- original receipt PDF storage
- date + store readable filenames
- internal receipt UUIDs
- PostgreSQL persistence
- receipt history
- reopen/edit/delete saved receipts
- product alias memory from corrections
- current-month dashboard
- simple month selector
- monthly spending total
- receipt count
- top categories
- most frequently purchased products
- recent price history
- recent receipts
- CSV export as `receipts.csv` and `items.csv`
- MYR-only behavior
- Docker-ready local development
- synthetic demo/test receipts
- automated tests for the core workflow

## Explicitly out of scope for V0.1

Do not implement unless the owner explicitly changes the specification:

- recipe generation
- recipe recommendations
- pantry inventory
- pantry depletion
- grocery budgeting
- meal planning
- nutrition planning
- store-price crawling
- live supermarket price lookup
- price prediction
- shopping-list optimization
- route optimization
- mobile application
- camera/photo receipt capture
- barcode scanning
- family accounts
- multi-user accounts
- role-based permissions
- authentication
- login
- public registration
- cloud sync
- hosted BEKAL accounts
- notifications
- HANA integration
- required external paid AI
- required cloud OCR
- advanced ML training pipelines
- XLSX generation
- currency conversion
- multi-currency analytics
- advanced receipt-history filtering
- branch/address/location tracking

When an attractive new idea appears:

> Put it in a backlog. Do not move the V0.1 finish line.

---

# 6. Scope-Control Rule

Before implementing any feature that is not obviously part of the current milestone, ask:

1. Does it directly support the approved V0.1 workflow?
2. Is it required by an existing acceptance criterion?
3. Does it fix a blocker preventing the current milestone from functioning?

If the answer to all three is **no**, defer it.

Astra is encouraged to state:

> "Useful idea, but outside the current milestone. I am placing it in the backlog and continuing with the approved scope."

---

# 7. Source-of-Truth Documents

Read the BEKAL design documents before substantial architectural changes.

Priority when documents conflict:

1. `BEKAL_Requirements_V0.1.md`
2. `BEKAL_ADR_V0.1.md`
3. `BEKAL_Data_Privacy_Security_V0.1.md`
4. `BEKAL_System_Architecture_V0.1.md`
5. `BEKAL_Development_Roadmap_V0.1.md`
6. `BEKAL_Project_Charter_V0.1.md`
7. `BEKAL_Document_Index.md`
8. `README_BEKAL_DRAFT.md`
9. `README.md` for current implementation instructions

If a conflict affects scope, privacy, irreversible data behavior, licensing, or a major architecture decision, stop and raise it to the owner instead of silently choosing a new direction.

Small implementation ambiguities may be resolved independently.

---

# 8. Accepted Architecture

## Frontend

Use:

- React
- TypeScript

UI principles:

- simple
- calm
- readable
- table-focused
- low-clutter
- understandable
- functional before decorative
- broadly consistent with the simplicity of HANA without copying HANA internals

Avoid unnecessary animations, excessive cards, and decorative complexity.

## Backend

Use:

- Python
- FastAPI

Keep receipt-processing logic separate from HTTP route code so it can be tested independently.

## Database

Use PostgreSQL.

Core entities include:

```text
receipts
receipt_items
products
product_aliases
categories
```

Use migrations.

## Deployment

Canonical local path:

```text
C:\Projects\Project-BEKAL
```

Target local topology:

```text
Docker Compose
├── frontend
├── backend
└── postgres

Private host/runtime storage
└── receipt PDFs / temporary candidates
```

## Local-first principle

The BEKAL core must work locally without requiring paid cloud services.

Do not make OpenAI, Google Vision, Azure, AWS, Groq, or another external service mandatory for the V0.1 receipt-processing path.

---

# 9. Receipt Processing Rules

## Input

V0.1 supports receipt PDFs.

Both must work:

1. PDFs containing embedded selectable text
2. scanned/image PDFs requiring OCR

## Extraction order

```text
PDF candidate
   ↓
Validate candidate
   ↓
Attempt embedded-text extraction
   ↓
Usable text?
   ├── Yes → parse direct text
   └── No  → render/extract page images → local OCR
                                      ↓
                                  parse text
                                      ↓
                           structured candidate
```

Do not invoke OCR when embedded text is sufficiently usable.

## Source of truth

The original PDF is the source of truth.

Raw OCR output does not need permanent storage in V0.1.

## Candidate before persistence

Extraction results remain temporary until review and confirmation.

```text
Candidate
   ↓
Review
   ↓
Edit
   ↓
Confirm & Save
   ↓
Permanent database + PDF storage
```

## Uncertain results

Do not fabricate certainty.

Review UI should use simple states such as:

- normal / confident
- `⚠` review recommended

Do not build complicated probability displays.

## Extraction failure

Manual entry is the fallback.

A failed OCR attempt must never become a reason to invent receipt data.

---

# 10. Privacy and Repository Safety

## Core rule

> **Source code may become public. User data must remain private.**

Never commit:

- real receipt PDFs/images
- receipt-derived private OCR caches
- PostgreSQL data directories
- real database dumps
- real CSV exports
- logs containing private receipt contents
- `.env`
- secrets contained in `.env.*`
- passwords
- API keys
- access tokens
- credentials
- private keys
- local backups
- user-specific private configuration

`.env.example` is an intentionally public, non-secret template and is allowed to be tracked. Privacy gates must distinguish `.env.example` from real environment/secret files rather than flagging it as a failure.

Treat `.gitignore` as security-relevant.

Use synthetic fixtures for committed tests and demos.

Before any public release, use defense in depth:

```text
.gitignore
   ↓
pre-commit safety checks
   ↓
secret scanning
   ↓
CI validation
   ↓
human review
```

The repository remains private until the owner explicitly approves publication.

---

# 11. Authentication

Authentication is out of scope for V0.1.

Do not implement:

- login
- signup
- passwords
- JWT
- OAuth
- user accounts
- role permissions

Keep boundaries clean enough that authentication could later be added without rewriting core receipt-processing logic.

Do not spend current milestone time building that future system.

---

# 12. HANA Boundary

BEKAL is not a HANA module.

Do not:

- place BEKAL code in the HANA repository
- copy HANA's database into BEKAL
- create direct HANA database dependencies
- require HANA to run BEKAL

Future HANA integration, if approved, should occur through a defined API.

HANA integration is out of scope for V0.1.

---

# 13. Git Authority

Astra may inside this repository:

- inspect history
- create/edit/move/delete project files
- refactor
- update documentation
- run tests/builds/linters
- create local commits
- push normal project commits to the configured private GitHub remote when working against that remote is part of the assigned task

Use clear commit messages, for example:

```text
chore: scaffold BEKAL v0.1 services
feat: add temporary receipt PDF intake and preview
feat: add receipt text extraction pipeline
test: cover OCR fallback selection
docs: update Phase 2 extraction architecture
```

Do not rewrite substantial user-authored Git history unless explicitly instructed.

Do not change repository visibility.

Do not add a software license until the owner chooses one.

Do not push secrets/private user data.

---

# 14. Full-Access Boundary

Astra has broad authority inside:

```text
C:\Projects\Project-BEKAL
```

It may:

- read all project files
- create/edit/delete/rename project files
- run package managers
- install project dependencies
- run Docker / Docker Compose
- run migrations
- run tests
- run linters/formatters/build tools
- run development servers
- inspect logs
- use Git
- generate synthetic test data
- update documentation

Do not modify unrelated projects or files outside BEKAL unless the owner explicitly asks.

Do not perform destructive machine-level operations unrelated to BEKAL.

---

# 15. Working Style

For each milestone:

1. Read the relevant specification.
2. Establish repository, branch, HEAD, working tree, remote/canonical state, and current evidence.
3. Identify the smallest coherent implementation step and explicit Non-Goals.
4. Implement it.
5. Run appropriate tests/checks.
6. Fix failures caused by the change; do not weaken gates to make them pass.
7. Review the diff.
8. Update documentation when reality changed.
9. Update **Current Execution State** in this `AGENTS.md` when a phase is completed/accepted.
10. Perform a final privacy/Git review.
11. When the phase exit condition is satisfied and no owner-level decision is outstanding, make a scoped commit and push it to the existing private remote.
12. Verify the exact pushed commit and clean working tree.
13. Continue to the next already-approved V0.1 phase without requiring a routine owner handoff.
14. Stop only at a material owner decision or after the authorized V0.1 work reaches its defined stopping point.

Do not ask for approval for routine matters such as helper-function names, small library choices, test placement, ordinary refactors, formatting, internal module boundaries, or other reversible choices inside an accepted milestone.

Ask the owner when a decision materially changes:

- V0.1 scope or finish line
- privacy/security behavior
- irreversible persistent-data semantics
- public-release policy
- software licensing
- repository visibility
- accepted architecture
- destructive migration of real user data
- major frameworks/dependencies
- reliance on required paid/external infrastructure

Do not choose a software license or make the repository public without explicit owner approval. Public-release preparation may proceed up to those decision boundaries.

---

# 16. Testing Expectations

Coverage percentage is not the goal. Core workflow reliability is.

V0.1 should eventually cover:

- PDF validation
- embedded-text extraction
- OCR fallback behavior
- metadata parsing
- line-item parsing
- product normalization
- product aliases
- category assignment
- total validation
- duplicate detection
- persistence
- update/delete behavior
- dashboard analytics
- CSV export
- API health
- end-to-end core workflow

Use synthetic receipts only.

---

# 17. V0.1 Definition of Done

V0.1 is complete when a user can:

1. start BEKAL locally,
2. select a receipt PDF,
3. extract receipt metadata and line items,
4. use direct text extraction when available,
5. use OCR fallback when required,
6. see uncertain rows flagged,
7. view original PDF beside extracted data,
8. edit rows,
9. add/delete rows,
10. correct receipt metadata,
11. see total validation,
12. manually enter data if extraction fails,
13. confirm/save a receipt,
14. privately store the original PDF,
15. see it in history,
16. reopen/edit it,
17. receive duplicate warnings,
18. retain aliases learned from corrections,
19. see monthly dashboard analytics,
20. export `receipts.csv`,
21. export `items.csv`,
22. delete a receipt and its PDF after explicit confirmation,
23. run locally through the documented setup,
24. pass required automated tests.

If those conditions pass:

> **Do not keep calling V0.1 incomplete because a new idea appeared.**

---

# 18. Roadmap

```text
Phase 0  Foundation                    ✅
Phase 1  Receipt intake / preview      ✅
Phase 2  Receipt extraction            ✅
Phase 3  Review & normalization        ✅
Phase 4  Persistence                   ✅
Phase 5  History / CRUD                ✅
Phase 6  Dashboard                     ✅
Phase 7  CSV export                    ✅
Phase 8  Testing / stabilization       ✅
Phase 9  V0.1 release candidate        ✅
Phase 10 Public-release preparation  🚧 next
```

No phase should silently consume the next phase's scope.

---

# 19. Current Mission — Phase 10 Public-Release Preparation

Phase 9 V0.1 release candidate has met its exit condition. Prepare the private repository for a possible public release: review tracked files and commit history for private data or secrets, check ignore and pre-commit/CI defenses, documentation, creator credit, and a safe synthetic demo path. Do not add product features. Do not choose a software license or change repository visibility without the owner's explicit decision. Complete reversible preparation, then stop at those owner-level decisions.

---

# 20. Preferred Astra / Codex Execution Block

When starting or continuing work, use this operating instruction:

```text
Work in C:\Projects\Project-BEKAL with full repository access.

Read AGENTS.md first and treat it as the persistent operating contract and current handoff for Project BEKAL. Then read only the source-of-truth BEKAL V0.1 documents relevant to the current milestone.

Establish current repository evidence before changing anything: repository, branch, HEAD, working tree, origin/canonical state, relevant tests, Docker/runtime state, affected code, migrations, and current accepted milestone.

Implement only the Current Mission defined in AGENTS.md. Keep explicit Non-Goals. Do not silently expand scope into later phases. If a useful idea is outside the current milestone, record/defer it and continue with the approved objective.

You may independently create, edit, delete, rename, refactor, test, document, install appropriate project dependencies, run Docker, run migrations, use Git, make scoped commits, and push normal commits to the existing private GitHub repository when the milestone exit condition is satisfied. Prefer simple, maintainable, local-first implementations over unnecessary architecture.

Protect privacy aggressively: never commit real receipts, runtime user data, exports containing real user data, secrets, credentials, real .env files, database data/dumps, or private logs. `.env.example` is an allowed non-secret template. Use synthetic fixtures only.

For each already-approved V0.1 milestone:
1. inspect current evidence first,
2. define the smallest coherent implementation and Non-Goals,
3. implement,
4. test,
5. fix root causes,
6. review the full diff,
7. update relevant documentation and AGENTS.md,
8. perform final Git/privacy checks,
9. commit and push if all gates pass,
10. verify the exact pushed commit and clean working tree,
11. continue to the next approved V0.1 phase.

Stop and ask the owner only if a decision would materially alter V0.1 scope/finish line, privacy/security behavior, irreversible persistent-data semantics, accepted architecture, software licensing, repository visibility/public release, destructive real-data behavior, major framework/dependency choice, or introduce required paid/external infrastructure.

Do not choose a software license or make the repository public without explicit owner approval.
```

## Owner-run Windows PowerShell convention

When the owner must run a multi-step Windows command, produce **one self-contained PowerShell 5.1-compatible copy/paste block** using the Project HANA execution shape.

Required outer structure:

```powershell
& {
    $ErrorActionPreference = 'Stop'
    Set-StrictMode -Version Latest

    # ============================================================
    # 1. STRICT ENTRY STATE
    # ============================================================

    # Verify path/repository/branch/HEAD/remote/preconditions here.
    # Fail closed before mutation when the expected entry state is not true.

    # ============================================================
    # 2. MAIN OPERATION
    # ============================================================

    # Perform the bounded operation here.

    # ============================================================
    # 3. VERIFICATION
    # ============================================================

    # Run tests/checks/audits and verify expected behavior here.

    # ============================================================
    # 4. FINAL STATE
    # ============================================================

    # Verify Git/runtime/final-state invariants here.

    # ============================================================
    # 5. FINAL RESULT
    # ============================================================

    Write-Host ''
    Write-Host '============================================================'
    Write-Host 'PROJECT BEKAL - <OPERATION> RESULT'
    Write-Host '============================================================'
    Write-Host ''

    # Print a concise final result summary.
}
```

Rules for owner-run PowerShell blocks:

- always wrap the entire operation in `& { ... }` so a terminating error stops the block instead of allowing later pasted commands to continue independently;
- set `$ErrorActionPreference = 'Stop'` at the top;
- normally use `Set-StrictMode -Version Latest`;
- use the five numbered sections above unless the operation is genuinely too small to need all five;
- make entry checks fail closed before mutation;
- put all mutation in the MAIN OPERATION section;
- run tests/checks after mutation in VERIFICATION;
- verify branch/HEAD/working tree/runtime invariants in FINAL STATE;
- print one concise result summary only after all gates pass;
- use PowerShell 5.1-compatible syntax unless the owner explicitly requests otherwise;
- wrap command output in `@(...)` when scalar-vs-array behavior could break under StrictMode;
- never assign to PowerShell's built-in `$Host` variable;
- do not weaken a safety/privacy/test gate merely to make the script continue;
- when scanning for secret environment files, allow the tracked non-secret template `.env.example` while still rejecting real `.env` and secret `.env.*` files;
- prefer a single copy/paste block over a sequence of separate commands.

---

# 21. Final Operating Principle

When uncertain, return to this:

> **BEKAL V0.1 exists to reliably turn receipt PDFs into reviewed, structured, private, useful data.**

If a task strengthens that path and belongs to the current milestone, do it.

If it does not, defer it.

The project should move forward rather than sideways.

---

**Project BEKAL**  
Created by **Wan Mohamad Haziq Mirza**
