# AGENTS.md — Project BEKAL

> **Primary coding agent:** GPT-6 Astra / Codex  
> **Project:** BEKAL  
> **Owner / Creator:** Wan Mohamad Haziq Mirza  
> **Canonical local workspace:** `C:\Projects\Project-BEKAL`  
> **Repository:** `haziqzes/Project-BEKAL`  
> **Repository status:** Private during development  
> **Current target:** BEKAL V0.1  
> **Last updated:** 2026-10-10

---

# 1. Purpose

This file is the persistent operating contract and handoff document for any AI coding agent working on Project BEKAL.

Astra has broad working authority inside `C:\Projects\Project-BEKAL`. It may create, edit, delete, rename, move, refactor, test, document, and organize project files as needed to complete the approved V0.1 scope.

The core rule is:

> **Implementation may change freely when justified, but the product goal, privacy model, accepted architecture, and V0.1 finish line must not be silently changed.**

This file should be kept current as development progresses. At the end of each accepted phase, update the **Current Execution State** section before or with the phase handoff commit.

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

## Current Phase

### Phase 3 — Review & Normalization ✅ Implementation complete; owner review pending

Verified Phase 3 behavior:

- conservative product-name cleanup, predefined categories, and supported quantity/unit inference
- missing or uncertain fields visibly flagged; item totals reconciled with subtotal or receipt total
- original PDF beside an editable temporary candidate
- pen action, row edit/save/cancel, add/delete rows, and editable metadata
- manual-entry form for no-data and extraction-error cases
- browser verification with synthetic text and scanned receipts; backend tests and frontend build pass
- PostgreSQL still contains only the foundation migration table; receipt data remains temporary

Current handoff: Phase 3 has reached its exit condition. Changes are uncommitted for owner review. Do not begin Phase 4 until the owner accepts or redirects the work.

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

Core future entities include:

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

Both must eventually work:

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

Extraction results remain temporary until the later review/confirm phase.

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

Phase 2 stops before permanent persistence.

## Uncertain results

Do not fabricate certainty.

Later review UI should use simple states such as:

- normal / confident
- `⚠` review recommended

Do not build complicated probability displays.

## Extraction failure

Later phases will provide manual entry.

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
- passwords
- API keys
- access tokens
- credentials
- private keys
- local backups
- user-specific private configuration

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
2. Inspect the current repository and Git status.
3. Identify the smallest coherent implementation step.
4. Implement it.
5. Run appropriate tests/checks.
6. Fix failures caused by the change.
7. Review the diff.
8. Update documentation when reality changed.
9. Update **Current Execution State** in this `AGENTS.md` when a phase is accepted/completed.
10. Make a clean commit when instructed or when the milestone contract says to do so.
11. Report changes, verification, limitations, and next logical step.

Do not ask for approval for routine matters such as helper-function names, small library choices, test placement, ordinary refactors, formatting, or internal module boundaries.

Ask the owner when a decision materially changes:

- V0.1 scope
- privacy behavior
- irreversible data semantics
- public-release policy
- software licensing
- accepted architecture
- destructive migration of real user data
- reliance on paid/external infrastructure

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
Phase 3  Review & normalization        ✅ review pending
Phase 4  Persistence
Phase 5  History / CRUD
Phase 6  Dashboard
Phase 7  CSV export
Phase 8  Testing / stabilization
Phase 9  V0.1 release candidate
Phase 10 Public-release preparation
```

No phase should silently consume the next phase's scope.

---

# 19. Current Mission — Phase 3 Review Handoff

Phase 3 was accepted for implementation after Phase 2 commit `cc684f0`. Its objective is to turn an imperfect temporary extraction into a user-reviewable and editable candidate while keeping the original PDF as the source of truth.

The Phase 3 exit condition is met when a user can compare the PDF with structured metadata and item rows, correct fields, edit/save/cancel rows, add/delete rows, resolve review warnings, reconcile totals, and manually enter data if extraction is unusable. All corrections remain temporary. Permanent persistence and all Phase 4+ features are excluded.

Implementation is complete and uncommitted for owner review. Do not begin Phase 4 automatically. Once accepted, update this mission and the Current Execution State for the next authorized phase.

---

# 20. Preferred Astra / Codex Execution Block

When starting or continuing work, use this operating instruction:

```text
Work in C:\Projects\Project-BEKAL with full repository access.

Read AGENTS.md first and treat it as the persistent operating contract and current handoff for Project BEKAL. Then read the source-of-truth BEKAL V0.1 documents relevant to the current milestone.

Inspect the repository, current Git history, working tree, Docker state, tests, and existing implementation before making changes.

Implement only the Current Mission defined in AGENTS.md. Do not silently expand scope into later phases. If you identify a useful out-of-scope feature, record it as a future/backlog idea and continue with the approved milestone.

You may independently create, edit, delete, rename, refactor, test, document, install appropriate project dependencies, run Docker, run migrations, and use Git inside this repository. Prefer simple, maintainable, local-first implementations over unnecessary architecture.

Protect privacy aggressively: never commit real receipts, runtime user data, exports, secrets, credentials, .env files, database data, or private logs. Use synthetic fixtures only.

For the current milestone:
1. inspect first,
2. implement the smallest coherent solution,
3. test it,
4. fix failures,
5. review the diff,
6. update relevant documentation,
7. update AGENTS.md Current Execution State when the phase reaches its exit condition,
8. perform a final Git/privacy review,
9. leave changes uncommitted for owner review unless explicitly instructed to commit,
10. stop at the milestone boundary.

If a decision would materially alter V0.1 scope, privacy behavior, irreversible data semantics, accepted core architecture, software licensing, repository visibility, or introduce required paid/external infrastructure, stop and ask the owner. Otherwise make the best engineering decision and keep moving.
```

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
